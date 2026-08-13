#!/usr/bin/env python3
"""
Linear mixed-effects test of TEE on ZuCo fixation durations -- the properly
POWERED complement to the per-subject Wilcoxon (which, at n=10, is conservative
and can miss a small consistent effect).

Word-level observations, random intercept + TEE slope per subject. This is the
standard reading-time analysis and is NOT pseudoreplication: the random effects
account for the within-subject nesting (unlike the earlier EEG bug that pooled
correlated channels as if independent).

Also prints the diagnostics the summary was missing:
  - words merged per subject (a broken sent_idx/word_idx merge attenuates effects)
  - how many subjects, and which
  - TEE<->surprisal collinearity (inflated SE hides real effects)

Inputs (same as analyze_fixation_tee.py):
  ET_DIR/*.csv        per-subject eye-tracking (extract_zuco_et.py)
  TEE_CSV             real per-word TEE (compute_tee_zuco.py); must be ~11k rows

Usage:
    python3 analyze_fixation_lmm.py [ET_DIR] [TEE_CSV]
      defaults: zuco_et  zuco_tee_real.csv
"""
import os, sys, re
import numpy as np
import pandas as pd

ET_DIR = sys.argv[1] if len(sys.argv) > 1 else "zuco_et"
TEE_CSV = sys.argv[2] if len(sys.argv) > 2 else "zuco_tee_real.csv"
OUTCOMES = ["FFD", "GD", "TRT"]

try:
    import statsmodels.formula.api as smf
except Exception:
    sys.exit("need statsmodels: pip install statsmodels")

try:
    from wordfreq import zipf_frequency
except Exception:
    zipf_frequency = None


def clean_word(w):
    return re.sub(r"[^A-Za-z']", "", str(w))


def zc(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / s if s > 0 else a * 0


def build():
    tee = pd.read_csv(TEE_CSV)
    if len(tee) < 1000:
        sys.exit(f"{TEE_CSV} has {len(tee)} rows -- still the 22-word toy file. "
                 "Recompute with compute_tee_zuco.py.")
    tee["wlen"] = tee["word"].map(lambda w: len(clean_word(w)))
    if zipf_frequency is not None:
        tee["logfreq"] = tee["word"].map(
            lambda w: zipf_frequency(clean_word(w).lower() or "the", "en"))
    else:
        tee["logfreq"] = 0.0
    cols = ["sent_idx", "word_idx", "tee_k3", "surp", "logfreq", "wlen", "has_trailing_punct"]
    tee = tee[cols]

    frames = []
    for f in sorted(x for x in os.listdir(ET_DIR) if x.endswith(".csv")):
        et = pd.read_csv(os.path.join(ET_DIR, f))
        et["subject"] = os.path.splitext(f)[0]
        m = et.merge(tee, on=["sent_idx", "word_idx"], how="inner")
        frames.append(m)
    df = pd.concat(frames, ignore_index=True)
    df = df[df["has_trailing_punct"] == 0]
    return df


def main():
    df = build()

    print("=== merge diagnostics ===")
    per = df.groupby("subject").size()
    print(f"subjects merged: {len(per)}  ({', '.join(per.index)})")
    print(f"words/subject: min {per.min()}, median {int(per.median())}, max {per.max()}")
    r = df[["tee_k3", "surp"]].dropna().corr().iloc[0, 1]
    print(f"corr(TEE, surprisal) = {r:+.3f}  (high |r| inflates SE, can hide effects)\n")

    print("=== linear mixed model: outcome ~ TEE + surp + logfreq + wlen, "
          "random intercept+TEE slope by subject ===")
    print(f"{'outcome':7} {'n_obs':>7} {'TEE beta':>10} {'SE':>8} {'z':>7} {'p':>10}")
    for oc in OUTCOMES:
        if oc not in df.columns:
            continue
        d = df.dropna(subset=[oc, "tee_k3", "surp", "logfreq", "wlen"]).copy()
        d = d[d[oc] > 0]
        for c in ["tee_k3", "surp", "logfreq", "wlen"]:
            d[c + "_z"] = zc(d[c])
        d["y_z"] = zc(d[oc])
        try:
            md = smf.mixedlm("y_z ~ tee_k3_z + surp_z + logfreq_z + wlen_z",
                             d, groups=d["subject"], re_formula="~tee_k3_z")
            fit = md.fit(method="lbfgs", maxiter=200, disp=False)
            b = fit.params["tee_k3_z"]; se = fit.bse["tee_k3_z"]
            zval = b / se; p = fit.pvalues["tee_k3_z"]
            print(f"{oc:7} {len(d):>7} {b:>+10.4f} {se:>8.4f} {zval:>+7.2f} {p:>10.4g}")
        except Exception as e:
            print(f"{oc:7} {len(d):>7}  FIT FAILED: {e}")
    print("\nStandardized betas (both sides z-scored): interpretable as partial")
    print("correlation-like effect size. A real reading effect is typically small")
    print("(~0.01-0.05) but should be positive and, with word-level power, significant")
    print("if the per-subject trend (all-positive, p~0.07) reflects a true effect.")


if __name__ == "__main__":
    main()
