# ECoG × TEE: first neural test of trajectory extrapolation error

Tests whether sink-controlled TEE tracks the ECoG high-gamma response during
naturalistic listening (OpenNeuro ds005574, "podcast", 9 subjects, English).
Result (see `P_RESULTS_ecog_tee.md`): TEE has a unique neural correlate beyond
surprisal + acoustics (9/9 subjects); after adding word frequency + length
controls it attenuates ~half and is marginal (8/9, Wilcoxon p=0.01, t p=0.035).
Real but modest. This is a LISTENING dataset; the reading version (ZuCo) is the
priority next step (see ../PLAN.md).

## Files here (small; raw neural data NOT included)
- compute_tee_podcast.py  -> podcast_tee.csv    sink-controlled TEE per word (GPT-2-small L6, k=3)
- trf_ecog_tee.py <subj>  -> trf_sub{NN}.npz    per-subject TRF encoding model (included)
- aggregate_trf.py                              across-subject test (the inference)
- P_RESULTS_ecog_tee.md                         result tables + caveats

## Getting the raw data (~4 GB, from OpenNeuro ds005574)
```
mkdir -p ds005574
# transcript (word onsets + GPT2-XL surprisal), ~0.5 MB
curl -sL -o transcript.tsv "https://s3.amazonaws.com/openneuro.org/ds005574/stimuli/gpt2-xl/transcript.tsv"
# acoustic stimulus for envelope control, ~303 MB
curl -sL -o ds005574/podcast.wav "https://s3.amazonaws.com/openneuro.org/ds005574/stimuli/podcast.wav"
# high-gamma ECoG per subject, ~250-830 MB each
for s in 01 02 03 04 05 06 07 08 09; do
  curl -sL -o ds005574/sub-${s}_highgamma_ieeg.fif \
    "https://s3.amazonaws.com/openneuro.org/ds005574/derivatives/ecogprep/sub-${s}/ieeg/sub-${s}_task-podcast_desc-highgamma_ieeg.fif"
done
```

## Run
```
pip install torch transformers mne scikit-learn scipy statsmodels wordfreq numpy pandas
# edit the D = "..." path at the top of each script to point here
python3 compute_tee_podcast.py           # -> podcast_tee.csv (needs transcript.tsv)
for s in 01 02 03 04 05 06 07 08 09; do python3 trf_ecog_tee.py $s; done
python3 aggregate_trf.py                  # across-subject test
```

## Method notes (carry to ZuCo/MEG-MASC)
- Words come ~3/sec => responses overlap; use a TRF/deconvolution (lagged ridge),
  NOT simple word-locked epoching.
- Always include the acoustic envelope + word-onset as nuisance regressors.
- Control word frequency + length: they share ~half of TEE's raw neural variance.
- Inference at the SUBJECT level (one value/subject), not per-channel.
- TEE sink control: the transcript token_id column is GPT-2 BPE; TEE anchored at
  each word's final subword; drop the first 2 words (token-0 sink).
