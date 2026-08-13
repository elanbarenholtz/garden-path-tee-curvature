"""
STRESS TESTS ON THE SAP ALL-WORDS RESULT
========================================
gp_allwords.py found, across all 144 SAP sentences, all conditions, 2,000
participants:
    TEE       beta = +0.0340   67.2% positive   p = 2.7e-67
    surprisal beta = +0.0241   56.8% positive   p = 7.0e-17

Before that can be believed, the two threats that actually mattered in Natural
Stories have to be checked. Both are misspecification threats: if a control is
entered in a form too rigid to absorb its true effect, TEE can pick up the
residual and look like an independent predictor.

THREAT 1 -- position. Only word positions 5-17 are usable, sentences are 13-17
words, and these are single-sentence self-paced trials, so there is a large
sentence-final wrap-up spike. gp_allwords.py controlled position with a single
LINEAR term. Natural Stories needed from_start, from_start^2, from_end,
from_end^2 before the position structure was absorbed. If TEE covaries with
position -- and it plausibly does, since the fit window is shorter early and the
trajectory is doing different things at sentence end -- a linear control leaves
exactly the residual TEE could be absorbing.

THREAT 2 -- surprisal linearity. In Natural Stories, replacing linear surprisal
with a spline improved AIC by 346.4, i.e. the linear form was genuinely wrong.
TEE survived there, but the test has to be repeated here.

Models (per participant, group Wilcoxon across participants, same as P1):
  M0  P1 as published in gp_allwords.py                 [linear pos, linear surp]
  M1  + from_start, fs2, from_end, fe2                  [flexible position]
  M2  + is_final indicator                              [wrap-up]
  M3  M1 with bs(surprisal, df=3)                       [flexible surprisal]
  M4  M1 with bs(surprisal, df=5)
  M5  M1 with bs(surprisal, df=8)                       [most flexible]
  M6  M5 + is_final + prev_log_RT                       [everything at once]

Criterion carried over unchanged from gp_allwords.py:
    SUPPORT = mean beta > 0, Wilcoxon p < .01, >= 65% of participants same sign.

Also reported: r(TEE, position) and mean TEE by position, so the position threat
can be judged directly rather than inferred; and the AIC gain from splining
surprisal, to establish whether the linear form was actually wrong here.
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency
import os, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
CACHE = f"{GP}/sap_measures_L6k3.csv"
LAYER, K = 6, 3
MIN_ROWS = 100
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def measures(words, tokz, model):
    ids, final_idx = [], []
    for i, w in enumerate(words):
        t = tokz.encode(w if i == 0 else " " + w)
        ids.extend(t)
        final_idx.append(len(ids) - 1)
    with torch.no_grad():
        out = model(torch.tensor([ids]).to(DEVICE))
    h = out.hidden_states[LAYER][0].float().cpu().numpy()
    lp = torch.log_softmax(out.logits[0].float(), -1)
    tok_s = np.zeros(len(ids))
    for t in range(1, len(ids)):
        tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
    starts, prev = [], 0
    for fi in final_idx:
        starts.append(prev)
        prev = fi + 1
    surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
    wh = h[final_idx]
    tee = np.full(len(words), np.nan)
    for i in range(len(words)):
        lo = max(i - K, 1)
        if i < 4 or (i - lo) < 2:
            continue
        Y = wh[lo:i]
        m = Y.shape[0]
        A = np.column_stack([np.ones(m), np.arange(m)])
        c, *_ = np.linalg.lstsq(A, Y, rcond=None)
        tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
    return tee, surp


def zs(x):
    s = x.std(ddof=0)
    return (x - x.mean()) / s if s > 0 else x * 0


d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})

if os.path.exists(CACHE):
    M = pd.read_csv(CACHE)
    print(f"measures loaded from cache ({len(M):,} rows)")
else:
    tokz = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
    model.eval().to(DEVICE)
    sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
               .sort_values(["item", "Type", "WordPosition"])
               .groupby(["item", "Type"]))
    rows = []
    for (item, typ), g in sents:
        words = [str(x) for x in g.EachWord.tolist()]
        tee, surp = measures(words, tokz, model)
        n = len(words)
        for j, (_, r) in enumerate(g.iterrows()):
            rows.append({"item": item, "Type": typ,
                         "WordPosition": r.WordPosition,
                         "tee": tee[j], "surp": surp[j], "sent_len": n})
    M = pd.DataFrame(rows)
    M.to_csv(CACHE, index=False)
    print(f"measures computed and cached ({len(M):,} rows)")

n0 = len(d)
d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
assert len(d) == n0

d["word_length"] = d.EachWord.str.len()
d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
d["from_start"] = d.WordPosition.astype(float)
d["fs2"] = d.from_start ** 2
d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
d["fe2"] = d.from_end ** 2
d["is_final"] = (d.from_end == 0).astype(float)

d = d.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
    drop=True)
g = d.groupby(["participant", "item", "Type"])
d["log_RT_raw"] = np.log(d.RT.clip(lower=1))
d["prev_log_RT"] = g["log_RT_raw"].shift(1)
d["prev_pos"] = g["WordPosition"].shift(1)
d.loc[(d.WordPosition - d.prev_pos) != 1, "prev_log_RT"] = np.nan

d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
d["log_RT"] = np.log(d.RT)
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
print(f"rows {len(d):,}   participants {d.participant.nunique():,}\n")

# ---------------------------------------------------------------- the threat
print("=" * 78)
print("THREAT 1 EVIDENCE: does TEE covary with position?")
print("=" * 78)
u = d.drop_duplicates(subset=["item", "Type", "WordPosition"])
print(f"  r(TEE, from_start) = {u.tee.corr(u.from_start):+.3f}")
print(f"  r(TEE, from_end)   = {u.tee.corr(u.from_end):+.3f}")
print(f"  r(TEE, is_final)   = {u.tee.corr(u.is_final):+.3f}")
print("\n  mean TEE and mean log RT by position from sentence end:")
t = d.groupby("from_end").agg(tee=("tee", "mean"), logRT=("log_RT", "mean"),
                              n=("tee", "size"))
print(t.head(9).round(3).to_string())

# ---------------------------------------------------------------- models
SPECS = [
    ("M0  linear pos, linear surp (= P1)",
     "z_log_RT ~ z_tee + z_surp + z_word_length + z_log_freq + punct "
     "+ z_from_start"),
    ("M1  + flexible position",
     "z_log_RT ~ z_tee + z_surp + z_word_length + z_log_freq + punct "
     "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
    ("M2  M1 + sentence-final flag",
     "z_log_RT ~ z_tee + z_surp + z_word_length + z_log_freq + punct "
     "+ z_from_start + z_fs2 + z_from_end + z_fe2 + is_final"),
    ("M3  M1, spline surprisal df=3",
     "z_log_RT ~ z_tee + bs(z_surp, df=3) + z_word_length + z_log_freq + punct "
     "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
    ("M4  M1, spline surprisal df=5",
     "z_log_RT ~ z_tee + bs(z_surp, df=5) + z_word_length + z_log_freq + punct "
     "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
    ("M5  M1, spline surprisal df=8",
     "z_log_RT ~ z_tee + bs(z_surp, df=8) + z_word_length + z_log_freq + punct "
     "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
    ("M6  M5 + final flag + prev log RT",
     "z_log_RT ~ z_tee + bs(z_surp, df=8) + z_word_length + z_log_freq + punct "
     "+ z_from_start + z_fs2 + z_from_end + z_fe2 + is_final + z_prev_log_RT"),
]

ZCOLS = ["log_RT", "tee", "surp", "word_length", "log_freq", "from_start",
         "fs2", "from_end", "fe2", "prev_log_RT"]

print("\n" + "=" * 78)
print("PER-PARTICIPANT MODELS  (criterion: p<.01 AND >=65% same sign)")
print("=" * 78)
print(f"{'model':<38}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'verdict':>9}")

subs = {}
for pid, sub in d.groupby("participant"):
    s = sub.copy()
    for c in ZCOLS:
        s["z_" + c] = zs(s[c].astype(float))
    subs[pid] = s

for lab, f in SPECS:
    need = ["z_prev_log_RT"] if "prev_log_RT" in f else []
    b = []
    for pid, s in subs.items():
        ss = s.dropna(subset=["z_log_RT", "z_tee", "z_surp"] + need)
        if len(ss) < MIN_ROWS or ss.z_tee.std(ddof=0) == 0:
            continue
        try:
            r = smf.ols(f, ss).fit()
            b.append(r.params["z_tee"])
        except Exception:
            continue
    b = np.array(b)
    if len(b) < 10:
        print(f"{lab:<38}{len(b):>6}   too few")
        continue
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue
    ok = (b.mean() > 0) and (p < .01) and (pos >= .65)
    print(f"{lab:<38}{len(b):>6}{b.mean():>+11.5f}{pos:>8.1%}{p:>11.2e}"
          f"{'SUPPORT' if ok else 'null':>9}")

# ------------------------------------------------- was linear surprisal wrong?
print("\n" + "=" * 78)
print("Was the LINEAR surprisal form actually wrong here? (pooled AIC)")
print("=" * 78)
dd = d.dropna(subset=["log_RT", "tee", "surp", "word_length", "log_freq",
                      "from_start", "from_end"]).copy()
for c in ZCOLS:
    if c in dd:
        dd["z_" + c] = zs(dd[c].astype(float))
base = ("z_log_RT ~ z_word_length + z_log_freq + punct + z_from_start + z_fs2 "
        "+ z_from_end + z_fe2")
for lab, term in [("linear surprisal", "z_surp"),
                  ("spline surprisal df=5", "bs(z_surp, df=5)"),
                  ("spline surprisal df=8", "bs(z_surp, df=8)")]:
    m = smf.mixedlm(f"{base} + {term}", dd, groups=dd.participant).fit(
        reml=False, method="lbfgs")
    m2 = smf.mixedlm(f"{base} + {term} + z_tee", dd,
                     groups=dd.participant).fit(reml=False, method="lbfgs")
    print(f"  {lab:<24} AIC {m.aic:>10.1f}   +TEE {m2.aic:>10.1f}   "
          f"dAIC(TEE) {m.aic - m2.aic:>+8.1f}")
