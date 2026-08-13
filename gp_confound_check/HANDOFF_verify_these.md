# Handoff: two claims about the garden-path analysis, and how to check them

For the session that ran the original analysis. Everything below concerns
`garden-path-p1/model_comparison_stats.py` and the Table 1 garden-path results
in arXiv 2606.05346. Nothing here concerns Natural Stories, which is a separate
pipeline and is not implicated.

Two of my earlier calls in this session were wrong and have been retracted —
listed at the bottom so they don't get inherited.

---

## CLAIM 1 — The published models never include the disambiguating word

**Statement.** `model_comparison_stats.py` filters to ROI ∈ {0,1,2} and *then*
computes `prev_log_RT` with `groupby(['participant','Sentence'])['log_RT'].shift(1)`.
ROI 0 is the first row of every group, so it becomes NaN and is removed by the
`dropna` that builds `base`. The published N = 95,173 is ROI 1 + ROI 2 only.
The Methods describe the critical region as "the disambiguating word and two
spillover positions (ROI codes 0, 1, and 2)".

**How to check — no GPT-2 needed, pure arithmetic, ~10 seconds:**

```python
import pandas as pd, numpy as np
rt = pd.read_csv('ClassicGardenPathSet.csv')
rt['participant'] = rt['MD5']
rt = rt[(rt.RT > 100) & (rt.RT < 5000)].copy()
rt['log_RT'] = np.log(rt.RT)

roi = rt[rt.ROI.isin([0,1,2])].copy()                      # filter FIRST (as in the script)
roi = roi.sort_values(['participant','Sentence','WordPosition'])
roi['prev_log_RT'] = roi.groupby(['participant','Sentence'])['log_RT'].shift(1)

print(len(roi))                                             # 142,886  (full ROI 0-2 pool)
print(roi.prev_log_RT.notna().sum())                        # 95,173   <-- published N
print(roi[roi.prev_log_RT.notna()].ROI.value_counts())      # only ROI 1 and ROI 2
```

**What I get:** 95,173 exactly, composed of ROI 1 = 47,532 and ROI 2 = 47,641.
Zero ROI 0.

**What would falsify it:** any ROI-0 rows surviving the dropna, or a different
version of the script (one that computes `prev_log_RT` before filtering, or that
includes a log-frequency control) that also lands on N = 95,173. The committed
script has no frequency control, but the paper says the control model "included
log word frequency" — so a later version may exist. **If it does, please check
whether it has the same shift-after-filter ordering.** That is the whole claim.

**Fix if confirmed:** either compute `prev_log_RT` on the full sentence before
filtering (ROI 0 then survives), or restate the region as spillover-only.

---

## CLAIM 2 — TEE's effect has opposite signs at ROI 1 and ROI 2

**Statement.** Fit the same model separately per position and the coefficient on
TEE reverses within the critical region, so the pooled estimate is not a stable
description.

Original spec, L6 w=3, isolated presentation, controls = word length, word
position, previous log RT, surprisal; mixedlm random intercept by participant,
`reml=False`; `prev_log_RT` from the full sentence so ROI 0 has data.

| ROI | n | β TEE | p | β surprisal | p |
|---|---|---|---|---|---|
| −1 | 47,645 | −0.0054 | 2.3e-4 | −0.0004 | .77 |
| 0 (disambiguation) | 47,610 | −0.0034 | **.084 n.s.** | +0.0341 | 1.8e-65 |
| 1 (spillover 1) | 47,614 | **−0.0085** | 6.6e-5 | +0.0405 | 1.8e-79 |
| 2 (spillover 2) | 47,647 | **+0.0102** | 5.5e-10 | −0.0022 | .19 |
| 3 (outside region) | 47,669 | +0.0207 | 2.4e-44 | +0.0125 | 2.3e-19 |

Formal test, ROI 0/1/2 pooled with ROI as a factor:
`z_tee × C(ROI)` interaction **χ²(2) = 36.8, p = 1.0e-8**.

Pooling comparison on identical rows (ROI 1+2):
- no ROI term (as published): β = **+0.0079**, p = 2.5e-9
- ROI as a factor: β = +0.0064, p = 6.1e-6
- the pooled estimate exceeds both constituent position estimates

**How to check.** Recompute TEE from `window_sweep.py` (GPT-2 small, layer 6,
`tokenizer(sentence)` with no context, word state = last subword, linear fit over
the 3 preceding word states, extrapolate one step, Euclidean distance), merge on
(item, Type, WordPosition), then fit per ROI. My implementation is
`gp_roi_signflip.py` in this folder; output in `roi_signflip_output.txt`.

**Please verify with a method that does not share my assumptions**, since the
sign is the whole claim — e.g. by-item aggregation (mean logRT per item/word,
correlate with TEE across the 144 sentences, per ROI), or per-participant
within-subject correlations, or a permutation test. Also worth trying to break
it: leave-one-item-out, trimming extreme TEE, dropping the longest RTs.

**Ruled out as explanations** (each checked): log frequency (flip survives,
ROI 1 −0.0085→−0.0071, ROI 2 +0.0102→+0.0060); punctuation (0% punct-final words
at these positions); the attention sink (w=3 windows never reach token 0 here);
construction type (no single construction drives it).

**Also worth knowing:** r(TEE, surprisal) = +0.42 at ROI 0 in these stimuli,
versus the r = .044 orthogonality reported for Natural Stories. And the largest
TEE effect anywhere is at ROI 3, outside the analyzed region.

---

## On the attention sink — mostly a false alarm here

The sink is real (token-0 norm ≈ 36× interior at layer 6) but does not threaten
this table. At L6/w=3, 0% of critical-region fit windows reach token 0; the
measure is bit-identical with token 0 excluded. Only w=7 is exposed (35.5% of
rows) and it still survives cleaning (ΔAIC +26.4 → +18.9, p = 5e-6).

Recommendation: report the control in Methods and state the presentation format
(the paper never says the stimuli were run as isolated sentences), but no result
needs to be withdrawn on sink grounds.

---

## Retractions — two things I said earlier in this session that were wrong

1. **"Drop M5 (L6 w=7), it's sink-driven."** Wrong. That came from a sample that
   included ROI 0, where w=7 is 44% sink-exposed. On the published sample it
   survives cleaning. Keep it.
2. **"Restoring ROI 0 flips the sign, so ROI 0 is the problem."** Wrong
   diagnosis. Pooling ROI 0+1+2 goes negative because two of three positions are
   negative. The actual issue is that the positions do not share a sign — the
   ROI-1-vs-ROI-2 disagreement above.

Both errors came from analyzing a reconstruction of the pipeline before the
original code was located. Everything in Claims 1 and 2 above is computed from
the original scripts and the real data.

---

## Files in this folder

- `gp_sink_check.py` / `RESULTS_gp_sink_check.md` — sink diagnostic on the 24 items
- `gp_table1_exact.py` / `RESULTS_table1_exact.md` — Table 1 under the original spec
- `gp_roi_signflip.py` / `RESULTS_roi_signflip.md` — the per-position analysis
- `table1_exact_output.txt`, `roi_signflip_output.txt` — raw output
