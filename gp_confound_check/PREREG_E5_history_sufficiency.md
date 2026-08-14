# Pre-registration — E5: History Beyond the Current Predictive Distribution

Written 2026-08-14, before any part of this analysis has been run. No sampling,
no candidate-state computation, and no statistic below has been computed on any
corpus at the time of writing. This document fixes the sampling scheme, model
ladder, statistic, exclusions, controls, and outcome interpretation. The
experiment will be run only after this file is committed.

## Core question

Does recent sequential history contain information about the actual human
continuation beyond the model's current next-token distribution P_t?

Surprisal theory's operational commitment is that P_t summarizes everything
cost-relevant about the context. The production-side analogue asks whether P_t
summarizes everything *continuation*-relevant: if human text is effectively a
draw from P_t, then no function of the recent trajectory should distinguish
human continuations from the model's own samples at the same prefix. If human
continuations differ systematically from P_t-samples along a trajectory
dimension, then P_t is not a sufficient statistic for human-generated text.

## Interpretation ceiling, registered in advance

A positive result does NOT show that human production uses history beyond the
human brain's own predictive state. It shows that THIS MODEL'S current output
distribution is not a sufficient statistic, relative to information in the
model-derived recent trajectory, for predicting human continuations. The
deflationary reading -- that the trajectory feature merely recovers information
a weak model failed to express through its output head -- is addressed by the
model ladder below, which is PRIMARY, not robustness: if the effect shrinks
toward zero as P_t improves, the deflationary reading wins.

We will not claim "humans are non-Markovian," "the brain retains trajectory,"
or any statement about the human predictive state from this experiment alone.

## Design (primary): rank of the human continuation among the model's own samples

Everything at GPT TOKEN granularity. No token-level quantity will be described
as a word-level quantity.

For each eligible token position t in each Natural Stories story:

1. Compute P_t = softmax(z_t), the model's full next-token distribution given
   the human prefix, under the project's standard chunked-context convention
   (1024-token chunks, stride 512, first-write-wins), so every position is
   conditioned on at least ~512 tokens of context except early positions.
2. Draw m = 20 candidate tokens i.i.d. from P_t: temperature 1.0, NO top-k,
   NO top-p, full vocabulary. RNG seed 20260814, one stream per story,
   consumption order = position order (fixed so the draw is reproducible).
3. For the human token and each of the 20 candidates, append that single token
   to the prefix and compute its layer-6 hidden state (one incremental forward
   step with cached context; identical machinery for human and candidates).
4. Candidate deviation D(c) = Euclidean distance between the candidate token's
   state and the one-step linear extrapolation of an OLS line fitted to the
   states of the preceding 3 TOKENS (fit window never includes token 0).
   This is the token-level analogue of the paper's measure, applied to
   counterfactual continuations. It is a property of the CANDIDATE and involves
   no leakage: the human token's D is computed identically to every sample's.
5. Position statistic: the mid-rank percentile of the human token's D among
   the 21 values {human, 20 samples}:
       u_t = (rank(D_human) - 0.5) / 21,  ties resolved by mid-rank.

NULL: if the human token is exchangeable with draws from P_t, u_t is uniform
on (0,1) and E[u_t] = 0.5, at every position, regardless of the geometry.
This holds no matter how mechanical, reversed, or artifact-laden the deviation
measure is -- which is precisely why this design survives the failure of the
momentum analysis. The test is of exchangeability, not of any geometric story.

### Primary statistic and test

  U = mean of u_t over eligible positions.

Test: story-level cluster bootstrap (resample the 10 stories with replacement,
10,000 draws) for a 95% CI on U. PRIMARY CRITERION: the CI excludes 0.5.
Direction is NOT assumed; the test is two-sided, and the sign of U - 0.5
(human continuations closer to vs farther from the extrapolation than the
model's samples) is a finding to be reported, not chosen.

Supporting (reported, no criterion): per-story U (sign consistency across the
10 stories); position-level Wilcoxon of u_t vs 0.5; KS distance of u_t from
uniform, as a shape descriptor.

### Negative control (primary, run first)

At every position, draw ONE additional sample from P_t (same settings, separate
seed 20260815) and designate it the pseudo-target. Compute its u_t against the
same 20 candidates. By construction the pseudo-target is exchangeable with the
candidates, so its U must not differ from 0.5.

GATE: if the control CI excludes 0.5, the pipeline is invalid (leakage,
state-computation asymmetry between target and samples, or RNG error).
STOP, diagnose, and do not interpret the human result. The human analysis is
only interpretable if the control passes.

## Model ladder (primary)

Two versions, both registered:

V1 -- fixed geometry, escalating baseline. Deviation D always computed from
GPT-2 Small layer 6 states. P_t (and therefore the samples) from:
   (a) GPT-2 Small   (b) GPT-2 XL   (c) Pythia-410M.
Tests whether the history signal disappears once the current predictive state
is estimated better. Note the candidates differ across rungs because they are
drawn from different P_t; that is the point.

V2 -- matched-model replication. Each model supplies both its own P_t and its
own mid-layer states for D (GPT-2 Small L6; GPT-2 XL mid-layer; Pythia-410M
mid-layer). Tests cross-model generality of the effect.

The ladder is part of the primary outcome logic, not a robustness appendix.

## Eligible positions and exclusions (fixed now)

- All token positions t with at least 4 preceding tokens in the story and a
  fit window that does not include token 0 (i.e., window start index >= 1).
- Positions where any required state is undefined are excluded and counted.
- No exclusions based on the value of any statistic.
- Word-level secondary (only if the primary is positive): restrict to
  positions where the human continuation is a complete single-token word;
  report U on that subset. No whole-word probability construction will be
  attempted in E5.

## Outcome logic (fixed now)

1. Human U deviates from 0.5; control U does not; effect survives the stronger
   P_t rungs (CI excludes 0.5 for XL and Pythia-410M) -> strong evidence that
   human-generated text carries sequential information not exhausted by these
   current predictive distributions. This result is important enough to
   reorganize v2 around; that decision is taken then, not now.
2. Human U deviates for GPT-2 Small but shrinks toward 0.5 up the ladder ->
   the trajectory feature recovers information a weaker model failed to express
   in its output head. Report as a model-insufficiency result; no claim about
   human production. v2 keeps its behavioral framing.
3. Human AND control both deviate -> pipeline artifact. Diagnose; do not
   interpret; report the failure.
4. Neither deviates -> no evidence from this test for history beyond the
   current predictive distribution. Reported as such; v2 keeps its behavioral
   framing.

## If E5 escalates to the residual-logit analysis

The rank test requires no fitted model and is therefore immune to
capacity/topic leakage. If a later phase fits a low-capacity correction
z'_t = z_t + f(H_t), the following become PRIMARY at that phase: story-level
cross-validation; shuffled-history features; within-story temporal permutation
of history; and the AI-sampled target control run through the identical
fitting pipeline. That phase will get its own preregistration; nothing in it
is licensed by this document.

## Not permitted under this document

Changing m, temperature, truncation, seeds, the deviation definition, the fit
window, the rank convention, or the eligible-position rules after seeing any
output; selecting among ladder rungs post hoc; reporting the word-level
secondary in place of the token-level primary; interpreting the human result
if the negative control fails.

## Materials

Natural Stories corpus text as tokenized by each model's own tokenizer;
locked word-level sample 8a6087341e is NOT the unit here (token-level), but
story identity and text are identical to it. Software: the project venv;
scripts to be committed alongside outputs, as with all prior preregistrations.
