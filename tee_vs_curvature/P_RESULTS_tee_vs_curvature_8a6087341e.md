# TEE vs Curvature: full-sample controlled double dissociation
Sample: hash 8a6087341e, n = 9,840 (locked). Curvature computed on hidden
states validated identical to the locked sample: 0/9840 closure & final_bpe
mismatches, max |tee_k3 - recomputed| = 1.4e-14, max |tee_k50 - re| = 1.4e-14.
Punct-free subsample (C4): n = 8,674. has_trailing_punct = 1166/8674 (matches
P1-A). Raw output: p_dissociation_output.txt. Compute: compute_curvature.py.
Analysis: analyze_dissociation.py.

Measures (all anchored at the word's final subword, same anchor as tee_k):
- tee_k3       short-window trajectory extrapolation error (locked col; a distance)
- curvature_3  King-style contextual curvature: mean angle between successive
               step vectors over the last 3 tokens (an angle, scale-free)
- curvature_1  single-step angle (matches the earlier compare_tee_vs_angular.py)

## Headline (numbers, no adjectives)
The two measures are distinct at n=9840: overlap r(tee_k3, curvature_3)=+0.10;
in a joint model neither absorbs the other (C6). The STRUCTURE-side dissociation
is clean and survives punctuation: tee_k3 tracks closure_depth (+0.13, punct-
controlled; +0.16 punct-free), curvature does not (null once punctuation is
controlled). On the ENTROPY side the two measures also dissociate but NOT in the
direction the 2-story head-to-head suggested: curvature couples NEGATIVELY with
entropy here (-0.11 to -0.18), and the 2-story +0.113 positive coupling does not
replicate (sign reverses). tee_k3's entropy coupling is small (+0.05 partial).

## C1. Uncontrolled Pearson r (full n) vs 2-story head-to-head
| measure     | x closure_depth      | x entropy            |
|-------------|----------------------|----------------------|
| 2-story ref | tee +0.081 / ang +0.024 | tee -0.019 / ang +0.114 |
| tee_k3      | +0.2066 (2.7e-95)    | +0.0429 (2.0e-05)    |
| curvature_3 | +0.1312 (5.1e-39)    | -0.1068 (2.3e-26)    |
| curvature_1 | +0.1995 (7.2e-89)    | -0.1741 (8.1e-68)    |

overlap: r(tee_k3, curvature_3)=+0.104; r(tee_k3, curvature_1)=+0.398.

ANOMALY (flagged): curvature x entropy is NEGATIVE at full n (-0.11/-0.17),
opposite the 2-story +0.114 and opposite King et al's reported positive
curvature-entropy coupling. The 2-story estimate was 2 stories, BPE-position
granularity, not word-final anchored (entropy_by_position.csv, n=2482 BPE
positions). The full-sample word-anchored estimate supersedes it. r(entropy,
surprisal)=+0.478 in this sample.

## C2. Partial r | position + story FE
| measure     | x closure_depth      | x entropy            |
|-------------|----------------------|----------------------|
| tee_k3      | +0.1898 (2.3e-80)    | +0.0508 (4.8e-07)    |
| curvature_3 | +0.1160 (9.2e-31)    | -0.1121 (7.5e-29)    |
| curvature_1 | +0.1823 (3.4e-74)    | -0.1723 (2.3e-66)    |

(tee_k3 x closure +0.1898 reproduces locked a1 k=3 to the printed digits:
residualization verified despite macOS/NumPy2 matmul RuntimeWarnings.)

## C3. Partial r | position + story FE + has_trailing_punct   [cleanest spec]
| measure     | x closure_depth      | x entropy            |
|-------------|----------------------|----------------------|
| tee_k3      | +0.1338 (1.8e-40)    | +0.0504 (5.8e-07)    |
| curvature_3 | -0.0290 (4.1e-03)    | -0.1159 (1.0e-30)    |
| curvature_1 | -0.0069 (5.0e-01)    | -0.1814 (1.8e-73)    |

Curvature's closure correlation (C1/C2: +0.13/+0.20) collapses to ~0 once
punctuation is controlled: it was punctuation-driven, the same trap as the
long-k TEE effect in P1. tee_k3's closure effect survives punctuation.

## C4. Partial r, PUNCT-FREE subsample (n=8,674) | position + story FE
| measure     | x closure_depth      | x entropy            |
|-------------|----------------------|----------------------|
| tee_k3      | +0.1636 (5.2e-53)    | +0.0500 (3.3e-06)    |
| curvature_3 | -0.0142 (1.9e-01)    | -0.1491 (2.9e-44)    |
| curvature_1 | +0.0112 (3.0e-01)    | -0.2461 (1.1e-119)   |

Independent route (subset, not covary): same pattern. tee->closure survives;
curvature->closure null; curvature->entropy negative and strong.

## C5. Double-dissociation joint regressions (z, cluster-robust by sent_uid)
DV ~ closure_depth + entropy + surprisal + word_length + log_freq
     + has_trailing_punct + position + C(story_id)

DV = z(tee_k3):       closure +0.1242 (4.8e-22) | entropy -0.1780 (7.4e-63) |
                      surprisal +0.1955 | log_freq -0.4036 | punct -0.1262 | R2=0.237
DV = z(curvature_3):  closure -0.0199 (2.6e-01, n.s.) | entropy -0.1131 (8.0e-18) |
                      surprisal +0.0639 | log_freq +0.1239 | punct +0.2492 | R2=0.078

NOTE (collinearity): tee_k3's entropy beta (-0.178) is a suppressor with
surprisal (+0.196), r(entropy,surprisal)=0.48. tee_k3's clean entropy relation
is the small positive bivariate/partial (+0.04/+0.05), NOT -0.18. Do not read
-0.178 as "TEE tracks (negative) entropy". curvature_3's entropy beta (-0.113)
matches its bivariate (-0.107): stable, not a suppressor.

## C6. Horse race: neither measure absorbs the other
closure_depth beta on tee_k3:  +0.1242 (no curvature) -> +0.1263 (+ curvature_3).
  curvature_3 does not dent TEE's closure effect; curvature_3's own beta = +0.106 (2.9e-12).
entropy beta on curvature_3:   -0.1131 (no tee) -> -0.0902 (+ tee_k3), survives.
  tee_k3's own beta on curvature_3 = +0.128 (2.9e-15).
Each measure carries variance the other does not.

## Verdict
1. tee_k3 and curvature are distinct measures (overlap r=0.10; mutual non-
   absorption in C6). CONFIRMED at n=9840.
2. STRUCTURE dissociation clean and punctuation-robust: TEE->closure yes,
   curvature->closure no (curvature's raw closure signal was punctuation).
3. ENTROPY: the measures dissociate (curvature couples with entropy, TEE barely),
   but curvature's coupling is NEGATIVE here (-0.11), NOT the positive coupling
   King reports and NOT the 2-story +0.114. Cannot currently claim "our curvature
   reproduces King's uncertainty geometry" on GPT-2-small layer 6.
4. Model/layer caveat: King used GPT-2-XL / Pythia-2.8B mid-layers; sign of the
   curvature-entropy coupling may be model/layer dependent. Untested here.
