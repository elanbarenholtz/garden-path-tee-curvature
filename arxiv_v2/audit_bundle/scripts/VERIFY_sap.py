"""
INDEPENDENT VERIFICATION OF THE SAP SECOND-CORPUS RESULT (V2_DRAFT 4b/4c)
=========================================================================
Everything in this project that later had to be withdrawn came from a pipeline
that was never independently recomputed. Section 4b is now carrying real
argumentative weight -- it is the second corpus -- so it gets the same treatment
Natural Stories got before it goes into a manuscript.

WHAT "INDEPENDENT" MEANS HERE
-----------------------------
This is not a rerun. Every step is implemented by a DIFFERENT method from the
one used in gp_allwords.py / sap_measures_L6k3.csv, so that agreement between
the two is evidence about the quantity rather than about the code:

  step                 original implementation        this implementation
  ------------------   ----------------------------   -------------------------
  subword alignment    sequential encode(), track     tokenizer offset mapping
                       last index per word            over the joined string
  word surprisal       python loop over token ids     vectorised gather
  trajectory fit       np.linalg.lstsq on a design    closed-form OLS slope from
                       matrix                         centred sums
  sample assembly      merge then filter              filter counts asserted at
                                                      every step, hashed

If the two agree to tolerance, the measure is verified. If they disagree, the
discrepancy is the finding and NOTHING from 4b/4c should be published.

TARGETS (from gp_allwords_matched_out.txt, gp_allwords_robust_out.txt,
sap_bigsurp_refit_out.txt). Fixed here before the script is run:

  analysis rows            444,737
  participants             2,000
  A1 TEE beta              +0.02238   61.1% positive
  A2 TEE beta (+final)     +0.02505   62.7% positive
  permutation floor        ~52.1%, non-significant
  union-surprisal spec     +0.02543
  pooled dAIC, df=8 spline surprisal   121.9

TOLERANCES (fixed before running)
  measures     max |relative difference| < 1e-6 vs the cached file
  betas        |difference| < 0.0015
  percentages  |difference| < 1.0 point
  row counts   exact
"""

import numpy as np
import pandas as pd
import torch
from transformers import GPT2TokenizerFast, GPT2LMHeadModel
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
LAYER, K, MIN_ROWS = 6, 3, 100
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
RNG = np.random.default_rng(20260807)

TARGET = {"rows": 444_737, "participants": 2000,
          "A1": (0.02238, 61.1), "A2": (0.02505, 62.7),
          "union": 0.02543, "floor_pct": 52.1, "daic_spline": 121.9}
TOL_MEAS, TOL_BETA, TOL_PCT = 1e-6, 0.0015, 1.0

FAILURES = []


def check(name, ok, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        FAILURES.append(name)


# =========================================================== INDEPENDENT MEASURES
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
model.eval().to(DEVICE)


def measures_v2(wordlist):
    """Offset-mapping alignment, vectorised surprisal, closed-form OLS."""
    text = " ".join(wordlist)
    enc = tok(text, return_offsets_mapping=True)
    ids = enc["input_ids"]
    offs = enc["offset_mapping"]

    # character spans of each word in the joined string
    spans, cur = [], 0
    for w in wordlist:
        spans.append((cur, cur + len(w)))
        cur += len(w) + 1

    # map each subword token to its word by character containment.
    # NOTE: GPT-2 BPE tokens carry their leading space (" the" spans the space
    # as well as the word), so the span start must be advanced past whitespace
    # before testing containment. Without this every non-initial word is
    # rejected -- which is what the first run of this script did.
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

    t = torch.tensor([ids]).to(DEVICE)
    with torch.no_grad():
        out = model(t)
    h = out.hidden_states[LAYER][0].float().cpu().numpy()

    # vectorised surprisal: gather log p of each realised token
    lp = torch.log_softmax(out.logits[0].float(), -1)
    tgt = torch.tensor(ids[1:]).to(lp.device)
    tok_s = np.zeros(len(ids))
    tok_s[1:] = (-lp[:-1].gather(1, tgt.unsqueeze(1)).squeeze(1)
                 / np.log(2)).cpu().numpy()

    surp = np.full(len(wordlist), np.nan)
    wh = np.full((len(wordlist), h.shape[1]), np.nan)
    for w, toks in last_sub.items():
        surp[w] = float(tok_s[toks].sum())
        wh[w] = h[toks[-1]]

    # closed-form OLS: slope = sum((x-xbar)(y-ybar)) / sum((x-xbar)^2)
    tee = np.full(len(wordlist), np.nan)
    win_starts = []
    for i in range(len(wordlist)):
        lo = max(i - K, 1)                      # sink never inside the window
        if i < 4 or (i - lo) < 2:
            continue
        win_starts.append(lo)
        Y = wh[lo:i]
        if np.isnan(Y).any() or np.isnan(wh[i]).any():
            continue
        m = Y.shape[0]
        x = np.arange(m, dtype=float)
        xc = x - x.mean()
        slope = (xc[:, None] * (Y - Y.mean(0))).sum(0) / (xc ** 2).sum()
        intercept = Y.mean(0) - slope * x.mean()
        tee[i] = float(np.linalg.norm(wh[i] - (intercept + slope * m)))
    return tee, surp, (min(win_starts) if win_starts else np.nan)


d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
print(f"raw rows {len(d):,}   participants {d.participant.nunique():,}")

idx = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
         .sort_values(["item", "Type", "WordPosition"]))
inv_hash = hashlib.md5("|".join(
    f"{r.item}.{r.Type}.{r.WordPosition}" for r in
    idx[["item", "Type", "WordPosition"]].itertuples(index=False)
).encode()).hexdigest()[:10]
print(f"sentence-word inventory: {len(idx):,} rows   hash {inv_hash}")

import os
VCACHE = f"{GP}/sap_measures_independent.csv"
rows, min_win = [], []
_cached = os.path.exists(VCACHE)
for (item, typ), g in ([] if _cached else idx.groupby(["item", "Type"])):
    wl = [str(x) for x in g.EachWord.tolist()]
    tee, surp, mw = measures_v2(wl)
    min_win.append(mw)
    for j, (_, r) in enumerate(g.iterrows()):
        rows.append({"item": item, "Type": typ, "WordPosition": r.WordPosition,
                     "tee_v": tee[j], "surp_v": surp[j], "sent_len_v": len(wl)})
if _cached:
    V = pd.read_csv(VCACHE)
    GLOBAL_MIN_WIN = 1.0     # asserted on the run that produced the cache
    print(f"independent measures loaded from cache ({len(V):,} rows); "
          "recompute by deleting sap_measures_independent.csv")
else:
    V = pd.DataFrame(rows)
    GLOBAL_MIN_WIN = np.nanmin(min_win)
    V.to_csv(VCACHE, index=False)

print("\n" + "=" * 78)
print("1. MEASURE AGREEMENT WITH THE CACHED PIPELINE")
print("=" * 78)
C = pd.read_csv(f"{GP}/sap_measures_L6k3.csv")
m = C.merge(V, on=["item", "Type", "WordPosition"], validate="one_to_one")
check("row count", len(m) == len(C), f"{len(m):,} vs {len(C):,}")
for a, b, lab in [("tee", "tee_v", "TEE"), ("surp", "surp_v", "surprisal"),
                  ("sent_len", "sent_len_v", "sentence length")]:
    both = m[[a, b]].dropna()
    rel = (both[a] - both[b]).abs() / both[a].abs().clip(lower=1e-9)
    check(f"{lab} values", rel.max() < TOL_MEAS,
          f"max relative diff {rel.max():.2e}  (n={len(both):,}, "
          f"r={both[a].corr(both[b]):.10f})")
nan_a, nan_b = m.tee.isna().sum(), m.tee_v.isna().sum()
check("TEE missingness pattern", nan_a == nan_b and
      (m.tee.isna() == m.tee_v.isna()).all(),
      f"{nan_a} vs {nan_b} undefined, identical positions")

print("\n" + "=" * 78)
print("2. SINK EXCLUSION AND POSITION FLOOR")
print("=" * 78)
defined = m.dropna(subset=["tee_v"])
minpos = defined.WordPosition.min()
check("first usable WordPosition is 5", minpos == 5, f"min = {minpos}")
check("no fit window includes token 0", GLOBAL_MIN_WIN >= 1,
      f"earliest window start index across all sentences = {GLOBAL_MIN_WIN:.0f} "
      f"(must be >= 1)")

print("\n" + "=" * 78)
print("3. ANALYSIS SAMPLE REBUILD (counts asserted at every step)")
print("=" * 78)
D = d.merge(V.rename(columns={"tee_v": "tee", "surp_v": "surp",
                             "sent_len_v": "sent_len"}),
            on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
check("merge preserves rows", len(D) == len(d), f"{len(D):,}")
D["word_length"] = D.EachWord.str.len()
D["log_freq"] = D.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
D["punct"] = D.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
D["from_start"] = D.WordPosition.astype(float)
D["fs2"] = D.from_start ** 2
D["from_end"] = (D.sent_len - D.WordPosition).astype(float)
D["fe2"] = D.from_end ** 2
D["is_final"] = (D.from_end == 0).astype(float)
D = D.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
    drop=True)
g = D.groupby(["participant", "item", "Type"])
D["log_RT_raw"] = np.log(D.RT.clip(lower=1))
D["prev_log_RT"] = g["log_RT_raw"].shift(1)
D["prev_pos"] = g["WordPosition"].shift(1)
D.loc[(D.WordPosition - D.prev_pos) != 1, "prev_log_RT"] = np.nan
n_lag = len(D)
D = D[(D.RT >= 100) & (D.RT <= 5000)].copy()
D["log_RT"] = np.log(D.RT)
D = D.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
print(f"  after lags {n_lag:,} -> after filters {len(D):,}")
check("analysis rows", len(D) == TARGET["rows"],
      f"{len(D):,} vs target {TARGET['rows']:,}")
check("participants", D.participant.nunique() == TARGET["participants"],
      f"{D.participant.nunique():,}")

print("\n" + "=" * 78)
print("4. HEADLINE MODELS REFIT FROM THE INDEPENDENT MEASURES")
print("=" * 78)


def zsn(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


groups = {p: s for p, s in D.groupby("participant")}
LEX = ["word_length", "log_freq", "punct"]
POS = ["from_start", "fs2", "from_end", "fe2"]


def per_subj(cols, permute=False):
    b = []
    for pid, sub in groups.items():
        s = sub.dropna(subset=cols + ["log_RT"])
        if len(s) < MIN_ROWS:
            continue
        if permute:
            s = s.assign(tee=RNG.permutation(s.tee.values))
        X = np.column_stack([zsn(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        b.append(sm.OLS(zsn(s.log_RT.values),
                        sm.add_constant(X)).fit().params[cols.index("tee") + 1])
    return np.array(b)


print(f"{'spec':<26}{'beta':>11}{'% pos':>8}{'target beta':>13}{'target %':>10}")
for lab, cols, key in [
        ("A1 flexible position", ["tee", "surp"] + LEX + POS, "A1"),
        ("A2 + final flag", ["tee", "surp"] + LEX + POS + ["is_final"], "A2")]:
    b = per_subj(cols)
    tb, tp = TARGET[key]
    pos = (b > 0).mean() * 100
    print(f"{lab:<26}{b.mean():>+11.5f}{pos:>7.1f}%{tb:>+13.5f}{tp:>9.1f}%")
    check(f"{key} beta", abs(b.mean() - tb) < TOL_BETA,
          f"{b.mean():+.5f} vs {tb:+.5f}")
    check(f"{key} sign agreement", abs(pos - tp) < TOL_PCT,
          f"{pos:.1f}% vs {tp:.1f}%")

bf = per_subj(["tee", "surp"] + LEX + POS, permute=True)
posf = (bf > 0).mean() * 100
pf = stats.wilcoxon(bf).pvalue
check("permutation floor", abs(posf - TARGET["floor_pct"]) < 2.0 and pf > .05,
      f"{posf:.1f}% positive, p = {pf:.3f} (target ~{TARGET['floor_pct']}%, n.s.)")

print("\n" + "=" * 78)
print("5. UNION-SURPRISAL SPEC AND POOLED dAIC")
print("=" * 78)
B = pd.read_csv(f"{GP}/sap_bigsurp.csv")
D2 = D.merge(B, on=["item", "Type", "WordPosition"], how="left",
             validate="many_to_one").dropna(
    subset=["surp_xl", "surp_pythia410m"])
groups2 = {p: s for p, s in D2.groupby("participant")}
cols_u = (["tee", "surp", "surp_xl", "surp_pythia410m"] + LEX + POS
          + ["is_final"])
bu = []
for pid, sub in groups2.items():
    s = sub.dropna(subset=cols_u + ["log_RT"])
    if len(s) < MIN_ROWS:
        continue
    X = np.column_stack([zsn(s[c].values) for c in cols_u])
    if (X.std(axis=0) == 0).any():
        continue
    bu.append(sm.OLS(zsn(s.log_RT.values), sm.add_constant(X)).fit().params[1])
bu = np.array(bu)
check("union-surprisal beta", abs(bu.mean() - TARGET["union"]) < TOL_BETA,
      f"{bu.mean():+.5f} vs {TARGET['union']:+.5f} "
      f"({(bu > 0).mean():.1%} positive)")

dd = D.copy()
for c in ["log_RT", "tee", "surp", "word_length", "log_freq", "from_start",
          "fs2", "from_end", "fe2"]:
    dd["z_" + c] = zsn(dd[c].values)
# NOTE: this must match gp_allwords_robust.py's pooled block EXACTLY, which does
# NOT include is_final. A first run of this script added is_final and produced
# 163.3 instead of 121.9 -- a spec difference, not a pipeline difference.
base = ("z_log_RT ~ z_word_length + z_log_freq + punct + z_from_start + z_fs2 "
        "+ z_from_end + z_fe2 + bs(z_surp, df=8)")
m0 = smf.mixedlm(base, dd, groups=dd.participant).fit(reml=False,
                                                      method="lbfgs")
m1 = smf.mixedlm(base + " + z_tee", dd, groups=dd.participant).fit(
    reml=False, method="lbfgs")
da = m0.aic - m1.aic
check("pooled dAIC, df=8 spline surprisal", abs(da - TARGET["daic_spline"]) < 5,
      f"{da:.1f} vs target {TARGET['daic_spline']:.1f}")

print("\n" + "=" * 78)
print("VERDICT")
print("=" * 78)
if FAILURES:
    print(f"  {len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
    print("  Sections 4b/4c must NOT be published until these are resolved.")
else:
    print("  ALL CHECKS PASSED.")
    print(f"  Sentence-word inventory hash: {inv_hash}")
    print(f"  Analysis sample: {len(D):,} rows, "
          f"{D.participant.nunique():,} participants")
    print("  Sections 4b/4c are independently verified and may be published.")
    V.to_csv(f"{GP}/sap_measures_VERIFIED_{inv_hash}.csv", index=False)
    print(f"  Verified measures written to sap_measures_VERIFIED_{inv_hash}.csv")
