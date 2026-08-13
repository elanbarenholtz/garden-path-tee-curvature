# Notes for the geometry paper

Material that is about what the measure *is*, rather than about what it predicts
in behaviour. Parked here so it does not leak into the v2 correction.

Last updated 2026-08-10.

---

## The finding: the measure is two things with opposite signatures

Extrapolation error at word *i* is `||h_i - proj||`, where `proj` is a line
through *h_{i−3}..h_{i−1}* projected one step. Decomposing the residual relative
to the fitted heading:

- **`resid_par`** — component *along* the heading. Overwhelmingly negative:
  the extrapolation overshoots, i.e. the trajectory did not travel as far as the
  straight-line prediction. Correlates with the composite at **r = −0.85**, so
  this is most of what the measure is.
- **`resid_perp`** — component *orthogonal* to the heading. The word took the
  representation sideways. This is the quantity the theory is actually about,
  and it is only **r = 0.56** with the composite.

The two are essentially independent of the run-up geometry
(`r(resid_perp, slope_norm) = .049`), so the decomposition separates cleanly.

**In OneStop they predict opposite behaviour** (subject-level, 180 participants,
controls = surprisal, log frequency, word length, punctuation):

| component | skipping | first fixation duration |
|---|---|---|
| composite `tee` | **+**0.0080, 66.1% (more skipping) | null |
| `resid_par` (overshoot) | −0.0216, 78.9% neg (more skipping) | +0.0058, p = .004 |
| `resid_perp` (lateral) | −0.0090, 71.1% neg (**less** skipping) | +0.0028, p = .029 |

Read carefully: the composite predicts *more* skipping; the lateral component
predicts *less* skipping and *longer* fixations — the difficulty direction the
theory predicts. The composite's behaviour is inherited from the overshoot
component, which dominates its variance.

**Implication.** The OneStop "reversal" reported in v2 is a property of the
composite measure, not of trajectory disruption. If this holds, the measure
should be split and `resid_perp` carried forward as the theoretically motivated
quantity.

## Supporting geometry

Confirmed directly on OneStop (`onestop_geometry.py`, reproduces the existing
values at r = 1.0000000000, max diff 1.4e−14):

- bent run-up → short fitted step: `r(curv_prev, slope_norm) = −0.60`
- composite tracks fitted step length: `r(tee, slope_norm) = +0.62`

So a large share of the composite is determined by the run-up *before the target
word is seen at all*. That is a property of the measure worth stating plainly in
any paper that uses it.

## What did NOT hold

The run-up account of the skipping effect. The hypothesis was that skipping
tracks the coherence of the preceding context — which would have neatly solved
the timing problem, since skipping decisions are made parafoveally. It does not
survive: entered head to head, `slope_norm` flips sign and `curv_prev` goes null,
while the target-deviation terms carry the effect.

The lag analysis that motivated it (`onestop_runup_probe.py`) still stands on its
own terms — tee(t−1) predicts skipping better than tee(t), +0.0119 vs +0.0080,
and survives when both are entered — but the direct decomposition says that is
not because run-up *geometry* is doing the work.

## Status and cautions

**Exploratory.** Four analyses on the same corpus in one session, none
preregistered. The par/perp split does have prior support in this project — the
entropy loadings went opposite ways for the two components in the Natural Stories
work — which is a coherence argument, not a confirmatory test.

**Partly lexical.** Adding previous-word length, frequency and surprisal pulls
every component below the 65% sign-agreement criterion (`resid_perp` → 38.3%,
p = 4.6e−5). Real but attenuated.

**Cross-corpus warning sign.** `r(tee, log_freq)` is **+0.18 in OneStop** and
**−0.44 in Natural Stories** — opposite signs for the same measure. This needs an
explanation before anything here is built on.

## Next steps, if taken up

1. Preregister the par/perp split and test it on Natural Stories reading times,
   where the pipeline is hash-locked.
2. Resolve the frequency-correlation sign difference between corpora first; it
   may be a tokenisation or context-length artefact.
3. Only then decide whether the measure should be redefined.

## Also belongs in this paper

- Curvature vs extrapolation error, and the King / Fedorenko / Hosseini
  engagement — their claim is about curvature and entropy inside the model, which
  is a model-internal argument.
- The causal wake and ablation results.
- Coarse, nonlinear and normalised variants; the meta-manifold work.
- Cross-layer structure (direction preservation persists at the final layer and
  dies after one word at layer 6).

---

## Relationship to v2

None of the above goes into v2. The one thing v2 arguably *should* say, because
it prevents a wrong reading, is that the negative coefficient on total reading
time tracks **fixation count** rather than fixation duration: high-value words
are skipped more (β = +0.008, p = 4.6e−8) and refixated less (β = −0.006,
p = 6e−4), while first fixation duration is null (p = .40). Readers are not
processing those words faster; their eyes are landing on them less often.
One sentence, no decomposition, no theory.

---

## Functional form of the effect (added 2026-08-10)

Explored while trying to build a core results figure for v2; dropped from that
paper because it raises a question the paper does not answer.

**The relationship is not linear, not a clean threshold, and not yet
characterised.** Partial-effect profiles (log RT residualised within participant
on all other predictors, binned by decile of the measure):

| decile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Natural Stories | −.011 | +.007 | −.014 | −.013 | −.002 | −.014 | −.004 | +.008 | +.012 | **+.031** |
| Garden path | −.015 | −.013 | −.033 | −.002 | +.009 | −.026 | −.001 | **+.030** | +.029 | +.022 |

The top-end rise is unambiguous (Natural Stories decile 10: t = 8.95,
p = 6e−16). The obvious reading is a threshold — flat below, rise above — but it
does not survive:

- **The low region is not flat and not noise.** Deciles 1, 3, 4 and 6 are each
  significantly *below* baseline (p = .004 to 6e−5) while 2, 5 and 7 sit at zero,
  and that alternation reproduces across random halves of participants
  (split-half r = +0.65 in Natural Stories, +0.88 in the garden-path corpus, on
  deciles 1–7 alone).
- **No shape wins.** Against linear, a top-decile indicator gives ΔAIC −0.61 and
  a hinge +0.21 (Natural Stories); −0.06 and +0.08 (garden path). Every model is
  within a point of every other and each wins in about half of participants.
- **A spline loses to linear** (ΔAIC −0.5 to −4.6, and −2.0 to −6.8), which is
  consistent with a threshold but equally consistent with the flexible fit
  spending parameters on structure it cannot capture. Per-participant fits are
  underpowered for this; a pooled spline was not tried.

**Half the Natural Stories effect is in the extremes.** Dropping the top and
bottom deciles leaves 47% of the coefficient (+0.0060 from +0.0128, 59.1% of
participants positive). In the garden-path corpus 77% survives.

**What this means for the measure.** The linear coefficient summarises a
relationship whose shape is reproducible and unidentified. That is a fact about
the measure rather than about reading, which is why it belongs here. It also
connects to the par/perp result above: a quantity that is two components glued
together might well have a composite functional form.

**Do not repeat:** the decile profiles were nearly reported as showing a
threshold effect, on the basis of eyeballing the top end and treating the rest as
noise. The split-half test says the rest is not noise.
