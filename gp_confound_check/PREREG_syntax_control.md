# Pre-registration: is trajectory structure reducible to constituent structure?

Written 2026-08-14, before any analysis in this document is run. The RT-side
models reuse the repaired-frequency headline specification, which is fixed and
published; no analysis relating syntactic variables to alignment or to the
trajectory measure has been run on this corpus at the time of writing.

## The objection this answers

The manuscript's framing claims language carries a short-range historical
dependency ("momentum") in its representational sequence, attributes it to
incremental production, and shows readers are sensitive to departures from it.
A leaner account: this is constituent structure in geometric disguise. Words
within a phrase are related, so their states move coherently; phrase boundaries
turn the trajectory; TEE is a graded boundary signal; and its reading-time
effect is syntactic wrap-up, known since Just & Carpenter. On that account
there is no momentum, no dynamics, and no trace of production — only grammar.

The right question is NOT whether syntax affects the trajectory (it should; a
dynamical system may turn at boundaries and still have momentum). The question
is QUANTITATIVE: how much of the observed structure does syntax absorb, and
does anything behaviourally relevant remain after it has taken its share?

## Data

Natural Stories locked sample 8a6087341e (hash asserted). Syntactic variables
from the corpus's Penn parses (`naturalstories/parses/penn/`), aligned to
sample words by story and token index. Alignment will be validated by checking
that parse terminals match sample word forms on >= 99% of words; mismatched
words are excluded and the exclusion count reported.

Per word-transition (w_{t-1} -> w_t) syntactic variables:
  close_t   brackets closed after w_{t-1} (already on the sample: closure_depth)
  open_t    brackets opened before w_t (extracted from parses)
  same_parent  1 if w_{t-1}, w_t share the immediately dominating constituent
  lca_dist  depth from w_t to the lowest common ancestor with w_{t-1}

## Part A — geometry

A1 (descriptive figure): mean directional alignment (cos between successive
steps, the paper's direction-preservation quantity) as a function of
lca_dist = 0, 1, 2, 3+, each against the random baseline (0.029). Reported
regardless of outcome.

A2 (the quantitative test): regress per-transition alignment on the full
syntactic transition class (close_t, open_t, same_parent, lca_dist, entered
jointly, plus sentence position controls). Report:
  - R^2_syntax: variance in alignment absorbed by syntax
  - residual mean alignment by transition class, against baseline
  - the pre-specified statistic: RESIDUAL alignment for deep transitions
    (lca_dist >= 3), i.e. is the trajectory still directed, above baseline,
    where syntax says it should have fully turned?

A3 (measure-level): same regression with TEE as outcome. Reports how much of
TEE's variance is syntactic transition structure. No criterion attached;
descriptive.

## Part B — reading time (the decisive part)

B1: add close_t, open_t, same_parent, lca_dist, and their interactions with
log position to the repaired-frequency headline model. Report TEE's beta and
dAIC before/after. Acknowledged in advance: collinearity among TEE, position
and syntax makes coefficient survival here suggestive, not decisive.

B2 (decisive): restrict to WITHIN-CONSTITUENT positions (close_t = 0 AND
same_parent = 1 — no wrap-up event at all) and refit the headline model,
subject-level. If TEE predicts RT here, wrap-up cannot be the story, because
nothing is wrapping.

B3 (symmetry check): same on the boundary-only complement. Expected larger if
syntax contributes; reported either way.

## Criteria, fixed now

Part A supports non-reducibility iff residual alignment at lca_dist >= 3
exceeds 3x the random baseline (i.e. >= 0.09) after the A2 regression.
[3x is a judgment call made now, before seeing data: comfortably above
baseline noise, far below the within-constituent 0.44.]

Part B supports non-reducibility iff, in the within-constituent subset (B2),
TEE's subject-level effect satisfies the paper's standing criterion:
group Wilcoxon p < .01 and >= 65% of participants sharing the positive sign.
The subset will be smaller, so the criterion is harder; that is accepted
rather than adjusted.

## Outcome logic (claims, not p-values)

1. A and B both pass  ->  "Constituent structure organizes the trajectory but
   does not exhaust it." The momentum framing and the trajectory-vs-point
   sentence go into the Cognition submission as defended claims.
2. A fails, B passes  ->  geometry is largely syntactic, but the behavioural
   effect is richer than wrap-up. Production-side interpretation is narrowed;
   the RT claim stands as "readers track a graded signal beyond the
   boundary/no-boundary distinction."
3. A passes, B fails  ->  language carries super-syntactic directional
   structure but readers' sensitivity to it is not demonstrable within
   constituents. The behavioural framing retreats to the pooled result.
4. Both fail  ->  TEE is a graded syntactic-boundary signal. The dynamical
   interpretation is dropped from the paper, and the measure is reported as
   what it is. This outcome is also worth knowing before a reviewer finds it.

## Known asymmetry, stated in advance

Automatic parses of naturalistic text are noisy. Parse errors blur transition
classes and therefore work AGAINST the syntactic account in A (they flatten
the syntax regression) but also inflate the within-constituent subset in B
with mislabelled boundary words (which works AGAINST TEE surviving there,
since boundary RT variance lands in the "no boundary" cell as noise). Neither
direction is clean; both are noted rather than corrected post hoc.

## Not permitted

Alternative alignment statistics, other layers or window sizes, other
syntactic codings, or subsetting beyond what is specified, in order to move
either criterion. Anything further is exploratory and labelled as such.

---

## RESULTS (2026-08-14) — including one reported deviation

**Deviation.** The prereg described Part A's quantity as "cos between
successive steps, the paper's direction-preservation quantity". Those are two
different quantities and the description was internally inconsistent. The
first run used raw successive-step cosine, which is approximately −0.40 in
every transition class: successive steps share an anti-correlated noise
component, so the raw quantity is noise-dominated and cannot bear on the
criterion, whose 0.029 baseline belongs to the fitted-direction |cos|.
Part A was rerun with the paper's actual quantity (v2_table4_dirpres
convention), which reproduces Table 4's published value exactly (0.4359 vs
0.436). Both runs are preserved (`syntax_control_out.txt`,
`syntax_control_A2.py`). The raw-step anti-persistence is a real property of
the states, recorded in GEOMETRY_PAPER_NOTES.md.

**Part A (corrected quantity): PASS.**
Direction preservation by lca_dist: 0 → .424, 1 → .445, 2 → .428,
3+ → **.451** (n = 277), all ≈ 15x baseline. The profile is FLAT: deep
boundary crossings are as directionally preserved as within-constituent
transitions. Syntax absorbs 3.1% of alignment variance (R² .0066 → .0380).
Criterion (≥ .09 at lca ≥ 3): passed at .451.

**Part B: PASS.**
B2 (within-constituent, close = 0 and same parent; 65,315 rows, 161
participants): β = +0.0496, **79.5% positive**, Wilcoxon p = 2.5e−18.
Standing criterion passed. B3 (boundary complement): β = +0.0076, 61.0%.
B1 (pooled): TEE survives syntax covariates (ΔAIC 78.4 → 116.2; the increase
is not interpreted, per the weaker-control lesson).

**Outcome 1: constituent structure organizes the trajectory but does not
exhaust it.** Stronger than anticipated on both sides: syntax explains almost
none of the directional coherence, and the reading-time effect is *stronger*
within constituents than at boundaries — the inversion of what a wrap-up
account predicts.

**Exploratory follow-ups permitted but not run:** signed (non-absolute)
fitted-direction cosine by class; A3 showed syntax absorbs 8.7% of TEE
variance (close_t being the largest piece), consistent with the composite
measure carrying some boundary signal while the RT effect does not depend
on it.
