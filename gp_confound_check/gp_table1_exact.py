"""
TABLE 1 UNDER THE ORIGINAL SPEC, WITH SINK CONTROLS
===================================================
Replicates model_comparison_stats.py from garden-path-p1 exactly
(mixedlm, random intercept by participant, ML fit; controls = word length,
word position, previous log RT; TEE and surprisal computed as in
window_sweep.py: word-level states at the last subword, linear fit over the
k preceding word states, extrapolate one step, Euclidean error) and then
recomputes the TEE predictor under three presentations:

  A_isolated  = the original: tokenizer(sentence), no BOS, no context
  B_prefix    = neutral prefix prepended (sink outside all fit windows)
  C_droptok0  = isolated, word 0 excluded from fit windows

NOTE ON SAMPLE: the original computes prev_log_RT by shifting within
(participant, Sentence) AFTER filtering to ROI 0/1/2, so every ROI-0 row gets
NaN and is dropped. The published N = 95,173 is ROI 1 and ROI 2 only -- the
disambiguating word is not in the RT models. This script reproduces that
sample exactly, and also reports a variant that keeps ROI 0 by taking
prev_log_RT from the full sentence.
"""

import numpy as np
import pandas as pd
import torch
import statsmodels.formula.api as smf
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import os, warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
PREFIX = "Yesterday afternoon we sat together and read a few short stories aloud."
PRES = ["A_isolated", "B_prefix", "C_droptok0"]
CONFIGS = [("L6_w3", 6, 3), ("L12_w5", 12, 5), ("L6_w5", 6, 5), ("L6_w7", 6, 7)]
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

tokz = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)


def measures(sentence, prefix=None, drop0=False):
    """Original window_sweep.py logic, with optional prefix / token-0 exclusion."""
    text = (prefix + " " + sentence) if prefix else sentence
    inputs = tokz(text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        out = model(**inputs)
    ids = inputs["input_ids"][0]
    toks = tokz.convert_ids_to_tokens(ids)
    logp = torch.log_softmax(out.logits, -1)
    tok_surp = [None] + [-float(logp[0, i - 1, ids[i]]) for i in range(1, len(ids))]

    # word -> token map, exactly as the original (split on leading-space marker)
    words = text.split()
    wmap, ti = [], 0
    for w in words:
        wt = []
        while ti < len(toks):
            if ti > 0 and toks[ti].startswith("Ġ") and len(wt) > 0:
                break
            wt.append(ti)
            ti += 1
        wmap.append(wt)

    n_pref = len(prefix.split()) if prefix else 0
    surp = [sum(tok_surp[t] for t in wt if tok_surp[t] is not None) for wt in wmap]

    res = {}
    for name, L, k in CONFIGS:
        h = out.hidden_states[L][0].float().cpu().numpy()
        wh = np.array([h[wt[-1]] for wt in wmap])
        errs = []
        for t in range(len(words)):
            lo = t - k
            if drop0:
                lo = max(lo, 1)
            if t < k or lo < 0 or (t - lo) < 2:
                errs.append(np.nan)
                continue
            win = wh[lo:t]
            m = len(win)
            A = np.column_stack([np.ones(m), np.arange(m)])
            c, *_ = np.linalg.lstsq(A, win, rcond=None)
            errs.append(float(np.linalg.norm(wh[t] - (c[0] + c[1] * m))))
        res[name] = errs[n_pref:]           # drop prefix words
    return res, surp[n_pref:]


def build_measures():
    src = pd.read_csv(RT_CSV)
    src["EachWord"] = src["EachWord"].str.replace("%2C", ",", regex=False)
    src["Sentence"] = src["Sentence"].str.replace("%2C", ",", regex=False)
    sents = (src.drop_duplicates(subset=["item", "Type", "WordPosition"])
             .sort_values(["item", "Type", "WordPosition"])
             .groupby(["item", "Type"])["Sentence"].first())
    rows = []
    for (item, typ), sent in sents.items():
        for pres in PRES:
            m, sp = measures(sent, prefix=PREFIX if pres == "B_prefix" else None,
                             drop0=(pres == "C_droptok0"))
            for i in range(len(sp)):
                r = dict(item=item, Type=typ, WordPosition=i + 1, pres=pres,
                         surprisal=sp[i])
                for name, _, _ in CONFIGS:
                    r[name] = m[name][i]
                rows.append(r)
    return pd.DataFrame(rows)


def build_rt(keep_roi0=False):
    rt = pd.read_csv(RT_CSV)
    rt["participant"] = rt["MD5"]
    rt["EachWord"] = rt["EachWord"].str.replace("%2C", ",", regex=False)
    rt["Sentence"] = rt["Sentence"].str.replace("%2C", ",", regex=False)
    rt = rt[(rt.RT > 100) & (rt.RT < 5000)].copy()
    rt["word_length"] = rt.EachWord.str.len()
    rt["log_RT"] = np.log(rt.RT)
    if keep_roi0:   # prev RT from the whole sentence, so ROI 0 survives
        rt = rt.sort_values(["participant", "Sentence", "WordPosition"])
        rt["prev_log_RT"] = rt.groupby(["participant", "Sentence"])["log_RT"].shift(1)
        d = rt[rt.ROI.isin([0, 1, 2])].copy()
    else:           # ORIGINAL: shift after filtering -> ROI 0 dropped
        d = rt[rt.ROI.isin([0, 1, 2])].copy()
        d = d.sort_values(["participant", "Sentence", "WordPosition"])
        d["prev_log_RT"] = d.groupby(["participant", "Sentence"])["log_RT"].shift(1)
    return d


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


FORM0 = "log_RT ~ z_word_length + z_WordPosition + z_prev_log_RT + z_surprisal"


def run(keep_roi0=False):
    meas = build_measures()
    d = build_rt(keep_roi0)
    tag = "ROI 0+1+2 (ROI 0 restored)" if keep_roi0 else "ROI 1+2 (original sample)"
    print(f"\n{'='*70}\n{tag}\n{'='*70}")
    for name, _, k in CONFIGS:
        print(f"\n#### {name} ####")
        print(f"{'presentation':<14}{'N':>8}{'dAIC':>9}{'beta':>10}{'p':>12}"
              f"{'win touches w0':>16}")
        for pres in PRES:
            m = meas[meas.pres == pres][["item", "Type", "WordPosition", "surprisal", name]]
            t = d.merge(m, left_on=["item", "Type", "WordPosition"],
                        right_on=["item", "Type", "WordPosition"], how="left")
            t = t.dropna(subset=["log_RT", "word_length", "WordPosition",
                                 "prev_log_RT", "surprisal", name])
            for c, zc in [("word_length", "z_word_length"), ("WordPosition", "z_WordPosition"),
                          ("prev_log_RT", "z_prev_log_RT"), ("surprisal", "z_surprisal"),
                          (name, "z_ee")]:
                t[zc] = z(t[c])
            m1 = smf.mixedlm(FORM0, t, groups=t["participant"]).fit(reml=False)
            m2 = smf.mixedlm(FORM0 + " + z_ee", t, groups=t["participant"]).fit(reml=False)
            exposed = (t.WordPosition - 1 - k <= 0).mean()
            print(f"{pres:<14}{len(t):>8,}{m1.aic-m2.aic:>9.1f}"
                  f"{m2.params['z_ee']:>10.4f}{m2.pvalues['z_ee']:>12.2e}"
                  f"{exposed:>15.1%}")
    print("\nPublished Table 1: L6/w3 +10.7 | L12/w5 +56.4 | L6/w5 0.0 | L6/w7 +31.4")


if __name__ == "__main__":
    run(keep_roi0=False)
    run(keep_roi0=True)
