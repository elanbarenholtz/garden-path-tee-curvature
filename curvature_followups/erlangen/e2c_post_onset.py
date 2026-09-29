"""
E2c -- post-onset single-word regression, per subject, EEG and MEG.
Pre-onset activity is never used (no baseline window; the deposit is already
1-20 Hz band-passed), which keeps the analysis clear of both the
curvature-before-onset definitional problem and the Schoenmann et al.
stimulus-dependency confound for pre-onset inference.

Per word w, response = data in [0, 800] ms after onset. Design (all z-scored):
  surprisal, entropy, curv3_L{l}                 (terms of interest)
  log_freq (wordfreq 'de'), n_chars, pres_order  (lexical/position nuisance)
  surprisal_{w+1}, curv3_L{l}_{w+1}, soa_next    (overlap nuisance: at ~3
                                                  words/s the next word's
                                                  response falls in the window)
  surprisal_{w-1}, curv3_L{l}_{w-1}, soa_prev    (the previous word's late
                                                  response overlaps the early
                                                  part of the window)
Fit by OLS for every channel x time (a priori layer) and for every layer on
the benchmark-window mean (layer depth profile).

Benchmark windows (Koelbl et al.):
  EEG  300-450 ms, ROI CP1 CPz CP2 P1 Pz P2
  MEG  500-650 ms, ROI chosen at group level in E2d (leave-one-subject-out)
A priori layer = measures_meta.json a_priori_layer (midpoint).

Usage: python3 e2c_post_onset.py --subjects all [--measures measures/<slug>_words.csv]
Output: betas/sub-{N}_{eeg,meg}.npz
"""
import argparse, glob, json, os, re
import numpy as np, pandas as pd, mne
from wordfreq import zipf_frequency
mne.set_log_level("ERROR")

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=os.environ.get("ERLANGEN_DATA", f"{HERE}/data"))
ap.add_argument("--subjects", default="all")
ap.add_argument("--measures", default=None)
ap.add_argument("--tmax", type=float, default=0.8)
args = ap.parse_args()
os.makedirs(f"{HERE}/betas", exist_ok=True)
meta = json.load(open(f"{HERE}/measures/measures_meta.json"))
NL, LA = meta["n_layers"], meta["a_priori_layer"]
mpath = args.measures or sorted(glob.glob(f"{HERE}/measures/*_words.csv"))[0]
MEAS = pd.read_csv(mpath)
WIN = {"eeg": (0.300, 0.450), "meg": (0.500, 0.650)}
EEG_ROI = ["CP1", "CPz", "CP2", "P1", "Pz", "P2"]
FILES = {"eeg": "EEGdata_raw", "meg": "fixed_ICA_prep_raw"}
TERMS = ["surprisal", "entropy", "curv"]


def z(a):
    a = np.asarray(a, float); sd = np.nanstd(a)
    return (a - np.nanmean(a)) / sd if sd > 0 else np.zeros_like(a)


def design(W, l):
    c = f"curv3_L{l}"
    X = np.column_stack([z(W.surprisal), z(W.entropy), z(W[c]),
                         z(W.log_freq), z(W.n_chars), z(W.pres_order),
                         z(W.surprisal_next), z(W[c + "_next"]), z(W.soa_next),
                         z(W.surprisal_prev), z(W[c + "_prev"]), z(W.soa_prev),
                         np.ones(len(W))])
    return X


def ols(X, Y):
    """Y (n, ...) -> betas (p, ...)"""
    sh = Y.shape; B = np.linalg.lstsq(X, Y.reshape(sh[0], -1), rcond=None)[0]
    return B.reshape((X.shape[1],) + sh[1:])


def run(n, kind):
    f = f"{args.data}/Prob{n}_{FILES[kind]}.fif"
    if not os.path.exists(f):
        return
    raw = mne.io.read_raw_fif(f, preload=True)
    picks = mne.pick_types(raw.info, meg=(kind == "meg"), eeg=(kind == "eeg"),
                           exclude="bads")
    X_all = raw.get_data(picks=picks); fs = raw.info["sfreq"]
    ch = [raw.ch_names[i] for i in picks]
    W = pd.read_csv(f"{HERE}/onsets/sub-{n}_words.csv").merge(
        MEAS.drop(columns=["word", "pres_order"], errors="ignore"),
        on=["audio_file", "word_i"], how="inner", validate="one_to_one")
    W = W.sort_values("onset_rec_s").reset_index(drop=True)
    W["log_freq"] = W.tok.astype(str).str.replace(r"[^\wäöüÄÖÜß]", "", regex=True) \
        .str.lower().map(lambda w: zipf_frequency(w, "de") if w else 0.0)
    W["n_chars"] = W.tok.astype(str).str.replace(r"[^\wäöüÄÖÜß]", "", regex=True).str.len()
    same = W.audio_file.shift(-1) == W.audio_file
    W["soa_next"] = (W.onset_rec_s.shift(-1) - W.onset_rec_s).where(same)
    W["surprisal_next"] = W.surprisal.shift(-1).where(same)
    samep = W.audio_file.shift(1) == W.audio_file
    W["soa_prev"] = (W.onset_rec_s - W.onset_rec_s.shift(1)).where(samep)
    W["surprisal_prev"] = W.surprisal.shift(1).where(samep)
    for l in range(1, NL + 1):
        W[f"curv3_L{l}_next"] = W[f"curv3_L{l}"].shift(-1).where(same)
        W[f"curv3_L{l}_prev"] = W[f"curv3_L{l}"].shift(1).where(samep)
    ns = int(round(args.tmax * fs)) + 1
    idx = np.round(W.onset_rec_s.values * fs).astype(int)
    ok = (idx >= 0) & (idx + ns <= X_all.shape[1])
    need = ["surprisal", "entropy", "soa_next", "surprisal_next", "log_freq",
            "soa_prev", "surprisal_prev"] + \
        [f"curv3_L{l}{sfx}" for l in range(1, NL + 1) for sfx in ("", "_next", "_prev")]
    ok &= W[need].notna().all(axis=1).values
    W, idx = W[ok].reset_index(drop=True), idx[ok]
    Y = np.stack([X_all[:, i:i + ns] for i in idx])          # (words, ch, t)
    Y = Y / Y[:, :, :].std()                                 # scale-free betas
    times = np.arange(ns) / fs
    w0, w1 = WIN[kind]; tw = (times >= w0) & (times <= w1)
    Ywin = Y[:, :, tw].mean(2)                                # (words, ch)
    # a priori layer: full channel x time betas
    B_time = ols(design(W, LA), Y)[:3]                        # (3, ch, t)
    # every layer: window-mean betas per channel
    B_layers = np.stack([ols(design(W, l), Ywin)[:3] for l in range(1, NL + 1)])  # (L,3,ch)
    out = dict(ch_names=np.array(ch), times=times, B_time=B_time, B_layers=B_layers,
               terms=np.array(TERMS), layers=np.arange(1, NL + 1), a_priori=LA,
               n_words=len(W), window=np.array(WIN[kind]))
    if kind == "eeg":
        roi = [ch.index(c) for c in EEG_ROI if c in ch]
        if len(roi) < len(EEG_ROI):
            print(f"  WARNING EEG ROI channels found: {[ch[i] for i in roi]}")
        out["roi_idx"] = np.array(roi)
    np.savez(f"{HERE}/betas/sub-{n}_{kind}.npz", info=np.array([0]), **out)
    msg = ""
    if kind == "eeg":
        b = B_layers[LA - 1][:, roi].mean(1)
        msg = f"ROI {w0*1000:.0f}-{w1*1000:.0f} ms at L{LA}: surp {b[0]:+.4f} ent {b[1]:+.4f} curv {b[2]:+.4f}"
    print(f"  sub {n} {kind}: {len(W)} words, {len(ch)} ch  {msg}")


subs = sorted(int(re.search(r"sub-(\d+)_", p).group(1))
              for p in glob.glob(f"{HERE}/onsets/sub-*_words.csv"))
if args.subjects != "all":
    subs = [int(s) for s in args.subjects.split(",")]
for n in subs:
    for kind in ("eeg", "meg"):
        run(n, kind)
