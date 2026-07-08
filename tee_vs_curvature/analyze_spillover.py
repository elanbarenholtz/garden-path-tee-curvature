"""
Spillover analysis, typed by the par/perp decomposition. Locked sample 8a6087341e.
Reading-time freeze lifted: the punctuation control (P1) is complete; punctuation
is controlled here and a punct-free robustness pass is reported.

Pre-committed question: do the two trajectory channels predict reading time at
different LAGS? Hypothesis: tee3_perp (lateral / branch change) shows spillover
(significant effect on the NEXT word's RT); tee3_par (along-heading / pace) is
local (concentrated on-word, little/no downstream).

DV = per-word mean log RT (RT filtered 100-3000 ms, averaged over participants).
Predictors z-scored (ddof=0), entered at lag 0 (on-word), lag 1 (prev word),
lag 2 (two back), within story:
  tee3_perp, tee3_par, surprisal, word_length, log_freq, has_trailing_punct
Nuisance: position (from_start,fs2,from_end,fe2) + C(story_id).
Cluster-robust SE by sent_uid. Lags via within-story shift (sample is a
contiguous suffix per story; first 2 words/story drop for want of lags).
"""
import hashlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

GP = "/Users/elansmini/Research/Garden_Path"
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id","word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

# --- reading times: filter, per-word mean log RT ---
R = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv", sep="\t")
R = R[(R.RT >= 100) & (R.RT <= 3000)].copy()
R["logRT"] = np.log(R["RT"])
agg = R.groupby(["item", "zone"]).agg(mean_logRT=("logRT", "mean"),
                                       n_obs=("logRT", "size")).reset_index()
agg = agg.rename(columns={"item": "story_id"})

# --- merge features + decomposition + RT ---
D = S.merge(CUR[["story_id","word_idx","tee3_par","tee3_perp","curvature_3"]],
            on=["story_id","word_idx"], validate="one_to_one")
D["has_trailing_punct"] = D["word"].astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
D = D.merge(agg, on=["story_id","zone"], validate="one_to_one")
assert len(D) == 9840, len(D)
print(f"SAMPLE: hash = {sh}   n = {len(D)}   RT obs (100-3000ms): {len(R)}")
print(f"mean n_obs/word = {D.n_obs.mean():.1f}\n")

# --- within-story lags ---
D = D.sort_values(["story_id","word_idx"]).reset_index(drop=True)
LAGVARS = ["tee3_perp","tee3_par","surprisal","word_length","log_freq",
           "has_trailing_punct"]
for v in LAGVARS:
    for L in (1, 2):
        D[f"{v}_L{L}"] = D.groupby("story_id")[v].shift(L)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)  # autocorr control
Dl = D.dropna(subset=[f"{v}_L{L}" for v in LAGVARS for L in (1,2)]
              + ["prev_logRT"]).reset_index(drop=True)
print(f"after lagging (drop first 2 words/story): n = {len(Dl)}")

def z(s): return (s - s.mean()) / s.std(ddof=0)

def fit(formula, data):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["sent_uid"]})

CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"

def build(dat, drop_L0_punct=False):
    """z-score predictors; return (z-frame, predictor-term list)."""
    Zf = dat.copy(); preds = []
    for v in LAGVARS:
        if not (drop_L0_punct and v == "has_trailing_punct"):
            Zf[v] = z(dat[v]); preds.append(v)
        for L in (1, 2):
            col = f"{v}_L{L}"
            Zf[col] = z(dat[col]); preds.append(col)
    Zf["prev_logRT"] = z(dat["prev_logRT"])
    return Zf, preds

Z, allpred = build(Dl)
m = fit(f"mean_logRT ~ {' + '.join(allpred)} + {CTRL}", Z)

def show(mod, label):
    print("\n" + "="*66)
    print(f"{label}   n={int(mod.nobs)}  R^2={mod.rsquared:.4f}")
    print("="*66)
    print(f"{'predictor':22s} {'L0':>18s} {'L1 (spillover)':>18s} {'L2':>14s}")
    for v in LAGVARS:
        cells = []
        for key in (v, f"{v}_L1", f"{v}_L2"):
            if key not in mod.params:
                cells.append(f"{'--':>16s}"); continue
            b, p = mod.params[key], mod.pvalues[key]
            star = "*" if p < .05 else " "
            cells.append(f"{b:+.4f}({p:.1e}){star}")
        print(f"{v:22s} {cells[0]:>18s} {cells[1]:>18s} {cells[2]:>14s}")

show(m, "FULL MODEL: per-word mean logRT ~ predictors x {L0,L1,L2} + prevRT + ctrl")

# --- punct-free robustness: current word not punct-final ---
Dpf = Dl[Dl.has_trailing_punct == 0].reset_index(drop=True)
Zp, predp = build(Dpf, drop_L0_punct=True)  # L0 punct is constant here
mp = fit(f"mean_logRT ~ {' + '.join(predp)} + {CTRL}", Zp)
show(mp, "PUNCT-FREE (current word not punct-final; forced deviation)")

print(f"\nAll results: hash = {sh}")
