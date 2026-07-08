"""
x2: Do coarse (neighborhood) trajectory measures predict reading time at
longer lags than fine TEE? Spillover conventions from analyze_spillover.py,
extended to L0..L3. DV = per-word mean logRT (100-3000ms filter).
Model A (fine baseline): tee3_par, tee3_perp (from parent decomposition cols
  via curvature_merged csv), surprisal, word_length, log_freq, punct.
Model B (add coarse): + ctee_m5, ntee_k100, nswitch_k100 at L0..L3.
Cluster-robust SE by sent_uid; prev_logRT autocorr control; punct-free pass.
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, load_rt, zscore, fit_cluster

RES = f"{GP}/extensions/results"; os.makedirs(RES, exist_ok=True)
S, sh = load_locked()
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
D = C.merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp"]],
            on=["story_id", "word_idx"], validate="one_to_one")
D = D.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
assert len(D) == 9840, len(D)
print(f"SAMPLE: hash={sh} n={len(D)}")

D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
FINE = ["tee3_perp", "tee3_par", "surprisal", "word_length", "log_freq",
        "has_trailing_punct"]
COARSE = ["ctee_m5", "ctee_m10", "ntee_k100", "nswitch_k100"]
LAGS = (1, 2, 3)
for v in FINE + COARSE:
    for L in LAGS:
        D[f"{v}_L{L}"] = D.groupby("story_id")[v].shift(L)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
need = [f"{v}_L{L}" for v in FINE + COARSE for L in LAGS] + ["prev_logRT"] \
    + COARSE
Dl = D.dropna(subset=need).reset_index(drop=True)
print(f"after L1-L3 lags: n = {len(Dl)}")

CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"

def build(dat, preds_base, drop_L0_punct=False):
    Zf = dat.copy(); preds = []
    for v in preds_base:
        if not (drop_L0_punct and v == "has_trailing_punct"):
            Zf[v] = zscore(dat[v]); preds.append(v)
        for L in LAGS:
            col = f"{v}_L{L}"
            Zf[col] = zscore(dat[col]); preds.append(col)
    Zf["prev_logRT"] = zscore(dat["prev_logRT"])
    return Zf, preds

def show(mod, varlist, label):
    print("\n" + "=" * 78)
    print(f"{label}   n={int(mod.nobs)}  R^2={mod.rsquared:.4f}")
    print("=" * 78)
    print(f"{'predictor':16s} {'L0':>17s} {'L1':>17s} {'L2':>17s} {'L3':>17s}")
    rows = []
    for v in varlist:
        cells = []
        for key in [v] + [f"{v}_L{L}" for L in LAGS]:
            if key not in mod.params:
                cells.append(f"{'--':>15s}")
                continue
            b, p = mod.params[key], mod.pvalues[key]
            star = "*" if p < .05 else " "
            cells.append(f"{b:+.4f}({p:.0e}){star}")
            rows.append({"model": label, "term": key, "beta": b, "p": p})
        print(f"{v:16s} " + " ".join(f"{c:>17s}" for c in cells))
    return rows

allrows = []
ZA, pA = build(Dl, FINE)
mA = fit_cluster(f"mean_logRT ~ {' + '.join(pA)} + {CTRL}", ZA)
allrows += show(mA, FINE, "A. FINE baseline (L0..L3)")

ZB, pB = build(Dl, FINE + COARSE)
mB = fit_cluster(f"mean_logRT ~ {' + '.join(pB)} + {CTRL}", ZB)
allrows += show(mB, FINE + COARSE, "B. FINE + COARSE (L0..L3)")

# coarse-only (are coarse effects there at all, without fine competition?)
ZC, pC = build(Dl, COARSE + ["surprisal", "word_length", "log_freq",
                             "has_trailing_punct"])
mC = fit_cluster(f"mean_logRT ~ {' + '.join(pC)} + {CTRL}", ZC)
allrows += show(mC, COARSE, "C. COARSE + lexical controls (no fine TEE)")

# punct-free robustness on model B
Dpf = Dl[Dl.has_trailing_punct == 0].reset_index(drop=True)
ZP, pP = build(Dpf, FINE + COARSE, drop_L0_punct=True)
mP = fit_cluster(f"mean_logRT ~ {' + '.join(pP)} + {CTRL}", ZP)
allrows += show(mP, FINE + COARSE, "D. PUNCT-FREE (current word not punct-final)")

pd.DataFrame(allrows).to_csv(f"{RES}/x2_rt_spillover.csv", index=False)
print(f"\nDONE hash={sh}")
