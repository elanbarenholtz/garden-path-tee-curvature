# Reconciling the ZuCo null with the Natural Stories effect (2026-07-27)

Subject-level inference throughout (one beta per participant, group Wilcoxon),
matching the ZuCo standard. Script `ns_zuco_reconcile.py`.

## Headline: it is power, quantitatively

Resampling 10 participants at a time from the 171 Natural Stories readers and
running the same group test ZuCo ran:

| sample | detection rate at n = 10 |
|---|---|
| full corpus | **41.8%** |
| ZuCo-like slice | 22.4% |

A 10-subject study would miss this effect **more than half the time**. ZuCo's
observed values — FFD p = .084, TRT p = .065, both trending positive, 0/10
individually significant — are precisely what an underpowered true effect looks
like. This is a quantitative answer to "why didn't it replicate," not a
rhetorical one, and it can go in the paper as a sentence with a number attached.

## Position: real, and it matters

| slice | positive betas | mean β | Wilcoxon |
|---|---|---|---|
| first 5 words of a sentence | 79/168 | **−0.00219** | .187 (null) |
| first 10 words | 103/171 | +0.00169 | 5.8e-3 |
| beyond word 10 | 131/171 | **+0.00560** | 3.9e-15 |

The effect is absent — slightly negative — in the first five words of a sentence
and strong deep into one. This confirms the position profile found earlier, now
under subject-level inference. It is a genuine boundary condition and should be
reported: a three-word backward window is partly undefined or spans a sentence
boundary at those positions, which is also where the first-token geometry lives.

## My sentence-length hypothesis was wrong

I predicted the effect would be weaker in short sentences, since ZuCo uses short
isolated ones. The opposite is true:

| sentence length | mean β | Wilcoxon |
|---|---|---|
| ≤ 15 words | **+0.00810** | 1.6e-9 |
| 16–25 words | +0.00318 | 7.6e-5 |
| > 25 words | +0.00362 | 3.4e-9 |

Short sentences show the *strongest* effect. And the combined "most ZuCo-like"
slice (short sentences, first 10 words) is still clearly significant
(+0.0074, p = 2.3e-7). So stimulus length does not explain the ZuCo null and
should not be offered as an explanation — it is checkable, and a referee who
checks it will find the opposite.

What survives is: position within sentence matters, sentence length does not.

## What to write

1. Report the ZuCo null plainly.
2. Explain it with the power simulation — 42% detection at n = 10 — not with
   speculation about stimuli.
3. Report the position boundary condition on its own merits, since it is real
   and interesting, without leaning on it to explain ZuCo.
4. Do not claim short/isolated stimuli weaken the effect. They do not.

The remaining honest possibility, which cannot be settled with these data, is a
paradigm difference: self-paced reading forces a button press per word and is
sensitive to integration cost; free eye movement permits skipping, regression
and parafoveal preview. Worth one sentence as a hypothesis, flagged as such.
