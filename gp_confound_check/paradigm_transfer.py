"""
HOW MUCH SHOULD AN EFFECT TRANSFER FROM SELF-PACED READING TO EYE TRACKING?
==========================================================================
TEE predicts self-paced RT in Natural Stories but not total reading time in
OneStop. Is that a meaningful failure, or is it what any effect would do?

Calibrate with predictors whose reality is not in doubt. Surprisal, log
frequency and word length are all established reading-time predictors. Estimate
each one's standardised effect in BOTH datasets under a matched specification,
then read TEE against that yardstick:

  transfer ratio = beta(OneStop TRT) / beta(Natural Stories SPR)

If surprisal and frequency transfer at ratio R, then a genuine effect of TEE
should show roughly R x its Natural Stories beta in OneStop. Compare that
prediction to what was actually observed.

Matched specification in both: outcome = log reading time, predictors z-scored,
controls = word length, log frequency, surprisal, previous-word reading time.
Subject-level estimation in both (one regression per participant, then mean),
so the two are on the same inferential footing.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
PREDS = ["word_length", "log_freq", "surprisal", "prev_rt", "tee"]


def per_subject(d, subj):
    """One OLS per participant; return mean beta and n for each predictor."""
    out = {p: [] for p in PREDS}
    for pid, sub in d.groupby(subj):
        s = sub.dropna(subset=PREDS + ["y"])
        if len(s) < 200:
            continue
        X = s[PREDS].astype(float)
        sd = X.std(ddof=0)
        if (sd == 0).any():
            continue
        X = sm.add_constant((X - X.mean()) / sd)
        r = sm.OLS(s.y.values, X.values).fit()
        for i, p in enumerate(PREDS):
            out[p].append(r.params[i + 1])
    return {p: np.array(v) for p, v in out.items()}


# ---------------- Natural Stories (self-paced) ----------------
w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
ns = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length", "log_freq"]],
              on=["story_id", "zone"], how="inner")
ns["y"] = np.log(ns.RT)
ns = ns.sort_values(["participant", "story_id", "zone"])
ns["prev_rt"] = ns.groupby(["participant", "story_id"])["y"].shift(1)
ns = ns.rename(columns={"tee_k3": "tee"})
NS = per_subject(ns, "participant")

# ---------------- OneStop (eye tracking, total reading time) ----------------
use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
                                  "wordfreq_frequency", "gpt2_surprisal"]
os_ = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
os_ = os_.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
                on=KEY, how="left")
for c in ["IA_DWELL_TIME", "word_length", "wordfreq_frequency", "gpt2_surprisal"]:
    os_[c] = pd.to_numeric(os_[c], errors="coerce")
os_ = os_[os_.IA_DWELL_TIME > 0].copy()
os_["y"] = np.log(os_.IA_DWELL_TIME)
os_["log_freq"] = np.log(os_.wordfreq_frequency.clip(lower=1e-9))
os_ = os_.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
os_ = os_.sort_values(["participant_id"] + KEY)
os_["prev_rt"] = os_.groupby(["participant_id", "article_id", "paragraph_id",
                              "difficulty_level"])["y"].shift(1)
OS = per_subject(os_, "participant_id")

print(f"Natural Stories (self-paced): {len(NS['tee'])} participants")
print(f"OneStop (eye tracking, TRT):  {len(OS['tee'])} participants\n")

print("=" * 78)
print("STANDARDISED EFFECTS IN BOTH PARADIGMS (subject-level means)")
print("=" * 78)
print(f"{'predictor':<16}{'NS self-paced':>16}{'OneStop TRT':>16}"
      f"{'transfer ratio':>17}")
ratios = {}
for p in PREDS:
    if p == "prev_rt":
        continue
    a, b = NS[p].mean(), OS[p].mean()
    ratios[p] = b / a if a != 0 else np.nan
    pa = stats.wilcoxon(NS[p]).pvalue
    pb = stats.wilcoxon(OS[p]).pvalue
    print(f"{p:<16}{a:>+11.5f}{'':>1}{'*' if pa<.05 else ' '}"
          f"{b:>+13.5f}{'*' if pb<.05 else ' '}{ratios[p]:>16.2f}")

est = [ratios[p] for p in ["surprisal", "log_freq", "word_length"]]
print(f"\n  mean transfer ratio of the three established predictors: "
      f"{np.mean(est):.2f}")
print(f"  (surprisal {ratios['surprisal']:.2f}, frequency {ratios['log_freq']:.2f}, "
      f"length {ratios['word_length']:.2f})")

pred = NS["tee"].mean() * np.mean(est)
obs = OS["tee"].mean()
se = OS["tee"].std(ddof=1) / np.sqrt(len(OS["tee"]))
print("\n" + "=" * 78)
print("IS TEE'S ONESTOP ESTIMATE WHAT THE BENCHMARK PREDICTS?")
print("=" * 78)
print(f"  TEE beta in Natural Stories            = {NS['tee'].mean():+.5f}")
print(f"  predicted OneStop beta at that ratio   = {pred:+.5f}")
print(f"  observed OneStop beta                  = {obs:+.5f}  (SE {se:.5f})")
z = (obs - pred) / se
print(f"  observed vs predicted                  = {z:+.2f} SE  "
      f"(p = {2*stats.norm.sf(abs(z)):.4f})")
print("\n  If the established predictors transfer but TEE lands far below its")
print("  predicted value, the non-replication is specific to TEE rather than")
print("  a general property of the paradigm shift.")
