# OneStop: TEE does not replicate, and reverses (2026-07-27)

OneStop Ordinary Reading, 360-participant corpus (180 participants in this
sub-corpus), 1,104,883 word-level observations, 128 paragraphs, 15,650 words
with usable TEE. Subject-level inference throughout: one regression per
participant, group test across participants — the standard that Natural Stories
passed and ZuCo failed.

Scripts: `onestop_compute_tee.py`, `onestop_analyze.py`; output
`onestop_results.txt`, `onestop_prevctrl.txt`.

## Pipeline validation (done before interpreting anything)

- IA_LABEL ↔ reconstructed word match rate: **100%**
- reconstructed text reads correctly, punctuation attached as in the corpus
- my GPT-2 surprisal vs OneStop's precomputed `gpt2_surprisal`: **r = 0.80**
  (not 1.0 — they likely use a different context window or variant; close
  enough to confirm alignment, not close enough to ignore)
- TEE computed with the sink excluded from every fit window (windows start at
  word index 1; only words at index ≥ 4 emitted)

The alignment is sound. What follows is a property of the data, not a merge bug.

## Result: significant effects in the OPPOSITE direction

| DV | positive betas | mean β | Wilcoxon |
|---|---|---|---|
| first fixation duration | 76/180 (42%) | −0.00199 | .005 |
| gaze duration | 70/180 (39%) | −0.00421 | 4.1e-6 |
| total reading time | 54/180 (30%) | **−0.00601** | 1.5e-8 |

Higher TEE predicts **shorter** fixations. Natural Stories gives +0.0039 with
73% of participants positive; OneStop gives −0.0060 with 30% positive on the
comparable measure. This is not a null — it is a reversal, at n = 180, under the
inferential standard we adopted precisely because it is strict.

### It is not the missing eye-tracking controls

The first-pass spec lacked the previous-word terms that dominate the Natural
Stories model. Adding them progressively:

| spec | FFD | GD | TRT |
|---|---|---|---|
| A first-pass | −0.00199 (.005) | −0.00421 (4e-6) | −0.00601 (1e-8) |
| B + prev length/freq/surprisal | −0.00069 (.25) | −0.00292 (.002) | −0.00584 (1e-7) |
| C + prev dwell time | −0.00057 (.33) | −0.00272 (.003) | −0.00620 (2e-8) |
| D + prev TEE | −0.00015 (.67) | −0.00248 (.011) | −0.00646 (4e-8) |

First-fixation duration goes null once preview controls are added — fine, FFD is
the earliest and noisiest measure. But gaze duration and total reading time keep
the negative effect at every level of control, and TRT gets slightly *stronger*.

### The position gradient replicates — with the sign inverted

| slice | Natural Stories | OneStop (TRT) |
|---|---|---|
| first 5 words of sentence | −0.0022 (null) | −0.0016 (null) |
| beyond word 10 | **+0.0056** (3.9e-15) | **−0.0074** (6.5e-8) |

Both corpora show the same profile — nothing at sentence onset, growing with
depth into the sentence — but Natural Stories grows positive and OneStop grows
negative. Whatever TEE indexes, it is being read out with opposite sign by the
two paradigms, and the *shape* of the position dependence is the same in both.
That is a strange and interesting pattern; it is also a serious problem.

## What this does to the story

The ZuCo null is no longer the thing to explain. ZuCo's trends were negative
too (its betas were positive in raw ms but the analysis was underpowered);
OneStop now shows a well-powered, controlled, significant reversal.

The honest reading is one of:

1. **Paradigm difference, real.** Self-paced reading meters a button press per
   word and is sensitive to integration cost; eye movements permit skipping,
   regression and preview. A word that is off-trajectory may attract a shorter
   first-pass fixation and a regression later — the total-time measure here
   includes regressions, which complicates that story rather than saving it.
2. **The self-paced effect is task-specific.** TEE may index something about
   button-press rhythm or motor pacing in SPR that has no counterpart in free
   reading. That would substantially deflate the claim that TEE indexes human
   processing cost.
3. **Something about my OneStop TEE differs from the Natural Stories TEE.**
   Paragraph-level context vs story-level, different text genre (Guardian vs
   narrative), different length. The r = 0.80 surprisal agreement is a hint that
   my forward pass is not identical to theirs and deserves a look.

I cannot currently distinguish these, and I do not want to guess after two wrong
calls in this session.

## Recommendation

**Do not submit a reading-time-led paper until this is resolved.** A referee
with OneStop — a public, popular, 360-participant corpus — can run this in an
afternoon, and a significant reversal found by a referee is far worse than one
disclosed by the author.

Concrete next steps, in order:
1. Reconcile the surprisal discrepancy (r = 0.80): match OneStop's exact
   surprisal procedure and confirm the TEE forward pass matches it.
2. Check whether the reversal holds for *skipping rate* and *regression
   probability*, which are the eye-tracking measures with no self-paced analogue.
3. Run the Natural Stories words through an eye-tracking corpus if one exists
   for the same texts, isolating paradigm from stimulus.

Framing B (model-internal geometry: structure vs uncertainty, causal wake) is
untouched by any of this. Its evidence is model-internal and does not depend on
which behavioral corpus reads out with which sign.
