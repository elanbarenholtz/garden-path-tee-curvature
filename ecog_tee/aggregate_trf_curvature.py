"""
Across-subject test for trf_ecog_curvature.py (subject = unit, n = 9).
Usage: ECOG_DIR=/path/to/zou2026 python3 aggregate_trf_curvature.py [--with-tee]
Writes P_RESULTS_ecog_curvature[_tee].md next to this script.
"""
import os, sys, glob, re, numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ.get("ECOG_DIR", "/Users/elansmini/Research/Garden_Path/data/zou2026")
sfx = "_tee" if "--with-tee" in sys.argv else ""
fs = sorted(f for f in glob.glob(f"{D}/trf_curv_sub*.npz") if f.endswith(f"{sfx}.npz")
            and (sfx or not f.endswith("_tee.npz")))
subs = [re.search(r"sub(\d+)", f).group(1) for f in fs]
Dd = [np.load(f) for f in fs]
L = [f"# ECoG (ds005574 podcast) x curvature, n = {len(subs)} subjects",
     f"Nuisance: envelope, onset, log frequency, length{' , TEE' if sfx else ''}. "
     "Unique r = r(full) - r(full without predictor); subject = mean over channels.\n",
     "| predictor | mean unique r | subjects > 0 | Wilcoxon p (one-sided) | t-test p |",
     "|---|---|---|---|---|"]
for key, lab in (("uniq_curv", "curvature_3"), ("uniq_surp", "surprisal (XL)"), ("uniq_ent", "entropy")):
    v = np.array([d[key].mean() for d in Dd])
    L.append(f"| {lab} | {v.mean():+.5f} | {(v > 0).sum()}/{len(v)} | "
             f"{stats.wilcoxon(v, alternative='greater').pvalue:.3g} | {stats.ttest_1samp(v, 0).pvalue:.3g} |")
L.append("\nPer subject unique curvature r: " + ", ".join(
    f"{s} {d['uniq_curv'].mean():+.4f}" for s, d in zip(subs, Dd)))
trf = np.mean([d["trf"] for d in Dd], 0); lags = Dd[0]["lags"]
L.append(f"\nGroup curvature TRF peak: {lags[np.argmax(np.abs(trf))]*1000:.0f} ms "
         "(latency varied widely for TEE; do not over-read)")
out = "\n".join(L) + "\n"
open(f"{HERE}/P_RESULTS_ecog_curvature{sfx}.md", "w").write(out); print(out)
