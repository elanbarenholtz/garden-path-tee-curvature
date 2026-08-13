# Deep dive: King, Fedorenko & Hosseini (2026) vs Barenholtz — corrected

**Supersedes the earlier version of this file, which contained two errors:**
it claimed their curvature excludes the current token (it does not), and it
claimed your `curvature_3` uses a different window from theirs (it does not).
Both retracted below in §2. Everything here has been checked against the
published equations and against re-run output from `analyze_dissociation.py`
and `analyze_stripping.py`.

---

## 1. What they find

Four results, in increasing strength of evidence.

**1a. Curvature predicts next-token entropy, peaking at the straightest layers.**
Average curvature falls from early layers to a minimum in the middle (GPT-2 XL:
~layer 23 of 48; Pythia-2.8B similar). Predictivity of entropy rises across
layers and peaks near that minimum. Peak r ≈ 0.15, 10-fold cross-validated OLS,
Fisher-z pooled. Both models. Modest but consistent across layers, datasets and
model classes.

**1b. The coupling emerges during training.** Using Pythia checkpoints across a
300B-token run (0%, 0.007%, 0.07%, 0.7%, 7%, 70%): curvature is initially flat
and high across all layers; by ~0.7% of training it drops in early-to-middle
layers and the entropy predictivity rises sharply in tandem. Control measures
(activation magnitude, trajectory distance) show weaker or later-emerging
coupling.

**1c. Causal, with a well-designed control ladder.** Additive perturbations
δ with |δ| = 0.2‖v_k‖ at middle layers (21/48 GPT-2 XL; 11/32 Pythia-2.8B),
drawn from five subspaces: full-space, random-subspace, activation-subspace
(top PCs of residual-stream activations — data-aligned but trajectory-agnostic),
trajectory-subspace (top PCs of that sample's own difference vectors), and
planar-subspace (plane of the two most recent displacements). Only the two
trajectory-aligned families produce a reliable ΔC → ΔH relationship; planar is
largest. Importance-reweighted to match |ΔC| distributions across families, so
it is not a scale artifact. **The activation-subspace control is the key move:**
it rules out "any low-dimensional, data-relevant direction would do."

**1d. Training intervention.** Auxiliary curvature penalty at layers 7–8 of a
from-scratch GPT-2 Small (100M tokens, BookCorpus + Wikipedia 1:3). "Untangled"
(penalty) → lower middle-layer curvature and lower token entropy; "tangled"
(negated penalty) → higher curvature, higher entropy in 2 of 3 datasets.
Validation loss unchanged. Effects small, three seeds per condition.

Their conclusion: straighter trajectories are easier to extrapolate from,
yielding lower-entropy output distributions. Curvature is a task-aligned
representational feature that *influences* behavioural uncertainty — where
"behavioural" means the model's own output distribution, not human behaviour.

---

## 2. Retraction: the measures are the same quantity

Their curvature: `v_k = x_{k+1} − x_k`; `c_k = angle(v_{k+1}, v_k)`, which uses
states `x_k, x_{k+1}, x_{k+2}`. Contextual curvature
`C_k = mean(c_{k−4}, c_{k−3}, c_{k−2})`, spanning `x_{k−4} … x_k` — **five
states, three angles, ending at the current token.**

Your `compute_curvature.py`: `step(i) = h_i − h_{i−1}`;
`ang_at(i) = angle(step(i), step(i−1))`, using `h_{i−2}, h_{i−1}, h_i`;
`curvature_3 = mean(ang_at(ls−2), ang_at(ls−1), ang_at(ls))`, spanning
`h_{ls−4} … h_{ls}` — **five states, three angles, ending at the current token.**

Identical. Their indices run forward from `i`, yours run backward to `i`; the
resulting set of angles is the same. There is no windowing discrepancy, and the
"prospective vs retrospective" framing in the previous draft was wrong.

**Real remaining differences in the measures:**

| | their curvature | your TEE |
|---|---|---|
| quantity | angle between successive steps, averaged over 3 | Euclidean distance from a linear extrapolation |
| units | scale-free | magnitude-sensitive (r = **+0.80** with raw displacement) |
| geometry used | 5 states, 3 angles | 4 states (3 fit + 1 target) |
| trajectory nodes | **every BPE token** | **word-final subwords only** |

That last row is a genuine implementation difference that has not been
reconciled: their trajectory steps token to token; yours steps word to word,
skipping intra-word subwords. For multi-token words these are different paths.

---

## 3. Where the findings actually differ

Your locked-sample numbers, partial r controlling position + story FE
(n = 9,840, GPT-2 Small, layer 6):

| measure | × closure_depth | × entropy |
|---|---|---|
| tee_k3 | +0.190 | +0.051 |
| teeN_k3 (normalised TEE) | +0.119 | **+0.165** |
| curvature_3 | +0.116 | **−0.112** |
| curvature_1 | +0.182 | **−0.172** |
| tee3_par (along-heading) | +0.219 | −0.098 |
| tee3_perp (lateral) | +0.001 | **+0.245** |

With punctuation controlled, curvature's closure correlation collapses
(−0.029 for c₃, −0.007 for c₁) while TEE's survives (+0.134), and perp's
closure correlation *appears* (+0.173). Punctuation is doing a lot of work in
this corpus and every comparison must be punct-controlled.

### The headline discrepancy

**They report curvature × entropy ≈ +0.15. You get −0.11.** Same measure, opposite
sign.

### But look at the spread within your own data

Every row above is "trajectory geometry," and the entropy relationship runs from
**+0.245 (perp) to −0.172 (curvature_1)**. Your own decomposition contains both
signs. Specifically:

- The **lateral** component of the deviation — the part that is about changing
  direction, conceptually closest to what curvature is supposed to capture —
  loads **+0.245** on entropy, the *same* direction they report.
- The **angle-based** measures load negative.
- **Normalising TEE by step size** (teeN) moves it from +0.05 to +0.165 — toward
  their sign.

So it is not the case that your data contradict theirs. Your data contain a
positive direction-change/entropy relationship of the sign and rough magnitude
they report. What is negative is specifically the *angle* formulation at this
model and layer.

---

## 4. What it might mean — four candidate explanations

**A. Model scale, and their own training result predicts this.** They show the
curvature–entropy coupling *emerges* over training, near-zero before ~0.7% of a
300B-token run. If it emerges with training, it may also emerge with scale. They
tested GPT-2 **XL** (1.5B) and Pythia-2.8B; they never tested GPT-2 Small for
this correlation — the only small model in their paper is one they trained
themselves for the regularization experiment. A 124M model may simply sit below
the transition. This is the most likely explanation and the easiest to test.

**B. Layer.** Their effect peaks at the *minimum-curvature* layer, identified
empirically per model (23/48, and middle for Pythia). You used layer 6 of 12
because intermediate layers carry syntax — a different criterion. GPT-2 Small's
minimum-curvature layer has not been located. If it is not layer 6, you are not
measuring at the layer their claim is about.

**C. Token-level vs word-level trajectories.** Theirs steps over every BPE token;
yours steps over word-final subwords. Word-level aggregation discards intra-word
geometry. Since angles are scale-free but sensitive to step direction, and
subword steps within a word are likely more collinear than word-to-word steps,
this could plausibly flip an angle-based statistic while leaving a
magnitude-based one alone.

**D. Corpus and punctuation.** Natural Stories glues trailing punctuation onto
words, and punctuation tokens are sink-like rest states. Note curvature_3's
punctuation coefficient in the joint model: **+0.249**, the largest of any
predictor, versus **−0.126** for TEE. Punctuation pushes the two measures in
opposite directions. Their UD corpus is differently constructed.

Note these are not mutually exclusive, and **(A) and (B) are the ones that
matter for whether you have a disagreement at all.**

---

## 5. The genuinely interesting scientific content

Setting the sign question aside, three things in your data are real contributions
to their line of work.

**5a. The decomposition explains why measure choice flips the sign.** Your
par/perp split shows the deviation contains two channels with *opposite* entropy
loadings (par −0.10, perp +0.25) and, punct-controlled, reinforcing structure
loadings (par +0.06, perp +0.17). Any scalar summary of trajectory geometry
weights these two channels implicitly, and its relationship to entropy depends
entirely on the weighting. That is a general point about this whole class of
measures, and it is yours.

**5b. Structure is not in their picture at all.** Their paper has no syntactic
variable. Your closure-depth result — surviving entropy, surprisal, frequency
and punctuation — says trajectory geometry carries information about the parse
that is not reducible to uncertainty. They cannot address this with their design.

**5c. The extrapolation tension.** Their mechanism is that straight trajectories
are linearly extrapolable. Your direction-preservation numbers (recomputed and
confirmed this session):

| layer | current | +1 | +2 | +3 |
|---|---|---|---|---|
| L6 | 0.436 | **0.099** | 0.078 | 0.077 |
| L12 | 0.615 | 0.541 | 0.540 | 0.539 |

against a chance baseline of 0.029. At the intermediate layer, directional
structure is nearly gone one word later. If direction does not persist,
"extrapolation" cannot mean what it sounds like it means at those layers.

Caveat to state carefully: their curvature is defined over *adjacent* difference
vectors, so it is a two-step-local quantity; a path can be locally smooth while
its direction decorrelates over 2–3 steps. And their perturbation result is
direct evidence that the trajectory is functionally live at those layers. So
this is a tension to pose, not a refutation to assert — but it is a real one,
and posing it well would be a genuine contribution.

---

## 6. The experiments that would resolve this

In priority order.

1. **Run their exact configuration.** GPT-2 XL, token-level trajectory, layer 21,
   your curvature code, correlate with entropy. If you get ≈ +0.15, the
   discrepancy is scale and/or tokenization and you can say so cleanly. If you
   don't, you have a replication issue and should write to Eghbal before
   publishing anything. **This is the one experiment that has to happen.**
2. **Locate GPT-2 Small's minimum-curvature layer** and re-run the dissociation
   there. Removes the layer-choice objection.
3. **Token-level vs word-level.** Recompute your curvature and TEE stepping over
   every BPE token, on the same corpus. Isolates (C).
4. **Layer sweep of curvature × entropy in GPT-2 Small.** If the sign flips
   somewhere in depth, that is itself a finding worth reporting.
5. **Add closure depth to their setup.** Their UD sentences have dependency
   parses. If curvature tracks structure in *their* configuration, your
   structural claim generalises beyond GPT-2 Small.

Experiments 1–3 are a day's work with the code that already exists.

---

## 7. Bottom line

You do not currently have a disagreement with them that you can defend, because
you have not measured in their configuration. What you have is a *different
measure family evaluated at a different scale on a different corpus*, which
produces a different sign for one statistic while reproducing their sign in the
component of your own decomposition that most resembles their measure.

The defensible claims, today:

- Trajectory geometry carries syntactic structure independent of surprisal and
  entropy (yours alone; they have no structural variable).
- The relationship between trajectory geometry and uncertainty is
  definition-dependent: within one decomposition, the lateral component loads
  +0.25 on entropy and the along-heading component −0.10.
- Directional persistence at the intermediate layer decays to near chance within
  one word, which raises a question about the extrapolation mechanism.

The claim to *not* make until experiment 1 is run: that their curvature–entropy
result does not hold.
