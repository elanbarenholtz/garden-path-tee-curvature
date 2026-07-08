"""
x5: Meta-TEE (heading dynamics) + manifold-corrected TEE. BPE grain, locked
anchor (final subword).
  mtee_k3       heading extrapolation error: extrapolate the unit-heading
                sequence u_i = (h_i - h_{i-1})/|..| linearly over 3 steps;
                error = angle(pred_heading, actual_heading)  [radians]
  hmag_k3       predicted-vs-actual step MAGNITUDE error (pace channel alone)
  tee_in_k20    component of the k=3 TEE residual INSIDE the local manifold
                (PCA d=10 on the 20 preceding states)
  tee_out_k20   component orthogonal to the local manifold
Dissociation tables + RT L0/L1.
Output: meta_manifold_8a6087341e.csv + results/x5_*.csv
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import (GP, load_locked, load_states, dissociation_table,
                  load_rt, zscore, fit_cluster)

RES = f"{GP}/extensions/results"; os.makedirs(RES, exist_ok=True)
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())

def angle(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-8 or nb < 1e-8:
        return np.nan
    return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1, 1)))

def meta_tee(H, t, k=3):
    """headings u at steps t-k..t-1 -> linear extrap -> compare to u at t."""
    if t - k - 1 < 0:
        return np.nan, np.nan
    U, mags = [], []
    for i in range(t - k, t + 1):
        d = H[i] - H[i - 1]; n = np.linalg.norm(d)
        if n < 1e-8:
            return np.nan, np.nan
        U.append(d / n); mags.append(n)
    U = np.stack(U)                    # k+1 headings; last is actual
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, U[:-1], rcond=None)
    pred = c[0] + c[1] * k
    m_ang = angle(pred, U[-1])
    cm, *_ = np.linalg.lstsq(A, np.array(mags[:-1])[:, None], rcond=None)
    pred_mag = float(np.asarray(cm[0] + cm[1] * k).ravel()[0])
    return m_ang, abs(pred_mag - mags[-1])

def manifold_split(H, t, k=3, kwin=20, d=10):
    if t - kwin < 0:
        return np.nan, np.nan
    W3 = H[t - k:t]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W3, rcond=None)
    r = H[t] - (c[0] + c[1] * k)
    Wm = H[t - kwin:t]
    mu = Wm.mean(0)
    U, s, Vt = np.linalg.svd(Wm - mu, full_matrices=False)
    V = Vt[:d].T
    r_in = V @ (V.T @ r)
    return float(np.linalg.norm(r_in)), float(np.linalg.norm(r - r_in))

rows = []
for sid in story_ids:
    H, bpe_word, first_sub, last_sub = load_states(sid)
    for w in S[S.story_id == sid].word_idx.values:
        t = last_sub[w]
        ma, mm = meta_tee(H, t, 3)
        ti, to = manifold_split(H, t)
        rows.append({"story_id": sid, "word_idx": int(w), "mtee_k3": ma,
                     "hmag_k3": mm, "tee_in_k20": ti, "tee_out_k20": to})
    print(f"story {sid} done", flush=True)

E = pd.DataFrame(rows)
M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
assert len(M) == 9840
M.to_csv(f"{GP}/extensions/meta_manifold_8a6087341e.csv", index=False)

MEAS = ["mtee_k3", "hmag_k3", "tee_in_k20", "tee_out_k20"]
print("\nNaN counts:", {m: int(M[m].isna().sum()) for m in MEAS})
print("share of TEE variance in/out:",
      f"in^2/(in^2+out^2) = "
      f"{(M.tee_in_k20**2/(M.tee_in_k20**2+M.tee_out_k20**2)).mean():.3f}")
T = dissociation_table(M, MEAS, label="x5 meta/manifold")
T.to_csv(f"{RES}/x5_dissociation.csv", index=False)

# ---- RT L0/L1 ----
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
BASE = ["surprisal", "word_length", "log_freq", "has_trailing_punct"]
for v in MEAS + BASE + ["tee_k3"]:
    D[f"{v}_L1"] = D.groupby("story_id")[v].shift(1)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"
res = []
for grp in [["mtee_k3", "hmag_k3"], ["tee_in_k20", "tee_out_k20"]]:
    need = grp + [f"{v}_L1" for v in grp] + ["prev_logRT"] \
        + [f"{v}_L1" for v in BASE]
    Dl = D.dropna(subset=need).reset_index(drop=True)
    Z = Dl.copy(); terms = []
    for v in grp + BASE:
        Z[v] = zscore(Dl[v]); Z[f"{v}_L1"] = zscore(Dl[f"{v}_L1"])
        terms += [v, f"{v}_L1"]
    Z["prev_logRT"] = zscore(Dl["prev_logRT"])
    mod = fit_cluster(f"mean_logRT ~ {' + '.join(terms)} + {CTRL}", Z)
    print(f"\nRT model {grp}: n={int(mod.nobs)}")
    for v in grp:
        for t in (v, f"{v}_L1"):
            b, p = mod.params[t], mod.pvalues[t]
            star = "*" if p < .05 else " "
            print(f"  {t:16s} beta={b:+.4f} p={p:.2e}{star}")
            res.append({"group": "+".join(grp), "term": t, "beta": b, "p": p})
pd.DataFrame(res).to_csv(f"{RES}/x5_rt.csv", index=False)
print(f"\nDONE hash={sh}")
