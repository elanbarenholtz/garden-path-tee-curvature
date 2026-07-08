# TEE Extensions: nonlinear trajectories & neighborhood-level dynamics

Locked sample 8a6087341e (n=9,840), GPT-2 small layer 6, Natural Stories.
All conventions inherited from parent project: z-scored predictors (ddof=0),
controls = from_start + fs2 + from_end + fe2 + C(story_id), cluster-robust SEs
by sent_uid, hash re-verified before every table, punctuation controlled +
punct-free robustness reported, raw tables only.

## Motivating result (parent project)
TEE (linear, point-level) is LOCAL: ≤1 word of behavioral spillover, ≤1 word of
causal wake. Long-range implications live in surprisal (5+ word wake). Question:
is that locality a fact about trajectory geometry, or about the LINEAR,
POINT-LEVEL version of it?

## Branch 1 — Neighborhood-level (coarse) TEE  [x1, x2, x3]
H1a. Coarse-grained trajectories (trailing-mean smoothing m∈{3,5,10} words;
     k-means soft-assignment trajectories k∈{30,100,300}) carry structure
     signal beyond word-level TEE (partial r vs closure, entropy; punct-ctrl).
H1b. Coarse-TEE predicts reading time at longer lags than fine TEE (L0..L3).
H1c. KEY TEST: coarse causal wake. Ablate word w; measure perturbation of the
     COARSE downstream state at +1..+10. If coarse reorientations propagate
     where fine ones vanish by +2, the range dissociation (geometry=local,
     information=propagating) is scale-dependent, not fundamental.

## Branch 2 — Nonlinear extrapolators  [x4]
H2a. Quadratic TEE (acceleration-aware) and local-LDS TEE (fitted dynamics)
     change what the residual carries. Risk to monitor: richer predictors may
     absorb the entropy channel and break TEE's orthogonality to surprisal.
H2b. Flow-field TEE (kNN corpus flow; allocentric: deviation from what
     trajectories TYPICALLY do here) dissociates from egocentric TEE
     (deviation from own recent heading).

## Branch 3 — Meta-TEE & manifold correction  [x5]
H3a. Meta-TEE: extrapolation error of the HEADING sequence (tangent dynamics).
H3b. Manifold-corrected TEE: split TEE into within-local-manifold vs
     off-manifold components (local PCA); does the structure signal live
     off-manifold?

## Pipeline
x0_compute_states.py   recompute + validate layer-6 states; save NPZ per story
x1_coarse_tee.py       build coarse measures; dissociation tables -> coarse_tee_*.csv
x2_coarse_rt.py        RT spillover L0..L3 with coarse measures
x3_coarse_wake.py      ablation wake at fine AND coarse scale, MAXL=10
x4_nonlinear_tee.py    quad / local-LDS / flow-field TEE + dissociation + RT
x5_meta_manifold.py    meta-TEE + manifold split + dissociation + RT
x6_verify.py           punct-free reruns, per-story sign consistency, sink audit

Every script re-verifies the sample hash and validates recomputed states
against locked tee_k3/tee_k50 before producing measures.
