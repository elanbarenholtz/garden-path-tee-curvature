# Is the TEE-regression effect oculomotor? (2026-07-27)

The concern: regressions are strongly driven by where a word sits on screen, and
OneStop displays multi-line paragraphs. If TEE correlates with line position,
the effect could be an artifact of eye-movement mechanics rather than language.
Output: `onestop_oculo.txt`, `onestop_oculo2.txt`.

## Screen position matters enormously — and TEE is orthogonal to it

P(regression out) by line position:

| position | P(regress) |
|---|---|
| line-initial | 0.056 |
| line-medial | 0.182 |
| **line-final** | **0.264** |

A near-5× swing. So the confound was worth taking seriously. But TEE barely
correlates with any spatial variable:

| variable | r with TEE |
|---|---|
| x-position within line | −0.001 |
| is line-final | +0.009 |
| is line-initial | +0.001 |
| line number | −0.010 |
| (word length, for scale) | +0.120 |

The two are cleanly separable: screen position drives regressions hard, TEE
doesn't track screen position at all.

## The effect survives the controls

| model | β | sign test | Wilcoxon |
|---|---|---|---|
| linguistic controls only | +0.0165 | .002 | 3.4e-5 |
| + line number, x-in-line | +0.0153 | .002 | 1.0e-4 |
| + launch site, landing position | +0.0162 | .006 | 6.6e-5 |

Essentially unchanged, and it clears both the sign test and the Wilcoxon.

## But it weakens on line-medial words

Dropping line-initial and line-final words entirely (957,902 of 1,104,883 rows
retained):

| model | β | sign test | Wilcoxon |
|---|---|---|---|
| line-medial only, linguistic controls | **+0.0080** | .21 | .031 |
| line-medial only, + spatial controls | +0.0079 | .33 | .038 |

The coefficient halves (+0.0165 → +0.0080) and the sign test goes null, though
Wilcoxon stays marginal. So roughly half the effect lives at line boundaries —
which the covariate-adjusted models were apparently not fully absorbing.

That is not the same as the effect being an artifact: TEE is uncorrelated with
line-final status (r = 0.009), so it is hard to see how line position alone
manufactures a TEE coefficient. But the honest reading is that the effect is
**smaller and less certain than the headline number**, and part of it is
carried by words in positions where regressions are most frequent and most
mechanically determined.

## Verdict

Is it real? **Probably, but half the size I first reported, and I would not build
a paper on it yet.**

What it survives: fair specification, surprisal controls, previous-word
controls, punctuation-free subsetting, position-in-text, Bonferroni across the
eight eye-movement measures tested, oculomotor covariates, and a weak
same-direction replication in ZuCo (8/12).

What still concerns me: line-medial β is half the full-sample β with a null sign
test; the ZuCo replication does not clear its preregistered bar; there is no
time-cost mechanism (conditional go-past is null); and 62% of participants
positive is a modest majority.

The genuinely interesting part remains that surprisal predicts regressions not
at all (p = .22) while TEE does. If that dissociation holds up in a
preregistered test on new data, it is worth a paper on its own. Right now it is
one well-powered corpus, one weak partial replication, and a coefficient that
halves under the most conservative subsetting.

## What would settle it

A preregistered test on a fresh eye-tracking corpus with single-line or
sentence-at-a-time presentation, which removes line-boundary mechanics from the
picture entirely. Provo (84 participants, short passages) or GECO (14
participants, whole novel) would both work. CELER presents isolated sentences
and would be the cleanest for this specific question despite its other
limitations.
