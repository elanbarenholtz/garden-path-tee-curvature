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

## Artifacts (repo: garden-path-tee-curvature/extensions/)

RESEARCH_PROGRAM.md (pre-committed design) · x0_compute_states.py (validated states)
· x1_coarse_tee.py → coarse_tee_8a6087341e.csv · x2_coarse_rt.py · x3_coarse_wake.py
→ wake_coarse_step6.csv · x3b_analyze_wake.py · x4_nonlinear_tee.py →
nonlinear_tee_8a6087341e.csv · x5_meta_manifold.py → meta_manifold_8a6087341e.csv ·
x6_verify.py · xlib.py (shared conventions) · x*.log (raw stdout) · results/*.csv
(machine-readable tables)
