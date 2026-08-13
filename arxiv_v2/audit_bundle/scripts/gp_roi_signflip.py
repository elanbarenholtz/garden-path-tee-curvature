"""
WHY DOES THE TEE-RT EFFECT FLIP SIGN AT THE DISAMBIGUATING WORD?
================================================================
Original spec (mixedlm, by-participant random intercept, ML; controls = word
length, word position, previous log RT, surprisal; TEE = L6 w=3, isolated
presentation). prev_log_RT is taken from the FULL sentence so ROI 0 survives.

Runs:
  1. Per-ROI models (-2..+3) -- is it a clean reversal at ROI 0 or noise?
  2. Does surprisal flip too? (if yes, it is about the position, not about TEE)
  3. Per construction and per ambiguity condition at ROI 0
  4. Word-property checks: is TEE at ROI 0 confounded with length/frequency/
     punctuation, and does controlling frequency remove the flip?
  5. Raw descriptive: mean logRT by TEE quintile at each ROI
"""

import numpy as np
import pandas as pd
import torch
import statsmodels.formula.api as smf
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from wordfreq import zipf_frequency
import os, warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
LAYER, K = 6, 3
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

tokz = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)


def measures(sentence):
    inputs = tokz(sentence, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        out = model(**inputs)
    ids = inputs["input_ids"][0]
    toks = tokz.convert_ids_to_tokens(ids)
    logp = torch.log_softmax(out.logits, -1)
    tok_surp = [None] + [-float(logp[0, i - 1, ids[i]]) for i in range(1, len(ids))]
    words = sentence.split()
    wmap, ti = [], 0
    for w in words:
        wt = []
        while ti < len(toks):
            if ti > 0 and toks[ti].startswith("Ġ") and len(wt) > 0:
                break
            wt.append(ti)
            ti += 1
        wmap.append(wt)
    surp = [sum(tok_surp[t] for t in wt if tok_surp[t] is not None) for wt in wmap]
    h = out.hidden_states[LAYER][0].float().cpu().numpy()
    wh = np.array([h[wt[-1]] for wt in wmap])
    errs = []
    for t in range(len(words)):
        if t < K:
            errs.append(np.nan)
            continue
        win = wh[t - K:t]
        A = np.column_stack([np.ones(K), np.arange(K)])
        c, *_ = np.linalg.lstsq(A, win, rcond=None)
        errs.append(float(np.linalg.norm(wh[t] - (c[0] + c[1] * K))))
    return errs, surp


def build():
    rt = pd.read_csv(RT_CSV)
    for c in ["EachWord", "Sentence"]:
        rt[c] = rt[c].str.replace("%2C", ",", regex=False)
    rt["participant"] = rt["MD5"]
    rt = rt[(rt.RT > 100) & (rt.RT < 5000)].copy()
    rt["log_RT"] = np.log(rt.RT)
    rt = rt.sort_values(["participant", "Sentence", "WordPosition"])
    rt["prev_log_RT"] = rt.groupby(["participant", "Sentence"])["log_RT"].shift(1)
    rt["word_length"] = rt.EachWord.str.len()
    rt["log_freq"] = rt.EachWord.str.strip(".,;:!?").str.lower().map(
        lambda w: zipf_frequency(w, "en"))
    rt["is_punct_final"] = rt.EachWord.str[-1].isin(list(".,;:!?"))

    sents = (rt.drop_duplicates(subset=["item", "Type", "WordPosition"])
             .sort_values(["item", "Type", "WordPosition"])
             .groupby(["item", "Type"])["Sentence"].first())
    rows = []
    for (item, typ), s in sents.items():
        e, sp = measures(s)
        for i in range(len(sp)):
            rows.append(dict(item=item, Type=typ, WordPosition=i + 1,
                             tee=e[i], surprisal=sp[i]))
    return rt.merge(pd.DataFrame(rows), on=["item", "Type", "WordPosition"], how="left")


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


CTRL = ["word_length", "WordPosition", "prev_log_RT", "surprisal"]


def prep(df, extra=()):
    """z-score predictors; drop any that are constant within this subset
    (e.g. ROI -2 is the same word in every item, so word_length has no
    variance there and would z-score to all-NaN)."""
    cols = CTRL + ["tee"] + list(extra)
    d = df.dropna(subset=["log_RT"] + cols).copy()
    d.attrs["terms"] = []
    for c in cols:
        if d[c].std() > 0:
            d["z_" + c] = z(d[c])
            d.attrs["terms"].append("z_" + c)
    return d


def coef(d, term, extra_terms=()):
    terms = [t for t in d.attrs["terms"] if t != "z_tee"] + list(extra_terms)
    if term not in terms:
        terms = terms + [term]
    form = "log_RT ~ " + " + ".join(terms)
    m = smf.mixedlm(form, d, groups=d["participant"]).fit(reml=False)
    return m.params[term], m.pvalues[term], m.aic


def run():
    d = build()
    print(f"device {DEVICE}\n")

    print("=" * 74)
    print("1. PER-ROI: TEE and surprisal coefficients (L6 w=3, isolated)")
    print("=" * 74)
    print(f"{'ROI':>5}{'n':>9}{'beta TEE':>12}{'p':>12}{'beta surp':>12}{'p':>12}")
    for roi in [-2, -1, 0, 1, 2, 3]:
        sub = prep(d[d.ROI == roi])
        if len(sub) < 500:
            continue
        bt, pt, _ = coef(sub, "z_tee")
        bs, ps, _ = coef(sub, "z_surprisal", extra_terms=["z_tee"])
        print(f"{roi:>5}{len(sub):>9,}{bt:>12.4f}{pt:>12.2e}{bs:>12.4f}{ps:>12.2e}")

    print("\n" + "=" * 74)
    print("2. ROI 0 by construction and by ambiguity")
    print("=" * 74)
    r0 = d[d.ROI == 0]
    for label, sub in ([(f"construction {c}", r0[r0.CONSTRUCTION == c])
                        for c in ["MVRR", "NPS", "NPZ"]] +
                       [(f"AMBUAMB {a}", r0[r0.AMBUAMB == a]) for a in sorted(r0.AMBUAMB.unique())]):
        s = prep(sub)
        if len(s) < 500:
            continue
        b, p, _ = coef(s, "z_tee")
        print(f"  {label:<22}n={len(s):>7,}  beta={b:>8.4f}  p={p:.2e}")

    print("\n" + "=" * 74)
    print("3. Does a frequency control remove the ROI-0 flip?")
    print("=" * 74)
    for roi in [0, 1, 2]:
        sub = prep(d[d.ROI == roi], extra=["log_freq"])
        no_freq = [t for t in sub.attrs["terms"] if t not in ("z_tee", "z_log_freq")]
        sub2 = sub.copy(); sub2.attrs["terms"] = no_freq
        b1, p1, _ = coef(sub2, "z_tee")
        b2, p2, _ = coef(sub, "z_tee")
        print(f"  ROI {roi}: without freq {b1:>8.4f} (p={p1:.1e})   "
              f"with freq {b2:>8.4f} (p={p2:.1e})")

    print("\n" + "=" * 74)
    print("4. What is TEE correlated with at each ROI? (word-level, n=144 sents)")
    print("=" * 74)
    w = d.drop_duplicates(subset=["item", "Type", "WordPosition"])
    print(f"{'ROI':>5}{'r(tee,len)':>13}{'r(tee,freq)':>13}{'r(tee,surp)':>13}"
          f"{'% punct-final':>15}{'mean tee':>10}")
    for roi in [-2, -1, 0, 1, 2, 3]:
        s = w[(w.ROI == roi)].dropna(subset=["tee", "log_freq"])
        if len(s) < 20:
            continue
        print(f"{roi:>5}{s.tee.corr(s.word_length):>13.3f}{s.tee.corr(s.log_freq):>13.3f}"
              f"{s.tee.corr(s.surprisal):>13.3f}{s.is_punct_final.mean():>14.1%}"
              f"{s.tee.mean():>10.1f}")

    print("\n" + "=" * 74)
    print("5. Descriptive: mean logRT by TEE quintile, per ROI (raw, no controls)")
    print("=" * 74)
    for roi in [0, 1, 2]:
        s = d[(d.ROI == roi)].dropna(subset=["tee", "log_RT"]).copy()
        s["q"] = pd.qcut(s.tee, 5, labels=False, duplicates="drop")
        mm = s.groupby("q").log_RT.mean()
        print(f"  ROI {roi}: " + "  ".join(f"Q{i+1} {v:.3f}" for i, v in mm.items()))


if __name__ == "__main__":
    run()
