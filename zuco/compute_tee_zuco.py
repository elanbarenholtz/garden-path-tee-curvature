#!/usr/bin/env python3
"""
Compute sink-controlled TEE (+ same-model surprisal/entropy) per word on the REAL
ZuCo sentences. This REPLACES the earlier zuco_tee.csv, which was accidentally
computed on 3 hardcoded relative-clause example sentences (22 words) and is
therefore meaningless -- the regressor had nothing to do with what subjects read.

ZuCo 1.0 Normal Reading: all subjects read the SAME ~300-400 sentences, so TEE is
computed ONCE from the sentence list (taken from any per-subject CSV produced by
extract_zuco_et.py) and later merged onto every subject's fixations by
(sent_idx, word_idx).

Method (identical to the validated podcast/Natural-Stories definition):
  - GPT-2-small, layer-6 hidden states.
  - Tokenize each sentence with GPT-2 BPE; each word = a contiguous subword span
    (leading space prefix for non-initial words, the GPT-2 convention).
  - TEE at each word's FINAL subword t: OLS-fit the preceding k=3 hidden states,
    extrapolate one step, Euclidean distance to the actual state at t.
  - Surprisal = summed -log2 p over the word's subwords; entropy at final subword.
  - Sentences are processed independently, so token 0 of EACH sentence is the
    attention sink: words whose final subword position < K get TEE = NaN and are
    dropped downstream (this is why word_idx starts at ~3 per sentence).

Output: zuco/zuco_tee.csv
    sent_idx, word_idx, word, tee_k3, surp, entropy, has_trailing_punct
matching the schema the rest of the pipeline already expects.

Usage:
    python3 compute_tee_zuco.py [ET_DIR] [OUT_CSV]
      ET_DIR   dir of per-subject CSVs from extract_zuco_et.py (default: zuco_et)
      OUT_CSV  output path                                     (default: zuco/zuco_tee.csv)
"""
import os, sys, re
import numpy as np
import pandas as pd
import torch
from transformers import GPT2TokenizerFast, GPT2LMHeadModel

ET_DIR = sys.argv[1] if len(sys.argv) > 1 else "zuco_et"
OUT = sys.argv[2] if len(sys.argv) > 2 else "zuco/zuco_tee.csv"
LAYER, K = 6, 3
LN2 = np.log(2)

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(4)


def load_sentences(et_dir):
    """Return {sent_idx: [word0, word1, ...]} from the first per-subject CSV.
    All NR subjects read the same sentences, so one file defines the stimulus."""
    csvs = sorted(f for f in os.listdir(et_dir) if f.endswith(".csv"))
    if not csvs:
        sys.exit(f"no per-subject CSVs in {et_dir!r}; run extract_zuco_et.py first")
    df = pd.read_csv(os.path.join(et_dir, csvs[0]))
    print(f"stimulus from {csvs[0]}: {df.sent_idx.nunique()} sentences, "
          f"{len(df)} words", flush=True)
    sents = {}
    for si, g in df.sort_values(["sent_idx", "word_idx"]).groupby("sent_idx"):
        sents[int(si)] = list(zip(g.word_idx.astype(int), g.word.astype(str)))
    return sents


def tokenize_words(words):
    """words: list of (word_idx, word_str). Returns (ids, spans) where spans[i] =
    (start, end) subword range for words[i], using the GPT-2 leading-space rule."""
    ids, spans = [], []
    for i, (_, w) in enumerate(words):
        piece = (" " + w) if i > 0 else w
        enc = tok.encode(piece)
        spans.append((len(ids), len(ids) + len(enc)))
        ids.extend(enc)
    return ids, spans


def tee_at(hs, t, k=K):
    if t < k:
        return np.nan
    W = hs[t - k:t]                                   # (k, d) preceding states
    A = np.column_stack([np.ones(k), np.arange(k, dtype=float)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    pred = coefs[0] + coefs[1] * k                    # extrapolate one step
    return float(np.linalg.norm(hs[t] - pred))


def main():
    sents = load_sentences(ET_DIR)
    rows = []
    for si in sorted(sents):
        words = sents[si]
        if len(words) < K + 1:
            continue
        ids, spans = tokenize_words(words)
        if len(ids) == 0:
            continue
        with torch.no_grad():
            out = model(torch.tensor(ids).unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].numpy()          # (T, d)
        logits = out.logits[0]
        logp = torch.log_softmax(logits, -1)
        p = torch.softmax(logits, -1)
        ent = (-(p * logp).sum(-1)).numpy()               # next-token entropy per pos
        for (widx, w), (s, e) in zip(words, spans):
            t = e - 1                                     # final subword of the word
            # summed surprisal over the word's subwords (bits); position 0 undefined
            surp = 0.0
            have = False
            for j in range(s, e):
                if j > 0:
                    surp += -logp[j - 1, ids[j]].item() / LN2
                    have = True
            rows.append({
                "sent_idx": si, "word_idx": int(widx), "word": w,
                "tee_k3": tee_at(hs, t),
                "surp": surp if have else np.nan,
                "entropy": float(ent[t]),
                "has_trailing_punct": int(bool(re.search(r"[^A-Za-z0-9]$", w))),
            })
    out = pd.DataFrame(rows)
    keep = out[out.tee_k3.notna()]
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"\n{len(out)} words, TEE non-nan: {len(keep)} "
          f"(dropped {len(out) - len(keep)} sink/early words)", flush=True)
    print(f"corr(TEE, surp)    = {keep[['tee_k3','surp']].corr().iloc[0,1]:+.3f}")
    print(f"corr(TEE, entropy) = {keep[['tee_k3','entropy']].corr().iloc[0,1]:+.3f}")
    print(f"punct-final words  = {int(out.has_trailing_punct.sum())}")
    print(f"\nsaved -> {OUT}")
    print(keep[['sent_idx','word','tee_k3','surp','entropy']].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
