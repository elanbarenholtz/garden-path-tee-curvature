"""F1c -- F1 robustness rows R1-R5 re-tested with two-way (participant x word)
clustered SEs, after F1b showed participant-only clustering is anticonservative
for word-level predictors (null |t| > 1.96 in 52% of permutations).
Point estimates and dAIC are unchanged from F1; only SEs differ."""
import os, sys, numpy as np, statsmodels.formula.api as smf
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "f1_joint_entropy_rt.py")).read()
src = src.split('PRIMARY = [')[0]           # reuse F1's data prep verbatim
exec(src)
PRIMARY = ["curvature_3", "surprisal", "entropy", "log_freq_fixed", "word_length", "from_start"]
D = d.dropna(subset=["log_RT"] + PRIMARY).copy()
for c in PRIMARY + ["prev_log_RT", "entropy_next", "surprisal_prev", "entropy_prev", "curvature_3_prev"]:
    v = D[c].dropna(); D["z_" + c] = (D[c] - v.mean()) / v.std()
D["pid"] = D.participant.astype("category").cat.codes
D["wid"] = (D.story_id * 10000 + D.zone).astype("category").cat.codes
CTRL = "z_surprisal + z_entropy + z_log_freq_fixed + z_word_length + z_from_start + C(story_id)"
SPEC = {"PRIMARY": CTRL,
        "R1 + prev_log_RT": CTRL + " + z_prev_log_RT",
        "R2 + next-word entropy": CTRL + " + z_entropy_next",
        "R4 + spillover (w-1 surp, ent, curv)": CTRL + " + z_surprisal_prev + z_entropy_prev + z_curvature_3_prev",
        "R5 all of R1+R2+R4": CTRL + " + z_prev_log_RT + z_entropy_next + z_surprisal_prev + z_entropy_prev + z_curvature_3_prev"}
print(f"{'spec':<40} {'beta':>9} {'t(part.)':>9} {'t(2-way)':>9} {'p(2-way)':>9}")
for lab, rhs in SPEC.items():
    cols = [t for t in rhs.replace("C(story_id)", "").replace("+", " ").split()] + ["z_curvature_3", "log_RT"]
    F = D.dropna(subset=cols)
    m = smf.ols(f"log_RT ~ {rhs} + z_curvature_3", F)
    a = m.fit(cov_type="cluster", cov_kwds={"groups": F.pid.values})
    b = m.fit(cov_type="cluster", cov_kwds={"groups": np.column_stack([F.pid.values, F.wid.values])})
    k = "z_curvature_3"
    print(f"{lab:<40} {b.params[k]:+.5f} {a.tvalues[k]:9.2f} {b.tvalues[k]:9.2f} {b.pvalues[k]:9.1e}", flush=True)
# joint w and w-1 curvature test (Wald, two-way)
F = D.dropna(subset=["z_surprisal_prev", "z_entropy_prev", "z_curvature_3_prev"])
m = smf.ols(f"log_RT ~ {CTRL} + z_surprisal_prev + z_entropy_prev + z_curvature_3 + z_curvature_3_prev", F).fit(
    cov_type="cluster", cov_kwds={"groups": np.column_stack([F.pid.values, F.wid.values])})
print(f"\ncurv_w-1 beta {m.params['z_curvature_3_prev']:+.5f}  t(2-way) {m.tvalues['z_curvature_3_prev']:.2f}")
print("joint Wald (curv_w = curv_w-1 = 0), two-way:", m.wald_test("z_curvature_3 = 0, z_curvature_3_prev = 0", scalar=True))
