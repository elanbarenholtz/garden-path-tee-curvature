# ECoG × TEE: first direct neural correspondence to trajectory extrapolation error
Dataset: OpenNeuro ds005574 (podcast listening, ECoG high-gamma, 9 subjects).
Predictor under test: sink-controlled GPT-2-small layer-6 TEE (k=3), computed per
word on the podcast transcript (transcript token_id = GPT-2 BPE; TEE anchored at
each word's final subword; first 2 sink-contaminated onset words dropped).

## Method
TRF encoding model (deconvolution; words come ~3/sec so responses overlap and
simple epoching conflates neighbors, as Zou et al. handled with lagged ridge).
Continuous high-gamma resampled to 32 Hz. Predictors as impulse trains at word
onsets, each lagged 0..0.57 s:
  - envelope  (acoustic broadband; the classic confound), continuous
  - onset     (word-rate/timing nuisance)
  - surp_xl   (GPT-2-XL surprisal; Zou's predictor)
  - tee       (the measure under test)
Per channel: 5-fold CV ridge, score = correlation(predicted, actual) on held-out.
Unique contribution of a predictor = r(full) - r(full without it). Inference at
the SUBJECT level (one mean-over-channels value per subject, n=9) to avoid
spatial-autocorrelation inflation.

## Result (n=9 subjects)
Unique contribution = r(full) - r(full minus that predictor); subject = unit.

### PRIMARY: full lexical control (nuisance = envelope+onset+surprisal+frequency+length)
| predictor | mean unique r | subjects positive | Wilcoxon p | t-test p |
|-----------|---------------|-------------------|------------|----------|
| TEE       | +0.0013       | 8/9               | 0.0098     | 0.035    |
| surprisal | +0.0025       | 9/9               | 0.0020     | 0.004    |

Per-subject TEE unique r (freq+len controlled): 01 +0.0017, 02 +0.0032,
03 +0.0001, 04 +0.0001, 05 -0.0002, 06 +0.0009, 07 +0.0042, 08 +0.0005, 09 +0.0009.

### Comparison: WITHOUT frequency/length (envelope+onset+surprisal only)
| predictor | mean unique r | subjects positive | Wilcoxon p |
|-----------|---------------|-------------------|------------|
| TEE       | +0.0023       | 9/9               | 0.0020     |
| surprisal | +0.0033       | 8/9               | 0.0039     |

Group TEE TRF latency variable across subjects (94-562 ms); do not over-read a
specific latency. Full-model max encoding r per subject 0.19-0.45 (auditory
channels, envelope-driven, as expected).

## Interpretation
TEE has a unique neural correlate in ECoG high-gamma, but it must be stated
carefully. Beyond acoustics + onset + surprisal alone, TEE is robust (9/9
subjects, p=0.002). Adding word frequency and length HALVES it (+0.0023 ->
+0.0013) and makes it marginal (8/9 subjects, Wilcoxon p=0.01, t p=0.035, one
subject slightly negative). So ~half of TEE's raw neural signal is shared with
lexical frequency/length; a modest trajectory-specific residual survives full
control across subjects but is weak. Surprisal is more robust to the lexical
control (stays 9/9). Bottom line: this is the first evidence that TEE has an
independent neural signature, but after honest lexical control it is small and
marginal, not the clean ~2/3-of-surprisal effect the uncontrolled version
suggested. Needs replication and ideally the MEG/M400c dataset.

## Caveats / what would harden it
- English podcast ECoG, NOT Zou's Chinese constituent-boundary MEG (the actual
  M400c). That MEG test (30 GB) is deferred to a machine with the disk.
- Effect sizes are small (unique r ~0.002); the strength is the 9/9 consistency
  and subject-level significance, not per-channel magnitude.
- Controls: envelope, onset, surprisal. NOT YET controlled: word frequency and
  word length. TEE could partly reflect lexical properties; adding freq+length as
  nuisance regressors is the key next control.
- Ridge alpha fixed (1e3), single lag window; no per-subject permutation null
  (across-subject 9/9 Wilcoxon is the inference).
- Boundary-specific (phrase-initial vs non-initial) split not run: transcript
  lacks punctuation (5/5136 words), so it needs a punctuation-restoration model
  as Zou used.

## Files
compute_tee_podcast.py  -> podcast_tee.csv     (TEE per word on the podcast)
trf_ecog_tee.py <subj>  -> trf_sub{NN}.npz     (per-subject TRF encoding model)
aggregate_trf.py                               (across-subject test)
data: ds005574/sub-{01..09}_highgamma_ieeg.fif, podcast.wav, transcript.tsv
