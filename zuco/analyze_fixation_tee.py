#!/usr/bin/env python3
"""
Does TEE predict fixation duration during natural reading, beyond frequency +
length + surprisal? This is the BEHAVIORAL test -- the direct analog of the
Natural Stories self-paced reading-time result, and the theoretically matched
one (TEE is a reading-time measure). It needs NO EEG and no fixation/EEG
synchronization, so it is immune to the dead-baseline problem that makes the
current EEG null uninterpretable.

Inference is SUBJECT-LEVEL (the lesson from the pseudoreplication bug): fit a
standardized multiple regression WITHIN each subject, take the TEE partial slope
per subject, then test those 12 slopes across subjects (t-test + Wilcoxon). No
pooling of correlated within-subject observations.

Inputs:
  zuco_et/*.csv       per-subject eye-tracking (from extract_zuco_et.py):
                      subject, sent_idx, word_idx, word, nFix, FFD, GD, TRT, GPT, SFD
  zuco/zuco_tee.csv   real per-word TEE (from compute_tee_zuco.py):
                      sent_idx, word_idx, word, tee_k3, surp, entropy, has_trailing_punct

Outcomes tested: FFD (first-fixation dur), GD (gaze dur), TRT (total reading time).
Predictor of interest: tee_k3. Controls: surp, log-frequency, word length.

Usage:
    python3 analyze_fixation_tee.py [ET_DIR] [TEE_CSV] [OUT_CSV]
      defaults: zuco_et  zuco/zuco_tee.csv  zuco/fixation_tee_subject_slopes.csv
"""
import os, sys, re
import numpy as np
import pandas as pd
from scipy import stats

try:
    from wordfreq import zipf_frequency
except Exception:
    zipf_frequency = None

ET_DIR = sys.argv[1] if len(sys.argv) > 1 else "zuco_et"
TEE_CSV = sys.argv[2] if len(sys.argv) > 2 else "zuco/zuco_tee.csv"
OUT = sys.argv[3] if len(sys.argv) > 3 else "zuco/fixation_tee_subject_slopes.csv"

OUTCOMES = ["FFD", "GD", "TRT"]
PREDICTORS = ["tee_k3", "surp", "logfreq", "wlen"]   # TEE first = coefficient of interest


def z(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / s if s > 0 else np.zeros_like(a)


def clean_word(w):
    return re.sub(r"[^A-Za-z']", "", str(w))


def lexical_cols(df):
    words = df["word"].astype(str)
    df["wlen"] = words.map(lambda w: len(clean_word(w)))
    if zipf_frequency is not None:
        df["logfreq"] = words.map(lambda w: zipf_frequency(clean_word(w).lower() or "the", "en"))
    else:
        df["logfreq"] = np.nan   # falls back to length-only control if wordfreq missing
    return df


def subject_slope(df, outcome):
    """Standardized multiple regression; return TEE partial slope + n."""
    preds = [p for p in PREDICTORS if df[p].notna().all() and df[p].std() > 0]
    if "tee_k3" not in preds:
        return None
    d = df.dropna(subset=[outcome] + preds)
    d = d[d[outcome] > 0]                       # fixated words only (dur > 0)
    if len(d) < 50:
        return None
    y = z(d[outcome].to_numpy())
    X = np.column_stack([np.ones(len(d))] + [z(d[p].to_numpy()) for p in preds])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    tee_i = 1 + preds.index("tee_k3")           # +1 for intercept column
    return {"beta_tee": float(beta[tee_i]), "n_words": len(d), "preds": "+".join(preds)}


def main():
    tee = pd.read_csv(TEE_CSV)
    if len(tee) < 1000:
        sys.exit(f"zuco_tee.csv has only {len(tee)} rows -- still the toy csv? "
                 f"recompute with compute_tee_zuco.py before running this.")
    tee = lexical_cols(tee)
    keep = ["sent_idx", "word_idx", "tee_k3", "surp", "logfreq", "wlen", "has_trailing_punct"]
    tee = tee[keep]

    csvs = sorted(f for f in os.listdir(ET_DIR) if f.endswith(".csv"))
    print(f"{len(csvs)} subjects; TEE words: {len(tee)}\n", flush=True)

    rows = []
    for f in csvs:
        subj = os.path.splitext(f)[0]
        et = pd.read_csv(os.path.join(ET_DIR, f))
        m = et.merge(tee, on=["sent_idx", "word_idx"], how="inner")
        m = m[m["has_trailing_punct"] == 0]     # drop punct-final (attention-sink confound)
        rec = {"subject": subj}
        for oc in OUTCOMES:
            if oc not in m.columns:
                continue
            r = subject_slope(m, oc)
            if r:
                rec[f"beta_{oc}"] = r["beta_tee"]
                rec[f"n_{oc}"] = r["n_words"]
        rows.append(rec)

    S = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    S.to_csv(OUT, index=False)

    print("=== Subject-level TEE partial slope on fixation duration ===")
    print("(standardized; controls = surprisal + log-freq + word length; n=12 subjects)\n")
    print(f"{'outcome':8} {'mean beta':>10} {'pos/12':>7} {'t p':>8} {'wilcoxon p':>11}")
    for oc in OUTCOMES:
        col = f"beta_{oc}"
        if col not in S:
            continue
        b = S[col].dropna().to_numpy()
        if len(b) < 3:
            continue
        pos = int((b > 0).sum())
        tp = stats.ttest_1samp(b, 0).pvalue
        try:
            wp = stats.wilcoxon(b).pvalue
        except ValueError:
            wp = np.nan
        print(f"{oc:8} {b.mean():>+10.4f} {pos:>4}/{len(b):<2} {tp:>8.4f} {wp:>11.4f}")
    print(f"\nsaved per-subject slopes -> {OUT}")
    print("\nInterpretation guide: a POSITIVE mean beta that is consistent across")
    print("subjects (high pos/12, small p) = longer TEE -> longer fixations, i.e.")
    print("TEE predicts reading time beyond surprisal+freq+length. A null here is a")
    print("REAL null (unlike the EEG one), because this measurement isn't broken.")


if __name__ == "__main__":
    main()
