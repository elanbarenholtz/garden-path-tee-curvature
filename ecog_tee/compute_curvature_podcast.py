"""
Curvature per word on the ds005574 podcast transcript (GPT-2 small, layer 6),
anchored at each word's final subword: the same definition and chunking as
tee_vs_curvature/compute_curvature.py (Natural Stories).

Source: podcast_tee.csv (words + final_tok from the original transcript
token stream). The token stream is rebuilt by tokenising the words joined with
single spaces; GATE: the rebuilt final-token index must equal final_tok for
every word, i.e. the stream is identical to the transcript's token_id column.
If transcript.tsv is available (TRANSCRIPT env var), its token_id column is
used directly instead and the gate compares the two.

Output: podcast_curvature.csv = podcast_tee.csv + curvature_1, curvature_3
Usage: GPT2_PATH=gpt2 python3 compute_curvature_podcast.py
"""
import os, sys, numpy as np, pandas as pd, torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.environ.get("GPT2_PATH", "gpt2")
LAYER, CHUNK, STRIDE = 6, 1024, 512
W = pd.read_csv(f"{HERE}/podcast_tee.csv")
tok = GPT2TokenizerFast.from_pretrained(P)
model = GPT2LMHeadModel.from_pretrained(P).eval()
torch.set_num_threads(os.cpu_count() or 4)

ids, last = [], []
for i, w in enumerate(W.word.astype(str)):
    ids += tok(w if i == 0 else " " + w)["input_ids"]
    last.append(len(ids) - 1)
last = np.array(last)
if os.environ.get("TRANSCRIPT"):
    T = pd.read_csv(os.environ["TRANSCRIPT"], sep="\t", index_col=0)
    assert (T.token_id.to_numpy() == np.array(ids)).all(), "token stream differs from transcript"
mism = (last != W.final_tok.to_numpy()).sum()
print(f"{len(W)} words, {len(ids)} tokens; final_tok mismatches: {mism}")
if mism:
    j = np.where(last != W.final_tok.to_numpy())[0][0]
    sys.exit(f"GATE FAIL at word {j} {W.word[j]!r}: rebuilt {last[j]} vs {W.final_tok[j]}")

ids_t = torch.tensor(ids); n = len(ids); H = {}; pos = 0
while True:
    end = min(pos + CHUNK, n)
    with torch.no_grad():
        hs = model(ids_t[pos:end].unsqueeze(0), output_hidden_states=True
                   ).hidden_states[LAYER][0].numpy()
    for i in range(end - pos):
        H.setdefault(pos + i, hs[i])
    if end >= n:
        break
    pos += STRIDE


def ang(i):
    if i < 2:
        return np.nan
    a, b = H[i] - H[i - 1], H[i - 1] - H[i - 2]
    return float(np.arccos(np.clip(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))


W["curvature_1"] = [ang(t) for t in last]
W["curvature_3"] = [np.mean([ang(t - 2), ang(t - 1), ang(t)]) if t >= 4 else np.nan for t in last]
W.to_csv(f"{HERE}/podcast_curvature.csv", index=False)
print(W[["curvature_3", "tee_k3", "surp_small", "entropy_small", "surp_xl"]].corr().round(3))
print(f"curvature_3 by trailing punctuation:\n{W.groupby('has_trailing_punct').curvature_3.describe().round(3)}")
print("wrote podcast_curvature.csv")
