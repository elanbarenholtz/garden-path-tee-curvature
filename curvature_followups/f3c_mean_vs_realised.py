"""F3c -- is the anticipated-mean -> RT(w+1) effect (F3b S2) just realised
curvature at w+1 arriving one step early?

Base = F3b secondary model (w+1 F1 predictors + curvature_3, surprisal,
ent_full at w), two-way clustered SEs.
  M0  base + ac_mean                       (reproduces S2's ac_mean effect)
  M1  base + angle_next_realised           (the realised angle at w+1's first subword)
  M2  base + angle_next_realised + ac_mean (does ac_mean survive?)
  M3  M2 + curvature_1 at w+1 (final-subword angle of w+1)
Also: forecast error (angle_next_realised - ac_mean) in place of both.
"""
import os, numpy as np
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "f3b_anticipated_rt.py")).read()
src = src.split('K = [20, 50, 100]')[0]
src = src.replace('acols = [c for c in A.columns if c.startswith(("ac_", "ent_full", "mass_"))]',
                  'acols = [c for c in A.columns if c.startswith(("ac_", "ent_full", "mass_", "angle_next"))]')
exec(src)
S["fc_err"] = S.angle_next_realised - S.ac_mean_k50
g = S.sort_values(["story_id", "word_idx"]).groupby("story_id")
S = S.sort_values(["story_id", "word_idx"])
S["curvature_1_next"] = g.curvature_1.shift(-1)
d = d.merge(S[["story_id", "zone", "fc_err", "curvature_1_next"]], on=["story_id", "zone"])
BASEV_ = BASEV
d = d.sort_values(["participant", "story_id", "zone"])
Z = [c + "_next" for c in BASEV_] + BASEV_ + ["ent_full", "ac_mean_k50", "angle_next_realised",
                                            "curvature_1_next", "fc_err"]
D = d.dropna(subset=["log_RT_next"] + Z).copy()
for c in Z:
    D["z_" + c] = (D[c] - D[c].mean()) / D[c].std()
print(f"rows {len(D):,}")
print("word-level r(ac_mean, angle_next_realised) =",
      round(S.ac_mean_k50.corr(S.angle_next_realised), 3),
      "  r(angle_next_realised, curvature_1_next) =",
      round(S.angle_next_realised.corr(S.curvature_1_next), 3))
BASE = " + ".join("z_" + c + "_next" for c in BASEV_) + " + z_curvature_3 + z_surprisal + z_ent_full + C(story_id)"
import statsmodels.formula.api as smf
def fit(rhs):
    return smf.ols(f"log_RT_next ~ {rhs}", D).fit(cov_type="cluster", cov_kwds={
        "groups": np.column_stack([D.pid.values, D.wid.values])})
m_base = fit(BASE)
for lab, add in [("M0 + ac_mean", ["z_ac_mean_k50"]),
                 ("M1 + realised angle", ["z_angle_next_realised"]),
                 ("M2 + realised + ac_mean", ["z_angle_next_realised", "z_ac_mean_k50"]),
                 ("M3 + realised + curv1(w+1) + ac_mean", ["z_angle_next_realised", "z_curvature_1_next", "z_ac_mean_k50"]),
                 ("M4 + forecast error only", ["z_fc_err"])]:
    m = fit(BASE + " + " + " + ".join(add))
    terms = "  ".join(f"{t[2:]} {m.params[t]:+.5f} (t {m.tvalues[t]:.1f})" for t in add)
    print(f"  {lab:<38} dAIC vs base {m_base.aic - m.aic:7.1f}   {terms}")
m2 = fit(BASE + " + z_angle_next_realised")
m3 = fit(BASE + " + z_angle_next_realised + z_ac_mean_k50")
print(f"\n  dAIC for ac_mean GIVEN realised angle: {m2.aic - m3.aic:.1f}")
