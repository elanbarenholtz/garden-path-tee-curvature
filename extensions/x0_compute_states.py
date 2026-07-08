"""
x0: Recompute layer-6 GPT-2 hidden states for all 10 stories with the exact
conventions of the locked sample (compute_curvature.py / e_compute.py):
layer 6, CHUNK 1024, STRIDE 512, first-write-wins, offset BPE->word map,
word anchored at final subword. Validate recomputed tee_k3/tee_k50/final_bpe
against the locked sample, then save states + maps to extensions/states/.
"""
import hashlib, os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
STORIES_DIR = f"{GP}/naturalstories"
OUT = f"{GP}/extensions/states"
os.makedirs(OUT, exist_ok=True)
LAYER, CHUNK_SIZE, STRIDE = 6, 1024, 512

words = pd.read_csv(f"{STORIES_DIR}/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna()].copy()
words = words[words["id"].str.split(".").str[-1] == "whole"].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
words["word_idx"] = words.groupby("story_id").cumcount()
story_ids = sorted(words["story_id"].unique())
story_words = {sid: words.loc[words.story_id == sid, "word"].tolist()
               for sid in story_ids}
story_texts = {sid: " ".join(ws) for sid, ws in story_words.items()}
print(f"corpus: {len(words)} words, stories {story_ids}", flush=True)

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(os.cpu_count() or 4)

def story_pass(text):
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
    n = ids.size(0); hidden = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().cpu().numpy()
        for i in range(end - pos):
            g = pos + i
            if g not in hidden:
                hidden[g] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE
    return hidden, offsets, n

def word_char_spans(word_list):
    spans, cursor = [], 0
    for w in word_list:
        spans.append((cursor, cursor + len(w))); cursor += len(w) + 1
    return spans

def tee_at(H, t, k):
    if t - k < 0 or t >= H.shape[0]:
        return np.nan
    W = H[t - k:t]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(H[t] - (coefs[0] + coefs[1] * k)))

for sid in story_ids:
    text = story_texts[sid]
    hidden, offsets, n_bpe = story_pass(text)
    H = np.stack([hidden[i] for i in range(n_bpe)]).astype(np.float32)
    spans = word_char_spans(story_words[sid])
    bpe_word = np.full(n_bpe, -1); wi = 0
    for bi, (cs, ce) in enumerate(offsets):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            bpe_word[bi] = wi
        else:
            sys.exit(f"BPE offset outside span story {sid} bpe {bi}")
    assert len(np.unique(bpe_word[bpe_word >= 0])) == len(spans)
    last_sub = np.full(len(spans), -1); first_sub = np.full(len(spans), -1)
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            if first_sub[w] < 0:
                first_sub[w] = bi
            last_sub[w] = bi
    np.savez_compressed(f"{OUT}/story{sid}_states.npz", H=H,
                        bpe_word=bpe_word, first_sub=first_sub,
                        last_sub=last_sub)
    print(f"story {sid}: {n_bpe} bpe, {len(spans)} words saved", flush=True)

# ---------- validation against locked sample ----------
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
errs3, errs50, fb_mm = [], [], 0
for sid in story_ids:
    z = np.load(f"{OUT}/story{sid}_states.npz")
    H, ls = z["H"].astype(np.float64), z["last_sub"]
    sub = S[S.story_id == sid]
    for r in sub.itertuples(index=False):
        t = ls[r.word_idx]
        if t != r.final_bpe:
            fb_mm += 1
        errs3.append(abs(tee_at(H, t, 3) - r.tee_k3))
        errs50.append(abs(tee_at(H, t, 50) - r.tee_k50))
print(f"\nVALIDATION (hash {sh}, n={len(S)}):")
print(f"  final_bpe mismatches: {fb_mm}")
print(f"  max |tee_k3  - locked|: {np.nanmax(errs3):.3e}")
print(f"  max |tee_k50 - locked|: {np.nanmax(errs50):.3e}")
ok = fb_mm == 0 and np.nanmax(errs3) < 1e-6 and np.nanmax(errs50) < 1e-6
print("GATE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
