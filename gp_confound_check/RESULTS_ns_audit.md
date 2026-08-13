# Natural Stories audit — looking for the garden-path failure mode (2026-07-27)

Checked the Natural Stories reading-time pipeline for the *class* of error that
broke the garden-path analysis. Run on the locked sample (8a6087341e, 9,840
words) merged to `processed_RTs.tsv` (848,875 rows, 180 participants),
replicating the prep in `garden-path-p1/ns_crossed_re.py`.
Scripts: `ns_audit.py`, output `ns_audit_output.txt`, `ns_pos_output.txt`.

## Verdict: the Natural Stories result is sound. It does not have the bug.

| check | result |
|---|---|
| A. merge integrity | **clean** — 0 duplicate (story, zone) keys; 848,875 rows in, 848,875 out, no multiplication; 4.2% unmatched (words outside the locked sample, expected) |
| B. lagged control | **minor, harmless** — 99.4% of `prev_log_RT` values are the genuinely adjacent word; 4,868 rows (0.6%) point 2+ zones back because the RT filter ran first. Repairing it changes nothing: ΔAIC 109.8 → 107.0, β +0.00351 → +0.00344 |
| C. sample equality | **clean** — M1 and M2 are fit on identical rows, so the AIC comparison is legitimate |
| D. heterogeneity | **passes** — 9/10 stories positive; position effect varies in size but not in sign except at sentence-initial words |

The critical contrast with the garden-path analysis: there, filtering happened
*before* the lag was computed and deleted an entire condition (all ROI-0 rows).
Here the same ordering costs 0.6% of rows and mislabels rather than deletes.
Repairing it moves the headline by 3 AIC units out of 110.

## Effect size on the locked sample

ΔAIC = **109.8**, β(TEE) = **+0.0035**, p = 4.0e-26, N = 813,621.

This is much stronger than the ΔAIC = 2.5 reported in the paper (Table 6,
GPT-2 Small), which came from `ns_crossed_re.py` with β = +0.00063, p = .034.
The locked-sample rebuild gives an effect five times larger and overwhelmingly
significant. Worth understanding which is right before either number is
published — most likely the locked sample has better word alignment (the
rebuild was specifically constructed to fix alignment bugs), but this should be
run down.

For scale, in the same model: β(surprisal) = +0.0112, β(log_freq) = +0.0072,
β(prev_log_RT) = +0.1396. TEE is about a third the size of surprisal — a real
but second-order effect, consistent with what the extensions writeups say.

## One thing to disclose, not fix

The effect grows with distance into the sentence and reverses at sentence-initial
words:

| position from sentence start | n | β | p |
|---|---|---|---|
| 0–2 | 100,705 | **−0.0027** | .022 |
| 3–5 | 100,948 | +0.0031 | 9.8e-4 |
| 6–10 | 157,927 | +0.0053 | 6.6e-14 |
| 11–20 | 253,602 | +0.0033 | 7.0e-9 |
| 21+ | 200,439 | +0.0080 | 9.6e-33 |

TEE × position interaction: χ²(4) = 220.8, p = 1.3e-46.

This is *not* the garden-path problem. There, two adjacent positions inside a
three-word region disagreed and the pooled estimate exceeded both — the number
described nothing real. Here 4 of 5 bins agree, the pooled estimate sits inside
the range of its parts, and the one negative bin is sentence-initial words where
a 3-word backward window is partly undefined or spans a sentence boundary. That
is an interpretable boundary condition, and arguably the same first-token
geometry the sink work is about.

Recommended handling: report the position profile, exclude or flag
sentence-initial words, and note that the effect strengthens mid-sentence. A
reviewer who finds this unreported will be far more troubled than one who reads
it in the paper.

## Still outstanding

- Reconcile ΔAIC 2.5 (paper) vs 109.8 (locked sample). Do not publish either
  until it is known why they differ.
- The `word_type` random-effect robustness check in `ns_crossed_re.py` never
  completed — `ns_crossed_re_results.csv` has only two rows, and the lexical
  baseline model is the missing one. Since word frequency is the dominant
  predictor of TEE, that is the check most worth having.
- The tee_vs_curvature and extensions pipelines have not yet been audited to
  this standard (task 7).
