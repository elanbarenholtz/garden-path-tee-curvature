"""
TEE vs curvature double dissociation on the locked sample 8a6087341e (n=9840).
Pre-committed analyses, in order; raw tables only; anomalies flagged.

Conventions (from excursion_tests/e_analysis.py):
  zscore ddof=0; controls = from_start + fs2 + from_end + fe2 + C(story_id);
  cluster-robust SEs by sent_uid; partial r residualizes on
  [1, story dummies, 4 position terms], df = n - p_ctrl - 2.

Measures:
  tee_k3       short-window trajectory extrapolation error (locked sample col)
  curvature_3  King-style contextual curvature (mean step-angle, last 3 tokens)
  curvature_1  single-step angle (matches earlier compare_tee_vs_angular.py)
Targets:  closure_depth (syntax),  entropy (model uncertainty)
Punct:    has_trailing_punct = 1 if word's final char is [^A-Za-z0-9]
"""
import hashlib, re
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

GP = "/Users/elansmini/Research/Garden_Path"
M = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sample_hash = hashlib.md5(
    "|".join(f"{r.story_id}.{r.word_idx}" for r in
             M[["story_id", "word_idx"]].itertuples(index=False)).encode()
).hexdigest()[:10]
assert sample_hash == "8a6087341e", sample_hash
M["has_trailing_punct"] = M["word"].astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
HDR = f"hash = {sample_hash}   n = {len(M)}"
npunct = int(M.has_trailing_punct.sum())
print(f"SAMPLE: {HDR}")
print(f"has_trailing_punct: {npunct} punct / {len(M)-npunct} non-punct "
      f"(P1-A baseline: 1166 / 8674)\n")

MEAS = ["tee_k3", "curvature_3", "curvature_1"]
TARG = ["closure_depth", "entropy"]

def zscore(s):
    return (s - s.mean()) / s.std(ddof=0)

# ---- partial-r machinery (position + story FE, optionally + punct) ----
def build_ctrl(D, with_punct=False):
    ctrl = pd.get_dummies(D["story_id"], prefix="st", drop_first=True).astype(float)
    cols = ["from_start", "fs2", "from_end", "fe2"]
    if with_punct:
        cols = cols + ["has_trailing_punct"]
    ctrl[cols] = D[cols].values
    return np.column_stack([np.ones(len(D)), ctrl.values])

def partial_r(D, Cm, xcol, ycol):
    def res(v):
        beta, *_ = np.linalg.lstsq(Cm, v, rcond=None)
        return v - Cm @ beta
    r = float(np.corrcoef(res(D[xcol].values.astype(float)),
                          res(D[ycol].values.astype(float)))[0, 1])
    dfree = len(D) - Cm.shape[1] - 2
    t = r * np.sqrt(dfree / max(1e-12, 1 - r ** 2))
    return r, 2 * stats.t.sf(abs(t), dfree)

# ============================================================ C1
print("=" * 74)
print(f"C1. Uncontrolled Pearson r (full n; cf. 2-story head-to-head)   {HDR}")
print("=" * 74)
print(f"{'measure':12s} | {'x closure_depth':>22s} | {'x entropy':>22s}")
print(f"{'2-story ref':12s} | {'tee +0.081 / ang +0.024':>22s} | "
      f"{'tee -0.019 / ang +0.114':>22s}")
print("-" * 74)
for m in MEAS:
    cells = []
    for t in TARG:
        r, p = stats.pearsonr(M[m], M[t])
        cells.append(f"{r:+.4f} (p={p:.1e})")
    print(f"{m:12s} | {cells[0]:>22s} | {cells[1]:>22s}")
r_tc, p_tc = stats.pearsonr(M["tee_k3"], M["curvature_3"])
r_tc1, p_tc1 = stats.pearsonr(M["tee_k3"], M["curvature_1"])
print(f"\nmeasure overlap: r(tee_k3, curvature_3) = {r_tc:+.4f} (p={p_tc:.1e}); "
      f"r(tee_k3, curvature_1) = {r_tc1:+.4f} (p={p_tc1:.1e})")

# ============================================================ C2
print("\n" + "=" * 74)
print(f"C2. Partial r | position + story FE   {HDR}")
print("=" * 74)
Cm = build_ctrl(M, with_punct=False)
print(f"{'measure':12s} | {'x closure_depth':>22s} | {'x entropy':>22s}")
print("-" * 74)
for m in MEAS:
    cells = [f"{partial_r(M,Cm,m,t)[0]:+.4f} (p={partial_r(M,Cm,m,t)[1]:.1e})"
             for t in TARG]
    print(f"{m:12s} | {cells[0]:>22s} | {cells[1]:>22s}")

# ============================================================ C3
print("\n" + "=" * 74)
print(f"C3. Partial r | position + story FE + has_trailing_punct   {HDR}")
print("=" * 74)
Cmp = build_ctrl(M, with_punct=True)
print(f"{'measure':12s} | {'x closure_depth':>22s} | {'x entropy':>22s}")
print("-" * 74)
for m in MEAS:
    cells = [f"{partial_r(M,Cmp,m,t)[0]:+.4f} (p={partial_r(M,Cmp,m,t)[1]:.1e})"
             for t in TARG]
    print(f"{m:12s} | {cells[0]:>22s} | {cells[1]:>22s}")

# ============================================================ C4
print("\n" + "=" * 74)
Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
print(f"C4. Partial r on PUNCT-FREE subsample | position + story FE")
print(f"    FORCED DEVIATION. locked {HDR}; punct-free n = {len(Mpf)}")
print("=" * 74)
Cmf = build_ctrl(Mpf, with_punct=False)
print(f"{'measure':12s} | {'x closure_depth':>22s} | {'x entropy':>22s}")
print("-" * 74)
for m in MEAS:
    cells = [f"{partial_r(Mpf,Cmf,m,t)[0]:+.4f} (p={partial_r(Mpf,Cmf,m,t)[1]:.1e})"
             for t in TARG]
    print(f"{m:12s} | {cells[0]:>22s} | {cells[1]:>22s}")

# ============================================================ C5
print("\n" + "=" * 74)
print(f"C5. Double-dissociation joint regressions   {HDR}")
print("    DV = z(measure) ~ closure_depth + entropy + surprisal + word_length")
print("         + log_freq + has_trailing_punct + position + C(story_id)")
print("    cluster-robust SE by sent_uid; all predictors z-scored (ddof=0)")
print("=" * 74)
Z = M.copy()
zcols = ["tee_k3", "curvature_3", "curvature_1", "closure_depth", "entropy",
         "surprisal", "word_length", "log_freq", "has_trailing_punct"]
for c in zcols:
    Z[c] = zscore(M[c])
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"

def fit(formula, data):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["sent_uid"]})

for m in ["tee_k3", "curvature_3"]:
    mod = fit(f"{m} ~ closure_depth + entropy + surprisal + word_length"
              f" + log_freq + has_trailing_punct + {CTRL}", Z)
    print(f"\nDV = z({m}):")
    for t in ["closure_depth", "entropy", "surprisal", "word_length",
              "log_freq", "has_trailing_punct"]:
        print(f"  {t:20s} beta = {mod.params[t]:+.4f}  se = {mod.bse[t]:.4f}"
              f"  p = {mod.pvalues[t]:.3e}")
    print(f"  R^2 = {mod.rsquared:.4f}  n = {int(mod.nobs)}")

# ============================================================ C6
print("\n" + "=" * 74)
print(f"C6. Does curvature absorb TEE's closure effect?   {HDR}")
print("    DV = z(tee_k3); add z(curvature_3) as a predictor")
print("=" * 74)
base = fit(f"tee_k3 ~ closure_depth + entropy + surprisal + word_length"
           f" + log_freq + has_trailing_punct + {CTRL}", Z)
wcur = fit(f"tee_k3 ~ closure_depth + curvature_3 + entropy + surprisal"
           f" + word_length + log_freq + has_trailing_punct + {CTRL}", Z)
print(f"  closure_depth beta  (no curvature) = {base.params['closure_depth']:+.4f}"
      f"  p = {base.pvalues['closure_depth']:.3e}")
print(f"  closure_depth beta  (+ curvature)  = {wcur.params['closure_depth']:+.4f}"
      f"  p = {wcur.pvalues['closure_depth']:.3e}")
print(f"  curvature_3 beta    (in that model)= {wcur.params['curvature_3']:+.4f}"
      f"  p = {wcur.pvalues['curvature_3']:.3e}")

# reverse: does TEE absorb curvature's entropy effect?
baseC = fit(f"curvature_3 ~ entropy + closure_depth + surprisal + word_length"
            f" + log_freq + has_trailing_punct + {CTRL}", Z)
wtee = fit(f"curvature_3 ~ entropy + tee_k3 + closure_depth + surprisal"
           f" + word_length + log_freq + has_trailing_punct + {CTRL}", Z)
print(f"\n  entropy beta on curvature_3 (no tee) = {baseC.params['entropy']:+.4f}"
      f"  p = {baseC.pvalues['entropy']:.3e}")
print(f"  entropy beta on curvature_3 (+ tee)  = {wtee.params['entropy']:+.4f}"
      f"  p = {wtee.pvalues['entropy']:.3e}")
print(f"  tee_k3 beta on curvature_3           = {wtee.params['tee_k3']:+.4f}"
      f"  p = {wtee.pvalues['tee_k3']:.3e}")

print(f"\nAll results: {HDR}")
