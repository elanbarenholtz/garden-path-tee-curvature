"""
PART A RERUN -- with the paper's direction-preservation quantity
================================================================
DEVIATION NOTICE (reported, not hidden): PREREG_syntax_control.md described
Part A's alignment as "cos between successive steps, the paper's
direction-preservation quantity". Those are two different quantities, and the
first run used the former. Raw successive-step cosine on these states is
approximately -0.40 in every transition class: successive steps share an
anti-correlated noise component (each step subtracts the previous word's
deviation), so the raw quantity is noise-dominated and carries no class
information. The paper's quantity -- |cos| between the OLS-fitted direction
over the preceding 3 word states and the current step (v2_table4_dirpres
convention, random baseline 0.029) -- averages that noise out. The 0.09
criterion was set against that baseline and is only meaningful for that
quantity. Part A is therefore rerun with the paper's quantity; the criterion
is unchanged. The negative raw-step autocorrelation is itself a real property
of the states (consistent with the overshoot dominance of the composite
measure) and is recorded for the geometry notes.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"
BASELINE = 0.029

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
X = pd.read_csv(f"{GPC}/syntax_vars_8a6087341e.csv")
S = S.merge(X[["story_id", "word_idx", "open_t", "close_t", "same_parent",
               "lca_dist"]], on=["story_id", "word_idx"], how="left",
            validate="one_to_one")

dp = np.full(len(S), np.nan)
Sg = S.reset_index()
for sid, sub in Sg.groupby("story_id"):
    zf = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
    H, ls = zf["H"].astype(np.float64), zf["last_sub"]
    for r in sub.itertuples():
        w = r.word_idx
        lo = max(w - 3, 1)
        if w < 4 or (w - lo) < 2:
            continue
        Y = np.stack([H[ls[j]] for j in range(lo, w)])
        m = Y.shape[0]
        x = np.arange(m, dtype=float)
        xc = x - x.mean()
        slope = (xc[:, None] * (Y - Y.mean(0))).sum(0) / (xc ** 2).sum()
        sn = np.linalg.norm(slope)
        step = H[ls[w]] - H[ls[w - 1]]
        stn = np.linalg.norm(step)
        if sn > 1e-9 and stn > 1e-9:
            dp[r.index] = abs(float(np.dot(slope, step) / (sn * stn)))
S["dirpres"] = dp
A = S.dropna(subset=["dirpres", "lca_dist", "close_t", "open_t",
                     "same_parent"]).copy()
A["lca_class"] = np.minimum(A.lca_dist, 3).astype(int)
A["log_pos"] = np.log(A.word_idx + 1)
print(f"{len(A):,} transitions   overall mean |cos| = {A.dirpres.mean():.4f} "
      f"(paper Table 4: 0.436)")

print("\nA1  direction preservation by transition class (baseline 0.029)")
print(f"{'lca_dist':>9}{'n':>8}{'mean |cos|':>13}{'x baseline':>12}")
for c, g in A.groupby("lca_class"):
    lab = f"{c}" if c < 3 else "3+"
    print(f"{lab:>9}{len(g):>8}{g.dirpres.mean():>13.4f}"
          f"{g.dirpres.mean()/BASELINE:>11.1f}x")

print("\nA2  variance absorbed by syntax")
m_pos = smf.ols("dirpres ~ log_pos + from_start + from_end", A).fit()
m_syn = smf.ols("dirpres ~ close_t + open_t + same_parent + C(lca_class) "
                "+ log_pos + from_start + from_end", A).fit()
print(f"  R^2 position only {m_pos.rsquared:.4f}   + syntax "
      f"{m_syn.rsquared:.4f}   absorbed "
      f"{m_syn.rsquared - m_pos.rsquared:.4f}")
deep = A[A.lca_dist >= 3]
crit = deep.dirpres.mean()
print(f"\n  CRITERION: mean |cos| at lca_dist >= 3 = {crit:.4f} "
      f"(n = {len(deep)}; threshold 0.09)")
print(f"  -> {'PASS' if crit >= 0.09 else 'FAIL'}")
