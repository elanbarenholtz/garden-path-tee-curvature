"""
x1: Neighborhood-level (coarse) TEE. Word-grain trajectory x(w) = layer-6 state
at w's final subword. Three coarse-grainings:
  (a) wtee            word-grain TEE (k=3 words) — the fine baseline at this grain
  (b) ctee_m{3,5,10}  trailing-mean smoothed trajectory, TEE k=3 on smoothed states
  (c) ntee_k{30,100,300} k-means neighborhood soft-assignment (Hellinger) TEE;
      nswitch_k*      hard cluster-switch indicator
par/perp decomposition kept for wtee and ctee_m5 (wake analysis needs it).
Dissociation tables (closure/entropy/surprisal/tee_k3) with punct control and
punct-free pass. Cluster punctuation-sink audit included.
Output: coarse_tee_8a6087341e.csv + results/x1_dissociation.csv
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, load_states, dissociation_table
from sklearn.cluster import KMeans

RES = f"{GP}/extensions/results"; os.makedirs(RES, exist_ok=True)
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
print(f"SAMPLE: hash={sh} n={len(S)}", flush=True)

# ---- word-grain trajectories per story ----
X = {}          # sid -> (n_words, 768) final-subword states
for sid in story_ids:
    H, bpe_word, first_sub, last_sub = load_states(sid)
    X[sid] = H[last_sub]
nw = {sid: X[sid].shape[0] for sid in story_ids}

def lin_extrap_err(traj, w, k=3, decomp=False):
    """Extrapolate traj rows w-k..w-1 -> w; return error (and par/perp)."""
    if w - k < 0 or w >= traj.shape[0]:
        return (np.nan, np.nan, np.nan) if decomp else np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    a, b = coefs[0], coefs[1]
    r = traj[w] - (a + b * k)
    if not decomp:
        return float(np.linalg.norm(r))
    nb = np.linalg.norm(b)
    if nb <= 0 or not np.isfinite(nb):
        return float(np.linalg.norm(r)), np.nan, np.nan
    bhat = b / nb
    par = float(np.dot(r, bhat))
    perp = float(np.linalg.norm(r - par * bhat))
    return float(np.linalg.norm(r)), abs(par), perp

def trailing_mean(traj, m):
    out = np.full_like(traj, np.nan)
    c = np.cumsum(traj, axis=0)
    out[m - 1:] = (c[m - 1:] - np.vstack([np.zeros(traj.shape[1]),
                   c[:-m]])[:traj.shape[0] - m + 1]) / m
    for i in range(min(m - 1, traj.shape[0])):
        out[i] = traj[:i + 1].mean(0)
    return out

# ---- k-means neighborhoods on all word states ----
ALL = np.vstack([X[sid] for sid in story_ids])
print(f"kmeans input: {ALL.shape}", flush=True)
soft = {}
km_models = {}
for K in (30, 100, 300):
    km = KMeans(n_clusters=K, n_init=4, random_state=0).fit(ALL)
    km_models[K] = km
    d2 = ((ALL[:, None, :] - km.cluster_centers_[None]) ** 2).sum(-1) \
        if False else None
    print(f"K={K} fit done", flush=True)
soft_sigma = {}

def soft_assign(x, km):
    d = np.linalg.norm(x[:, None, :] - km.cluster_centers_[None], axis=-1)
    sig = np.median(d.min(1))
    p = np.exp(-(d ** 2) / (2 * sig ** 2))
    p /= p.sum(1, keepdims=True)
    return p, sig

rows = []
for sid in story_ids:
    traj = X[sid]
    sm = {m: trailing_mean(traj, m) for m in (3, 5, 10)}
    sq = {}
    hard = {}
    for K in (30, 100, 300):
        p, sig = soft_assign(traj, km_models[K])
        sq[K] = np.sqrt(p)                      # Hellinger embedding
        hard[K] = km_models[K].predict(traj)
    for w in range(nw[sid]):
        rec = {"story_id": sid, "word_idx": w}
        t, pa, pe = lin_extrap_err(traj, w, 3, decomp=True)
        rec["wtee"], rec["wtee_par"], rec["wtee_perp"] = t, pa, pe
        for m in (3, 5, 10):
            if m == 5:
                t, pa, pe = lin_extrap_err(sm[m], w, 3, decomp=True)
                rec[f"ctee_m{m}"], rec["ctee_m5_par"], rec["ctee_m5_perp"] = \
                    t, pa, pe
            else:
                rec[f"ctee_m{m}"] = lin_extrap_err(sm[m], w, 3)
        for K in (30, 100, 300):
            rec[f"ntee_k{K}"] = lin_extrap_err(sq[K], w, 3)
            rec[f"nswitch_k{K}"] = (float(hard[K][w] != hard[K][w - 1])
                                    if w > 0 else np.nan)
        rows.append(rec)
E = pd.DataFrame(rows)
M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
assert len(M) == 9840, len(M)
M.to_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv", index=False)
print(f"saved coarse_tee csv n={len(M)}", flush=True)

# ---- punctuation sink audit for clusters ----
punct_word = np.concatenate([(S[S.story_id == sid].sort_values("word_idx")
    .set_index("word_idx").has_trailing_punct
    .reindex(range(nw[sid]))).fillna(0).values for sid in story_ids])
print("\ncluster punct audit (max share of punct-anchored words in a cluster,"
      " weighted by cluster size):")
for K in (30, 100, 300):
    lab = km_models[K].predict(ALL)
    shares = pd.DataFrame({"lab": lab, "p": punct_word}).groupby("lab") \
        .agg(share=("p", "mean"), n=("p", "size"))
    top = shares.sort_values("share", ascending=False).head(3)
    print(f"K={K}: top punct clusters:\n{top.to_string()}")

MEAS = (["wtee", "ctee_m3", "ctee_m5", "ctee_m10",
         "ntee_k30", "ntee_k100", "ntee_k300",
         "nswitch_k100", "wtee_par", "wtee_perp",
         "ctee_m5_par", "ctee_m5_perp"])
T = dissociation_table(M, MEAS, label="x1 coarse measures")
T.to_csv(f"{RES}/x1_dissociation.csv", index=False)
print(f"\nDONE hash={sh}")
