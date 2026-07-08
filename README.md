# TEE vs Curvature — trajectory measures, what they reflect, and how far they reach

Self-contained bundle for the Natural Stories / GPT-2 layer-6 analyses comparing
trajectory extrapolation error (TEE) to King/Fedorenko/Hosseini contextual
curvature. Locked sample hash `8a6087341e`, n = 9,840. Everything validated
against the locked sample (recomputed TEE matches to 1.4e-14; 0/9840 closure and
final-bpe mismatches).

## Start here
`tee_vs_curvature/WRITEUP_TEE_vs_curvature_full.html` — the full narrative
writeup (open in a browser). The four `P_RESULTS_*.md` are the per-analysis
tables.

## Findings in one paragraph
TEE and curvature are genuinely different measures (overlap r=0.10; neither
absorbs the other): TEE tracks syntactic structure (closure), curvature tracks
predictive uncertainty (entropy). TEE's orthogonality to surprisal is a
cancellation: the TEE deviation splits into two orthogonal channels (along-
heading `par`, lateral `perp`) whose entropy signals have opposite sign and
cancel while their structure signals reinforce. The reorientation is a LOCAL
event: behavioral spillover reaches at most 1 word, and the causal ablation wake
inside the model reaches at most 1 word. Long-range implications exist but live
in INFORMATION (surprisal has a 5+ word causal wake), not in the trajectory
geometry. NB: a punctuation confound (Natural Stories glues trailing punctuation
onto words; GPT-2 punct tokens are sink states) produced spurious effects in four
places; every reported claim is on the punctuation-controlled result.

## Layout
```
rebuild_v2_outputs/sample_8a6087341e.csv        locked sample (features, tee_k*, surprisal, entropy, ...)
naturalstories/words.tsv                        corpus words
naturalstories/parses/penn/all-parses-aligned.txt.penn   PTB parses (closure_depth)
naturalstories/naturalstories_RTS/processed_RTs.tsv      self-paced RT (848,875 obs)
tee_vs_curvature/
  compute_curvature.py     recompute layer-6 states; curvature + par/perp decomposition  -> curvature_merged_8a6087341e.csv
  analyze_dissociation.py  analysis 1: TEE vs curvature double dissociation
  analyze_stripping.py     analysis 2: magnitude-stripping + par/perp cancellation
  analyze_spillover.py     analysis 3: reading-time spillover, typed by decomposition
  compute_wake.py          causal ablation wake  -> wake_step6.csv (STEP arg; 6 -> ~1640 words)
  analyze_wake.py          analysis 4: does reorientation reach downstream beyond surprisal
  P_RESULTS_*.md           result tables (one per analysis)
  p_*_output.txt           raw script stdout
  curvature_merged_*.csv, wake_step6.csv   precomputed measures (skip the compute step)
```

## Running (one path change)
The scripts hardcode `GP = "/Users/elansmini/Research/Garden_Path"`. Set it to
this repo's root on your machine (edit the `GP =` line at the top of each script),
then:
```
pip install numpy pandas scipy statsmodels torch transformers nltk
cd tee_vs_curvature
python3 analyze_dissociation.py     # uses precomputed curvature_merged_*.csv
python3 analyze_stripping.py
python3 analyze_spillover.py
python3 analyze_wake.py             # uses precomputed wake_step6.csv
# to recompute from scratch (needs GPT-2 download, CPU ok):
python3 compute_curvature.py        # ~2 min -> curvature_merged_*.csv
python3 compute_wake.py 6           # ~8 min  -> wake_step6.csv
```
`compute_*` recompute the layer-6 hidden states and re-validate against the
locked sample before producing any measure. The `analyze_*` scripts run on the
precomputed CSVs included here, so they work without a GPU or the compute step.

## Conventions (match the parent project)
z-scored predictors (ddof=0); controls = from_start + fs2 + from_end + fe2 +
C(story_id); cluster-robust SEs by sent_uid; hash re-verified before every table;
punctuation controlled + punct-free robustness reported; raw tables only, no
interpretive rescue.
