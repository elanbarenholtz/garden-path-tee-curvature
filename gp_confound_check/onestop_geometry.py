"""
DECOMPOSE THE ONESTOP MEASURE: RUN-UP GEOMETRY vs TARGET DEVIATION
===================================================================
Extrapolation error at word i is ||h_i - (fit through h_{lo..i-1} projected one
step)||. That single number confounds two things:

  RUN-UP GEOMETRY -- properties of words lo..i-1 alone. Fully determined before
    word i is seen, and therefore available to a reader deciding whether to skip
    word i. A straight run-up gives a long fitted step, which projects far ahead
    and leaves room to miss; a bent run-up gives a short fitted step that cannot
    miss by much.

  TARGET DEVIATION -- how far h_i actually falls from that projection, which is
    a property of word i and is not available before fixating it.

The lag analysis showed the skipping effect is carried by word i-1 rather than
word i, which points at the run-up. This computes the components directly so the
question can be asked without going through a lag.

EMITTED PER WORD (same pipeline conventions as onestop_context_tee.py: GPT-2
small, layer 6, k=3, article-level context, 1024/512 chunks, first-write-wins,
word state = final subword, fit window never includes token 0):

  run-up only (pre-fixation):
    slope_norm    ||c1||, length of the fitted per-step vector
    curv_prev     angle between step(i-1) and step(i-2), the bend of the run-up
    runup_disp    ||h_{i-1} - h_{lo}||, net distance covered by the run-up
    last_step     ||h_{i-1} - h_{i-2}||
  target deviation (post-fixation):
    resid_par     residual component along the fitted direction (signed)
    resid_perp    residual component orthogonal to it
    tee           ||residual||  (= sqrt(par^2 + perp^2); checked against the
                  existing onestop_tee_ctx.csv as a pipeline sanity check)

Output: onestop_geometry.csv
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import os, warnings
warnings.filterwarnings("ignore")

HERE = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check")
IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
KEY = ["article_id", "paragraph_id", "difficulty_level"]
LAYER, K = 6, 3
CHUNK, STRIDE = 1024, 512
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

d = pd.read_csv(IA, usecols=KEY + ["IA_ID", "IA_LABEL"], low_memory=False)
paras = (d.drop_duplicates(subset=KEY + ["IA_ID"])
           .sort_values(KEY + ["IA_ID"]).reset_index(drop=True))
del d

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEVICE)
torch.set_num_threads(os.cpu_count() or 4)


def angle(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9:
        return np.nan
    return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1, 1)))


def doc_pass(words):
    ids, final_idx = [], []
    for i, w in enumerate(words):
        t = tok.encode(w if i == 0 else " " + w)
        if not t:
            final_idx.append(None)
            continue
        ids.extend(t)
        final_idx.append(len(ids) - 1)
    n = len(ids)
    hidden, pos = {}, 0
    while pos < n:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            out = model(torch.tensor([ids[pos:end]]).to(DEVICE),
                        output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().cpu().numpy()
        for i in range(end - pos):
            g = pos + i
            if g not in hidden:
                hidden[g] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE

    nw = len(words)
    out = {k: np.full(nw, np.nan) for k in
           ["tee", "slope_norm", "curv_prev", "runup_disp", "last_step",
            "resid_par", "resid_perp"]}
    for i in range(nw):
        lo = max(i - K, 1)
        if i < 4 or (i - lo) < 2:
            continue
        idxs = [final_idx[j] for j in range(lo, i + 1)]
        if any(x is None for x in idxs):
            continue
        H = [hidden[x] for x in idxs]
        Y = np.stack(H[:-1])
        m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        pred = c[0] + c[1] * m
        resid = H[-1] - pred

        slope = c[1]
        sn = float(np.linalg.norm(slope))
        out["slope_norm"][i] = sn
        out["tee"][i] = float(np.linalg.norm(resid))
        if sn > 1e-9:
            u = slope / sn
            par = float(np.dot(resid, u))
            out["resid_par"][i] = par
            out["resid_perp"][i] = float(
                np.linalg.norm(resid - par * u))
        out["runup_disp"][i] = float(np.linalg.norm(Y[-1] - Y[0]))
        if m >= 2:
            out["last_step"][i] = float(np.linalg.norm(Y[-1] - Y[-2]))
        # curvature of the run-up: bend between the two steps ending at i-1
        if lo >= 1 and (i - 1) - 2 >= lo - 1:
            j = i - 1
            tri = [final_idx[j - 2], final_idx[j - 1], final_idx[j]]
            if all(x is not None and x in hidden for x in tri):
                a = hidden[tri[1]] - hidden[tri[0]]
                b = hidden[tri[2]] - hidden[tri[1]]
                out["curv_prev"][i] = angle(a, b)
    return out


rows = []
docs = list(paras.groupby(["article_id", "difficulty_level"], sort=False))
for di, ((aid, lvl), g) in enumerate(docs):
    g = g.sort_values(["paragraph_id", "IA_ID"])
    words = [str(x) for x in g.IA_LABEL.tolist()]
    o = doc_pass(words)
    for j, (_, r) in enumerate(g.iterrows()):
        rec = {"article_id": aid, "paragraph_id": r.paragraph_id,
               "difficulty_level": lvl, "IA_ID": r.IA_ID}
        rec.update({k: o[k][j] for k in o})
        rows.append(rec)
    if (di + 1) % 10 == 0:
        print(f"  {di+1}/{len(docs)} documents", flush=True)

G = pd.DataFrame(rows)
G.to_csv(f"{HERE}/onestop_geometry.csv", index=False)
print(f"\nwrote onestop_geometry.csv  ({len(G):,} rows, "
      f"{G.tee.notna().sum():,} with defined geometry)")

# ---------------- sanity: does this reproduce the existing TEE? ----------
C = pd.read_csv(f"{HERE}/onestop_tee_ctx.csv")
M = G.merge(C, on=KEY + ["IA_ID"], how="inner")
b = M.dropna(subset=["tee", "tee_ctx"])
print(f"\nSANITY vs onestop_tee_ctx.csv:  n = {len(b):,}   "
      f"r = {b.tee.corr(b.tee_ctx):.10f}   "
      f"max|diff| = {(b.tee - b.tee_ctx).abs().max():.2e}")

print("\ncomponent correlations (word level):")
cols = ["tee", "slope_norm", "curv_prev", "runup_disp", "last_step",
        "resid_par", "resid_perp"]
print(G[cols].corr().round(3).to_string())
print("\n  note: slope_norm and curv_prev should be strongly negatively")
print("  related if the geometric mechanism is as described (a bent run-up")
print("  produces a short fitted step).")
