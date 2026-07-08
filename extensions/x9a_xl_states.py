"""
x9a: States + surprisal/entropy for a larger GPT-2 (default gpt2-xl), same
corpus/chunking conventions as the locked pipeline. Saves per story:
  H_mid      full BPE states at the mid layer (float32)
  anchors    word-final-subword states at sampled layers (float16)
  maps       bpe_word / first_sub / last_sub
plus a per-word CSV with model-native surprisal (sum of subword -log p, nats)
and entropy (next-token entropy at the position predicting the word's first
subword, nats). When MODEL=gpt2, correlates these definitions against the
locked sample columns as a definition check.
Usage: python3 x9a_xl_states.py [gpt2|gpt2-medium|gpt2-xl]
"""
import os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked

MODEL = sys.argv[1] if len(sys.argv) > 1 else "gpt2-xl"
TAG = MODEL.replace("-", "_")
OUT = f"{GP}/extensions/{TAG}_states"
os.makedirs(OUT, exist_ok=True)
CHUNK_SIZE, STRIDE = 1024, 512
DEV = "mps" if torch.backends.mps.is_available() else "cpu"

S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
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
NLAYER = model.config.n_layer
LAYER_MID = NLAYER // 2
step = max(1, NLAYER // 12)
LAYERS = list(range(0, NLAYER + 1, step))
if LAYERS[-1] != NLAYER:
    LAYERS.append(NLAYER)
print(f"{MODEL} on {DEV}: n_layer={NLAYER} mid={LAYER_MID} "
      f"sweep layers={LAYERS}", flush=True)

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c + len(w))); c += len(w) + 1
    return spans

rows = []
for sid in story_ids:
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
    n = ids.size(0)
    hid_mid, hid_anch, logp, ent = {}, {}, {}, {}
    pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0).to(DEV),
                        output_hidden_states=True)
            hs_mid = out.hidden_states[LAYER_MID][0].float().cpu().numpy()
            hs_anch = np.stack([out.hidden_states[l][0].half().cpu().numpy()
                                for l in LAYERS], axis=1)
            lsm = torch.log_softmax(out.logits[0].float(), dim=-1)
            tgt = ids[pos + 1:end].to(DEV)
            lp = lsm[:-1].gather(1, tgt.unsqueeze(1)).squeeze(1).cpu().numpy()
            en = (-(lsm.exp() * lsm).sum(-1)).cpu().numpy()
        for i in range(end - pos):
            g = pos + i
            if g not in hid_mid:
                hid_mid[g] = hs_mid[i]
                hid_anch[g] = hs_anch[i]
                ent[g] = float(en[i])
            if i < end - pos - 1 and (g + 1) not in logp:
                logp[g + 1] = float(lp[i])
        del out
        if end >= n:
            break
        pos += STRIDE
    H_mid = np.stack([hid_mid[i] for i in range(n)]).astype(np.float32)
    spans = word_char_spans(story_words[sid])
    bpe_word = np.full(n, -1); wi = 0
    for bi, (cs, ce) in enumerate(offsets):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            bpe_word[bi] = wi
    first_sub = np.full(len(spans), -1); last_sub = np.full(len(spans), -1)
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            if first_sub[w] < 0:
                first_sub[w] = bi
            last_sub[w] = bi
    anchors = np.stack([hid_anch[last_sub[w]] for w in range(len(spans))])
    np.savez_compressed(f"{OUT}/story{sid}.npz", H_mid=H_mid,
                        anchors=anchors, bpe_word=bpe_word,
                        first_sub=first_sub, last_sub=last_sub)
    for w in range(len(spans)):
        fs, ls = first_sub[w], last_sub[w]
        srp = (np.nan if fs == 0 else
               -sum(logp.get(b, np.nan) for b in range(fs, ls + 1)))
        e_first = ent[fs - 1] if fs > 0 else np.nan   # predicting first sub
        rows.append({"story_id": sid, "word_idx": w,
                     f"surprisal_{TAG}": srp, f"entropy_{TAG}": e_first})
    print(f"story {sid}: {n} bpe saved", flush=True)

E = pd.DataFrame(rows)
E.to_csv(f"{GP}/extensions/{TAG}_surp_ent.csv", index=False)
if MODEL == "gpt2":
    M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
    ok = M.dropna(subset=[f"surprisal_{TAG}", f"entropy_{TAG}"])
    print("\nDEFINITION CHECK vs locked sample:")
    print(f"  r(surprisal_sum, locked surprisal) = "
          f"{np.corrcoef(ok[f'surprisal_{TAG}'], ok.surprisal)[0,1]:.6f}")
    print(f"  r(entropy_first, locked entropy)   = "
          f"{np.corrcoef(ok[f'entropy_{TAG}'], ok.entropy)[0,1]:.6f}")
print(f"\nDONE {MODEL} hash={sh}")
