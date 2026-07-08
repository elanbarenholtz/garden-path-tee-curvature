"""
x9b: XL causal wake (mid layer), STEP=12 subsample, MAXL=10, CTX=256 —
identical ablation to x3 but on gpt2-xl with MPS. DVs: wake_rel_L (fine) and
wake_nbhd_L (Hellinger shift of k=100 soft assignment, centroids from x9c).
Usage: python3 x9b_xl_wake.py [STEP=12] [gpt2-xl]
"""
import os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked

STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 12
MODEL = sys.argv[2] if len(sys.argv) > 2 else "gpt2-xl"
TAG = MODEL.replace("-", "_")
CTX, MAXL = 256, 10
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())

KM = np.load(f"{GP}/extensions/{TAG}_kmeans_mid.npz")
CENT, SIG = KM["centroids"], float(KM["sigma"])

words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna() &
              (words["id"].str.split(".").str[-1] == "whole")].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
story_words = {s: words.loc[words.story_id == s, "word"].tolist()
               for s in story_ids}

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained(MODEL).eval().to(DEV)
LAYER_MID = model.config.n_layer // 2
print(f"{MODEL} on {DEV}, wake at layer {LAYER_MID}, STEP={STEP}", flush=True)

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c + len(w))); c += len(w) + 1
    return spans

def story_bpe_map(sid):
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = enc["input_ids"]; offs = enc["offset_mapping"]
    spans = word_char_spans(story_words[sid]); n = len(ids)
    bpe_word = np.full(n, -1); wi = 0
    for bi, (cs, ce) in enumerate(offs):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            bpe_word[bi] = wi
    first_sub, last_sub = {}, {}
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            first_sub.setdefault(w, bi); last_sub[w] = bi
    return torch.tensor(ids), first_sub, last_sub, len(spans)

@torch.no_grad()
def hmid(ids_1d, mask_1d):
    pos = torch.arange(ids_1d.size(0)).unsqueeze(0).to(DEV)
    out = model(ids_1d.unsqueeze(0).to(DEV),
                attention_mask=mask_1d.unsqueeze(0).to(DEV),
                position_ids=pos, output_hidden_states=True)
    return out.hidden_states[LAYER_MID][0].float().cpu().numpy()

def soft1(x):
    d = np.linalg.norm(CENT - x, axis=1)
    p = np.exp(-(d ** 2) / (2 * SIG ** 2)); p /= p.sum()
    return p

Ss = S.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
targets = Ss.iloc[::STEP][["story_id", "word_idx"]].copy()
print(f"targets: {len(targets)}", flush=True)

rows = []
for sid in story_ids:
    ids, first_sub, last_sub, nw = story_bpe_map(sid)
    tg = targets[targets.story_id == sid].word_idx.tolist()
    done = 0
    for w in tg:
        if w + MAXL >= nw:
            continue
        ls = last_sub[w]; end = last_sub[w + MAXL]
        start = max(0, ls - CTX + 1)
        win = ids[start:end + 1]
        fm = torch.ones(win.size(0), dtype=torch.long)
        am = fm.clone()
        for b in range(first_sub[w] - start, ls - start + 1):
            am[b] = 0
        hf = hmid(win, fm); ha = hmid(win, am)
        rec = {"story_id": sid, "word_idx": w}
        for L in range(1, MAXL + 1):
            m = last_sub[w + L] - start
            d = hf[m] - ha[m]; nf = np.linalg.norm(hf[m])
            rec[f"wake_rel_{L}"] = float(np.linalg.norm(d) / nf) \
                if nf > 0 else np.nan
            pf, pa = soft1(hf[m]), soft1(ha[m])
            rec[f"wake_nbhd_{L}"] = float(np.linalg.norm(
                np.sqrt(pf) - np.sqrt(pa)) / np.sqrt(2))
        rows.append(rec); done += 1
    print(f"story {sid}: {done} done", flush=True)

W = pd.DataFrame(rows)
W.to_csv(f"{GP}/extensions/{TAG}_wake_step{STEP}.csv", index=False)
print(f"\nn={len(W)} -> {TAG}_wake_step{STEP}.csv")
for L in range(1, MAXL + 1):
    print(f"  L{L}: rel={W[f'wake_rel_{L}'].mean():.4f} "
          f"nbhd={W[f'wake_nbhd_{L}'].mean():.4f}")
