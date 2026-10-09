"""
F7 -- a single reportable effect size for planning N, for the headline effect:
curvature_3 at word w in the F1 primary model (log RT; surprisal, entropy,
log freq, length, position; story FE).

1. Subject-level d_z: OLS per participant (z-scored predictors computed on the
   full frame), slope of curvature_3; d_z = mean / SD across participants.
   Analytic N for 80/90/95% power (two-sided alpha .05, one-sample t on slopes).
   Also the same for curvature_3 at w-1 (next-word spillover), the larger effect.
2. Resampling power: draw N participants (with their full data), refit the
   pooled model with two-way (participant x word) clustered SEs, record
   p < .05; 100 draws per N.
"""
import os, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(f"{HERE}/f5_geometry_rt.py").read().split("res = []")[0])   # builds D

CTRL = "z_surprisal + z_entropy + z_log_freq_fixed + z_word_length + z_from_start"
words_per = D.groupby("pid").size()
print(f"participants {D.pid.nunique()}, words read per participant: median {words_per.median():.0f}, "
      f"range {words_per.min()}-{words_per.max()}")

out = {}
for lab, term, rhs in [("curvature_3 at w (headline)", "z_curvature_3", CTRL + " + z_curvature_3"),
                       ("curvature_3 at w-1 (spillover)", "z_curvature_3_prev",
                        CTRL + " + z_surprisal_prev + z_entropy_prev + z_curvature_3_prev")]:
    sl = []
    for p, g in D.groupby("pid"):
        if len(g) < 500:
            continue
        m = smf.ols(f"log_RT ~ {rhs}" + (" + C(story_id)" if g.story_id.nunique() > 1 else ""), g).fit()
        sl.append(m.params[term])
    sl = np.array(sl); dz = sl.mean() / sl.std(ddof=1)
    t = stats.ttest_1samp(sl, 0)
    print(f"\n{lab}: {len(sl)} participants with >=500 words")
    print(f"  mean slope {sl.mean():+.5f} log units/SD ({100*(np.exp(sl.mean())-1):.2f}% per SD), "
          f"SD {sl.std(ddof=1):.5f}, positive in {(sl > 0).mean():.0%}")
    print(f"  d_z = {dz:.3f}   (t({len(sl)-1}) = {t.statistic:.2f}, p = {t.pvalue:.1e})")
    for pw in (0.80, 0.90, 0.95):
        # exact one-sample t power, smallest N
        n = 3
        while stats.nct.sf(stats.t.ppf(.975, n - 1), n - 1, dz * np.sqrt(n)) < pw:
            n += 1
        print(f"  N for {int(pw*100)}% power: {n}")
    out[lab] = dz

print("\nRESAMPLING POWER (pooled model, two-way clustered, 100 draws per N; headline effect)")
rng = np.random.default_rng(0)
pids = D.pid.unique()
for N in (10, 15, 20, 30, 40, 60):
    hits = 0
    for _ in range(100):
        S = D[D.pid.isin(rng.choice(pids, N, replace=False))]
        m = smf.ols(f"log_RT ~ {CTRL} + z_curvature_3 + C(story_id)", S).fit(
            cov_type="cluster", cov_kwds={"groups": np.column_stack([S.pid.values, S.wid.values])})
        hits += m.pvalues["z_curvature_3"] < .05 and m.params["z_curvature_3"] > 0
    print(f"  N = {N:>3}: power {hits/100:.2f}")
