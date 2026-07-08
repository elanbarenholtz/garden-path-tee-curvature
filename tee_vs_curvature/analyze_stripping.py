"""
Magnitude-stripping series + residual decomposition, locked sample 8a6087341e.
Tests the interpretation: syntactic structure lives in the DISPLACEMENT
magnitude of the trajectory deviation, not in its turning ANGLE.

Series (magnitude information retained -> removed), all anchored at final subword:
  tee_k3       raw extrapolation-error DISTANCE          (full magnitude)
  teeN_k3      distance / mean local step size           (scale-normalized)
  curvature_3  mean angle between successive steps        (pure angle, King)
  curvature_1  single-step angle
Decomposition of the k=3 residual r = h_t - pred (tee_k3 = sqrt(par^2+perp^2)):
  tee3_par     |along-heading| magnitude  (overshoot/undershoot on the line)
  tee3_perp    lateral magnitude          (off-the-line deviation)

Identical spec across all measures: partial r | position + story FE,
then + has_trailing_punct, then punct-free subsample. Targets: closure_depth,
entropy. cluster/df conventions per e_analysis.py.
"""
import hashlib
import numpy as np
import pandas as pd
from scipy import stats

GP = "/Users/elansmini/Research/Garden_Path"
M = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     M[["story_id","word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
M["has_trailing_punct"] = M["word"].astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
HDR = f"hash = {sh}   n = {len(M)}"
print(f"SAMPLE: {HDR}\n")

# identity check: tee_k3^2 == par^2 + perp^2
lhs = M.tee_k3.values**2
rhs = M.tee3_par.values**2 + M.tee3_perp.values**2
print(f"decomposition identity max|tee^2 - (par^2+perp^2)| = "
      f"{np.nanmax(np.abs(lhs-rhs)):.3e}  (should be ~0)")
print(f"mean tee3_par = {M.tee3_par.mean():.3f}  mean tee3_perp = {M.tee3_perp.mean():.3f}"
      f"  (lateral vs along-heading share of the deviation)\n")

def build_ctrl(D, with_punct=False):
    ctrl = pd.get_dummies(D["story_id"], prefix="st", drop_first=True).astype(float)
    cols = ["from_start","fs2","from_end","fe2"] + (["has_trailing_punct"] if with_punct else [])
    ctrl[cols] = D[cols].values
    return np.column_stack([np.ones(len(D)), ctrl.values])

def partial_r(D, Cm, x, y):
    def res(v):
        beta,*_ = np.linalg.lstsq(Cm, v, rcond=None); return v - Cm@beta
    r = float(np.corrcoef(res(D[x].values.astype(float)), res(D[y].values.astype(float)))[0,1])
    dfree = len(D)-Cm.shape[1]-2
    t = r*np.sqrt(dfree/max(1e-12,1-r**2))
    return r, 2*stats.t.sf(abs(t), dfree)

SERIES = ["tee_k3","teeN_k3","curvature_3","curvature_1"]
DECOMP = ["tee3_par","tee3_perp"]

def block(title, D, with_punct):
    Cm = build_ctrl(D, with_punct)
    print("="*72); print(f"{title}   (n={len(D)})"); print("="*72)
    print(f"{'measure':14s} | {'x closure_depth':>21s} | {'x entropy':>21s}")
    print("-"*72)
    for m in SERIES + ["--"] + DECOMP:
        if m == "--":
            print("-"*72); continue
        c = partial_r(D,Cm,m,"closure_depth"); e = partial_r(D,Cm,m,"entropy")
        print(f"{m:14s} | {c[0]:+.4f} (p={c[1]:.1e}) | {e[0]:+.4f} (p={e[1]:.1e})")
    print()

block("D1. partial r | position + story FE", M, False)
block("D2. partial r | position + story FE + has_trailing_punct", M, True)
Mpf = M[M.has_trailing_punct==0].reset_index(drop=True)
block("D3. partial r | position + story FE   (PUNCT-FREE, forced deviation)", Mpf, False)

# correlations among the series
print("="*72); print(f"Cross-correlations among the series   {HDR}"); print("="*72)
allm = ["tee_k3","teeN_k3","curvature_3","curvature_1","tee3_par","tee3_perp"]
C = M[allm].corr()
print(C.round(3).to_string())
print(f"\nAll results: {HDR}")
