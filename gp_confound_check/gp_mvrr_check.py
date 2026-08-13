"""
IS THE NEGATIVE MVRR dTEE REAL, OR A FEW OUTLIER ITEMS?
=======================================================
gp_item_nofe.py reported mean dTEE = -1.72 for MVRR at ROI 0: the AMBIGUOUS
reduced-relative produces LESS trajectory extrapolation error at the
disambiguating word than its unambiguous control. That is backwards for the
mechanism the garden-path paper proposed, so before it is treated as a fact:

  1. per-item sign counts and one-sample t / Wilcoxon per construction
  2. the same for surprisal (does the model find the ambiguous version easier
     by that measure too, or is this specific to TEE?)
  3. the raw TEE levels, not just the difference, so we can see which side moves
  4. what words actually sit in the k=3 fit window in each version -- for MVRR
     the three words before the disambiguator are identical across conditions
     ("...past the barn" + "fell"), so any difference must come from earlier
     context propagating into the hidden states, not from different words
  5. per-item listing so outliers are visible

Same measure pipeline as gp_item_nofe.py (GPT-2 small, L6, k=3, sink excluded).
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
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
        starts.append(prev)
        prev = fi + 1
    surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
    wh = h[final_idx]
    tee = np.full(len(words), np.nan)
    for i in range(len(words)):
        lo = max(i - K, 1)
        if i < 4 or (i - lo) < 2:
            continue
        Y = wh[lo:i]
        m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
    return tee, surp


d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d[(d.RT > 100) & (d.RT < 5000)].copy()
d["amb"] = (d.AMBUAMB == 1).astype(int)
d["construction"] = d.CONSTRUCTION

sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
           .sort_values(["item", "Type", "WordPosition"])
           .groupby(["item", "Type"]))
rows = []
for (item, typ), g in sents:
    words = [str(x) for x in g.EachWord.tolist()]
    tee, surp = measures(words)
    for j, (_, r) in enumerate(g.iterrows()):
        rows.append({"item": item, "Type": typ, "WordPosition": r.WordPosition,
                     "tee": tee[j], "surp": surp[j], "word": words[j],
                     "w_m1": words[j - 1] if j >= 1 else "",
                     "w_m2": words[j - 2] if j >= 2 else "",
                     "w_m3": words[j - 3] if j >= 3 else ""})
M = pd.DataFrame(rows)
d = d.merge(M, on=["item", "Type", "WordPosition"], how="left")

roi0 = d[d.ROI == 0].drop_duplicates(
    subset=["item", "construction", "amb", "WordPosition"])
piv = (roi0.groupby(["item", "construction", "amb"])[["tee", "surp"]]
           .mean().unstack("amb"))
piv.columns = ["tee_unamb", "tee_amb", "surp_unamb", "surp_amb"]
piv["dTEE"] = piv.tee_amb - piv.tee_unamb
piv["dSurp"] = piv.surp_amb - piv.surp_unamb
X = piv.dropna().reset_index()

print("=" * 78)
print("ROI 0: is dTEE reliably negative for MVRR?")
print("=" * 78)
print(f"{'constr':<7}{'n':>4}{'mean dTEE':>11}{'neg':>7}{'t':>8}{'p':>10}"
      f"{'Wilcox p':>11}")
for con, g in X.groupby("construction"):
    t = stats.ttest_1samp(g.dTEE, 0)
    w = stats.wilcoxon(g.dTEE)
    print(f"{con:<7}{len(g):>4}{g.dTEE.mean():>+11.2f}"
          f"{(g.dTEE < 0).sum():>4}/{len(g):<3}{t.statistic:>8.2f}"
          f"{t.pvalue:>10.4f}{w.pvalue:>11.4f}")

print("\n" + "=" * 78)
print("same for SURPRISAL (is the ambiguous version 'easier' by that too?)")
print("=" * 78)
print(f"{'constr':<7}{'n':>4}{'mean dSurp':>12}{'neg':>8}{'p':>10}")
for con, g in X.groupby("construction"):
    t = stats.ttest_1samp(g.dSurp, 0)
    print(f"{con:<7}{len(g):>4}{g.dSurp.mean():>+12.2f}"
          f"{(g.dSurp < 0).sum():>5}/{len(g):<3}{t.pvalue:>10.4f}")

print("\n" + "=" * 78)
print("RAW LEVELS: which side moves?")
print("=" * 78)
print(X.groupby("construction")[["tee_unamb", "tee_amb",
                                 "surp_unamb", "surp_amb"]].mean().round(2)
       .to_string())

print("\n" + "=" * 78)
print("FIT-WINDOW WORDS at the disambiguator (first 6 MVRR items)")
print("k=3 window = the three preceding words; if identical across conditions")
print("the dTEE difference comes from earlier context, not different words.")
print("=" * 78)
mv = d[(d.ROI == 0) & (d.construction == "MVRR")].drop_duplicates(
    subset=["item", "Type"]).sort_values(["item", "Type"])
for it in sorted(mv.item.unique())[:6]:
    for _, r in mv[mv.item == it].iterrows():
        tag = "AMB  " if r.amb == 1 else "UNAMB"
        print(f"  item {r['item']:>2} {tag} "
              f"window=[{r['w_m3']} {r['w_m2']} {r['w_m1']}] "
              f"-> '{r['word']}'   TEE={r['tee']:.1f}")
    print()

print("=" * 78)
print("PER-ITEM MVRR (sorted by dTEE) - look for outlier domination")
print("=" * 78)
g = X[X.construction == "MVRR"].sort_values("dTEE")
print(g[["item", "tee_unamb", "tee_amb", "dTEE", "dSurp"]]
      .round(2).to_string(index=False))

X.to_csv(f"{GP}/gp_roi0_item_diffs.csv", index=False)
print(f"\nsaved per-item table -> gp_roi0_item_diffs.csv")
