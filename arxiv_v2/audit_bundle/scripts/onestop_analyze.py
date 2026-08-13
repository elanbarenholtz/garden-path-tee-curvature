"""
DOES TEE PREDICT EYE MOVEMENTS IN ONESTOP? (subject-level inference)
====================================================================
Pre-registered expectation from the Natural Stories work:
  - TEE should predict reading time beyond length, frequency and surprisal
  - the effect should be ABSENT at sentence-initial positions and present
    later in the sentence (the position boundary condition)
  - ZuCo's null should be attributable to power (42% detection at n=10)

Three dependent measures, matching the ZuCo analysis:
  FFD = IA_FIRST_FIXATION_DURATION
  GD  = IA_FIRST_RUN_DWELL_TIME     (gaze duration)
  TRT = IA_DWELL_TIME               (total reading time)

Inference: one regression per participant, then a group test across
participants. Never pooled across words.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import os, warnings
warnings.filterwarnings("ignore")

HERE = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check")
IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
DVS = {"FFD": "IA_FIRST_FIXATION_DURATION",
       "GD": "IA_FIRST_RUN_DWELL_TIME",
       "TRT": "IA_DWELL_TIME"}
PUNCT = set(".,;:!?\"'`)(-—")


def load():
    use = ["participant_id"] + KEY + list(DVS.values()) + \
          ["word_length", "wordfreq_frequency", "gpt2_surprisal"]
    d = pd.read_csv(IA, usecols=use, low_memory=False)
    T = pd.read_csv(f"{HERE}/onestop_tee.csv")
    d = d.merge(T[KEY + ["word", "tee_k3", "surprisal_own", "word_idx", "n_words"]],
                on=KEY, how="left")
    for c in list(DVS.values()) + ["word_length", "wordfreq_frequency",
                                   "gpt2_surprisal"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
    d["punct_final"] = d.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
    # position within sentence: restart after any sentence-final punctuation
    d = d.sort_values(["participant_id"] + KEY)
    sent_end = d.word.astype(str).str[-1].isin(list(".!?"))
    d["sent_idx"] = sent_end.groupby(
        [d.participant_id, d.article_id, d.paragraph_id, d.difficulty_level]
    ).cumsum().shift(1).fillna(0)
    d["from_sent_start"] = d.groupby(
        ["participant_id", "article_id", "paragraph_id", "difficulty_level",
         "sent_idx"]).cumcount()
    return d


PREDS = ["word_length", "log_freq", "surprisal_own", "tee_k3"]
PREDS_ZUCO = ["word_length", "log_freq", "tee_k3"]


def per_subject(d, dv, preds, min_n=150):
    out = []
    for pid, sub in d.groupby("participant_id"):
        s = sub.dropna(subset=preds + [dv])
        s = s[s[dv] > 0]
        if len(s) < min_n:
            continue
        X = s[preds].astype(float)
        sd = X.std(ddof=0)
        if (sd == 0).any():
            continue
        X = sm.add_constant((X - X.mean()) / sd)
        r = sm.OLS(np.log(s[dv].values), X.values).fit()
        out.append({"participant_id": pid, "n": len(s),
                    "beta": r.params[-1], "p": r.pvalues[-1]})
    return pd.DataFrame(out)


def group(B, label):
    if B is None or len(B) < 5:
        print(f"  {label:<40} too few participants")
        return
    pos = int((B.beta > 0).sum())
    w = stats.wilcoxon(B.beta).pvalue
    t = stats.ttest_1samp(B.beta, 0)
    print(f"  {label:<40} n={len(B):>4}  pos={pos:>3}/{len(B):<4} "
          f"({pos/len(B):>5.1%})  mean b={B.beta.mean():+.5f}  "
          f"Wilcoxon p={w:.2e}  t={t.statistic:>6.2f}  sig={int((B.p<.05).sum())}")


def main():
    d = load()
    print(f"rows={len(d):,}  participants={d.participant_id.nunique()}  "
          f"words with TEE={d.tee_k3.notna().sum():,}\n")

    print("=" * 108)
    print("MAIN: TEE beyond length, frequency, surprisal (subject-level)")
    print("=" * 108)
    for name, dv in DVS.items():
        group(per_subject(d, dv, PREDS), f"{name}  (full controls)")

    print("\n" + "=" * 108)
    print("ZuCo-style controls (length + frequency only), for direct comparison")
    print("=" * 108)
    for name, dv in DVS.items():
        group(per_subject(d, dv, PREDS_ZUCO), f"{name}  (length+freq only)")

    print("\n" + "=" * 108)
    print("PUNCTUATION-FREE (word not punctuation-final)")
    print("=" * 108)
    pf = d[d.punct_final == 0]
    for name, dv in DVS.items():
        group(per_subject(pf, dv, PREDS), f"{name}  (punct-free)")

    print("\n" + "=" * 108)
    print("POSITION BOUNDARY CONDITION (predicted: null early, present later)")
    print("=" * 108)
    for name, dv in DVS.items():
        print(f"  -- {name} --")
        group(per_subject(d[d.from_sent_start <= 4], dv, PREDS), "first 5 words of sentence")
        group(per_subject(d[d.from_sent_start > 9], dv, PREDS), "beyond word 10")


if __name__ == "__main__":
    main()
