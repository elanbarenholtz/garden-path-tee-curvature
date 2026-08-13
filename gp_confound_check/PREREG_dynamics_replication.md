# Pre-registration: does the dynamic TEE response replicate in eye-tracking?

Written before the held-out data are touched. Timestamp 2026-07-28.
Natural Stories analyses (P1, P2) are complete and their results are fixed.

## The prediction, and why it matters

All prior eye-tracking analyses in this project tested TEE at **lag 0 only** —
does TEE at word *t* predict a reading measure at word *t*. In OneStop that was
null (first fixation, gaze duration) or slightly negative (total reading time).

Natural Stories now shows the response **peaks at lag 1**, not lag 0
(β = +0.0205 vs +0.0160, 81.9% vs 74.9% sign agreement). If that lag structure
is a property of the effect rather than of self-paced reading, then the OneStop
non-replication may be an artefact of measuring at the wrong lag.

This is a sharp, falsifiable prediction and it is worth stating plainly:
**if TEE's effect in OneStop is also positive at lag 1, the earlier
non-replication was a lag-alignment error. If lag 1 is null or negative, the
non-replication stands and is not about lag.**

## Data

- **OneStop** ordinary-reading subcorpus, 180 participants. Primary.
- **ZuCo**, 12 participants. Secondary, underpowered, reported for direction only.

Both use TEE already computed for those corpora (`onestop_tee_ctx.csv`,
`zuco_tee.csv`), GPT-2 Small layer 6 k=3, sink excluded from fit windows.

## P3 (primary, OneStop)

Impulse response of log total reading time to z(TEE) across lags 0–5, all lags
in one model, per participant, group test across participants. Controls at every
lag: surprisal (the corpus's own annotation), log frequency, word length,
punctuation. Lag = next word in the text, defined by interest-area order.

**Criteria, fixed now:**
- *Replication:* β at lag 1 is positive, Wilcoxon p < .0017 (Bonferroni for 6
  lags), and ≥ 65% of participants share the sign.
- *Non-replication:* lag 1 fails either condition.

I commit to reporting this either way. A null at lag 1 means the eye-tracking
failure is real and not a lag artefact, and that is the conclusion I will draw.

## P4 (secondary, OneStop): decay comparison

Late/early ratio R = (β₃+β₄+β₅)/(β₀+β₁+β₂) for TEE and surprisal, paired
Wilcoxon, same positivity guard as P2 (include only participants with positive
early-lag sums for both measures; report the number excluded).

Prediction: R_TEE < R_surprisal, matching Natural Stories.

## P5 (secondary, ZuCo)

Same as P3 on total reading time. 12 participants; direction and sign count
reported, no significance claim.

## Known interpretive limit, stated before seeing results

In self-paced reading, word *t+1* is necessarily read after word *t*. In free
eye movement it is not — readers skip and regress. So "lag" in eye-tracking is
position in the text, not necessarily order of processing. A null at lag 1 in
OneStop is therefore ambiguous between "no effect" and "lag in text is the wrong
alignment for eye movements." This limit is stated now so it cannot be deployed
selectively after seeing a null.

A positive result at lag 1 does not suffer this ambiguity.

## Not permitted

Trying lags beyond 0–5, other TEE variants, other eye-tracking measures
(first fixation, gaze duration, regression probability) as the primary test, or
subsetting, in order to find a positive lag. Any of these may be run afterwards
as explicitly labelled exploratory analyses.
