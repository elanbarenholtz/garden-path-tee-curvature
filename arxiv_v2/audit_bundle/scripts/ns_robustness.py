"""
NATURAL STORIES: the two robustness checks the paper is missing
==============================================================
1. PUNCTUATION. The locked sample's `final_bpe` is the token the word's state is
   read from; Natural Stories glues trailing punctuation onto words and GPT-2
   punctuation tokens are sink/rest states. Does the TEE effect survive a
   punctuation covariate, and does it survive on punctuation-free words only?

2. LEXICAL BASELINE. Frequency is the dominant predictor of TEE, so the question
   is whether TEE predicts RT beyond WORD IDENTITY. `ns_crossed_re.py` tried a
   (1|word_type) random effect and never completed. Equivalent and tractable:
   center log_RT and every predictor within word type (word-identity fixed
   effects by demeaning), which asks whether TEE explains RT variation for the
   SAME word across contexts.

Also reports the by-participant random-intercept headline for reference.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

REPO = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
CTRL = "z_word_length + z_log_freq + z_zone + z_prev_log_RT"
F1 = f"log_RT ~ {CTRL} + z_surprisal"
F2 = F1 + " + z_tee_k3"
PUNCT = set(".,;:!?\"'`)(-—")


def zc(d, cols):
    for c in cols:
        v = d[c].dropna()
        d["z_" + c] = (d[c] - v.mean()) / v.std()
    return d


def build():
    w = pd.read_csv(f"{REPO}/rebuild_v2_outputs/sample_8a6087341e.csv")
    w["punct_final"] = w.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
    rt = pd.read_csv(f"{REPO}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    m = rt.merge(w[["story_id", "zone", "word", "tee_k3", "surprisal", "word_length",
                    "log_freq", "punct_final"]], on=["story_id", "zone"], how="inner",
                 suffixes=("_rt", ""))
    m["log_RT"] = np.log(m.RT)
    m = m.sort_values(["participant", "story_id", "zone"])
    m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
    wcol = "word" if "word" in m.columns else "word_y"
    m["word_type"] = m[wcol].astype(str).str.lower().str.strip()
    d = m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                         "prev_log_RT", "surprisal", "tee_k3"]).copy()
    return zc(d, ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"])


def report(label, d, form1=F1, form2=F2, groups="participant"):
    m1 = smf.mixedlm(form1, d, groups=d[groups]).fit(reml=False, method="lbfgs")
    m2 = smf.mixedlm(form2, d, groups=d[groups]).fit(reml=False, method="lbfgs")
    print(f"{label:<44}n={len(d):>8,}  dAIC={m1.aic-m2.aic:>8.1f}  "
          f"beta={m2.params['z_tee_k3']:>+.5f}  p={m2.pvalues['z_tee_k3']:.2e}")
    return m2


def main():
    d = build()
    print(f"punct-final words in sample: {d.punct_final.mean():.1%} of observations\n")

    print("=" * 96)
    print("1. PUNCTUATION")
    print("=" * 96)
    report("headline (no punctuation control)", d)
    d2 = d.copy()
    d2["z_punct"] = (d2.punct_final - d2.punct_final.mean()) / d2.punct_final.std()
    report("+ punctuation covariate", d2,
           F1 + " + z_punct", F2 + " + z_punct")
    report("punctuation-free words only", d[d.punct_final == 0].pipe(
        zc, ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"]))

    print("\n" + "=" * 96)
    print("2. LEXICAL BASELINE (does TEE predict RT for the SAME word "
          "across contexts?)")
    print("=" * 96)
    dw = d.copy()
    cols = ["log_RT", "z_word_length", "z_log_freq", "z_zone", "z_prev_log_RT",
            "z_surprisal", "z_tee_k3"]
    g = dw.groupby("word_type")
    keep = g["log_RT"].transform("size") >= 5      # word must recur
    dw = dw[keep].copy()
    g = dw.groupby("word_type")
    for c in cols:
        dw[c] = dw[c] - g[c].transform("mean")
    print(f"word types retained (>=5 occurrences): {dw.word_type.nunique():,}")
    report("word-identity demeaned", dw)

    print("\n" + "=" * 96)
    print("3. BOTH (punctuation-free AND word-identity demeaned)")
    print("=" * 96)
    db = d[d.punct_final == 0].copy()
    db = zc(db, ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"])
    g = db.groupby("word_type")
    db = db[g["log_RT"].transform("size") >= 5].copy()
    g = db.groupby("word_type")
    for c in cols:
        db[c] = db[c] - g[c].transform("mean")
    report("punct-free + word-identity demeaned", db)


if __name__ == "__main__":
    main()
