# ZuCo test of the regression prediction — mixed, and it breaks my account (2026-07-27)

Preregistered in `PREREG_zuco_regressions.md` before running. 12 subjects,
30,708 fixated words, regression flag derived as GPT > GD (pre-specified),
subject-level inference, controls = word length, log frequency, surprisal.
Output: `zuco_regress.txt`.

## Results against the pre-specified predictions

| prediction | pre-specified criterion | result | verdict |
|---|---|---|---|
| **P1** TEE → regression probability | ≥ 7/10 positive | 8/12 (67%), β = +0.034, sign p = .39, Wilcoxon p = .034 | **weakly supportive, does not clear the bar** |
| **P2** TEE does NOT predict durations | 4–6/10 positive | TRT **11/12**, β = +0.0079, sign p = .006; GD 10/12, p = .042 | **CONTRADICTED** |
| **P3** surprisal predicts durations, not regressions | — | surprisal GD p = .68, TRT p = .052; regression model failed to converge | **untestable / surprisal weak here** |

Punctuation-free P1: 9/12 positive, β = +0.037, Wilcoxon p = .034.

## What this does to the account

The story I proposed — trajectory departure produces a look-back rather than a
longer look, so TEE predicts regressions and not durations — required P2. P2 is
contradicted in the opposite direction: in ZuCo, TEE predicts **total reading
time** in 11 of 12 subjects. That is the cleanest duration effect in any
eye-tracking data I have run, and it is exactly what the account said should not
happen.

So the account is dead. I am not going to construct a third one.

## The actual state of the evidence

Three behavioral corpora, and they do not agree:

| corpus | paradigm | n | TEE → reading time |
|---|---|---|---|
| Natural Stories | self-paced | 171 | **positive**, 73% of participants, p = 5e-12 |
| ZuCo | eye-tracking, isolated sentences | 12 | **positive** (TRT), 11/12, p = .003 |
| OneStop | eye-tracking, paragraphs | 180 | **null to negative**, TRT β = −0.0023, p = .029 |

The mismatch is therefore **not** self-paced versus eye-tracking — ZuCo is free
reading and shows a positive duration effect agreeing with Natural Stories. The
odd one out is OneStop, which is also the best-powered.

Candidate differences for OneStop specifically, none tested:
- Guardian news prose vs narrative (Natural Stories) and mixed sentences (ZuCo)
- multi-line paragraph display vs single sentences
- a comprehension-question task after every paragraph
- 360 participants recruited across two sites (MIT / Technion)

Note also that ZuCo's earlier in-house analysis found a *null* on the same data
(`HONEST_RESULTS_behavioral.md`: TRT Wilcoxon p = .065, 10 subjects). The
difference here is log-transformed durations, a surprisal control, and all 12
subjects rather than 10. That is a defensible spec, but it means the ZuCo result
is sensitive to analysis choices in a way the Natural Stories result is not.

## Honest summary

- The OneStop regression effect (β = +0.017, p = 3.4e-5, n = 180, surprisal
  null on the same measure) is real and interesting, and it replicates weakly in
  ZuCo (8/12, p = .034 by Wilcoxon, not by sign test).
- The duration effects are inconsistent across corpora and the inconsistency is
  not explained by paradigm.
- Nothing here supports a confident claim that TEE indexes human processing cost
  in general. It supports "TEE predicts reading behaviour in some corpora and not
  others, for reasons not currently understood."

## Recommendation

Do not build the paper on the behavioral results. Framing B — the model-internal
geometry, where the dissociation and the causal wake are large, controlled and
audited — does not depend on any of this. The behavioral work becomes a section
reporting a mixed picture honestly, or a separate paper once the OneStop
discrepancy is understood.
