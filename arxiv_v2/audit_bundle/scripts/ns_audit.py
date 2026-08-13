"""
NATURAL STORIES PIPELINE AUDIT
==============================
Looks for the CLASS of error that broke the garden-path analysis:
  A. merge integrity      -- does the word->RT merge multiply or drop rows?
  B. lagged control       -- is prev_log_RT actually the ADJACENT word, or was
                             it computed after row-filtering (so it silently
                             points at whatever row survived)?
  C. sample equality      -- are the AIC-compared nested models fit on the
                             SAME rows?
  D. heterogeneity        -- does the TEE effect hold its sign across stories
                             and sentence positions, or is the pooled estimate
                             an average over disagreeing subsets (the failure
                             mode that broke the garden-path result)?

Replicates the prep in garden-path-p1/ns_crossed_re.py, but on the locked
sample (hash 8a6087341e), which carries tee_k3, surprisal, log_freq, etc.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import os, warnings
warnings.filterwarnings("ignore")

REPO = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
SAMPLE = f"{REPO}/rebuild_v2_outputs/sample_8a6087341e.csv"
RTS = f"{REPO}/naturalstories/naturalstories_RTS/processed_RTs.tsv"


def load():
    w = pd.read_csv(SAMPLE)
    rt = pd.read_csv(RTS, sep="\t")
    rt = rt.rename(columns={"item": "story_id", "WorkerId": "participant"})
    return w, rt


def main():
    w, rt_raw = load()
    print(f"locked sample: {len(w):,} words | RT file: {len(rt_raw):,} rows, "
          f"{rt_raw.participant.nunique()} participants")

    # ---------- A. merge integrity ----------
    print("\n" + "=" * 72)
    print("A. MERGE INTEGRITY")
    print("=" * 72)
    dup = w.duplicated(subset=["story_id", "zone"]).sum()
    print(f"duplicate (story_id, zone) keys in word table: {dup}")
    rt = rt_raw[(rt_raw.RT >= 100) & (rt_raw.RT <= 3000)].copy()
    before = len(rt)
    m = rt.merge(w[["story_id", "zone", "word", "tee_k3", "surprisal",
                    "word_length", "log_freq"]],
                 on=["story_id", "zone"], how="left")
    print(f"RT rows before merge {before:,} -> after {len(m):,} "
          f"({'OK, no multiplication' if len(m) == before else 'ROW COUNT CHANGED'})")
    print(f"rows with no matching word record: {m.tee_k3.isna().sum():,} "
          f"({m.tee_k3.isna().mean():.1%})")

    # ---------- B. lagged control ----------
    print("\n" + "=" * 72)
    print("B. LAGGED CONTROL (prev_log_RT)")
    print("=" * 72)
    m["log_RT"] = np.log(m.RT)
    m = m.sort_values(["participant", "story_id", "zone"])
    g = m.groupby(["participant", "story_id"])
    m["prev_log_RT"] = g["log_RT"].shift(1)
    m["prev_zone"] = g["zone"].shift(1)
    m["gap"] = m.zone - m.prev_zone
    ok = (m.gap == 1)
    print(f"prev_log_RT rows where previous row is the ADJACENT word: "
          f"{ok.sum():,} / {m.prev_zone.notna().sum():,} "
          f"({ok.sum()/max(m.prev_zone.notna().sum(),1):.1%})")
    print(f"rows where the 'previous' word is 2+ zones back (filtered-out "
          f"neighbour): {(m.gap > 1).sum():,}")
    print("  -> same shape as the garden-path bug: the lag is computed AFTER "
          "row filtering.")
    print("     Milder here: it mislabels the control on a minority of rows "
          "rather than deleting a whole condition.")

    # ---------- C. sample equality across nested models ----------
    print("\n" + "=" * 72)
    print("C. SAMPLE EQUALITY FOR THE AIC COMPARISON")
    print("=" * 72)
    d = m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                         "prev_log_RT", "surprisal", "tee_k3"]).copy()
    for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"]:
        v = d[c].dropna()
        d["z_" + c] = (d[c] - v.mean()) / v.std()
    print(f"analysis N = {len(d):,}  participants = {d.participant.nunique()}  "
          f"stories = {d.story_id.nunique()}")
    print("M1 and M2 are both fit on this frame (M2 adds a term that is already "
          "non-null here), so the nested comparison is on identical rows: OK.")

    CTRL = "z_word_length + z_log_freq + z_zone + z_prev_log_RT"
    F1 = f"log_RT ~ {CTRL} + z_surprisal"
    F2 = F1 + " + z_tee_k3"
    m1 = smf.mixedlm(F1, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
    m2 = smf.mixedlm(F2, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
    print(f"\nheadline: dAIC = {m1.aic - m2.aic:.1f}   "
          f"beta(TEE) = {m2.params['z_tee_k3']:+.5f}   "
          f"p = {m2.pvalues['z_tee_k3']:.3e}")
    print(f"for scale: beta(surprisal) = {m2.params['z_surprisal']:+.5f}, "
          f"beta(log_freq) = {m2.params['z_log_freq']:+.5f}, "
          f"beta(prev_log_RT) = {m2.params['z_prev_log_RT']:+.5f}")

    # lag control fixed: keep only rows whose previous word really is adjacent
    d2 = d[d.gap == 1].copy()
    m1b = smf.mixedlm(F1, d2, groups=d2["participant"]).fit(reml=False, method="lbfgs")
    m2b = smf.mixedlm(F2, d2, groups=d2["participant"]).fit(reml=False, method="lbfgs")
    print(f"\nwith the lag control repaired (adjacent-word rows only, "
          f"n = {len(d2):,}):")
    print(f"  dAIC = {m1b.aic - m2b.aic:.1f}   "
          f"beta(TEE) = {m2b.params['z_tee_k3']:+.5f}   "
          f"p = {m2b.pvalues['z_tee_k3']:.3e}")

    # ---------- D. heterogeneity ----------
    print("\n" + "=" * 72)
    print("D. HETEROGENEITY -- does the effect hold its sign across subsets?")
    print("=" * 72)
    print("\nby story:")
    signs = []
    for s, sub in d.groupby("story_id"):
        mm = smf.mixedlm(F2, sub, groups=sub["participant"]).fit(reml=False, method="lbfgs")
        b, p = mm.params["z_tee_k3"], mm.pvalues["z_tee_k3"]
        signs.append(np.sign(b))
        print(f"  story {s:>2}  n={len(sub):>7,}  beta={b:>+.5f}  p={p:.3f}")
    print(f"  -> {int(sum(1 for x in signs if x > 0))}/{len(signs)} stories positive")

    print("\nby sentence position (from_start bucket):")
    d["pos_bin"] = pd.cut(d.from_start, [-1, 2, 5, 10, 20, 999],
                          labels=["0-2", "3-5", "6-10", "11-20", "21+"])
    for b, sub in d.groupby("pos_bin", observed=True):
        if len(sub) < 5000:
            continue
        mm = smf.mixedlm(F2, sub, groups=sub["participant"]).fit(reml=False, method="lbfgs")
        print(f"  pos {str(b):>6}  n={len(sub):>7,}  "
              f"beta={mm.params['z_tee_k3']:>+.5f}  p={mm.pvalues['z_tee_k3']:.3e}")

    print("\nformal test: TEE x position-bin interaction")
    mi = smf.mixedlm(F2 + " + z_tee_k3:C(pos_bin)", d,
                     groups=d["participant"]).fit(reml=False, method="lbfgs")
    from scipy import stats as st
    lr = -2 * (m2.llf - mi.llf)
    dfd = len(mi.params) - len(m2.params)
    print(f"  chi2({dfd}) = {lr:.1f}, p = {st.chi2.sf(lr, dfd):.3e}")


if __name__ == "__main__":
    main()
