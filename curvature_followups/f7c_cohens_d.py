"""F7c -- Cohen's d for the curvature reading-time effect as a two-condition contrast.
Residualise log RT on the F1 controls (surprisal, entropy, log freq, length,
position, story FE) WITHOUT curvature; then per participant, mean residual for
words in the top vs bottom quartile of curvature_3 (also top vs bottom half).
  d_z  = mean(paired diff) / SD(paired diff)                 (within-subject d)
  d_av = mean(paired diff) / average within-participant SD of residual log RT
         across the two conditions (Cumming's d_av; the 'classic' d scale)
  d_rm (Lakens 2013) also reported.
Also the word-level d: difference of word-mean residual log RT between the
quartiles divided by pooled SD across words.
"""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(f"{HERE}/f5_geometry_rt.py").read().split("res = []")[0])
CTRL = "z_surprisal + z_entropy + z_log_freq_fixed + z_word_length + z_from_start + C(story_id)"
D["res"] = smf.ols(f"log_RT ~ {CTRL}", D).fit().resid
q = D.drop_duplicates("wid").curvature_3.quantile([.25, .5, .75])
for lab, lo, hi in [("top vs bottom quartile", D.curvature_3 <= q[.25], D.curvature_3 >= q[.75]),
                    ("top vs bottom half", D.curvature_3 < q[.5], D.curvature_3 >= q[.5])]:
    rows = []
    for p, g in D.groupby("pid"):
        a, b = g.res[hi.loc[g.index]], g.res[lo.loc[g.index]]
        if len(a) >= 50 and len(b) >= 50:
            rows.append((a.mean(), b.mean(), a.std(), b.std()))
    A = np.array(rows); diff = A[:, 0] - A[:, 1]
    dz = diff.mean() / diff.std(ddof=1)
    dav = diff.mean() / np.mean((A[:, 2] + A[:, 3]) / 2)
    r = np.corrcoef(A[:, 0], A[:, 1])[0, 1]
    drm = dz * np.sqrt(2 * (1 - r))
    W = D[hi | lo].groupby("wid").agg(res=("res", "mean"), hi=("curvature_3", lambda x: x.iloc[0] >= (q[.75] if "quartile" in lab else q[.5])))
    m1, m0 = W[W.hi].res, W[~W.hi].res
    dw = (m1.mean() - m0.mean()) / np.sqrt((m1.var() + m0.var()) / 2)
    print(f"{lab}: {len(A)} participants; mean diff {diff.mean():+.4f} log units "
          f"(~{100*(np.exp(diff.mean())-1):.1f}% , ~{D.RT.mean()*(np.exp(diff.mean())-1):.1f} ms)")
    print(f"   d_z {dz:.2f}   d_rm {drm:.2f}   d_av {dav:.3f}   word-level d {dw:.2f} "
          f"({len(m1)} vs {len(m0)} words)")
