"""
F6 -- effect sizes for the significant Natural Stories reading-time effects.

Frame: F1/F5 (locked sample 8a6087341e, RT 100-3000 ms, story FE, same controls).
Reported for curvature_3 at w, curvature_3 at w-1, TEE at w and w-1, step size at
w-1, and surprisal / entropy as benchmarks:
  ms_per_sd     slope from a raw-RT (ms) model, per SD of the predictor
  pct_per_sd    100*(exp(beta_log)-1) from the log-RT model
  p10_p90_ms    predicted RT difference between the 10th and 90th percentile
  dR2_trial     unique R^2 at the trial level (full model minus model without it)
  dR2_word      unique R^2 on per-word mean log RT (removes reader noise)
  f2_word       Cohen's f^2 at the word level
Full model contains every listed term at both w and w-1, so "unique" means
beyond all of the others, including surprisal and entropy at both positions.
"""
import os, numpy as np, pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/f5_geometry_rt.py").read().split("res = []")[0]
exec(src)                                  # builds D (trial frame) with z_ columns

TERMS = {"curvature_3 (w)": "curvature_3", "curvature_3 (w-1)": "curvature_3_prev",
         "TEE (w)": "tee_k3", "TEE (w-1)": "tee_k3_prev", "step size (w-1)": "step_norm_prev",
         "surprisal (w)": "surprisal", "surprisal (w-1)": "surprisal_prev",
         "entropy (w)": "entropy", "entropy (w-1)": "entropy_prev"}
CTRL = ["log_freq_fixed", "word_length", "from_start"]
ALLZ = [f"z_{v}" for v in TERMS.values()] + [f"z_{c}" for c in CTRL]
rhs = " + ".join(ALLZ) + " + C(story_id)"
mean_rt = D.RT.mean()
print(f"trials {len(D):,}; mean RT {mean_rt:.0f} ms; median {D.RT.median():.0f} ms")

full_log = smf.ols(f"log_RT ~ {rhs}", D).fit()
full_ms = smf.ols(f"RT ~ {rhs}", D).fit()
Wd = D.groupby("wid").agg(log_RT=("log_RT", "mean"), story_id=("story_id", "first"),
                          **{c: (c, "first") for c in ALLZ}).reset_index()
full_w = smf.ols(f"log_RT ~ {rhs}", Wd).fit()
print(f"R2 full: trial {full_log.rsquared:.4f}   word-level {full_w.rsquared:.4f}\n")

rows = []
for lab, v in TERMS.items():
    z = f"z_{v}"
    red = rhs.replace(z + " + ", "")
    r_t = full_log.rsquared - smf.ols(f"log_RT ~ {red}", D).fit().rsquared
    r_w = full_w.rsquared - smf.ols(f"log_RT ~ {red}", Wd).fit().rsquared
    sd = D[v].std(); p10, p90 = D[v].quantile([.1, .9])
    rows.append(dict(term=lab, ms_per_sd=full_ms.params[z],
                     pct_per_sd=100 * (np.exp(full_log.params[z]) - 1),
                     p10_p90_ms=full_ms.params[z] * (p90 - p10) / sd,
                     dR2_trial=r_t, dR2_word=r_w, f2_word=r_w / (1 - full_w.rsquared)))
R = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(R.to_string(index=False, float_format=lambda x: f"{x:.5f}" if abs(x) < 0.01 else f"{x:.2f}"))
s = R.set_index("term")
curv_total = s.loc[["curvature_3 (w)", "curvature_3 (w-1)"], "dR2_word"].sum()
surp_total = s.loc[["surprisal (w)", "surprisal (w-1)"], "dR2_word"].sum()
print(f"\nword-level unique R2, curvature (w + w-1 summed): {curv_total:.4f}   "
      f"surprisal (w + w-1 summed): {surp_total:.4f}   ratio {curv_total / surp_total:.2f}")
R.to_csv(f"{HERE}/f6_effect_sizes.csv", index=False)

# block effects: all geometry terms jointly vs surprisal pair jointly vs entropy pair
GEO = ["z_curvature_3", "z_curvature_3_prev", "z_tee_k3", "z_tee_k3_prev", "z_step_norm_prev"]
def block(terms):
    red = " + ".join(t for t in ALLZ if t not in terms) + " + C(story_id)"
    return (full_log.rsquared - smf.ols(f"log_RT ~ {red}", D).fit().rsquared,
            full_w.rsquared - smf.ols(f"log_RT ~ {red}", Wd).fit().rsquared)
print("\nBLOCK unique R2 (trial, word):")
for lab, t in [("geometry (curv3 w,w-1; TEE w,w-1; step w-1)", GEO),
               ("curvature only (w, w-1)", GEO[:2]),
               ("surprisal (w, w-1)", ["z_surprisal", "z_surprisal_prev"]),
               ("entropy (w, w-1)", ["z_entropy", "z_entropy_prev"])]:
    a, b = block(t); print(f"  {lab:<46} trial {a:.5f}   word {b:.4f}")
