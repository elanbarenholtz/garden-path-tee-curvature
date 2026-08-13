"""
ITEM-LEVEL GARDEN-PATH TEST WITHOUT CONSTRUCTION FIXED EFFECTS
==============================================================
Elan's objection to the fixed-effects analysis: the theoretical claim was always
about the garden-path effect itself (ambiguous vs unambiguous), so the pooled
comparison across all 72 item x construction pairs is the one that matches the
claim, and partialling out construction removes the very contrast of interest.

That is a fair reading, so this runs the pooled version:

    z_dRT ~ z_dSurp + z_dTEE          (NO construction fixed effects)

and reports alongside it everything needed to judge how much the pooled estimate
leans on the three construction means:

  (a) pooled OLS, classical SEs                      <- the test as framed
  (b) same, cluster-robust SEs by construction (G=3) <- honest inference
  (c) leave-one-construction-out refits              <- stability
  (d) construction-mean table                        <- what drives the pooled fit
  (e) fixed-effects version                          <- for contrast
  (f) between/within variance decomposition

TEE is RECOMPUTED here with exactly the settings used in gp_item_level.py
(GPT-2 small, layer 6, k=3, word state = final subword, sink never inside a fit
window). gp_table1_measures.csv is NOT reused: it holds the original
sink-inclusive TEE and does not reproduce the published item-level values.

GUARD: before reporting anything, reproduce the published ROI-0 numbers from
gp_item_level_out.txt (mean dTEE +1.69, mean dSurp +4.89, r = +0.280). Abort
on mismatch.
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from scipy import stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
LAYER, K = 6, 3
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

REF = {"dTEE": 1.69, "dSurp": 4.89, "r": 0.280}

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
        lo = max(i - K, 1)                     # sink never inside the window
        if i < 4 or (i - lo) < 2:
            continue
        Y = wh[lo:i]
        m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
    return tee, surp


def load():
    d = pd.read_csv(RT_CSV)
    for c in ["EachWord", "Sentence"]:
        d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
    d = d[(d.RT > 100) & (d.RT < 5000)].copy()
    d["log_RT"] = np.log(d.RT)
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
            rows.append({"item": item, "Type": typ,
                         "WordPosition": r.WordPosition,
                         "tee": tee[j], "surp": surp[j]})
    M = pd.DataFrame(rows)
    return d.merge(M, on=["item", "Type", "WordPosition"], how="left")


def diffs(d, roi_set):
    sub = d[d.ROI.isin(roi_set)].copy()
    hum = (sub.groupby(["item", "construction", "amb"])
              .log_RT.mean().unstack("amb"))
    hum.columns = ["unamb_RT", "amb_RT"]
    hum["dRT"] = hum.amb_RT - hum.unamb_RT
    mod = (sub.drop_duplicates(subset=["item", "construction", "amb",
                                       "WordPosition"])
              .groupby(["item", "construction", "amb"])[["tee", "surp"]]
              .mean().unstack("amb"))
    mod.columns = ["unamb_tee", "amb_tee", "unamb_surp", "amb_surp"]
    mod["dTEE"] = mod.amb_tee - mod.unamb_tee
    mod["dSurp"] = mod.amb_surp - mod.unamb_surp
    X = hum.join(mod).dropna().reset_index()
    for c in ["dTEE", "dSurp", "dRT"]:
        X["z_" + c] = (X[c] - X[c].mean()) / X[c].std(ddof=0)
    return X


def main():
    d = load()
    X0 = diffs(d, [0])
    r0 = stats.pearsonr(X0.dTEE, X0.dRT)[0]

    print("=" * 74)
    print("GUARD: reproduce published ROI-0 item-level numbers")
    print("=" * 74)
    print(f"  n pairs      {len(X0)}          expected 72")
    print(f"  mean dTEE    {X0.dTEE.mean():+.2f}   expected {REF['dTEE']:+.2f}")
    print(f"  mean dSurp   {X0.dSurp.mean():+.2f}   expected {REF['dSurp']:+.2f}")
    print(f"  r(dTEE,dRT)  {r0:+.3f}   expected {REF['r']:+.3f}")
    ok = (len(X0) == 72
          and abs(X0.dTEE.mean() - REF["dTEE"]) < .05
          and abs(X0.dSurp.mean() - REF["dSurp"]) < .05
          and abs(r0 - REF["r"]) < .01)
    print(f"\n  MATCH: {'YES' if ok else 'NO'}")
    if not ok:
        print("\n  ABORTING: measures differ from the published item-level run.")
        return

    for roi, lab in [([0], "ROI 0 (disambiguating word)"),
                     ([0, 1, 2], "critical region ROI 0+1+2"),
                     ([1, 2], "spillover ROI 1+2 (published sample)")]:
        X = diffs(d, roi)
        print("\n" + "=" * 74)
        print(f"{lab}   n = {len(X)}")
        print("=" * 74)

        m = smf.ols("z_dRT ~ z_dSurp + z_dTEE", X).fit()
        print("\n(a) POOLED, no construction fixed effects, classical SEs")
        for t in ["z_dSurp", "z_dTEE"]:
            print(f"    {t:<9} beta = {m.params[t]:+.3f}   "
                  f"SE = {m.bse[t]:.3f}   p = {m.pvalues[t]:.4f}")
        print(f"    R^2 = {m.rsquared:.3f}")

        mc = smf.ols("z_dRT ~ z_dSurp + z_dTEE", X).fit(
            cov_type="cluster", cov_kwds={"groups": X.construction})
        print("\n(b) same model, SEs clustered by construction (G = 3)")
        for t in ["z_dSurp", "z_dTEE"]:
            print(f"    {t:<9} beta = {mc.params[t]:+.3f}   "
                  f"SE = {mc.bse[t]:.3f}   p = {mc.pvalues[t]:.4f}")

        print("\n(c) leave-one-construction-out (pooled, no FE)")
        for con in sorted(X.construction.unique()):
            sub = X[X.construction != con].copy()
            for c in ["dTEE", "dSurp", "dRT"]:
                sub["z_" + c] = (sub[c] - sub[c].mean()) / sub[c].std(ddof=0)
            mm = smf.ols("z_dRT ~ z_dSurp + z_dTEE", sub).fit()
            print(f"    drop {con:<5} n={len(sub):>3}  "
                  f"dTEE {mm.params['z_dTEE']:+.3f} (p={mm.pvalues['z_dTEE']:.3f})   "
                  f"dSurp {mm.params['z_dSurp']:+.3f} (p={mm.pvalues['z_dSurp']:.3f})")

        print("\n(d) construction means (the 3 points a pooled slope rests on)")
        print(X.groupby("construction")[["dTEE", "dSurp", "dRT"]]
               .mean().round(4).to_string())

        mf = smf.ols("z_dRT ~ z_dSurp + z_dTEE + C(construction)", X).fit()
        print("\n(e) WITH construction fixed effects (within-construction only)")
        for t in ["z_dSurp", "z_dTEE"]:
            print(f"    {t:<9} beta = {mf.params[t]:+.3f}   "
                  f"p = {mf.pvalues[t]:.4f}")

        print("\n(f) variance decomposition")
        for v in ["dTEE", "dSurp", "dRT"]:
            tot = X[v].var(ddof=0)
            btw = X.groupby("construction")[v].mean().reindex(
                X.construction).values
            print(f"    {v:<6} between-construction share = {np.var(btw)/tot:.1%}")


if __name__ == "__main__":
    main()
