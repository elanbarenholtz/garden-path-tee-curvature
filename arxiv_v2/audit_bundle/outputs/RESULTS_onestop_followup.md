# OneStop follow-up: the reversal shrinks a lot under a fair spec (2026-07-27)

Chasing the r = 0.80 surprisal discrepancy and the missing-context hypothesis.
Scripts: `onestop_context_tee.py`, output `onestop_ctx_log.txt`,
`onestop_final.txt`.

## Context is not the explanation

Natural Stories TEE used whole-story forward passes (1024-token chunks, stride
512); my first OneStop pass used isolated paragraphs. Recomputing OneStop with
article-level context (paragraphs of an article concatenated in order):

- **r(TEE isolated, TEE article-context) = 0.988** — context barely moves TEE
- r(OneStop surprisal, mine): 0.802 isolated → 0.812 with context
- no position-in-paragraph signature of a context mismatch

So the two pipelines do not differ meaningfully in context, and the surprisal
discrepancy is not a context effect. It remains unexplained — most likely a
different GPT-2 variant or a different word-level aggregation on their side.
It is worth one email to the authors, but it is not what is driving anything.

## Under a fair specification, the reversal largely dissolves

Progressive replacement of my pipeline choices with theirs, all with previous-word
controls (length, frequency, surprisal, dwell time):

| DV | my surprisal + isolated TEE | their surprisal + isolated TEE | their surprisal + context TEE |
|---|---|---|---|
| FFD | −0.00029 (.70) | +0.00030 (.58) | **+0.00061 (.27)** |
| GD | −0.00230 (.016) | −0.00108 (.35) | **−0.00058 (.71)** |
| TRT | −0.00522 (1.1e-6) | −0.00295 (.004) | **−0.00225 (.029)** |

Two of three measures go null once their surprisal and context-based TEE are
used. First-fixation duration even turns (non-significantly) positive.

**What survives:** total reading time, β = −0.0023, p = .029. Attenuated by more
than half from the first-pass estimate, and now at a p-value that would not
survive correction for three dependent measures × several specifications.

## Revised reading

My earlier framing — "a significant reversal at n = 180" — was too strong. What
the data support is:

1. **TEE does not predict eye movements in OneStop.** Two of three measures are
   null under the fair spec. This is a failure to replicate, not a reversal.
2. **There is a residual negative trend in total reading time**, which is the
   measure that includes regressions and re-reading. That is worth a sentence
   and worth understanding, not worth a headline in either direction.
3. **The self-paced result stands on its own** but now clearly does not
   generalise to eye movements. Two eye-tracking corpora (ZuCo, OneStop) fail to
   show the effect; ZuCo underpowered, OneStop well-powered and null-to-slightly-
   negative.

I overstated the first-pass result. The specification I ran initially lacked
previous-word controls and used my own surprisal; both mattered. The corrected
picture is less dramatic and more ordinary: an effect that appears in self-paced
reading and does not appear in eye tracking.

## What this means for the paper

The claim "TEE indexes human processing cost" cannot be supported in general
form. What can be supported: TEE predicts self-paced reading time, robustly and
at the subject level, and does not predict eye-movement measures in two
independent corpora. That is a real and reportable pattern — self-paced reading
meters processing serially and is known to be more sensitive to integration
difficulty than first-pass fixation measures — but it is a narrower claim than
the arXiv paper makes, and it must be stated with the eye-tracking nulls in
plain view.

Framing B (model-internal geometry) remains unaffected and is now clearly the
stronger paper.

## Outstanding

- The r = 0.80 surprisal disagreement with OneStop's published values is still
  unexplained. Not load-bearing, but it should be resolved before citing their
  annotations.
- Skipping rate and regression probability were not analysed; they are the
  eye-tracking measures with no self-paced analogue and would sharpen the
  paradigm story.
