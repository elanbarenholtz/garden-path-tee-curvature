"""
IS THE TRAJECTORY EFFECT THRESHOLDED, AND IS THE LOW-DECILE STRUCTURE REAL?
===========================================================================
The decile profiles are flat across deciles 1-7 and rise from 8 upward, which
suggests a threshold rather than a graded effect. Two things have to be checked
before that story is told.

(1) The apparent bump at decile 2 in Natural Stories (+0.0065) is nearly as high
    as decile 8 (+0.0075). Under a threshold account it should be flat. Is it
    real? Overall split-half stability was r = .88, but that could be carried
    entirely by the top-end rise. So: split-half stability computed on deciles
    1-7 ONLY, and per-decile tests against zero.

(2) If the effect is thresholded, a single indicator for the top decile should
    fit about as well as a linear term -- and a hinge (flat below a knot, linear
    above) should fit better than either. A spline already lost to linear, which
    is consistent with a threshold: a spline spends parameters modelling wiggle
    in the flat region, a hinge spends one in the right place.

TESTS
  T1  per-decile mean with 95% CI across participants, and t vs zero, so we can
      see which deciles are actually distinguishable from the baseline
  T2  split-half shape stability restricted to deciles 1-7
  T3  linear vs top-decile indicator vs hinge, by AIC within participant
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"
RNG = np.random.default_rng(20260810)
NBIN = 10


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
ns = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                 "log_freq"]], on=["story_id", "zone"], how="inner")
ns["log_RT"] = np.log(ns.RT)
ns = ns.sort_values(["participant", "story_id", "zone"])
ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                       "prev_log_RT", "tee_k3", "surprisal"]).rename(
    columns={"tee_k3": "tee"})

d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
d = d.merge(pd.read_csv(f"{GPC}/sap_measures_L6k3.csv"),
            on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
d["word_length"] = d.EachWord.str.len()
d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
d["from_start"] = d.WordPosition.astype(float)
d["fs2"] = d.from_start ** 2
d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
d["fe2"] = d.from_end ** 2
d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
d["log_RT"] = np.log(d.RT)
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq",
                     "log_RT"]).rename(columns={"surp": "surprisal"})

CORPORA = [
    ("Natural Stories", ns, ["surprisal", "word_length", "log_freq", "zone",
                             "prev_log_RT"], 300),
    ("Garden-path corpus", d, ["surprisal", "word_length", "log_freq", "punct",
                               "from_start", "fs2", "from_end", "fe2"], 100),
]

for name, df, ctrl, minn in CORPORA:
    print("=" * 86)
    print(name)
    print("=" * 86)
    profs, aic = [], {"linear": [], "top-decile indicator": [], "hinge": []}
    for pid, s in df.groupby("participant"):
        s = s.dropna(subset=["log_RT", "tee"] + ctrl)
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in ctrl])
        y = zs(s.log_RT.values)
        fit = sm.OLS(y, sm.add_constant(X)).fit()
        res = y - fit.fittedvalues
        t = s.tee.values
        try:
            q = pd.qcut(t, NBIN, labels=False, duplicates="drop")
        except ValueError:
            continue
        if len(np.unique(q)) < NBIN:
            continue
        profs.append([res[q == b].mean() for b in range(NBIN)])

        # T3: three shapes for the trajectory term
        knot = np.percentile(t, 70)
        terms = {"linear": zs(t),
                 "top-decile indicator": (q == NBIN - 1).astype(float),
                 "hinge": np.clip(t - knot, 0, None)}
        for k, v in terms.items():
            Xk = np.column_stack([zs(v)] + [zs(s[c].values) for c in ctrl])
            aic[k].append(sm.OLS(y, sm.add_constant(Xk)).fit().aic)

    P = np.array(profs)
    n = len(P)
    print(f"  {n} participants\n")

    print("  T1  per-decile residual mean (across participants)")
    print(f"      {'decile':>7}{'mean':>10}{'95% CI':>20}{'t':>8}{'p':>10}")
    for b in range(NBIN):
        col = P[:, b]
        se = col.std(ddof=1) / np.sqrt(n)
        t_, p_ = stats.ttest_1samp(col, 0)
        star = " *" if p_ < .05 else ""
        print(f"      {b+1:>7}{col.mean():>+10.4f}"
              f"   [{col.mean()-1.96*se:+.4f}, {col.mean()+1.96*se:+.4f}]"
              f"{t_:>8.2f}{p_:>10.1e}{star}")

    def splithalf(cols, reps=200):
        r = []
        for _ in range(reps):
            i = RNG.permutation(n)
            a = P[i[:n // 2]][:, cols].mean(0)
            b = P[i[n // 2:]][:, cols].mean(0)
            r.append(np.corrcoef(a, b)[0, 1])
        return np.array(r)

    all_r = splithalf(list(range(NBIN)))
    low_r = splithalf(list(range(7)))
    print(f"\n  T2  split-half shape stability")
    print(f"      all deciles      r = {all_r.mean():+.3f} (sd {all_r.std():.3f})")
    print(f"      deciles 1-7 only r = {low_r.mean():+.3f} (sd {low_r.std():.3f})"
          f"   <- is the flat region real structure?")

    print(f"\n  T3  shape of the trajectory term (AIC, lower is better)")
    base = np.array(aic["linear"])
    for k in ["linear", "top-decile indicator", "hinge"]:
        v = np.array(aic[k])
        d_ = base - v
        print(f"      {k:<24} mean dAIC vs linear = {d_.mean():+7.2f}   "
              f"better in {(d_ > 0).mean():5.1%} of participants")
    print()
