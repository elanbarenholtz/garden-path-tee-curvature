"""
E8 -- curvature as a reading-time predictor (reviewer-anticipating control).
Spec fixed before results are seen: the repaired-frequency headline model
(identical to e7_dist_control), locked sample 8a6087341e, curvature from
tee_vs_curvature/curvature_merged_8a6087341e.csv (King/Hosseini-style mean
angle between successive step vectors, computed and validated in the v1-era
dissociation work; r(tee_k3, curvature_3) = +0.10 on this sample).

Questions, in order:
  1. Does curvature_3 predict RT beyond surprisal + lexical controls?
  2. Does TEE survive curvature entered jointly (and vice versa)?
  3. Same at subject level, standing criterion (p < .01, >= 65%).
Secondary: curvature_1; joint model with the E7 distribution functionals.
"""
import os, sys, hashlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from wordfreq import zipf_frequency

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
GPC = f"{GP}/gp_confound_check"

S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()
     ).hexdigest()[:10]
assert sh == "8a6087341e", sh
F = pd.read_csv(f"{GPC}/e7_functionals_8a6087341e.csv")
S = S.merge(F, on=["story_id", "word_idx"], how="left")
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
print(f"locked sample {sh}: {len(S):,} words   "
      f"r(tee_k3, curvature_3) = "
      f"{S.tee_k3.corr(S.curvature_3):+.3f}   "
      f"r(tee_k3, curvature_1) = {S.tee_k3.corr(S.curvature_1):+.3f}")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "curvature_3", "curvature_1",
                "surprisal", "word_length", "log_freq_fixed",
                "f_entropy", "f_renyi2", "f_top1", "f_top10"]],
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
BASE_COLS = ["word_length", "log_freq_fixed", "zone", "prev_log_RT",
             "surprisal"]
D = d.dropna(subset=["log_RT", "tee_k3", "curvature_3", "curvature_1"]
             + BASE_COLS).copy()


def z(s):
    v = s.dropna(); return (s - v.mean()) / v.std()


for c in BASE_COLS + ["tee_k3", "curvature_3", "curvature_1",
                      "f_entropy", "f_renyi2", "f_top1", "f_top10"]:
    D["z_" + c] = z(D[c])
print(f"RT rows: {len(D):,}   participants {D.participant.nunique()}")

BASE = ("log_RT ~ z_word_length + z_log_freq_fixed + z_zone + z_prev_log_RT"
        " + z_surprisal")
m0 = smf.mixedlm(BASE, D, groups=D.participant).fit(reml=False,
                                                    method="lbfgs")
print("\n" + "=" * 72)
print("POOLED (headline spec)")
print("=" * 72)
for lab, term in [("TEE alone", "z_tee_k3"),
                  ("curvature_3 alone", "z_curvature_3"),
                  ("curvature_1 alone", "z_curvature_1")]:
    m1 = smf.mixedlm(BASE + f" + {term}", D, groups=D.participant
                     ).fit(reml=False, method="lbfgs")
    print(f"  {lab:<20} dAIC {m0.aic - m1.aic:>7.1f}   "
          f"beta {m1.params[term]:+.5f}   p {m1.pvalues[term]:.2e}")
mj = smf.mixedlm(BASE + " + z_tee_k3 + z_curvature_3", D,
                 groups=D.participant).fit(reml=False, method="lbfgs")
print(f"  JOINT: tee beta {mj.params['z_tee_k3']:+.5f} "
      f"(p {mj.pvalues['z_tee_k3']:.2e})   curv3 beta "
      f"{mj.params['z_curvature_3']:+.5f} "
      f"(p {mj.pvalues['z_curvature_3']:.2e})")
mjf = smf.mixedlm(BASE + " + z_f_entropy + z_f_renyi2 + z_f_top1 + z_f_top10"
                  " + z_tee_k3 + z_curvature_3", D,
                  groups=D.participant).fit(reml=False, method="lbfgs")
print(f"  JOINT + functionals: tee {mjf.params['z_tee_k3']:+.5f} "
      f"(p {mjf.pvalues['z_tee_k3']:.2e})   curv3 "
      f"{mjf.params['z_curvature_3']:+.5f} "
      f"(p {mjf.pvalues['z_curvature_3']:.2e})")


def zs(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def subj(frame, xcol, covcols, minn=100, label=""):
    betas = []
    for pid, s in frame.groupby("participant"):
        s = s.dropna(subset=["log_RT", xcol] + covcols)
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in [xcol] + covcols])
        if (X.std(axis=0) == 0).any():
            continue
        X = np.column_stack([np.ones(len(s)), X])
        b, *_ = np.linalg.lstsq(X, s.log_RT.values, rcond=None)
        betas.append(b[1])
    betas = np.array(betas)
    pos = (betas > 0).mean()
    w = stats.wilcoxon(betas)
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"  {label:<34} n {len(betas)}  beta {betas.mean():+.5f}  "
          f"%pos {pos:.1%}  p {w.pvalue:.2e}  "
          f"{'PASS' if ok else 'FAIL'}")


print("\n" + "=" * 72)
print("SUBJECT-LEVEL (standing criterion)")
print("=" * 72)
subj(D, "tee_k3", BASE_COLS, label="TEE | base")
subj(D, "curvature_3", BASE_COLS, label="curvature_3 | base")
subj(D, "curvature_1", BASE_COLS, label="curvature_1 | base")
subj(D, "tee_k3", BASE_COLS + ["curvature_3"], label="TEE | base + curv3")
subj(D, "curvature_3", BASE_COLS + ["tee_k3"], label="curvature_3 | base + TEE")
