"""
TABLE 1 RERUN WITH SINK-CLEAN TEE
=================================
Refits the arXiv 2606.05346 garden-path reading-time models (Table 1, M0-M5)
with TEE computed three ways:
  A_isolated  : sentence alone -- the presumed original condition (token 0 = sink)
  B_prefix    : neutral prefix prepended so the sink sits outside all windows
  C_droptok0  : isolated, word 0 excluded from fit windows

Data: SAP ClassicGP self-paced reading (N=2000 participants, 24 items x 6 types).
Critical region ROI 0/1/2 (disambiguating word + 2 spillover), per the paper.
Controls: word length, word position, previous log RT, log word frequency.
Surprisal computed under the matching presentation.
Outcome: log RT. Models compared by AIC, as in the paper.
"""

import numpy as np
import pandas as pd
import torch
import statsmodels.api as sm
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from wordfreq import zipf_frequency
import os, warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
PREFIX = "Yesterday afternoon we sat together and read a few short stories aloud."
PRES = ["A_isolated", "B_prefix", "C_droptok0"]
CONFIGS = [("L6_k3", 6, 3), ("L12_k5", 12, 5), ("L6_k5", 6, 5), ("L6_k7", 6, 7)]
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

tok = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)


def encode(words, prefix=None):
    ids, final_idx = [], []
    if prefix is not None:
        ids.extend(tok.encode(prefix))
    for i, w in enumerate(words):
        piece = (" " + w) if (i > 0 or prefix is not None) else w
        ids.extend(tok.encode(piece))
        final_idx.append(len(ids) - 1)
    return ids, final_idx


def measures(words, prefix=None, drop0=False):
    """Per-word TEE (each config) and surprisal for one presentation."""
    ids, final_idx = encode(words, prefix=prefix)
    with torch.no_grad():
        out = model(torch.tensor([ids]).to(DEVICE))
    logits = out.logits[0].float()
    logprobs = torch.log_softmax(logits, -1)
    # surprisal of token t (t>=1) from logits at t-1; sum subwords within a word
    surp_tok = np.zeros(len(ids))
    for t in range(1, len(ids)):
        surp_tok[t] = -float(logprobs[t - 1, ids[t]]) / np.log(2)
    starts = [0] + [j + 1 for j in final_idx[:-1]]
    surp = [float(surp_tok[s:e + 1].sum()) for s, e in zip(starts, final_idx)]

    res = {}
    for name, L, k in CONFIGS:
        W = out.hidden_states[L][0].float().cpu().numpy()[final_idx]
        vals = np.full(len(words), np.nan)
        for i in range(len(words)):
            lo = i - k
            if drop0:
                lo = max(lo, 1)
            if lo < 0 or i - lo < 2:
                continue
            Y = W[lo:i]
            m = Y.shape[0]
            t = np.arange(m, dtype=float)
            A = np.vstack([t, np.ones(m)]).T
            coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
            vals[i] = np.linalg.norm(W[i] - (coef[0] * m + coef[1]))
        res[name] = vals
    return res, surp


def build():
    d = pd.read_csv(RT_CSV)
    d = d[d.ROI.astype(str).isin(["0", "1", "2"])].copy()
    # per-sentence word lists (from the presented words themselves)
    key = ["item", "Type"]
    sent_words = (pd.read_csv(RT_CSV)
                  .drop_duplicates(subset=key + ["WordPosition"])
                  .sort_values(key + ["WordPosition"])
                  .groupby(key)["EachWord"].apply(list))
    rows = []
    for (item, typ), words in sent_words.items():
        for pres in PRES:
            m, surp = measures(words,
                               prefix=PREFIX if pres == "B_prefix" else None,
                               drop0=(pres == "C_droptok0"))
            for i, w in enumerate(words):
                r = dict(item=item, Type=typ, WordPosition=i + 1, pres=pres,
                         surprisal=surp[i])
                for name, _, _ in CONFIGS:
                    r[name] = m[name][i]
                rows.append(r)
    meas = pd.DataFrame(rows)
    meas.to_csv(os.path.join(HERE, "gp_table1_measures.csv"), index=False)

    # previous-word RT within trial, from the unfiltered frame
    full = pd.read_csv(RT_CSV)[["MD5", "item", "Type", "WordPosition", "RT"]]
    full = full.rename(columns={"RT": "prevRT"})
    full["WordPosition"] = full["WordPosition"] + 1
    d = d.merge(full, on=["MD5", "item", "Type", "WordPosition"], how="left")
    d["word_len"] = d.EachWord.str.len()
    d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
        lambda w: zipf_frequency(w, "en"))
    d = d[(d.RT >= 100) & (d.RT <= 5000) & (d.prevRT >= 100) & (d.prevRT <= 5000)]
    d["logRT"] = np.log(d.RT)
    d["prev_logRT"] = np.log(d.prevRT)
    return d, meas


def z(x):
    return (x - np.nanmean(x)) / np.nanstd(x)


def fit(df, extra):
    cols = ["word_len", "WordPosition", "prev_logRT", "log_freq"] + extra
    X = pd.DataFrame({c: z(df[c].astype(float)) for c in cols})
    X = sm.add_constant(X)
    return sm.OLS(df["logRT"].values, X.values).fit()


def run():
    d, meas = build()
    names = [c for c, _, _ in CONFIGS]

    # one wide frame: every measure from every presentation on the SAME rows
    wide = d.copy()
    for pres in PRES:
        m = meas[meas.pres == pres].drop(columns="pres").rename(
            columns={n: f"{n}__{pres}" for n in names} | {"surprisal": f"surp__{pres}"})
        wide = wide.merge(m, on=["item", "Type", "WordPosition"], how="left")
    wide = wide.dropna(subset=["log_freq"] + [f"surp__{p}" for p in PRES])

    # PER-CONFIG samples: rows where THAT config is defined under all three
    # presentations. A global intersection would delete the sentence-initial
    # rows (k=7 undefined there) -- i.e. exactly where the sink bites.
    for n in names:
        sub = wide.dropna(subset=[f"{n}__{p}" for p in PRES]).copy()
        a, b, c = (sub[f"{n}__{p}"] for p in PRES)
        exposed = float((np.abs(a.values - c.values) > 1e-9).mean())
        print(f"\n################ {n}  (n = {len(sub):,}, "
              f"{sub.MD5.nunique()} participants) ################")
        print(f"rows whose fit window touches word 0: {exposed:.1%}   "
              f"r(isolated, droptok0) = {np.corrcoef(a,c)[0,1]:.3f}   "
              f"r(isolated, prefix) = {np.corrcoef(a,b)[0,1]:.3f}")
        print(f"mean TEE  isolated {a.mean():.1f} | prefix {b.mean():.1f} "
              f"| droptok0 {c.mean():.1f}")
        for label, df in [("OLS", sub), ("participant-demeaned", demean(sub, names))]:
            print(f"\n  --- {label} ---")
            print(f"  {'presentation':<16}{'dAIC surp':>12}{'dAIC TEE':>11}"
                  f"{'beta':>10}{'p':>12}")
            for pres in PRES:
                sur, tv = f"surp__{pres}", f"{n}__{pres}"
                m0, m1 = fit(df, []), fit(df, [sur])
                mk = fit(df, [sur, tv])
                print(f"  {pres:<16}{m0.aic-m1.aic:>12.1f}{m1.aic-mk.aic:>11.1f}"
                      f"{mk.params[-1]:>10.4f}{mk.pvalues[-1]:>12.2e}")
    print("\nPaper Table 1 (for reference): M1 dAIC -1.9 (n.s.); "
          "L6/w3 +10.7; L12/w5 +56.4; L6/w5 0.0; L6/w7 +31.4; N = 95,173")


def demean(df, names):
    """Within-participant centering: approximates a by-participant random intercept."""
    out = df.copy()
    cols = ["logRT", "prev_logRT", "word_len", "WordPosition", "log_freq"] \
           + [f"{n}__{p}" for n in names for p in PRES] \
           + [f"surp__{p}" for p in PRES]
    g = out.groupby("MD5")
    for c in cols:
        out[c] = out[c] - g[c].transform("mean")
    return out


if __name__ == "__main__":
    run()
