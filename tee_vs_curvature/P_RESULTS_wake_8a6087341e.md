# Causal downstream-wake (locked sample 8a6087341e, systematic subsample)
n = 1,633 target words (every 6th sample word with >=5 downstream words in-story).
Wake = layer-6 hidden-state perturbation at w+L when word w is ablated from the
model's context (attention mask zeroes w's keys; positions preserved). Causal
intervention, not attention weights. Mean relative wake by lag: L1 0.458, L2
0.243, L3 0.155, L4 0.112, L5 0.088 (decays with distance, as expected).
Analysis: wake_rel(w,L) ~ tee3_perp + tee3_par + surprisal(w) + word_length +
log_freq + has_trailing_punct + target(w+L) surprisal/length/freq + position +
C(story_id); z-scored; cluster-robust by sent_uid. Raw: p_wake_output.txt.

## Coefficients (beta; * p<.05)

FULL (punctuation controlled):
| lag | perp             | par              | surprisal(w)     |
|-----|------------------|------------------|------------------|
| L1  | +0.137 (1e-08)*  | -0.003 (n.s.)    | +0.118 (9e-06)*  |
| L2  | +0.100 (2e-03)*  | -0.001 (n.s.)    | +0.140 (8e-06)*  |
| L3  | +0.064 (5e-02)*  | -0.002 (n.s.)    | +0.095 (2e-03)*  |
| L4  | +0.046 (n.s.)    | +0.014 (n.s.)    | +0.051 (m.)      |
| L5  | +0.051 (m.)      | +0.017 (n.s.)    | +0.033 (n.s.)    |

PUNCT-FREE (w not punct-final; trustworthy):
| lag | perp             | par              | surprisal(w)     |
|-----|------------------|------------------|------------------|
| L1  | +0.099 (2e-04)*  | -0.018 (n.s.)    | +0.179 (2e-09)*  |
| L2  | +0.028 (n.s.)    | -0.025 (n.s.)    | +0.201 (1e-08)*  |
| L3  | -0.015 (n.s.)    | -0.040 (n.s.)    | +0.165 (7e-07)*  |
| L4  | -0.033 (n.s.)    | -0.012 (n.s.)    | +0.112 (2e-04)*  |
| L5  | -0.039 (n.s.)    | -0.012 (n.s.)    | +0.106 (8e-05)*  |

## Findings (punct-free)
1. REORIENTATION HAS A SHORT CAUSAL REACH. perp (lateral / branch) predicts
   downstream wake beyond surprisal at L1 (+0.099) only; gone by L2. par
   (along-heading) predicts wake at NO lag. Both channels are local.
   (The apparent long-range par wake in the punct-uncontrolled model was
   entirely punctuation; it vanishes when controlled. Fourth punctuation trap.)
2. INFORMATION HAS A LONG CAUSAL REACH. surprisal(w) predicts downstream wake
   strongly and PERSISTENTLY, significant all the way to L5 (+0.106, p=8e-05).
   Removing an informative word keeps reshaping the model's representation five
   words later; removing a reorienting-but-unsurprising word does not.

## Answer to the short- vs long-range question
Converging across three probes (static decomposition, behavioral spillover,
causal wake): the REORIENTATION itself (what TEE measures, both channels) is a
LOCAL event. Behaviorally its footprint is <=1 word; causally in the model it
reaches at most 1 word (perp) or 0 (par). It is short-range recalculation.

Long-range implications DO exist in the model, but they are carried by the
word's INFORMATION CONTENT (surprisal), which has a 5+ word causal wake, NOT by
the trajectory reorientation. TEE is a momentum/heading readout with no reach;
surprisal is the quantity that reshapes the downstream trajectory. So TEE and
surprisal differ not only in what they measure locally but in their RANGE:
surprisal propagates, TEE does not.

## Caveats
- Causal wake is in GPT-2's representation, a model of (not identical to) human
  processing. The behavioral spillover (SPR) is the human-side probe and agrees
  that reorientation is local, but SPR truncates long spillover.
- n=1,633 systematic subsample, layer 6, relative-L2 perturbation.
- Surprisal's long wake is partly mechanical (removing a low-probability token
  changes the actual token stream downstream) but that IS the phenomenon:
  information propagates, geometry does not.
- perp L1 wake is small (+0.099) and clean of punctuation; par has none.
