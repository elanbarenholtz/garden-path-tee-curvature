"""
x9c: XL measures + non-wake analyses. From x9a saved states:
  tee_k3_xl        fine TEE at mid layer (BPE grain, locked anchor)
  curvature_3_xl   King-style curvature at mid layer (sign check vs King)
  ntee_l{i}_xl     neighborhood TEE (k=100, Hellinger) per sampled layer
Analyses: dissociation partial rs (closure / entropy_xl / surprisal_xl,
punct-free), RT (fine TEE beyond XL surprisal; ntee on-word), and saves
kmeans centroids/sigma at the mid layer for x9b.
Usage: python3 x9c_xl_measures.py [gpt2_xl]
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import (GP, load_locked, load_rt, zscore, fit_cluster, build_ctrl,
                  partial_r)
from sklearn.cluster import KMeans

TAG = sys.argv[1] if len(sys.argv) > 1 else "gpt2_xl"
STD = f"{GP}/extensions/{TAG}_states"
RES = f"{GP}/extensions/results"
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
SE = pd.read_csv(f"{GP}/extensions/{TAG}_surp_ent.csv")

Z0 = np.load(f"{STD}/story{story_ids[0]}.npz")
NLAY = Z0["anchors"].shape[1]
print(f"{TAG}: sampled layers in anchors = {NLAY}", flush=True)
MIDI = None  # index of mid layer in sampled list = middle entry
MIDI = NLAY // 2

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

def angle(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-8 or nb < 1e-8:
        return np.nan
    return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1, 1)))

def curv3(H, ls):
    def ang_at(i):
        if i - 2 < 0:
            return np.nan
        return angle(H[i] - H[i - 1], H[i - 1] - H[i - 2])
    a = [ang_at(ls - 2), ang_at(ls - 1), ang_at(ls)]
    return float(np.mean(a)) if all(np.isfinite(x) for x in a) else np.nan

# ---- fine measures + anchor collection ----
anch = {}
rows = []
for sid in story_ids:
    z = np.load(f"{STD}/story{sid}.npz")
    H = z["H_mid"].astype(np.float64); ls = z["last_sub"]
    anch[sid] = z["anchors"].astype(np.float64)   # (nw, NLAY, d)
    for w in range(len(ls)):
        t = ls[w]
        rows.append({"story_id": sid, "word_idx": w,
                     "tee_k3_xl": lin_err(H, t, 3),
                     "curvature_3_xl": curv3(H, t)})
    print(f"story {sid} fine done", flush=True)
F = pd.DataFrame(rows)

# ---- ntee per sampled layer ----
for li in range(NLAY):
    ALL = np.vstack([anch[sid][:, li, :] for sid in story_ids])
    km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(ALL)
    dnn = np.linalg.norm(ALL[:, None, :] - km.cluster_centers_[None],
                         axis=-1).min(1)
    sig = float(np.median(dnn))
    if li == MIDI:
        np.savez_compressed(f"{GP}/extensions/{TAG}_kmeans_mid.npz",
                            centroids=km.cluster_centers_, sigma=sig)
    col = []
    for sid in story_ids:
        A_ = anch[sid][:, li, :]
        d = np.linalg.norm(A_[:, None, :] - km.cluster_centers_[None],
                           axis=-1)
        p = np.exp(-(d ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
        sq = np.sqrt(p)
        col += [{"story_id": sid, "word_idx": w,
                 f"ntee_l{li}_xl": lin_err(sq, w, 3)}
                for w in range(A_.shape[0])]
    F = F.merge(pd.DataFrame(col), on=["story_id", "word_idx"])
    print(f"layer-slot {li} ntee done", flush=True)

M = S.merge(F, on=["story_id", "word_idx"], validate="one_to_one") \
     .merge(SE, on=["story_id", "word_idx"], validate="one_to_one")
assert len(M) == 9840
M.to_csv(f"{GP}/extensions/{TAG}_measures_8a6087341e.csv", index=False)

# ---- dissociation (punct-free) ----
NTEE_MID = f"ntee_l{MIDI}_xl"
Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
Cm = build_ctrl(Mpf)
print(f"\nXL dissociation, punct-free (n={len(Mpf)}):")
for meas in ["tee_k3_xl", "curvature_3_xl", NTEE_MID]:
    cells = []
    for t in ["closure_depth", f"entropy_{TAG}", f"surprisal_{TAG}"]:
        r, p = partial_r(Mpf, Cm, meas, t)
        cells.append(f"{t.split('_')[0]}: {r:+.4f}(p={p:.0e})")
    print(f"  {meas:16s} | " + " | ".join(cells))
print("  (King sign check: curvature_3_xl x entropy above; King reported "
      "+0.15 on XL mid-layers)")

# ---- RT: fine TEE beyond XL surprisal; ntee on-word ----
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
BASE = [f"surprisal_{TAG}", "word_length", "log_freq", "has_trailing_punct"]
for v in BASE + ["tee_k3_xl", NTEE_MID]:
    D[f"{v}_L1"] = D.groupby("story_id")[v].shift(1)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"
for label, meas in [("fine tee_k3_xl", "tee_k3_xl"),
                    (f"ntee mid ({NTEE_MID})", NTEE_MID)]:
    Dl = D.dropna(subset=[meas, f"{meas}_L1", "prev_logRT"]
                  + [f"{v}_L1" for v in BASE] + BASE).reset_index(drop=True)
    Z = Dl.copy(); terms = []
    for v in [meas] + BASE:
        Z[v] = zscore(Dl[v]); Z[f"{v}_L1"] = zscore(Dl[f"{v}_L1"])
        terms += [v, f"{v}_L1"]
    Z["prev_logRT"] = zscore(Dl["prev_logRT"])
    mod = fit_cluster(f"mean_logRT ~ {' + '.join(terms)} + {CTRL}", Z)
    print(f"\nRT: {label} (n={int(mod.nobs)}):")
    for t in [meas, f"{meas}_L1", f"surprisal_{TAG}",
              f"surprisal_{TAG}_L1"]:
        print(f"  {t:22s} beta={mod.params[t]:+.4f} "
              f"p={mod.pvalues[t]:.2e}{'*' if mod.pvalues[t] < .05 else ''}")

# layer sweep: RT beta per layer slot (punct-free simple battery)
print("\nlayer-slot sweep, on-word RT beta (surprisal/lexical/prevRT ctl, "
      "punct-free):")
Dpf = D[D.has_trailing_punct == 0].reset_index(drop=True)
for li in range(NLAY):
    meas = f"ntee_l{li}_xl"
    Dl = Dpf.dropna(subset=[meas, "prev_logRT"]).reset_index(drop=True)
    Z = Dl.copy()
    for c in [meas, f"surprisal_{TAG}", "word_length", "log_freq",
              "prev_logRT"]:
        Z[c] = zscore(Dl[c])
    mod = fit_cluster(f"mean_logRT ~ {meas} + surprisal_{TAG} + word_length"
                      f" + log_freq + prev_logRT + from_start + fs2"
                      f" + from_end + fe2 + C(story_id)", Z)
    print(f"  slot {li:2d}: beta={mod.params[meas]:+.4f} "
          f"p={mod.pvalues[meas]:.0e}")
print(f"\nDONE {TAG} hash={sh}")
