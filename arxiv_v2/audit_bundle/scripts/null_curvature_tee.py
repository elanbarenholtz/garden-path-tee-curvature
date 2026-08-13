"""
NULL MODEL: is the curvature(t-1) -> TEE(t) relationship mechanical?
====================================================================
In the locked sample, curvature at t-1 forecasts LOWER TEE at t
(beta = -0.151 for curvature_3, -0.225 for curvature_1).

Candidate mechanical account: a bent fit window has partially cancelling steps,
so the least-squares slope is small, so the extrapolation barely projects past
the last point and cannot miss by much. A straight window gives a long
extrapolation vector with more room to overshoot. If so, the negative
relationship should appear in ANY trajectory with no language in it.

Test: synthetic 768-dim walks with no linguistic content, generated with a
tunable directional persistence so curvature varies naturally. Step-size
distribution matched to the real layer-6 word-to-word displacements
(mean 64.0, sd 9.4 from displacement_8a6087341e.csv).

We compute exactly the same two quantities as the real analysis:
  curvature_3(t-1)  = mean of 3 successive angles ending at t-1
  TEE(t)            = ||h_t - extrapolate(OLS fit over h_{t-3..t-1})||
and regress z(TEE_t) on z(curvature_{t-1}).

Reference values to beat (real data, position + story FE + punct + lexical):
  curvature_3 -> TEE : -0.151
  curvature_1 -> TEE : -0.225
Same-position correlations in real data: r(TEE, curv_3) = +0.104,
                                         r(TEE, curv_1) = +0.398
"""

import numpy as np
import pandas as pd
from scipy import stats

RNG = np.random.default_rng(20260727)
D = 768
N_WALKS = 400
LEN = 60
STEP_MEAN, STEP_SD = 64.0, 9.4        # matched to real layer-6 word steps


def make_walk(n, persistence):
    """Random walk with directional persistence in [0,1).
    0 = isotropic (high curvature); ->1 = strongly directional (low curvature)."""
    dirs = np.zeros((n, D))
    v = RNG.normal(size=D)
    v /= np.linalg.norm(v)
    for i in range(n):
        new = RNG.normal(size=D)
        new /= np.linalg.norm(new)
        v = persistence * v + (1 - persistence) * new
        v /= np.linalg.norm(v)
        dirs[i] = v
    mags = RNG.normal(STEP_MEAN, STEP_SD, size=n).clip(1.0)
    steps = dirs * mags[:, None]
    return np.cumsum(steps, axis=0)


def angle(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return np.nan
    c = np.clip(np.dot(a, b) / (na * nb), -1, 1)
    return float(np.arccos(c))


def measures(H):
    """Return per-index (curv_1, curv_3, tee_k3) with the project's conventions."""
    n = H.shape[0]
    step = lambda i: H[i] - H[i - 1]
    ang = np.full(n, np.nan)
    for i in range(2, n):
        ang[i] = angle(step(i), step(i - 1))
    curv1 = ang.copy()
    curv3 = np.full(n, np.nan)
    for i in range(4, n):
        curv3[i] = np.nanmean(ang[i - 2:i + 1])
    tee = np.full(n, np.nan)
    for t in range(3, n):
        Y = H[t - 3:t]
        A = np.column_stack([np.ones(3), np.arange(3)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[t] = np.linalg.norm(H[t] - (c[0] + c[1] * 3))
    return curv1, curv3, tee


rows = []
# a spread of persistence values so curvature varies across and within walks
for w in range(N_WALKS):
    p = RNG.uniform(-0.9, 0.9)
    H = make_walk(LEN, p)
    c1, c3, tee = measures(H)
    for t in range(5, LEN):
        rows.append({"walk": w, "persistence": p, "t": t,
                     "curv1_prev": c1[t - 1], "curv3_prev": c3[t - 1],
                     "curv1": c1[t], "curv3": c3[t], "tee": tee[t]})

df = pd.DataFrame(rows).dropna()
print(f"synthetic: {N_WALKS} walks x {LEN} steps -> n = {len(df):,} usable points")
print(f"curvature_3 range {df.curv3.min():.2f}-{df.curv3.max():.2f} "
      f"(real data mean ~1.99)")
print(f"TEE mean {df.tee.mean():.1f} (real data mean ~94.9)\n")


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


print("=" * 74)
print("CROSS-POSITION: curvature(t-1) -> TEE(t)   [real data: -0.151 / -0.225]")
print("=" * 74)
for lab, col in [("curvature_3(t-1)", "curv3_prev"), ("curvature_1(t-1)", "curv1_prev")]:
    r, p = stats.pearsonr(z(df[col]), z(df.tee))
    print(f"  {lab:<22} r = {r:>+7.4f}   p = {p:.2e}")

print("\n" + "=" * 74)
print("SAME-POSITION: curvature(t) vs TEE(t)   [real data: +0.104 / +0.398]")
print("=" * 74)
for lab, col in [("curvature_3(t)", "curv3"), ("curvature_1(t)", "curv1")]:
    r, p = stats.pearsonr(z(df[col]), z(df.tee))
    print(f"  {lab:<22} r = {r:>+7.4f}   p = {p:.2e}")

print("\n" + "=" * 74)
print("WITHIN-WALK (persistence held fixed): does it survive?")
print("=" * 74)
res = []
for w, g in df.groupby("walk"):
    if len(g) < 20:
        continue
    res.append(stats.pearsonr(g.curv3_prev, g.tee)[0])
res = np.array(res)
print(f"  mean within-walk r(curv3_prev, TEE) = {res.mean():+.4f}   "
      f"{(res < 0).sum()}/{len(res)} negative   "
      f"Wilcoxon p = {stats.wilcoxon(res).pvalue:.2e}")

print("\n" + "=" * 74)
print("MECHANISM CHECK: does bent window -> short fitted step?")
print("=" * 74)
sub = df.dropna(subset=["curv3_prev"])
fit_norm = []
for w, g in df.groupby("walk"):
    pass
# recompute fitted-slope norms directly on a fresh set of walks
norms, curvs = [], []
for w in range(120):
    p = RNG.uniform(-0.9, 0.9)
    H = make_walk(LEN, p)
    c1, c3, tee = measures(H)
    for t in range(5, LEN):
        Y = H[t - 3:t]
        A = np.column_stack([np.ones(3), np.arange(3)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        if not np.isnan(c3[t - 1]):
            norms.append(np.linalg.norm(c[1]))     # fitted per-step direction norm
            curvs.append(c3[t - 1])
r, p = stats.pearsonr(curvs, norms)
print(f"  r(curvature(t-1), ||fitted slope||) = {r:+.4f}  p = {p:.2e}")
print("  (strong negative => bent windows produce short extrapolation vectors,")
print("   which is the proposed mechanism)")
