# Pre-registration: TEE and regression probability in ZuCo

Written **before** running anything on the ZuCo eye-tracking data.
Timestamp: 2026-07-27, following the OneStop result.

## Background

In OneStop (180 participants, subject-level inference, fair specification with
OneStop's own surprisal and article-context TEE):

- TEE predicts **probability of a regression out** of a word: β = +0.0165,
  111/180 participants positive, Wilcoxon p = 3.4e-5
- stronger punctuation-free (+0.0189) and deeper into the text (+0.0226)
- **surprisal does NOT** predict regression probability: β = −0.0033, p = .22
- TEE does not predict first fixation, gaze duration, or go-past
- regression *count* is null; conditional go-past given a regression is null

Proposed account: a trajectory departure produces a decision to look back rather
than a longer look. In self-paced reading, looking back is impossible, so the
cost surfaces as button-press latency (the Natural Stories effect). In free
reading it surfaces as a regression.

## Predictions for ZuCo (10 subjects, different lab, different stimuli)

**P1 (primary).** TEE positively predicts regression probability, subject-level,
controlling word length, log frequency and surprisal.
Direction is the test; with n = 10 the OneStop-based power estimate is low
(the earlier simulation gave ~22-42% detection at n = 10 for effects of this
size), so **the pre-specified primary criterion is DIRECTION plus a binomial
sign test**, not p < .05 on a Wilcoxon.
  - supportive: ≥ 7/10 subjects positive
  - null: 4-6/10 positive
  - contradictory: ≤ 3/10 positive

**P2.** TEE does NOT predict first fixation duration or gaze duration
(replicating the OneStop nulls). Supportive if 4-6/10 positive.

**P3.** Surprisal does NOT predict regression probability, while it DOES predict
fixation durations. This is the dissociation that makes the finding
interesting; if surprisal predicts regressions in ZuCo, the OneStop
dissociation was corpus-specific and the story weakens considerably.

## Analysis, fixed in advance

- Regression measure: ZuCo does not ship a regression-out flag. Derive it as
  **go-past (GPT) > gaze duration (GD)** on fixated words, which is true exactly
  when the reader left the word to the left before moving past it.
- Predictors: word_length, log frequency, GPT-2 surprisal (computed in the same
  forward pass as TEE), TEE k=3 layer 6, sink excluded from all fit windows.
- Inference: one logistic (or OLS for durations) regression per subject, then a
  group test across subjects. Never pooled across words.
- Exclusions: unfixated words for duration measures; punctuation-final words
  reported separately.

## Commitment

If P1 comes out null or contradictory, the OneStop regression effect is reported
as a single-corpus result requiring replication, and it does not become the
paper's headline. I will not reinterpret a null as support.
