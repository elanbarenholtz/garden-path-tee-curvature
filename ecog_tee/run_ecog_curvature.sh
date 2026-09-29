#!/bin/bash
# Curvature x ECoG (ds005574). podcast_curvature.csv is precomputed and committed.
# Needs ECOG_DIR with ds005574/sub-XX_highgamma_ieeg.fif + ds005574/podcast.wav
# (the same data folder the TEE analysis used; see README for download commands).
set -e
cd "$(dirname "$0")"
export ECOG_DIR=${ECOG_DIR:-/Users/elansmini/Research/Garden_Path/data/zou2026}
for s in 01 02 03 04 05 06 07 08 09; do python3 trf_ecog_curvature.py $s; done
python3 aggregate_trf_curvature.py
for s in 01 02 03 04 05 06 07 08 09; do python3 trf_ecog_curvature.py $s --with-tee; done
python3 aggregate_trf_curvature.py --with-tee
