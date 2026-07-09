# TEE Extensions: nonlinear trajectories and neighborhood-level dynamics

> **Manuscript framing (post-external-validation).**
> Working title: *Multiscale trajectory geometry in language models predicts human
> reading time and model-internal causal dynamics.*
> Central abstract sentence: *Fine-grained trajectory reorientation predicts local
> reading-time costs, whereas deep neighborhood-level trajectory displacement produces
> long-range causal effects in the model's future representations; however, these deep
> geometric displacements do not map reliably onto human event-boundary judgments.*
> Terminology: neighborhood TEE = **contextual state relocation** (a model-geometric
> term), NOT "semantic/topical repositioning" (a discourse-cognition claim we tested
> and could not support). The HippoCorpus human event-boundary null (Addendum 6) is a
> **boundary condition to report in Results/Discussion as a deliberately performed
> external validation** — not a buried caveat. Suggested sentence: "To test whether
> deep neighborhood relocation corresponds to human event segmentation, we applied the
> same pipeline to an independently annotated human event-boundary corpus; the result
> was decisively null." Targets: Cognitive Science or TACL primary.

Locked sample 8a6087341e (n = 9,840), GPT-2 small layer 6, Natural Stories.
All analyses inherit the parent conventions: z-scored predictors (ddof=0), position +
story fixed effects, cluster-robust SEs by sent_uid, hash re-verified before every
table, punctuation controlled with punct-free robustness reported. Every claim below
is stated on the punctuation-controlled or punct-free result.

**Validation gate.** Layer-6 states recomputed on this machine (M5, torch 2.10):
0/9,840 final_bpe mismatches; recomputed tee_k3 matches locked to max relative error
1.0e-06, r = 0.9999999999991. (Not the parent's 1.4e-14: cross-machine float32 GEMM
variation, not a pipeline difference.)

## The question

The parent project concluded the trajectory reorientation is a LOCAL event (≤1 word
behavioral spillover, ≤1 word causal wake) while long-range implications live in
information (surprisal, 5+ word wake). Is that locality a fact about trajectory
geometry, or about the linear, point-level version of it?

## Headline findings

**1. Neighborhood-level geometry propagates. The range dissociation is
scale-dependent, not fundamental.**
ntee_k100 — TEE computed on the trajectory through k-means neighborhood space
(soft-assignment / Hellinger embedding, k = 100) — has a causal ablation wake that is
significant at EVERY lag 1–10 (punct-free betas +0.12 to +0.18, all p < 1e-4),
controlling for surprisal, entropy, curvature, tee3_perp/par, word length, and
frequency. In the same regressions the parent result replicates exactly: perp's wake
dies after +1, par has none, surprisal propagates. Entropy's own wake dies by +4, so
the ntee wake is not a smuggled uncertainty effect. It holds whether the downstream
perturbation is measured on the fine state, the trailing-mean neighborhood state, or
the cluster assignment; it survives the strictest subset with no punct-final word in
w+1..w+5 (L5: +0.145, p = 2e-3, n = 701); per-story betas are positive 8/10.
Interpretation: when a word relocates the trajectory to an unexpected *neighborhood*
(as opposed to bending its local heading), the model's downstream representations are
reshaped for at least ten words — a geometry channel with surprisal-like range,
independent of surprisal.

**2. Neighborhood TEE is also a new on-word behavioral cost.**
In the RT spillover model with fine TEE channels AND surprisal present, ntee_k100
predicts on-word RT: +0.0042 (p = 2e-10); punct-free +0.0039 (p = 6e-9); per-story
7/10 positive. No positive spillover at L1–L3 (self-paced reading truncation caveat
applies). Smoothed coarse TEE (trailing means m = 3/5/10) predicts nothing — the
neighborhood (cluster) construction, not smoothing, is what matters.

**3. The entropy cancellation is specific to the fine grain.**
Word-grain TEE preserves the parent signature (closure +0.144, entropy +0.016 n.s.,
punct-free). Every coarse variant re-couples with uncertainty (entropy +0.14 to +0.19).
At the coarse grain both par and perp load POSITIVELY on entropy (+0.085/+0.147) —
the negative along-heading entropy channel that produces the cancellation exists only
at the fine scale. TEE's orthogonality to surprisal is a fine-scale balance point,
not a property of trajectory geometry per se.

**4. Allocentric (flow-field) TEE beats egocentric TEE on next-word reading time.**
ftee_n50 = deviation from the mean next-step of the 50 nearest other-story corpus
states (what trajectories TYPICALLY do here), vs TEE's deviation from the word's own
recent heading. In direct competition: ftee_L1 +0.0051 (p = 5e-9) while tee_k3_L1
drops to n.s.; on-word both survive. Per-story 10/10 positive. ftee keeps a low
entropy coupling (+0.036), so the orthogonality-to-uncertainty property survives the
allocentric move. The ego–allo prediction gap (fgap) is itself an entropy tracker
(+0.22): where the word's own heading disagrees with typical corpus flow, the model
is uncertain.

**5. The cancellation has a geometric home: on- vs off-manifold.**
Splitting the k=3 TEE residual by a local PCA manifold (d = 10 over the 20 preceding
states): the within-manifold component carries structure (closure +0.100, entropy
−0.131), the off-manifold component carries uncertainty (entropy +0.299, surprisal
+0.377) — punct-free. Both cost reading time on-word; the in-manifold component also
carries to L1 (+0.0042, p = 1e-13). Structural reorientation is movement WITHIN the
locally explored subspace; uncertainty shows up as excursions OFF it.

**6. Nulls worth having.** Quadratic TEE (r = .88 with tee_k3) adds nothing to RT;
acceleration-awareness is not the missing ingredient. Local-LDS TEE is weakly coupled
and behaviorally inert. Meta-TEE (heading-of-heading) is an entropy-negative tee_k3
correlate with a marginal L1 RT effect. Cluster hard-switch (nswitch) predicts
nothing robustly — the SOFT neighborhood displacement, not the categorical switch,
is the operative variable.

## Synthesis

The parent paper's "ship turning" is real but local — at the point level. These
results add a second geometry channel one level up: words that relocate the
trajectory across neighborhoods produce (a) an on-word processing cost humans pay
beyond surprisal and fine TEE, and (b) a causal reorganization of the model's context
that persists 10+ words — the long-range influence the parent project found missing
from geometry. The two-channel picture becomes three-scale: fine TEE = local
structural reorientation (closure; cancellation; ≤1 word), neighborhood TEE =
contextual state relocation (uncertainty-coupled; 10+ word model-internal wake;
on-word cost), surprisal = lexical prediction error (its own propagating wake). And
the fine channel itself decomposes geometrically: structure in-manifold, uncertainty
off-manifold. (NB: "contextual state relocation" is deliberately a model-geometric
description, not a discourse-cognition one — an external human event-boundary test,
Addendum 6, was null and bounds the interpretation.)

## Caveats

GPT-2 small, layer 6, Natural Stories, self-paced reading throughout. k-means fit on
all stories including the target story (mild leakage; the flow-field measure excluded
same-story neighbors and behaves consistently, but a held-out-story clustering rerun
is cheap and should be done). Wake is the STEP=6 subsample (n = 1,627), relative-L2,
CTX = 256, MAXL = 10. Punctuation clusters exist (several k=100 clusters are 100%
punct-anchored); all claims punct-free-verified. Behavioral locality remains bounded
by the self-paced method. Effects are second-order to lexical frequency.

## Next steps

Held-out-story clustering for ntee (leakage control). Layer sweep (does the ntee wake
peak where the parent's structure signal peaks?). k-sensitivity beyond {30,100,300}
and soft-assignment temperature. Do high-ntee words align with human event/topic
boundaries (event segmentation norms)? Eye-tracking Natural Stories for the long
behavioral tail. GPT-2-XL replication (also resolves the curvature-entropy sign).
Manuscript: fold in the scale-dependence of the range dissociation as the answer to
"where did the long-range implications go" — they were in the neighborhood
trajectory all along.

## Addendum (same session): held-out clustering + layer sweep

**Held-out control (x7).** Refitting k=100 per story on the OTHER nine stories only
(story-independent neighborhoods, training-set sigma): the long wake survives at every
lag punct-free with entropy/curvature/surprisal/perp/par controls — L1 +0.186
(p=8e-12), L5 +0.115 (p=2e-5), L10 +0.093 (p=9e-4); entropy's wake dies by L5. The
on-word RT effect holds attenuated (+0.0023, p=2e-4; a small negative L1 term
appears). The leakage caveat is closed: the headline wake result is not an artifact
of clustering on the target story.

**Layer sweep (x8).** ntee (k=100, per layer) predicting the layer-6 wake at L5 and
on-word RT, punct-free:

| layer | closure | entropy | RT beta (p) | wake5 beta (p) |
|---|---|---|---|---|
| 0 (emb) | +.024 | +.094 | **+.0079 (2e-35)** | +.097 (6e-5) |
| 1 | +.058 | +.117 | +.0045 (6e-15) | +.083 |
| 2 | +.046 | +.159 | +.0037 (5e-10) | +.082 |
| 3 | +.042 | +.163 | +.0025 (3e-5) | +.088 |
| 4–6 | ~+.05 | ~+.17 | n.s. | +.07–.12 |
| 7 | +.068 | +.181 | +.0023 (1e-4) | +.181 (7e-12) |
| 8 | +.037 | +.122 | n.s. | +.211 (7e-17) |
| **9** | −.000 | +.097 | n.s. | **+.271 (1e-23)** |
| 10 | +.016 | +.015 | −.0018 | +.237 (4e-20) |
| 11 | +.013 | −.023 | −.0014 | +.214 (1e-16) |
| 12 | −.028 | −.249 | n.s. | +.042 n.s. |

Two gradients, doubly dissociated: the HUMAN on-word cost tracks SHALLOW neighborhood
displacement (monotone decline from the embedding layer, gone by layer 4), while the
MODEL's long-range reorganization tracks DEEP displacement (rising to layer 9, then
collapsing at 12). Neighborhood relocation is not one thing: shallow relocation is
lexical-surface novelty humans pay for immediately; deep relocation (layers 7–11) is
the contextual repositioning that reshapes the model's downstream processing for 10+
words. Sensitivity note: the layer-6 on-word RT effect depends on specification
(present in the x2 full battery, +0.0039, and the held-out variant, +0.0023; null in
the minimal x8 spec with a global-sigma refit), so treat "which mid layer carries the
human cost" as open; the shallow-RT and deep-wake gradients are the robust patterns.

## Addendum 2: pre-submission package (robustness table, discourse validation, GPT-2 XL)

**Locked robustness table** (results/ROBUSTNESS_TABLE.md). Both headline claims
stable across every pre-specified variant. ntee wake at L1/L5/L10: punct-controlled,
punct-free, held-out clustering, k=30, k=300, and no-downstream-punct — all
significant. ntee on-word RT: all variants significant (~+0.002); documented nulls:
ctee_m5, nswitch (negative), curvature, and fine channels at L5 wake.

**Discourse validation (x11).** Deep ntee (layer 9) is a strong discourse-transition
detector: sentence-boundary logistic b = +1.87 (p = 1e-140) vs surprisal +0.90 and
fine TEE −0.95; top ntee decile is 32% sentence-initial vs 0.1% for the bottom
decile. Nuance: explicit connectives (but/however/then) are LOW-ntee — they signal
transitions lexically while being generic trajectory states; and among
sentence-initial words, larger model-internal semantic shift predicts *lower* ntee —
external event-segmentation norms are needed for a clean test. Critically, the long
wake is NOT a sentence-boundary artifact: sent_initial itself has no wake, ntee's
betas are unchanged with the boundary control, and the wake persists when
sentence-initial targets are excluded entirely (L5 +0.089, p = .02).

**GPT-2 XL replication (x9a–e; n = 9,840, same locked sample; XL-native surprisal/
entropy, definitions validated to r = 1.000 against the locked columns on gpt2).**
The honest verdict is: the signals replicate, but their laminar home moves to the
network's edges, and the middle of XL behaves differently.

- Fine-TEE signature by layer (punct-free): closure coupling and positive RT exist
  at the EMBEDDING layer (closure +0.150, RT +0.0076, p = 1e-33) and at the FINAL
  layer 48 (closure +0.132, RT +0.0037, p = 2e-9, entropy-quiet +0.03) — but are
  absent through XL's middle (layers 8–32: closure ~0, RT null/negative). The
  small-model "mid-layer" locus does not transfer by depth fraction.
- ntee long wake: at XL's mid layer the conditional wake is null-to-negative; the
  positive long-wake predictor is the FINAL layer (slot 48: +0.163, p = 3e-5 at L5)
  and weakly the embeddings. Directionally consistent with small ("late layers carry
  the propagating displacement"), but in XL, ENTROPY also carries a robust wake at
  all lags (+0.12–0.20) — in the bigger model, uncertainty itself propagates.
- King sign check: curvature×entropy on XL mid-layer is −0.026 (weakly negative;
  King reported +0.15), and curvature carries closure (+0.086) on XL — the
  curvature-entropy coupling still does not reproduce on our pipeline; unresolved.

Reading: GPT-2 small's 12 layers compress lexical→contextual→predictive processing
so the trajectory signals concentrate mid-network; XL's 48 layers stretch that
pipeline, leaving a long signature-free middle and pushing the behaviorally and
causally potent geometry to the input and output ends. For the paper: report XL as a
replication of the *existence* of both signals (fine structure-coupled TEE with RT
value; late-layer neighborhood displacement with long causal wake) plus a
model-dependence of the laminar locus — and treat cross-model layer correspondence
as an open methods question, not an assumption.

## Addendum 3: event-segmentation validation (the interpretation test)

Sentence boundary is a crude proxy; the claim is that deep ntee indexes *event/
topic relocation*, not sentence restarts. Test: a coarse event/topic segmentation of
all 472 sentences (LLM annotation following Michelmann et al. 2023, blind to
per-sentence ntee; 152 boundaries, 32%) — a stand-in for human norms, which don't
exist for this corpus. The discriminating design holds the sentence-restart confound
constant by testing **only among sentence-initial words**: which sentence-starts are
*event* boundaries, and does deep ntee (layer 9) know?

**Result — deep ntee predicts event boundaries better than surprisal and fine TEE.**
Among sentence-initial words (n = 427, punct-free, first-sentence-of-story dropped),
predicting event-boundary status: ntee_l9 b = +0.374 (p = 2e-3), while surprisal
(p = 0.40), fine TEE (p = 0.51), and entropy (p = 0.06) do not discriminate.
Single-predictor AUC: ntee 0.589 vs surprisal 0.507 (chance) vs fine TEE 0.450. The
effect is modest in absolute terms but it is the *only* measure that separates event
boundaries from ordinary sentence starts, and it beats both competitors the reviewer
named.

**The long wake is not "event-restart geometry."** Adding event-boundary status to
the wake regression leaves ntee's betas unchanged at every lag (L1 +0.182 → +0.182;
L10 +0.124), and event_bnd carries no wake of its own (all p > 0.4). Excluding
event-boundary target words entirely, the wake persists at full strength (L10 +0.137,
p = 4e-4). So the propagating displacement is a graded, continuous property of
neighborhood relocation — event boundaries are its high end, not its cause.

Caveat: annotations are AI-generated (single annotator = this model), pre-registered
as blind but pending human event-segmentation norms; AUC is modest; the clean claim is
directional superiority over surprisal/fine-TEE plus wake-survival, not a large-margin
classifier.

## Addendum 4: leakage-safe deep ntee, blind audit, pre-registration

**The long wake is a DEEP-layer, story-independent phenomenon (x13).** Recomputing
deep ntee at layer 9 with per-story held-out clustering (`ntee_l9_ho`) and racing it
against the original layer-6 `ntee_k100` in the wake regression: the deep held-out
measure dominates completely — L1 +0.352 (p = 3e-27), L5 +0.255 (p = 1e-13), L10
+0.184 (p = 1e-8) — while layer-6 ntee_k100 falls to ~0 (all p > 0.2). The earlier
layer-6 result was a weaker proxy for a deep-layer, leakage-safe signal. This is the
strongest and cleanest version of the central result: **words that relocate the deep
neighborhood causally reshape the model's next ten words, robustly and
story-independently.**

**Event-boundary discrimination replicates held-out but is a weak diffuse gradient
(x13).** With `ntee_l9_ho`, among sentence-initial words it still beats the
competitors at predicting event boundaries (b = +0.36, p = 2e-3; AUC 0.579 vs
surprisal 0.507, fine TEE 0.450; entropy also discriminates, b = +0.34). BUT the
pre-committed blind top/bottom-30 audit is a genuine tempering result: the top-30 and
bottom-30 deep-ntee sentence-starts have IDENTICAL event-boundary rates (0.30 vs 0.30)
and the top sentences do not obviously read as topic/scene shifts. So the
discourse-boundary link is real in aggregate but diffuse — a graded correlation, not a
sharp detector. The paper should state it exactly that way and lean on the wake result
for the strong claim.

**Pre-registration + human-annotation kit.** The final analysis specification is
frozen in `PREREGISTRATION.md` (measures, covariate set, confirmatory tests,
exclusions, model family). A ready-to-run human event-segmentation kit is in
`human_annotation_kit/` (per-sentence sheet, standard Zacks-style instructions) with
`analyze_human_boundaries.py`, which builds graded boundary-agreement and re-runs the
confirmatory deep-ntee test against human consensus — a one-step add once norms are
collected. No public human event norms exist for Natural Stories (searched); the
current annotation is single-annotator AI, and human collection is the top pre-draft
recommendation.

## Addendum 5: GPT-2 medium — the discrepancy is depth, not a fluke

GPT-2 medium (24 layers) replicates GPT-2 small almost point-for-point, and is the
cleaner of the two larger-model checks:

- Fine TEE (mid layer): closure +0.197 (p = 3e-76), entropy +0.06, RT +0.0048
  (p = 8e-16) — the small-model structure-coupled, RT-positive signature.
- ntee: on-word RT +0.0040 (p = 9e-11), positive at essentially every layer (unlike
  XL's dead middle).
- ntee wake: significant at nearly every lag to L10 (+0.08 to +0.17), and the
  wake-by-layer sweep rises to a DEEP peak (slot 9: +0.197, p = 1e-7) — the same
  shallow-RT / deep-wake gradient found in small.
- King curvature×entropy sign: −0.15 (again negative, opposite King's +0.15) — now
  consistent across small, medium, AND XL, so the sign discrepancy is a robust
  property of our GPT-2 pipeline, not model-specific noise.

Three-model picture: the signals exist in all of small/medium/XL. Medium (24L) still
concentrates them mid-to-deep like small (12L); only XL (48L) stretches the pipeline
enough to hollow out the middle and push the potent geometry to the input/output
edges. The small↔XL laminar discrepancy is therefore a depth effect, not a fluke —
exactly the "one more medium model" check the reviewer asked for, and it resolves
which way to read the XL result.

## Addendum 6: EXTERNAL HUMAN VALIDATION — a decisive null that reshapes the claims

The interpretation "deep ntee indexes relocation of the discourse/event state" needed
real human event labels, not our AI annotation. We ran it on the Wang, Jafarpour & Sap
(2022) corpus: 240 HippoCorpus diary stories, 3,925 sentences, each labeled by 8
crowdworkers as no-event / expected / surprising event boundary. GPT-2 small, same
pipeline; deep ntee (layer 9) at the sentence-initial word (the transition into the
sentence), against human boundary status, controlling surprisal, entropy, fine TEE,
sentence length; cluster-robust by story.

**Result: null.** Deep ntee does not predict human event boundaries (b = −0.02,
p = 0.65; AUC 0.493 = chance). Held-out (leave-half-out) clustering: same (AUC 0.495).
Graded boundary-agreement: null. If anything, deep ntee is *negatively* related to
"surprising" boundaries (b = −0.05, p = 0.008). The only model quantities that track
human boundaries are entropy (b = +0.18) and sentence length. An exploratory
sentence-SCALE neighborhood measure (trajectory through sentence-centroid clusters)
was also null (AUC 0.488) and a sentence-to-sentence cosine-shift ran backwards
(AUC 0.432). The negative result is robust across scale, clustering, and grading.

**What this does to the paper.** The discourse/event-cognition interpretation is NOT
externally supported and must be dropped, not just softened. The weak Natural-Stories
AI-annotation result (AUC 0.58) does not replicate against human labels on an
independent corpus — consistent with the blind top-word audit (Addendum 4), which had
already shown the extremes don't separate. The reviewer's instinct to demand human
norms was correct and it changed the conclusion.

**What still stands (and is now cleanly bounded):**
1. Fine TEE predicts reading time beyond surprisal (parent, replicated).
2. Neighborhood TEE predicts on-word reading time beyond surprisal AND fine TEE
   (robust, replicated in GPT-2 medium).
3. Deep neighborhood TEE has a long (10+ word) causal wake INSIDE the model —
   leakage-safe, deep-layer, replicated in medium. This is a claim about the model's
   representational dynamics, not about human discourse cognition.
4. Shallow→RT / deep→wake layer dissociation.
5. Core conceptual claim survives, correctly scoped: information (surprisal) and
   geometry (TEE) decompose across scale, and long-range structure lives in
   neighborhood — not point — geometry. This is a statement about the model plus human
   *reading-time* cost; the bridge to human *event-segmentation* cognition is not
   supported by current data and is left as an open question.

The honest paper is stronger for this: the model-internal multiscale-geometry result
is solid and now has a firm boundary drawn around it by a pre-registered external test.

## Addendum 7: nonlinear × neighborhood — completing the 2×2

The original hunch had two axes: nonlinear extrapolation AND higher-order (neighborhood)
space. We ran them separately; this fills the missing joint cell — nonlinear
extrapolation IN neighborhood space, at deep layer 9, held-out clustering. Measures on
the sqrt-soft k=100 assignment trajectory: linear k=3 (lntee9), quadratic k=5 /
acceleration (qntee9, r=0.86 with lntee9), and neighborhood-space curvature (nbcurv9).

The 2×2 now reads:
- **linear × point** = classic TEE (parent).
- **nonlinear × point** = null for RT (x4: quadratic tracks TEE at r=.88, adds nothing;
  LDS inert).
- **linear × neighborhood** = the ntee results (RT + the 10-word causal wake).
- **nonlinear × neighborhood** = a genuine dissociation, below.

**Wake is purely linear.** With lntee9, qntee9, nbcurv9 competing, lntee9 dominates the
causal wake at every lag (L1 +0.342 p=3e-13 → L10 +0.177 p=9e-5); qntee9 adds NOTHING
(all n.s.). The model-internal long-range signal is a linear-trend phenomenon in
neighborhood space; acceleration does not help. (nbcurv9 carries a small, distinct
early-lag wake, L1–L5, gone by L10.)

**But deep on-word RT is carried by the nonlinear component.** Orthogonalizing qntee9
against lntee9 (the pure acceleration residual): at layer 9 the LINEAR neighborhood
trend does not predict on-word reading time (β = −0.0007, n.s.), while the
ORTHOGONALIZED nonlinear component does (β = +0.0029, p = 1.4e-8), beyond surprisal and
fine TEE. So the deep neighborhood trajectory carries reading-time-relevant structure
that a linear extrapolator is blind to — the one place nonlinearity earns its keep.

**Orthogonality preserved.** Nonlinearity does not re-introduce a structure coupling or
change the entropy relationship (qntee9 × entropy +0.083 ≈ lntee9 × entropy +0.100;
both × closure ≈ 0), so the surprisal-orthogonality story is unaffected.

Caveat: the deep-nonlinear-RT effect is one clean specification (orthogonalized,
held-out, punct-free); a layer sweep of the nonlinear component would confirm where it
peaks and is the natural robustness follow-up. Net answer to "what about nonlinear
trends?": they add nothing at the point scale and nothing to the causal wake, but the
acceleration component of the DEEP neighborhood trajectory is a real, separable
predictor of human reading time.

## Artifacts (repo: garden-path-tee-curvature/extensions/)

RESEARCH_PROGRAM.md (pre-committed design) · x0_compute_states.py (validated states)
· x1_coarse_tee.py → coarse_tee_8a6087341e.csv · x2_coarse_rt.py · x3_coarse_wake.py
→ wake_coarse_step6.csv · x3b_analyze_wake.py · x4_nonlinear_tee.py →
nonlinear_tee_8a6087341e.csv · x5_meta_manifold.py → meta_manifold_8a6087341e.csv ·
x6_verify.py · x7_heldout_ntee.py → ntee_heldout_8a6087341e.csv · x8_layer_sweep.py
→ results/x8_layer_sweep.csv · xlib.py (shared conventions) · x*.log (raw stdout) ·
results/*.csv (machine-readable tables)
