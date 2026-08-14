# Pre-registration — E7: Does processing cost exceed the current predictive
# distribution?

Written 2026-08-14, after E5's verdict (outcome 2, model-limited) and before
any analysis in this document has been run. No distribution functional beyond
surprisal has ever been entered into the paper's RT models on the locked
sample. Committed before first execution.

## The question, stated exactly

The paper's RT result shows processing cost is not exhausted by SURPRISAL.
Surprisal is one scalar extracted from the current next-token distribution
P_t. Two hypotheses survive that result:

  H-dist    readers are current-distribution processors with a cost function
            richer than surprisal — cost = f(P_t, w) for some f — and TEE
            proxies distribution shape (entropy, confidence, concentration).
  H-hist    cost depends on the recent representational trajectory beyond any
            functional of the current distribution.

TEE is a relation between the incoming word and the fitted heading of the
preceding three states; it is not naturally a functional of (P_t, w). If its
RT effect survives controlling for and matching on distribution shape, H-dist
is rejected in favor of H-hist — the comprehension-side history claim, immune
to E5's deflationary reading because it concerns processing cost, not text
statistics. If TEE dies under distribution controls, the paper's measure is
reinterpreted as a distribution-shape proxy and the manuscript must say so.

## Data and fixed inputs

Natural Stories locked sample 8a6087341e (hash asserted); repaired-frequency
headline RT specification, unchanged: log RT ~ z(word_length) + z(zipf freq)
+ z(zone) + z(prev log RT) + z(surprisal) [+ z(TEE)], mixed model with
participant intercepts pooled, plus the subject-level standing criterion
(group Wilcoxon p < .01 AND >= 65% of participants with positive TEE sign;
>= 100 usable observations per participant). RT window 100-3000 ms.

## Distribution functionals (fixed now)

Computed from GPT-2 Small (the paper's model) under the project's chunked
context convention, from the logits row that predicts the word's FIRST
subword — the distribution in force at the moment the word begins:

  entropy      H(P_t) = -sum p log p
  renyi2       -log sum p^2   (collision entropy; concentration)
  top1         log max(P_t)   (confidence)
  top10        log of the summed probability of the 10 most probable tokens

All z-scored. The full correlation matrix among TEE, surprisal, and the four
functionals is reported descriptively before any model. If |r(TEE, x)| > .9
for any functional, that collinearity is reported and the model still run.

## Part A — covariate control

Add the four functionals to the headline model. Report TEE's pooled beta, p,
dAIC, and the subject-level criterion (per-participant OLS with the same
covariates).

CRITERION A: the standing subject-level criterion (p < .01 and >= 65%) holds
with all four functionals in the model.

## Part B — distribution matching (the stringent test)

Cells = quintile(surprisal) x quintile(entropy) x quintile(top1), quintiles
computed on the pooled analysis sample (125 cells). Within-cell demeaning of
log RT, TEE, and the remaining nuisance covariates (word length, zipf freq,
zone, prev log RT), pooled; then per-participant OLS of demeaned RT on
demeaned TEE + demeaned nuisance covariates. Within a cell, distribution
shape is (coarsely) held fixed; TEE variation within cells is the
history-specific variation.

CRITERION B: standing subject-level criterion on the within-cell TEE effect.

Power guard, fixed now: if the median within-participant count of usable
demeaned observations falls below 100, Part B is reported as descriptive
(underpowered), and the claim rests on Part A with the matching caveat.

## Secondary (only if Criterion A passes)

Same Part A on the SAP corpus (locked sample e9fd2c547a, its published
specification with corpus-appropriate nuisance controls), functionals from
the same convention. Reported as replication; no gate.

## Outcome logic (fixed now)

1. A and B pass -> "Reading cost tracks the recent representational
   trajectory beyond the current predictive distribution." The history claim,
   comprehension-side, goes to v2/Cognition as a defended claim; framing
   decided then, not now.
2. A passes, B fails (not merely underpowered) -> TEE survives smooth
   distribution covariates but not matching; claim limited to "beyond
   surprisal, entropy, and confidence"; the H-dist/H-hist question is
   reported as open.
3. A fails -> the TEE-RT effect is reducible to distribution shape. Major
   reinterpretation: the measure is reported as a distribution-shape proxy,
   and the manuscript's "beyond surprisal" claim is qualified accordingly.
   Which functional absorbs the effect is reported.
4. A passes, B underpowered -> claim rests on A; B descriptive.

## Not permitted

Alternative functional sets, other quantile resolutions, other layers or
models for the functionals, per-participant cell redefinition, or dropping
collinear covariates to rescue a criterion. Anything further is exploratory
and labelled as such.

---

## RESULTS (2026-08-14) — OUTCOME 1: A and B both pass

Provenance: computed entropy matches the locked sample's entropy column at
r = 1.0000 (bits); the headline dAIC reproduces at exactly 78.4.

**The decisive descriptive fact, visible before any model:** TEE is nearly
orthogonal to distribution shape. r(TEE, entropy) = .043, renyi2 .062,
top1 -.068, top10 -.059 (the functionals correlate .89-.98 among themselves,
as they should). TEE shares variance with surprisal (.31) but almost none
with how concentrated or confident the distribution is.

**Part A — PASS.** Adding all four functionals leaves TEE untouched:
dAIC 78.4 -> 79.4, beta +0.00298 -> +0.00307, p 1.8e-19. Subject-level:
67.8% positive without functionals; **74.7%** positive with them
(n = 174, Wilcoxon p = 1.3e-11). The effect strengthens slightly, consistent
with the functionals absorbing nuisance variance rather than TEE variance.
(n_subj here is 174 vs the published 171: the functional merge changes row
availability marginally; within-run comparisons are like-for-like.)

**Part B — PASS, fully powered.** 91 matched cells, median 4,853 usable
observations per participant (power guard cleared by 48x). Within
distribution-matched cells: mean beta +0.00418, **74.7% positive**,
Wilcoxon p = 7.9e-14.

**Conclusion (preregistered outcome 1).** Reading cost tracks the recent
representational trajectory beyond the current predictive distribution:
holding the distribution's surprisal, entropy, and confidence (coarsely)
fixed, words that depart from the fitted heading of the preceding states are
read more slowly, in three quarters of participants. Together with E5
(production content is distribution-sufficient under a strong model), the
day's picture: history lives in the COMPREHENSION mechanism, not in text
content. H-dist is rejected on this corpus for this model's functionals.

Limits, stated plainly: functionals are GPT-2 Small's (prereg-fixed);
matching is quintile-coarse (the near-zero raw correlations make residual
confounding through distribution shape an unlikely rescue for H-dist);
stronger-model functionals are a legitimate exploratory follow-up and are
labelled as such if run.
