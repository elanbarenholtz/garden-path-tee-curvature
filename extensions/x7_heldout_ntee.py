"""
x7: Held-out-story clustering control for the ntee_k100 results.
For each story s, k-means (k=100, same seed/params as x1) is fit on the word
states of the OTHER 9 stories only; story s's trajectory is soft-assigned with
sigma = median nearest-centroid distance of the TRAINING states. ntee_ho is
the k=3 extrapolation error in the held-out Hellinger space. Then the two
headline regressions are rerun punct-free with ntee_ho in place of ntee_k100:
  (a) on-word RT with fine TEE + surprisal competition
  (b) causal wake at lags 1,2,3,5,7,10 with entropy/curvature controls
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import (GP, load_locked, load_states, load_rt, zscore, fit_cluster,
                  build_ctrl, partial_r)
from sklearn.cluster import KMeans

RES = f"{GP}/extensions/results"
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
X = {}
for sid in story_ids:
    H, bpe_word, first_sub, last_sub = load_states(sid)
    X[sid] = H[last_sub]

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

rows = []
for sid in story_ids:
    TR = np.vstack([X[s] for s in story_ids if s != sid])
    km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(TR)
    dtr = np.linalg.norm(TR[:, None, :] - km.cluster_centers_[None],
                         axis=-1).min(1)
    sig = float(np.median(dtr))
    d = np.linalg.norm(X[sid][:, None, :] - km.cluster_centers_[None],
                       axis=-1)
    p = np.exp(-(d ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
    sq = np.sqrt(p)
    for w in range(X[sid].shape[0]):
        rows.append({"story_id": sid, "word_idx": w,
                     "ntee_ho": lin_err(sq, w, 3)})
    print(f"story {sid} held-out fit done", flush=True)

E = pd.DataFrame(rows)
M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
M = M.merge(C[["story_id", "word_idx", "ntee_k100", "ctee_m5"]],
            on=["story_id", "word_idx"])
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
M = M.merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp",
                 "curvature_3"]], on=["story_id", "word_idx"])
assert len(M) == 9840
M[["story_id", "word_idx", "ntee_ho"]].to_csv(
    f"{GP}/extensions/ntee_heldout_8a6087341e.csv", index=False)
print(f"\nr(ntee_ho, ntee_k100) = "
      f"{np.corrcoef(M.ntee_ho, M.ntee_k100)[0, 1]:+.4f}")
Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
Cm = build_ctrl(Mpf, with_punct=False)
for t in ("closure_depth", "entropy", "surprisal", "tee_k3"):
    r, p = partial_r(Mpf, Cm, "ntee_ho", t)
    print(f"  ntee_ho x {t}: r={r:+.4f} (p={p:.0e})  [punct-free]")

# (a) on-word RT, punct-free
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
BASE = ["tee3_perp", "tee3_par", "surprisal", "word_length", "log_freq",
        "has_trailing_punct"]
for v in BASE + ["ntee_ho"]:
    D[f"{v}_L1"] = D.groupby("story_id")[v].shift(1)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"
Dpf = D[D.has_trailing_punct == 0].dropna(
    subset=["prev_logRT", "ntee_ho_L1"] + [f"{v}_L1" for v in BASE]
    ).reset_index(drop=True)
Z = Dpf.copy(); terms = []
for v in ["ntee_ho"] + BASE:
    if v != "has_trailing_punct":
        Z[v] = zscore(Dpf[v]); terms.append(v)
    Z[f"{v}_L1"] = zscore(Dpf[f"{v}_L1"]); terms.append(f"{v}_L1")
Z["prev_logRT"] = zscore(Dpf["prev_logRT"])
mod = fit_cluster(f"mean_logRT ~ {' + '.join(terms)} + {CTRL}", Z)
print(f"\n(a) PUNCT-FREE on-word RT (n={int(mod.nobs)}):")
for t in ["ntee_ho", "ntee_ho_L1", "tee3_perp", "surprisal"]:
    print(f"  {t:12s} beta={mod.params[t]:+.4f} p={mod.pvalues[t]:.2e}"
          f"{'*' if mod.pvalues[t] < .05 else ''}")

# (b) wake, punct-free, entropy+curvature controls
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
DW = W.merge(M, on=["story_id", "word_idx"], validate="one_to_one")
DWpf = DW[DW.has_trailing_punct == 0].reset_index(drop=True)
PRED = ["ntee_ho", "entropy", "curvature_3", "surprisal", "tee3_perp",
        "tee3_par", "ctee_m5", "word_length", "log_freq"]
CTRL2 = "from_start + fs2 + from_end + fe2 + C(story_id)"
print(f"\n(b) PUNCT-FREE wake_rel_L ~ ntee_ho + controls (n={len(DWpf)}):")
for L in (1, 2, 3, 5, 7, 10):
    dv = f"wake_rel_{L}"
    Dl = DWpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p_ in PRED:
        Z[p_] = zscore(Dl[p_])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL2}", Z)
    b, pv = mod.params["ntee_ho"], mod.pvalues["ntee_ho"]
    be, pe = mod.params["entropy"], mod.pvalues["entropy"]
    bs, ps = mod.params["surprisal"], mod.pvalues["surprisal"]
    print(f"  L{L:>2d}: ntee_ho={b:+.3f}(p={pv:.0e})"
          f"{'*' if pv < .05 else ' '}  entropy={be:+.3f}(p={pe:.0e})"
          f"  surprisal={bs:+.3f}(p={ps:.0e})")
print(f"\nDONE hash={sh}")
