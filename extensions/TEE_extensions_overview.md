# Trajectory geometry beyond the point: neighborhood-level TEE
### High-level summary for collaborators — Elan Barenholtz lab, July 2026

## Background

Our prior work (arXiv:2606.05346 and the TEE-vs-curvature follow-up) established that
**trajectory extrapolation error (TEE)** — how far a word throws the GPT-2 hidden-state
trajectory off its own linearly extrapolated path — predicts human reading time
independently of surprisal. TEE tracks syntactic structure (constituent closure), not
predictive uncertainty; its orthogonality to surprisal turned out to be a precise
cancellation between two geometric channels (along-heading and lateral). But the same
work delivered an apparent limit: the reorientation is a *local* event. Behaviorally it
reaches at most one word; causally (context-ablation inside the model) it also dies at
one word, while surprisal's causal wake persists 5+ words. Conclusion at the time:
long-range implications live in *information*, not *geometry*.

The question behind this new round: is that locality a fact about trajectory geometry,
or only about the **linear, point-level** version of it? Two generalizations were
tested: nonlinear extrapolators, and trajectories through a **coarser state space** —
movement between *neighborhoods* rather than points.

## Setup

Everything runs on the locked sample from the parent project (Natural Stories corpus,
GPT-2 small, layer 6, n = 9,840 words, hash-verified; recomputed states validated
against the locked measures before any new analysis). Conventions inherited
throughout: z-scored predictors, position + story fixed effects, cluster-robust SEs by
sentence, punctuation controlled with punct-free robustness passes (the corpus's
trailing-punctuation confound produced spurious effects repeatedly in the parent work;
all claims below are stated on punctuation-controlled or punct-free results).

The key new measure: **neighborhood TEE (ntee)**. Cluster the word-level hidden states
(k-means, k = 100), represent each word as its soft assignment over clusters (a point
on the simplex, Hellinger-embedded), and compute the same k = 3 linear extrapolation
error on *that* trajectory. Intuitively: fine TEE asks "did this word bend the path?";
ntee asks "did this word relocate the discourse to an unexpected region of state
space?"

## Findings

**1. Neighborhood geometry propagates — the locality result is scale-dependent.**
In the causal ablation paradigm (mask a word's attention keys, measure downstream
perturbation, now extended to 10 words), ntee predicts the size of the model's
downstream reorganization at *every* lag 1–10 (punct-free betas +0.12 to +0.19, all
p < 1e-4), controlling for surprisal, entropy, curvature, the fine TEE channels, word
length, and frequency. In the same regressions the parent result replicates exactly:
the fine lateral channel dies after one word; surprisal propagates. So geometry does
carry long-range influence — one level up. Crucially this survives a held-out control
(clusters fit on the other nine stories only) and a strict subset with no punctuation
anywhere in the downstream window. Entropy's own wake dies by lag 4, so this is not a
smuggled uncertainty effect.

**2. Neighborhood TEE is also a new human processing cost.** In reading-time models
that already contain surprisal and both fine TEE channels, ntee adds an on-word effect
(+0.004, p = 2e-10; held-out variant +0.0023, p = 2e-4). No behavioral spillover past
the word — but self-paced reading truncates spillover, so that side stays open.

**3. A layer-wise double dissociation.** Sweeping ntee across all 13 layers: the
*human* on-word cost tracks **shallow** neighborhood displacement (strongest at the
embedding layer, gone by layer 4), while the *model's* long-range wake tracks **deep**
displacement (rising to a peak at layer 9, +0.27, p = 1e-23, collapsing at 12).
Neighborhood relocation is two things: shallow relocation ≈ lexical-surface novelty,
paid immediately by readers; deep relocation ≈ contextual repositioning that reshapes
the model's processing for ten-plus words.

**4. The surprisal-orthogonality of TEE is a fine-scale phenomenon.** Word-grain TEE
keeps the parent signature (structure, not entropy). Every coarse variant re-couples
with uncertainty: the negative along-heading entropy channel that produces the
cancellation simply does not exist at the coarse grain.

**5. The cancellation has a geometric home.** Splitting the TEE residual against a
local PCA manifold of the recent trajectory: the within-manifold component carries the
structure signal (closure +0.10, entropy −0.13), the off-manifold component carries
uncertainty (entropy +0.30, surprisal +0.38). Structural reorientation is movement
*within* the locally explored subspace; uncertainty shows up as excursions *off* it.

**6. Allocentric beats egocentric for next-word cost.** A flow-field TEE (deviation
from the average next-step of the 50 nearest other-story states — what trajectories
*typically* do here, rather than what *this* trajectory was doing) out-competes
standard TEE on next-word reading time (10/10 stories), while preserving the low
entropy coupling. Nulls worth having: quadratic and locally-fitted-dynamics
extrapolators add nothing; hard cluster *switches* predict nothing — the soft
displacement is the operative variable.

**7. Deep neighborhood TEE tracks discourse events.** Against a blind event/topic
segmentation of the corpus, deep ntee (layer 9) distinguishes event-boundary
sentence-starts from ordinary sentence-starts (b = +0.37, p = 2e-3; AUC 0.59) where
surprisal (AUC 0.51, chance) and fine TEE (0.45) do not. And the long causal wake is
not merely "sentence/event restart geometry": it is unchanged by an event-boundary
control and persists at full strength when event-boundary words are excluded. ntee
indexes graded relocation of the discourse state; event boundaries are its high end.
(Annotations are AI-generated pending human norms — directional, not a large-margin
classifier.)

**8. Replication in GPT-2 medium and XL.** Medium (24 layers) reproduces small almost
exactly — structure-coupled fine TEE with RT value, ntee RT effect at every layer,
deep-peaked wake. XL (48 layers) shows the same signal *types* but relocates them to
the network's edges, hollowing out the middle. So the small↔XL laminar difference is a
depth effect, not a fluke; cross-model layer correspondence is an open methods
question, not an assumption. (A curvature-entropy sign discrepancy with King et al.
recurs across all three models — flagged, unresolved.)

## The picture

Three channels, three ranges. **Fine TEE**: local structural integration — syntactic,
uncertainty-cancelled, resolved within a word. **Neighborhood TEE**: semantic/topical
repositioning — uncertainty-coupled, costs readers on-word, causally reorganizes the
model's context for 10+ words (deep-layer component), and tracks human-annotated
discourse-event boundaries better than surprisal or fine TEE. **Surprisal**: lexical
prediction error with its own independent propagating wake.

The one-sentence version, which is the whole paper: **long-range context was not
absent from trajectory geometry; it was absent only from *point-level* trajectory
geometry.** Language understanding is not a single next-token prediction signal but a
trajectory through nested representational scales — at the finest scale words bend the
path and incur local structural-integration cost; at a coarser scale words relocate
the system into a new neighborhood of continuations, reshaping the future over many
words. Surprisal measures the probability of the next lexical item; neighborhood
geometry measures where the continuation has moved. Information and geometry do not
compete — they decompose across scale.

## Caveats

GPT-2 small only; Natural Stories + self-paced reading only; wake results from a
systematic subsample (n = 1,627); the "which mid layer carries the human cost"
question is specification-sensitive; k = 100 and the soft-assignment temperature were
not exhaustively tuned (30/100/300 behave consistently); all effects second-order to
lexical frequency.

## Next steps

Align high deep-layer-ntee words with human event/topic segmentation norms (the
strongest available bridge to discourse psychology); eye-tracking for the behavioral
long tail; GPT-2-XL replication (also resolves a standing curvature-entropy sign
discrepancy with King et al.); manuscript integration.

## Reproducibility

Repo `elanbarenholtz/garden-path-tee-curvature`, directory `extensions/`:
pre-registered design (RESEARCH_PROGRAM.md), full results (RESULTS_TEE_EXTENSIONS.md),
scripts x0–x8 (state validation → coarse TEE → RT → causal wake → nonlinear variants
→ manifold split → held-out control → layer sweep), computed measures as CSVs, raw
logs. Every script re-verifies the locked sample hash (8a6087341e) before producing a
table.
