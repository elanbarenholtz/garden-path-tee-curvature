"""
E4 -- multivariate temporal response function (mTRF) for the Erlangen data.
Curvature enters as one regressor alongside acoustics, surprisal, and entropy.
No epoching; overlapping word responses are deconvolved.

Predictors (word-level ones are impulses at word onset, value = z-scored measure):
  env        acoustic envelope, continuous. From the chapter audio placed at
             the offsets found by e2a (--audio), else from the recorded
             stimulus channel (flagged in output; weaker nuisance).
  onset      word-onset impulse (rate/timing)
  log_freq, n_chars                    lexical nuisance (the ECoG lesson:
                                       frequency+length shared ~half of TEE's
                                       raw neural variance)
  surprisal, entropy                   competitors
  curv       curv3 at layer l (a priori layer = midpoint; every layer run)
Lags 0..800 ms (post-onset scope; --tmin < 0 adds pre-onset lags, exploratory).

Fitting: data resampled to FS=50 Hz; ridge via normal equations. Folds are
the audio excerpts (leave-one-chapter-out), so train/test are contiguous
blocks. Ridge alpha chosen per outer fold and per model by inner
leave-one-chapter-out CV on the training chapters (grid ALPHAS), scored by
mean r across channels.
Score per channel = Pearson r(predicted, observed) on held-out chapters.
Unique contribution of X = r(full) - r(full without X).
Inference at the SUBJECT level: mean unique r over channels (all channels;
EEG also the N400 ROI), then t-test / Wilcoxon / sign count across subjects.

Usage:
  python3 e4_trf.py --subjects all [--audio audio_dir]      per-subject fits
  python3 e4_trf.py --group                                 group table
Output: trf/sub-{N}_{eeg,meg}.npz, E4_RESULTS.md
"""
import argparse, glob, json, os, re
import numpy as np, pandas as pd, mne
from scipy import stats
from scipy.io import wavfile
from scipy.signal import hilbert, resample_poly, butter, sosfiltfilt
from wordfreq import zipf_frequency
mne.set_log_level("ERROR")

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=os.environ.get("ERLANGEN_DATA", f"{HERE}/data"))
ap.add_argument("--audio", default=None)
ap.add_argument("--subjects", default="all")
ap.add_argument("--measures", default=None)
ap.add_argument("--tmin", type=float, default=0.0)
ap.add_argument("--tmax", type=float, default=0.8)
ap.add_argument("--fs", type=float, default=50.0)
ap.add_argument("--group", action="store_true")
args = ap.parse_args()
os.makedirs(f"{HERE}/trf", exist_ok=True)
FS = args.fs
LAGS = np.arange(int(round(args.tmin * FS)), int(round(args.tmax * FS)) + 1)
ALPHAS = 10.0 ** np.arange(0, 7)
EEG_ROI = ["CP1", "CPz", "CP2", "P1", "Pz", "P2"]
FILES = {"eeg": "EEGdata_raw", "meg": "fixed_ICA_prep_raw"}


def z(a):
    a = np.asarray(a, float); sd = np.nanstd(a)
    return (a - np.nanmean(a)) / sd if sd > 0 else np.zeros_like(a)


def env_from(x, fs_in):
    e = np.abs(hilbert(np.asarray(x, float) - np.mean(x)))
    e = sosfiltfilt(butter(4, min(8, 0.4 * FS), fs=fs_in, output="sos"), e)
    from fractions import Fraction
    fr = Fraction(FS / fs_in).limit_denominator(1000)
    return resample_poly(e, fr.numerator, fr.denominator)


def lagged(x):
    """(T,) -> (T, n_lags), zero-padded (no wraparound)"""
    T = len(x); out = np.zeros((T, len(LAGS)), np.float32)
    for j, L in enumerate(LAGS):
        if L >= 0:
            out[L:, j] = x[:T - L]
        else:
            out[:T + L, j] = x[-L:]
    return out


def build_predictors(n, T, W, l, stim_fs_raw, stim_x):
    idx = np.round(W.onset_rec_s.values * FS).astype(int)
    ok = (idx >= 0) & (idx < T)
    P = {}
    for name, v in [("onset", np.ones(len(W))), ("log_freq", z(W.log_freq)),
                    ("n_chars", z(W.n_chars)), ("surprisal", z(W.surprisal)),
                    ("entropy", z(W.entropy)), ("curv", z(W[f"curv3_L{l}"]))]:
        s = np.zeros(T, np.float32); v = np.nan_to_num(v)
        np.add.at(s, idx[ok], v[ok]); P[name] = s
    P["env"] = ENV[:T] if len(ENV) >= T else np.r_[ENV, np.zeros(T - len(ENV))]
    return P


def fold_blocks(W, T):
    """contiguous sample ranges per audio excerpt (the CV folds)"""
    b = []
    for f, g in W.groupby("audio_file"):
        a0 = int(max(0, (g.onset_rec_s.min() - 1) * FS))
        a1 = int(min(T, (g.onset_rec_s.max() + args.tmax + 1) * FS))
        b.append((f, a0, a1))
    b = sorted(b, key=lambda x: x[1])
    if len(b) < 3:          # fallback: 5 contiguous blocks spanning the words
        a0, a1 = b[0][1], b[-1][2]; e = np.linspace(a0, a1, 6).astype(int)
        b = [(f"block{i}", e[i], e[i + 1]) for i in range(5)]
        print("  (fewer than 3 excerpts: using 5 contiguous time blocks as folds)")
    return b


def cv_scores(Xfull, Y, blocks, cols):
    """leave-one-block-out; alpha by inner LOBO on training blocks. returns r per channel"""
    X = Xfull[:, cols]
    XtX = [X[a:b].T @ X[a:b] for _, a, b in blocks]
    XtY = [X[a:b].T @ Y[a:b] for _, a, b in blocks]
    I = np.eye(X.shape[1]); pred = np.zeros_like(Y); used = np.zeros(len(Y), bool)
    K = len(blocks)

    def solve(tr, alpha):
        A = sum(XtX[i] for i in tr); B = sum(XtY[i] for i in tr)
        sc = np.trace(A) / A.shape[0]
        return np.linalg.solve(A + alpha * sc * I, B)

    def r_cols(p, y):
        p = p - p.mean(0); y = y - y.mean(0)
        return (p * y).sum(0) / np.sqrt((p ** 2).sum(0) * (y ** 2).sum(0) + 1e-20)

    for k in range(K):
        tr = [i for i in range(K) if i != k]
        best, best_a = -np.inf, ALPHAS[0]
        for a in ALPHAS:
            rs = []
            for j in tr:
                inner = [i for i in tr if i != j]
                _, a0, a1 = blocks[j]
                rs.append(np.nanmean(r_cols(X[a0:a1] @ solve(inner, a), Y[a0:a1])))
            if np.mean(rs) > best:
                best, best_a = np.mean(rs), a
        _, a0, a1 = blocks[k]
        pred[a0:a1] = X[a0:a1] @ solve(tr, best_a); used[a0:a1] = True
    return r_cols(pred[used], Y[used])


def run(n, kind):
    f = f"{args.data}/Prob{n}_{FILES[kind]}.fif"
    if not os.path.exists(f):
        return
    raw = mne.io.read_raw_fif(f, preload=True)
    raw.pick("eeg" if kind == "eeg" else "meg", exclude="bads")
    raw.resample(FS)
    Y = raw.get_data().T.astype(np.float32); Y = (Y - Y.mean(0)) / (Y.std(0) + 1e-20)
    T, nch = Y.shape; ch = raw.ch_names
    W = pd.read_csv(f"{HERE}/onsets/sub-{n}_words.csv").merge(
        MEAS.drop(columns=["word", "pres_order"], errors="ignore"),
        on=["audio_file", "word_i"], how="inner", validate="one_to_one")
    clean = W.tok.astype(str).str.replace(r"[^\wäöüÄÖÜß]", "", regex=True)
    W["log_freq"] = clean.str.lower().map(lambda w: zipf_frequency(w, "de") if w else 0.0)
    W["n_chars"] = clean.str.len()
    blocks = fold_blocks(W, T)
    base = ["env", "onset", "log_freq", "n_chars"]
    res = {}
    for l in range(1, NL + 1):
        P = build_predictors(n, T, W, l, None, None)
        names = base + ["surprisal", "entropy", "curv"]
        Xfull = np.hstack([lagged(P[k]) for k in names])
        col = {k: np.arange(i * len(LAGS), (i + 1) * len(LAGS)) for i, k in enumerate(names)}
        allc = np.concatenate([col[k] for k in names])
        r_full = cv_scores(Xfull, Y, blocks, allc)
        r_nocurv = cv_scores(Xfull, Y, blocks, np.concatenate([col[k] for k in names if k != "curv"]))
        res[f"L{l}_uniq_curv"] = r_full - r_nocurv
        res[f"L{l}_r_full"] = r_full
        if l == LA:
            for comp in ("surprisal", "entropy"):
                rr = cv_scores(Xfull, Y, blocks, np.concatenate([col[k] for k in names if k != comp]))
                res[f"uniq_{comp}"] = r_full - rr
            # TRF shape for curvature at the a priori layer (all data, median alpha)
            A = Xfull.T @ Xfull; sc = np.trace(A) / A.shape[0]
            Bw = np.linalg.solve(A + 1e3 * sc * np.eye(A.shape[0]), Xfull.T @ Y)
            res["trf_curv"] = Bw[col["curv"]].T; res["trf_surprisal"] = Bw[col["surprisal"]].T
        print(f"  sub {n} {kind} L{l}: unique curv mean r {res[f'L{l}_uniq_curv'].mean():+.5f}"
              f"  full r {r_full.mean():.4f}", flush=True)
    roi = np.array([ch.index(c) for c in EEG_ROI if c in ch]) if kind == "eeg" else np.array([], int)
    np.savez(f"{HERE}/trf/sub-{n}_{kind}.npz", ch_names=np.array(ch), lags=LAGS / FS,
             a_priori=LA, n_layers=NL, roi_idx=roi, env_source=ENV_SRC, **res)


def group():
    lines = ["# E4 mTRF results (subject = unit)\n"]
    rows = []
    for kind in ("eeg", "meg"):
        D = [dict(np.load(f, allow_pickle=True)) for f in sorted(glob.glob(f"{HERE}/trf/sub-*_{kind}.npz"))]
        if not D:
            continue
        LAg, NLg = int(D[0]["a_priori"]), int(D[0]["n_layers"])
        lines.append(f"## {kind.upper()} (n = {len(D)}; envelope from {D[0]['env_source']})\n")
        lines.append("| quantity | channels | mean unique r | t | p (t) | p (Wilcoxon) | subjects > 0 |")
        lines.append("|---|---|---|---|---|---|---|")

        def add(label, vals, chans):
            v = np.array(vals); t = stats.ttest_1samp(v, 0)
            w = stats.wilcoxon(v).pvalue if len(v) >= 6 else np.nan
            rows.append(dict(modality=kind, quantity=label, channels=chans, mean=v.mean(),
                             t=t.statistic, p=t.pvalue, p_w=w, pos=(v > 0).sum(), n=len(v)))
            lines.append(f"| {label} | {chans} | {v.mean():+.5f} | {t.statistic:+.2f} | "
                         f"{t.pvalue:.2g} | {w:.2g} | {(v>0).sum()}/{len(v)} |")
        for l in range(1, NLg + 1):
            tag = f"curvature L{l}" + (" (a priori)" if l == LAg else "")
            add(tag, [d[f"L{l}_uniq_curv"].mean() for d in D], "all")
            if kind == "eeg" and len(D[0]["roi_idx"]):
                add(tag, [d[f"L{l}_uniq_curv"][d["roi_idx"]].mean() for d in D], "N400 ROI")
        for comp in ("surprisal", "entropy"):
            add(f"{comp} (benchmark)", [d[f"uniq_{comp}"].mean() for d in D], "all")
        lines.append("")
    pd.DataFrame(rows).to_csv(f"{HERE}/e4_trf_group.csv", index=False)
    open(f"{HERE}/E4_RESULTS.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if args.group:
    group(); raise SystemExit
meta = json.load(open(f"{HERE}/measures/measures_meta.json"))
NL, LA = meta["n_layers"], meta["a_priori_layer"]
MEAS = pd.read_csv(args.measures or sorted(glob.glob(f"{HERE}/measures/*_words.csv"))[0])
subs = sorted(int(re.search(r"sub-(\d+)_", p).group(1)) for p in glob.glob(f"{HERE}/onsets/sub-*_words.csv"))
if args.subjects != "all":
    subs = [int(s) for s in args.subjects.split(",")]
for n in subs:
    # envelope in the recording frame
    st = mne.io.read_raw_fif(f"{args.data}/Prob{n}_stimuli_channel_raw.fif", preload=True)
    Tst = int(np.ceil(st.n_times * FS / st.info["sfreq"]))
    if args.audio:
        W0 = pd.read_csv(f"{HERE}/onsets/sub-{n}_words.csv")
        ENV = np.zeros(Tst)
        for fname, g in W0.groupby("audio_file"):
            sr, a = wavfile.read(f"{args.audio}/{fname}.wav")
            a = a.mean(1) if a.ndim > 1 else a
            e = env_from(a.astype(float), sr)
            off = float((g.onset_rec_s - g.onset_s).median())
            s0 = int(round((g.onset_s.min() - 0.5) * FS)); s1 = int(round((g.onset_s.max() + 2) * FS))
            s0, s1 = max(s0, 0), min(s1, len(e))
            d0 = s0 + int(round(off * FS))
            lo, hi = max(d0, 0), min(d0 + s1 - s0, Tst)
            ENV[lo:hi] = e[s0 + (lo - d0): s0 + (hi - d0)]
        ENV_SRC = "chapter audio"
    else:
        ENV = env_from(st.get_data()[0], st.info["sfreq"]); ENV_SRC = "recorded stimulus channel"
    ENV = z(ENV).astype(np.float32)
    for kind in ("eeg", "meg"):
        run(n, kind)
