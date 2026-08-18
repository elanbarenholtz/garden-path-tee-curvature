"""
E9 part B -- curvature on the garden-path (SAP) materials.
PREREG_E9_curvature.md (committed before this run). Three analyses:

  B1 corpus-wide RT: the published A1 specification (VERIFY_sap.py) with
     curvature_3 in place of TEE (and jointly with it). Standing criterion.
  B2 ambiguity contrast at the disambiguating word (CriticalPosition):
     ambiguous-minus-unambiguous curvature per item, by construction.
     TEE's known reversal for MV/RR is the reference; the theoretical
     question is whether the ANGLE shows the contrast the intuition
     describes where the distance did not.
  B3 item-level: does the curvature difference predict the reading-time
     difference across items, construction controlled? (TEE and surprisal
     both failed here; expectation is null, reported either way.)

Curvature convention identical to E9/NS: token-level steps, mean of the 3
angles ending at the word's final subword, eligible where ls-4 >= 1.
Sentence processing identical to VERIFY_sap.py (offset alignment).
"""
import os, hashlib, warnings
import numpy as np
import pandas as pd
import torch
from transformers import GPT2TokenizerFast, GPT2LMHeadModel
from scipy import stats
import statsmodels.api as sm
from wordfreq import zipf_frequency
warnings.filterwarnings("ignore")

GP = os.path.expanduser(
    "~/Projects/garden-path-tee-curvature/gp_confound_check")
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
CACHE = f"{GP}/e9_sap_curv_measures.csv"
LAYER, K, MIN_ROWS = 6, 3, 100

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval()


def measures(wordlist):
    text = " ".join(wordlist)
    enc = tok(text, return_offsets_mapping=True)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    spans, cur = [], 0
    for w in wordlist:
        spans.append((cur, cur + len(w))); cur += len(w) + 1
    last_sub, wi = {}, 0
    for bi, (cs, ce) in enumerate(offs):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            last_sub.setdefault(wi, []).append(bi)
    with torch.no_grad():
        out = model(torch.tensor([ids]))
    h = out.hidden_states[LAYER][0].float().numpy()
    lp = torch.log_softmax(out.logits[0].float(), -1)
    tgt = torch.tensor(ids[1:])
    tok_s = np.zeros(len(ids))
    tok_s[1:] = (-lp[:-1].gather(1, tgt.unsqueeze(1)).squeeze(1)
                 / np.log(2)).numpy()
    n = len(wordlist)
    surp = np.full(n, np.nan)
    wh = np.full((n, h.shape[1]), np.nan)
    ls_of = np.full(n, -1)
    for w, toks in last_sub.items():
        surp[w] = float(tok_s[toks].sum())
        wh[w] = h[toks[-1]]
        ls_of[w] = toks[-1]
    tee = np.full(n, np.nan)
    curv = np.full(n, np.nan)
    for i in range(n):
        lo = max(i - K, 1)
        if i >= 4 and (i - lo) >= 2 and not (np.isnan(wh[lo:i]).any()
                                             or np.isnan(wh[i]).any()):
            Y = wh[lo:i]
            m = Y.shape[0]
            x = np.arange(m, dtype=float); xc = x - x.mean()
            slope = (xc[:, None] * (Y - Y.mean(0))).sum(0) / (xc ** 2).sum()
            intercept = Y.mean(0) - slope * x.mean()
            tee[i] = float(np.linalg.norm(wh[i] - (intercept + slope * m)))
        ls = ls_of[i]
        if ls - 4 >= 1:
            seg = np.diff(h[ls - 4:ls + 1].astype(np.float64), axis=0)
            nn = np.linalg.norm(seg, axis=1)
            if (nn > 1e-9).all():
                cosv = (seg[1:] * seg[:-1]).sum(1) / (nn[1:] * nn[:-1])
                curv[i] = float(np.arccos(np.clip(cosv, -1, 1)).mean())
    return tee, surp, curv


d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
idx = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
         .sort_values(["item", "Type", "WordPosition"]))

if os.path.exists(CACHE):
    V = pd.read_csv(CACHE)
else:
    rows = []
    for (item, typ), g in idx.groupby(["item", "Type"]):
        wl = [str(x) for x in g.EachWord.tolist()]
        tee, surp, curv = measures(wl)
        for j, (_, r) in enumerate(g.iterrows()):
            rows.append({"item": item, "Type": typ,
                         "WordPosition": r.WordPosition,
                         "tee": tee[j], "surp": surp[j], "curv3": curv[j],
                         "sent_len": len(wl)})
    V = pd.DataFrame(rows)
    V.to_csv(CACHE, index=False)

# validation: TEE/surp must match the verified independent pipeline
C = pd.read_csv(f"{GP}/sap_measures_independent.csv")
m = C.merge(V, on=["item", "Type", "WordPosition"], validate="one_to_one")
for a, b in [("tee_v", "tee"), ("surp_v", "surp")]:
    both = m[[a, b]].dropna()
    rel = (both[a] - both[b]).abs() / both[a].abs().clip(lower=1e-9)
    print(f"VALIDATION {a}: max rel diff {rel.max():.2e} "
          f"({'PASS' if rel.max() < 1e-5 else 'FAIL'})")

D = d.merge(V, on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
D["word_length"] = D.EachWord.str.len()
D["log_freq"] = D.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
D["punct"] = D.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
D["from_start"] = D.WordPosition.astype(float)
D["fs2"] = D.from_start ** 2
D["from_end"] = (D.sent_len - D.WordPosition).astype(float)
D["fe2"] = D.from_end ** 2
D = D[(D.RT >= 100) & (D.RT <= 5000)].copy()
D["log_RT"] = np.log(D.RT)
D = D.dropna(subset=["tee", "surp", "curv3", "word_length", "log_freq",
                     "log_RT"])
print(f"analysis rows {len(D):,}   participants "
      f"{D.participant.nunique():,}  (TEE-sample reference: 444,737)")


def zsn(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


LEX = ["word_length", "log_freq", "punct"]
POS = ["from_start", "fs2", "from_end", "fe2"]
groups = {p: s for p, s in D.groupby("participant")}


def per_subj(target, cols):
    b = []
    for pid, sub in groups.items():
        s = sub.dropna(subset=cols + ["log_RT"])
        if len(s) < MIN_ROWS:
            continue
        X = np.column_stack([zsn(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        b.append(sm.OLS(zsn(s.log_RT.values), sm.add_constant(X)
                        ).fit().params[cols.index(target) + 1])
    b = np.array(b)
    pos = (b > 0).mean()
    w = stats.wilcoxon(b)
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"  {target:<7} | {'+'.join(c for c in cols if c != target)[:40]:<42}"
          f" beta {b.mean():+.5f}  %pos {pos:.1%}  p {w.pvalue:.2e}  "
          f"{'PASS' if ok else 'FAIL'}")


print("\nB1. CORPUS-WIDE RT (published A1 spec)")
per_subj("curv3", ["curv3", "surp"] + LEX + POS)
per_subj("tee", ["tee", "surp"] + LEX + POS)
per_subj("curv3", ["curv3", "tee", "surp"] + LEX + POS)

print("\nB2. AMBIGUITY CONTRAST AT THE DISAMBIGUATING WORD")
crit = D.drop_duplicates(subset=["item", "Type", "WordPosition"])
crit = crit[crit.WordPosition == crit.CriticalPosition]
amb = crit.pivot_table(index=["item", "CONSTRUCTION"], columns="AMBUAMB",
                       values=["curv3", "tee", "surp"], aggfunc="first")
for meas in ["curv3", "tee", "surp"]:
    try:
        diff = amb[(meas, "AMB")] - amb[(meas, "UAMB")]
    except KeyError:
        cols_avail = amb.columns.get_level_values(1).unique().tolist()
        print(f"  [AMBUAMB levels: {cols_avail}]")
        break
    for cons, g in diff.groupby(level="CONSTRUCTION"):
        g = g.dropna()
        t = stats.ttest_1samp(g, 0)
        print(f"  {meas:<6} {cons:<8} diff {g.mean():+8.3f}  "
              f"{(g > 0).sum()}/{len(g)} items positive  p {t.pvalue:.3f}")

print("\nB3. ITEM-LEVEL PREDICTION OF THE RT EFFECT")
rtc = (D[D.WordPosition == D.CriticalPosition]
       .groupby(["item", "CONSTRUCTION", "AMBUAMB"]).log_RT.mean()
       .unstack("AMBUAMB"))
rt_diff = (rtc["AMB"] - rtc["UAMB"]).rename("rt_diff")
for meas in ["curv3", "tee", "surp"]:
    md = (amb[(meas, "AMB")] - amb[(meas, "UAMB")]).rename("m_diff")
    J = pd.concat([rt_diff, md], axis=1).dropna().reset_index()
    cons_d = pd.get_dummies(J.CONSTRUCTION, drop_first=True).astype(float)
    X = np.column_stack([np.ones(len(J)), zsn(J.m_diff.values),
                         cons_d.values])
    fit = sm.OLS(zsn(J.rt_diff.values), X).fit()
    print(f"  {meas:<6} beta {fit.params[1]:+.4f}  p {fit.pvalues[1]:.3f}  "
          f"(n items {len(J)})")
