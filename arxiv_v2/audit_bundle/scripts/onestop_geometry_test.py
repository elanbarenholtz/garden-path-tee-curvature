"""
WHICH COMPONENT DRIVES SKIPPING: RUN-UP GEOMETRY OR TARGET DEVIATION?
=====================================================================
onestop_geometry.py decomposed the measure and reproduced it exactly
(r = 1.0000000000 against the existing values). The components:

  RUN-UP ONLY, known before word i is fixated:
    slope_norm   length of the fitted per-step vector
    curv_prev    bend of the run-up
    last_step    size of the last step into i-1
  TARGET DEVIATION, only knowable after fixating word i:
    resid_perp   residual orthogonal to the heading  -- "went somewhere else"
    resid_par    residual along the heading (negative = the extrapolation
                 overshot; the trajectory did not travel as far as predicted)

The separation is clean where it matters: resid_perp is essentially uncorrelated
with slope_norm (r = .049) and curv_prev (r = -.050), so the two families are
not competing for the same variance.

Note on what the measure mostly is: tee correlates +0.62 with slope_norm and
-0.85 with resid_par. A high value therefore reflects, more than anything, that
the extrapolation OVERSHOT after a straight run-up -- not that the word landed
somewhere unexpected. That is worth knowing regardless of how this test comes
out.

TESTS (subject-level, controls = surprisal, log frequency, word length,
punctuation of the current word):
  G1  skip ~ tee                                  [the reported effect]
  G2  skip ~ slope_norm + curv_prev               [run-up only]
  G3  skip ~ resid_perp + resid_par               [target deviation only]
  G4  skip ~ all four                             [head to head]
  G5  G4 + previous word length/frequency/surprisal   [deflationary check]
  G6  same as G4 for first fixation duration      [contrast]

Fixed in advance: if the run-up terms carry the effect and survive in G4, the
skipping result is about the coherence of the preceding context, not about the
target word, and the timing objection dissolves. If resid_perp carries it, the
reader is responding to the target word and the parafoveal question stands.
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
d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_geometry.csv"),
            on=KEY, how="left")
d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[
            KEY + ["word"]], on=KEY, how="left")
for c in use:
    if c not in ["participant_id"] + KEY:
        d[c] = pd.to_numeric(d[c], errors="coerce")
d = d.rename(columns={"gpt2_surprisal": "surprisal"})
d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
d["punct"] = d.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
d["skipped"] = (d.IA_DWELL_TIME.fillna(0) == 0).astype(float)
d["logFFD"] = np.log(d.IA_FIRST_FIXATION_DURATION.where(
    d.IA_FIRST_FIXATION_DURATION > 0))

d = d.sort_values(TRIAL + ["IA_ID"]).reset_index(drop=True)
g = d.groupby(TRIAL)
for nm, src in [("len_m1", "word_length"), ("freq_m1", "log_freq"),
                ("surp_m1", "surprisal")]:
    d[nm] = g[src].shift(1)
d["id_m1"] = g["IA_ID"].shift(1)
bad = (d["IA_ID"] - d["id_m1"]) != 1
for c in ["len_m1", "freq_m1", "surp_m1"]:
    d.loc[bad, c] = np.nan

print(f"rows {len(d):,}   participants {d.participant_id.nunique()}")
print(f"mean P(skip) = {d.skipped.mean():.3f}\n")

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
        for f in focus:
            out[f].append(r.params[cols.index(f) + 1])
    return {f: np.array(v) for f, v in out.items()}


def row(label, b):
    if len(b) < 10:
        print(f"    {label:<38} too few")
        return
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue
    star = "  *" if (p < .01 and max(pos, 1 - pos) >= .65) else ""
    print(f"    {label:<38} beta={b.mean():>+9.5f}  {pos:>5.1%} pos  "
          f"p={p:<10.2e}{star}")


RUNUP = ["slope_norm", "curv_prev"]
TARGET = ["resid_perp", "resid_par"]

print("=" * 88)
print("OUTCOME: P(skip)          [* = p<.01 and >=65% sign agreement]")
print("=" * 88)
print("\n  G1  the reported effect")
row("tee", subj(["tee"], [], "skipped")["tee"])

print("\n  G2  run-up geometry only (pre-fixation information)")
r2 = subj(RUNUP, [], "skipped")
for f in RUNUP:
    row(f, r2[f])

print("\n  G3  target deviation only (post-fixation information)")
r3 = subj(TARGET, [], "skipped")
for f in TARGET:
    row(f, r3[f])

print("\n  G4  head to head, all four entered")
r4 = subj(RUNUP + TARGET, [], "skipped")
for f in RUNUP + TARGET:
    row(f, r4[f])

print("\n  G5  G4 + previous-word length, frequency, surprisal")
r5 = subj(RUNUP + TARGET, PREV, "skipped")
for f in RUNUP + TARGET:
    row(f, r5[f])

print("\n" + "=" * 88)
print("OUTCOME: first fixation duration (contrast)")
print("=" * 88)
r6 = subj(RUNUP + TARGET, [], "logFFD")
for f in RUNUP + TARGET:
    row(f, r6[f])

print("\n" + "=" * 88)
print("READING")
print("=" * 88)
print("""  Run-up terms surviving in G4/G5 -> the skipping effect is about the
  coherence of the preceding context, which the reader has already read. The
  timing objection to the skipping result dissolves, and the measure's
  behavioural signature in free reading is not about the target word at all.

  resid_perp surviving instead -> the reader is responding to the target word,
  and how they could do so before fixating it remains to be explained.""")
