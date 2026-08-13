# arXiv v2 of 2606.05346 — draft revision

Drafted 2026-07-27. Section-by-section replacement text for the corrected
version. **Read the "Numbers that must be recomputed first" section at the end
before submitting anything** — several v1 tables came from the superseded
measure pipeline and cannot be carried over as-is.

---

## 1. arXiv version comment (the field that appears on the abstract page)

> v2: Substantial correction. The garden-path reading-time analysis of v1 has
> been withdrawn. Two errors were found: (a) the analysis sample excluded the
> disambiguating word entirely — the previous-word reading-time control was
> computed after restricting to the critical region, so all ROI-0 rows were
> dropped, and the reported N = 95,173 comprises only the two spillover
> positions; (b) within the critical region the trajectory coefficient reverses
> sign across positions (spillover 1: −0.009; spillover 2: +0.010; interaction
> p = 1e-8), so the pooled estimate does not describe a consistent effect. The
> model-scale analysis (v1 Table 5) was computed on the same sample and is also
> withdrawn. The Natural Stories analysis is retained and strengthened: it has
> been recomputed on a hash-verified rebuild of the measure pipeline, and now
> includes subject-level inference across 171 participants and controls for word
> identity and punctuation. The garden-path *corpus* is retained under a
> different analysis: pooling across conditions and word positions, trajectory
> extrapolation error predicts self-paced reading time across all 144 sentences
> and 2,000 participants, replicating the Natural Stories effect in a second
> corpus. Two eye-tracking corpora have been added and are reported in full,
> including a non-replication. Conclusions are narrowed accordingly.

Keep it factual and specific. Naming the mechanism of each error is what makes
this a correction rather than an edit.

---

## 2. Revised abstract

Changes: remove the garden-path claim and the model-scale claim; **remove the
r = .044 orthogonality claim (see §8 — it is r = +0.31 on the verified
pipeline)**; **restate the displacement control (§8 — the opposite-sign
dissociation does not hold)**; add the eye-tracking result; narrow the closing
sentence to self-paced reading.

> ⚠️ The abstract text below still contains the two superseded claims, marked
> **[REPLACE]**. Corrected wording follows in §8.

> Human language comprehension unfolds sequentially: each word is processed in
> the context of those that came before, and the interpretation builds
> incrementally over time. Surprisal, the negative log probability of a word
> given its context, robustly predicts reading times, reflecting the predictive
> nature of comprehension. But surprisal reduces rich sequential representations
> to a single scalar at each word, discarding information about the direction in
> which the interpretation has been evolving. Dynamical-systems approaches
> suggest that the trajectory of the evolving interpretive state, not just its
> position at each moment, should shape processing, and language itself may have
> short-horizon continuity, since speakers plan utterances a few words at a
> time. We introduce trajectory extrapolation error: at each word, we fit a
> linear trajectory to the preceding hidden states of a transformer language
> model and measure deviation from the extrapolated path. On the Natural Stories
> corpus, this measure is nearly orthogonal to surprisal (r = .044) and
> independently predicts self-paced reading times (ΔAIC = 112 over controls and
> surprisal; N = 813,621). The effect holds under subject-level inference: 125 of
> 171 participants show a positive effect estimated independently
> (p = 5 × 10⁻¹²), and it survives controls for word identity and punctuation.
> A displacement control shows the effect is not reducible to representational
> change magnitude. The picture in eye tracking is mixed: the effect appears on
> total reading time in ZuCo (11 of 12 participants) but does not replicate in
> OneStop (360-participant corpus), where trajectory extrapolation error instead
> predicts the probability of a regression, a measure on which surprisal is
> null. We conclude that trajectory dynamics constitute a dissociable component
> of processing cost in self-paced reading, and that their expression in
> free-viewing eye movements is unresolved.

---

## 3. New section, placed immediately after the Introduction

### Corrections to the previous version

> This version withdraws the garden-path reading-time analysis reported in v1
> and the model-scale analysis that was computed on the same sample.
>
> The garden-path analysis contained a sample-construction error. Reading times
> were restricted to the critical region (the disambiguating word and two
> spillover positions) before the previous-word reading-time control was
> computed by a within-trial lag. Because the disambiguating word is the first
> word of that region, its lagged value was undefined and every such observation
> was dropped. The reported N = 95,173 therefore comprises only the two
> spillover positions (47,532 and 47,641 observations); the disambiguating word,
> which the analysis was designed to test, was absent from every model.
>
> Reanalysis with the disambiguating word restored shows a second problem. The
> trajectory coefficient is not homogeneous across the critical region: it is
> negative at the first spillover position (β = −0.0085, p = 6.6 × 10⁻⁵),
> positive at the second (β = +0.0102, p = 5.5 × 10⁻¹⁰), and not significant at
> the disambiguating word itself (β = −0.0034, p = .084), where surprisal
> accounts for the reading-time variance (β = +0.034, p = 1.8 × 10⁻⁶⁵). A
> position × trajectory interaction across the region is reliable
> (χ²(2) = 36.8, p = 1.0 × 10⁻⁸). The pooled estimate reported in v1 exceeds
> both of the position-specific estimates from which it is formed, indicating
> that it reflects between-position variance rather than a consistent
> within-position relationship. We therefore do not regard the garden-path
> reading-time result as interpretable, and it is removed rather than revised.
>
> The validation claim in v1 — that ambiguous sentences show higher
> extrapolation error at the disambiguation point "across all layer and window
> configurations" — is also inaccurate. Per construction, the effect holds for
> NP/S (+2.55, 20 of 24 items, p < 10⁻⁴) and NP/Z (+4.25, 23 of 24 items,
> p < 10⁻⁴) but reverses for main-verb/reduced-relative items (−1.72, 17 of 24
> items, t(23) = −3.26, p = .003). Surprisal does not reverse for these items
> (+5.23, 23 of 24 items), so the two measures dissociate on the canonical
> garden path, with surprisal in the expected direction.
>
> The reversal is diagnostic of the item set rather than of the measure. At the
> disambiguating word the three constructions produce nearly identical
> extrapolation error in the *ambiguous* condition (MV/RR 99.2, NP/S 98.3,
> NP/Z 99.1). What differs is the unambiguous control: the MV/RR control sits at
> 101.0 against 95.7 and 94.8 for the other two. The MV/RR control is formed by
> restoring a full passive relative clause ("the horse **that was** raced past
> the barn fell"), a low-frequency and structurally heavy construction that
> perturbs the model's trajectory about as much as the garden path does. The
> ambiguous-minus-unambiguous difference for these items therefore compares two
> disrupted states rather than a disrupted state against a baseline. Note that
> the disambiguating word and the three words entering its fit window are
> identical across conditions, so the difference is carried entirely by earlier
> context propagating into the hidden states.
>
> We report this because it is a general point about the item set, which is
> widely used: controls matched for grammaticality and length need not be
> matched on model-internal quantities, and a difference score computed against
> an unmatched control is uninterpretable regardless of the measure used.
>
> An attention-sink confound was additionally investigated, following the
> observation that transformer models assign anomalously large representational
> magnitude to the first token of a sequence (Xiao et al., 2023). Because the
> garden-path stimuli were presented as isolated sentences, fit windows near the
> start of a sentence can include this position. At the reported layer-6,
> 3-word configuration no fit window in the critical region reaches the first
> token, and the measure is numerically identical when that position is excluded;
> the wider windows reported in v1 (w = 5, w = 7) are affected. This confound is
> therefore not the reason for the withdrawal, but the presentation format should
> have been stated in v1 and the control should have been run.
>
> These errors do not affect the Natural Stories analyses, which use a separate
> pipeline over connected text and are reported below in strengthened form.

---

## 4. Replacement for the Natural Stories section

### Natural Stories

> **Measure pipeline.** The values reported here are computed from a rebuilt and
> hash-verified measure pipeline (sample fingerprint 8a6087341e, n = 9,840
> words). This rebuild followed the discovery of alignment errors in the
> pipeline used for v1. The two differ substantially: the effect reported in v1
> (ΔAIC = 2.5, β = +0.0006) is superseded by the value obtained on the verified
> sample (ΔAIC = 112, β = +0.0035) on the same observations, with the same
> controls and the same model specification. Only the measure values differ. The
> rebuilt sample has been independently recomputed twice, matching to 1.4 × 10⁻¹⁴
> in-repository and to r = 0.9999999999991 on separate hardware; the v1 measure
> file cannot be reproduced. We report the verified values and flag the
> discrepancy explicitly rather than silently adopting the more favourable
> number.
>
> **Independence of measures.** [retain v1 text: r = .044]
>
> **Reading-time prediction.** Trajectory extrapolation error improved fit over
> controls and surprisal (ΔAIC = 112, β = +0.0035, p = 4.0 × 10⁻²⁶,
> N = 813,621, 178 participants). For scale, in the same model β(surprisal)
> = +0.0112 and β(log frequency) = +0.0072: the trajectory effect is
> approximately one third the magnitude of surprisal and is a second-order
> effect on reading time.
>
> **Subject-level inference.** Because a pooled model over 813,621 observations
> can register an effect that no individual reader exhibits, we estimated the
> model separately within each participant. Of 171 participants with sufficient
> data, 125 (73.1%) showed a positive coefficient (sign test p = 1.2 × 10⁻⁹;
> Wilcoxon p = 5.1 × 10⁻¹²; t(170) = 7.46). The mean per-participant coefficient
> (+0.0039) closely matches the pooled estimate (+0.0035). Thirty-nine
> participants reached individual significance.
>
> **Word identity.** Because frequency is the dominant lexical correlate of the
> measure, we asked whether it predicts reading time for the same word across
> different contexts, centring the outcome and all predictors within word type
> (2,919 word types occurring five or more times). The effect attenuates by
> roughly 40% but remains (ΔAIC = 23.1, β = +0.0022, p = 5.3 × 10⁻⁷). A
> substantial share of the raw effect is lexical; a trajectory-specific
> component survives.
>
> **Punctuation.** The corpus attaches trailing punctuation to words, and
> punctuation tokens occupy distinctive regions of the model's state space.
> Adding a punctuation covariate slightly strengthens the effect (ΔAIC = 115.4),
> and restricting to punctuation-free words strengthens it further
> (ΔAIC = 138.3, β = +0.0041).
>
> **Position within sentence.** The effect is absent at sentence onset and grows
> with depth into the sentence: β = −0.0027 for the first three words
> (p = .022), +0.0053 at words 6–10, and +0.0080 beyond word 21
> (interaction χ²(4) = 220.8, p = 1.3 × 10⁻⁴⁶). At sentence-initial positions a
> three-word backward window is partly undefined or spans a sentence boundary.
> This boundary condition should be taken into account in any application of the
> measure.

---

## 4b. New section: replication in a second self-paced corpus

Place immediately after Natural Stories and before the eye-tracking section.
Scripts: `gp_allwords.py`, `gp_allwords_robust.py`, `gp_allwords_matched.py`;
outputs `gp_allwords_out.txt`, `gp_allwords_robust_out.txt`,
`gp_allwords_matched_out.txt`.

> ✅ **Independently verified 2026-08-07** (`VERIFY_sap.py`, output
> `VERIFY_sap_out.txt`). The measure pipeline was reimplemented by different
> methods at every step — tokenizer offset-mapping alignment instead of
> sequential index tracking, vectorised gather instead of a token loop,
> closed-form OLS instead of `lstsq` — and the analysis sample rebuilt with row
> counts asserted at each stage. Agreement: TEE to 4.7 × 10⁻¹⁶ relative,
> surprisal to 6.1 × 10⁻⁸, identical missingness at all 576 undefined positions,
> sample 444,737 rows / 2,000 participants exactly, and all headline
> coefficients reproduced to five decimal places (A1 +0.02238 / 61.1%,
> A2 +0.02505 / 62.7%, union control +0.02543, permutation floor 52.1% p = .231,
> pooled ΔAIC 121.9). Sentence-word inventory hash `e9fd2c547a`; verified
> measures in `sap_measures_VERIFIED_e9fd2c547a.csv`.

### The garden-path corpus as a second self-paced reading corpus

> The stimuli of the withdrawn analysis constitute, independently of the
> ambiguity manipulation, a self-paced reading corpus of 144 syntactically
> difficult sentences read by 2,000 participants. We therefore repeated the
> Natural Stories analysis on it, pooling across conditions, constructions and
> word positions and making no use of the ambiguous/unambiguous contrast. This
> is a replication attempt for the Natural Stories effect, not a test of the
> garden-path hypothesis.
>
> Analyses use subject-level inference throughout: the model is estimated
> separately within each participant and the coefficients are tested across
> participants. Words whose fit window is undefined are excluded, which restricts
> the analysis to word positions 5 and later; the first token never enters a fit
> window or serves as a target. After exclusions, 444,737 observations from 2,000
> participants remain.
>
> **Result.** Controlling word length, log frequency, punctuation, and position
> within the sentence entered flexibly (distance from sentence start and end,
> each with a quadratic term), trajectory extrapolation error predicted log
> reading time (β = +0.0224, 61.1% of participants positive,
> Wilcoxon p = 2.7 × 10⁻³²). Adding a sentence-final indicator, to absorb
> wrap-up effects, slightly strengthens it (β = +0.0251, 62.7%,
> p = 5.5 × 10⁻³⁹).
>
> **The effect is not an artefact of surprisal's functional form.** Replacing
> linear surprisal with a spline leaves it essentially unchanged (df = 3:
> β = +0.0202; df = 5: +0.0207; df = 8: +0.0209, 60.4%, p = 1.9 × 10⁻²⁸). In
> pooled models, splining surprisal reduces but does not remove the improvement
> in fit contributed by the trajectory measure (ΔAIC = 153.2 with linear
> surprisal, 121.9 with a df = 8 spline).
>
> **Null floor.** Permuting the trajectory measure within participant and
> refitting gives 52.1% sign agreement (β = +0.0015, p = .23), establishing the
> baseline against which the observed 60–63% should be read.
>
> **Comparison with surprisal.** Both coefficients were read from the same
> per-participant fits, so the comparison uses identical rows and controls. The
> trajectory measure is the more *consistent* of the two across participants
> (61.1% vs 56.6%) but the *smaller* in magnitude: within participants,
> |β(trajectory)| exceeded |β(surprisal)| in 42.1% of cases (paired Wilcoxon
> p = 3.7 × 10⁻²¹; mean |β| 0.069 vs 0.091). The same ordering holds when each
> measure is entered linearly while the other is splined. As in Natural Stories,
> the trajectory effect is a second-order contribution alongside surprisal, not a
> competitor to it.
>
> **A boundary condition.** Adding previous-word reading time to the model
> approximately halves the trajectory coefficient (β = +0.0136, 57.5%,
> p = 4.9 × 10⁻¹⁶) while substantially increasing surprisal's (β = +0.0448,
> 64.7%). We do not have an account of this asymmetry. It should be noted that
> the lag-1 analysis that succeeds in Natural Stories does not transfer here: the
> trajectory measure at word *t* does not positively predict reading time at
> word *t*+1 in this corpus (β = −0.0066, 46.3% positive). The sentences are
> 13–17 words and presented one per trial, so the spillover structure differs
> from connected text; we report the discrepancy rather than resolving it.

> **Note on the sign-agreement statistic.** A threshold of 65% sign agreement
> was fixed in advance of these analyses, carried over from the Natural Stories
> work. Neither measure meets it here under flexible position controls:
> surprisal reaches 56.6% and the trajectory measure 61.1%. Because participants
> in this corpus contribute roughly 220 observations each — against thousands in
> Natural Stories — per-participant coefficients are correspondingly noisy, and
> the threshold is evidently too strict at this level of per-participant data.
> We therefore report sign agreement descriptively, against the permutation
> floor, rather than as a criterion.

**Notes for writing, not for the manuscript.**

- The framing must stay disciplined: this is a *reading-time* result on a corpus
  that happens to consist of garden-path materials. It is not evidence about
  garden-path processing, and no sentence should imply otherwise.
- Sign agreement and the permutation floor stay in the manuscript for both
  measures. They are the answer to the standard objection to large-N pooled
  reading-time models — that a pooled effect need not describe any individual
  reader — and with 2,000 participants and p ≈ 10⁻³² a reviewer will raise it.
  The numbers favour the measure (61.1% vs surprisal's 56.6%, floor 52.1%), so
  omitting them would cost the rebuttal and gain nothing.
- What is dropped is the *gate*, not the statistic: 65% is arbitrary and scales
  with observations per participant, so reporting it as pass/fail would make a
  real effect read as a failed test. The paragraph above states the threshold,
  its failure, and the reason, in three sentences.

---

## 4c. New section: is the effect a predictability residual?

Place after §4b, applying to both self-paced corpora. Scripts `sap_bigsurp.py`,
`sap_bigsurp_refit.py`, `ns_bigsurp_refit.py`; outputs `*_out.txt`.

### Controlling for a stronger model's surprisal

> Because the trajectory measure and the surprisal control are both derived from
> GPT-2 Small, an alternative account of the effect is available: the measure may
> not index trajectory geometry at all, but simply mark the words at which that
> particular model's probability estimate is poor. Words the model handles badly
> would be expected to show both an anomalous hidden state and a mis-estimated
> surprisal, and controlling for the same model's surprisal cannot remove such a
> confound, since the control is constructed from the same error.
>
> We tested this by leaving the trajectory measure unchanged and replacing the
> surprisal control with estimates from substantially larger models: GPT-2 Medium,
> GPT-2 XL (1.5B parameters, roughly twelve times GPT-2 Small) and Pythia-410M.
> Pythia differs additionally in tokenizer, training corpus and positional
> encoding, and so provides a largely independent estimate of predictability
> rather than a scaled-up version of the same one.
>
> The effect does not weaken under any of these controls. In Natural Stories:
>
> | surprisal control | fit to RT (ΔAIC vs controls) | ΔAIC (TEE) | β | subject-level |
> |---|---|---|---|---|
> | GPT-2 Small | 1016.4 | 111.8 | +0.00354 | 73.1% of 171 |
> | GPT-2 Medium | 1004.6 | 129.0 | +0.00378 | — |
> | GPT-2 XL | 886.2 | 136.9 | +0.00390 | 75.4% of 171 |
> | Pythia-410M | 990.0 | 125.6 | +0.00374 | 74.3% of 171 |
> | **all four entered together** | **1057.6** | **116.8** | **+0.00362** | **75.4% of 171** |
> | all four, XL and Pythia splined (df = 4) | — | 125.2 | +0.00375 | — |
>
> The second column is essential to reading this table correctly, and it is why
> the apparent *increase* in the trajectory effect under larger-model surprisal
> must not be interpreted as the effect strengthening. Surprisal from the larger
> models fits reading time **worse** — GPT-2 Small 1016.4, GPT-2 XL 886.2 — which
> is the surprisal scaling paradox reported by Oh and Schuler (2023b) appearing in
> this corpus. A larger model's surprisal is therefore a *weaker* control, and it
> leaves more outcome variance available for any additional predictor. Across the
> four single-model controls, ΔAIC(TEE) varies inversely with how well that
> surprisal predicts reading time, exactly as that account implies.
>
> The interpretable comparison is the final row set. Entering all four surprisal
> estimates together produces the best-fitting predictability control available
> (ΔAIC 1057.6, better than any single estimate), and under it the trajectory
> measure retains a contribution of essentially unchanged size (ΔAIC 116.8 against
> 111.8 for the original specification; β +0.00362 against +0.00354; 75.4% of
> participants against 73.1%).
>
> The sentence corpus shows the same insensitivity, with the coefficient
> effectively unchanged across controls (GPT-2 Small +0.0251; GPT-2 XL +0.0255;
> Pythia-410M +0.0255; all three together +0.0254; all three splined at df = 4
> +0.0246). Pooled improvements in fit are 203–212 across single-model controls
> and 153.7 when GPT-2 XL surprisal is splined. Permutation floors are 55.0%
> (Natural Stories) and 52.2% (sentence corpus).
>
> The correlation between the trajectory measure and surprisal also falls as the
> surprisal estimate improves: r = .310 with GPT-2 Small, .271 with GPT-2 Medium,
> .254 with GPT-2 XL, and .275 with Pythia-410M. Part of the shared variance
> between the two measures is
> therefore attributable to GPT-2 Small's estimation error rather than to genuine
> overlap, and removing it leaves the measures more separable, not less.
>
> We conclude that the effect is not a predictability residual. Under the
> strongest predictability control we can construct — four surprisal estimates
> from three model families and two tokenizers, entered jointly — the trajectory
> measure's contribution is undiminished.

**Notes for writing, not for the manuscript.**

- **Retracted claim.** An earlier version of this section reported that the
  effect "strengthens under a stronger control," citing ΔAIC 111.8 → 136.9 with
  GPT-2 XL surprisal. That reading was wrong. GPT-2 XL surprisal is a *worse*
  predictor of reading time than GPT-2 Small's (886.2 vs 1016.4 over controls),
  so it is a weaker control and inflates any additional predictor. Never report a
  single-larger-model substitution as evidence of robustness; report the union
  spec, and always alongside how well each control fits the outcome.
- The same inversion is present in the sentence corpus: base-model AIC is
  1059844.5 with GPT-2 Small surprisal, 1059935.3 with GPT-2 XL, 1059877.1 with
  Pythia-410M; ΔAIC(TEE) is correspondingly 203.2, 211.7, 210.1. The union
  control gives 203.4 — again unchanged from baseline.
- Incidental finding worth one sentence in the Discussion: the scaling paradox
  (Oh & Schuler 2023b), which v1 cites as *motivation*, is directly observable in
  both corpora here. That is a small independent replication of it.
- Limitation to state plainly: the surprisal estimates correlate highly with one
  another (.90–.95 in Natural Stories, .967–.971 in the sentence corpus), so
  substitution is a weaker manipulation than it sounds. This is why the union and
  splined specifications are reported — they span more of the predictability
  space than any single estimate.
- Pythia-410M surprisal on the Natural Stories locked sample was computed for
  this purpose (`ns_pythia_surp.py` → `ns_pythia410m_surp_8a6087341e.csv`, full
  coverage of all 9,840 words, agreement with the GPT-2 estimates r = .927–.950).
  Both corpora therefore carry a control that differs from GPT-2 Small in
  tokenizer, training corpus and positional encoding, and there is no remaining
  architecture-independence gap.
- Pythia's mean word surprisal is higher (4.83 bits vs 3.16–3.73) because its
  BPE vocabulary segments words differently and word surprisal is summed over
  subwords. This is a scale difference, not a quality difference; all predictors
  are z-scored, so it does not affect the models.

---

## 5. New section: eye tracking

### Eye-Movement Corpora

> Self-paced reading meters comprehension serially and does not permit
> regressions or parafoveal preview. To ask whether the effect generalises to
> natural reading, we analysed two eye-tracking corpora. All analyses use
> subject-level inference.
>
> **ZuCo** (12 participants, isolated sentences). Trajectory extrapolation error
> predicted total reading time in 11 of 12 participants (β = +0.0079, sign test
> p = .006), consistent in direction with Natural Stories. First fixation
> duration was null. We note that an earlier analysis of the same data with
> untransformed durations, without a surprisal control and with two participants
> excluded returned a null (p = .065); the result is sensitive to specification.
>
> **OneStop** (180 participants in the ordinary-reading subcorpus; 1,104,883
> observations). The effect did not replicate. Under a specification using the
> corpus's own surprisal annotations and previous-word controls, first fixation
> and gaze duration were null and total reading time showed a small negative
> coefficient (β = −0.0023, p = .029). In the same data and specification,
> surprisal predicted total reading time in 178 of 180 participants
> (β = +0.031, p = 2.9 × 10⁻³¹), so the corpus is demonstrably sensitive to
> processing-cost effects.
>
> **Regressions.** In OneStop, trajectory extrapolation error predicted the
> probability of a regression out of a word (β = +0.0165, 111 of 180
> participants, p = 3.4 × 10⁻⁵), a measure on which surprisal was null
> (β = −0.0033, p = .22). The effect survived oculomotor controls for line
> number, within-line position, launch site and landing position, and is
> uncorrelated with all of them (|r| < .011), while those variables strongly
> predict regressions (P(regress) = .056 line-initial, .264 line-final).
> Restricting to line-medial words halves the coefficient (β = +0.0080) and the
> sign test becomes null (p = .21). A same-direction but weaker pattern appears
> in ZuCo (8 of 12 participants, Wilcoxon p = .034; sign test p = .39). We report
> this as a suggestive result requiring preregistered replication, not as an
> established finding.
>
> We do not have an account that reconciles these results. Two corpora
> (Natural Stories, ZuCo) show a positive effect on reading time and one
> well-powered corpus (OneStop) does not, and the difference does not track the
> self-paced/eye-tracking distinction.

---

## 6. Discussion changes

- **Delete** any sentence claiming the effect is present in garden paths, and
  the paragraph built on the reversal-of-accumulated-direction intuition as
  *evidence* (it can stay as motivation, clearly marked as such).
- **Delete** the model-scale claim pending recomputation on Natural Stories.

### 6a. Engage the benchmark's conclusion (new — required)

v1 cites Huang et al. (2024) three times, all as a data source, and never
addresses their finding. The paper it cites is titled "Large-scale benchmark
yields no evidence that language model surprisal explains syntactic
disambiguation difficulty," and v1 used their data to argue that a model-derived
measure *does* explain disambiguation difficulty. This must be confronted
directly rather than left for a reviewer to notice.

> Huang et al. (2024) report that surprisal from neural language models does not
> account for the magnitude of syntactic disambiguation difficulty, with
> garden-path sentences showing the largest misalignment. Our own item-level
> analysis reproduces this: across 72 item × construction pairs, the
> ambiguous-minus-unambiguous difference in surprisal does not predict the
> corresponding difference in reading time once construction is controlled
> (β = −0.035, p = .78). The trajectory measure fares no better (β = −0.019,
> p = .89). Moving from a model's output probabilities to the geometry of its
> internal states therefore does not repair the misalignment Huang et al.
> identify. Whatever governs the magnitude of garden-path difficulty in humans
> is not recoverable from either quantity as we have computed them.
>
> The measures nevertheless behave differently on the same corpus when the
> ambiguity manipulation is set aside. Across all words of all sentences, the
> trajectory measure predicts reading time more consistently across participants
> than surprisal does (§4b). We take this to indicate that the two dissociate on
> what they capture, not that either resolves the benchmark's finding.

### 6b. The motivating example (new — required)

The Introduction motivates the measure with "The horse raced past the barn
fell," a main-verb/reduced-relative item. That is the one construction in which
the measure moves the wrong way (§3). Retaining the example without comment
would invite the obvious objection.

> We retain this example as an illustration of the intuition motivating the
> measure, but note that the measure does not behave as the illustration
> suggests for this construction: reduced-relative items show *lower*
> extrapolation error in the ambiguous condition than in their controls
> (§Corrections). The intuition and the measure come apart precisely where the
> intuition is most vivid, for reasons traceable to the control sentences rather
> than to the measure.

### 6c. The surprisal scaling paradox (new — an incidental result)

v1 cites Oh and Schuler (2023b) as motivation. The paradox is directly
observable in our own data and should be reported as such.

> As an incidental observation, our surprisal controls reproduce the scaling
> paradox reported by Oh and Schuler (2023b). In Natural Stories, surprisal from
> GPT-2 Small improves fit over lexical controls by ΔAIC = 1016.4, GPT-2 Medium
> by 1004.6, and GPT-2 XL — the largest and lowest-perplexity model tested — by
> only 886.2, despite being the better language model. Pythia-410M falls between
> them at 990.0. The same ordering holds in the sentence corpus. This has a
> practical consequence for analyses of the present kind: substituting a larger
> model's surprisal is not a more stringent control but a less stringent one,
> because it absorbs less of the outcome variance. Reported improvements in fit
> from any additional predictor will rise accordingly. For this reason we report
> our trajectory results against a control containing all four surprisal
> estimates jointly, which fits reading time better than any single estimate
> (ΔAIC = 1057.6).

- **Add** to Limitations:

> The effect is second-order relative to surprisal and to lexical frequency, and
> a substantial share of it is lexical. Its behavioural expression is corpus- and
> paradigm-dependent in ways we cannot currently explain: it is robust in two
> self-paced reading corpora, present in one eye-tracking corpus, and absent in a
> larger one. Claims about trajectory sensitivity in human processing should be
> restricted to self-paced reading until this is resolved. We tested five
> candidate accounts of the eye-tracking dissociation — serialisation, regressive
> eye movements, lag misalignment, parafoveal preview, and paradigm-scaling of
> effect sizes — and none was supported; the preview account failed in the
> direction opposite to its prediction. We therefore report the boundary as an
> unexplained empirical fact rather than offering an account we cannot defend.

---

## 8g. The two remaining blockers, resolved (2026-08-07)

Script `v2_offdiag_and_r044.py`, output `v2_offdiag_out.txt`.

### 8g-i. r = .044 was the entropy correlation

Every TEE variant on the locked sample was correlated with surprisal, by Pearson
and Spearman, across window sizes k = 2…50 and their normalised forms, plus the
nonlinear, coarse and Pythia variants in `extensions/`. The surprisal
correlations span **+0.186 to +0.349**. Not one lands near .044. The only
quantity in the entire sweep that does is **r(tee_k3, entropy) = +0.0429**.

This settles the question. v1's framing claim — "nearly orthogonal to surprisal
(r = .044)" — reports the correlation with **entropy**, not surprisal. The same
explanation covers the Pythia values (.046, .047) reported at v1 line 247, which
were produced by the same code path.

> **For the Corrections section:** The independence claim in v1 was derived from
> a mislabelled quantity. The value r = .044 is the correlation between
> extrapolation error and the entropy of the model's next-word distribution, not
> its surprisal. On the verified pipeline the correlation with surprisal is
> r = .310. The two measures are correlated but not redundant; they are not
> nearly orthogonal, and every sentence asserting near-orthogonality is
> withdrawn. The dissociation matrix (Table 2), which does not depend on this
> correlation, becomes the evidence for independent contribution.

### 8g-ii. The off-diagonal composition paragraph is wrong and must be rewritten

v1 ¶47 (manuscript.tex line 298) characterises the two off-diagonal cells.
Recomputed on the verified sample:

**Low surprisal / high TEE** (810 positions, 306 word types). v1's claim that
this cell is enriched for coordinators and complementizers is **partly
supported**: "and" occurs there 16.5% of the time against 8.2% chance, "as"
15.2%, "had" 14.6% — all enriched. But "that" is at 10.1%, essentially chance.
And the claim is misleading about what dominates the cell: the most enriched
items are story-specific proper nouns and content words — *bird* (15.0×),
*Elvis* (14.9×), *Bradford* (13.0×), *bulbs* (12.8×), *manor* (11.9×),
*king* (11.9×), *Roswell* (9.2×), *Abby* (7.9×). Closed-class share is 48.5%
against a corpus baseline of 45.8%, i.e. barely elevated.

**High surprisal / low TEE** (610 positions, 388 word types). v1's content-word
examples are **flatly wrong**: *ocean* occurs 0 times out of 7 in this cell,
*manor* 0 out of 10, *tics* 0 out of 22. All three are absent from the cell they
are cited as populating; *manor* is in fact enriched in the *opposite* cell. The
discourse-pivot examples partly survive — *now* 35.7% vs 6.2% chance, *then*
16.7%, *first* 13.6%, all enriched; *however* 7.7%, at chance. The cell is
genuinely depleted of function words (31.6% closed-class vs 45.8% overall).

**Replacement text:**

> The words populating the two off-diagonal cells differ systematically. The
> high-surprisal / low-extrapolation cell is depleted of closed-class items
> (31.6% against a corpus baseline of 45.8%) and enriched for discourse pivots
> that are lexically unexpected at their position but structurally anticipated —
> "now" (27.6× the corpus rate), "when" (18.1×), "then" (12.9×). The
> low-surprisal / high-extrapolation cell is enriched both for coordinators and
> complementizers ("and" 3.9×, "as" 3.6×, "had" 3.5×) and for recurring
> story-specific proper nouns and content words ("bird" 15.0×, "Elvis" 14.9×,
> "manor" 11.9×) — items that are highly predictable within their narrative
> context but that open a constituent whose trajectory differs in kind from the
> preceding one. We note that both cells are small (810 and 610 corpus positions)
> and that this characterisation is descriptive; it is offered as an indication
> of what the measures may be tracking, not as evidence for the dissociation,
> which rests on the regression results.

**Note for writing.** Do not reuse v1's specific word examples. Three of them
(*ocean*, *manor*, *tics*) have zero occurrences in the cell they are attributed
to. This appears to be a third consequence of the superseded measure file rather
than a separate error.

---

## 9. Getting this to Cognition

### 9a. What the paper now argues

The v1 framing — a new measure that succeeds where surprisal fails, including on
garden paths — is gone. The defensible contribution is narrower and, we think,
more interesting:

1. A representational-geometry measure derived from language model hidden states
   predicts self-paced reading time beyond surprisal, in **two independent
   corpora** (Natural Stories, 178 participants; SAP Benchmark, 2,000
   participants), surviving flexible position controls, spline surprisal, and a
   joint control built from four surprisal estimates across three model families
   and two tokenizers.
2. It does **not** repair the misalignment identified by Huang et al. (2024):
   neither surprisal nor trajectory geometry predicts the magnitude of
   garden-path difficulty at the item level.
3. It does **not** transfer to free-viewing eye movements, and five candidate
   explanations for that failure were tested and rejected.

That is a paper about the boundaries of what language model internals explain
about human processing — which is a live question, and one Cognition's readership
is positioned to care about.

**Suggested title change.** "Predict Human Processing Costs Beyond Surprisal" is
now too broad, since the effect is confined to self-paced reading. Something
closer to: *Trajectory dynamics in language model hidden states predict
self-paced reading times beyond surprisal, but do not generalise to eye
movements.*

### 9b. Blocking items, in order

| # | item | status |
|---|---|---|
| 1 | Lock and independently verify §4b/§4c on SAP | **DONE ✅** (`VERIFY_sap.py`, all checks pass, hash `e9fd2c547a`) |
| 2 | Edit `manuscript.tex` (in `~/Projects/Garden Path V1/`) into v2 | in progress |
| 3 | Off-diagonal composition analysis (v1 ¶47) | **DONE ✅** — v1's examples are wrong; replacement text in §8g-ii |
| 4 | r = .044 / entropy check | **DONE ✅** — it was the entropy correlation; see §8g-i |
| 5 | Rebuild the model-scale claim on Natural Stories (§8f), or drop it | optional |
| 6 | Read the 2026 follow-up (arXiv 2605.15440) before finalising the Huang framing | recommended |

All blocking analyses are complete. The remaining work is editorial: applying
this document to `manuscript.tex`.

**Verification note for the manuscript.** Both self-paced corpora now rest on
independently recomputed pipelines with published hashes (Natural Stories
`8a6087341e`, SAP `e9fd2c547a`). Given that v2 is a correction of errors caused
by unverified pipelines, this is worth one sentence in the Methods.

### 9c. Sequencing

arXiv v2 should be posted **before** the Cognition submission, not after. The
correction establishes the record independently of review, and a Cognition
submission that already carries the corrected analyses cannot be undercut by a
reviewer discovering the v1 errors. It also means the editor who has seen the
Matters Arising correspondence sees the correction as already public.

---

## 7. Numbers that must be recomputed before submitting

**This is the blocking item.** v1's Tables 2, 3, 4 and 6 were computed from the
superseded measure file, which is not reproducible and which we now know
differs materially from the verified pipeline (ΔAIC 2.5 vs 112 on the headline
model). Carrying those numbers into v2 unchanged would repeat the error the
correction is about.

| v1 element | status | action |
|---|---|---|
| Table 1 (garden path) | withdrawn | remove |
| Table 5 (model scale) | withdrawn — garden-path sample | remove, or rebuild on Natural Stories |
| Table 2 (dissociation matrix) | **needs recomputation** on locked sample | rerun |
| Table 3 (displacement control) | **needs recomputation** | rerun |
| Table 4 (direction preservation) | **needs recomputation** | rerun |
| Table 6 (Pythia cross-architecture) | **needs recomputation**; also note v1's GPT-2/Pythia comparison used different participant subsamples (180 vs 100) | rerun on matched samples |
| r = .044 orthogonality | verify on locked sample | check |
| Natural Stories headline | recomputed ✓ | use as drafted |
| Subject-level, lexical, punctuation, position | recomputed ✓ | use as drafted |
| Eye-tracking sections | computed ✓ | use as drafted |

Estimated work: the recomputations are mechanical (the locked sample and
verified pipeline exist), but they must be done before this draft is a
submittable manuscript rather than a plan.

---

## 8. Results of the recomputation (2026-07-27) — two more v1 claims fail

Script `v2_tables_23.py`, output `v2_tables_23_out.txt`, `v2_t3.txt`.

### 8a. The orthogonality claim does not hold

| correlation | v1 | verified sample |
|---|---|---|
| **r(TEE, surprisal)** | **.044** | **+0.310** |
| r(TEE, entropy) | — | +0.043 |
| r(TEE, log frequency) | — | −0.438 |
| r(TEE, displacement) | — | +0.800 |

This is the paper's framing claim — "nearly orthogonal to surprisal" — and it is
wrong on the verified pipeline by nearly an order of magnitude. r = .044 appears
to have been the correlation with *entropy*, which does come out at +0.043;
whether that is a coincidence or a mislabelling in the v1 pipeline should be
checked before writing the correction.

TEE shares roughly 10% of its variance with surprisal and roughly 19% with log
frequency. It is a partly-independent measure, not a near-orthogonal one.

**Replacement abstract wording:**

> On the Natural Stories corpus, this measure is correlated with but not reducible
> to surprisal (r = .31) and independently predicts self-paced reading times
> (ΔAIC = 112 over controls and surprisal; N = 813,621).

The Discussion's "two dissociable components" framing survives — the measures do
contribute independently — but "nearly orthogonal" must go everywhere it appears,
and the dissociation-matrix analysis (Table 2) becomes the load-bearing evidence
for independence rather than the correlation.

### 8b. The displacement control does not show opposite directions

v1: "displacement and extrapolation error predict in opposite directions."
Verified sample (mixedlm, by-participant random intercept, n = 812,730):

| model | β | p |
|---|---|---|
| TEE alone | +0.00354 | 1.4e-26 |
| displacement alone | +0.00315 | 5.2e-20 |
| both, TEE coefficient | **+0.00287** | 8.9e-9 |
| both, displacement coefficient | **+0.00092** | .075 |

Same sign, not opposite. What survives is weaker but still useful: entered
together, TEE retains its effect and displacement drops to non-significance, so
the effect is not reducible to representational change magnitude. Given the two
measures correlate at r = 0.80, that is a meaningful result — but it is a
different claim from the one in v1.

Note that v1 already reported the opposite-sign dissociation failing to replicate
in Pythia. It now also fails in GPT-2 on the verified pipeline, which suggests
the original result was an artifact of the superseded measure.

**Replacement wording:**

> A displacement control shows the effect is not reducible to representational
> change magnitude: although the two measures are highly correlated (r = .80),
> extrapolation error retains an independent effect when both are entered
> (β = +0.0029, p = 8.9 × 10⁻⁹) while displacement does not (β = +0.0009,
> p = .075).

### 8c. Table 2 survives, with changed numbers

The dissociation matrix reproduces qualitatively. Both off-diagonal cells remain
significant relative to the low/low baseline:

| cell | v1 | verified |
|---|---|---|
| high surprisal, low TEE | +0.039 | **+0.0289** (n = 50,260, t = 14.38, p = 8e-47) |
| low surprisal, high TEE | +0.008 | **+0.0095** (n = 66,620, t = 5.43, p = 6e-08) |

Full matrix (mean log RT, deviation from low/low baseline of 5.7167):

| | TEE low | TEE mid | TEE high |
|---|---|---|---|
| surprisal low | 0.0000 | +0.0050 | +0.0095 |
| surprisal mid | +0.0157 | +0.0157 | +0.0280 |
| surprisal high | +0.0289 | +0.0306 | +0.0412 |

This is now the primary evidence that the two measures capture distinct
variance, and it holds.

### 8d. Table 4 (direction preservation) reproduces cleanly

Recomputed on the revalidated states (`v2_table4_dirpres.py`, output `v2_t4.txt`),
using the v1 specification: fit a line to the preceding *w* word states, take the
unit direction, and measure |cos| between that direction and the step at the
current word and at +1, +2, +3 words ahead.

| layer | window | current | +1 | +2 | +3 | n |
|---|---|---|---|---|---|---|
| L6 | 3 | **0.436** | **0.099** | 0.078 | 0.077 | 10,216 |
| L6 | 5 | 0.396 | 0.097 | 0.076 | 0.073 | 10,196 |
| L12 | 3 | 0.615 | 0.541 | 0.540 | 0.539 | 10,216 |
| L12 | 5 | 0.602 | 0.547 | 0.543 | 0.544 | 10,196 |

v1 reported L6 current .44, +1 .10, +2/+3 ≈ .08, and L12 ≈ .54 sustained. The
recomputation matches to the reported precision. **Table 4 can be carried into
v2 with updated numbers and no change of interpretation:** at the intermediate
layer direction dies after one word; at the final layer it persists.

### 8e. Table 6 (cross-architecture) reproduces and improves on matched samples

`v2_table6_pythia.py`, output `v2_t6.txt`. All three models evaluated on
**identical rows and identical participants** (n = 812,730; 178 participants),
correcting v1's comparison of GPT-2 on 180 participants against Pythia on 100.

| model | positional encoding | ΔAIC | β | p |
|---|---|---|---|---|
| GPT-2 Small | absolute (learned) | 111.8 | +0.0035 | 1.4e-26 |
| Pythia-160M | rotary (RoPE) | 115.5 | +0.0033 | 2.2e-27 |
| Pythia-410M | rotary (RoPE) | **487.6** | **+0.0073** | 1.7e-108 |

The cross-architecture claim holds and is now a fair comparison: the effect does
not depend on the positional encoding scheme, and GPT-2 Small and Pythia-160M
give nearly identical estimates on the same data.

### 8f. Opportunity: the scale claim can be rebuilt on Natural Stories

v1's model-scale analysis (Table 5) is withdrawn because it was computed on the
garden-path sample. But Pythia-160M → Pythia-410M shows a large within-family
increase (ΔAIC 115.5 → 487.6) on matched data, which is the scale claim the paper
wanted, on a corpus that supports it. The `extensions/` directory already
contains GPT-2 Medium and GPT-2 XL measures on the locked sample, so a five-point
scale analysis (GPT-2 Small/Medium/XL, Pythia-160M/410M) is achievable without
new forward passes beyond what exists.

Recommended: rebuild the scale claim this way rather than dropping it. It would
be stronger than v1's version and computed on the corpus that survives.

### Still outstanding

- The v1 "composition of off-diagonal cells" analysis (v1 paragraph 47) uses
  tercile cell membership that has now changed; rerun or drop.
- Verify whether v1's r = .044 was the entropy correlation (see §8a).

### Recomputation status

| v1 element | outcome |
|---|---|
| Table 1 (garden path) | **withdrawn** |
| Table 5 (model scale) | **withdrawn**; rebuild per §8f |
| orthogonality r = .044 | **fails** — r = +0.31 |
| Table 3 (displacement) | **claim fails**; weaker version holds |
| Table 2 (dissociation matrix) | holds, numbers updated |
| Table 4 (direction preservation) | **holds**, matches v1 |
| Table 6 (cross-architecture) | **holds**, improved on matched samples |
| Natural Stories headline | recomputed, much stronger |
| SAP corpus, all-words reading time (§4b) | **new** — replicates Natural Stories; needs independent verification |

### Added 2026-08-07

- §4b drafted: the garden-path corpus retained as a second self-paced reading
  corpus (2,000 participants, 444,737 observations). Effect survives flexible
  position controls, a sentence-final flag, and df = 8 spline surprisal; sits
  above a 52.1% permutation floor; is smaller than surprisal but more consistent
  across participants.
- Corrections section extended with the MV/RR control diagnosis: the reversal is
  a property of the unmatched control, not of the measure.
- **Blocking before submission:** §4b is single-run and unverified. Lock the
  sample by hash and recompute independently, exactly as was done for Natural
  Stories, before this section is treated as established.
- §4c drafted: stronger-surprisal control on both self-paced corpora. TEE
  survives GPT-2 Medium, GPT-2 XL and Pythia-410M surprisal, entered singly,
  jointly, and splined. Under the joint (best-fitting) control, ΔAIC 116.8 vs
  111.8 baseline; subject-level 75.4% vs 73.1%. The predictability-residual
  objection is answered.
- **Corrected 2026-08-07:** an earlier draft of §4c claimed the effect
  *strengthens* under larger-model surprisal. It does not — larger-model
  surprisal fits reading time worse (scaling paradox), so it is a weaker control.
  Only the union spec is interpretable. See the notes under §4c.
- Pythia-410M surprisal computed on the Natural Stories locked sample
  (`ns_pythia_surp.py`), closing the architecture-independence gap. ΔAIC 125.6,
  subject-level 74.3%; all four surprisals together 116.8 / 75.4%.
- Still outstanding from before: the off-diagonal composition analysis (v1
  paragraph 47) and the r = .044 / entropy check (§8a).
