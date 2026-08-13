# The sign flip: it is position heterogeneity, not the disambiguating word (2026-07-27)

Original spec throughout (mixedlm, by-participant random intercept, ML; controls
= word length, word position, previous log RT, surprisal; TEE = L6 w=3, isolated
presentation). `prev_log_RT` taken from the full sentence so ROI 0 survives.
Script `gp_roi_signflip.py`, output `roi_signflip_output.txt`.

## Per-position coefficients

| ROI | n | β TEE | p | β surprisal | p |
|---|---|---|---|---|---|
| −2 | 47,642 | −0.0051 | .012 | +0.0029 | .036 |
| −1 | 47,645 | −0.0054 | 2.3e-4 | −0.0004 | .77 |
| **0 (disambiguating word)** | 47,610 | **−0.0034** | **.084 (n.s.)** | +0.0341 | 1.8e-65 |
| **1 (spillover 1)** | 47,614 | **−0.0085** | **6.6e-5** | +0.0405 | 1.8e-79 |
| **2 (spillover 2)** | 47,647 | **+0.0102** | **5.5e-10** | −0.0022 | .19 |
| 3 (outside region) | 47,669 | +0.0207 | 2.4e-44 | +0.0125 | 2.3e-19 |

TEE × ROI interaction across the critical region: **χ²(2) = 36.8, p = 1.0e-8**.
The effect is not homogeneous across ROI 0/1/2 — it reverses between spillover 1
and spillover 2.

## What this means

1. **At the disambiguating word, TEE contributes nothing** once surprisal is in
   the model (p = .084, and negative in direction). Surprisal is doing all the
   work there (β = +0.034, p = 1.8e-65). The paper's framing — that TEE captures
   processing cost at the point of reanalysis — is not supported at the point of
   reanalysis.
2. **The published positive effect comes from ROI 2 alone.** At ROI 1 the
   coefficient is *negative* and significant (−0.0085); at ROI 2 it is positive
   (+0.0102). Pooling ROI 1+2 without a ROI term yields +0.0079, which is larger
   than either constituent estimate — the pooled number is partly between-position
   variance, not a within-position relationship. Adding ROI as a factor to the
   same rows drops it to +0.0064; splitting it shows the two halves disagree.
3. **My earlier "restoring ROI 0 flips the sign" was the wrong diagnosis.**
   Pooling ROI 0+1+2 goes negative because two of three positions are negative.
   The real problem is that the three positions do not share a sign, so *any*
   pooled estimate over this region is an artifact of which positions are in it.
4. **Pre-critical positions also show negative TEE effects** (ROI −2, −1), before
   any disambiguation has occurred. Whatever TEE is tracking here, it is not
   specific to reanalysis.
5. **The largest effect is outside the critical region** (ROI 3, +0.0207,
   p = 2.4e-44), which the paper never examined.

## Not explained by

- **Frequency:** adding log frequency barely moves any coefficient (ROI 1:
  −0.0085 → −0.0071; ROI 2: +0.0102 → +0.0060). The flip survives.
- **Punctuation:** 0% of words at any of these positions are punctuation-final.
- **The attention sink:** w=3 windows never reach word 0 at these positions.
- **Construction:** at ROI 0 no construction is individually significant
  (MVRR −0.0009, NPS −0.0057, NPZ +0.0080); the pattern is not one item type.

## What TEE is correlated with, position by position

| ROI | r(TEE, word length) | r(TEE, log freq) | r(TEE, surprisal) |
|---|---|---|---|
| −1 | −0.26 | −0.44 | +0.12 |
| 0 | −0.17 | −0.21 | **+0.42** |
| 1 | −0.29 | +0.13 | +0.26 |
| 2 | +0.12 | −0.25 | −0.06 |
| 3 | +0.38 | −0.37 | +0.34 |

TEE's relationship to lexical properties and to surprisal is itself unstable
across adjacent positions — which is the likely source of the coefficient
instability. Note r(TEE, surprisal) = +0.42 at ROI 0, far above the r = .044
orthogonality reported for Natural Stories; in this stimulus set at this
position the two measures are substantially entangled.

## Recommendation

This is more serious than the sink issue, and it is not fixable by a control.
The garden-path reading-time claim as stated does not hold: TEE does not predict
processing cost at the disambiguating word, and its apparent effect over the
spillover region depends on pooling two positions whose coefficients have
opposite signs.

Options, in order of preference:

1. **Report the position-resolved analysis honestly.** State that the effect is
   carried by later spillover (ROI 2–3) and is absent or reversed at
   disambiguation. This is a weaker but defensible claim, and the ROI 3 result
   suggests the region should have extended further.
2. **Drop the garden-path reading-time analysis** and keep garden paths as a
   measure-validation demonstration only (ambiguous vs unambiguous TEE, which
   does hold for NPS and NPZ though not MVRR).
3. Do not submit the current version — the pooled positive coefficient is not a
   stable description of the data.

The Natural Stories reading-time result is untouched by any of this.
