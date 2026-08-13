# Pre-registration: does TEE shape reading-time DYNAMICS?

Written before any of the analyses below are run. Timestamp 2026-07-28.
Everything specified here is fixed; deviations must be reported as deviations.

## Motivation

All analyses to date ask whether TEE at word *t* predicts reading time at word
*t*. But TEE is a property of a trajectory over several words, and reading times
are themselves a sequence with structure — autocorrelation, runs, acceleration.
The current design treats that structure as nuisance (the `prev_log_RT` control)
rather than as the thing to be explained.

If the trajectory account is right, a departure from the representational path
should perturb the *reading-time series*, not merely raise one value. A
single-lag coefficient captures the lag-0 slice of that perturbation and nothing
else. In particular, a biphasic response — speeding up then slowing, or the
reverse — would produce a near-zero or sign-unstable single-lag estimate, which
is consistent with what we observe across corpora.

## Data

Natural Stories, locked sample 8a6087341e (GPT-2 Small, layer 6, k = 3),
self-paced reading, 171 participants, hash asserted before every table.

Confirmatory analyses use Natural Stories only. OneStop is designated a
**held-out replication set** and will not be examined until the Natural Stories
analyses are complete and written up.

## Primary analysis (P1): impulse-response function

Estimate the response of log reading time to a TEE impulse across lags 0–5.

- Impulse: z(TEE) at word *t*.
- Outcome: z(log RT) at words *t* through *t+5*.
- Simultaneous lags in one model (not separate models per lag), so each lag's
  coefficient is adjusted for the others.
- Controls, entered at every lag alongside TEE: surprisal, log frequency, word
  length, punctuation. Plus position (from_start, fs2, from_end, fe2) and story
  fixed effects. `prev_log_RT` is **excluded** from the primary model, because
  it absorbs precisely the autocorrelation this analysis is about; a secondary
  model including it is specified below.
- Estimation: per participant, then group test across the 171 participants
  (Wilcoxon and sign test). Never pooled across words.

**Pre-specified criteria.**

- *Support for a dynamic response:* the lag profile differs reliably from a
  flat profile — omnibus test of lag×TEE across lags 0–5, p < .01 — AND at
  least one lag beyond lag 0 reaches p < .01 with ≥ 65% of participants sharing
  its sign.
- *Support for the biphasic hypothesis specifically:* coefficients at two
  separated lags have opposite signs, each with p < .01 and ≥ 65% of
  participants sharing the sign.
- *Null:* no lag beyond 0 clears p < .01, or the profile does not differ from
  flat.

I commit to reporting the full lag profile whatever it shows, including when
lag 0 is the only significant term (which would mean the current single-lag
approach was already adequate and this analysis adds nothing).

## Secondary analyses, all pre-specified

**S1. With `prev_log_RT` included.** Same model plus the lagged-RT control.
Reported alongside P1; if the profile changes materially, both are reported and
neither is preferred post hoc.

**S2. Surprisal's impulse response, same model.** A reference profile. Surprisal
is an established predictor, so its response shape calibrates what a real
impulse response looks like in this data, and shows whether any TEE profile is
distinctive or just the generic shape.

**S3. Reading-time extrapolation error.** Apply TEE's own operation to the RT
series: fit a line to log RT at words *t−3…t−1*, extrapolate one step, take the
absolute error. Ask whether hidden-state TEE at *t* predicts this quantity,
with the same controls. Tests whether a break in the model's trajectory
coincides with a break in the reader's pacing.

**S4. Does TEE reduce the predictability of subsequent RTs?** Per participant,
correlate TEE at *t* with the absolute residual of an AR(2) model of log RT
fitted within story. Tests disruption of dynamics rather than shift in level.

## Analyses I am NOT permitted to run under this pre-registration

Free choice of lag window after seeing results; smoothing or basis functions
chosen post hoc; alternative TEE variants (par, perp, normalised, neighbourhood)
substituted for tee_k3 in the primary test; subsetting by position, punctuation
or word class except as pre-specified. Any of these may be run as clearly
labelled exploratory follow-ups, never as the confirmatory result.

## Multiple comparisons

P1 involves 6 lags. The omnibus test is primary. Per-lag claims use
Bonferroni-corrected α = .01/6 = .0017 for the "significant lag" criterion above,
and this is the threshold referred to by "p < .01" in the criteria — stated
explicitly here to prevent later softening.

S1–S4 are four secondary tests and are reported with that count stated.

## Implementation constraints (from this project's failure history)

- Sample hash asserted before every table.
- All merges use `validate="one_to_one"`.
- Lags computed **before** any row filtering, and row counts asserted after
  each step.
- Number of rows entering each model printed and checked against expectation.
- The script prints the full lag profile; no result is summarised by the same
  pass that produced it without the raw table alongside.

## Commitment

If P1 returns the pre-specified null, the conclusion is that TEE does not shape
reading-time dynamics beyond its lag-0 effect, and the dynamics framing is
abandoned rather than reformulated. I will not reinterpret a flat profile as
support.
