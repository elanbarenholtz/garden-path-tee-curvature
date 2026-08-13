# Executive summary — TEE project status, 2026-07-27

## Bottom line

The garden-path work is not salvageable and must be withdrawn from the arXiv
paper. The Natural Stories work is sound and five times stronger than published.
The model-internal work (geometry, causal wake) is the strongest material in the
project and survived every audit. Two of the paper's framing claims —
orthogonality to surprisal, and the displacement dissociation — do not hold on
the verified pipeline.

Two papers follow: a corrected v2 of arXiv 2606.05346, and a new paper on the
model-internal geometry.

---

## 1. What broke

**Garden paths (arXiv §3.1, Tables 1 and 5) — withdrawn.**
- `model_comparison_stats.py` filters to the critical region, *then* computes the
  previous-word RT control by a within-trial lag. The disambiguating word is
  first in that region, so every one of its rows is dropped. Published
  N = 95,173 is exactly the two spillover positions (47,532 + 47,641); the word
  the analysis was about was never in the models.
- With it restored, the coefficient reverses within the region: −0.0085 at
  spillover 1, +0.0102 at spillover 2, n.s. at the disambiguating word;
  interaction χ²(2) = 36.8, p = 1e-8. The pooled estimate exceeds both parts.
- Validation claim ("higher error across all configurations") is false for MVRR
  (−1.72, p = .003).
- Table 5's model-scale claim is computed on the same sample and goes with it.

**Orthogonality — fails.** r(TEE, surprisal) = **+0.31** on the verified
pipeline, not .044. Note r(TEE, entropy) = +0.043; the published figure may have
been the entropy correlation. r(TEE, log frequency) = −0.44.

**Displacement control — claim fails.** v1: "opposite directions." Actual: same
sign (TEE +0.0035, displacement +0.0032). What survives is weaker and still
useful — entered jointly, TEE holds (+0.0029, p = 9e-9), displacement goes n.s.
(p = .075) despite r = 0.80 between them.

---

## 2. What held, and improved

**Natural Stories reading time.** ΔAIC = **112** (published: 2.5), β = +0.0035,
p = 4e-26, N = 813,621. The published value came from a pre-rebuild pipeline with
known alignment bugs and is not reproducible; the locked sample is
hash-verified and independently recomputed twice.

Robustness, all new:
- **Subject-level:** 125/171 participants positive independently, p = 5e-12.
  Not pseudoreplication.
- **Word identity:** survives centring within word type — ΔAIC 23.1, p = 5e-7.
  Attenuates ~40%, so a real share is lexical, but it is not a frequency proxy.
- **Punctuation:** stronger without punctuation-final words (ΔAIC 138).
- **Position:** absent at sentence onset, grows with depth (χ²(4) = 221).
  A boundary condition to report.

**Direction preservation (Table 4)** reproduces to reported precision.
**Cross-architecture (Table 6)** reproduces and improves on matched samples
(v1 compared GPT-2 on 180 participants to Pythia on 100):

| model | encoding | ΔAIC |
|---|---|---|
| GPT-2 Small | absolute | 111.8 |
| Pythia-160M | RoPE | 115.5 |
| Pythia-410M | RoPE | 487.6 |

**Bonus:** the 160M → 410M jump is the scale claim v1 wanted, on the corpus that
survives. With GPT-2 Medium/XL already in `extensions/`, a five-point scale
analysis is available with no new compute.

**Model-internal work — audited, clean.** The tee_vs_curvature and extensions
pipelines use hash assertions, `validate="one_to_one"` merges and correct lag
ordering; the garden-path failure mode is structurally impossible there. The
neighborhood-TEE causal wake (10 lags, β 0.13–0.20) survives target controls and
a newly added displacement control essentially unchanged.

---

## 3. The behavioral picture is unresolved

| corpus | paradigm | n | result |
|---|---|---|---|
| Natural Stories | self-paced | 171 | positive, 73% of participants, p = 5e-12 |
| ZuCo | eye-tracking, sentences | 12 | positive (TRT), 11/12, p = .003 |
| OneStop | eye-tracking, paragraphs | 180 | null; TRT β = −0.0023 |

The split does not track self-paced vs eye-tracking. OneStop is the outlier and
the best-powered. In OneStop, surprisal predicts total reading time in 178/180
participants, so the corpus is demonstrably sensitive — it just does not see TEE.

One live lead: in OneStop, TEE predicts **probability of a regression**
(β = +0.0165, p = 3.4e-5) where surprisal is null (p = .22). It survives
oculomotor controls but halves on line-medial words (β = +0.0080, sign test
n.s.), and replicates weakly in ZuCo (8/12). Suggestive, not established.

---

## 4. Recommended plan

1. **arXiv v2** — corrected behavioral paper. Draft in `V2_DRAFT.md`, including
   the version comment, revised abstract, corrections section, and all
   recomputed numbers. Remaining: rerun the off-diagonal composition analysis,
   confirm the .044/entropy question, optionally add the five-point scale figure.
2. **New paper** — model-internal geometry: structure/uncertainty dissociation,
   par/perp cancellation, causal wake. Strongest material, fully audited,
   independent of the behavioral mess.
3. **Later, if at all** — the regression effect, preregistered, one corpus
   (CELER is cleanest: isolated sentences, no line-boundary mechanics), criteria
   fixed in advance, answer accepted either way.

---

## 5. Caveat on this session's process

Three intermediate conclusions I reported were later overturned by better
specifications: that w=7 should be dropped for sink contamination (it survives),
that the sign flip was a ROI-0 effect (it is ROI-1-vs-2 heterogeneity), and that
OneStop showed a significant reversal (it is a non-replication with a small
residual). A fourth — the regression/serialization account — died against its own
preregistered test. Every result above that matters has been recomputed under a
fair specification, but the pattern argues for independent verification of the
key claims before submission, particularly the N = 95,173 decomposition (which is
pure arithmetic and takes ten seconds) and the ΔAIC 2.5 → 112 reconciliation.

Files: all analyses, outputs and per-topic result documents are in
`gp_confound_check/`. `HANDOFF_verify_these.md` contains the verification recipes.
