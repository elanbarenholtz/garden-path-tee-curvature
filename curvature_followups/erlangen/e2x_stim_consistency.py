"""Cross-subject check of the Erlangen stimulus channels: did every subject hear the same audio, in the same order?
Usage: python3 -I e2x_stim_consistency.py /path/to/erlangen_meg"""
import glob, re, sys, numpy as np, mne
from scipy.signal import hilbert, butter, sosfiltfilt, fftconvolve, resample_poly
mne.set_log_level("ERROR")
D = sys.argv[1]
def load(n):
    return mne.io.read_raw_fif(f"{D}/Prob{n}_stimuli_channel_raw.fif", preload=True).get_data()[0]
def env(x):
    e = np.abs(hilbert(x - x.mean())); e = sosfiltfilt(butter(4, 10, fs=200, output="sos"), e)
    e = resample_poly(e, 1, 4); return (e - e.mean()) / e.std()          # 50 Hz
def raw(x):
    y = sosfiltfilt(butter(4, [20, 95], btype="band", fs=200, output="sos"), x); return y / y.std()
def nxc(sig, tpl):
    m = len(tpl); t = tpl - tpl.mean(); num = fftconvolve(sig, t[::-1], "valid")
    cs, cs2 = np.cumsum(np.r_[0, sig]), np.cumsum(np.r_[0, sig**2])
    s1, s2 = cs[m:] - cs[:-m], cs2[m:] - cs2[:-m]
    return num / (np.sqrt(np.maximum(s2 - s1**2 / m, 1e-12)) * np.linalg.norm(t))
subs = sorted(int(re.search(r"Prob(\d+)_", f).group(1)) for f in glob.glob(f"{D}/Prob*_stimuli_channel_raw.fif"))
X = {n: load(n) for n in subs}
print("durations (min):", {n: round(len(x)/200/60, 1) for n, x in X.items()})
ref = X[1]; E1, R1 = env(ref), raw(ref)
# active 60 s windows of the reference
W = 60
starts = [s for s in range(30, int(len(ref)/200) - W, W) if np.std(ref[s*200:(s+W)*200]) > 0.3*np.std(ref)]
print(f"reference windows: {len(starts)} x {W}s\n")
print(f"{'subj':>4} {'env: matched':>13} {'lags(s)':>22} {'raw: peak r med':>16} {'raw lag spread(ms)':>18}")
for n in subs:
    if n == 1: continue
    E, R = env(X[n]), raw(X[n])
    lags, zs, rr, rl = [], [], [], []
    for s in starts:
        c = nxc(E, E1[s*50:(s+W)*50]); j = int(np.argmax(c)); z = (c[j]-c.mean())/c.std()
        if z > 8: lags.append(j/50 - s); zs.append(z)
        # raw: search +-3 s around the envelope match
        if z > 8:
            c0 = int((j/50)*200); seg = R[max(0, c0-600): c0 + W*200 + 600]
            cr = nxc(seg, R1[s*200:(s+W)*200]); k = int(np.argmax(cr))
            rr.append(cr[k]); rl.append((max(0, c0-600) + k)/200 - s)
    L = np.round(np.array(lags), 1)
    uniq = np.unique(np.round(L))
    print(f"{n:>4} {len(lags):>6}/{len(starts):<6} {str(list(uniq[:4]))[:22]:>22} "
          f"{np.median(rr) if rr else float('nan'):>16.3f} "
          f"{1000*np.std(np.array(rl) - np.median(rl)) if rl else float('nan'):>18.1f}")

print("\nORDER CHECK: position in each subject of each ref window; segments of constant lag")
# reference silence gaps (chapter breaks) in subject 1
r = np.sqrt(np.convolve(ref**2, np.ones(200)/200, "same"))
quiet = r < 0.15*np.median(r[r > np.percentile(r, 20)])
runs, s0 = [], None
for i, q in enumerate(np.r_[quiet, False]):
    if q and s0 is None: s0 = i
    if not q and s0 is not None:
        if i - s0 > 5*200: runs.append((s0/200, i/200))
        s0 = None
print("subject 1 silences >5 s (s):", [(round(a), round(b)) for a, b in runs])
for n in subs:
    if n == 1: continue
    E = env(X[n]); pos = []
    for s in starts:
        c = nxc(E, E1[s*50:(s+W)*50]); j = int(np.argmax(c)); z = (c[j]-c.mean())/c.std()
        pos.append(j/50 if z > 8 else np.nan)
    p = np.array(pos); ok = ~np.isnan(p)
    mono = np.all(np.diff(p[ok]) > 0)
    lag = p - np.array(starts); segs = []
    for v in lag[ok]:
        if not segs or abs(v - segs[-1][0]) > 1.0: segs.append([v, 1])
        else: segs[-1][1] += 1
    print(f"  {n:>2}: same order {mono}   lag segments (lag s x windows): "
          + " ".join(f"{v:+.0f}x{k}" for v, k in segs))
