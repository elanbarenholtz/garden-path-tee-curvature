"""
COMPUTE TEE ON THE ONESTOP PARAGRAPHS
=====================================
OneStop Ordinary Reading (360-participant corpus; ordinary-reading subcorpus).
Word sequences are reconstructed from the interest-area report itself
(IA_LABEL ordered by IA_ID within article/paragraph/difficulty), so the TEE
values align to the eye-tracking rows by construction.

Conventions match the locked Natural Stories pipeline:
  GPT-2 small, layer 6, word state = hidden state at the word's FINAL subword,
  TEE_k3 = || h(w) - extrapolate(linear fit over the 3 preceding word states) ||.

Sink handling: paragraphs are fed in isolation, so token 0 is the attention-sink
position. Fit windows are started at word index 1, and only words at index >= 4
are emitted, so no reported value has the sink inside its window.

Surprisal is computed in the same forward pass for internal consistency
(OneStop also ships a precomputed gpt2_surprisal, kept as a cross-check).

Output: onestop_tee.csv  (article_id, paragraph_id, difficulty_level, IA_ID,
        word, tee_k3, surprisal_own, word_idx, n_words)
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import os, warnings
warnings.filterwarnings("ignore")

IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
OUT = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check/onestop_tee.csv")
LAYER, K = 6, 3
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

KEY = ["article_id", "paragraph_id", "difficulty_level"]

print("reading interest-area report (label columns only)...", flush=True)
d = pd.read_csv(IA, usecols=KEY + ["IA_ID", "IA_LABEL"], low_memory=False)
print(f"  {len(d):,} rows", flush=True)

# one row per (paragraph, word position)
paras = (d.drop_duplicates(subset=KEY + ["IA_ID"])
           .sort_values(KEY + ["IA_ID"])
           .reset_index(drop=True))
print(f"  {paras.groupby(KEY).ngroups:,} unique paragraphs, "
      f"{len(paras):,} paragraph-word slots", flush=True)
del d

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEVICE)
torch.set_num_threads(os.cpu_count() or 4)


def tee_for(words):
    """Return per-word (tee_k3, surprisal); NaN where undefined or sink-exposed."""
    ids, final_idx = [], []
    for i, w in enumerate(words):
        piece = w if i == 0 else " " + w
        t = tok.encode(piece)
        if not t:                       # empty label guard
            final_idx.append(None)
            continue
        ids.extend(t)
        final_idx.append(len(ids) - 1)
    if len(ids) < 8:
        return [np.nan] * len(words), [np.nan] * len(words)
    with torch.no_grad():
        out = model(torch.tensor([ids]).to(DEVICE), output_hidden_states=True)
    h = out.hidden_states[LAYER][0].float().cpu().numpy()
    lp = torch.log_softmax(out.logits[0].float(), -1)

    # word-level surprisal (sum of subword surprisals, base 2)
    tok_s = np.zeros(len(ids))
    for t in range(1, len(ids)):
        tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
    starts, prev = [], 0
    for fi in final_idx:
        starts.append(prev)
        if fi is not None:
            prev = fi + 1
    surp = [float(tok_s[s:f + 1].sum()) if f is not None else np.nan
            for s, f in zip(starts, final_idx)]

    wh = np.array([h[fi] if fi is not None else np.full(h.shape[1], np.nan)
                   for fi in final_idx])
    tee = np.full(len(words), np.nan)
    for i in range(len(words)):
        lo = max(i - K, 1)              # never let word 0 into the window
        if i < 4 or (i - lo) < 2 or np.isnan(wh[lo:i + 1]).any():
            continue
        Y = wh[lo:i]
        m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
    return tee, surp


rows = []
groups = list(paras.groupby(KEY, sort=False))
for gi, (key, g) in enumerate(groups):
    words = [str(x) for x in g.IA_LABEL.tolist()]
    tee, surp = tee_for(words)
    for j, (_, r) in enumerate(g.iterrows()):
        rows.append({"article_id": key[0], "paragraph_id": key[1],
                     "difficulty_level": key[2], "IA_ID": r.IA_ID,
                     "word": words[j], "word_idx": j, "n_words": len(words),
                     "tee_k3": tee[j], "surprisal_own": surp[j]})
    if (gi + 1) % 50 == 0:
        print(f"  {gi+1}/{len(groups)} paragraphs", flush=True)

T = pd.DataFrame(rows)
T.to_csv(OUT, index=False)
print(f"\nDONE -> {OUT}")
print(f"  {len(T):,} paragraph-word rows; usable TEE: {T.tee_k3.notna().sum():,}")
print(f"  mean TEE {T.tee_k3.mean():.2f}  sd {T.tee_k3.std():.2f}")
