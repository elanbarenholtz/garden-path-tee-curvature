"""
x16: NONLINEAR x NEIGHBORHOOD — the last cell of the 2x2 (linear/nonlinear
extrapolation x point/neighborhood space). At the point scale, nonlinearity
was null (x4). Does the DEEP NEIGHBORHOOD trajectory carry nonlinear structure
a linear extrapolator misses?

Layer-9 word anchors (x11/x13 conventions), held-out per-story k=100 clustering
(leakage-safe). On the sqrt-soft assignment (Hellinger) neighborhood
trajectory:
  lntee9   linear k=3 extrapolation error            (baseline = the ntee result)
  qntee9   quadratic k=5 extrapolation error         (adds acceleration)
  nbcurv9  neighborhood curvature: mean angle between successive neighborhood
           step vectors over the last 3 (King-style, in neighborhood space)
Tests:
  D  dissociation (closure/entropy/surprisal) punct-free — does nonlinearity
     re-introduce entropy coupling (break orthogonality)?
  RT does qntee9/nbcurv9 predict on-word RT BEYOND lntee9 + surprisal + fine TEE?
  W  does qntee9 predict the layer-6 causal wake BEYOND lntee9 (L1..L10)?
"""
import os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
from sklearn.cluster import KMeans
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import (GP, load_locked, load_rt, zscore, fit_cluster, build_ctrl,
                  partial_r)

RES = f"{GP}/extensions/results"
LAYER, CHUNK, STRIDE = 9, 1024, 512
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna() &
              (words["id"].str.split(".").str[-1] == "whole")].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
story_words = {s: words.loc[words.story_id == s, "word"].tolist()
               for s in story_ids}
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(os.cpu_count() or 4)

def spans_(wl):
    sp, c = [], 0
    for w in wl:
        sp.append((c, c + len(w))); c += len(w) + 1
    return sp

anchor = {}
for sid in story_ids:
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offs = enc["offset_mapping"]
    n = ids.size(0); hid = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().numpy()
        for i in range(end - pos):
            if (pos + i) not in hid:
                hid[pos + i] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE
    sp = spans_(story_words[sid]); wi = 0; last = {}
    for bi, (cs, ce) in enumerate(offs):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(sp) and cs >= sp[wi][1]:
            wi += 1
        if wi < len(sp) and cs >= sp[wi][0] and ce <= sp[wi][1]:
            last[wi] = bi
    anchor[sid] = np.stack([hid[last[w]] for w in range(len(sp))]) \
        .astype(np.float64)
print("anchors done", flush=True)

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

def quad_err(traj, w, k=5):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    x = np.arange(k, dtype=np.float64)
    A = np.column_stack([np.ones(k), x, x ** 2])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    pred = c[0] + c[1] * k + c[2] * k ** 2
    return float(np.linalg.norm(traj[w] - pred))

def nb_curv(traj, w):
    def ang(i):
        if i - 2 < 0:
            return np.nan
        a = traj[i] - traj[i - 1]; b = traj[i - 1] - traj[i - 2]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-9 or nb < 1e-9:
            return np.nan
        return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1, 1)))
    vals = [ang(w - 2), ang(w - 1), ang(w)]
    return float(np.mean(vals)) if all(np.isfinite(v) for v in vals) else np.nan

rows = []
for sid in story_ids:
    TR = np.vstack([anchor[s] for s in story_ids if s != sid])
    km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(TR)
    sig = float(np.median(km.transform(TR).min(1)))
    A_ = anchor[sid]
    p = np.exp(-(km.transform(A_) ** 2) / (2 * sig ** 2))
    p /= p.sum(1, keepdims=True)
    sq = np.sqrt(p)
    for w in range(A_.shape[0]):
        rows.append({"story_id": sid, "word_idx": w,
                     "lntee9": lin_err(sq, w, 3),
                     "qntee9": quad_err(sq, w, 5),
                     "nbcurv9": nb_curv(sq, w)})
    print(f"story {sid} done", flush=True)
E = pd.DataFrame(rows)
M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
M = M.merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp"]],
            on=["story_id", "word_idx"])
M.to_csv(f"{GP}/extensions/nonlinear_nbhd_8a6087341e.csv", index=False)
print(f"\nr(qntee9, lntee9) = {np.corrcoef(M.qntee9.fillna(0), M.lntee9.fillna(0))[0,1]:.3f}")

# D: dissociation punct-free
Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
Cm = build_ctrl(Mpf)
print("\nD. dissociation (punct-free): does nonlinearity re-introduce entropy?")
for meas in ["lntee9", "qntee9", "nbcurv9"]:
    cells = []
    for t in ["closure_depth", "entropy", "surprisal"]:
        r, p = partial_r(Mpf, Cm, meas, t)
        cells.append(f"{t[:4]}: {r:+.3f}(p={p:.0e})")
    print(f"  {meas:8s} | " + " | ".join(cells))

# RT: does nonlinear neighborhood add beyond linear ntee?
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"
Dpf = D[D.has_trailing_punct == 0].dropna(
    subset=["prev_logRT", "lntee9", "qntee9", "nbcurv9"]).reset_index(drop=True)
Z = Dpf.copy()
for c in ["lntee9", "qntee9", "nbcurv9", "tee3_perp", "tee3_par", "surprisal",
          "word_length", "log_freq", "prev_logRT"]:
    Z[c] = zscore(Dpf[c])
print("\nRT (punct-free): on-word logRT ~ lntee9 + qntee9 + nbcurv9 + fine TEE"
      " + surprisal + lexical")
m = fit_cluster("mean_logRT ~ lntee9 + qntee9 + nbcurv9 + tee3_perp + tee3_par"
                f" + surprisal + word_length + log_freq + {CTRL}", Z)
for t in ["lntee9", "qntee9", "nbcurv9", "surprisal"]:
    print(f"  {t:8s} beta={m.params[t]:+.4f} p={m.pvalues[t]:.2e}"
          f"{'*' if m.pvalues[t]<.05 else ''}")

# W: wake — does qntee9 beat lntee9 predicting the layer-6 wake?
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
DW = W.merge(M, on=["story_id", "word_idx"], validate="one_to_one")
DWpf = DW[DW.has_trailing_punct == 0].reset_index(drop=True)
PRED = ["lntee9", "qntee9", "nbcurv9", "entropy", "surprisal", "tee3_perp",
        "tee3_par", "word_length", "log_freq"]
CTRL2 = "from_start + fs2 + from_end + fe2 + C(story_id)"
print("\nW. wake_rel_L (punct-free): lntee9 vs qntee9 vs nbcurv9 together")
print(f"{'lag':>3s} {'lntee9':>15s} {'qntee9':>15s} {'nbcurv9':>15s}")
for L in (1, 2, 5, 10):
    dv = f"wake_rel_{L}"
    Dl = DWpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z2 = Dl.copy(); Z2["y"] = zscore(Dl[dv])
    for p_ in PRED:
        Z2[p_] = zscore(Dl[p_])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL2}", Z2)
    print(f"{L:>3d} " + " ".join(
        f"{mod.params[t]:+.3f}({mod.pvalues[t]:.0e}){'*' if mod.pvalues[t]<.05 else ' '}"
        for t in ["lntee9", "qntee9", "nbcurv9"]))
print(f"\nDONE hash={sh}")
