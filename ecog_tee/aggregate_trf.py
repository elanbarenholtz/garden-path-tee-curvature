"""
Aggregate per-subject TRF results (trf_sub{01..09}.npz) into the across-subject
test: is TEE's unique encoding contribution > 0 across the 9 subjects?
This is the clean inference (subject as the unit), avoiding the spatial-
autocorrelation inflation of per-channel tests.
"""
import numpy as np, glob, re
from scipy import stats

D = "/Users/elansmini/Research/Garden_Path/data/zou2026"
subs = sorted(re.search(r"trf_sub(\d+)", f).group(1)
              for f in glob.glob(f"{D}/trf_sub*.npz"))
print(f"subjects: {subs}\n")

rows = []
trfs = []
for s in subs:
    d = np.load(f"{D}/trf_sub{s}.npz", allow_pickle=True)
    ut, us = d["uniq_tee"], d["uniq_surp"]
    sc = d["scores"].item()
    rows.append(dict(s=s, n_ch=len(ut),
                     tee_uniq=ut.mean(), surp_uniq=us.mean(),
                     tee_pos=(ut > 0).mean(), full_max=sc["full"].max(),
                     peak_ms=float(d["lags"][np.argmax(np.abs(d["trf"]))]*1000)))
    trfs.append(d["trf"])
    lags = d["lags"]

print(f"{'subj':5s} {'n_ch':>4s} {'TEE_uniq':>9s} {'surp_uniq':>9s} "
      f"{'TEE %ch>0':>9s} {'full_max_r':>10s} {'TEE_peak_ms':>11s}")
for r in rows:
    print(f"{r['s']:5s} {r['n_ch']:>4d} {r['tee_uniq']:>+9.4f} {r['surp_uniq']:>+9.4f} "
          f"{r['tee_pos']*100:>8.0f}% {r['full_max']:>10.3f} {r['peak_ms']:>11.0f}")

tee = np.array([r["tee_uniq"] for r in rows])
surp = np.array([r["surp_uniq"] for r in rows])
print(f"\nAcross-subject (n={len(subs)}) unique encoding contribution:")
print(f"  TEE  mean={tee.mean():+.4f}  ({(tee>0).sum()}/{len(tee)} subjects positive)  "
      f"Wilcoxon p={stats.wilcoxon(tee, alternative='greater')[1]:.4f}  "
      f"t-test p={stats.ttest_1samp(tee,0)[1]:.4f}")
print(f"  surp mean={surp.mean():+.4f}  ({(surp>0).sum()}/{len(surp)} subjects positive)  "
      f"Wilcoxon p={stats.wilcoxon(surp, alternative='greater')[1]:.4f}  "
      f"t-test p={stats.ttest_1samp(surp,0)[1]:.4f}")

trf = np.array(trfs).mean(0)
print(f"\nGroup TEE TRF peak latency: {lags[np.argmax(np.abs(trf))]*1000:.0f} ms")
print(f"TRF (ms:weight): " + "  ".join(
    f"{int(l*1000)}:{w:+.3f}" for l, w in zip(lags, trf))[:400])
