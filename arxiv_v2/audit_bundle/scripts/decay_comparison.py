"""
P2: does TEE's reading-time impulse response decay faster than surprisal's?
==========================================================================
Specified in PREREG_decay_comparison.md before running.

Per participant, from the P1 model (lags 0-5 simultaneously, standard controls,
no prev_log_RT):
    R = (b3 + b4 + b5) / (b0 + b1 + b2)     computed for TEE and for surprisal
Paired Wilcoxon of R_TEE vs R_surprisal.

Support: R_TEE < R_surprisal, p < .01, >= 65% of participants in that direction.
Stability guard (fixed in advance): include a participant only if the early-lag
sum is POSITIVE for both measures.

S5 half-life: first lag where |b| < 50% of that measure's peak |b|.
S6 bootstrap CI on the mean difference.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
LAGS = list(range(6))
RNG = np.random.default_rng(20260728)

CTRL = ["surprisal", "word_length", "log_freq", "punct",
        "from_start", "fs2", "from_end", "fe2"]


def build():
    w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
         w[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
    assert sh == "8a6087341e", sh
    w["punct"] = w.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
    rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id",
                                               "WorkerId": "participant"})
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    d = rt.merge(w[["story_id", "zone", "word_idx", "tee_k3", "surprisal",
                    "word_length", "log_freq", "punct", "from_start", "fs2",
                    "from_end", "fe2"]],
                 on=["story_id", "zone"], how="inner", validate="many_to_one")
    d["log_RT"] = np.log(d.RT)
    d = d.sort_values(["participant", "story_id", "word_idx"]).reset_index(drop=True)
    g = d.groupby(["participant", "story_id"])
    for L in LAGS:
        d[f"y_lead{L}"] = g["log_RT"].shift(-L)
        d[f"widx_lead{L}"] = g["word_idx"].shift(-L)
    for L in LAGS:
        ok = (d[f"widx_lead{L}"] - d.word_idx) == L
        d.loc[~ok, f"y_lead{L}"] = np.nan
    print(f"hash {sh} verified | rows {len(d):,} | "
          f"participants {d.participant.nunique()}")
    return d


def zs(x):
    s = x.std(ddof=0)
    return (x - x.mean()) / s if s > 0 else x * 0


def betas_per_subject(d, focus):
    """Return {participant: array of 6 betas} for the given focus predictor."""
    cols = [focus] + [c for c in CTRL if c != focus]
    out = {}
    for pid, sub in d.groupby("participant"):
        b = []
        ok = True
        for L in LAGS:
            s = sub.dropna(subset=cols + [f"y_lead{L}"])
            if len(s) < 300:
                ok = False
                break
            X = s[cols].astype(float).apply(zs)
            if (X.std(ddof=0) == 0).any():
                ok = False
                break
            r = sm.OLS(zs(s[f"y_lead{L}"]).values,
                       sm.add_constant(X.values)).fit()
            b.append(r.params[1])
        if ok:
            out[pid] = np.array(b)
    return out


def main():
    d = build()
    B_tee = betas_per_subject(d, "tee_k3")
    B_sur = betas_per_subject(d, "surprisal")
    shared = sorted(set(B_tee) & set(B_sur))
    print(f"participants with both profiles: {len(shared)}")

    early_t = np.array([B_tee[p][:3].sum() for p in shared])
    late_t = np.array([B_tee[p][3:].sum() for p in shared])
    early_s = np.array([B_sur[p][:3].sum() for p in shared])
    late_s = np.array([B_sur[p][3:].sum() for p in shared])

    keep = (early_t > 0) & (early_s > 0)          # pre-specified guard
    print(f"excluded by positivity guard: {(~keep).sum()} "
          f"({(~keep).mean():.1%})   analysed: {keep.sum()}")

    R_t = late_t[keep] / early_t[keep]
    R_s = late_s[keep] / early_s[keep]

    print("\n" + "=" * 78)
    print("P2 (PRIMARY): late/early ratio, TEE vs surprisal")
    print("=" * 78)
    print(f"  mean R(TEE)       = {R_t.mean():+.4f}   median {np.median(R_t):+.4f}")
    print(f"  mean R(surprisal) = {R_s.mean():+.4f}   median {np.median(R_s):+.4f}")
    diff = R_t - R_s
    frac = (diff < 0).mean()
    w = stats.wilcoxon(R_t, R_s)
    print(f"\n  mean difference (TEE - surprisal) = {diff.mean():+.4f}")
    print(f"  participants with R_TEE < R_surprisal: {frac:.1%}")
    print(f"  paired Wilcoxon: p = {w.pvalue:.3e}")
    ok = (w.pvalue < .01) and (frac >= .65) and (R_t.mean() < R_s.mean())
    print(f"\n  PRE-SPECIFIED CRITERIA: {'MET' if ok else 'NOT MET'}")

    print("\n" + "=" * 78)
    print("S5: half-life (first lag where |beta| < 50% of that measure's peak)")
    print("=" * 78)

    def halflife(b):
        pk = np.abs(b).max()
        for L in LAGS:
            if abs(b[L]) < .5 * pk:
                return L
        return len(LAGS)

    h_t = np.array([halflife(B_tee[p]) for p, k in zip(shared, keep) if k])
    h_s = np.array([halflife(B_sur[p]) for p, k in zip(shared, keep) if k])
    fr = (h_t < h_s).mean()
    w5 = stats.wilcoxon(h_t, h_s)
    print(f"  median half-life TEE       = {np.median(h_t):.1f} words")
    print(f"  median half-life surprisal = {np.median(h_s):.1f} words")
    print(f"  participants with TEE shorter: {fr:.1%}")
    print(f"  paired Wilcoxon: p = {w5.pvalue:.3e}")

    print("\n" + "=" * 78)
    print("S6: bootstrap 95% CI on mean(R_TEE - R_surprisal)")
    print("=" * 78)
    bs = [np.mean(RNG.choice(diff, len(diff), replace=True)) for _ in range(10000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"  mean difference {diff.mean():+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]")

    print("\n" + "=" * 78)
    print("Mean profiles (for the record)")
    print("=" * 78)
    print(f"{'lag':>4}{'TEE':>12}{'surprisal':>13}")
    for L in LAGS:
        t = np.mean([B_tee[p][L] for p, k in zip(shared, keep) if k])
        s = np.mean([B_sur[p][L] for p, k in zip(shared, keep) if k])
        print(f"{L:>4}{t:>+12.5f}{s:>+13.5f}")


if __name__ == "__main__":
    main()
