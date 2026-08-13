"""
IS THE "STRONGER SURPRISAL" CONTROL ACTUALLY STRONGER *AS A CONTROL*?
=====================================================================
I reported that TEE's dAIC RISES when GPT-2 Small surprisal is replaced by
GPT-2 XL surprisal (111.8 -> 136.9 in Natural Stories) and read that as the
effect strengthening under a better control. That reading may be wrong.

Oh & Schuler (2023) -- cited in v1's own introduction as the "surprisal scaling
paradox" -- showed that surprisal from LARGER language models is a WORSE
predictor of human reading times. If GPT-2 XL surprisal fits reading time worse
than GPT-2 Small surprisal, then it is a WEAKER control, absorbing less outcome
variance and leaving more for TEE to explain. dAIC(TEE) would rise for a reason
that is not favourable to TEE at all.

The SAP output already hints at exactly this (sap_bigsurp_refit_out.txt):
    base model AIC, GPT-2 Small surprisal   1059844.5
    base model AIC, GPT-2 XL surprisal      1059935.3   <- WORSE fit
    base model AIC, Pythia-410M surprisal   1059877.1   <- WORSE fit
Lower AIC = better. GPT-2 Small is the best RT predictor of the three.

The Natural Stories run printed only dAIC, not the base AICs, so the same check
was never made there. This script prints them.

If the same pattern holds, then:
  - the claim "the effect strengthens under a stronger control" must be dropped
  - the defensible claim is the UNION spec, which contains GPT-2 Small surprisal
    (the best single RT predictor) PLUS the others, and therefore strictly
    dominates any single control
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
                   "surprisal_gpt2_medium"),
                  (f"{GP}/extensions/gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl"),
                  (f"{GP}/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv",
                   "surprisal_pythia410m")]:
    S = S.merge(pd.read_csv(path)[["story_id", "word_idx", col]],
                on=["story_id", "word_idx"], how="left", validate="one_to_one")

ks = ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl",
      "surprisal_pythia410m"]
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "word_length", "log_freq"] + ks],
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                     "prev_log_RT", "tee_k3"] + ks)
for c in ["word_length", "log_freq", "zone", "prev_log_RT", "tee_k3"] + ks:
    d["z_" + c] = z(d[c])
print(f"n = {len(d):,}   participants = {d.participant.nunique()}\n")

BASE = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT"
m_ctrl = smf.mixedlm(BASE, d, groups=d.participant).fit(reml=False,
                                                        method="lbfgs")
print("=" * 80)
print("HOW WELL DOES EACH SURPRISAL PREDICT READING TIME, ON ITS OWN?")
print("=" * 80)
print(f"  controls only (no surprisal)      AIC {m_ctrl.aic:12.1f}")
print(f"{'surprisal source':<26}{'base AIC':>13}{'dAIC vs ctrl':>14}"
      f"{'dAIC(TEE)':>12}")
res = {}
for lab, c in [("GPT-2 Small", "surprisal"),
               ("GPT-2 Medium", "surprisal_gpt2_medium"),
               ("GPT-2 XL", "surprisal_gpt2_xl"),
               ("Pythia-410M", "surprisal_pythia410m")]:
    m0 = smf.mixedlm(f"{BASE} + z_{c}", d, groups=d.participant).fit(
        reml=False, method="lbfgs")
    m1 = smf.mixedlm(f"{BASE} + z_{c} + z_tee_k3", d,
                     groups=d.participant).fit(reml=False, method="lbfgs")
    res[lab] = (m0.aic, m_ctrl.aic - m0.aic, m0.aic - m1.aic)
    print(f"{lab:<26}{m0.aic:>13.1f}{m_ctrl.aic - m0.aic:>14.1f}"
          f"{m0.aic - m1.aic:>12.1f}")

allterm = " + ".join(f"z_{c}" for c in ks)
m0 = smf.mixedlm(f"{BASE} + {allterm}", d, groups=d.participant).fit(
    reml=False, method="lbfgs")
m1 = smf.mixedlm(f"{BASE} + {allterm} + z_tee_k3", d,
                 groups=d.participant).fit(reml=False, method="lbfgs")
print(f"{'all four together':<26}{m0.aic:>13.1f}{m_ctrl.aic - m0.aic:>14.1f}"
      f"{m0.aic - m1.aic:>12.1f}")

print("\n" + "=" * 80)
print("READING")
print("=" * 80)
best = min(res, key=lambda k: res[k][0])
print(f"  best single RT-predicting surprisal: {best}")
print("  If GPT-2 Small is best, the scaling paradox is present in this corpus,")
print("  and a rise in dAIC(TEE) under larger-model surprisal reflects a WEAKER")
print("  control, not a stronger one. The union spec is then the honest one:")
print("  it contains the best single predictor plus the others.")
