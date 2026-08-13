"""
RECOMPUTE v1 TABLES 2 AND 3 ON THE VERIFIED SAMPLE
==================================================
v1's Table 2 (surprisal x TEE dissociation matrix) and Table 3 (displacement
control) were computed from the superseded measure file. Recomputed here on
locked sample 8a6087341e with the displacement values from
displacement_8a6087341e.csv (states revalidated: 0/9,840 alignment mismatches).

Also verifies the r = .044 orthogonality claim.

Model spec follows the project convention used for the v2 headline:
mixedlm, by-participant random intercept, ML fit,
controls = word length + log frequency + zone + previous log RT.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"


def build():
    w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    dp = pd.read_csv(f"{GP}/gp_confound_check/displacement_8a6087341e.csv")
    w = w.merge(dp, on=["story_id", "word_idx"], validate="one_to_one")
    rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id",
                                               "WorkerId": "participant"})
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                    "log_freq", "disp_word", "state_norm"]],
                 on=["story_id", "zone"], how="inner")
    m["log_RT"] = np.log(m.RT)
    m = m.sort_values(["participant", "story_id", "zone"])
    m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
    return w, m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                               "prev_log_RT", "surprisal", "tee_k3", "disp_word"])


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


def main():
    w, d = build()

    print("=" * 74)
    print("ORTHOGONALITY (v1 claim: r = .044)")
    print("=" * 74)
    print(f"  word-level r(TEE, surprisal)      = {w.tee_k3.corr(w.surprisal):+.4f}  "
          f"(n = {w.tee_k3.notna().sum():,})")
    print(f"  word-level r(TEE, entropy)        = {w.tee_k3.corr(w.entropy):+.4f}")
    print(f"  word-level r(TEE, log_freq)       = {w.tee_k3.corr(w.log_freq):+.4f}")
    print(f"  word-level r(TEE, displacement)   = {w.tee_k3.corr(w.disp_word):+.4f}")
    print(f"  word-level r(displacement, surp)  = {w.disp_word.corr(w.surprisal):+.4f}")

    print("\n" + "=" * 74)
    print("TABLE 2: dissociation matrix, mean log RT by surprisal x TEE tercile")
    print("=" * 74)
    d = d.copy()
    d["s_t"] = pd.qcut(d.surprisal, 3, labels=["low", "mid", "high"])
    d["e_t"] = pd.qcut(d.tee_k3, 3, labels=["low", "mid", "high"])
    piv = d.pivot_table(index="s_t", columns="e_t", values="log_RT",
                        aggfunc="mean", observed=True)
    cnt = d.pivot_table(index="s_t", columns="e_t", values="log_RT",
                        aggfunc="size", observed=True)
    print("\nmean log RT:")
    print(piv.round(4).to_string())
    print("\ncell n:")
    print(cnt.to_string())
    base = piv.loc["low", "low"]
    print(f"\nrelative to low/low baseline ({base:.4f}):")
    print((piv - base).round(4).to_string())
    print("\nkey off-diagonal cells (v1: high-surp/low-TEE +0.039; "
          "low-surp/high-TEE +0.008):")
    for s_, e_, lab in [("high", "low", "high surprisal, low TEE"),
                        ("low", "high", "low surprisal, high TEE")]:
        cell = d[(d.s_t == s_) & (d.e_t == e_)]
        ref = d[(d.s_t == "low") & (d.e_t == "low")]
        from scipy import stats as st
        t = st.ttest_ind(cell.log_RT, ref.log_RT, equal_var=False)
        print(f"  {lab:<26} delta = {cell.log_RT.mean()-ref.log_RT.mean():+.4f}  "
              f"n = {len(cell):,}  t = {t.statistic:.2f}  p = {t.pvalue:.2e}")

    print("\n" + "=" * 74)
    print("TABLE 3: displacement control")
    print("=" * 74)
    print("v1 claim: displacement and extrapolation error predict in OPPOSITE "
          "directions")
    for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal",
              "tee_k3", "disp_word"]:
        d["z_" + c] = z(d[c])
    CTRL = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_surprisal"
    specs = [("TEE alone", CTRL + " + z_tee_k3", "z_tee_k3"),
             ("displacement alone", CTRL + " + z_disp_word", "z_disp_word"),
             ("both: TEE", CTRL + " + z_tee_k3 + z_disp_word", "z_tee_k3"),
             ("both: displacement", CTRL + " + z_tee_k3 + z_disp_word", "z_disp_word")]
    print(f"\n{'model':<24}{'beta':>12}{'p':>14}")
    for lab, f, term in specs:
        m = smf.mixedlm(f, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
        print(f"{lab:<24}{m.params[term]:>12.5f}{m.pvalues[term]:>14.2e}")
    print(f"\nn = {len(d):,}   participants = {d.participant.nunique()}")


if __name__ == "__main__":
    main()
