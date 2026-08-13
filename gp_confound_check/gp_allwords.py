"""
DOES TEE PREDICT READING TIME ACROSS THE SAP CORPUS AS A WHOLE?
==============================================================
SPEC FIXED BEFORE RUNNING. Deviations must be reported as deviations.

Motivation
----------
Every previous garden-path analysis in this project asked about the
ambiguous-minus-unambiguous CONTRAST, at selected ROIs. Those are dead:
the item-level contrast is unpredicted by TEE (and by surprisal), and for MVRR
the contrast is contaminated because the unambiguous control is itself
trajectory-disruptive (baseline TEE 101.0 vs 94.8-95.7 for the other controls).

This asks a different question, the one that works in Natural Stories:
across ALL words of ALL 144 sentences, ignoring condition entirely, does TEE
predict log RT beyond surprisal? The SAP corpus is then simply a SECOND
self-paced-reading corpus, made of syntactically unusual sentences. If TEE's
Natural Stories effect is real, it should appear here too; if these odd
constructions are where trajectory geometry matters most, it could be larger.

Status: this is a NEW question on data already inspected many times. It is
exploratory with respect to the corpus, but the spec below is fixed before
seeing any result, and it is a direct replication attempt of an effect
established elsewhere (Natural Stories, 171 participants).

Design
------
Unit: one word, one participant, one trial. Participant = MD5.
Excluded: RT outside [100, 5000]; words with undefined TEE (sentence-initial
positions, since the fit window must start at index >= 1 and needs >= 2 points).
NO ROI selection. NO condition selection. Both ambiguous and unambiguous
sentences included, all 6 Types.

PRIMARY (P1). Per participant OLS:
    z(log RT) ~ z(TEE) + z(surprisal) + z(word_length) + z(log_freq)
                + punct + z(WordPosition)
Group test: Wilcoxon signed-rank on the per-participant TEE coefficients.
  SUPPORT  : mean beta > 0, p < .01, and >= 65% of participants share the sign
  NULL     : otherwise
Participants with < 100 usable rows are dropped (fixed now).

SECONDARY
  S1. same + z(prev_log_RT)
  S2. lag 1: TEE at word t predicting log RT at word t+1, within sentence,
      contiguity enforced. Natural Stories peaked at lag 1, so this is the
      pre-specified second look, not a fishing expedition.
  S3. surprisal's own coefficient from P1, as a reference magnitude.
  S4. split by construction (MVRR / NPS / NPZ) and by ambiguity, descriptive
      only, no significance claims -- reported to show whether any effect is
      carried by one cell.
  S5. pooled mixedlm dAIC, for comparability with the published table only,
      explicitly flagged as pseudoreplicated.

IMPLEMENTATION GUARDS (this project's failure history)
  - lags computed BEFORE any filtering; row counts printed at each step
  - merges validated
  - TEE recomputed with the documented pipeline (GPT-2 small, L6, k=3,
    word state = final subword, sink never inside a fit window), NOT read from
    gp_table1_measures.csv, which holds the older sink-inclusive values
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
LAYER, K = 6, 3
MIN_ROWS = 100
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

tokz = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)


def measures(words):
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


# ------------------------------------------------------------------ load
d = pd.read_csv(RT_CSV)
print(f"raw rows                {len(d):,}")
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
print(f"participants            {d.participant.nunique():,}")
print(f"sentences               {d.Sentence.nunique()}   types {d.Type.nunique()}")

# ------------------------------------------------- model measures per sentence
sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
           .sort_values(["item", "Type", "WordPosition"])
           .groupby(["item", "Type"]))
rows = []
for (item, typ), g in sents:
    words = [str(x) for x in g.EachWord.tolist()]
    tee, surp = measures(words)
    for j, (_, r) in enumerate(g.iterrows()):
        rows.append({"item": item, "Type": typ,
                     "WordPosition": r.WordPosition,
                     "tee": tee[j], "surp": surp[j]})
M = pd.DataFrame(rows)
n_before = len(d)
d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
assert len(d) == n_before, "merge changed row count"
print(f"after measure merge     {len(d):,}")

d["word_length"] = d.EachWord.str.len()
d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)

# -------------------------------------- LAGS BEFORE ANY FILTERING
d = d.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
    drop=True)
g = d.groupby(["participant", "item", "Type"])
d["log_RT_raw"] = np.log(d.RT.clip(lower=1))
d["prev_log_RT"] = g["log_RT_raw"].shift(1)
d["y_lead1"] = g["log_RT_raw"].shift(-1)
d["pos_lead1"] = g["WordPosition"].shift(-1)
d.loc[(d.pos_lead1 - d.WordPosition) != 1, "y_lead1"] = np.nan
d["prev_pos"] = g["WordPosition"].shift(1)
d.loc[(d.WordPosition - d.prev_pos) != 1, "prev_log_RT"] = np.nan
print(f"after lag construction  {len(d):,}")

# -------------------------------------- filters
d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
print(f"after RT filter         {len(d):,}")
d["log_RT"] = np.log(d.RT)
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
print(f"after dropping undefined TEE etc  {len(d):,}")
print(f"  usable WordPositions: {sorted(d.WordPosition.unique())}")
print(f"  participants remaining: {d.participant.nunique():,}\n")

BASE = ["tee", "surp", "word_length", "log_freq", "punct", "WordPosition"]


def per_subject(df, cols, outcome, focus="tee", minr=MIN_ROWS):
    out, ref = [], []
    for pid, sub in df.groupby("participant"):
        s = sub.dropna(subset=cols + [outcome])
        if len(s) < minr:
            continue
        X = s[cols].astype(float).apply(zs)
        if (X.std(ddof=0) == 0).any():
            continue
        r = sm.OLS(zs(s[outcome]).values, sm.add_constant(X.values)).fit()
        out.append(r.params[cols.index(focus) + 1])
        ref.append(r.params[cols.index("surp") + 1])
    return np.array(out), np.array(ref)


def report(b, label):
    if len(b) < 10:
        print(f"{label}: only {len(b)} participants -- not reported")
        return
    pos = (b > 0).mean()
    agree = max(pos, 1 - pos)
    p = stats.wilcoxon(b).pvalue
    ok = (b.mean() > 0) and (p < .01) and (pos >= .65)
    print(f"{label}\n    n = {len(b)}   mean beta = {b.mean():+.5f}   "
          f"{pos:.1%} positive   Wilcoxon p = {p:.3e}   "
          f"{'SUPPORT' if ok else 'null'}")


print("=" * 78)
print("P1 (PRIMARY): TEE -> log RT, all words, all conditions")
print("=" * 78)
b_tee, b_sur = per_subject(d, BASE, "log_RT")
report(b_tee, "  TEE")
print(f"\nS3 reference -- surprisal from the same models:")
print(f"    mean beta = {b_sur.mean():+.5f}   "
      f"{(b_sur > 0).mean():.1%} positive   "
      f"Wilcoxon p = {stats.wilcoxon(b_sur).pvalue:.3e}")
print(f"    TEE / surprisal magnitude ratio = "
      f"{abs(b_tee.mean()) / abs(b_sur.mean()):.2f}")

print("\n" + "=" * 78)
print("S1: same, controlling previous log RT")
print("=" * 78)
b1, _ = per_subject(d, BASE + ["prev_log_RT"], "log_RT")
report(b1, "  TEE")

print("\n" + "=" * 78)
print("S2: lag 1 -- TEE at word t -> log RT at word t+1")
print("=" * 78)
b2, _ = per_subject(d, BASE, "y_lead1")
report(b2, "  TEE")

print("\n" + "=" * 78)
print("S4 (descriptive): breakdown -- is any effect carried by one cell?")
print("=" * 78)
print(f"{'subset':<22}{'n subj':>8}{'mean beta':>12}{'% pos':>9}{'p':>12}")
for lab, sub in ([(f"construction {c}", d[d.CONSTRUCTION == c])
                  for c in sorted(d.CONSTRUCTION.unique())]
                 + [("ambiguous", d[d.AMBUAMB == 1]),
                    ("unambiguous", d[d.AMBUAMB == 0])]):
    bb, _ = per_subject(sub, BASE, "log_RT", minr=40)
    if len(bb) < 10:
        print(f"{lab:<22}{len(bb):>8}   too few")
        continue
    print(f"{lab:<22}{len(bb):>8}{bb.mean():>+12.5f}{(bb > 0).mean():>8.1%}"
          f"{stats.wilcoxon(bb).pvalue:>12.2e}")

print("\n" + "=" * 78)
print("S5: pooled mixedlm dAIC  [PSEUDOREPLICATED -- comparability only]")
print("=" * 78)
dd = d.dropna(subset=BASE + ["log_RT"]).copy()
for c in BASE:
    dd["z_" + c] = zs(dd[c].astype(float))
f0 = ("log_RT ~ z_surp + z_word_length + z_log_freq + z_punct "
      "+ z_WordPosition")
m0 = smf.mixedlm(f0, dd, groups=dd.participant).fit(reml=False, method="lbfgs")
m1 = smf.mixedlm(f0 + " + z_tee", dd, groups=dd.participant).fit(
    reml=False, method="lbfgs")
print(f"  n = {len(dd):,}   participants = {dd.participant.nunique():,}")
print(f"  AIC without TEE {m0.aic:.1f}   with TEE {m1.aic:.1f}   "
      f"dAIC = {m0.aic - m1.aic:+.1f}")
print(f"  z_tee beta = {m1.params['z_tee']:+.5f}   p = {m1.pvalues['z_tee']:.3e}")
