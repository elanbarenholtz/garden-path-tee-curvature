ated# Pre-registration: does TEE's reading-time response decay faster than surprisal's?

Written before running. Timestamp 2026-07-28, following the P1 result in
`PREREG_rt_dynamics.md` / `rt_dynamics_out.txt`.

## What prompted this

P1 estimated impulse-response functions on Natural Stories and found (observed,
already seen — this is therefore a follow-up, not a fresh confirmatory test):

| lag | TEE β | surprisal β |
|---|---|---|
| 0 | +0.0160 | +0.0226 |
| 1 | +0.0205 | +0.0384 |
| 2 | +0.0085 | +0.0332 |
| 3 | +0.0041 | +0.0210 |
| 4 | +0.0028 | +0.0129 |
| 5 | −0.0005 | +0.0112 |

Descriptively, TEE's response is gone by lag 3 while surprisal's persists to
lag 5. **No formal test of that difference was pre-specified**, and comparing
two profiles by eye is exactly how this project has gone wrong before. This
document fixes the test before it is run.

The comparison matters because the same dissociation appears model-internally:
the ablation analysis found the fine-grained trajectory wake dies after one
word while surprisal's persists 5+. If the behavioural profiles show the same
contrast, representational and behavioural dynamics agree.

## Status of this test

**Follow-up, not confirmatory.** The profiles that motivate it have been seen.
It will be reported as a planned-after-inspection test, and it requires
replication on the held-out OneStop data before it can be treated as
established. That replication is not run under this document.

## Primary test (P2)

Per participant, from the P1 models already specified (lags 0–5, all lags in one
model, standard controls, no `prev_log_RT`):

    R = (β₃ + β₄ + β₅) / (β₀ + β₁ + β₂)

computed separately for TEE and for surprisal. R is scale-free within measure,
so it compares *shape* rather than magnitude.

**Test:** paired Wilcoxon of R_TEE against R_surprisal across participants
(paired, since both come from the same participant's data).

**Criteria, fixed now:**
- *Support:* R_TEE < R_surprisal, paired Wilcoxon p < .01, and ≥ 65% of
  participants show the difference in that direction.
- *Null:* p ≥ .01 or sign agreement < 65%.

**Stability guard:** R is undefined or unstable when the denominator approaches
zero. Participants are included only if the early-lag sum (β₀+β₁+β₂) is positive
for **both** measures. The number excluded will be reported. This rule is fixed
now and will not be adjusted after seeing the exclusion count.

## Secondary tests

**S5. Half-life.** For each participant and measure, the smallest lag at which
|β| falls below 50% of that measure's peak |β| across lags 0–5. Paired Wilcoxon.
Prediction: TEE's is smaller. Reported with the same 65% sign criterion.

**S6. Bootstrap.** 10,000 resamples over participants of the mean difference
R_TEE − R_surprisal, reporting a 95% percentile interval. Descriptive; no
threshold attached.

## Not permitted under this document

Trying other decay statistics after seeing P2 (e.g. exponential fits, other
lag splits, area-under-curve variants) and reporting whichever separates best.
If P2 is null, the conclusion is that the profiles do not differ reliably in
shape, and any further statistic is exploratory and labelled as such.

Substituting other TEE variants (par, perp, normalised, neighbourhood) for
tee_k3.

## Commitment

If P2 is null I will report that the apparent difference in decay is not
statistically supported, and the convergence with the model-internal wake result
will be described as suggestive at best.
