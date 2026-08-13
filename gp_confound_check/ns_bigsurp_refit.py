"""
DOES THE NATURAL STORIES TEE EFFECT SURVIVE A STRONGER SURPRISAL CONTROL?
========================================================================
Same objection as for SAP: TEE and surprisal both come from GPT-2 Small, so the
TEE effect could be a predictability residual -- TEE marking the places where
GPT-2 Small's own probability estimate is wrong. Controlling for that model's
surprisal cannot remove such a confound, because the control is built from the
same error.

TEE is left exactly as reported (GPT-2 Small, mid layer, k = 3, locked sample
8a6087341e). Only the surprisal control changes. Stronger surprisals already
exist on this sample from the extensions pipeline, so no new forward passes are
needed:
    extensions/gpt2_medium_surp_ent.csv   surprisal_gpt2_medium
    extensions/gpt2_xl_surp_ent.csv       surprisal_gpt2_xl

Headline specification carried over unchanged from v2_table6_pythia.py:
    log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_<surprisal>
    mixedlm, by-participant random intercept, ML fit
    dAIC = improvement from adding z_tee_k3
Reference value on this spec with GPT-2 Small surprisal: dAIC = 111.8,
beta = +0.0035.

Specs:
    N0  GPT-2 Small surprisal            [reference]
    N1  GPT-2 Medium surprisal
    N2  GPT-2 XL surprisal
    N3  all three entered together       [union control]
    N4  N3 with GPT-2 XL surprisal splined df=5

Subject-level inference is run for N0 and N3 so the result is not resting on a
pooled model over 800k observations.

NOTE: Pythia-410M TEE exists on this sample but Pythia SURPRISAL does not; that
would need a fresh forward pass. GPT-2 XL (1.5B) is the strongest control
available without new compute, and is ~12x GPT-2 Small.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
print(f"sample hash {sh} verified   words {len(S):,}")

for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
                   "surprisal_gpt2_medium"),
                  (f"{GP}/extensions/gpt2_xl_surp_ent.csv",
                   "surprisal_gpt2_xl"),
                  (f"{GP}/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv",
                   "surprisal_pythia410m")]:
    E = pd.read_csv(path)[["story_id", "word_idx", col]]
    n0 = len(S)
    S = S.merge(E, on=["story_id", "word_idx"], how="left", validate="one_to_one")
    assert len(S) == n0
    print(f"  merged {col}: {S[col].notna().sum():,} non-missing")

SURPS = {"GPT-2 Small": "surprisal",
         "GPT-2 Medium": "surprisal_gpt2_medium",
         "GPT-2 XL": "surprisal_gpt2_xl",
         "Pythia-410M": "surprisal_pythia410m"}

print("\nword-level agreement between surprisal estimates:")
ks = list(SURPS.values())
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        print(f"  r({ks[i]}, {ks[j]}) = {S[ks[i]].corr(S[ks[j]]):+.3f}")
print("\nmean surprisal (bits) and correlation with TEE:")
for lab, c in SURPS.items():
    print(f"  {lab:<14} mean {S[c].mean():6.3f}   r(TEE, surp) = "
          f"{S.tee_k3.corr(S[c]):+.3f}")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
cols = ["story_id", "zone", "tee_k3", "word_length", "log_freq"] + ks
d = rt.merge(S[cols], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                     "prev_log_RT", "tee_k3"] + ks)
print(f"\nMATCHED SAMPLE (all surprisals non-missing): n = {len(d):,}   "
      f"participants = {d.participant.nunique()}")

for c in ["word_length", "log_freq", "zone", "prev_log_RT", "tee_k3"] + ks:
    d["z_" + c] = z(d[c])

BASE = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT"
SPECS = [
    ("N0  GPT-2 Small surprisal [ref]", "z_surprisal"),
    ("N1  GPT-2 Medium surprisal", "z_surprisal_gpt2_medium"),
    ("N2  GPT-2 XL surprisal", "z_surprisal_gpt2_xl"),
    ("N3  all three GPT-2 surprisals",
     "z_surprisal + z_surprisal_gpt2_medium + z_surprisal_gpt2_xl"),
    ("N4  N3, GPT-2 XL splined df=5",
     "z_surprisal + z_surprisal_gpt2_medium + bs(z_surprisal_gpt2_xl, df=5)"),
    ("N5  Pythia-410M surprisal", "z_surprisal_pythia410m"),
    ("N6  all four surprisals",
     "z_surprisal + z_surprisal_gpt2_medium + z_surprisal_gpt2_xl "
     "+ z_surprisal_pythia410m"),
    ("N7  all four, XL+Pythia splined df=4",
     "z_surprisal + z_surprisal_gpt2_medium + bs(z_surprisal_gpt2_xl, df=4) "
     "+ bs(z_surprisal_pythia410m, df=4)"),
]

print("\n" + "=" * 82)
print("POOLED: dAIC and beta for TEE under each surprisal control")
print("=" * 82)
print(f"{'spec':<34}{'dAIC(TEE)':>12}{'beta':>11}{'p':>13}")
for lab, term in SPECS:
    m0 = smf.mixedlm(f"{BASE} + {term}", d, groups=d.participant).fit(
        reml=False, method="lbfgs")
    m1 = smf.mixedlm(f"{BASE} + {term} + z_tee_k3", d,
                     groups=d.participant).fit(reml=False, method="lbfgs")
    print(f"{lab:<34}{m0.aic - m1.aic:>12.1f}{m1.params['z_tee_k3']:>11.5f}"
          f"{m1.pvalues['z_tee_k3']:>13.2e}")

print("\n" + "=" * 82)
print("SUBJECT-LEVEL: per-participant TEE coefficient")
print("=" * 82)
print(f"{'spec':<34}{'n':>6}{'mean beta':>12}{'% pos':>8}{'Wilcoxon p':>13}")


def subject_level(surp_cols, permute=False, rng=None):
    cols = ["tee_k3", "word_length", "log_freq", "zone",
            "prev_log_RT"] + surp_cols
    out = []
    for pid, sub in d.groupby("participant"):
        s = sub.dropna(subset=cols + ["log_RT"])
        if len(s) < 300:
            continue
        if permute:
            s = s.assign(tee_k3=rng.permutation(s.tee_k3.values))
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
        out.append(r.params[1])
    return np.array(out)


for lab, sc in [("N0  GPT-2 Small surprisal [ref]", ["surprisal"]),
                ("N2  GPT-2 XL surprisal", ["surprisal_gpt2_xl"]),
                ("N5  Pythia-410M surprisal", ["surprisal_pythia410m"]),
                ("N6  all four surprisals", ks)]:
    b = subject_level(sc)
    print(f"{lab:<34}{len(b):>6}{b.mean():>+12.5f}{(b > 0).mean():>8.1%}"
          f"{stats.wilcoxon(b).pvalue:>13.2e}")

rng = np.random.default_rng(20260807)
b = subject_level(ks, permute=True, rng=rng)
print(f"{'F   permuted TEE (floor)':<34}{len(b):>6}{b.mean():>+12.5f}"
      f"{(b > 0).mean():>8.1%}{stats.wilcoxon(b).pvalue:>13.2e}")
