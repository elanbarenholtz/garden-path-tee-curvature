"""
Causal downstream-wake measure. For each target word w, ablate it from the
model's context (attention mask zeroes w's subword key positions so no later
token can attend to w) and measure how much the layer-6 hidden state at each
downstream word w+1..w+5 changes relative to the full-context run.

wake(w, L) = || h6_full[w+L] - h6_ablate_w[w+L] ||        (L2)
             1 - cos(h6_full[w+L], h6_ablate_w[w+L])       (cosine)

This is a causal influence measure (intervention, not attention weights).
Positions are preserved (explicit position_ids), so ablation removes w's
CONTENT, not its slot. Window = CTX tokens of left context ending at w, plus
enough downstream tokens to reach w+5's final subword. Internally consistent
(full vs ablated share the window); not compared to the locked tee, so the
fixed-window positions need not match the locked chunking.

Usage: python3 compute_wake.py [STEP]   (systematic every-STEP subsample of the
locked sample; STEP=6 -> ~1640 words. STEP=400 -> ~25 words for a sanity test.)
"""
import sys, unicodedata
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

GP = "/Users/elansmini/Research/Garden_Path"
STORIES_DIR = f"{GP}/naturalstories"
OUT = f"{GP}/tee_vs_curvature"
LAYER, CTX, MAXL = 6, 256, 5
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6

# ---- corpus (same word list/order as compute_curvature.py) ----
words = pd.read_csv(f"{STORIES_DIR}/words.tsv", sep="\t", header=None,
                    names=["id","word"], dtype={"id":str,"word":str})
words = words[words["word"].notna() & (words["id"].str.split(".").str[-1]=="whole")].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+","",regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
words["word_idx"] = words.groupby("story_id").cumcount()
story_ids = sorted(words["story_id"].unique())
story_words = {s: words.loc[words.story_id==s,"word"].tolist() for s in story_ids}
story_texts = {s: " ".join(w) for s,w in story_words.items()}

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c+len(w))); c += len(w)+1
    return spans

def story_bpe_map(sid):
    """token ids + per-word (first_sub, last_sub) via char offsets."""
    text = story_texts[sid]
    enc = tok(text, return_offsets_mapping=True)
    ids = enc["input_ids"]; offs = enc["offset_mapping"]
    spans = word_char_spans(story_words[sid]); n = len(ids)
    bpe_word = np.full(n, -1); wi = 0
    for bi,(cs,ce) in enumerate(offs):
        while cs < ce and text[cs].isspace(): cs += 1
        if ce <= cs: continue
        while wi < len(spans) and cs >= spans[wi][1]: wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            bpe_word[bi] = wi
    first_sub, last_sub = {}, {}
    for bi,w in enumerate(bpe_word):
        if w >= 0:
            first_sub.setdefault(w, bi); last_sub[w] = bi
    return torch.tensor(ids), first_sub, last_sub, len(spans)

@torch.no_grad()
def h6(ids_1d, mask_1d):
    pos = torch.arange(ids_1d.size(0)).unsqueeze(0)
    out = model(ids_1d.unsqueeze(0), attention_mask=mask_1d.unsqueeze(0),
                position_ids=pos, output_hidden_states=True)
    return out.hidden_states[LAYER][0]           # (seq, dim)

# ---- target words: systematic subsample of the locked sample ----
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
S = S.sort_values(["story_id","word_idx"]).reset_index(drop=True)
targets = S.iloc[::STEP][["story_id","word_idx"]].copy()
print(f"STEP={STEP}  target words: {len(targets)}", flush=True)

rows = []
for sid in story_ids:
    ids, first_sub, last_sub, nw = story_bpe_map(sid)
    tg = targets[targets.story_id==sid].word_idx.tolist()
    for w in tg:
        if w+MAXL >= nw:            # need 5 downstream words in-story
            continue
        ls = last_sub[w]
        end = last_sub[w+MAXL]
        start = max(0, ls-CTX+1)
        win = ids[start:end+1]
        full_mask = torch.ones(win.size(0), dtype=torch.long)
        ab_mask = full_mask.clone()
        for b in range(first_sub[w]-start, ls-start+1):   # mask w's subwords
            ab_mask[b] = 0
        hf = h6(win, full_mask); ha = h6(win, ab_mask)
        rec = {"story_id": sid, "word_idx": w}
        for L in range(1, MAXL+1):
            m = last_sub[w+L] - start
            d = (hf[m]-ha[m]); nf = hf[m].norm().item()
            rec[f"wake_L2_{L}"] = d.norm().item()
            rec[f"wake_rel_{L}"] = d.norm().item()/nf if nf>0 else np.nan
            cos = torch.nn.functional.cosine_similarity(hf[m], ha[m], dim=0).item()
            rec[f"wake_cos_{L}"] = 1.0 - cos
        rows.append(rec)
    print(f"story {sid}: {len(tg)} targets done", flush=True)

W = pd.DataFrame(rows)
outfile = f"{OUT}/wake_step{STEP}.csv"
W.to_csv(outfile, index=False)
print(f"\nn = {len(W)}  ->  {outfile}")
print("\nmean relative wake by lag (should be large at L1, decay):")
for L in range(1, MAXL+1):
    print(f"  L{L}: rel={W[f'wake_rel_{L}'].mean():.4f}  cos={W[f'wake_cos_{L}'].mean():.4f}")
