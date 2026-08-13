# Subject-level inference: does the Natural Stories effect survive the ZuCo standard? (2026-07-27)

The ZuCo eye-tracking analysis returned a null using subject-level inference —
one beta per subject, group test across subjects, explicitly to avoid
pseudoreplication. The Natural Stories result pools 813,621 observations with a
by-participant random intercept. Applying the stricter standard to Natural
Stories decides whether ΔAIC = 112 is a real effect or a large-N artifact.

Script `ns_subject_level.py`; per-participant coefficients in
`subject_betas_*.csv`.

## Result: it survives, comfortably

One OLS per participant (171 of 178 with enough data), then a group test on the
distribution of TEE coefficients.

| specification | positive betas | mean β | Wilcoxon p | t-test | individually sig |
|---|---|---|---|---|---|
| FULL controls (length, freq, position, prevRT, surprisal) | **125/171 (73.1%)** | +0.00388 | 5.1e-12 | t(170) = 7.46, p = 4.2e-12 | 39/171 |
| ZuCo-style controls (length, freq only) | **136/171 (79.5%)** | +0.00577 | 3.3e-16 | t(170) = 9.29, p = 7.4e-17 | 44/171 |
| punctuation-free, FULL controls | **128/171 (74.9%)** | +0.00442 | 3.5e-13 | t(170) = 7.83, p = 5.0e-13 | 43/171 |

Three-quarters of participants show a positive effect independently, sign test
p = 1.2e-9. The per-participant mean β (+0.0039) closely matches the pooled
estimate (+0.0035), which is what a genuine effect looks like and what a
large-N artifact does not.

**The pooled Natural Stories result is not pseudoreplication.** It holds under
the same inferential standard that produced the ZuCo null.

## So why is ZuCo null?

Not because the analysis standard differs — Natural Stories passes that standard.
Candidate explanations, in the order I would argue them:

1. **Power.** ZuCo has 10 subjects; Natural Stories has 171. Only 23% of
   individual Natural Stories participants reach p < .05 on their own, so with
   n = 10 a group test would frequently miss. Note ZuCo's FFD (p = .084) and TRT
   (p = .065) both trend positive — consistent with a real but small effect the
   study is underpowered to resolve.
2. **Paradigm.** Self-paced reading forces a button press per word and is
   sensitive to integration difficulty; free eye movement allows skipping,
   regressions, and parafoveal preview. A trajectory-integration cost has an
   obvious route into button-press latency and a much less direct route into
   first-fixation duration.
3. **Stimuli.** ZuCo sentences are isolated, short, and drawn from movie reviews
   and Wikipedia; Natural Stories are long connected narratives. A 3-word
   backward window behaves differently in each — and per the position analysis,
   the TEE effect is weakest at sentence-initial positions and strongest deep
   into a sentence. ZuCo is disproportionately made of the positions where the
   effect is weak.

Point 3 is testable on the existing data: restrict Natural Stories to
sentence-initial and early positions and see whether the effect drops toward the
ZuCo null. If it does, that is a genuine, publishable reconciliation rather than
a hand-wave.

## Recommendation

Report ZuCo. A null in a second paradigm, disclosed and explained, is far
stronger than a paper that quietly uses only the corpus that worked — and the
position-profile explanation is empirically checkable rather than rhetorical.

This also removes the main obstacle to Framing A: the reading-time claim now
rests on 171 independently-estimated participant effects, not on a single pooled
model with a large denominator.
