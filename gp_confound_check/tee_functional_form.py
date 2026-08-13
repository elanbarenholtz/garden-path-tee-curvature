"""
IS A LINEAR FIT THE RIGHT SUMMARY OF THE TRAJECTORY EFFECT?
============================================================
We tested whether SURPRISAL's functional form matters (it does: splining it
improves fit substantially). We never tested the functional form of the
trajectory measure itself, and the partial-effect profiles now suggest we
should: in Natural Stories the profile rises roughly monotonically, but in the
garden-path corpus it is jagged and non-monotone, so a positive linear
coefficient there may be summarising a shape that is not a line.

TESTS, per corpus, subject-level throughout:

  F1  linear vs spline in TEE. Fit z(logRT) with TEE entered linearly, then as
      a B-spline (df = 3, 5, 8), everything else held fixed. Compare by AIC
      within participant, then across participants. If the spline does not
      improve fit, linear is an adequate summary and the jaggedness in the
      profile is noise.

  F2  monotonicity. Across the ten within-participant deciles, count the
      fraction of participants whose profile is monotonically increasing, and
      test the decile means for trend (Spearman rho of mean residual against
      decile, per participant). A real effect that is linear should give a high
      positive rho; a jagged profile should not.

  F3  shape stability. Split participants at random into two halves and
      correlate the two decile profiles. A shape driven by real structure
      should replicate across halves; noise should not. Repeated 50 times.

  F4  is the effect carried by the extremes? Refit the linear model dropping the
      top and bottom decile of TEE. If the coefficient survives, the effect is
      distributed; if it collapses, it is an extremes phenomenon.

Reported for both corpora so they can be compared directly.
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
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


# ------------------------------------------------------------------ corpora
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
    print("=" * 84)
    print(name)
    print("=" * 84)
    print(f"  {len(df):,} rows, {df.participant.nunique():,} participants")

    # ---------------- F1: linear vs spline in TEE ----------------
    zc = ["log_RT", "tee"] + ctrl
    gains = {3: [], 5: [], 8: []}
    for pid, s in df.groupby("participant"):
        s = s.dropna(subset=zc)
        if len(s) < minn:
            continue
        s = s.copy()
        for c in zc:
            s["z_" + c] = zs(s[c].values)
        base = "z_log_RT ~ " + " + ".join("z_" + c for c in ctrl)
        try:
            lin = smf.ols(base + " + z_tee", s).fit()
            for k in gains:
                sp = smf.ols(base + f" + bs(z_tee, df={k})", s).fit()
                gains[k].append(lin.aic - sp.aic)
        except Exception:
            continue
    print("\n  F1  linear vs spline in TEE  (positive = spline fits better)")
    for k, v in gains.items():
        v = np.array(v)
        print(f"      df={k}:  mean dAIC = {v.mean():+7.2f}   "
              f"spline better in {(v > 0).mean():5.1%} of participants   "
              f"n={len(v)}")

    # ---------------- F2: monotonicity of the decile profile ----------------
    rhos, monos, profs = [], [], []
    for pid, s in df.groupby("participant"):
        s = s.dropna(subset=zc)
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in ctrl])
        y = zs(s.log_RT.values)
        res = y - sm.OLS(y, sm.add_constant(X)).fit().fittedvalues
        try:
            q = pd.qcut(s.tee.values, NBIN, labels=False, duplicates="drop")
        except ValueError:
            continue
        if len(np.unique(q)) < NBIN:
            continue
        prof = np.array([res[q == b].mean() for b in range(NBIN)])
        profs.append(prof)
        rhos.append(stats.spearmanr(np.arange(NBIN), prof).statistic)
        monos.append(bool(np.all(np.diff(prof) > 0)))
    rhos = np.array(rhos)
    P = np.array(profs)
    print(f"\n  F2  monotonicity across deciles")
    print(f"      mean Spearman rho(decile, residual) = {rhos.mean():+.3f}   "
          f"positive in {(rhos > 0).mean():.1%} of participants")
    print(f"      strictly monotone increasing profiles: {np.mean(monos):.1%}")
    grand = P.mean(0)
    print(f"      grand profile rho = "
          f"{stats.spearmanr(np.arange(NBIN), grand).statistic:+.3f}")
    print(f"      grand profile: {np.round(grand, 4)}")

    # ---------------- F3: split-half shape stability ----------------
    cors = []
    for _ in range(50):
        idx = RNG.permutation(len(P))
        a, b = P[idx[:len(P) // 2]].mean(0), P[idx[len(P) // 2:]].mean(0)
        cors.append(np.corrcoef(a, b)[0, 1])
    cors = np.array(cors)
    print(f"\n  F3  split-half shape stability: r = {cors.mean():+.3f} "
          f"(sd {cors.std():.3f}) over 50 splits")

    # ---------------- F4: drop the extreme deciles ----------------
    full, trimmed = [], []
    for pid, s in df.groupby("participant"):
        s = s.dropna(subset=zc)
        if len(s) < minn:
            continue
        cols = ["tee"] + ctrl
        X = np.column_stack([zs(s[c].values) for c in cols])
        y = zs(s.log_RT.values)
        full.append(sm.OLS(y, sm.add_constant(X)).fit().params[1])
        lo, hi = np.percentile(s.tee.values, [10, 90])
        m = (s.tee.values > lo) & (s.tee.values < hi)
        if m.sum() < minn // 2:
            continue
        s2 = s[m]
        X2 = np.column_stack([zs(s2[c].values) for c in cols])
        trimmed.append(sm.OLS(zs(s2.log_RT.values),
                              sm.add_constant(X2)).fit().params[1])
    full, trimmed = np.array(full), np.array(trimmed)
    print(f"\n  F4  effect without the extreme deciles")
    print(f"      full     beta = {full.mean():+.5f}  "
          f"{(full > 0).mean():.1%} positive")
    print(f"      trimmed  beta = {trimmed.mean():+.5f}  "
          f"{(trimmed > 0).mean():.1%} positive  "
          f"({trimmed.mean() / full.mean():.0%} of full)")
    print()
