"""
WHAT DRIVES THE NEGATIVE TEE EFFECT ON ONESTOP TOTAL READING TIME?
==================================================================
Verification established that the OneStop result is not a null: total reading
time carries a reliably NEGATIVE coefficient for extrapolation error under every
specification tried (-0.0023 to -0.0060, the stronger estimates from the better
controlled models). That is a harder fact than an absence, and the preview
account in the Discussion does not obviously explain it -- preview predicts
attenuation toward zero, not a sign flip.

Before deciding how to write it, find out whether the negative is (a) a genuine
duration effect, or (b) an artifact of what total reading time aggregates.

TRT sums ALL fixations on a word, including refixations and fixations from
regressions back to it. So TRT ~= first-pass duration + re-reading. If high-TEE
words are SKIPPED more often, or attract fewer refixations, TRT falls without
any word ever being read faster.

DECOMPOSITION (all subject-level, same controls):
  1. skipping        P(skip)          -- is the word fixated at all?
  2. first fixation  FFD              -- earliest measure, first-pass only
  3. gaze duration   GD               -- first-pass, all fixations before leaving
  4. total time      TRT              -- everything, including re-reading
  5. re-reading      TRT - GD         -- the part that is not first pass
  6. refixation      P(GD > FFD)      -- did the reader refixate within first pass

If the negative lives in skipping or in (TRT - GD), it is about where the eyes
GO, not about how long processing takes, and the Discussion should say so.
If it is present in GD and FFD too, it is a genuine speed-up and needs an
account.

Conditioning note, stated in advance: measures 2-6 are conditional on the word
being fixated, so if skipping is itself predicted by TEE they inherit a
selection effect. That is why skipping is tested first and reported regardless.
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


cols = pd.read_csv(ONESTOP, nrows=0).columns.tolist()
want = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
                                   "wordfreq_frequency", "gpt2_surprisal"]
for c in ["IA_FIRST_FIXATION_DURATION", "IA_FIRST_RUN_DWELL_TIME",
          "IA_FIXATION_COUNT", "IA_SKIP", "IA_FIRST_RUN_FIXATION_COUNT"]:
    if c in cols:
        want.append(c)
print("columns available:", [c for c in want if c not in
      ["participant_id"] + KEY])

d = pd.read_csv(ONESTOP, usecols=want, low_memory=False)
d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
            on=KEY, how="left")
d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[
            KEY + ["word"]], on=KEY, how="left")
for c in want:
    if c not in ["participant_id"] + KEY:
        d[c] = pd.to_numeric(d[c], errors="coerce")
d = d.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
d["punct"] = d.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
print(f"rows {len(d):,}   participants {d.participant_id.nunique()}")

FFD = "IA_FIRST_FIXATION_DURATION"
GD = "IA_FIRST_RUN_DWELL_TIME"
d["skipped"] = (d.IA_DWELL_TIME.fillna(0) == 0).astype(float)
fix = d[d.IA_DWELL_TIME > 0].copy()
fix["logTRT"] = np.log(fix.IA_DWELL_TIME)
if GD in fix:
    fix["logGD"] = np.log(fix[GD].where(fix[GD] > 0))
    fix["reread"] = (fix.IA_DWELL_TIME - fix[GD]).clip(lower=0)
    fix["has_reread"] = (fix.reread > 0).astype(float)
    fix["log_reread"] = np.log(fix.reread.where(fix.reread > 0))
if FFD in fix:
    fix["logFFD"] = np.log(fix[FFD].where(fix[FFD] > 0))
    if GD in fix:
        fix["refix"] = (fix[GD] > fix[FFD]).astype(float)

CTRL = ["surprisal", "log_freq", "word_length", "punct"]


def subj(df, outcome, minn=200):
    out = []
    for pid, s in df.groupby("participant_id"):
        s = s.dropna(subset=["tee"] + CTRL + [outcome])
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in ["tee"] + CTRL])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s[outcome].values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


def row(label, b, note=""):
    if len(b) < 10:
        print(f"  {label:<34} too few participants")
        return
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue
    print(f"  {label:<34} n={len(b):>4}  beta={b.mean():>+9.5f}  "
          f"{pos:>5.1%} pos  p={p:<10.2e} {note}")


print("\n" + "=" * 88)
print("DECOMPOSING THE NEGATIVE")
print("=" * 88)
print("\n  [1] does TEE predict SKIPPING?  (all rows, incl. unfixated)")
row("P(skip)", subj(d, "skipped"), "<- positive = high TEE skipped more")

print("\n  [2-4] durations, conditional on being fixated")
if "logFFD" in fix:
    row("first fixation duration", subj(fix, "logFFD"))
if "logGD" in fix:
    row("gaze duration (first pass)", subj(fix, "logGD"))
row("total reading time", subj(fix, "logTRT"), "<- the reported negative")

print("\n  [5-6] the part of TRT that is not first pass")
if "has_reread" in fix:
    row("P(any re-reading)", subj(fix, "has_reread"))
    row("log re-reading time | any", subj(fix[fix.reread > 0], "log_reread"))
if "refix" in fix:
    row("P(refixation in first pass)", subj(fix, "refix"))
if "IA_FIXATION_COUNT" in fix:
    row("fixation count", subj(fix, "IA_FIXATION_COUNT"))

print("\n" + "=" * 88)
print("READING")
print("=" * 88)
print("""  If the negative is concentrated in skipping, re-reading, or fixation
  count, it reflects where the eyes go rather than how fast a word is read,
  and total reading time is the wrong summary statistic for this measure.
  If first fixation and gaze duration are also negative, it is a genuine
  speed-up and the Discussion owes an account of it.""")
