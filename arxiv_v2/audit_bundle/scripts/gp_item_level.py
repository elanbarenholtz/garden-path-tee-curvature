"""
THE TEST THE ORIGINAL INTUITION ACTUALLY IMPLIES
================================================
The paper asked: does TEE predict word-by-word RT inside the critical region?
The motivating intuition was different and stronger: in a garden-path sentence
the accumulated trajectory reverses at the disambiguating word, and THAT is what
costs the reader. If so, items whose TEE is disrupted more by the ambiguity
should show a bigger human garden-path effect.

That is an ITEM-LEVEL question about the ambiguous-minus-unambiguous DIFFERENCE,
not a word-level question about RT. It was never tested.

  Predictor:  dTEE_i  = TEE(ambiguous) - TEE(unambiguous)   at the disambiguating word
  Outcome:    dRT_i   = mean logRT(ambiguous) - mean logRT(unambiguous)
  Control:    dSurp_i = surprisal(ambiguous) - surprisal(unambiguous)

24 items x 3 constructions = 72 item-condition pairs. Underpowered by design;
reported as such.

TEE computed with the sink excluded from every fit window (windows start at
word index 1), GPT-2 small layer 6, k=3, word states at final subword.
Both ROI 0 (the disambiguating word) and the pooled critical region are tested.
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from scipy import stats
import statsmodels.formula.api as smf
import os, warnings
warnings.filterwarnings("ignore")

RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
LAYER, K = 6, 3
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

tokz = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)


def measures(words):
    ids, final_idx = [], []
    for i, w in enumerate(words):
        t = tokz.encode(w if i == 0 else " " + w)
        ids.extend(t)
        final_idx.append(len(ids) - 1)
    with torch.no_grad():
        out = model(torch.tensor([ids]).to(DEVICE))
    h = out.hidden_states[LAYER][0].float().cpu().numpy()
    lp = torch.log_softmax(out.logits[0].float(), -1)
    tok_s = np.zeros(len(ids))
    for t in range(1, len(ids)):
        tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
    starts, prev = [], 0
    for fi in final_idx:
        starts.append(prev); prev = fi + 1
    surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
    wh = h[final_idx]
    tee = np.full(len(words), np.nan)
    for i in range(len(words)):
        lo = max(i - K, 1)                      # sink never inside the window
        if i < 4 or (i - lo) < 2:
            continue
        Y = wh[lo:i]; m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
    return tee, surp


# ---------- human garden-path effect, per item x construction ----------
d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].str.replace("%2C", ",", regex=False)
d = d[(d.RT > 100) & (d.RT < 5000)].copy()
d["log_RT"] = np.log(d.RT)
d["amb"] = (d.AMBUAMB == 1).astype(int)     # 1 = ambiguous

# ---------- model measures per sentence ----------
sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
           .sort_values(["item", "Type", "WordPosition"])
           .groupby(["item", "Type"]))
rows = []
for (item, typ), g in sents:
    words = [str(x) for x in g.EachWord.tolist()]
    tee, surp = measures(words)
    for j, (_, r) in enumerate(g.iterrows()):
        rows.append({"item": item, "Type": typ, "WordPosition": r.WordPosition,
                     "tee": tee[j], "surp": surp[j]})
M = pd.DataFrame(rows)
d = d.merge(M, on=["item", "Type", "WordPosition"], how="left")
d["construction"] = d.CONSTRUCTION

print(f"items={d.item.nunique()}  constructions={d.construction.nunique()}  "
      f"types={d.Type.nunique()}")


def build_diffs(roi_set, label):
    sub = d[d.ROI.isin(roi_set)].copy()
    # human: mean logRT per item x construction x ambiguity
    hum = (sub.groupby(["item", "construction", "amb"])
              .log_RT.mean().unstack("amb"))
    hum.columns = ["unamb_RT", "amb_RT"]
    hum["dRT"] = hum.amb_RT - hum.unamb_RT
    # model: mean TEE / surprisal per item x construction x ambiguity
    mod = (sub.drop_duplicates(subset=["item", "construction", "amb", "WordPosition"])
              .groupby(["item", "construction", "amb"])[["tee", "surp"]].mean()
              .unstack("amb"))
    mod.columns = ["unamb_tee", "amb_tee", "unamb_surp", "amb_surp"]
    mod["dTEE"] = mod.amb_tee - mod.unamb_tee
    mod["dSurp"] = mod.amb_surp - mod.unamb_surp
    X = hum.join(mod).dropna().reset_index()
    print(f"\n{'='*74}\n{label}   n = {len(X)} item x construction pairs\n{'='*74}")
    print(f"  mean human GP effect (dRT)  = {X.dRT.mean():+.4f} log-ms  "
          f"({(X.dRT>0).sum()}/{len(X)} positive)")
    print(f"  mean dTEE                   = {X.dTEE.mean():+.2f}")
    print(f"  mean dSurp                  = {X.dSurp.mean():+.2f} bits")

    r1, p1 = stats.pearsonr(X.dTEE, X.dRT)
    r2, p2 = stats.pearsonr(X.dSurp, X.dRT)
    print(f"\n  r(dTEE,  dRT) = {r1:+.3f}   p = {p1:.3f}")
    print(f"  r(dSurp, dRT) = {r2:+.3f}   p = {p2:.3f}")

    for c in ["dTEE", "dSurp", "dRT"]:
        X["z_" + c] = (X[c] - X[c].mean()) / X[c].std(ddof=0)
    m = smf.ols("z_dRT ~ z_dSurp + z_dTEE + C(construction)", X).fit()
    print(f"\n  joint model (construction fixed effects):")
    print(f"    dSurp beta = {m.params['z_dSurp']:+.3f}  p = {m.pvalues['z_dSurp']:.3f}")
    print(f"    dTEE  beta = {m.params['z_dTEE']:+.3f}  p = {m.pvalues['z_dTEE']:.3f}")
    print(f"    R^2 = {m.rsquared:.3f}")

    print(f"\n  by construction:")
    for con, g in X.groupby("construction"):
        if len(g) < 5:
            continue
        rr, pp = stats.pearsonr(g.dTEE, g.dRT)
        print(f"    {con:<6} n={len(g):>3}  r(dTEE,dRT) = {rr:+.3f}  p = {pp:.3f}  "
              f"mean dRT = {g.dRT.mean():+.4f}")
    return X


build_diffs([0], "ROI 0 only (the disambiguating word)")
build_diffs([0, 1, 2], "critical region (ROI 0+1+2 pooled)")
build_diffs([1, 2], "spillover only (ROI 1+2) - the published sample")
