"""
Frank et al. (2015) EEG reading data: GPT-2 measures per word.

Each of the 205 sentences was presented in isolation (RSVP), so each sentence
is its own GPT-2 context: "<|endoftext|>" + sentence. Per word, anchored at
the final subword (same definitions as Natural Stories):
  surprisal   sum of -log p over the word's subwords (nats)
  entropy     entropy of the next-token distribution before the word
  curvature_3 mean turning angle of the layer-6 path over the final 3 subwords
  curvature_1 turning angle at the final subword

Attention sink: the <|endoftext|> state at position 0 is an extreme outlier
(the artifact behind the withdrawn TEE result). curvature_3 at final subword ls
uses states ls-4..ls, so it is set to NaN unless ls-4 >= 1 (sink_clear flag).

Words: the sentence strings from stimuli_erp.mat (punctuation attached, as
presented). Output: frank2015/frank_gpt2_measures.csv (s, w, word, ...).
Usage: FRANK_MAT=/path/stimuli_erp.mat GPT2_PATH=gpt2 python3 f1_compute_measures.py
"""
import os, numpy as np, pandas as pd, torch, scipy.io as sio
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

HERE = os.path.dirname(os.path.abspath(__file__))
MAT = os.environ.get("FRANK_MAT", f"{HERE}/stimuli_erp.mat")
P = os.environ.get("GPT2_PATH", "gpt2")
LAYER = 6
m = sio.loadmat(MAT, squeeze_me=True, struct_as_record=False)
tok = GPT2TokenizerFast.from_pretrained(P)
model = GPT2LMHeadModel.from_pretrained(P).eval()


def ang(H, i):
    a, b = H[i] - H[i - 1], H[i - 1] - H[i - 2]
    return float(np.arccos(np.clip(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))


rows = []
for s, sent in enumerate(m["sentences"], start=1):
    words = [str(w) for w in np.atleast_1d(sent)]
    ids, last, first = [tok.bos_token_id], [], []
    for i, w in enumerate(words):
        t = tok((" " if i else "") + w)["input_ids"]
        first.append(len(ids)); ids += t; last.append(len(ids) - 1)
    with torch.no_grad():
        o = model(torch.tensor([ids]), output_hidden_states=True)
    H = o.hidden_states[LAYER][0].numpy()
    lp = torch.log_softmax(o.logits[0].float(), -1)
    ent = (-(lp.exp() * lp).sum(-1)).numpy()
    for w, word in enumerate(words, start=1):
        f, ls = first[w - 1], last[w - 1]
        surp = float(-sum(lp[j - 1, ids[j]] for j in range(f, ls + 1)))
        clear = ls - 4 >= 1
        rows.append(dict(s=s, w=w, word=word, n_words=len(words), n_sub=ls - f + 1,
                         final_tok=ls, surprisal=surp, entropy=float(ent[f - 1]),
                         sink_clear=int(clear),
                         curvature_3=np.mean([ang(H, j) for j in (ls - 2, ls - 1, ls)]) if clear else np.nan,
                         curvature_1=ang(H, ls) if ls - 2 >= 1 else np.nan))
D = pd.DataFrame(rows)
D.to_csv(f"{HERE}/frank_gpt2_measures.csv", index=False)
print(f"{len(D)} words in {D.s.nunique()} sentences; curvature_3 defined for {D.curvature_3.notna().sum()}")
print(D[["surprisal", "entropy", "curvature_3", "curvature_1"]].describe().round(3))
