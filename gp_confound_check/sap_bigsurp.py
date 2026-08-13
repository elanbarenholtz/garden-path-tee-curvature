"""
STRONGER SURPRISAL CONTROLS FOR THE SAP CORPUS
==============================================
The objection this addresses: TEE and surprisal both come from GPT-2 Small, so
TEE could be measuring not trajectory geometry but simply WHERE GPT-2 SMALL'S
PROBABILITY ESTIMATE IS BAD. Words the model handles poorly would show both an
off-trajectory hidden state and a mis-estimated surprisal, and controlling for
that same model's surprisal cannot remove the confound because the control is
made of the same error.

Substituting a STRONGER model's surprisal breaks the circularity. If the SAP
effect is a predictability residual, a better predictability estimate should
absorb it.

TEE is left exactly as reported: GPT-2 Small, layer 6, k = 3, sink excluded from
every fit window. Only the surprisal control changes.

Control models: GPT-2 XL (1.5B) and Pythia-410M. Both, so the result cannot
depend on which stronger model is chosen. Pythia additionally differs in
tokenizer, training corpus and positional encoding (RoPE), so it is close to an
independent estimate of predictability rather than a scaled-up GPT-2.

Word-level surprisal = sum of token surprisals over the word's subword tokens,
the same convention used for the GPT-2 Small values throughout this project.

INTERPRETATION FIXED BEFORE RUNNING (see conversation log 2026-08-07):
  - TEE survives at roughly its current magnitude -> the predictability-residual
    account is ruled out; report as a strengthening result.
  - TEE drops substantially -> TEE is partly a proxy for GPT-2 Small's
    estimation error; the claim narrows to that and is reported, not buried.
Either outcome is reported.

Output: sap_bigsurp.csv  (item, Type, WordPosition, surp_xl, surp_pythia410m)
"""

import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
OUT = f"{GP}/sap_bigsurp.csv"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

MODELS = [("surp_xl", "gpt2-xl"),
          ("surp_pythia410m", "EleutherAI/pythia-410m")]


def word_surprisals(words, tok, model):
    """Sum of subword token surprisals (bits) per word."""
    ids, final_idx = [], []
    for i, w in enumerate(words):
        t = tok.encode(w if i == 0 else " " + w, add_special_tokens=False)
        ids.extend(t)
        final_idx.append(len(ids) - 1)
    with torch.no_grad():
        out = model(torch.tensor([ids]).to(DEVICE))
    lp = torch.log_softmax(out.logits[0].float(), -1)
    tok_s = np.zeros(len(ids))
    for t in range(1, len(ids)):
        tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
    starts, prev = [], 0
    for fi in final_idx:
        starts.append(prev)
        prev = fi + 1
    return [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]


d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)

sent_index = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
                .sort_values(["item", "Type", "WordPosition"]))
groups = list(sent_index.groupby(["item", "Type"]))
print(f"sentences: {len(groups)}   "
      f"sentence-words: {len(sent_index):,}")

base = sent_index[["item", "Type", "WordPosition"]].reset_index(drop=True)
res = base.copy()

for col, name in MODELS:
    print(f"\nloading {name} ...")
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name)
    model.eval().to(DEVICE)
    rows = []
    for (item, typ), g in groups:
        words = [str(x) for x in g.EachWord.tolist()]
        s = word_surprisals(words, tok, model)
        for j, (_, r) in enumerate(g.iterrows()):
            rows.append({"item": item, "Type": typ,
                         "WordPosition": r.WordPosition, col: s[j]})
    S = pd.DataFrame(rows)
    n0 = len(res)
    res = res.merge(S, on=["item", "Type", "WordPosition"],
                    how="left", validate="one_to_one")
    assert len(res) == n0
    print(f"  {name}: mean {res[col].mean():.2f} bits   "
          f"sd {res[col].std():.2f}   missing {res[col].isna().sum()}")
    del model, tok
    if DEVICE == "mps":
        torch.mps.empty_cache()

# sanity: correlation with the GPT-2 Small values already cached
small = pd.read_csv(f"{GP}/sap_measures_L6k3.csv")
chk = res.merge(small[["item", "Type", "WordPosition", "surp", "tee"]],
                on=["item", "Type", "WordPosition"], how="left",
                validate="one_to_one")
print("\n" + "=" * 70)
print("SANITY: agreement between surprisal estimates (sentence-word level)")
print("=" * 70)
print(f"  r(GPT-2 Small, GPT-2 XL)      = {chk.surp.corr(chk.surp_xl):+.3f}")
print(f"  r(GPT-2 Small, Pythia-410M)   = "
      f"{chk.surp.corr(chk.surp_pythia410m):+.3f}")
print(f"  r(GPT-2 XL,    Pythia-410M)   = "
      f"{chk.surp_xl.corr(chk.surp_pythia410m):+.3f}")
print("\n  mean surprisal (bits): "
      f"small {chk.surp.mean():.2f}  xl {chk.surp_xl.mean():.2f}  "
      f"pythia {chk.surp_pythia410m.mean():.2f}")
print("  (a stronger model should assign LOWER surprisal on average)")
print("\n  correlation of each surprisal with TEE (GPT-2 Small L6 k=3):")
for c in ["surp", "surp_xl", "surp_pythia410m"]:
    print(f"    r(TEE, {c:<16}) = {chk.tee.corr(chk[c]):+.3f}")

res.to_csv(OUT, index=False)
print(f"\nsaved -> {OUT}   ({len(res):,} rows)")
