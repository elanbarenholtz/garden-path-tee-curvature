"""
GARDEN PATH SINK/PUNCTUATION DIAGNOSTIC
=======================================
Tests whether the SAP ClassicGP ambiguous-vs-unambiguous TEE effect at the
disambiguating word (arXiv 2606.05346, Sec 3.1) survives removal of the
attention-sink first token and punctuation asymmetries.

Presentation conditions:
  A_isolated   : sentence alone (presumed paper condition; token 0 = sink)
  B_prefix     : neutral 10-word prefix prepended (sink far from windows)
  C_droptok0   : isolated, but word 0 excluded from all fit windows

Per condition: TEE at the disambiguating word, layers 6 and 12, k = 3,5,7
(word-level trajectory over final-subword states, linear fit, Euclidean
error — matching the manuscript spec). Paired amb-unamb stats per
construction (MVRR, NPS, NPZ) and overall. Bookkeeping: does the fit
window contain word 0? does it contain a punctuation-final state?
Also reports the token-0 norm ratio to document the sink itself.
"""

import numpy as np
import pandas as pd
import torch
from scipy import stats
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import os, sys, warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
STIM = os.path.join(HERE, "items_ClassicGP.csv")
PREFIX = "Yesterday afternoon we sat together and read a few short stories aloud."
LAYERS = [6, 12]
KS = [3, 5, 7]
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

tok = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)

PUNCT = set(".,;:!?\"'`)(")

def word_states(text, prefix=None):
    """Return per-word final-subword hidden states {layer: [n_words, 768]},
    plus per-word punct-final flags. Words = whitespace tokens of `text`
    (prefix words excluded from the returned arrays)."""
    words = text.split()
    ids, final_idx = [], []
    if prefix is not None:
        pref_ids = tok.encode(prefix)
        ids.extend(pref_ids)
    for i, w in enumerate(words):
        piece = (" " + w) if (i > 0 or prefix is not None) else w
        wid = tok.encode(piece)
        ids.extend(wid)
        final_idx.append(len(ids) - 1)
    with torch.no_grad():
        out = model(torch.tensor([ids]).to(DEVICE))
    hs = {L: out.hidden_states[L][0].float().cpu().numpy() for L in LAYERS}
    W = {L: hs[L][final_idx] for L in LAYERS}
    punct_final = [w[-1] in PUNCT for w in words]
    tok0_norm = float(np.linalg.norm(out.hidden_states[LAYERS[0]][0][0].float().cpu().numpy()))
    interior = float(np.mean(np.linalg.norm(hs[LAYERS[0]][1:], axis=1)))
    return W, punct_final, tok0_norm, interior

def tee(W, i, k, drop0=False):
    """TEE at word i: linear fit over word states i-k..i-1, extrapolate."""
    lo = i - k
    if drop0:
        lo = max(lo, 1)
    if lo < 0 or i - lo < 2:
        return np.nan, None
    Y = W[lo:i]                      # m x 768
    m = Y.shape[0]
    t = np.arange(m, dtype=float)
    A = np.vstack([t, np.ones(m)]).T
    coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
    pred = coef[0] * m + coef[1]
    return float(np.linalg.norm(W[i] - pred)), lo

def run():
    df = pd.read_csv(STIM)
    rows = []
    sink_ratios = []
    for _, r in df.iterrows():
        ctype = r["condition"].split("_")[0]           # MVRR / NPS / NPZ
        for cond, sent, dpos in [("amb", r["ambiguous"], int(r["disambPositionAmb"])),
                                 ("unamb", r["unambiguous"], int(r["disambPositionUnamb"]))]:
            i = dpos - 1                               # 1-indexed -> 0-indexed
            for pres in ["A_isolated", "B_prefix", "C_droptok0"]:
                prefix = PREFIX if pres == "B_prefix" else None
                W, pf, t0n, intn = word_states(sent, prefix=prefix)
                if pres == "A_isolated":
                    sink_ratios.append(t0n / intn)
                for L in LAYERS:
                    for k in KS:
                        e, lo = tee(W[L], i, k, drop0=(pres == "C_droptok0"))
                        if lo is None:
                            continue
                        rows.append(dict(
                            item=r["item"], ctype=ctype, cond=cond, pres=pres,
                            layer=L, k=k, tee=e,
                            win_has_word0=(lo == 0),
                            win_has_punct=any(pf[lo:i]),
                            crit_is_punct=pf[i], dpos=dpos))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "gp_sink_check_results.csv"), index=False)
    print(f"n sentences: {df.shape[0]*2} | device {DEVICE}")
    print(f"token-0 norm / interior norm (L{LAYERS[0]}, isolated): "
          f"median {np.median(sink_ratios):.1f}x")
    print("\n=== paired amb - unamb TEE at disambiguating word ===")
    hdr = f"{'pres':<12}{'L':<4}{'k':<4}{'d_mean':>9}{'t':>8}{'p':>12}   win0 amb/un   punct amb/un"
    for pres in ["A_isolated", "B_prefix", "C_droptok0"]:
        print("\n" + hdr)
        for L in LAYERS:
            for k in KS:
                sub = out[(out.pres == pres) & (out.layer == L) & (out.k == k)]
                p_ = sub.pivot_table(index=["item", "ctype"], columns="cond", values="tee").dropna()
                d = p_["amb"] - p_["unamb"]
                tt = stats.ttest_1samp(d, 0)
                w0 = sub.groupby("cond")["win_has_word0"].mean()
                pu = sub.groupby("cond")["win_has_punct"].mean()
                print(f"{pres:<12}{L:<4}{k:<4}{d.mean():>9.2f}{tt.statistic:>8.2f}{tt.pvalue:>12.2e}"
                      f"   {w0.get('amb',0):.2f}/{w0.get('unamb',0):.2f}"
                      f"      {pu.get('amb',0):.2f}/{pu.get('unamb',0):.2f}")
    print("\n=== by construction (L6, k=3) ===")
    for pres in ["A_isolated", "B_prefix", "C_droptok0"]:
        for ct in ["MVRR", "NPS", "NPZ"]:
            sub = out[(out.pres == pres) & (out.layer == 6) & (out.k == 3) & (out.ctype == ct)]
            p_ = sub.pivot_table(index="item", columns="cond", values="tee").dropna()
            d = p_["amb"] - p_["unamb"]
            tt = stats.ttest_1samp(d, 0)
            print(f"{pres:<12}{ct:<6}d={d.mean():>8.2f}  t={tt.statistic:>6.2f}  p={tt.pvalue:.2e}  n={len(d)}")

if __name__ == "__main__":
    run()
