# Garden path sink/punctuation diagnostic — results (2026-07-27)

SAP ClassicGP, 24 items × 3 constructions × {amb, unamb} = 144 sentences.
GPT-2 small, word-level TEE (final-subword states, linear fit, Euclidean error)
at the disambiguating word. Presentations: A isolated (presumed paper condition),
B neutral 10-word prefix, C isolated with word 0 dropped from fit windows.
Paired t on amb − unamb per item. Script: `gp_sink_check.py`;
full table: `gp_sink_check_results.csv`.

**The sink is present and large:** token-0 norm is ~36× the interior-token norm
at layer 6.

## Verdict by configuration

| config | isolated | prefix | drop-tok0 | sink exposure (amb/unamb windows containing word 0) |
|---|---|---|---|---|
| L6 k=3 | +1.73, p=1e-4 | +1.76, p=6e-5 | identical | 0 / 0 — clean |
| L6 k=5 | **+458, p=7e-10** | −1.18, n.s. | +1.88, p=1e-3 | **0.42 / 0.00 — asymmetric** |
| L6 k=7 | −2.39, n.s. | +5.92, p=4e-5 | +4.94, p=4e-27 | 1.00 / 0.79 — asymmetric |
| L12 k=3 | −6.84, p=.008 | −5.11, n.s. | identical | 0 / 0 |
| L12 k=5 | +7.98, p=.01 | −4.38, p=.05 | −1.83, n.s. | 0.42 / 0.00 — asymmetric |
| L12 k=7 | −3.49, n.s. | −2.22, n.s. | −1.46, n.s. | 1.00 / 0.79 |

1. **The headline configuration (L6, k=3) survives.** Fit windows at the
   disambiguator never reach token 0, and the amb>unamb effect is unchanged
   under context-prepending. The core validation claim is sink-clean.
2. **k=5 and k=7 on isolated sentences are contaminated.** Window-sink
   exposure differs by condition (amb disambiguators sit 1–2 words earlier),
   and at k=5 the isolated "effect" is inflated ~200× (d=+458 vs +1.9 clean).
   Any manuscript result from w=5/w=7 — including the Table 1 L12/w=5 model,
   the strongest RT result — must be rerun with prefix or token-0 exclusion.
3. **L12 does not support the validation claim** in any clean configuration
   (null or reversed).

## Per-construction (L6, k=3, all presentations agree)

- NPS: +2.55, p=3e-6 — robust, punctuation-clean. Best exemplar.
- NPZ: +4.35, p=4e-7 — robust, BUT unambiguous versions contain the
  disambiguating comma inside the fit window (33% of unamb windows contain a
  punct-final state vs 0% amb); given punct tokens are rest states, part of
  this effect may be punctuation asymmetry. Needs a punct-matched control.
- **MVRR: −1.72, p=.003 — REVERSED.** "The horse raced…"-type items show
  *lower* TEE at disambiguation in the ambiguous condition. Contradicts the
  manuscript's blanket "higher extrapolation error across all configurations"
  sentence (which reports no numbers).

## Implications for the Cognition submission

- The paper survives the sink at its central configuration — no withdrawal
  scenario — but the Methods must state presentation format and report this
  control, and the w=5/7 and L12 analyses must be rerun clean or dropped.
- The validation section should report numbers per construction and address
  the MVRR reversal and the NPZ comma confound rather than the current
  unquantified blanket claim.
- Caveat: this is a reconstruction of the paper's spec from its text
  (word-level windows, final-subword states, disambiguating word only, no
  ROI 1–2 spillover); if the original pipeline differed (token-level windows,
  BOS handling, ROI pooling), rerun this script with that spec before editing
  the manuscript.
