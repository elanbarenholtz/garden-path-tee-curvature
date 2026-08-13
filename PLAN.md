# TEE research — status + plan (handoff for a fresh session on the laptop)

This repo is the portable record of a multi-thread investigation of **trajectory
extrapolation error (TEE)**: at each word, fit a line to the preceding k=3 GPT-2
hidden states, extrapolate one step, measure the Euclidean deviation. TEE is
nearly orthogonal to surprisal (r=.044) yet predicts human reading times, and it
tracks syntactic structure. This document is the pick-up point.

If you are a fresh Claude session: read this file, then the `P_RESULTS_*.md` in
each folder. The immediate next task is the **ZuCo reading + EEG + eye-tracking**
analysis (Section "PLAN"), reusing the TRF deconvolution already validated in
`ecog_tee/`.

Machine note: this work is intended to run on a laptop with ~634 GB free (the
prior session ran on a Mac with only ~16 GB free, which blocked the big neural
datasets). All large datasets below fit comfortably.

---

## What is established (done, in this repo)

### 1. tee_vs_curvature/ — TEE vs King curvature; the cancellation account
- TEE and King/Fedorenko/Hosseini **contextual curvature are different measures**
  (overlap r=0.10; neither absorbs the other). TEE tracks syntactic closure;
  curvature tracks entropy (predictive uncertainty). Within-sample double
  dissociation on the locked Natural Stories sample 8a6087341e (n=9,840).
- **Why TEE is orthogonal to surprisal:** the TEE deviation splits into two
  orthogonal channels (along-heading `par`, lateral `perp`) whose *entropy*
  loadings have opposite sign and CANCEL, while their *structure* loadings add.
  TEE is the balance point where uncertainty nets out and structure survives.
- **Range:** behavioral spillover (reading time) and a causal ablation "wake"
  inside the model both show the reorientation is LOCAL (<=1 word). Long-range
  implications live in INFORMATION (surprisal has a 5+ word causal wake), not in
  the trajectory geometry.
- Files: P_RESULTS_{tee_vs_curvature, stripping_decomposition, spillover, wake}.md
  + scripts + WRITEUP_TEE_vs_curvature_full.html (narrative).
- RECURRING HAZARD: Natural Stories glues trailing punctuation onto words and
  GPT-2 punctuation tokens are attention sinks. This produced spurious effects in
  ~4 analyses; every claim is stated on the punctuation-controlled result.

### 2. ecog_tee/ — first neural test of TEE (OpenNeuro ds005574 podcast ECoG)
- TRF encoding model, 9 subjects. TEE's unique contribution beyond
  surprisal+acoustics: **9/9 subjects positive, p=0.002.** After adding word
  frequency+length controls: **attenuates ~half, 8/9, Wilcoxon p=0.01, t=0.035**
  (marginal). Real but modest. First time TEE ever touched neural data.
- This is LISTENING (English podcast), not reading — the key limitation.

### 3. Matters Arising / constituent-boundary sink finding (in main Garden_Path,
    not this repo): re-ran sink_diagnostic.py on Zou et al.'s Chinese MEG
    stimuli. The boundary TEE effect is ~92% a token-0 attention-sink artifact
    (raw d=8.8 -> clean d=0.73); the typicality-invariance claim (the paper's
    core) collapses from 99% to 27% retention (no better than displacement). A
    small residual boundary effect survives sink removal (clean d~0.5) but under
    pooled stats only and without the typicality property. The anti-Zou claim
    does not stand; a plain "small boundary effect" is the most that survives.

---

## PLAN (next, in priority order)

### P1. ZuCo — the optimal dataset (DO THIS FIRST)
Why: ZuCo has **simultaneous EEG + eye-tracking during natural READING**. TEE is
a reading-time measure, so this is the theoretically matched test AND lets TEE be
tested against BOTH the neural signal and the reading behavior (fixation
durations) in the same subjects. No other dataset does this.
- Size: ZuCo 1.0 = 64.7 GB (osf.io/q3zws, 12 subjects), ZuCo 2.0 = 128.9 GB
  (osf.io/2urht). Start with 1.0's natural-reading task.
- Method: natural reading => EEG is fixation-locked with OVERLAPPING responses
  (fixation-related potentials). Use the SAME TRF/lagged-ridge deconvolution as
  ecog_tee/, with predictors = TEE + surprisal + frequency + length + acoustic/
  visual onset. Compute sink-controlled TEE (GPT-2) on the ZuCo sentences.
- Two deliverables: (a) does TEE predict the EEG beyond surprisal+freq+length;
  (b) does TEE predict eye-tracking fixation durations (the reading-time analog).
  The complete story is TEE in both brain AND behavior during reading.

### P2. MEG-MASC (Gwilliams et al., OpenNeuro) — high-power MEG confirmation
27 subjects, ~2 h each, naturalistic narratives, word-annotated, MEG. Best power
for TEE's small effect and a bridge to the MEG/M400c literature. Listening.

### P3. Zou MEG (30 GB, Zenodo 10.5281/zenodo.15236117) — OPTIONAL
Only to close the constituent-boundary thread. The sink control already gutted
that claim, so low priority. MEG.tar is 30.3 GB.

### Also worth doing
- Frank et al. 2015 reading EEG (word-by-word RSVP; cleanest reading paradigm)
  as a fast confirmatory if obtainable.
- Fold the cancellation account + the range dissociation into the main TEE
  manuscript as the mechanistic explanation of TEE's independence from surprisal;
  reframe the King comparison as complementary (structure vs uncertainty).

---

## Environment (install once on the laptop)
```
pip install torch transformers mne mne-bids scikit-learn scipy statsmodels wordfreq numpy pandas nltk
```
GPT-2 small is used for TEE (layer 6, k=3). All neural analysis uses MNE + a
sklearn-ridge TRF (see ecog_tee/trf_ecog_tee.py as the template to adapt).

## Key methodological lessons (apply to every dataset)
1. Deconvolve, don't epoch: overlapping word/fixation responses need lagged ridge.
2. Always regress out acoustic envelope (listening) or onset/visual (reading).
3. Control word frequency + length: ~half of TEE's raw neural variance is lexical.
4. Sink-control TEE (drop token-0-contaminated words; watch punctuation-final).
5. Inference at the subject level, not per-channel (spatial autocorrelation).
6. Report punctuation-controlled results; flag every artifact.

## Repo layout
```
PLAN.md                     <- this file
tee_vs_curvature/           thread 1: TEE vs curvature, cancellation, spillover, wake
  WRITEUP_..._full.html     narrative writeup of thread 1
  P_RESULTS_*.md            4 result docs
ecog_tee/                   thread 2: first neural test (ECoG); scripts+results, no raw data
  README.md                 how to fetch ds005574 raw data + run
rebuild_v2_outputs/         locked Natural Stories sample 8a6087341e.csv
naturalstories/             corpus (words, parses, self-paced RTs) for thread 1
```
