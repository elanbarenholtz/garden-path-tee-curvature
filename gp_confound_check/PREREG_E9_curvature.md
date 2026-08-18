# Pre-registration — E9: trajectory curvature as the behavioral measure

Written 2026-08-14, after E8 (the reviewer-anticipating control that
disclosed the trigger result: on Natural Stories, curvature_3 predicts
reading time at dAIC 573.0 vs TEE's 78.4, 86.8% of participants, robust to
punctuation, surviving TEE jointly) and BEFORE any analysis below has been
run. E8's spec was fixed before its results were seen; everything here
extends the curvature measure through the rest of the program with specs
fixed now.

## Measure (fixed; identical to tee_vs_curvature/compute_curvature.py)

curvature_3: with h_i the layer-6 token states and ls the word's final
subword index, step(i) = h_i - h_{i-1}, angle(i) = arccos(cos(step(i),
step(i-1))); curvature_3 = mean(angle(ls-2), angle(ls-1), angle(ls)),
radians. Eligible where ls-3 >= 1 (no window touches token 0). Speech
corpora use the identical formula over each corpus's token states under the
project's chunked convention.

## Analyses and criteria (standing criterion: Wilcoxon p < .01 AND >= 65%
of clusters positive, cluster defined per corpus as in the TEE analyses)

A. NS distribution sufficiency (E7-analog): subject-level curvature effect
   with the four distribution functionals as covariates, and within the
   same quintile-matched cells (surprisal x entropy x top1). Criteria as E7.
B. SAP corpus replication: the published SAP specification with curvature
   in place of TEE. Criterion applied; the TEE precedent (61.1%) makes
   partial replication the expectation, reported either way.
C. Syntax control B2: within-constituent subset (close = 0, same parent),
   subject-level curvature effect, standing criterion (the wrap-up defense).
D. Production: Buckeye full corpus (cluster = talker, >= 200) and
   Switchboard (cluster = conversation side, >= 200), curvature of the
   launched word in place of TEE, identical controls (surprisal, four
   functionals, frequency, length, run position, cumulative position),
   identical demeaning and criteria. TEE co-entered as a secondary model.
E. (Registered, not run now) Content rank test with a curvature-based
   deviation; exploratory when run; the E5 verdict is expected to be
   measure-independent.

## Interpretation, fixed now

If A-D pass, the paper's headline behavioral measure becomes curvature --
the straightening literature's own quantity -- with TEE reported as a
related extrapolation measure capturing additional variance (its unique
contribution after curvature: 64.4%, just under criterion, p 7e-6, E8).
If curvature fails where TEE passed (notably production), the two measures
dissociate behaviorally and both are reported with that dissociation.
No result is dropped for framing reasons.

## Not permitted
Other windows, layers, angle weightings, or cluster redefinitions; dropping
either measure from any analysis it was registered for.
