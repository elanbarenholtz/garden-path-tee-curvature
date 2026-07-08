# TEE Extensions: nonlinear trajectories and neighborhood-level dynamics

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
structural integration (closure; cancellation; ≤1 word), neighborhood TEE = semantic/
topical repositioning (uncertainty-coupled; 10+ word wake; on-word cost), surprisal =
lexical prediction error (its own propagating wake). And the fine channel itself
decomposes geometrically: structure in-manifold, uncertainty off-manifold.

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

## Artifacts (repo: garden-path-tee-curvature/extensions/)

RESEARCH_PROGRAM.md (pre-committed design) · x0_compute_states.py (validated states)
· x1_coarse_tee.py → coarse_tee_8a6087341e.csv · x2_coarse_rt.py · x3_coarse_wake.py
→ wake_coarse_step6.csv · x3b_analyze_wake.py · x4_nonlinear_tee.py →
nonlinear_tee_8a6087341e.csv · x5_meta_manifold.py → meta_manifold_8a6087341e.csv ·
x6_verify.py · x7_heldout_ntee.py → ntee_heldout_8a6087341e.csv · x8_layer_sweep.py
→ results/x8_layer_sweep.csv · xlib.py (shared conventions) · x*.log (raw stdout) ·
results/*.csv (machine-readable tables)
