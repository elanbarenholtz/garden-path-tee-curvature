"""
x4: Nonlinear extrapolators at the locked anchor (final subword, BPE grain).
  qtee_k5, qtee_k7   quadratic extrapolation (adds acceleration term)
  ldstee_k10         local linear-dynamical-system TEE: fit one-step ridge map
                     in a local PCA basis over the last 10 states, roll forward
  ftee_n50           flow-field TEE (ALLOCENTRIC): mean next-step of the 50
                     nearest corpus states from OTHER stories, applied to
                     h[ls-1]; error vs actual h[ls]
  ftee_res           flow-residual TEE: tee_k3-style egocentric prediction
                     minus corpus-flow prediction magnitude (dissociation aid)
Then: dissociation tables (closure/entropy/surprisal/tee_k3) + RT L0/L1 test.
Output: nonlinear_tee_8a6087341e.csv + results/x4_*.csv
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
H_ = {}; LS = {}
for sid in story_ids:
    H, bpe_word, first_sub, last_sub = load_states(sid)
    H_[sid] = H; LS[sid] = last_sub

def quad_tee(H, t, k):
    if t - k < 0:
        return np.nan
    W = H[t - k:t]
    x = np.arange(k, dtype=np.float64)
    A = np.column_stack([np.ones(k), x, x ** 2])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    pred = coefs[0] + coefs[1] * k + coefs[2] * k ** 2
    return float(np.linalg.norm(H[t] - pred))

def lds_tee(H, t, k=10, d=6, lam=1e-2):
    if t - k < 0:
        return np.nan
    W = H[t - k:t]
    mu = W.mean(0); Wc = W - mu
    U, s, Vt = np.linalg.svd(Wc, full_matrices=False)
    V = Vt[:d].T
    Y = Wc @ V                       # (k, d) local coords
    A0, A1 = Y[:-1], Y[1:]
    G = A0.T @ A0 + lam * np.eye(d)
    Wmap = np.linalg.solve(G, A0.T @ A1)   # d x d one-step map
    y_pred = Y[-1] @ Wmap
    pred = mu + y_pred @ V.T
    return float(np.linalg.norm(H[t] - pred))

# ---- flow field: nearest neighbours from OTHER stories ----
corpus = {sid: H_[sid][:-1] for sid in story_ids}          # states with a next
steps = {sid: H_[sid][1:] - H_[sid][:-1] for sid in story_ids}

def flow_pred_errors(sid, anchors, N=50):
    """For each anchor ls: mean next-step of N nearest other-story states to
    h[ls-1]; returns flow-TEE and norm of (egocentric - flow) prediction gap."""
    XO = np.vstack([corpus[s] for s in story_ids if s != sid])
    DO = np.vstack([steps[s] for s in story_ids if s != sid])
    Q = H_[sid][[a - 1 for a in anchors]]                  # (q,768)
    q2 = (Q ** 2).sum(1)[:, None]; x2 = (XO ** 2).sum(1)[None]
    D2 = q2 + x2 - 2 * Q @ XO.T
    idx = np.argpartition(D2, N, axis=1)[:, :N]
    out_f, out_gap = [], []
    for i, a in enumerate(anchors):
        dbar = DO[idx[i]].mean(0)
        pred_flow = H_[sid][a - 1] + dbar
        out_f.append(float(np.linalg.norm(H_[sid][a] - pred_flow)))
        # egocentric k=3 prediction for the gap
        W = H_[sid][a - 3:a]
        A = np.column_stack([np.ones(3), np.arange(3, dtype=np.float64)])
        c, *_ = np.linalg.lstsq(A, W, rcond=None)
        pred_ego = c[0] + c[1] * 3
        out_gap.append(float(np.linalg.norm(pred_ego - pred_flow)))
    return out_f, out_gap

rows = []
for sid in story_ids:
    ls = LS[sid]; H = H_[sid]
    sub = S[S.story_id == sid].sort_values("word_idx")
    anchors = [ls[w] for w in sub.word_idx]
    ftee, fgap = flow_pred_errors(sid, anchors)
    for j, w in enumerate(sub.word_idx.values):
        t = ls[w]
        rows.append({"story_id": sid, "word_idx": int(w),
                     "qtee_k5": quad_tee(H, t, 5),
                     "qtee_k7": quad_tee(H, t, 7),
                     "ldstee_k10": lds_tee(H, t, 10),
                     "ftee_n50": ftee[j], "fgap_n50": fgap[j]})
    print(f"story {sid} done", flush=True)

E = pd.DataFrame(rows)
M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
assert len(M) == 9840
M.to_csv(f"{GP}/extensions/nonlinear_tee_8a6087341e.csv", index=False)

MEAS = ["qtee_k5", "qtee_k7", "ldstee_k10", "ftee_n50", "fgap_n50"]
print("\nraw correlations with tee_k3:")
for m in MEAS:
    print(f"  {m}: r={np.corrcoef(M[m], M.tee_k3)[0,1]:+.4f}")
T = dissociation_table(M, MEAS, label="x4 nonlinear extrapolators")
T.to_csv(f"{RES}/x4_dissociation.csv", index=False)

# ---- RT: L0/L1, each variant vs tee_k3 competition ----
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
BASE = ["surprisal", "word_length", "log_freq", "has_trailing_punct"]
for v in MEAS + BASE + ["tee_k3"]:
    D[f"{v}_L1"] = D.groupby("story_id")[v].shift(1)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"
res = []
for m in MEAS:
    Dl = D.dropna(subset=[m, f"{m}_L1", "prev_logRT", "tee_k3_L1"]
                  + [f"{v}_L1" for v in BASE]).reset_index(drop=True)
    Z = Dl.copy()
    terms = []
    for v in [m, "tee_k3"] + BASE:
        Z[v] = zscore(Dl[v]); Z[f"{v}_L1"] = zscore(Dl[f"{v}_L1"])
        terms += [v, f"{v}_L1"]
    Z["prev_logRT"] = zscore(Dl["prev_logRT"])
    mod = fit_cluster(f"mean_logRT ~ {' + '.join(terms)} + {CTRL}", Z)
    print(f"\nRT model with {m} (competing with tee_k3):  n={int(mod.nobs)}")
    for t in [m, f"{m}_L1", "tee_k3", "tee_k3_L1", "surprisal",
              "surprisal_L1"]:
        b, p = mod.params[t], mod.pvalues[t]
        star = "*" if p < .05 else " "
        print(f"  {t:16s} beta={b:+.4f} p={p:.2e}{star}")
        res.append({"measure": m, "term": t, "beta": b, "p": p})
pd.DataFrame(res).to_csv(f"{RES}/x4_rt.csv", index=False)
print(f"\nDONE hash={sh}")
