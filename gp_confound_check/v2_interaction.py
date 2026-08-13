"""
RECOMPUTE THE SURPRISAL x EXTRAPOLATION-ERROR INTERACTION TEST
==============================================================
v1's Regression paragraph claims: "The additive model was preferred over a model
including their interaction (dAIC = -2.0 in favor of the simpler model)."

That number came from the superseded measure pipeline and was never recomputed.
It survived the manuscript's numeric audit only because "2.0" matches trivially.
It is the last v1 statistic still in the text without provenance on the verified
sample.

Recomputed here on locked sample 8a6087341e, same specification as the headline
model: mixedlm, by-participant random intercept, ML fit, controls = word length
+ log frequency + zone + previous log RT.

Reported either way. If the interaction is now favoured, the claim of additivity
must be withdrawn, not softened.
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
print(f"locked sample {sh} verified")

# [2026-08-13] frequency repaired: the sample's log_freq is zero for 19.7% of
# words (unnormalised lookup). Recomputed as Zipf of the lowercased,
# punctuation-stripped word, matching every other analysis in v2.
from wordfreq import zipf_frequency
S["log_freq"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]').str.lower()
                 .map(lambda w: zipf_frequency(w, "en")))

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                "log_freq"]], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                     "prev_log_RT", "surprisal", "tee_k3"])
for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal",
          "tee_k3"]:
    d["z_" + c] = z(d[c])
print(f"n = {len(d):,}   participants = {d.participant.nunique()}\n")

CTRL = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT"
add = f"{CTRL} + z_surprisal + z_tee_k3"
itx = f"{CTRL} + z_surprisal * z_tee_k3"

m_add = smf.mixedlm(add, d, groups=d.participant).fit(reml=False,
                                                      method="lbfgs")
m_itx = smf.mixedlm(itx, d, groups=d.participant).fit(reml=False,
                                                      method="lbfgs")

print("=" * 74)
print("ADDITIVE vs INTERACTION")
print("=" * 74)
print(f"  additive     AIC {m_add.aic:12.1f}")
print(f"  interaction  AIC {m_itx.aic:12.1f}")
d_aic = m_add.aic - m_itx.aic
print(f"\n  dAIC (additive - interaction) = {d_aic:+.1f}")
print(f"  {'INTERACTION favoured' if d_aic > 0 else 'ADDITIVE favoured'} "
      f"by {abs(d_aic):.1f}")

term = "z_surprisal:z_tee_k3"
if term in m_itx.params:
    print(f"\n  interaction coefficient = {m_itx.params[term]:+.5f}   "
          f"p = {m_itx.pvalues[term]:.3e}")
print(f"  main effects in the interaction model: "
      f"surprisal {m_itx.params['z_surprisal']:+.5f}, "
      f"TEE {m_itx.params['z_tee_k3']:+.5f}")

print("\n" + "=" * 74)
print("v1 CLAIM CHECK")
print("=" * 74)
print("  v1: 'additive model preferred over interaction, dAIC = -2.0'")
if d_aic < 0 and abs(abs(d_aic) - 2.0) < 2.0:
    print("  -> reproduces in direction and roughly in magnitude.")
elif d_aic < 0:
    print(f"  -> additivity holds, but the magnitude differs "
          f"({abs(d_aic):.1f} vs 2.0). Update the number.")
else:
    print("  -> DOES NOT HOLD. The interaction model is now favoured.")
    print("     The additivity claim must be withdrawn, not softened.")
