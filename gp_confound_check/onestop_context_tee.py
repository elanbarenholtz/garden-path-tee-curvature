"""
DOES THE ONESTOP REVERSAL COME FROM MISSING CONTEXT?
====================================================
The Natural Stories TEE was computed over whole stories (1024-token chunks,
stride 512), so a word deep in a story has hundreds of words of preceding
context. My first OneStop pass fed each paragraph in ISOLATION -- at most ~120
words, and near-zero for words early in a paragraph.

That is a real difference between the two pipelines, and readers in OneStop do
see the preceding paragraphs (they read each article sequentially).

This script recomputes TEE and surprisal with ARTICLE-LEVEL context: paragraphs
of the same article and difficulty level concatenated in order, one forward
pass per article, values emitted per paragraph-word.

Diagnostics:
  1. r(my surprisal, OneStop gpt2_surprisal) under isolated vs article context,
     overall and by position within paragraph. If OneStop used larger context,
     the article-context version should agree better, especially early in a
     paragraph.
  2. r(TEE isolated, TEE article-context) -- how much does context change it?

Output: onestop_tee_ctx.csv
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

d = pd.read_csv(IA, usecols=KEY + ["IA_ID", "IA_LABEL", "gpt2_surprisal"],
                low_memory=False)
paras = (d.drop_duplicates(subset=KEY + ["IA_ID"])
           .sort_values(KEY + ["IA_ID"]).reset_index(drop=True))
del d

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEVICE)
torch.set_num_threads(os.cpu_count() or 4)


def doc_pass(words):
    """Chunked forward pass over a whole document; first-write-wins, matching
    the Natural Stories convention. Returns per-word (tee, surprisal)."""
    ids, final_idx = [], []
    for i, w in enumerate(words):
        t = tok.encode(w if i == 0 else " " + w)
        if not t:
            final_idx.append(None)
            continue
        ids.extend(t)
        final_idx.append(len(ids) - 1)
    n = len(ids)
    hidden, logits = {}, {}
    pos = 0
    while pos < n:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            out = model(torch.tensor([ids[pos:end]]).to(DEVICE),
                        output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().cpu().numpy()
        lp = torch.log_softmax(out.logits[0].float(), -1).cpu().numpy()
        for i in range(end - pos):
            g = pos + i
            if g not in hidden:
                hidden[g] = hs[i]
                logits[g] = lp[i]
        del out
        if end >= n:
            break
        pos += STRIDE

    tok_s = np.zeros(n)
    for t in range(1, n):
        tok_s[t] = -float(logits[t - 1][ids[t]]) / np.log(2)
    starts, prev = [], 0
    for fi in final_idx:
        starts.append(prev)
        if fi is not None:
            prev = fi + 1
    surp = [float(tok_s[s:f + 1].sum()) if f is not None else np.nan
            for s, f in zip(starts, final_idx)]

    tee = np.full(len(words), np.nan)
    for i in range(len(words)):
        lo = max(i - K, 1)
        if i < 4 or (i - lo) < 2:
            continue
        idxs = [final_idx[j] for j in range(lo, i + 1)]
        if any(x is None for x in idxs):
            continue
        Y = np.stack([hidden[x] for x in idxs[:-1]])
        m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[i] = float(np.linalg.norm(hidden[idxs[-1]] - (c[0] + c[1] * m)))
    return tee, surp


rows = []
docs = list(paras.groupby(["article_id", "difficulty_level"], sort=False))
for di, ((aid, lvl), g) in enumerate(docs):
    g = g.sort_values(["paragraph_id", "IA_ID"])
    words = [str(x) for x in g.IA_LABEL.tolist()]
    tee, surp = doc_pass(words)
    for j, (_, r) in enumerate(g.iterrows()):
        rows.append({"article_id": aid, "paragraph_id": r.paragraph_id,
                     "difficulty_level": lvl, "IA_ID": r.IA_ID,
                     "tee_ctx": tee[j], "surprisal_ctx": surp[j]})
    if (di + 1) % 10 == 0:
        print(f"  {di+1}/{len(docs)} documents", flush=True)

C = pd.DataFrame(rows)
C.to_csv(f"{HERE}/onestop_tee_ctx.csv", index=False)

# ---- diagnostics ----
iso = pd.read_csv(f"{HERE}/onestop_tee.csv")
ref = paras.copy()
ref["gpt2_surprisal"] = pd.to_numeric(ref.gpt2_surprisal, errors="coerce")
M = (iso.merge(C, on=KEY + ["IA_ID"])
        .merge(ref[KEY + ["IA_ID", "gpt2_surprisal"]], on=KEY + ["IA_ID"]))
ok = M.dropna(subset=["gpt2_surprisal", "surprisal_own", "surprisal_ctx"])
print(f"\nn = {len(ok):,}")
print(f"r(OneStop surprisal, mine ISOLATED)        = "
      f"{ok.surprisal_own.corr(ok.gpt2_surprisal):.4f}")
print(f"r(OneStop surprisal, mine ARTICLE CONTEXT) = "
      f"{ok.surprisal_ctx.corr(ok.gpt2_surprisal):.4f}")
print(f"r(TEE isolated, TEE article-context)       = "
      f"{M.tee_k3.corr(M.tee_ctx):.4f}")
print("\nby position within paragraph:")
M["bin"] = pd.cut(M.word_idx, [-1, 9, 29, 59, 9999],
                  labels=["0-9", "10-29", "30-59", "60+"])
for b, s in M.groupby("bin", observed=True):
    s = s.dropna(subset=["gpt2_surprisal", "surprisal_own", "surprisal_ctx"])
    print(f"  {str(b):>6}  n={len(s):>6,}  r(iso)={s.surprisal_own.corr(s.gpt2_surprisal):.3f}"
          f"   r(ctx)={s.surprisal_ctx.corr(s.gpt2_surprisal):.3f}")
