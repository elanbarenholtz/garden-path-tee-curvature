"""
IS THE SKIPPING EFFECT ABOUT THE TARGET WORD OR ABOUT THE RUN-UP?
==================================================================
OneStop shows that words with high extrapolation error are SKIPPED more
(beta = +0.008, 66.1% of participants, p = 4.6e-8), while first fixation
duration is null. A reader cannot skip a word *because* it broke their
interpretation -- the skipping decision is made parafoveally, before the word is
identified. So either enough of the target word is extracted in the parafovea to
drive the decision, or the effect is not about the target word at all.

The second possibility has a mechanism behind it. Extrapolation error at word t
is the distance from a line fitted through words t-3..t-1. When that window is
STRAIGHT, the fitted step is long, the extrapolation projects far, and there is
more room to miss -- high error. When the window is BENT, the fitted step is
short and the prediction cannot miss by much -- low error. (This project's own
null-model work found exactly this: r(curvature(t-1), ||fitted slope||) is
strongly negative.) So high extrapolation error partly indexes "the preceding
context was moving coherently in one direction" -- which is the condition under
which a reader can predict what comes next and skip it. And all of that is
available BEFORE fixating word t.

CHEAP TEST, using only data already computed. If the effect lives in the run-up
rather than in the target word, then the PREVIOUS word's extrapolation error
should predict skipping of the current word.

  S1  skip(t) ~ tee(t)                     [the reported effect]
  S2  skip(t) ~ tee(t-1)                   [run-up proxy, fully pre-fixation]
  S3  skip(t) ~ tee(t) + tee(t-1)          [which survives?]
  S4  skip(t) ~ tee(t-1) + tee(t-2)        [how far back does it go?]
  S5  same as S3 for first fixation duration, for contrast

Controls throughout: surprisal, log frequency, word length, punctuation -- of the
CURRENT word, plus the previous word's length and frequency in S3-S4, since
parafoveal skipping is strongly driven by the properties of the launch word.

Interpretation fixed in advance:
  - tee(t-1) predicts skipping and survives alongside tee(t)  -> run-up account
    supported; the expensive decomposition is worth doing.
  - only tee(t) predicts skipping                             -> parafoveal
    identification of the target word; run-up account not supported.
  - neither survives with previous-word controls added        -> the effect is
    launch-site lexical properties, and is deflationary.
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
TRIAL = ["participant_id", "article_id", "paragraph_id", "difficulty_level"]


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
                                  "wordfreq_frequency", "gpt2_surprisal",
                                  "IA_FIRST_FIXATION_DURATION"]
d = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
            on=KEY, how="left")
d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[
            KEY + ["word"]], on=KEY, how="left")
for c in use:
    if c not in ["participant_id"] + KEY:
        d[c] = pd.to_numeric(d[c], errors="coerce")
d = d.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
d["punct"] = d.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
d["skipped"] = (d.IA_DWELL_TIME.fillna(0) == 0).astype(float)
d["logFFD"] = np.log(d.IA_FIRST_FIXATION_DURATION.where(
    d.IA_FIRST_FIXATION_DURATION > 0))

# ---- lagged predictors, contiguity enforced on interest-area order ----
d = d.sort_values(TRIAL + ["IA_ID"]).reset_index(drop=True)
g = d.groupby(TRIAL)
for L in (1, 2):
    d[f"tee_m{L}"] = g["tee"].shift(L)
    d[f"len_m{L}"] = g["word_length"].shift(L)
    d[f"freq_m{L}"] = g["log_freq"].shift(L)
    d[f"surp_m{L}"] = g["surprisal"].shift(L)
    d[f"id_m{L}"] = g["IA_ID"].shift(L)
    bad = (d["IA_ID"] - d[f"id_m{L}"]) != L
    for c in [f"tee_m{L}", f"len_m{L}", f"freq_m{L}", f"surp_m{L}"]:
        d.loc[bad, c] = np.nan
print(f"rows {len(d):,}   participants {d.participant_id.nunique()}")
print(f"mean P(skip) = {d.skipped.mean():.3f}")
print(f"r(tee(t), tee(t-1)) = {d.tee.corr(d.tee_m1):+.3f}   "
      f"r(tee(t), log_freq) = {d.tee.corr(d.log_freq):+.3f}   "
      f"r(tee(t), word_length) = {d.tee.corr(d.word_length):+.3f}")
print(f"r(tee(t-1), len(t-1)) = {d.tee_m1.corr(d.len_m1):+.3f}\n")

CUR = ["surprisal", "log_freq", "word_length", "punct"]
PREV = ["len_m1", "freq_m1", "surp_m1"]


def subj(focus, extra, outcome, minn=200):
    cols = focus + CUR + extra
    out = {f: [] for f in focus}
    for pid, s in d.groupby("participant_id"):
        s = s.dropna(subset=cols + [outcome])
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        r = sm.OLS(zs(s[outcome].values), sm.add_constant(X)).fit()
        for i, f in enumerate(focus):
            out[f].append(r.params[cols.index(f) + 1])
    return {f: np.array(v) for f, v in out.items()}


def row(label, b):
    if len(b) < 10:
        print(f"  {label:<40} too few")
        return
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue
    star = "  *" if (p < .01 and max(pos, 1 - pos) >= .65) else ""
    print(f"  {label:<40} n={len(b):>4}  beta={b.mean():>+9.5f}  "
          f"{pos:>5.1%} pos  p={p:<10.2e}{star}")


print("=" * 92)
print("OUTCOME: P(skip)")
print("=" * 92)
row("S1  tee(t) alone", subj(["tee"], [], "skipped")["tee"])
row("S2  tee(t-1) alone", subj(["tee_m1"], [], "skipped")["tee_m1"])
r3 = subj(["tee", "tee_m1"], [], "skipped")
row("S3  tee(t)   [both entered]", r3["tee"])
row("S3  tee(t-1) [both entered]", r3["tee_m1"])
r4 = subj(["tee_m1", "tee_m2"], [], "skipped")
row("S4  tee(t-1) [t-1 and t-2]", r4["tee_m1"])
row("S4  tee(t-2) [t-1 and t-2]", r4["tee_m2"])

print("\n  with previous-word lexical controls added "
      "(length, frequency, surprisal of t-1):")
r5 = subj(["tee", "tee_m1"], PREV, "skipped")
row("S3b tee(t)   + prev lexical", r5["tee"])
row("S3b tee(t-1) + prev lexical", r5["tee_m1"])

print("\n" + "=" * 92)
print("OUTCOME: first fixation duration (for contrast)")
print("=" * 92)
r6 = subj(["tee", "tee_m1"], [], "logFFD")
row("tee(t)", r6["tee"])
row("tee(t-1)", r6["tee_m1"])

print("\n" + "=" * 92)
print("READING")
print("=" * 92)
print("""  tee(t-1) predicting skipping, and surviving alongside tee(t), supports the
  run-up account: the measure partly indexes how coherently the preceding
  context was moving, which is information the reader has before fixating.
  If tee(t-1) dies once previous-word length and frequency are controlled, the
  effect is launch-site lexical properties and the account is deflationary.""")
