"""
DOES TEE SURVIVE FLEXIBLE CONTROLS? (the misspecification test)
==============================================================
Standard objection to any "beyond surprisal" claim: if surprisal (or frequency,
or length) enters linearly but its true relationship to reading time is curved,
the unfit curvature stays in the residual as a systematic function of that
predictor. Anything correlated with it can then absorb the leftover and look
like an independent effect.

TEE is correlated r = +0.31 with surprisal and r = -0.44 with log frequency, so
it is positioned to do exactly this.

Test: give surprisal, log frequency and word length natural cubic splines with
increasing degrees of freedom, so the model can fit whatever shape is really
there, and ask whether TEE still improves fit. TEE itself stays linear
throughout -- if its own form is misspecified that costs power, not validity.

Locked sample 8a6087341e; mixedlm with by-participant random intercept, ML fit.
Reference: linear spec gives dAIC = 112, beta = +0.0035.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from patsy import dmatrix
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"


def build():
    w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    w["punct"] = w.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
    rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id",
                                               "WorkerId": "participant"})
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "entropy",
                    "word_length", "log_freq", "punct"]],
                 on=["story_id", "zone"], how="inner")
    m["log_RT"] = np.log(m.RT)
    m = m.sort_values(["participant", "story_id", "zone"])
    m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
    d = m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                         "prev_log_RT", "surprisal", "tee_k3"]).copy()
    for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal",
              "tee_k3", "entropy"]:
        v = d[c]
        d["z_" + c] = (v - v.mean()) / v.std()
    return d


def spline_terms(df, cols, dfree):
    """Add natural-cubic-spline basis columns; return the term names."""
    names = []
    for c in cols:
        B = dmatrix(f"cr(x, df={dfree}) - 1", {"x": df[c].values},
                    return_type="dataframe")
        for j in range(B.shape[1]):
            nm = f"s_{c}_{dfree}_{j}"
            df[nm] = B.iloc[:, j].values
            names.append(nm)
    return names


def main():
    d = build()
    print(f"n = {len(d):,}   participants = {d.participant.nunique()}")
    print(f"r(TEE, surprisal) = {d.tee_k3.corr(d.surprisal):+.3f}   "
          f"r(TEE, log_freq) = {d.tee_k3.corr(d.log_freq):+.3f}\n")

    FLEX = ["surprisal", "log_freq", "word_length"]
    BASE_LINEAR = "z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_surprisal"

    print("=" * 80)
    print("Does TEE survive as surprisal/frequency/length are given more freedom?")
    print("=" * 80)
    print(f"{'control specification':<42}{'dAIC(TEE)':>11}{'beta':>10}{'p':>12}")

    # linear reference
    m1 = smf.mixedlm(f"log_RT ~ {BASE_LINEAR}", d,
                     groups=d["participant"]).fit(reml=False, method="lbfgs")
    m2 = smf.mixedlm(f"log_RT ~ {BASE_LINEAR} + z_tee_k3", d,
                     groups=d["participant"]).fit(reml=False, method="lbfgs")
    print(f"{'linear (published spec)':<42}{m1.aic-m2.aic:>11.1f}"
          f"{m2.params['z_tee_k3']:>10.5f}{m2.pvalues['z_tee_k3']:>12.2e}")

    for dfree in [3, 5, 8, 12]:
        terms = spline_terms(d, FLEX, dfree)
        base = " + ".join(["z_zone", "z_prev_log_RT"] + terms)
        a = smf.mixedlm(f"log_RT ~ {base}", d,
                        groups=d["participant"]).fit(reml=False, method="lbfgs")
        b = smf.mixedlm(f"log_RT ~ {base} + z_tee_k3", d,
                        groups=d["participant"]).fit(reml=False, method="lbfgs")
        print(f"{'splines df=' + str(dfree) + ' on surp/freq/len':<42}"
              f"{a.aic-b.aic:>11.1f}{b.params['z_tee_k3']:>10.5f}"
              f"{b.pvalues['z_tee_k3']:>12.2e}")

    # strictest: splines + entropy + punctuation
    terms = spline_terms(d, FLEX, 8)
    base = " + ".join(["z_zone", "z_prev_log_RT", "z_entropy", "punct"] + terms)
    a = smf.mixedlm(f"log_RT ~ {base}", d,
                    groups=d["participant"]).fit(reml=False, method="lbfgs")
    b = smf.mixedlm(f"log_RT ~ {base} + z_tee_k3", d,
                    groups=d["participant"]).fit(reml=False, method="lbfgs")
    print(f"{'df=8 splines + entropy + punctuation':<42}{a.aic-b.aic:>11.1f}"
          f"{b.params['z_tee_k3']:>10.5f}{b.pvalues['z_tee_k3']:>12.2e}")

    print("\n" + "=" * 80)
    print("How curved IS the surprisal-RT relationship? (is the worry real?)")
    print("=" * 80)
    lin = smf.mixedlm(f"log_RT ~ z_zone + z_prev_log_RT + z_word_length "
                      f"+ z_log_freq + z_surprisal", d,
                      groups=d["participant"]).fit(reml=False, method="lbfgs")
    st = spline_terms(d, ["surprisal"], 8)
    spl = smf.mixedlm(f"log_RT ~ z_zone + z_prev_log_RT + z_word_length "
                      f"+ z_log_freq + " + " + ".join(st), d,
                      groups=d["participant"]).fit(reml=False, method="lbfgs")
    print(f"  linear surprisal   AIC = {lin.aic:.1f}")
    print(f"  spline surprisal   AIC = {spl.aic:.1f}   "
          f"improvement = {lin.aic - spl.aic:.1f}")
    print("  (large improvement => surprisal really is nonlinear here, so the")
    print("   misspecification worry was well founded)")


if __name__ == "__main__":
    main()
