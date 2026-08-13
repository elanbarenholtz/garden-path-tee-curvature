"""
DOES THE SAP TEE EFFECT SURVIVE A STRONGER SURPRISAL CONTROL?
=============================================================
TEE unchanged (GPT-2 Small, L6, k=3, sink excluded). Only the surprisal control
varies. Control models computed in sap_bigsurp.py: GPT-2 XL, Pythia-410M.

CAVEAT ESTABLISHED BEFORE THESE FITS (sap_bigsurp_out.txt): the three surprisal
estimates correlate at r = .967-.971 with each other, and each correlates with
TEE at r = .374-.386. They are near-interchangeable, so simply SUBSTITUTING one
for another is a weak test -- it cannot move much. The informative specs are
therefore the ones that enter several surprisals TOGETHER (union control) and
that spline them, since the union spans more of the predictability space than
any single estimate and leaves less room for a "predictability residual" to
hide in.

Reference (gp_allwords_matched.py, GPT-2 Small surprisal):
    A1 flexible position            TEE beta = +0.02238   61.1%
    A2 A1 + sentence-final flag     TEE beta = +0.02505   62.7%

Specs, all per participant, group Wilcoxon, identical rows within a block:
    S0  small surprisal                        [reference]
    S1  GPT-2 XL surprisal
    S2  Pythia-410M surprisal
    S3  all three, linear                      [union control]
    S4  all three, each splined df=4           [union, flexible form]
    S5  S3 + previous log RT                   [the known soft spot]

Reported for every spec: TEE beta, % positive, Wilcoxon p, and -- for context --
the coefficient on whichever surprisal is present (for S3/S4, GPT-2 XL's).

Also: a permutation floor for the S3 spec, since sign agreement has no meaning
without one.
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
MIN_ROWS = 100
RNG = np.random.default_rng(20260807)


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


d = pd.read_csv(f"{GP}/ClassicGardenPathSet.csv")
for c in ["EachWord", "Sentence"]:
    d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})

M = pd.read_csv(f"{GP}/sap_measures_L6k3.csv")
B = pd.read_csv(f"{GP}/sap_bigsurp.csv")
M = M.merge(B, on=["item", "Type", "WordPosition"], validate="one_to_one")
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
d = d.dropna(subset=["tee", "surp", "surp_xl", "surp_pythia410m",
                     "word_length", "log_freq", "log_RT"])
print(f"rows {len(d):,}   participants {d.participant.nunique():,}\n")

POSFLAG = ["from_start", "fs2", "from_end", "fe2", "is_final"]
LEX = ["word_length", "log_freq", "punct"]

LINSPECS = [
    ("S0  GPT-2 Small surprisal  [ref]", ["tee", "surp"] + LEX + POSFLAG, "surp"),
    ("S1  GPT-2 XL surprisal", ["tee", "surp_xl"] + LEX + POSFLAG, "surp_xl"),
    ("S2  Pythia-410M surprisal", ["tee", "surp_pythia410m"] + LEX + POSFLAG,
     "surp_pythia410m"),
    ("S3  all three surprisals", ["tee", "surp", "surp_xl", "surp_pythia410m"]
     + LEX + POSFLAG, "surp_xl"),
    ("S5  S3 + previous log RT", ["tee", "surp", "surp_xl", "surp_pythia410m"]
     + LEX + POSFLAG + ["prev_log_RT"], "surp_xl"),
]

groups = {pid: s for pid, s in d.groupby("participant")}


def run_linear(cols, focus="tee", ref=None, permute=False):
    bt, br = [], []
    for pid, sub in groups.items():
        s = sub.dropna(subset=cols + ["log_RT"])
        if len(s) < MIN_ROWS:
            continue
        s = s if not permute else s.assign(tee=RNG.permutation(s.tee.values))
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
        bt.append(r.params[cols.index(focus) + 1])
        if ref:
            br.append(r.params[cols.index(ref) + 1])
    return np.array(bt), np.array(br)


def line(lab, b, ref=None):
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue
    extra = f"{ref.mean():>+12.5f}" if ref is not None and len(ref) else " " * 12
    print(f"{lab:<36}{len(b):>6}{b.mean():>+11.5f}{pos:>8.1%}{p:>11.2e}{extra}")


print("=" * 88)
print("TEE COEFFICIENT UNDER INCREASINGLY STRONG SURPRISAL CONTROLS")
print("=" * 88)
print(f"{'spec':<36}{'n':>6}{'TEE beta':>11}{'% pos':>8}{'p':>11}"
      f"{'surp beta':>12}")
for lab, cols, ref in LINSPECS:
    bt, br = run_linear(cols, ref=ref)
    line(lab, bt, br)

# S4: all three splined
print("\n" + "=" * 88)
print("S4  all three surprisals splined (df=4 each)")
print("=" * 88)
ZC = ["log_RT", "tee", "surp", "surp_xl", "surp_pythia410m", "word_length",
      "log_freq", "from_start", "fs2", "from_end", "fe2"]
f4 = ("z_log_RT ~ z_tee + bs(z_surp, df=4) + bs(z_surp_xl, df=4) "
      "+ bs(z_surp_pythia410m, df=4) + z_word_length + z_log_freq + punct "
      "+ z_from_start + z_fs2 + z_from_end + z_fe2 + is_final")
b4 = []
for pid, sub in groups.items():
    s = sub.dropna(subset=[c for c in ZC])
    if len(s) < MIN_ROWS:
        continue
    s = s.copy()
    for c in ZC:
        s["z_" + c] = zs(s[c].values)
    try:
        b4.append(smf.ols(f4, s).fit().params["z_tee"])
    except Exception:
        continue
print(f"{'spec':<36}{'n':>6}{'TEE beta':>11}{'% pos':>8}{'p':>11}")
line("S4  three splined surprisals", np.array(b4))

print("\n" + "=" * 88)
print("FLOOR: S3 spec with TEE permuted within participant")
print("=" * 88)
cols3 = LINSPECS[3][1]
bperm, _ = run_linear(cols3, permute=True)
print(f"{'spec':<36}{'n':>6}{'TEE beta':>11}{'% pos':>8}{'p':>11}")
line("F   permuted TEE", bperm)

print("\n" + "=" * 88)
print("POOLED dAIC: gain from adding TEE to each surprisal specification")
print("=" * 88)
dd = d.copy()
for c in ["log_RT", "tee", "surp", "surp_xl", "surp_pythia410m", "word_length",
          "log_freq", "from_start", "fs2", "from_end", "fe2"]:
    dd["z_" + c] = zs(dd[c].values)
base = ("z_log_RT ~ z_word_length + z_log_freq + punct + z_from_start + z_fs2 "
        "+ z_from_end + z_fe2 + is_final")
for lab, term in [
        ("GPT-2 Small only", "z_surp"),
        ("GPT-2 XL only", "z_surp_xl"),
        ("Pythia-410M only", "z_surp_pythia410m"),
        ("all three", "z_surp + z_surp_xl + z_surp_pythia410m"),
        ("all three, XL splined df=5",
         "z_surp + bs(z_surp_xl, df=5) + z_surp_pythia410m")]:
    m0 = smf.mixedlm(f"{base} + {term}", dd, groups=dd.participant).fit(
        reml=False, method="lbfgs")
    m1 = smf.mixedlm(f"{base} + {term} + z_tee", dd,
                     groups=dd.participant).fit(reml=False, method="lbfgs")
    print(f"  {lab:<28} AIC {m0.aic:>10.1f}  +TEE {m1.aic:>10.1f}  "
          f"dAIC(TEE) {m0.aic - m1.aic:>+8.1f}  "
          f"beta {m1.params['z_tee']:>+8.5f}")
