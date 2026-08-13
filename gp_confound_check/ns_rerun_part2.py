"""
REMAINDER OF THE FREQUENCY-REPAIR RERUN (R3-R7)
===============================================
R1 (stronger surprisal controls) and R2 (displacement) completed in
ns_rerun_all_fixedfreq.py. R3 crashed for a legitimate reason and the rest did
not run.

R3 NOTE. Centring within word type zeroes any predictor that is constant within
a type -- which word length and log frequency both are. The published
word-identity analysis therefore cannot have contained a frequency term, and is
unaffected by the repair. It is refit here without those two predictors, purely
to confirm the published value reproduces.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
S["punct"] = S.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
PY = pd.read_csv(f"{GPC}/pythia_tee_8a6087341e.csv")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
# processed_RTs.tsv carries its own `word` column; renaming the sample's before
# the merge avoids the word_x/word_y suffixing that has caused errors here twice.
d = rt.merge(S[["story_id", "zone", "word", "tee_k3", "surprisal",
                "word_length", "log_freq", "log_freq_fixed", "punct"]]
             .rename(columns={"word": "wordform"}),
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
D = d.dropna(subset=["log_RT", "word_length", "log_freq", "log_freq_fixed",
                     "zone", "prev_log_RT", "tee_k3", "surprisal"]).copy()
for c in ["word_length", "zone", "prev_log_RT", "tee_k3", "log_freq",
          "log_freq_fixed", "surprisal", "punct"]:
    D["z_" + c] = z(D[c])
print(f"n = {len(D):,}  participants = {D.participant.nunique()}\n")


def daic(frame, base, extra):
    m0 = smf.mixedlm(base, frame, groups=frame.participant).fit(
        reml=False, method="lbfgs")
    m1 = smf.mixedlm(base + " + " + extra, frame,
                     groups=frame.participant).fit(reml=False, method="lbfgs")
    return m0.aic - m1.aic, m1.params[extra], m1.pvalues[extra]


CORE = "log_RT ~ z_word_length + z_zone + z_prev_log_RT"

print("=" * 84)
print("R3  WORD-IDENTITY CONTROL")
print("=" * 84)
W = D.copy()
W["wtype"] = W.wordform.astype(str).str.lower()
vc = W.wtype.value_counts()
W = W[W.wtype.isin(vc[vc >= 5].index)].copy()
cols = ["tee_k3", "surprisal", "zone", "prev_log_RT"]
for c in cols + ["log_RT"]:
    W["c_" + c] = W[c] - W.groupby("wtype")[c].transform("mean")
print(f"  {W.wtype.nunique():,} word types, n = {len(W):,}")
print("  word length and log frequency are constant within word type, so they")
print("  are necessarily absent from this model; the repair cannot affect it.")
a, b_, p_ = daic(W, "c_log_RT ~ c_surprisal + c_zone + c_prev_log_RT",
                 "c_tee_k3")
print(f"  dAIC {a:.1f}   beta {b_:+.5f}   p {p_:.2e}   "
      f"(published: dAIC 23.1, beta +0.0022, p 5.3e-7)")

print("\n" + "=" * 84)
print("R4  PUNCTUATION")
print("=" * 84)
for lab, fq in [("old log_freq", "z_log_freq"),
                ("repaired", "z_log_freq_fixed")]:
    b = f"{CORE} + {fq} + z_surprisal"
    a1, _, _ = daic(D, b + " + z_punct", "z_tee_k3")
    sub = D[D.punct == 0]
    a2, b2, _ = daic(sub, b, "z_tee_k3")
    print(f"  {lab:<16} +punct covariate dAIC {a1:>7.1f}  |  "
          f"punct-free dAIC {a2:>7.1f} (beta {b2:+.5f}, n={len(sub):,})")

print("\n" + "=" * 84)
print("R5  PYTHIA CROSS-ARCHITECTURE, MATCHED SAMPLE")
print("=" * 84)
P = D.merge(PY[["story_id", "zone", "tee_pythia_160m", "tee_pythia_410m"]],
            on=["story_id", "zone"], how="inner").dropna(
    subset=["tee_pythia_160m", "tee_pythia_410m"])
for c in ["tee_pythia_160m", "tee_pythia_410m"]:
    P["z_" + c] = z(P[c])
print(f"  n = {len(P):,}  participants = {P.participant.nunique()}")
print(f"  {'frequency':<16}{'GPT-2 Small':>14}{'Pythia-160M':>14}"
      f"{'Pythia-410M':>14}")
for lab, fq in [("old log_freq", "z_log_freq"),
                ("repaired", "z_log_freq_fixed")]:
    b = f"{CORE} + {fq} + z_surprisal"
    vals = []
    for c in ["z_tee_k3", "z_tee_pythia_160m", "z_tee_pythia_410m"]:
        a, _, _ = daic(P, b, c)
        vals.append(f"{a:>14.1f}")
    print(f"  {lab:<16}" + "".join(vals))

print("\n" + "=" * 84)
print("R7  FIGURE 2 COEFFICIENTS (subject-level unique contribution)")
print("=" * 84)


def subj_focus(frame, focus, others, minn=300):
    out = []
    for pid, s in frame.groupby("participant"):
        s = s.dropna(subset=[focus] + others + ["log_RT"])
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[focus].values)]
                            + [zs(s[c].values) for c in others])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s.log_RT.values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


for lab, fq in [("old", "log_freq"), ("repaired", "log_freq_fixed")]:
    allc = ["tee_k3", "surprisal", "word_length", fq, "zone", "prev_log_RT"]
    parts = []
    for c in ["tee_k3", "surprisal", fq]:
        b = subj_focus(D, c, [o for o in allc if o != c])
        parts.append(f"{c[:14]:<15}{b.mean():+.5f} ({(b > 0).mean():.0%})")
    print(f"  {lab:<10}" + " | ".join(parts))
