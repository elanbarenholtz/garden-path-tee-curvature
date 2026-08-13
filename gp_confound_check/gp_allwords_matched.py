"""
MATCHED COMPARISON: TEE vs SURPRISAL UNDER IDENTICAL SPECIFICATIONS
===================================================================
gp_allwords_robust.py showed TEE's per-participant sign agreement falls from
67.2% to ~60-61% once position is controlled flexibly, failing the >=65%
criterion fixed beforehand. The open question: is 65% the wrong bar for THIS
corpus (short sentences, ~220 observations per participant, so noisy
per-participant coefficients), or is TEE simply weak here?

The bar cannot be judged in the abstract, only against a reference measure run
through exactly the same machinery. Surprisal is that reference: an effect
nobody disputes exists in self-paced reading.

Design -- symmetric by construction
-----------------------------------
For the fully linear specs, BOTH coefficients come from the SAME fit, so the
comparison is exact: identical rows, identical controls, identical participants.

  A1  flexible position                      -> beta_TEE and beta_SURP
  A2  A1 + sentence-final flag               -> beta_TEE and beta_SURP
  A3  A2 + previous log RT                   -> beta_TEE and beta_SURP

For the flexible-form specs, each measure is the linear focus while the OTHER is
splined, which is the symmetric version of the df=5 test already run:

  B1  z_tee + bs(z_surp, df=5) + flexible position   -> beta_TEE
  B2  z_surp + bs(z_tee, df=5) + flexible position   -> beta_SURP

FLOOR (C). The same A1 model with TEE permuted within participant (seed fixed),
to establish what sign agreement looks like when there is no effect at all.
Without this, 60% has no reference point. Expect ~50%.

PAIRED TEST (D). Because A1-A3 give both coefficients per participant, we can
ask directly, per participant, whether |beta_TEE| > |beta_SURP|, and run a
paired Wilcoxon. This is the sharpest form of Elan's hypothesis -- that these
syntactically odd sentences are captured better by trajectory geometry than by
probability.

Reported for every measure: mean beta, % positive, Wilcoxon p.
No criterion is re-set here. The 65% threshold from the earlier document stands;
this run only establishes what that threshold means in this corpus.
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
CACHE = f"{GP}/sap_measures_L6k3.csv"
MIN_ROWS = 100
RNG = np.random.default_rng(20260807)


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


d = pd.read_csv(RT_CSV)
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
M = pd.read_csv(CACHE)
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

POS = ["from_start", "fs2", "from_end", "fe2"]
LEX = ["word_length", "log_freq", "punct"]

SPECS = {
    "A1  flexible position":            ["tee", "surp"] + LEX + POS,
    "A2  A1 + final flag":              ["tee", "surp"] + LEX + POS + ["is_final"],
    "A3  A2 + previous log RT":         ["tee", "surp"] + LEX + POS
                                        + ["is_final", "prev_log_RT"],
}

groups = {pid: s for pid, s in d.groupby("participant")}
print(f"participants with data: {len(groups):,}")


def fit_pair(cols):
    """Return (beta_tee, beta_surp) arrays from the SAME per-participant fit."""
    bt, bs_ = [], []
    for pid, sub in groups.items():
        s = sub.dropna(subset=cols + ["log_RT"])
        if len(s) < MIN_ROWS:
            continue
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
        bt.append(r.params[cols.index("tee") + 1])
        bs_.append(r.params[cols.index("surp") + 1])
    return np.array(bt), np.array(bs_)


def line(lab, b):
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue
    flag = "PASS" if (b.mean() > 0 and p < .01 and pos >= .65) else ""
    print(f"{lab:<34}{len(b):>6}{b.mean():>+11.5f}{pos:>8.1%}{p:>11.2e}{flag:>6}")


print("=" * 78)
print("A. BOTH MEASURES FROM THE SAME FIT (identical rows and controls)")
print("=" * 78)
print(f"{'spec / measure':<34}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'':>6}")
pairs = {}
for lab, cols in SPECS.items():
    bt, bsu = fit_pair(cols)
    pairs[lab] = (bt, bsu)
    line(f"{lab}  [TEE]", bt)
    line(f"{'':<4}{'':<26}  [surprisal]", bsu)
    print()

print("=" * 78)
print("B. EACH MEASURE LINEAR WHILE THE OTHER IS SPLINED (df=5)")
print("=" * 78)
BSPECS = [
    ("B1  TEE, spline surprisal", "z_tee",
     "z_log_RT ~ z_tee + bs(z_surp, df=5) + z_word_length + z_log_freq + punct"
     " + z_from_start + z_fs2 + z_from_end + z_fe2"),
    ("B2  surprisal, spline TEE", "z_surp",
     "z_log_RT ~ z_surp + bs(z_tee, df=5) + z_word_length + z_log_freq + punct"
     " + z_from_start + z_fs2 + z_from_end + z_fe2"),
]
ZC = ["log_RT", "tee", "surp", "word_length", "log_freq", "from_start", "fs2",
      "from_end", "fe2"]
zsubs = {}
for pid, sub in groups.items():
    s = sub.dropna(subset=["log_RT", "tee", "surp", "word_length", "log_freq"])
    if len(s) < MIN_ROWS:
        continue
    s = s.copy()
    for c in ZC:
        s["z_" + c] = zs(s[c].values)
    zsubs[pid] = s

print(f"{'spec':<34}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'':>6}")
for lab, term, f in BSPECS:
    b = []
    for pid, s in zsubs.items():
        try:
            b.append(smf.ols(f, s).fit().params[term])
        except Exception:
            continue
    line(lab, np.array(b))

print("\n" + "=" * 78)
print("C. FLOOR: A1 with TEE permuted within participant")
print("=" * 78)
cols = SPECS["A1  flexible position"]
bperm = []
for pid, sub in groups.items():
    s = sub.dropna(subset=cols + ["log_RT"])
    if len(s) < MIN_ROWS:
        continue
    s = s.copy()
    s["tee"] = RNG.permutation(s.tee.values)
    X = np.column_stack([zs(s[c].values) for c in cols])
    if (X.std(axis=0) == 0).any():
        continue
    r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
    bperm.append(r.params[cols.index("tee") + 1])
print(f"{'spec':<34}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'':>6}")
line("C   permuted TEE (null floor)", np.array(bperm))

print("\n" + "=" * 78)
print("D. PAIRED, WITHIN PARTICIPANT: is |beta_TEE| > |beta_surprisal|?")
print("=" * 78)
for lab, (bt, bsu) in pairs.items():
    n = min(len(bt), len(bsu))
    at, asu = np.abs(bt[:n]), np.abs(bsu[:n])
    frac = (at > asu).mean()
    w = stats.wilcoxon(at, asu)
    print(f"  {lab:<30} |TEE|>|surp| in {frac:>5.1%} of participants   "
          f"paired p = {w.pvalue:.2e}")
    print(f"  {'':<30} mean |beta| TEE {at.mean():.5f}  "
          f"surprisal {asu.mean():.5f}")
