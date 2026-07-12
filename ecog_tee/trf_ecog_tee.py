"""
ECoG x TEE correspondence via a TRF encoding model (ds005574 podcast).
Words come ~3/sec so responses overlap; we deconvolve with lagged ridge
(as Zou et al. did) instead of simple epoching.

Predictors (impulse trains at word onsets, z-scored values), each lagged 0..0.5s:
  envelope   acoustic broadband envelope (continuous nuisance; the classic confound)
  onset      word-onset impulse (nuisance: rate/timing)
  surp_xl    GPT2-XL surprisal (Zou's predictor; pipeline validation)
  tee        sink-controlled GPT2-small layer-6 TEE (the measure under test)

Per channel, 5-fold CV ridge; score = correlation(pred, actual) on held-out.
Models: base(env+onset), +surp, +tee, full. UNIQUE contribution of a predictor
= r(full) - r(full without it). Answers: does TEE track the ECoG response beyond
surprisal and acoustics, and where/when (TRF weight shape).

Usage: python3 trf_ecog_tee.py 01
"""
import sys, re, numpy as np, pandas as pd, mne
from scipy.io import wavfile
from scipy.signal import hilbert
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from wordfreq import zipf_frequency
mne.set_log_level("ERROR")

D = "/Users/elansmini/Research/Garden_Path/data/zou2026"
subj = sys.argv[1] if len(sys.argv) > 1 else "01"
FS = 32; LAGS = np.arange(0, int(0.6*FS))    # 0..~0.57s
ALPHA = 1e3

# ---- neural ----
raw = mne.io.read_raw_fif(f"{D}/ds005574/sub-{subj}_highgamma_ieeg.fif", preload=True)
raw.resample(FS)
Y = raw.get_data().T                         # (T, n_chan)
Y = (Y - Y.mean(0)) / (Y.std(0) + 1e-9)
T, nch = Y.shape
print(f"sub-{subj}: {nch} chan, {T} samples @ {FS}Hz ({T/FS:.0f}s)")

# ---- acoustic envelope ----
sr, wav = wavfile.read(f"{D}/ds005574/podcast.wav")
if wav.ndim > 1: wav = wav.mean(1)
env = np.abs(hilbert(wav.astype(float)[::max(1, sr//1000)]))   # ~1kHz then to FS
env_fs = sr / max(1, sr//1000)
idx = (np.arange(T) * env_fs / FS).astype(int)
env = env[np.clip(idx, 0, len(env)-1)]
env = (env - env.mean()) / (env.std() + 1e-9)

# ---- word predictors ----
tee = pd.read_csv(f"{D}/podcast_tee.csv")
tee = tee[tee.word_idx >= 3].dropna(subset=["tee_k3"])        # drop sink-contaminated onset words
def z(a): a=np.asarray(a,float); return (a-np.nanmean(a))/(np.nanstd(a)+1e-9)
onset_samp = np.round(tee.start.values * FS).astype(int)
keep = (onset_samp >= 0) & (onset_samp < T)
onset_samp = onset_samp[keep]
# lexical nuisances: word length and log frequency (Zipf), punctuation stripped
def clean(w): return re.sub(r"[^A-Za-z0-9']", "", str(w)).lower()
cw = [clean(w) for w in tee.word.values[keep]]
wlen = np.array([len(w) for w in cw], float)
logfreq = np.array([zipf_frequency(w, "en") if w else 0.0 for w in cw], float)
cols = {"tee": z(tee.tee_k3.values[keep]), "surp_xl": z(tee.surp_xl.values[keep]),
        "logfreq": z(logfreq), "wlen": z(wlen), "onset": np.ones(keep.sum())}
def impulse(vals):
    s = np.zeros(T); s[onset_samp] = vals; return s
imp = {k: impulse(v) for k, v in cols.items()}
imp["env"] = env

def lagmat(x):
    return np.column_stack([np.roll(x, l) for l in LAGS])
X = {k: lagmat(v) for k, v in imp.items()}

def design(keys): return np.column_stack([X[k] for k in keys])

# nuisance set now includes lexical frequency + length, plus surprisal + acoustics
NUIS = ["env", "onset", "logfreq", "wlen", "surp_xl"]
FULL = NUIS + ["tee"]
MODELS = {"nuis": NUIS, "full": FULL,
          "no_tee": NUIS, "no_surp": ["env","onset","logfreq","wlen","tee"]}

kf = KFold(5, shuffle=False)
def cv_score(keys):
    Xm = design(keys); pred = np.zeros_like(Y)
    for tr, te in kf.split(Xm):
        pred[te] = Ridge(alpha=ALPHA).fit(Xm[tr], Y[tr]).predict(Xm[te])
    return np.array([np.corrcoef(pred[:, c], Y[:, c])[0, 1] for c in range(nch)])

scores = {"nuis": cv_score(NUIS), "full": cv_score(FULL),
          "no_surp": cv_score(["env","onset","logfreq","wlen","tee"])}
uniq_tee  = scores["full"] - scores["nuis"]      # TEE beyond acoustics+onset+freq+len+surp
uniq_surp = scores["full"] - scores["no_surp"]   # surp beyond acoustics+onset+freq+len+tee
def summ(name, s):
    print(f"  {name:16s} mean r={s.mean():+.4f}  max r={s.max():+.4f}  "
          f"chans>0: {(s>0).sum()}/{nch}")
print("\nCV encoding correlation (nuisance = env+onset+freq+len+surp):")
summ("nuisance", scores["nuis"]); summ("full(+tee)", scores["full"])
print("\nUNIQUE contribution beyond ALL nuisances (incl. freq+length):")
summ("tee unique", uniq_tee)
summ("surp unique", uniq_surp)
from scipy import stats
tt = stats.wilcoxon(uniq_tee)[1]; ts = stats.wilcoxon(uniq_surp)[1]
print(f"\nWilcoxon (unique>0 across channels): tee p={tt:.2e} | surp p={ts:.2e}")
print(f"channels with positive unique TEE: {(uniq_tee>0).sum()}/{nch}")

# TEE TRF shape (mean weights over channels, from full model refit on all data)
r = Ridge(alpha=ALPHA).fit(design(FULL), Y)
tee_block = FULL.index("tee") * len(LAGS)
W = r.coef_[:, tee_block:tee_block+len(LAGS)]   # (nch, nlags)
trf = W.mean(0)
peak = LAGS[np.argmax(np.abs(trf))] / FS
print(f"\nTEE TRF peak latency: {peak*1000:.0f} ms  (weight {trf[np.argmax(np.abs(trf))]:+.4f})")
np.savez(f"{D}/trf_sub{subj}.npz", scores={k: scores[k] for k in scores},
         uniq_tee=uniq_tee, uniq_surp=uniq_surp, trf=trf, lags=LAGS/FS,
         ch_names=np.array(raw.ch_names))
print(f"saved trf_sub{subj}.npz")
