"""F7b -- subject-level d_z for the headline curvature effect as a function of
words read per participant (random contiguous story subsets are not possible for
all sizes, so words are subsampled at random within participant; 20 repeats)."""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(f"{HERE}/f5_geometry_rt.py").read().split("res = []")[0])
CTRL = "z_surprisal + z_entropy + z_log_freq_fixed + z_word_length + z_from_start"
rng = np.random.default_rng(1)
G = {p: g for p, g in D.groupby("pid") if len(g) >= 3000}
print(f"participants with >=3000 words: {len(G)}")
def nfor(dz, pw=.8):
    n = 3
    while stats.nct.sf(stats.t.ppf(.975, n - 1), n - 1, dz * np.sqrt(n)) < pw: n += 1
    return n
for k in (250, 500, 1000, 2000, 3000):
    dzs = []
    for rep in range(20):
        sl = [smf.ols(f"log_RT ~ {CTRL} + z_curvature_3", g.sample(k, random_state=int(rng.integers(1e9)))).fit()
              .params["z_curvature_3"] for g in G.values()]
        sl = np.array(sl); dzs.append(sl.mean() / sl.std(ddof=1))
    dz = np.mean(dzs)
    print(f"  {k:>5} words/participant: d_z {dz:.2f}   N for 80% power {nfor(dz)}, 90% {nfor(dz, .9)}")
