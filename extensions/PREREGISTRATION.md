# Locked analysis specification (internal pre-registration)

Frozen before manuscript drafting. Any deviation is reported as an explicit,
labeled robustness deviation, not folded silently into the main result.

## Sample
Locked sample `8a6087341e`, n = 9,840 words, 10 Natural Stories, GPT-2 small
layer 6 (parent). Hash re-verified at the top of every script. States
recomputed on-machine and validated against locked tee_k3/tee_k50
(r > 1 − 1e-9, max rel err < 1e-4) before any measure is trusted.

## Measures (final)
- Fine TEE: `tee_k3` (k = 3 linear extrapolation, BPE grain, final-subword
  anchor). Decomposition `tee3_par`, `tee3_perp`.
- Neighborhood TEE: `ntee_k100` = k = 3 extrapolation error on the sqrt-soft
  k-means (k = 100) assignment trajectory. Primary k = 100; k = 30, 300
  reported as robustness only.
- Deep neighborhood TEE for discourse analyses: `ntee_l9` (layer 9, the
  wake-peak layer). Leakage-safe variant `ntee_l9_ho` (per-story held-out
  clustering) is the confirmatory version.
- Controls: surprisal, entropy (model-native, definitions validated to
  r ≥ 0.99998 vs locked), word_length, log_freq, has_trailing_punct.

## Covariate set (fixed)
All regressions: position FE (`from_start + fs2 + from_end + fe2`) +
`C(story_id)`, cluster-robust SE by `sent_uid`, predictors z-scored (ddof = 0).
RT models add `prev_logRT` (lag-1 autocorrelation control). DV for behavior =
per-word mean log RT, RT filtered 100–3000 ms.

## Confirmatory tests (the ones the paper stands on)
1. **Fine TEE → RT beyond surprisal** (parent replication), on-word + L1.
2. **ntee → RT**, full fine-TEE + surprisal + lexical battery, on-word.
   Primary lag = 0. Spillover L1–L3 exploratory (self-paced truncation noted).
3. **ntee causal wake**, DV = `wake_rel_L`, L = 1..10, controls = entropy,
   curvature, surprisal, tee3_perp/par, ctee_m5, length, freq. Primary
   contrast: ntee wake persists ≥ L5 while fine perp dies by L2.
4. **Layer dissociation**: on-word RT tracks shallow-layer ntee; long wake
   tracks deep-layer ntee. Reported as beta-by-layer curves, not a single p.
5. **Event-boundary discrimination** (confirmatory = held-out ntee_l9_ho):
   among sentence-initial, punct-free, non-truncated words, logistic
   `event_bnd ~ ntee_l9_ho + surprisal + entropy + tee_k3 + length + freq`.
   Primary claim = ntee beats surprisal and fine TEE (sign + AUC), not a
   fixed effect-size threshold.

## Exclusions (fixed)
- Punctuation: every headline result reported punct-controlled AND punct-free;
  punct-free is the confirmatory version where they diverge.
- Each story's truncated first sentence dropped from sentence-initial analyses.
- Wake: systematic every-STEP subsample (STEP = 6 small; STEP = 12 larger
  models), MAXL = 10, CTX = 256.

## Robustness package (report once, then stop; ROBUSTNESS_TABLE.md)
punct-controlled; punct-free; held-out clustering; k = 30/100/300; no-punct
downstream window; documented nulls (ctee_m5, nswitch, quadratic/LDS
extrapolators, hard cluster switch).

## Model family (fixed)
Primary: GPT-2 small. Replication: GPT-2 medium and GPT-2 XL — reported to
establish that both signal TYPES recur and that the laminar locus is
model-dependent. No further models before submission.

## What is explicitly OUT of scope for this paper
MEG/fMRI; GPT-4-scale models; a full theory of allocentric vs egocentric TEE;
per-layer mechanistic tracing. Flagged as future work.
