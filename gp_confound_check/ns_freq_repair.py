"""
DOES THE NATURAL STORIES EFFECT SURVIVE A CORRECT FREQUENCY CONTROL?
=====================================================================
The `log_freq` column on the locked sample is wrong for 19.7% of words: 1,937 of
9,840 carry a value of 0, and 99.6% of those have a real frequency once the word
is lowercased and stripped of attached punctuation (hummed 2.37, clattered 2.17,
wool 3.91, residents 4.64). Only 37% of the zeroed words are punctuated, so this
is not only the trailing-punctuation problem. The scale is also not Zipf --
"the" is 6.67 in the column against a Zipf value of 7.73 -- so whatever produced
it, it is not the lookup the methods imply. Correlation with a correct lookup is
only +0.84.

This matters because frequency is a CONTROL in every Natural Stories model and
correlates with the trajectory measure at -0.44. A control that is wrong on a
fifth of observations leaves lexical variance unabsorbed, which the trajectory
term is then free to pick up. So the question is not cosmetic: does the headline
effect survive once frequency is measured properly?

REPAIR: log_freq_fixed = zipf_frequency(lowercased, punctuation-stripped word).
The garden-path pipeline already does exactly this, which is why its frequency
behaved more sensibly.

REPORTED FOR EACH SPECIFICATION, old control vs repaired control:
  H1  pooled headline    dAIC and beta for the trajectory term
  H2  subject-level      mean beta, % positive, Wilcoxon p
  H3  both frequencies entered together, to see what the repaired one absorbs
  H4  the frequency coefficient itself, to confirm the suppression story holds
      up once the variable is correct

If the trajectory effect drops substantially under H1/H2, the Natural Stories
result was partly an artefact of a degraded control and the paper has to say so.
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

S["log_freq_fixed"] = (S.word.astype(str)
                       .str.strip('.,;:!?"\'()[]')
                       .str.lower()
                       .map(lambda w: zipf_frequency(w, "en")))
print(f"locked sample {sh}   {len(S):,} words")
print(f"  old log_freq  : zeros {(S.log_freq == 0).sum():,} "
      f"({(S.log_freq == 0).mean():.1%})  mean {S.log_freq.mean():.3f}")
print(f"  repaired      : zeros {(S.log_freq_fixed == 0).sum():,} "
      f"({(S.log_freq_fixed == 0).mean():.1%})  "
      f"mean {S.log_freq_fixed.mean():.3f}")
print(f"  r(old, repaired) = {S.log_freq.corr(S.log_freq_fixed):+.4f}")
print(f"  r(TEE, old)      = {S.tee_k3.corr(S.log_freq):+.4f}")
print(f"  r(TEE, repaired) = {S.tee_k3.corr(S.log_freq_fixed):+.4f}")
print(f"  r(surprisal, old)      = {S.surprisal.corr(S.log_freq):+.4f}")
print(f"  r(surprisal, repaired) = "
      f"{S.surprisal.corr(S.log_freq_fixed):+.4f}")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                "log_freq", "log_freq_fixed"]],
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "log_freq_fixed",
                     "zone", "prev_log_RT", "tee_k3", "surprisal"])
for c in ["word_length", "log_freq", "log_freq_fixed", "zone", "prev_log_RT",
          "surprisal", "tee_k3"]:
    d["z_" + c] = z(d[c])
print(f"\nn = {len(d):,}   participants = {d.participant.nunique()}")

print("\n" + "=" * 80)
print("H1  POOLED HEADLINE: dAIC and beta for the trajectory term")
print("=" * 80)
BASE = "log_RT ~ z_word_length + z_zone + z_prev_log_RT + z_surprisal"
specs = [("old log_freq (as published)", BASE + " + z_log_freq"),
         ("repaired log_freq", BASE + " + z_log_freq_fixed"),
         ("both frequencies", BASE + " + z_log_freq + z_log_freq_fixed")]
print(f"{'frequency control':<30}{'dAIC(TEE)':>12}{'beta(TEE)':>12}{'p':>12}")
for lab, f in specs:
    m0 = smf.mixedlm(f, d, groups=d.participant).fit(reml=False,
                                                     method="lbfgs")
    m1 = smf.mixedlm(f + " + z_tee_k3", d, groups=d.participant).fit(
        reml=False, method="lbfgs")
    print(f"{lab:<30}{m0.aic - m1.aic:>12.1f}"
          f"{m1.params['z_tee_k3']:>12.5f}{m1.pvalues['z_tee_k3']:>12.2e}")

print("\n" + "=" * 80)
print("H2  SUBJECT-LEVEL")
print("=" * 80)


def subj(cols):
    out = []
    for pid, s in d.groupby("participant"):
        s = s.dropna(subset=cols + ["log_RT"])
        if len(s) < 300:
            continue
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s.log_RT.values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


CTRL = ["word_length", "zone", "prev_log_RT", "surprisal"]
print(f"{'frequency control':<30}{'beta':>11}{'% positive':>13}{'p':>12}")
for lab, fq in [("old log_freq (as published)", ["log_freq"]),
                ("repaired log_freq", ["log_freq_fixed"]),
                ("both frequencies", ["log_freq", "log_freq_fixed"])]:
    b = subj(["tee_k3"] + CTRL + fq)
    print(f"{lab:<30}{b.mean():>+11.5f}{(b > 0).mean():>12.1%}"
          f"{stats.wilcoxon(b).pvalue:>12.2e}")

print("\n" + "=" * 80)
print("H4  THE FREQUENCY COEFFICIENT ITSELF (subject-level)")
print("=" * 80)


def subj_focus(focus, others):
    out = []
    for pid, s in d.groupby("participant"):
        s = s.dropna(subset=[focus] + others + ["log_RT"])
        if len(s) < 300:
            continue
        X = np.column_stack([zs(s[focus].values)]
                            + [zs(s[c].values) for c in others])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s.log_RT.values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


for lab, fq in [("old log_freq", "log_freq"),
                ("repaired log_freq", "log_freq_fixed")]:
    a = subj_focus(fq, [])
    b = subj_focus(fq, ["word_length"])
    c = subj_focus(fq, ["word_length", "surprisal", "tee_k3", "zone",
                        "prev_log_RT"])
    print(f"  {lab:<20} alone {a.mean():+.4f} | "
          f"+length {b.mean():+.4f} | full model {c.mean():+.4f}")
