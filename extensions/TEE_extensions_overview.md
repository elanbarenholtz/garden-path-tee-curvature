# Multiscale trajectory geometry in language models predicts human reading time and model-internal causal dynamics
### High-level summary for collaborators — Elan Barenholtz lab, July 2026

**Central claim (abstract sentence).** Fine-grained trajectory reorientation predicts
local reading-time costs, whereas deep neighborhood-level trajectory displacement
produces long-range causal effects in the model's future representations; however,
these deep geometric displacements do not map reliably onto human event-boundary
judgments. The contribution is a multiscale dissociation in model geometry and
reading-time prediction — not a theory of human event segmentation.

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

**7. The discourse-cognition interpretation did NOT survive human validation (a
decisive null).** A blind AI event-segmentation of Natural Stories had suggested deep
ntee tracks event boundaries (AUC 0.59 > surprisal/fine-TEE), but the pre-registered
external test — the Wang/Jafarpour/Sap (2022) HippoCorpus, 3,925 sentences with 8
human event-boundary labels each — is null: deep ntee does not predict human event
boundaries (AUC 0.49 = chance; held-out 0.50; graded null; exploratory sentence-scale
also null). So the "neighborhood relocation = discourse/event cognition" reading is
not supported and is dropped. The long causal wake remains — but it is a claim about
the model's internal representational dynamics, not about human discourse perception.

**8. Replication in GPT-2 medium and XL.** Medium (24 layers) reproduces small almost
exactly — structure-coupled fine TEE with RT value, ntee RT effect at every layer,
deep-peaked wake. XL (48 layers) shows the same signal *types* but relocates them to
the network's edges, hollowing out the middle. So the small↔XL laminar difference is a
depth effect, not a fluke; cross-model layer correspondence is an open methods
question, not an assumption. (A curvature-entropy sign discrepancy with King et al.
recurs across all three models — flagged, unresolved.)

## The picture

Three channels, three ranges. **Fine TEE**: local structural reorientation —
syntactic, uncertainty-cancelled, resolved within a word; costs reading time beyond
surprisal. **Neighborhood TEE = contextual state relocation**: uncertainty-coupled,
costs readers on-word beyond surprisal and fine TEE, and (deep-layer) causally
reorganizes the model's own context for 10+ words. **Surprisal**: lexical prediction
error with its own independent propagating wake.

Explicitly: although contextual relocation is compatible with discourse-level change,
an external human event-boundary validation did not support that interpretation. Thus
the present results establish a multiscale dissociation in model geometry and
reading-time prediction, not a theory of human event segmentation.

The one-sentence version, correctly scoped: **long-range context was not absent from
trajectory geometry; it was absent only from *point-level* trajectory geometry.**
Language modeling is not a single next-token signal but a trajectory through nested
representational scales — at the finest scale words bend the path and incur local
structural-integration cost (paid by human readers); at a coarser scale words relocate
the system into a new neighborhood of continuations, reshaping the model's future over
many words. Surprisal measures the probability of the next lexical item; neighborhood
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
