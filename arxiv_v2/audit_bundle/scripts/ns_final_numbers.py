"""
EXACT NUMBERS FOR THE MANUSCRIPT, REPAIRED FREQUENCY CONTROL
============================================================
Everything the v2 text needs to quote, computed in one place so the manuscript
can be edited from a single output rather than assembled from several runs.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
PY = pd.read_csv(f"{GPC}/pythia_tee_8a6087341e.csv")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                "log_freq_fixed"]], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
D = d.dropna(subset=["log_RT", "word_length", "log_freq_fixed", "zone",
                     "prev_log_RT", "tee_k3", "surprisal"]).copy()
for c in ["word_length", "zone", "prev_log_RT", "tee_k3", "log_freq_fixed",
          "surprisal"]:
    D["z_" + c] = z(D[c])

print("=" * 76)
print("HEADLINE MODEL (repaired frequency)")
print("=" * 76)
BASE = ("log_RT ~ z_word_length + z_log_freq_fixed + z_zone + z_prev_log_RT "
        "+ z_surprisal")
m0 = smf.mixedlm(BASE, D, groups=D.participant).fit(reml=False,
                                                    method="lbfgs")
m1 = smf.mixedlm(BASE + " + z_tee_k3", D, groups=D.participant).fit(
    reml=False, method="lbfgs")
print(f"  n = {len(D):,}   participants = {D.participant.nunique()}")
print(f"  dAIC(TEE)            = {m0.aic - m1.aic:.1f}")
print(f"  beta(TEE)            = {m1.params['z_tee_k3']:+.5f}  "
      f"p = {m1.pvalues['z_tee_k3']:.2e}")
print(f"  beta(surprisal)      = {m1.params['z_surprisal']:+.5f}")
print(f"  beta(log frequency)  = {m1.params['z_log_freq_fixed']:+.5f}")
print(f"  beta(word length)    = {m1.params['z_word_length']:+.5f}")
print(f"  ratio TEE/surprisal  = "
      f"{m1.params['z_tee_k3'] / m1.params['z_surprisal']:.2f}")

print("\n" + "=" * 76)
print("SUBJECT-LEVEL (repaired frequency)")
print("=" * 76)
b, nsig = [], 0
for pid, s in D.groupby("participant"):
    cols = ["tee_k3", "surprisal", "word_length", "log_freq_fixed", "zone",
            "prev_log_RT"]
    s = s.dropna(subset=cols + ["log_RT"])
    if len(s) < 300:
        continue
    X = np.column_stack([zs(s[c].values) for c in cols])
    if (X.std(axis=0) == 0).any():
        continue
    r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
    b.append(r.params[1])
    if r.pvalues[1] < .05 and r.params[1] > 0:
        nsig += 1
b = np.array(b)
npos = int((b > 0).sum())
print(f"  participants with sufficient data : {len(b)}")
print(f"  positive coefficients             : {npos} ({npos/len(b):.1%})")
print(f"  mean per-participant coefficient  : {b.mean():+.5f}")
print(f"  sign test p                       : "
      f"{stats.binomtest(npos, len(b), .5).pvalue:.2e}")
print(f"  Wilcoxon p                        : {stats.wilcoxon(b).pvalue:.2e}")
print(f"  t({len(b)-1})                          : "
      f"{stats.ttest_1samp(b, 0).statistic:.2f}")
print(f"  individually significant, positive: {nsig}")

print("\n" + "=" * 76)
print("PYTHIA CROSS-ARCHITECTURE (repaired frequency, matched sample)")
print("=" * 76)
P = D.merge(PY[["story_id", "zone", "tee_pythia_160m", "tee_pythia_410m"]],
            on=["story_id", "zone"], how="inner").dropna(
    subset=["tee_pythia_160m", "tee_pythia_410m"])
for c in ["tee_pythia_160m", "tee_pythia_410m"]:
    P["z_" + c] = z(P[c])
print(f"  n = {len(P):,}   participants = {P.participant.nunique()}")
q0 = smf.mixedlm(BASE, P, groups=P.participant).fit(reml=False,
                                                    method="lbfgs")
for lab, c in [("GPT-2 Small", "z_tee_k3"),
               ("Pythia-160M", "z_tee_pythia_160m"),
               ("Pythia-410M", "z_tee_pythia_410m")]:
    q1 = smf.mixedlm(BASE + " + " + c, P, groups=P.participant).fit(
        reml=False, method="lbfgs")
    print(f"  {lab:<14} dAIC {q0.aic - q1.aic:>7.1f}   "
          f"beta {q1.params[c]:+.5f}   p {q1.pvalues[c]:.2e}")
