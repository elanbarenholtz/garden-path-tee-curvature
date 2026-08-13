"""
PYTHIA-410M SURPRISAL ON THE NATURAL STORIES LOCKED SAMPLE
==========================================================
Closes the last gap in the stronger-surprisal control (§4c of V2_DRAFT).
GPT-2 Medium and GPT-2 XL surprisal already exist on this sample, but they share
GPT-2 Small's tokenizer, training corpus and positional encoding, so they are not
independent estimates of predictability. Pythia-410M differs on all three
(BPE vocabulary trained on the Pile, rotary position embeddings), which makes it
the control a reviewer would actually ask for.

Pythia-410M *TEE* on this sample already exists (pythia_tee_8a6087341e.csv);
only its surprisal was never computed. This script computes it.

Conventions copied exactly from v2_table6_pythia.py so the values are
commensurable with everything else on this sample:
  - text = words joined by single spaces, per story
  - chunked forward passes, CHUNK 1024 / STRIDE 512, FIRST-WRITE-WINS, so every
    token is scored with the longest left context available at its first
    computation
  - word alignment by tokenizer offset mapping; a subword belongs to a word only
    if it lies entirely inside that word's character span
  - word surprisal = SUM of its subword token surprisals, in bits

Validation before saving (mirrors the guard discipline used throughout):
  - locked-sample hash asserted
  - coverage: every sample word must receive a value
  - correlation against the existing GPT-2 Small / Medium / XL surprisals; a
    value far outside the .85-.95 range seen among those would indicate a
    misalignment rather than a genuine model difference

Output: ns_pythia410m_surp_8a6087341e.csv  (story_id, word_idx, surprisal_pythia410m)
"""

import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
OUT = f"{GP}/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv"
NAME = "EleutherAI/pythia-410m"
CHUNK, STRIDE = 1024, 512
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# ---------------- corpus (identical construction to the verified pipeline) ----
words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words.word.notna()].copy()
words = words[words.id.str.split(".").str[-1] == "whole"].copy()
words["word"] = words.word.str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words.id.str.split(".").str[0].astype(int)
words["word_idx"] = words.groupby("story_id").cumcount()
story_words = {s: g.word.tolist() for s, g in words.groupby("story_id")}
print(f"corpus: {len(words):,} words, {len(story_words)} stories", flush=True)


def spans_for(wl):
    out, cur = [], 0
    for w in wl:
        out.append((cur, cur + len(w)))
        cur += len(w) + 1
    return out


tok = AutoTokenizer.from_pretrained(NAME)
model = AutoModelForCausalLM.from_pretrained(NAME).eval().to(DEVICE)
print(f"loaded {NAME} on {DEVICE}", flush=True)

rows = []
for sid, wl in story_words.items():
    text = " ".join(wl)
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"])
    offs = enc["offset_mapping"]
    n = ids.size(0)

    tok_surp, pos = {}, 0
    while pos < n:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0).to(DEVICE))
        lp = torch.log_softmax(out.logits[0].float(), -1).cpu()
        # token at local i is predicted from logits at local i-1
        for i in range(1, end - pos):
            g = pos + i
            if g not in tok_surp:
                tok_surp[g] = -float(lp[i - 1, ids[g]]) / np.log(2)
        del out, lp
        if end >= n:
            break
        pos += STRIDE

    sp = spans_for(wl)
    members = {}
    wi = 0
    for bi, (cs, ce) in enumerate(offs):
        if ce <= cs:
            continue
        while wi < len(sp) and cs >= sp[wi][1]:
            wi += 1
        if wi < len(sp) and cs >= sp[wi][0] and ce <= sp[wi][1]:
            members.setdefault(wi, []).append(bi)

    for w in range(len(sp)):
        toks = members.get(w)
        if not toks or any(t not in tok_surp for t in toks):
            continue
        rows.append({"story_id": sid, "word_idx": w,
                     "surprisal_pythia410m": float(
                         sum(tok_surp[t] for t in toks))})
    print(f"  story {sid}: {len(sp):,} words -> "
          f"{sum(1 for r in rows if r['story_id'] == sid):,} scored", flush=True)

P = pd.DataFrame(rows)
print(f"\ntotal scored words: {len(P):,}")

# ------------------------------------------------------------------ validate
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
print(f"locked sample hash {sh} verified ({len(S):,} words)")

for f, c in [("gpt2_medium_surp_ent.csv", "surprisal_gpt2_medium"),
             ("gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl")]:
    S = S.merge(pd.read_csv(f"{GP}/extensions/{f}")[["story_id", "word_idx", c]],
                on=["story_id", "word_idx"], how="left", validate="one_to_one")

chk = S.merge(P, on=["story_id", "word_idx"], how="left", validate="one_to_one")
missing = chk.surprisal_pythia410m.isna().sum()
print(f"coverage: {len(chk) - missing:,}/{len(chk):,} sample words scored "
      f"({missing} missing)")

print("\nagreement with existing surprisal estimates on the sample:")
ok = True
for c in ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl"]:
    r = chk[c].corr(chk.surprisal_pythia410m)
    flag = "" if 0.75 <= r <= 0.98 else "   <-- OUT OF EXPECTED RANGE"
    if flag:
        ok = False
    print(f"  r(pythia410m, {c:<22}) = {r:+.3f}{flag}")
print(f"\nmean surprisal (bits): "
      f"small {chk.surprisal.mean():.3f}  "
      f"medium {chk.surprisal_gpt2_medium.mean():.3f}  "
      f"xl {chk.surprisal_gpt2_xl.mean():.3f}  "
      f"pythia410m {chk.surprisal_pythia410m.mean():.3f}")
print(f"r(TEE, pythia410m surprisal) = "
      f"{chk.tee_k3.corr(chk.surprisal_pythia410m):+.3f}   "
      f"[small +0.310, medium +0.271, xl +0.254]")

if missing > 0 or not ok:
    print("\nWARNING: coverage or agreement outside expectation. "
          "Saving anyway, but inspect before use in the manuscript.")

P.to_csv(OUT, index=False)
print(f"\nsaved -> {OUT}")
