"""
x3: Causal wake at fine AND coarse (neighborhood) scale, MAXL=10.
Ablation identical to parent compute_wake.py (attention-mask zeroes target
word's subword keys, positions preserved, CTX=256 left context). New DVs:
  wake_rel_L        fine: relative L2 perturbation of layer-6 state at w+L
  wake_coarse_L     neighborhood: rel. perturbation of the trailing mean of
                    the last min(5,L) DOWNSTREAM word states (words w+1..w+L;
                    the ablated word itself is never averaged in)
  wake_nbhd_L       Hellinger distance between k=100 soft cluster assignments
                    of full vs ablated state at w+L
  wake_switch_L     hard: nearest centroid changed (0/1)
Usage: python3 x3_coarse_wake.py [STEP=6]
Output: extensions/wake_coarse_step{STEP}.csv
"""
import os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, load_states
from sklearn.cluster import KMeans

LAYER, CTX, MAXL = 6, 256, 10
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())

# corpus text (identical construction to parent)
words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna() &
              (words["id"].str.split(".").str[-1] == "whole")].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
story_words = {s: words.loc[words.story_id == s, "word"].tolist()
               for s in story_ids}
story_texts = {s: " ".join(w) for s, w in story_words.items()}

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(os.cpu_count() or 4)

# k=100 neighborhoods, same fit as x1 (same data order, same seed)
ALL = np.vstack([load_states(sid)[0][load_states(sid)[3]]
                 for sid in story_ids])
km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(ALL)
CENT = km.cluster_centers_
d_nn = np.linalg.norm(ALL[:, None, :] - CENT[None], axis=-1).min(1)
SIG = float(np.median(d_nn))
print(f"kmeans k=100 refit; sigma={SIG:.3f}", flush=True)

def soft1(x):
    d = np.linalg.norm(CENT - x, axis=1)
    p = np.exp(-(d ** 2) / (2 * SIG ** 2)); p /= p.sum()
    return p, int(d.argmin())

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c + len(w))); c += len(w) + 1
    return spans

def story_bpe_map(sid):
    text = story_texts[sid]
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
def h6(ids_1d, mask_1d):
    pos = torch.arange(ids_1d.size(0)).unsqueeze(0)
    out = model(ids_1d.unsqueeze(0), attention_mask=mask_1d.unsqueeze(0),
                position_ids=pos, output_hidden_states=True)
    return out.hidden_states[LAYER][0]

Ss = S.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
targets = Ss.iloc[::STEP][["story_id", "word_idx"]].copy()
print(f"STEP={STEP} target words: {len(targets)}", flush=True)

rows = []
for sid in story_ids:
    ids, first_sub, last_sub, nw = story_bpe_map(sid)
    tg = targets[targets.story_id == sid].word_idx.tolist()
    done = 0
    for w in tg:
        if w + MAXL >= nw:
            continue
        ls = last_sub[w]
        end = last_sub[w + MAXL]
        start = max(0, ls - CTX + 1)
        win = ids[start:end + 1]
        full_mask = torch.ones(win.size(0), dtype=torch.long)
        ab_mask = full_mask.clone()
        for b in range(first_sub[w] - start, ls - start + 1):
            ab_mask[b] = 0
        hf = h6(win, full_mask).double().numpy()
        ha = h6(win, ab_mask).double().numpy()
        rec = {"story_id": sid, "word_idx": w}
        f_states, a_states = [], []   # downstream word-final states w+1..w+L
        for L in range(1, MAXL + 1):
            m = last_sub[w + L] - start
            f_states.append(hf[m]); a_states.append(ha[m])
            d = hf[m] - ha[m]; nf = np.linalg.norm(hf[m])
            rec[f"wake_rel_{L}"] = float(np.linalg.norm(d) / nf) if nf > 0 \
                else np.nan
            cf = np.mean(f_states[-5:], axis=0)
            ca = np.mean(a_states[-5:], axis=0)
            ncf = np.linalg.norm(cf)
            rec[f"wake_coarse_{L}"] = float(np.linalg.norm(cf - ca) / ncf) \
                if ncf > 0 else np.nan
            pf, kf = soft1(hf[m]); pa, ka = soft1(ha[m])
            rec[f"wake_nbhd_{L}"] = float(np.linalg.norm(
                np.sqrt(pf) - np.sqrt(pa)) / np.sqrt(2))
            rec[f"wake_switch_{L}"] = float(kf != ka)
        rows.append(rec); done += 1
    print(f"story {sid}: {done} targets done", flush=True)

W = pd.DataFrame(rows)
out = f"{GP}/extensions/wake_coarse_step{STEP}.csv"
W.to_csv(out, index=False)
print(f"\nn = {len(W)} -> {out}")
for L in range(1, MAXL + 1):
    print(f"  L{L}: rel={W[f'wake_rel_{L}'].mean():.4f} "
          f"coarse={W[f'wake_coarse_{L}'].mean():.4f} "
          f"nbhd={W[f'wake_nbhd_{L}'].mean():.4f} "
          f"switch={W[f'wake_switch_{L}'].mean():.3f}")
