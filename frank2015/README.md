# Frank et al. (2015) EEG reading: curvature vs N400

Data: supplementary zip of Frank, Otten, Galli & Vigliocco (2015), Brain and Language
(https://ars.els-cdn.com/content/image/1-s2.0-S0093934X15001182-mmc1.zip). Only
`stimuli_erp.mat` is needed (not committed; cite the paper). Set FRANK_MAT to its path.

    FRANK_MAT=... GPT2_PATH=gpt2 python3 f1_compute_measures.py   # -> frank_gpt2_measures.csv
    FRANK_MAT=... python3 f2_n400_regression.py                   # -> f2_out.log, f2_results.csv

Each sentence is its own GPT-2 context (<|endoftext|> + sentence); curvature_3 is NaN when its
window touches the sink state. Two-way (participant x word) clustered SEs; permutation null.
