# Displacement control on the causal wake (2026-07-27)

The objection: the wake is measured by ablating word w and observing how much
downstream representations shift. A word that simply moves the hidden state a
long way — regardless of direction — removes more representational mass when
deleted, so it would produce a larger downstream shift mechanically. The
extensions wake models control surprisal, length, frequency and punctuation at
w, but nothing about the raw magnitude of w's own state change.

Scripts: `compute_displacement.py` (state recomputation), output
`displacement_output.txt`; displacement values in `displacement_8a6087341e.csv`.

## Recomputation and validation gate

Layer-6 states recomputed with the project's conventions (CHUNK 1024,
STRIDE 512, first-write-wins, word = final subword), then validated against the
locked sample before any displacement value was used:

- closure_depth mismatches: **0 / 9,840**
- final_bpe mismatches: **0 / 9,840**
- max |tee_k3 − recomputed|: 1.0e-4 (cross-machine float32 GEMM variation, the
  same order the extensions run reports)

Three measures emitted: `disp_step` = ‖h[ls] − h[ls−1]‖ (last BPE step),
`disp_word` = ‖h[ls] − h[prev word's ls]‖ (word-to-word displacement, the
quantity of interest), `state_norm` = ‖h[ls]‖.

## Displacement is strongly correlated with TEE — the control was worth running

| pair | r |
|---|---|
| disp_word × tee_k3 | **+0.80** |
| disp_word × tee3_perp | +0.76 |
| disp_word × ntee_k100 | see output |

This is much higher than I expected and is the reason the control matters: at
r = 0.80 with tee_k3, "how far the state moved" and "how far off-heading it
moved" are largely the same variable in this corpus. Any claim that TEE is not
reducible to displacement needs to be made carefully, and the arXiv paper's
opposite-signs dissociation for reading time becomes a more important result,
not a lesser one.

## The neighborhood wake survives, essentially untouched

Punct-free, DV = wake_rel, with target controls throughout; displacement added
as a covariate at w.

| lag | ntee_k100 without disp | ntee_k100 with disp | disp_word |
|---|---|---|---|
| L1 | +0.1997 (7.4e-19) | **+0.1983 (1.2e-18)** | +0.1038 (.044)* |
| L2 | +0.1754 (1.2e-09) | +0.1750 (1.2e-09) | +0.0324 (.65) |
| L3 | +0.1715 (1.6e-09) | +0.1695 (1.9e-09) | +0.1443 (.028)* |
| L4 | +0.1672 (6.1e-08) | +0.1662 (6.3e-08) | +0.0698 (.30) |
| L5 | +0.1628 (1.5e-08) | +0.1621 (1.4e-08) | +0.0539 (.41) |
| L6 | +0.1331 (1.7e-06) | +0.1314 (1.8e-06) | +0.1178 (.063) |
| L7 | +0.1162 (2.3e-05) | +0.1156 (2.3e-05) | +0.0459 (.53) |
| L8 | +0.1326 (1.4e-06) | +0.1322 (1.2e-06) | +0.0285 (.70) |
| L9 | +0.1404 (3.1e-07) | +0.1400 (2.8e-07) | +0.0214 (.75) |
| L10 | +0.1298 (1.6e-06) | +0.1289 (1.5e-06) | +0.0623 (.39) |

The largest change at any lag is 0.0017 in β. Displacement itself is significant
at only 2 of 10 lags and never approaches ntee's magnitude.

**Interpretation.** The long-range causal wake is carried by *where* the
trajectory was relocated, not by *how much* the state moved. That is the
strongest form of the claim, and it is now defended against the obvious
mechanical objection. Given that displacement and the fine-grained TEE measures
are collinear at r ≈ 0.8, it is notable that neighborhood TEE is not — the
neighborhood construction evidently captures something displacement does not.

## Recommendation

Add `disp_word` to the published wake specification alongside the target
controls. Both are free — neither changes a coefficient meaningfully — and
together they close the two most likely referee objections to a causal claim.

Report the r = 0.80 displacement–TEE correlation openly rather than letting a
reviewer discover it. It makes the dissociations that do hold more impressive,
and concealing it would be the kind of thing that looks worse than it is.
