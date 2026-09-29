"""
E2a -- recover word onsets for the Erlangen audiobook MEG/EEG deposit
(Zenodo 15744486, Koelbl et al.).

The deposit ships NO word timings, transcript, or audio: only per subject
  Prob{N}_EEGdata_raw.fif, Prob{N}_fixed_ICA_prep_raw.fif (MEG),
  Prob{N}_stimuli_channel_raw.fif  (the audio signal recorded during playback,
                                    per the paper, used for synchronisation).
The stimulus is ~50 min of "Vakuum" (Phillip P. Peterson, read by Uve Teschner,
Argon Hoerbuch): two storylines, eight alternating ~7 min chapters. The paper
aligned words with WebMAUS but did not deposit the output.

So we rebuild it:
  1. You supply the audiobook audio for the candidate chapters (AUDIO_DIR/*.wav)
     and, per audio file, the WebMAUS TextGrid (same stem, .TextGrid, tier
     ORT-MAU) plus the punctuated transcript (same stem, .txt).
     (Faster route: ask Koelbl et al. for their MAUS output + chapter list.)
  2. For each subject, the stimulus channel is converted to an amplitude
     envelope and every 30 s window of every audio file is located in it by
     normalised cross-correlation. Windows whose peak is an outlier
     (> Z_ACCEPT SD above that window's xcorr distribution) vote for a file
     offset; the file's offset is the median vote, its used span the range of
     accepted windows. This also identifies WHICH chapter excerpts were played.
  3. Word onsets (MAUS time + offset) are converted to samples in the
     stimulus-channel frame; words outside the matched span are dropped.

Run diagnostics first: `python3 e2a_onsets.py --inspect 1` prints what the
stimulus channel actually contains (sfreq, duration, value distribution,
trigger-like or audio-like) and whether its first_samp/n_times agree with the
EEG and MEG files. If it is trigger pulses rather than audio, the xcorr step
is replaced by edge detection (--triggers).

Outputs: onsets/sub-{N}_words.csv
  subject, audio_file, word_i (within file), word (MAUS), token (transcript),
  onset_s (MAUS), onset_rec_s, onset_idx (index into get_data()), match_z, pres_order
Usage:
  python3 e2a_onsets.py --inspect 1
  python3 e2a_onsets.py --subjects all
"""
import argparse, glob, os, re, difflib, unicodedata
import numpy as np, pandas as pd, mne
from scipy.io import wavfile
from scipy.signal import hilbert, butter, sosfiltfilt, resample_poly, fftconvolve
mne.set_log_level("ERROR")

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=os.environ.get("ERLANGEN_DATA", f"{HERE}/data"),
                help="folder with the Zenodo FIF files")
ap.add_argument("--audio", default=os.environ.get("ERLANGEN_AUDIO", f"{HERE}/audio"),
                help="folder with chapter .wav + .TextGrid + .txt")
ap.add_argument("--subjects", default="all")
ap.add_argument("--inspect", type=int, default=None)
ap.add_argument("--triggers", action="store_true")
args = ap.parse_args()
ENV_FS, WIN_S, Z_ACCEPT = 50, 30.0, 8.0
os.makedirs(f"{HERE}/onsets", exist_ok=True)


def fif(n, kind):
    pat = {"eeg": "EEGdata_raw", "meg": "fixed_ICA_prep_raw",
           "stim": "stimuli_channel_raw"}[kind]
    return f"{args.data}/Prob{n}_{pat}.fif"


def subjects():
    ns = sorted(int(re.search(r"Prob(\d+)_", p).group(1))
                for p in glob.glob(f"{args.data}/Prob*_stimuli_channel_raw.fif"))
    return ns if args.subjects == "all" else [int(s) for s in args.subjects.split(",")]


def envelope(x, fs):
    x = np.asarray(x, float); x = x - x.mean()
    e = np.abs(hilbert(x))
    sos = butter(4, min(10, 0.45 * fs), fs=fs, output="sos")
    e = sosfiltfilt(sos, e)
    from fractions import Fraction
    fr = Fraction(ENV_FS / fs).limit_denominator(1000)
    e = resample_poly(e, fr.numerator, fr.denominator)
    return (e - e.mean()) / (e.std() + 1e-12)


def norm_xcorr(sig, tpl):
    """normalised cross-correlation of template over signal ('valid')"""
    m = len(tpl); t = tpl - tpl.mean(); tn = np.linalg.norm(t)
    num = fftconvolve(sig, t[::-1], mode="valid")
    cs, cs2 = np.cumsum(np.r_[0, sig]), np.cumsum(np.r_[0, sig ** 2])
    s1, s2 = cs[m:] - cs[:-m], cs2[m:] - cs2[:-m]
    den = np.sqrt(np.maximum(s2 - s1 ** 2 / m, 1e-12)) * tn
    return num / den


def inspect(n):
    st = mne.io.read_raw_fif(fif(n, "stim"), preload=True)
    x = st.get_data()
    print(f"stim: {st.ch_names}  sfreq {st.info['sfreq']}  n_times {st.n_times}  "
          f"dur {st.times[-1]/60:.1f} min  first_samp {st.first_samp}")
    for i, ch in enumerate(st.ch_names):
        v = x[i]; u = np.unique(np.round(v, 12))
        print(f"  {ch}: unique values {len(u)}  min {v.min():.3g} max {v.max():.3g} "
              f"sd {v.std():.3g}  -> {'TRIGGER-LIKE' if len(u) <= 16 else 'AUDIO-LIKE'}")
        if len(u) <= 16:
            print(f"    values: {u[:16]}")
    for k in ("eeg", "meg"):
        if os.path.exists(fif(n, k)):
            r = mne.io.read_raw_fif(fif(n, k), preload=False)
            print(f"{k}: {len(r.ch_names)} ch  sfreq {r.info['sfreq']}  n_times "
                  f"{r.n_times}  first_samp {r.first_samp}  dur {r.times[-1]/60:.1f} min"
                  f"  {'SAME FRAME' if (r.n_times, r.first_samp, r.info['sfreq']) == (st.n_times, st.first_samp, st.info['sfreq']) else 'DIFFERENT FRAME: check sync'}")


def read_textgrid_words(path, tier="ORT-MAU"):
    txt = open(path, encoding="utf-8").read()
    blocks = re.split(r'item \[\d+\]:', txt)
    blk = next(b for b in blocks if f'name = "{tier}"' in b)
    iv = re.findall(r'xmin = ([\d.]+)\s*xmax = ([\d.]+)\s*text = "(.*?)"', blk, re.S)
    return [(float(a), float(b), t.strip()) for a, b, t in iv if t.strip()]


def nrm(w):
    w = unicodedata.normalize("NFC", w).lower()
    return re.sub(r"[^\wäöüß]", "", w)


def align_tokens(maus_words, tokens):
    """map transcript tokens (punctuated) onto MAUS words; returns token per MAUS word"""
    a, b = [nrm(w) for w in maus_words], [nrm(t) for t in tokens]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out = [None] * len(a)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            out[blk.a + k] = tokens[blk.b + k]
    return out


def audio_files():
    fs = sorted(glob.glob(f"{args.audio}/*.wav"))
    assert fs, f"no .wav in {args.audio}"
    return fs


def locate(stim_env, wav_path):
    sr, a = wavfile.read(wav_path)
    a = a.mean(1) if a.ndim > 1 else a
    e = envelope(a.astype(float), sr)
    w = int(WIN_S * ENV_FS); votes, spans, zs = [], [], []
    for s0 in range(0, len(e) - w + 1, w // 2):
        c = norm_xcorr(stim_env, e[s0:s0 + w])
        j = int(np.argmax(c)); z = (c[j] - c.mean()) / (c.std() + 1e-12)
        if z > Z_ACCEPT:
            votes.append((j - s0) / ENV_FS); spans.append(s0 / ENV_FS); zs.append(z)
    if len(votes) < 2:
        return None
    off = float(np.median(votes))
    good = np.abs(np.array(votes) - off) < 0.1            # windows agreeing within 100 ms
    if good.sum() < 2:
        return None
    # refine the played span at 1 s resolution: rolling 4 s correlation between
    # audio and recording envelopes at the fixed offset; keep the longest run
    # (gaps <= 3 s bridged) above half the median in-span correlation.
    lag = int(round(off * ENV_FS)); W, H = 4 * ENV_FS, ENV_FS
    r = []
    for s0 in range(0, len(e) - W + 1, H):
        j0 = s0 + lag
        if j0 < 0 or j0 + W > len(stim_env):
            r.append(np.nan); continue
        r.append(np.corrcoef(e[s0:s0 + W], stim_env[j0:j0 + W])[0, 1])
    r = np.nan_to_num(np.array(r), nan=-1)
    thr = max(0.15, 0.5 * np.median(r[r > np.percentile(r, 50)]))
    on = r > thr
    runs, start, gap = [], None, 0
    for i, v in enumerate(np.r_[on, False]):
        if v:
            start = i if start is None else start; gap = 0; last = i
        elif start is not None:
            gap += 1
            if gap > 3 or i == len(on):
                runs.append((start, last)); start, gap = None, 0
    a0, a1 = max(runs, key=lambda x: x[1] - x[0])
    return dict(offset_s=off, span=(a0 * H / ENV_FS, (a1 * H + W) / ENV_FS),
                n_windows=int(good.sum()), median_z=float(np.median(np.array(zs)[good])),
                offset_spread_ms=float(1000 * np.std(np.array(votes)[good])))


def run(n):
    st = mne.io.read_raw_fif(fif(n, "stim"), preload=True)
    fs = st.info["sfreq"]; x = st.get_data()[0]
    if args.triggers:
        raise SystemExit("trigger mode: inspect output first, then map rising edges "
                         "to chapter starts (layout depends on the codes found)")
    senv = envelope(x, fs)
    rows = []
    for wav in audio_files():
        stem = os.path.splitext(wav)[0]
        loc = locate(senv, wav)
        name = os.path.basename(stem)
        if loc is None:
            print(f"  sub {n}: {name}: not found in recording"); continue
        print(f"  sub {n}: {name}: offset {loc['offset_s']:.2f}s  span "
              f"{loc['span'][0]:.0f}-{loc['span'][1]:.0f}s of audio  windows "
              f"{loc['n_windows']}  z {loc['median_z']:.1f}  spread "
              f"{loc['offset_spread_ms']:.0f} ms")
        words = read_textgrid_words(stem + ".TextGrid")
        toks = open(stem + ".txt", encoding="utf-8").read().split() \
            if os.path.exists(stem + ".txt") else [w for _, _, w in words]
        tok_for = align_tokens([w for _, _, w in words], toks)
        miss = sum(t is None for t in tok_for)
        if miss:
            print(f"    WARNING {miss}/{len(words)} MAUS words without transcript token")
        for i, ((on, off_, w), t) in enumerate(zip(words, tok_for)):
            if not (loc["span"][0] <= on <= loc["span"][1]):
                continue
            rec = on + loc["offset_s"]
            rows.append(dict(subject=n, audio_file=name, word_i=i, word=w, token=t,
                             onset_s=on, offset_s_word=off_, onset_rec_s=rec,
                             onset_idx=int(round(rec * fs)),   # index into get_data() (first_samp excluded)
                             match_z=loc["median_z"]))
    D = pd.DataFrame(rows).sort_values("onset_rec_s")
    D["pres_order"] = np.arange(len(D))
    D.to_csv(f"{HERE}/onsets/sub-{n}_words.csv", index=False)
    print(f"  sub {n}: {len(D)} words across {D.audio_file.nunique()} files  "
          f"-> onsets/sub-{n}_words.csv")


if __name__ == "__main__":
    if args.inspect is not None:
        inspect(args.inspect)
    else:
        for n in subjects():
            run(n)
