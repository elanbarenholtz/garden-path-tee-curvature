"""
SUBJECT-LEVEL INFERENCE ON THE NATURAL STORIES TEE EFFECT
=========================================================
The ZuCo eye-tracking analysis found a null using SUBJECT-LEVEL inference:
one beta per subject, then a group test across subjects, explicitly to avoid
pseudoreplication. The Natural Stories result instead pools 813,621
observations with a by-participant random intercept.

This script applies the ZuCo standard to Natural Stories: fit the model
separately within each of the 180 participants, then test the distribution of
per-participant TEE coefficients at the subject level.

If the betas are overwhelmingly positive, the pooled result is not a large-N
artifact and the ZuCo null is a paradigm difference. If they scatter around
zero, the headline needs rethinking.

Three specifications:
  FULL   = the project's control set (length, freq, position, prev RT, surprisal)
  ZUCO   = ZuCo's leaner control set (length, freq only) for direct comparability
  PUNCTFREE = FULL on punctuation-free words (ZuCo also removed these)
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
PUNCT = set(".,;:!?\"'`)(-—")


def build():
    w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    w["punct_final"] = w.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
    rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id",
                                               "WorkerId": "participant"})
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                    "log_freq", "punct_final"]],
                 on=["story_id", "zone"], how="inner")
    m["log_RT"] = np.log(m.RT)
    m = m.sort_values(["participant", "story_id", "zone"])
    m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
    return m


SPECS = {
    "FULL      (length, freq, zone, prevRT, surprisal)":
        ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"],
    "ZUCO-style(length, freq only)":
        ["word_length", "log_freq", "tee_k3"],
}


def per_subject(d, cols):
    """One OLS per participant; return the TEE coefficient from each."""
    out = []
    for pid, sub in d.groupby("participant"):
        s = sub.dropna(subset=cols + ["log_RT"])
        if len(s) < 200:
            continue
        X = s[cols].astype(float)
        X = (X - X.mean()) / X.std(ddof=0)
        X = sm.add_constant(X)
        if X.isna().any().any() or np.linalg.matrix_rank(X.values) < X.shape[1]:
            continue
        r = sm.OLS(s.log_RT.values, X.values).fit()
        out.append({"participant": pid, "n": len(s),
                    "beta": r.params[-1], "p": r.pvalues[-1]})
    return pd.DataFrame(out)


def report(label, B):
    n = len(B)
    pos = int((B.beta > 0).sum())
    w = stats.wilcoxon(B.beta)
    t = stats.ttest_1samp(B.beta, 0)
    sign = stats.binomtest(pos, n, 0.5)
    print(f"\n{'='*74}\n{label}\n{'='*74}")
    print(f"  participants            : {n}")
    print(f"  positive betas          : {pos}/{n} ({pos/n:.1%})")
    print(f"  mean beta               : {B.beta.mean():+.5f}  (SD {B.beta.std():.5f})")
    print(f"  median beta             : {B.beta.median():+.5f}")
    print(f"  sign test               : p = {sign.pvalue:.3e}")
    print(f"  Wilcoxon signed-rank    : p = {w.pvalue:.3e}")
    print(f"  one-sample t            : t({n-1}) = {t.statistic:.2f}, p = {t.pvalue:.3e}")
    print(f"  individually sig (p<.05): {int((B.p < .05).sum())}/{n}")
    return dict(label=label, n=n, pos=pos, mean=B.beta.mean(),
                wilcoxon_p=w.pvalue, t_p=t.pvalue, sign_p=sign.pvalue,
                n_sig=int((B.p < .05).sum()))


def main():
    d = build()
    print(f"participants = {d.participant.nunique()}   rows = {len(d):,}")
    rows = []
    for label, cols in SPECS.items():
        B = per_subject(d, cols)
        rows.append(report(label, B))
        B.to_csv(f"{GP}/gp_confound_check/subject_betas_"
                 f"{label.split('(')[0].strip().lower()}.csv", index=False)

    pf = d[d.punct_final == 0]
    B = per_subject(pf, SPECS["FULL      (length, freq, zone, prevRT, surprisal)"])
    rows.append(report("PUNCT-FREE (FULL controls, punctuation-final removed)", B))

    print(f"\n{'='*74}\nZuCo comparison (10 subjects, eye-tracking, subject-level)")
    print(f"{'='*74}")
    print("  FFD  Wilcoxon p = .084   0/10 individually significant")
    print("  GD   Wilcoxon p = .160   0/10")
    print("  TRT  Wilcoxon p = .065   0/10")

    pd.DataFrame(rows).to_csv(f"{GP}/gp_confound_check/subject_level_summary.csv",
                              index=False)


if __name__ == "__main__":
    main()
