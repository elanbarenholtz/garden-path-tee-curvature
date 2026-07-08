# Magnitude-stripping + residual decomposition (locked sample 8a6087341e)
n = 9,840; punct-free n = 8,674. Curvature/decomposition on hidden states
validated identical to the locked sample (tee match 1.4e-14). Raw output:
p_stripping_output.txt. The k=3 residual r = h_t - pred decomposes exactly
into along-heading (par) and lateral (perp) magnitudes: tee_k3^2 = par^2 + perp^2
(max residual 1.5e-11). The two components are geometrically orthogonal:
r(tee3_par, tee3_perp) = +0.015.

## The decomposition is the finding (partial r, punct-controlled = trustworthy)

| measure     | closure (D2 +punct / D3 punct-free) | entropy (D2 / D3)      |
|-------------|-------------------------------------|------------------------|
| tee_k3      | +0.134 / +0.164                     | +0.050 / +0.050        |
| teeN_k3     | +0.136 / +0.141                     | +0.165 / +0.174        |
| curvature_3 | -0.029 / -0.014  (~0)               | -0.116 / -0.149        |
| curvature_1 | -0.007 / +0.011  (~0)               | -0.181 / -0.246        |
| tee3_par    | +0.062 / +0.087                     | -0.103 / -0.134        |
| tee3_perp   | +0.173 / +0.182                     | +0.250 / +0.299        |

(Uncontrolled D1 attributes closure to tee3_par (+0.219) instead of tee3_perp
(+0.001); that attribution is PUNCTUATION-DRIVEN and reverses under control.
Punct-controlled specs are primary, per P1.)

## Interpretation the numbers force

1. Raw TEE is a SUM of two orthogonal channels with OPPOSITE-sign entropy
   loadings: along-heading (par) entropy -0.10, lateral (perp) entropy +0.25.
   In the sum these largely CANCEL -> tee_k3 x entropy = +0.05 (near zero),
   while their closure loadings REINFORCE (both +) -> tee_k3 x closure = +0.13.
   TEE's orthogonality to prediction (the manuscript's r=.044 vs surprisal) is
   thus not blindness to uncertainty; it is the balanced combination where the
   uncertainty signal nets out and the structure signal survives.

2. No single raw component is a clean structure detector. tee3_perp carries
   structure (+0.18) AND entropy (+0.30). teeN carries structure (+0.14) AND
   entropy (+0.17). Only the specific combination tee_k3 isolates structure
   with ~zero entropy.

3. Curvature is the opposite balance: ~0 net structure, carries entropy
   (negative here). It weights the two channels so structure cancels and
   uncertainty survives. This is why tee_k3 and curvature are near-orthogonal
   (r=0.10): they are near-complementary weightings of the same two channels.

## Revises the earlier "magnitude vs angle" framing
The clean cut is NOT magnitude (tee) vs angle (curvature). Both par and perp
are magnitudes, and both correlate with entropy (opposite signs). The operative
variable is the DIRECTION of the deviation (along-heading vs lateral) and, above
that, the specific linear combination. TEE and curvature differ because they are
different combinations of the par/perp channels, not because one is a distance
and one is an angle.

## Caveats (unchanged)
- Curvature-entropy coupling is NEGATIVE here (opposite King's +0.15);
  model/layer dependence untested (GPT-2-small L6 vs their XL/Pythia mid).
- par/perp closure attribution is punctuation-sensitive (D1 vs D2/D3); only the
  punct-controlled attribution (structure in perp) is trustworthy.
- All GPT-2-small layer 6, Natural Stories, model-internal. RT link frozen.
- Everything second-order to lexical frequency.

## Cross-correlations (n=9840)
              tee_k3 teeN_k3 curv_3 curv_1 par    perp
tee_k3        1.000  0.632   0.104  0.398  0.858  0.521
teeN_k3       0.632  1.000  -0.300  0.262  0.450  0.476
curvature_3   0.104 -0.300   1.000  0.540  0.245 -0.208
curvature_1   0.398  0.262   0.540  1.000  0.631 -0.275
tee3_par      0.858  0.450   0.245  0.631  1.000  0.015
tee3_perp     0.521  0.476  -0.208 -0.275  0.015  1.000
