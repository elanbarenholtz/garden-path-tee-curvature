# Table 1 rerun with sink-clean TEE (2026-07-27)

SAP ClassicGP self-paced reading, N = 2,000 participants, 24 items × 6 types,
critical region ROI 0/1/2. Controls: word length, word position, previous log
RT, log word frequency (all z-scored); outcome log RT; surprisal computed under
the matching presentation. Each configuration uses its own sample — the rows
where that measure is defined under all three presentations — because a global
intersection deletes the sentence-initial rows, which is exactly where the sink
bites. Script `gp_table1_rerun.py`, raw output `table1_rerun_output.txt`.

Presentations: **A** isolated sentence (presumed original), **B** neutral prefix
prepended, **C** isolated with word 0 excluded from fit windows.

## Reconstruction fidelity

Participant-demeaned M1 (surprisal over frequency controls) gives ΔAIC = **−2.0,
p = .84** against the paper's **−1.9, p = .71** — the baseline reproduces almost
exactly, and only under participant-level structure with isolated presentation.
That is good evidence the pipeline and the presentation assumption are right.
The individual TEE configurations do **not** reproduce numerically (see below),
and the L6/k=3 coefficient comes out negative here vs +0.005 in the paper, so
treat absolute values as a reconstruction, not a replication. The
presentation-to-presentation *contrasts* — same rows, same controls, only the
sink handling changes — are the trustworthy part.

## Sink exposure per configuration

| config | rows whose window touches word 0 | r(isolated, droptok0) | r(isolated, prefix) | mean TEE isolated → clean |
|---|---|---|---|---|
| L6 k=3 | **0.0%** | 1.000 | 0.984 | 94.9 → 94.9 |
| L12 k=5 | 7.2% | 0.883 | 0.712 | 50.2 → 48.4 |
| L6 k=5 | 7.2% | 0.265 | **−0.067** | 153.0 → 74.5 |
| L6 k=7 | **43.8%** | 0.192 | **−0.030** | 409.4 → 69.4 |

At w=5 and w=7 the isolated measure is essentially *uncorrelated* with its own
clean counterpart. It is not a noisy version of the intended quantity; it is a
different quantity, dominated by distance to a 36×-norm outlier.

## ΔAIC for the TEE term (over controls + surprisal)

Participant-demeaned models; OLS in the raw output tells the same story.

| config | A isolated | B prefix | C droptok0 | verdict |
|---|---|---|---|---|
| L6 k=3 | +102.5 | +109.2 | +102.5 | **unaffected — sink-immune by construction** |
| L12 k=5 | −0.1 (n.s.) | +67.9 | +35.1 | **survives; stronger when cleaned** |
| L6 k=5 | +90.2 | −0.4 (n.s.) | +17.2 | **mostly artifact** |
| L6 k=7 | −1.0 (n.s.) | −0.6 (n.s.) | −1.7 (n.s.) | **nothing there under any handling** |

## What this means for the manuscript

1. **The headline configuration is safe.** L6/k=3 windows never reach word 0 —
   0.0% exposure, r = 1.000 with the drop-token-0 version. Its RT contribution
   is large and unchanged under every presentation. Model M2 needs no revision
   on sink grounds.
2. **M5 (L6, w=7, paper ΔAIC = +31.4) should be dropped.** 44% of its rows are
   sink-exposed, its measure is uncorrelated with the clean version (r = −0.03,
   mean 409 vs 69), and it is null under every clean handling.
3. **M4 (L6, w=5) is not a usable robustness check.** The paper reported it as
   null (ΔAIC 0.0), which happens to be the right conclusion, but for the wrong
   reason — in this reconstruction the isolated version looks strong (+90) and
   collapses to null once cleaned. Either way it should not be cited as
   independent support.
4. **M3 (L12, w=5, paper ΔAIC = +56.4) survives and improves.** Cleaning makes
   it stronger (+67.9 with prefix), so the strongest RT result is not a sink
   artifact. It is, however, the configuration with the largest gap between
   presentations, so report which one was used.
5. **Methods must state the presentation format.** The paper never says whether
   garden-path stimuli were run in isolation. Given that w=5/w=7 results depend
   entirely on that choice, it cannot stay implicit.

## Caveats

- Reconstruction, not the original pipeline: the surprisal baseline matches the
  paper closely but the TEE coefficients do not, including a sign difference at
  L6/k=3. Rerunning with the original garden-path code (not yet located) is the
  right next step before editing the manuscript.
- Sample is 142,681 (k=3/k=5) or 102,290 (k=7) ROI 0–2 observations vs the
  paper's 95,173; the paper applied additional exclusions not documented in the
  text.
- Participant-demeaning approximates a by-participant random intercept; it does
  not include by-item random effects, which the paper notes absorb much of the
  TEE variance at the disambiguation point.
