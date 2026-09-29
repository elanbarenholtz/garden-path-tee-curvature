# Curvature follow-ups (2026-09-28)

Four analyses toward one paper: curvature as a predictor of human behavioral
and physiological data, beyond surprisal and entropy.

| # | analysis | status | files |
|---|---|---|---|
| 1 | NS joint regression (curvature vs entropy) | **run** | `f1_joint_entropy_rt.py`, `f1_out.log`, `f1_results.csv` |
| 1b | inference calibration for #1 | **run** | `f1b_inference_check.py`, `f1b_out.log`, `f1b_perm_null.csv` |
| 3 | anticipated curvature (NS) | ready, needs GPT-2 weights | `anticipated.py`, `f3_anticipated_ns.py`, `f3b_anticipated_rt.py` |
| 2 | Erlangen MEG/EEG post-onset | ready, needs word onsets | `erlangen/e2a..e2d` |
| 4 | mTRF on Erlangen | ready, needs word onsets | `erlangen/e4_trf.py` |

## Inference note (read before quoting #1)
Participant-clustered SEs (the F1 spec) are anticonservative for word-level
predictors: in a smoke test, pure-noise word-level predictors reached |t| 4-5.
Quote the two-way (participant x word) or word-level result from F1b. F3b uses
two-way clustering throughout.

## 3. Anticipated curvature
At each word's final subword, for each top-k next-token candidate: one cached
forward step, angle the candidate would produce at t+1, weighted by p.
`ac_mean`, `ac_var` (primary), `ac_disp` (direction-sensitive pairwise
dispersion). k in {5,10,20,50,100} from one pass; primary k = 50.
Gates: locked hash, final_bpe 9840/9840, cached state == full-pass state for
the realised next token.
```
python3 f3_anticipated_ns.py        # ~5-15 min CPU -> f3_anticipated_8a6087341e.csv
python3 f3b_anticipated_rt.py       # pre-specified RT tests -> f3b_results.csv
```

## 2 + 4. Erlangen (Zenodo 15744486)
The deposit has **no word timings, transcript, or audio**: only preprocessed
(1-20 Hz, ICA) EEG/MEG FIF files and a recorded stimulus-audio channel per
subject. Stimulus: *Vakuum* (P. P. Peterson, read by U. Teschner, Argon
Hoerbuch), 8 alternating ~7 min chapters. Onsets requested from the authors
(Krauss, Schilling, Koelbl). Fallback: supply chapter audio + WebMAUS
TextGrids + transcripts and `e2a` locates each excerpt in every subject's
stimulus channel.
```
export ERLANGEN_DATA=/path/to/zenodo_fifs  ERLANGEN_AUDIO=/path/to/chapters
python3 erlangen/e2a_onsets.py --inspect 1        # FIRST: what is the stimulus channel? same time base as EEG/MEG?
python3 erlangen/e2a_onsets.py                    # -> erlangen/onsets/sub-N_words.csv
python3 erlangen/e2b_german_measures.py --model dbmdz/german-gpt2   # all layers; a priori = midpoint
python3 erlangen/e2c_post_onset.py                # per-subject post-onset betas
python3 erlangen/e2d_group.py                     # -> E2_RESULTS.md (primary, depth profile, clusters)
python3 erlangen/e4_trf.py --audio $ERLANGEN_AUDIO && python3 erlangen/e4_trf.py --group   # -> E4_RESULTS.md
```
If the authors send onset tables instead of TextGrids, write them to
`erlangen/onsets/sub-N_words.csv` with columns
`audio_file, word_i, word, token, onset_s, onset_rec_s, pres_order` and skip e2a.

Pre-specified (E2): EEG ROI CP1 CPz CP2 P1 Pz P2, 300-450 ms; MEG 500-650 ms,
ROI = 20 sensors with largest leave-one-subject-out surprisal effect,
sign-aligned. Post-onset only (no baseline), nuisance: log freq, length,
position, and w-1 / w+1 surprisal, curvature, SOA. Subject = unit.
(E4): lagged ridge at 50 Hz, lags 0-800 ms, leave-one-chapter-out with nested
alpha; unique r = r(full) - r(full minus predictor).

## Validation done here (no real weights/data reachable from this workspace)
- anticipated.py: cache path reproduces full-pass states (max diff 2e-8), tiny random GPT-2
- e2a: synthetic recording with 2 of 3 chapter excerpts played at known offsets:
  offsets exact, unplayed chapter rejected, onset error 0 ms
- e2b: tiny local tokenizer + random GPT-2, multi-chunk text
- e2c/e2d: 8 simulated subjects with planted N400 (-1.0 surprisal, -0.5 curvature):
  recovered -0.20 / -0.10 (2:1), entropy ~0, EEG clusters 315-480 ms, MEG 480-665 ms
- e4: same simulation; curvature unique r > 0 in 8/8, strongest in N400 ROI
- f3b: runs end to end on the real NS frame (with fake anticipated values)
