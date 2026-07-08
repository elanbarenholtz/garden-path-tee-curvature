# Spillover analysis, typed by the par/perp decomposition (locked sample 8a6087341e)
RT freeze lifted (P1 punctuation control complete). DV = per-word mean log RT
(self-paced reading, 848,875 obs filtered 100-3000 ms, averaged over 180
participants). Predictors z-scored (ddof=0), entered at lag 0 (on-word), lag 1
(previous word), lag 2. Controls: prev-word mean logRT (autocorrelation),
position, C(story_id). Cluster-robust SE by sent_uid. n=9,820 (first 2 words/
story drop for want of lags). Raw output: p_spillover_output.txt.

Pre-committed hypothesis: perp (lateral / branch change) spills to +1; par
(along-heading / pace) stays local. RESULT: hypothesis reversed (see below).

## Coefficients (beta on z-scored predictor; * = p<.05)

FULL MODEL (R^2=0.726):
| predictor  | L0 on-word        | L1 spillover      | L2                |
|------------|-------------------|-------------------|-------------------|
| tee3_perp  | +0.0045 (4e-12)*  | +0.0021 (1e-02)*  | -0.0031 (4e-05)*  |
| tee3_par   | +0.0023 (2e-03)*  | +0.0040 (7e-08)*  | -0.0008 (n.s.)    |
| surprisal  | +0.0074 (4e-22)*  | +0.0109 (7e-47)*  | +0.0009 (n.s.)    |

PUNCT-FREE (current word not punct-final; R^2=0.730, n=8,657):
| predictor  | L0 on-word        | L1 spillover      | L2                |
|------------|-------------------|-------------------|-------------------|
| tee3_perp  | +0.0034 (4e-07)*  | +0.0012 (n.s.)    | -0.0028 (3e-04)*  |
| tee3_par   | +0.0038 (1e-06)*  | +0.0038 (5e-07)*  | -0.0007 (n.s.)    |
| surprisal  | +0.0062 (5e-20)*  | +0.0101 (8e-47)*  | +0.0009 (n.s.)    |

## Findings (punct-free = trustworthy)
1. BOTH channels predict RT on-word (perp L0 +0.0034, par L0 +0.0038, both
   p<1e-6). The internal geometric decomposition is behaviorally real, not an
   internal-representation curiosity. Both survive punctuation control.
2. They differ in TIMING. par spills to +1 (L1 +0.0038, p=5e-7, as large as its
   on-word effect, punct-clean). perp does NOT spill (L1 n.s. once punctuation
   is controlled): it is resolved on-word.
   -> HYPOTHESIS REVERSED: the along-heading/pace channel carries forward; the
      lateral/branch channel is immediate. (Tentative reading: a bearing change
      is a discrete on-word event; an along-heading over/undershoot is a graded
      mismatch registered only when the next word confirms it. par/perp
      semantics remain fragile, hold loosely.)
3. FOOTPRINT IS SHORT. Nothing positive survives at L2 for either channel. The
   L2 NEGATIVES (perp -0.0028; also word_length -0.0055, log_freq -0.0039,
   punct -0.0024) are autocorrelation artifacts of the strong prev_logRT
   control (word_length/log_freq two-back cannot truly speed reading), not
   substantive. Disregard L2.

## Bearing on the short- vs long-range question
On self-paced RT, out to 2 lags, with autocorrelation controlled, the behavioral
cost of both channels is confined to a ~1-word window (on-word + at most one
word of spillover). This LEANS toward short-range / local recalculation and
AGAINST a multi-word behavioral wake. Caveats that bound this:
- SPR truncates spillover (no regressions); eye-tracking would test longer tails.
- Only 2 lags; a uniform lag regression on naturalistic text will not capture
  event-specific long-range effects (e.g. garden-path reanalysis at +3/+4).
- prev_logRT is a conservative control that shrinks genuine spillover.
- Complementary probe not yet run: model-internal downstream perturbation
  (hidden-state wake), which could show longer model-side propagation even where
  SPR RT does not.

## Validation / provenance
Surprisal shows the classic self-paced spillover profile (L1 +0.0109 > L0
+0.0074, L2 null): the lag machinery is behaving correctly. Merge to RT: 9,840/
9,840 on (story,zone), word strings 100% agree, zone==word_idx+1. Curvature/
decomposition on hidden states validated identical to the locked sample.
