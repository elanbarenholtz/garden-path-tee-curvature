# Extensions / tee_vs_curvature audit (2026-07-27)

Audited for the class of error that broke the garden-path analysis, then
stress-tested the headline claim. Scripts: `ext_wake_targetctrl.py`, output
`ext_wake_output.txt`.

## Structural audit: this code is written to a different standard

| check | tee_vs_curvature + extensions |
|---|---|
| sample identity | MD5 hash of (story_id, word_idx) asserted before every table (`assert sh == "8a6087341e"`) |
| merge integrity | every merge uses `validate="one_to_one"`; row counts asserted (`assert len(D) == 9840`) |
| lag construction | lags computed on the full frame, **then** filtered — the correct order, and the exact inverse of the garden-path bug |
| punct-free subsets | derived after lagging, with predictors re-z-scored within subset |
| inference | cluster-robust SEs by sentence, position + story fixed effects throughout |

The garden-path failure mode is structurally impossible in this code. The
`validate="one_to_one"` calls alone would have raised on the merge patterns that
went wrong there.

Reproduction check: `analyze_dissociation.py` and `analyze_wake.py` were rerun
from the repo and reproduce their published tables exactly (dissociation:
TEE×closure +0.134, curvature×closure −0.029, curvature×entropy −0.116; wake:
perp significant at L1 only punct-free, surprisal persisting to L5).

## The one real gap: missing target controls — and the claim survives it

The parent `analyze_wake.py` controls properties of the word being measured at
lag L (surprisal, length, frequency at w+L), on the reasoning that a
high-surprisal target has a more volatile state and will show a larger relative
change under any perturbation. The extensions version `x3b_analyze_wake.py`,
which produced the headline "neighborhood TEE has a causal wake at every lag
1–10", **omits those controls**. No extensions script includes them.

Added back (punct-free, DV = wake_rel):

| lag | ntee_k100 as published | ntee_k100 + target controls |
|---|---|---|
| L1 | +0.1997 (8.7e-13) | +0.1997 (7.4e-19) |
| L2 | +0.1877 (2.0e-10) | +0.1754 (1.2e-09) |
| L3 | +0.1724 (2.5e-09) | +0.1715 (1.6e-09) |
| L4 | +0.1687 (5.8e-08) | +0.1672 (6.1e-08) |
| L5 | +0.1676 (6.8e-09) | +0.1628 (1.5e-08) |
| L6 | +0.1330 (2.0e-06) | +0.1331 (1.7e-06) |
| L7 | +0.1148 (3.1e-05) | +0.1162 (2.3e-05) |
| L8 | +0.1328 (1.1e-06) | +0.1326 (1.4e-06) |
| L9 | +0.1434 (1.6e-07) | +0.1404 (3.1e-07) |
| L10 | +0.1287 (2.0e-06) | — |

Essentially unchanged at every lag. The neighborhood wake is not an artifact of
target-word properties. Add the controls to the published spec anyway — it costs
nothing and closes an obvious reviewer question.

The same table also reproduces the parent dissociation cleanly: `tee3_perp`
(fine-grained reorientation) is significant at L1 and gone thereafter, while
`ntee_k100` persists to L10. That contrast — local at the point level,
propagating at the neighborhood level — is the substantive finding, and it holds
under the stricter spec.

## Remaining caveats, none fatal

- **Wake n = 1,627** words (the ablation is expensive, computed on a STEP=6
  subsample of the locked sample). Smaller than the RT analyses by two orders of
  magnitude. Worth stating plainly; the effects are large enough to carry it.
- **No displacement control in any wake model.** The models control surprisal,
  length, frequency and punctuation at w, but not the raw magnitude of w's own
  state change. A reviewer could ask whether an unusual word mechanically
  produces a larger downstream perturbation regardless of trajectory geometry.
  The arXiv paper has a displacement control for the RT analyses; the analogous
  control for the wake analyses does not exist and would need hidden states to
  compute. **This is the one check I would run before submitting.**
- **Clustering circularity** was anticipated and handled — `x7_heldout_ntee.py`
  builds a held-out-clustering version (`ntee_ho`) and `x10_robustness_table.py`
  reruns the headline regressions with it. Good practice, already in place.

## Bottom line

The newer pipelines are sound. The one methodological gap I found does not change
the result. Combined with the Natural Stories audit, a paper built on
locked-sample material — TEE/curvature dissociation, the par/perp cancellation,
neighborhood wake, and the reading-time result with its lexical and punctuation
robustness checks — rests on code I could not break.
