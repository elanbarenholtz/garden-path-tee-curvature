"""
PARAMETER-SELECTION SWEEP UNDER THE CORRECTED PIPELINE
======================================================
The Methods claim that "the 3-word linear fit at layer 6 consistently
outperformed longer windows and higher-degree fits". The audit found no current
output supporting this: the selection was made on the superseded pipeline, before
the frequency repair.

WHAT CAN BE VERIFIED HERE. The locked sample carries extrapolation error at
window sizes k = 2, 3, 4, 5, 7, 10, 15, 20, 30, 50, all at layer 6, in both raw
and length-normalised form. The window comparison can therefore be rerun exactly,
with the repaired frequency control.

WHAT CANNOT. Layer and polynomial-degree variants are not in the locked sample;
recomputing them requires fresh forward passes over the corpus. Those parts of
the claim are not re-verified here and the Methods wording is narrowed
accordingly rather than left as an unsupported assertion.

Each window is entered in the headline specification (repaired frequency) and
compared by the improvement in fit it contributes over the same model without it.
Subject-level sign agreement is reported alongside, since that is the paper's
declared reliability criterion.
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
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))

WINDOWS = [c for c in S.columns if c.startswith("tee_k")]
NORMED = [c for c in S.columns if c.startswith("teeN_k")]
print(f"locked sample {sh}   windows available: "
      f"{[c.replace('tee_k','') for c in WINDOWS]}")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
cols = ["story_id", "zone", "surprisal", "word_length",
        "log_freq_fixed"] + WINDOWS + NORMED
d = rt.merge(S[cols], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq_fixed", "zone",
                     "prev_log_RT", "surprisal", "tee_k3"])
for c in ["word_length", "zone", "prev_log_RT", "log_freq_fixed",
          "surprisal"] + WINDOWS + NORMED:
    if c in d:
        d["z_" + c] = z(d[c])
print(f"n = {len(d):,}   participants = {d.participant.nunique()}\n")

BASE = ("log_RT ~ z_word_length + z_log_freq_fixed + z_zone + z_prev_log_RT "
        "+ z_surprisal")
m0 = smf.mixedlm(BASE, d, groups=d.participant).fit(reml=False,
                                                    method="lbfgs")


def subj(col):
    out = []
    cols_ = [col, "surprisal", "word_length", "log_freq_fixed", "zone",
             "prev_log_RT"]
    for pid, s in d.groupby("participant"):
        s = s.dropna(subset=cols_ + ["log_RT"])
        if len(s) < 300:
            continue
        X = np.column_stack([zs(s[c].values) for c in cols_])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s.log_RT.values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


print("=" * 78)
print("WINDOW SWEEP, layer 6, repaired frequency control")
print("=" * 78)
print(f"{'window k':>9}{'dAIC':>10}{'beta':>11}{'% positive':>13}{'p':>12}")
rows = []
for c in sorted(WINDOWS, key=lambda x: int(x.split("k")[-1])):
    if d[c].notna().sum() < 1000:
        continue
    sub = d.dropna(subset=[c])
    b0 = smf.mixedlm(BASE, sub, groups=sub.participant).fit(reml=False,
                                                            method="lbfgs")
    b1 = smf.mixedlm(BASE + f" + z_{c}", sub, groups=sub.participant).fit(
        reml=False, method="lbfgs")
    sb = subj(c)
    rows.append((int(c.split("k")[-1]), b0.aic - b1.aic, b1.params[f"z_{c}"],
                 (sb > 0).mean(), stats.wilcoxon(sb).pvalue))
    k, a, bb, pos, p = rows[-1]
    star = "  <-- reported" if k == 3 else ""
    print(f"{k:>9}{a:>10.1f}{bb:>11.5f}{pos:>12.1%}{p:>12.2e}{star}")

best = max(rows, key=lambda r: r[1])
print(f"\n  best fit by dAIC: k = {best[0]} ({best[1]:.1f})")
print(f"  k = 3 (reported): dAIC {[r for r in rows if r[0]==3][0][1]:.1f}")
print("\n  NOTE: layer and polynomial-degree variants are not in the locked")
print("  sample and are NOT verified by this sweep.")
