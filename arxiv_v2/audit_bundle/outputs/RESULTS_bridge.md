# Bridge test: does uncertainty now predict extrapolation failure next? (2026-07-27)

Locked sample 8a6087341e, GPT-2 Small layer 6, 9,830 adjacent word pairs,
position + story FE, cluster-robust SEs by sentence.
Script `bridge_entropy_to_tee.py`.

The prediction, from taking King/Fedorenko/Hosseini's mechanism seriously: if a
bendy path leaves the model uncertain where to go next, then uncertainty at
word t should forecast a larger extrapolation error at word t+1. Neither paper
makes this prediction.

## 1. The bridge holds

| model | β | p |
|---|---|---|
| entropy(t−1) → TEE(t), position + story FE | +0.137 | 9e-43 |
| + punctuation at t and t−1 | +0.134 | 8e-47 |
| + lexical properties of word t | +0.130 | 2e-57 |
| **+ surprisal at t (strict)** | **+0.123** | 3e-53 |
| + surprisal at t−1 as well | +0.056 | 4e-08 |

The effect survives controlling how surprising word t actually turned out to be
(+0.123). That matters: it is not merely that uncertain contexts contain
surprising words. Uncertainty *before* the word arrives forecasts how far the
representation lands from its extrapolated heading, over and above the word's
own surprisal.

Adding surprisal at t−1 cuts it to +0.056 (still p = 4e-8). Entropy and
surprisal at the same position share variance by construction, so this is the
conservative bound rather than a refutation.

**This links the two papers empirically: their prospective measure predicts my
retrospective one.**

## 2. It is specifically the along-heading component

| outcome at word t | β from entropy(t−1) | p |
|---|---|---|
| **tee3_par** (along-heading: overshoot/undershoot) | **+0.149** | 3e-69 |
| **tee3_perp** (lateral: veering onto a new direction) | +0.005 | .52 (null) |

A clean dissociation. Uncertainty forecasts *mis-scaling of the step along the
direction of travel* — the model does not know how far to go — and has nothing
to say about whether the trajectory turns.

This is the sharpest result here. It says uncertainty and direction-change are
different things, which is exactly the structure/uncertainty split, now expressed
predictively across adjacent positions rather than as a same-position
correlation.

## 3. Their measure forecasts TEE in the *opposite* direction

| model | β | p |
|---|---|---|
| curvature_3(t−1) → TEE(t) | **−0.151** | 2e-58 |
| curvature_1(t−1) → TEE(t) | **−0.225** | 1e-142 |
| joint: entropy(t−1) coefficient | +0.114 | 3e-44 |
| joint: curvature_3(t−1) coefficient | −0.137 | 2e-47 |

Both survive together with opposite signs. If the chain were simply
curvature → uncertainty → extrapolation failure, curvature should forecast TEE
*positively*. It does the reverse.

**Important caveat: this may be mechanical rather than meaningful.** A highly
bent recent path produces a fitted direction with a small norm — the steps
partly cancel — so the extrapolation lands near the recent centroid and cannot
overshoot far. A straight path yields a long extrapolation vector with more room
to miss. So curvature and TEE are plausibly coupled through the geometry of the
fit itself, independent of anything about language or uncertainty.

This needs a null model before it is interpreted: simulate random walks with
matched step-size distributions and varying curvature, and check whether the
negative curvature→TEE relationship appears there too. If it does, it is an
artifact of the measures and should be reported as such. **Do not put this in a
paper before running that check.**

## 4. Same-position relationships are control-sensitive — handle with care

| specification | r or β for TEE × entropy |
|---|---|
| partial r, position + story FE | **+0.051** |
| partial r, + punctuation | +0.050 |
| regression, + punctuation + frequency + length | **−0.127** |

Adding word frequency flips the sign. Given r(TEE, log frequency) = −0.438,
frequency is a large shared influence on both measures. Any claim about the
same-position TEE–entropy relationship depends on the control set and should not
be made without stating it. This also bears on the v2 abstract: the honest
statement is that TEE and entropy are weakly and unstably related, not that they
are independent.

## 5. What to take from this

**Solid:** uncertainty at one word forecasts extrapolation error at the next
(+0.123 with surprisal controlled), and it does so entirely through the
along-heading channel, not the lateral one.

**Interesting but unverified:** curvature forecasts extrapolation error
negatively. Likely mechanical; test with a null model first.

**Cautionary:** the same-position TEE–entropy correlation flips sign with
frequency controls, so the "nearly orthogonal to surprisal" framing was fragile
in more ways than the r = .31 finding already showed.

## 6. Why this is worth writing up

It converts the relationship between the two papers from a rhetorical comparison
into a measured one. Their claim is that bendy paths make the model uncertain.
The bridge shows that when the model is uncertain, the representation
subsequently fails to land where its heading pointed — and specifically fails by
mis-scaling along the heading rather than by turning. That is a mechanistic
elaboration of their result using the more direct instrument, and it belongs in
the geometry paper as a section rather than in a dispute.
