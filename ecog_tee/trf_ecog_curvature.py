"""
ECoG x curvature: TRF encoding model on ds005574 (podcast, high-gamma ECoG),
identical in every respect to trf_ecog_tee.py (32 Hz, lags 0..~0.57 s, 5-fold
contiguous CV, ridge alpha 1e3, subject-level inference) except:
  * the measure under test is curvature_3 (GPT-2 small, layer 6, final subword)
  * entropy (GPT-2 small, pre-word) is added as a competing predictor, so the
    question is the same as on Natural Stories: curvature beyond surprisal
    AND entropy, with envelope, onset, frequency and length as nuisance.

Unique contribution of X = r(full) - r(full without X), per channel; subject
summary = mean over channels. Also reports TEE in the same model family for a
direct comparison (--with-tee adds TEE as an extra nuisance: does curvature
survive TEE?).

Usage: ECOG_DIR=/path/to/zou2026 python3 trf_ecog_curvature.py 01 [--with-tee]
Output: $ECOG_DIR/trf_curv_sub{NN}[_tee].npz
"""
import os, sys, re, numpy as np, pandas as pd, mne
from scipy.io import wavfile
from scipy.signal import hilbert
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from wordfreq import zipf_frequency
mne.set_log_level("ERROR")

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ.get("ECOG_DIR", "/Users/elansmini/Research/Garden_Path/data/zou2026")
subj = sys.argv[1] if len(sys.argv) > 1 else "01"
WITH_TEE = "--with-tee" in sys.argv
FS = 32; LAGS = np.arange(0, int(0.6 * FS)); ALPHA = 1e3

raw = mne.io.read_raw_fif(f"{D}/ds005574/sub-{subj}_highgamma_ieeg.fif", preload=True)
raw.resample(FS)
Y = raw.get_data().T
Y = (Y - Y.mean(0)) / (Y.std(0) + 1e-9)
T, nch = Y.shape
print(f"sub-{subj}: {nch} chan, {T} samples @ {FS}Hz ({T/FS:.0f}s)")

sr, wav = wavfile.read(f"{D}/ds005574/podcast.wav")
if wav.ndim > 1: wav = wav.mean(1)
env = np.abs(hilbert(wav.astype(float)[::max(1, sr // 1000)]))
env_fs = sr / max(1, sr // 1000)
idx = (np.arange(T) * env_fs / FS).astype(int)
env = env[np.clip(idx, 0, len(env) - 1)]
env = (env - env.mean()) / (env.std() + 1e-9)

W = pd.read_csv(os.environ.get("CURV_CSV", f"{HERE}/podcast_curvature.csv"))
W = W[W.word_idx >= 3].dropna(subset=["curvature_3", "tee_k3", "entropy_small", "surp_xl"])
def z(a): a = np.asarray(a, float); return (a - np.nanmean(a)) / (np.nanstd(a) + 1e-9)
onset = np.round(W.start.values * FS).astype(int)
keep = (onset >= 0) & (onset < T); onset = onset[keep]; Wk = W[keep]
def clean(w): return re.sub(r"[^A-Za-z0-9']", "", str(w)).lower()
cw = [clean(w) for w in Wk.word.values]
cols = {"curv": z(Wk.curvature_3), "surp_xl": z(Wk.surp_xl), "entropy": z(Wk.entropy_small),
        "tee": z(Wk.tee_k3),
        "logfreq": z([zipf_frequency(w, "en") if w else 0.0 for w in cw]),
        "wlen": z([len(w) for w in cw]), "onset": np.ones(keep.sum())}
def impulse(v):
    s = np.zeros(T); s[onset] = v; return s
imp = {k: impulse(v) for k, v in cols.items()}; imp["env"] = env
def lagmat(x):   # zero-padded shift (np.roll would wrap the end onto the start)
    out = np.zeros((len(x), len(LAGS)))
    for j, L in enumerate(LAGS):
        out[L:, j] = x[:len(x) - L] if L else x
    return out
X = {k: lagmat(v) for k, v in imp.items()}
def design(keys): return np.column_stack([X[k] for k in keys])

NUIS = ["env", "onset", "logfreq", "wlen"] + (["tee"] if WITH_TEE else [])
FULL = NUIS + ["surp_xl", "entropy", "curv"]
kf = KFold(5, shuffle=False)
def cv_score(keys):
    Xm = design(keys); pred = np.zeros_like(Y)
    for tr, te in kf.split(Xm):
        pred[te] = Ridge(alpha=ALPHA).fit(Xm[tr], Y[tr]).predict(Xm[te])
    return np.array([np.corrcoef(pred[:, c], Y[:, c])[0, 1] for c in range(nch)])

s_full = cv_score(FULL)
uniq = {k: s_full - cv_score([x for x in FULL if x != k]) for k in ("curv", "surp_xl", "entropy")}
for k, u in uniq.items():
    print(f"  unique {k:8s} mean r {u.mean():+.5f}   chans>0 {(u > 0).sum()}/{nch}")
r = Ridge(alpha=ALPHA).fit(design(FULL), Y)
b = FULL.index("curv") * len(LAGS)
trf = r.coef_[:, b:b + len(LAGS)].mean(0)
np.savez(f"{D}/trf_curv_sub{subj}{'_tee' if WITH_TEE else ''}.npz", full=s_full,
         uniq_curv=uniq["curv"], uniq_surp=uniq["surp_xl"], uniq_ent=uniq["entropy"],
         trf=trf, lags=LAGS / FS, ch_names=np.array(raw.ch_names))
print(f"saved trf_curv_sub{subj}{'_tee' if WITH_TEE else ''}.npz")
