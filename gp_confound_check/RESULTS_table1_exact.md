# Table 1 under the original spec, with sink controls (2026-07-27)

Now run against the real pipeline (`garden-path-p1/model_comparison_stats.py`
and `window_sweep.py`), not a reconstruction: mixedlm with a by-participant
random intercept, ML fit, controls = word length + word position + previous log
RT, TEE = word-level states at the last subword, linear fit over the k preceding
word states, one-step extrapolation, Euclidean error. Script
`gp_table1_exact.py`, output `table1_exact_output.txt`.

**Sample reproduces exactly: N = 95,173.** Betas are positive, matching the
published +0.005 direction. (My earlier reconstruction's negative sign came from
including ROI 0 and a frequency control — see below.)

## Finding 1: the published RT models exclude the disambiguating word

`model_comparison_stats.py` filters to ROI 0/1/2 and *then* computes
`prev_log_RT` by shifting within (participant, Sentence). ROI 0 is the first row
of every group, so it gets NaN and is dropped at the `dropna`. The published
N = 95,173 is exactly ROI 1 (47,532) + ROI 2 (47,641) — the total ROI 0/1/2 pool
is 142,886.

The Methods say the critical region "included the disambiguating word and two
spillover positions (ROI codes 0, 1, and 2)". For the RT models that is not what
was fit. **The garden-path reading-time effect is a spillover effect**, measured
one and two words after disambiguation, with the disambiguating word absent.

This is fixable two ways — restate the region as spillover-only, or take
prev_log_RT from the full sentence so ROI 0 survives — but it cannot stay as is.

## Finding 2: restoring ROI 0 flips the sign

| | ROI 1+2 (published) | ROI 0+1+2 (restored) |
|---|---|---|
| L6 w=3 β | **+0.0080** (p = 1.4e-9) | **−0.0081** (p = 1.9e-14) |

At spillover positions, higher TEE predicts *longer* reading time. At the
disambiguating word itself, higher TEE predicts *shorter* reading time, about as
strongly. The published positive effect exists only because the negative-signed
positions were dropped. This needs an explanation before the paper goes out —
it is not a sink artifact (0% window exposure at w=3 either way) and it is not
small.

## Finding 3: the sink barely matters for the published table

Because ROI 0 is excluded, the critical rows sit further from the sentence start
than I assumed, and sink exposure largely disappears.

| config | window touches word 0 | isolated (published) | prefix | drop-tok0 |
|---|---|---|---|---|
| L6 w=3 | 0.0% | +34.7 | +56.8 | +34.7 (identical) |
| L12 w=5 | 0.0% | +11.3 | +42.9 | +11.3 (identical) |
| L6 w=5 | 0.0% | −0.7 (n.s.) | −1.9 (n.s.) | −0.7 (n.s.) |
| L6 w=7 | 35.5% | +26.4 | +39.6 | **+18.9, p = 5e-6** |

Every significant configuration stays significant under clean handling, and two
get stronger with context prepended. **My earlier conclusion that M5 (w=7) should
be dropped was wrong** — that was based on a sample including ROI 0, where w=7 is
44% exposed and does collapse. On the published sample it survives at +18.9.

So: no withdrawal, no dropped rows on sink grounds. Report the control, state
the presentation format, and note that w=7 attenuates ~30% when the first token
is excluded.

## Discrepancies worth resolving

- ΔAIC values partially reproduce: L6/w5 (−0.7 vs published 0.0) and L6/w7
  (+26.4 vs +31.4) are close; L6/w3 (+34.7 vs +10.7) and L12/w5 (+11.3 vs +56.4)
  are not. Most likely cause: the committed script's controls do **not** include
  log word frequency, while the paper text says the control model "included log
  word frequency" and Table 1 labels M0 "Controls (incl. log freq)". There is
  probably a later version of the script that was actually used for the table.
  Worth locating — it changes two of four published ΔAICs.
- `zou_stimuli.csv` and the Matters Arising drafts are in the same repo; the
  withdrawal there was the right call and is unaffected by any of this.
