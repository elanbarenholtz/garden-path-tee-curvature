#!/usr/bin/env python3
"""
Does TEE bite harder in high-reorientation sentences? Direct test of the serial/
garden-path account: if TEE indexes a trajectory-reorientation cost, its effect
on reading time should be LARGER in structurally harder sentences and small/flat
in easy ones. If instead the (weak) TEE effect is uniform across sentence types,
the reorientation story is not doing the work.

Difficulty is defined at the SENTENCE level and INDEPENDENTLY of the target
word's TEE (avoids circularity):
  - len_hard : sentence longer than the median (# words)
  - has_rc   : sentence contains a relative-clause / embedding marker
               (which/who/whom/whose) -- crude but interpretable proxy
(Both are structural, not TEE-derived. A robustness moderator, sentence max
surprisal, is also reported; since TEE is ~orthogonal to surprisal it is a fair
independent difficulty index.)

Two analyses per outcome (FFD/GD/TRT):
  A. Interaction LMM (powered): y_z ~ TEE_z * hard + surp_z + logfreq_z + wlen_z,
     random intercept+TEE slope by subject. The TEE:hard coefficient is the test.
  B. Stratified per-subject (robust): TEE slope fit within hard vs easy separately,
     per subject, then compared across subjects (paired Wilcoxon).

Usage:
    python3 analyze_difficulty_split.py [ET_DIR] [TEE_CSV]
      defaults: zuco_et  zuco_tee_real.csv
"""
import os, sys, re
import numpy as np
import pandas as pd
from scipy import stats

ET_DIR = sys.argv[1] if len(sys.argv) > 1 else "zuco_et"
TEE_CSV = sys.argv[2] if len(sys.argv) > 2 else "zuco_tee_real.csv"
OUTCOMES = ["FFD", "GD", "TRT"]
RC_MARKERS = {"which", "who", "whom", "whose"}

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


def load_words():
    tee = pd.read_csv(TEE_CSV)
    if len(tee) < 1000:
        sys.exit(f"{TEE_CSV} has {len(tee)} rows -- still the toy file. Recompute TEE.")
    tee["wlen"] = tee["word"].map(lambda w: len(clean_word(w)))
    tee["logfreq"] = (tee["word"].map(lambda w: zipf_frequency(clean_word(w).lower() or "the", "en"))
                      if zipf_frequency is not None else 0.0)
    # sentence-level difficulty, independent of a word's own TEE
    g = tee.groupby("sent_idx")
    sent = pd.DataFrame({
        "n_words": g.size(),
        "has_rc": g["word"].apply(lambda ws: int(any(clean_word(x).lower() in RC_MARKERS for x in ws))),
        "max_surp": g["surp"].max(),
    })
    med = sent["n_words"].median()
    sent["len_hard"] = (sent["n_words"] > med).astype(int)
    sent["surp_hard"] = (sent["max_surp"] > sent["max_surp"].median()).astype(int)
    tee = tee.merge(sent[["len_hard", "has_rc", "surp_hard"]], left_on="sent_idx", right_index=True)
    print(f"sentences: {len(sent)}  (len median={med:.0f}; "
          f"{int(sent.len_hard.sum())} long, {int(sent.has_rc.sum())} with RC marker)\n")
    return tee


def build():
    tee = load_words()
    keep = ["sent_idx", "word_idx", "tee_k3", "surp", "logfreq", "wlen",
            "has_trailing_punct", "len_hard", "has_rc", "surp_hard"]
    tee = tee[keep]
    frames = []
    for f in sorted(x for x in os.listdir(ET_DIR) if x.endswith(".csv")):
        et = pd.read_csv(os.path.join(ET_DIR, f))
        et["subject"] = os.path.splitext(f)[0]
        frames.append(et.merge(tee, on=["sent_idx", "word_idx"], how="inner"))
    df = pd.concat(frames, ignore_index=True)
    return df[df["has_trailing_punct"] == 0]


def interaction_lmm(df, oc, mod):
    d = df.dropna(subset=[oc, "tee_k3", "surp", "logfreq", "wlen", mod]).copy()
    d = d[d[oc] > 0]
    for c in ["tee_k3", "surp", "logfreq", "wlen"]:
        d[c + "_z"] = zc(d[c])
    d["y_z"] = zc(d[oc]); d["hard"] = d[mod].astype(float)
    md = smf.mixedlm(f"y_z ~ tee_k3_z * hard + surp_z + logfreq_z + wlen_z",
                     d, groups=d["subject"], re_formula="~tee_k3_z")
    fit = md.fit(method="lbfgs", maxiter=300, disp=False)
    key = "tee_k3_z:hard"
    return {"n": len(d), "tee_easy": fit.params["tee_k3_z"],
            "inter": fit.params[key], "inter_se": fit.bse[key], "inter_p": fit.pvalues[key]}


def stratified(df, oc, mod):
    """Per-subject standardized TEE slope within hard vs easy; paired across subjects."""
    easy_b, hard_b = [], []
    for subj, d0 in df.groupby("subject"):
        d0 = d0.dropna(subset=[oc, "tee_k3", "surp", "logfreq", "wlen", mod])
        d0 = d0[d0[oc] > 0]
        betas = {}
        for lab, sub in [("easy", d0[d0[mod] == 0]), ("hard", d0[d0[mod] == 1])]:
            if len(sub) < 40 or sub["tee_k3"].std() == 0:
                betas[lab] = np.nan; continue
            y = zc(sub[oc]); X = np.column_stack([np.ones(len(sub))] +
                [zc(sub[c]) for c in ["tee_k3", "surp", "logfreq", "wlen"]])
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            betas[lab] = beta[1]
        easy_b.append(betas["easy"]); hard_b.append(betas["hard"])
    e = np.array(easy_b, float); h = np.array(hard_b, float)
    ok = ~np.isnan(e) & ~np.isnan(h)
    e, h = e[ok], h[ok]
    p = np.nan
    if len(e) >= 3 and np.any(h - e != 0):
        try: p = stats.wilcoxon(h, e).pvalue
        except ValueError: pass
    return {"n_subj": len(e), "easy_mean": e.mean(), "hard_mean": h.mean(), "paired_p": p}


def main():
    df = build()
    per = df.groupby("subject").size()
    print(f"merged {len(per)} subjects, {int(per.median())} words/subject median\n")
    for mod, label in [("len_hard", "SENTENCE LENGTH (long vs short)"),
                       ("has_rc", "RELATIVE-CLAUSE marker present vs absent"),
                       ("surp_hard", "MAX SURPRISAL (high vs low) [robustness]")]:
        print(f"==================== moderator: {label} ====================")
        print(f"{'outcome':7} | {'A. interaction LMM':^40} | {'B. stratified per-subject':^34}")
        print(f"{'':7} | {'TEE(easy)':>9} {'TEE:hard':>9} {'SE':>7} {'p':>9} | "
              f"{'easyβ':>7} {'hardβ':>7} {'paired p':>9}")
        for oc in OUTCOMES:
            if oc not in df.columns:
                continue
            try:
                a = interaction_lmm(df, oc, mod)
                b = stratified(df, oc, mod)
                print(f"{oc:7} | {a['tee_easy']:>+9.4f} {a['inter']:>+9.4f} {a['inter_se']:>7.4f} "
                      f"{a['inter_p']:>9.4g} | {b['easy_mean']:>+7.3f} {b['hard_mean']:>+7.3f} "
                      f"{b['paired_p']:>9.4g}")
            except Exception as e:
                print(f"{oc:7} | FAILED: {e}")
        print()
    print("READ: theory predicts a POSITIVE, significant TEE:hard interaction (A) and")
    print("hardβ > easyβ (B). If TEE's effect is flat across difficulty, the serial/")
    print("garden-path reorientation account is NOT carrying the ZuCo behavior.")


if __name__ == "__main__":
    main()
