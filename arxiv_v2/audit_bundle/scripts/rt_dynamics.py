"""
RT DYNAMICS: impulse-response of reading time to a TEE event
============================================================
Confirmatory analysis, specified in PREREG_rt_dynamics.md before running.
Any deviation from that document must be reported as a deviation.

P1  impulse-response of log RT to z(TEE) across lags 0-5, all lags in one
    model, controls entered at every lag, per participant then group test.
S1  same with prev_log_RT included
S2  surprisal's impulse response as a reference profile
S3  does TEE predict RT-extrapolation error (TEE's own operation on the RT series)
S4  does TEE predict the residual of an AR(2) model of log RT

Criteria (fixed in advance):
  dynamic response  = profile differs from flat (omnibus p < .01) AND some lag
                      > 0 reaches p < .0017 with >= 65% of participants agreeing
  biphasic          = two separated lags with opposite signs, each p < .0017
                      and >= 65% sign agreement
  null              = neither

Implementation guards (from this project's failure history):
  - sample hash asserted
  - merges validated one-to-one
  - LAGS COMPUTED BEFORE ANY FILTERING; row counts printed at each step
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
LAGS = list(range(6))                      # 0..5, fixed in advance
ALPHA_LAG = .01 / len(LAGS)                # .0017
SIGN_THRESHOLD = 0.65


def build():
    w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
         w[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
    assert sh == "8a6087341e", sh
    w["punct"] = w.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)

    rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id",
                                               "WorkerId": "participant"})
    print(f"hash {sh} verified | raw RT rows {len(rt):,}")
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    print(f"after RT filter          {len(rt):,}")

    d = rt.merge(w[["story_id", "zone", "word_idx", "tee_k3", "surprisal",
                    "word_length", "log_freq", "punct", "from_start", "fs2",
                    "from_end", "fe2"]],
                 on=["story_id", "zone"], how="inner", validate="many_to_one")
    print(f"after merge to measures  {len(d):,}")
    d["log_RT"] = np.log(d.RT)

    # ---- LAGS BUILT BEFORE ANY FURTHER FILTERING ----
    d = d.sort_values(["participant", "story_id", "word_idx"]).reset_index(drop=True)
    g = d.groupby(["participant", "story_id"])
    # outcome at t+L  == predictor at t shifted BACK by L
    for L in LAGS:
        d[f"y_lead{L}"] = g["log_RT"].shift(-L)
        d[f"widx_lead{L}"] = g["word_idx"].shift(-L)
    d["prev_log_RT"] = g["log_RT"].shift(1)
    # RT-extrapolation error (S3): line through log RT at t-3..t-1
    for j in (1, 2, 3):
        d[f"rt_m{j}"] = g["log_RT"].shift(j)
    pred = 3 * d.rt_m1 - 3 * d.rt_m2 + d.rt_m3        # OLS 1-step extrapolation
    d["rt_extrap_err"] = (d.log_RT - pred).abs()
    print(f"after lag construction   {len(d):,}")

    # contiguity: outcome at lead L must really be L words later
    for L in LAGS:
        ok = (d[f"widx_lead{L}"] - d.word_idx) == L
        d.loc[~ok, f"y_lead{L}"] = np.nan
    return d


def zs(x):
    s = x.std(ddof=0)
    return (x - x.mean()) / s if s > 0 else x * 0


CTRL = ["surprisal", "word_length", "log_freq", "punct",
        "from_start", "fs2", "from_end", "fe2"]


def irf(d, focus, extra_ctrl=(), label=""):
    """Per-participant impulse response: outcome at t+L on focus at t."""
    out = {L: [] for L in LAGS}
    cols = [focus] + CTRL + list(extra_ctrl)
    for pid, sub in d.groupby("participant"):
        for L in LAGS:
            s = sub.dropna(subset=cols + [f"y_lead{L}"])
            if len(s) < 300:
                continue
            X = s[cols].astype(float).apply(zs)
            if (X.std(ddof=0) == 0).any():
                continue
            X = sm.add_constant(X.values)
            r = sm.OLS(zs(s[f"y_lead{L}"]).values, X).fit()
            out[L].append(r.params[1])
    return {L: np.array(v) for L, v in out.items()}


def report(res, title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    print(f"{'lag':>4}{'n subj':>8}{'mean beta':>12}{'% same sign':>13}"
          f"{'Wilcoxon p':>13}{'sig?':>7}")
    prof = []
    for L in LAGS:
        b = res[L]
        if len(b) < 20:
            print(f"{L:>4}{len(b):>8}   too few participants")
            continue
        pos = (b > 0).mean()
        agree = max(pos, 1 - pos)
        p = stats.wilcoxon(b).pvalue
        star = "YES" if (p < ALPHA_LAG and agree >= SIGN_THRESHOLD) else ""
        print(f"{L:>4}{len(b):>8}{b.mean():>+12.5f}{agree:>12.1%}"
              f"{p:>13.2e}{star:>7}")
        prof.append(b)
    # omnibus: does the profile differ from flat? (Friedman across lags)
    if len(prof) == len(LAGS):
        m = min(len(x) for x in prof)
        stat, p = stats.friedmanchisquare(*[x[:m] for x in prof])
        print(f"\n  omnibus (profile differs from flat): "
              f"chi2 = {stat:.1f}, p = {p:.3e}   "
              f"{'PASS' if p < .01 else 'fail'}")
    return prof


def main():
    d = build()
    print(f"participants {d.participant.nunique()}   "
          f"words {d.word_idx.nunique()}\n")

    p1 = irf(d, "tee_k3")
    report(p1, "P1 (PRIMARY): impulse response of log RT to TEE, lags 0-5")

    s1 = irf(d, "tee_k3", extra_ctrl=["prev_log_RT"])
    report(s1, "S1: same, with prev_log_RT included")

    s2 = irf(d, "surprisal")
    report(s2, "S2 (reference): impulse response to SURPRISAL")

    print("\n" + "=" * 78)
    print("S3: does TEE predict RT-extrapolation error at the same word?")
    print("=" * 78)
    out = []
    cols = ["tee_k3"] + CTRL
    for pid, sub in d.groupby("participant"):
        s = sub.dropna(subset=cols + ["rt_extrap_err"])
        if len(s) < 300:
            continue
        X = sm.add_constant(s[cols].astype(float).apply(zs).values)
        out.append(sm.OLS(zs(s.rt_extrap_err).values, X).fit().params[1])
    out = np.array(out)
    pos = (out > 0).mean()
    print(f"  n = {len(out)}  mean beta = {out.mean():+.5f}  "
          f"same sign {max(pos,1-pos):.1%}  Wilcoxon p = {stats.wilcoxon(out).pvalue:.2e}")

    print("\n" + "=" * 78)
    print("S4: does TEE predict the residual of an AR(2) model of log RT?")
    print("=" * 78)
    d["ar_resid"] = np.nan
    g = d.groupby(["participant", "story_id"])
    d["rt_l1"] = g["log_RT"].shift(1)
    d["rt_l2"] = g["log_RT"].shift(2)
    sub = d.dropna(subset=["log_RT", "rt_l1", "rt_l2"])
    X = sm.add_constant(sub[["rt_l1", "rt_l2"]].values)
    ar = sm.OLS(sub.log_RT.values, X).fit()
    d.loc[sub.index, "ar_resid"] = np.abs(ar.resid)
    out = []
    for pid, s2_ in d.groupby("participant"):
        s = s2_.dropna(subset=cols + ["ar_resid"])
        if len(s) < 300:
            continue
        X = sm.add_constant(s[cols].astype(float).apply(zs).values)
        out.append(sm.OLS(zs(s.ar_resid).values, X).fit().params[1])
    out = np.array(out)
    pos = (out > 0).mean()
    print(f"  n = {len(out)}  mean beta = {out.mean():+.5f}  "
          f"same sign {max(pos,1-pos):.1%}  Wilcoxon p = {stats.wilcoxon(out).pvalue:.2e}")


if __name__ == "__main__":
    main()
