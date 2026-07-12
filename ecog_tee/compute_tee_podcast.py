"""
Compute sink-controlled TEE (and same-model surprisal/entropy) per word on the
ds005574 podcast transcript, for the ECoG x TEE correspondence test.

The transcript's token_id column is GPT-2 BPE (same tokenizer for small/XL), and
word_idx maps each token to its word. So we run GPT-2-small over that exact token
stream (chunk 1024 / stride 512, first-write-wins), take layer-6 hidden states,
and compute TEE at each word's FINAL subword (matching the manuscript definition):
OLS-fit preceding k=3 states, extrapolate one step, Euclidean distance to actual.

Continuous stream => the token-0 attention sink touches only the first few words
(negligible over ~5k words). The relevant confound is punctuation-final words
(transcript glues punctuation on, e.g. "one,"); flagged as has_trailing_punct.

Output: podcast_tee.csv  (word_idx, word, start, end, tee_k3, has_trailing_punct,
surp_small, entropy_small, surp_xl)  aligned to df_word by word_idx.
"""
import numpy as np, pandas as pd, torch, re
from transformers import GPT2LMHeadModel

D = "/Users/elansmini/Research/Garden_Path/data/zou2026"
LAYER, CHUNK, STRIDE, K = 6, 1024, 512, 3

df = pd.read_csv(f"{D}/transcript.tsv", sep="\t", index_col=0)
ids = df["token_id"].to_numpy()
widx = df["word_idx"].to_numpy()
n = len(ids)
print(f"transcript: {n} tokens, {df.word_idx.nunique()} words")

model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(4)

hidden = {}
tok_surp = np.full(n, np.nan)
tok_ent = np.full(n, np.nan)
pos = 0
while pos < n:
    end = min(pos + CHUNK, n)
    chunk = torch.tensor(ids[pos:end]).unsqueeze(0)
    with torch.no_grad():
        out = model(chunk, output_hidden_states=True)
    hs = out.hidden_states[LAYER][0].numpy()
    logits = out.logits[0]
    logp = torch.log_softmax(logits, -1)
    p = torch.softmax(logits, -1)
    ent = -(p * logp).sum(-1).numpy()            # entropy of next-token dist at each pos
    ks = 0 if pos == 0 else STRIDE // 2
    for i in range(end - pos):
        g = pos + i
        if g not in hidden:
            hidden[g] = hs[i]
            # surprisal of token g = -logprob(token g | prev), read from position g-1
            if g > 0 and (g - 1) >= pos:
                tok_surp[g] = -logp[i - 1, ids[g]].item() / np.log(2)  # bits
            if i < end - pos:
                tok_ent[g] = ent[i]
    if end >= n:
        break
    pos += STRIDE

def tee_at(t, k=K):
    idxs = range(t - k, t)
    if t < k or any(j not in hidden for j in idxs) or t not in hidden:
        return np.nan
    W = np.stack([hidden[j] for j in idxs])
    A = np.column_stack([np.ones(k), np.arange(k, dtype=float)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(hidden[t] - (coefs[0] + coefs[1] * k)))

# per word: final subword = last token row of that word_idx
dfw = df.groupby("word_idx").agg(word=("word", "first"), start=("start", "first"),
                                 end=("end", "last")).reset_index()
last_tok = {}
for row_i, w in enumerate(widx):
    last_tok[w] = row_i            # row index in token stream (0..n-1) == hidden key
rows = []
for _, r in dfw.iterrows():
    w = int(r.word_idx); ft = last_tok[w]
    # sum surprisal over the word's subwords; final-subword TEE
    sub_rows = np.where(widx == w)[0]
    surp_small = np.nansum(tok_surp[sub_rows]) if len(sub_rows) else np.nan
    wordstr = str(r.word)
    rows.append({"word_idx": w, "word": wordstr, "start": r.start, "end": r.end,
                 "final_tok": ft, "tee_k3": tee_at(ft),
                 "has_trailing_punct": int(bool(re.search(r"[^A-Za-z0-9]$", wordstr))),
                 "surp_small": surp_small,
                 "entropy_small": tok_ent[ft]})
out = pd.DataFrame(rows)

# same-word gpt2-xl surprisal from transcript (true_prob), summed over subwords
xl = df.copy()
xl["surp_xl"] = -np.log2(xl["true_prob"].clip(lower=1e-12))
xl_w = xl.groupby("word_idx").agg(surp_xl=("surp_xl", "sum")).reset_index()
out = out.merge(xl_w, on="word_idx", how="left")

out.to_csv(f"{D}/podcast_tee.csv", index=False)
print(f"words: {len(out)}  TEE non-nan: {out.tee_k3.notna().sum()}  "
      f"punct-final: {out.has_trailing_punct.sum()}")
print(f"corr(TEE, surp_small) = {out[['tee_k3','surp_small']].corr().iloc[0,1]:+.3f}"
      f"   corr(TEE, surp_xl) = {out[['tee_k3','surp_xl']].corr().iloc[0,1]:+.3f}")
print(out[["word","tee_k3","surp_small","surp_xl","has_trailing_punct"]].head(8).to_string())
print(f"\nsaved podcast_tee.csv")
