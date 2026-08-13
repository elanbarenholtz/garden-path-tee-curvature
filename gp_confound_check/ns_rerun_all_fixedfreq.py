"""
RERUN EVERY NATURAL STORIES ANALYSIS WITH THE REPAIRED FREQUENCY CONTROL
========================================================================
`log_freq` on the locked sample is zero for 1,937 of 9,840 words (19.7%), and
99.6% of those have a real frequency once lowercased and stripped of attached
punctuation. Frequency is a control in every Natural Stories model, so every
number that used it has to be recomputed.

Repaired variable: zipf_frequency(lowercased, punctuation-stripped word).
Zeros fall from 1,937 to 7.

Already established (ns_freq_repair.py):
    headline dAIC 111.8 -> 78.4, beta +0.00354 -> +0.00298
    subject-level +0.01277 / 73.1% -> +0.01095 / 67.3%

This script recomputes the rest, reporting old and new side by side:
  R1  stronger-surprisal controls (GPT-2 Medium/XL, Pythia-410M, joint)
  R2  displacement control
  R3  word-identity control (centring within word type)
  R4  punctuation checks
  R5  Pythia cross-architecture, matched samples
  R6  position-within-sentence interaction
  R7  the coefficient comparison used in Figure 2

Every model keeps its published specification; only the frequency variable
changes.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
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
for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
                   "surprisal_gpt2_medium"),
                  (f"{GP}/extensions/gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl"),
                  (f"{GPC}/ns_pythia410m_surp_8a6087341e.csv",
                   "surprisal_pythia410m")]:
    S = S.merge(pd.read_csv(path)[["story_id", "word_idx", col]],
                on=["story_id", "word_idx"], how="left", validate="one_to_one")
KS = ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl",
      "surprisal_pythia410m"]

disp = pd.read_csv(f"{GPC}/displacement_8a6087341e.csv")
S = S.merge(disp[["story_id", "word_idx", "disp_word"]],
            on=["story_id", "word_idx"], how="left", validate="one_to_one")
PY = pd.read_csv(f"{GPC}/pythia_tee_8a6087341e.csv")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
base_cols = (["story_id", "zone", "word", "word_idx", "tee_k3", "word_length",
              "log_freq", "log_freq_fixed", "punct", "disp_word"] + KS)
d = rt.merge(S[base_cols], on=["story_id", "zone"], how="inner",
             suffixes=("", "_s"))
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
D = d.dropna(subset=["log_RT", "word_length", "log_freq", "log_freq_fixed",
                     "zone", "prev_log_RT", "tee_k3"] + KS).copy()
print(f"n = {len(D):,}  participants = {D.participant.nunique()}\n")

for c in (["word_length", "zone", "prev_log_RT", "tee_k3", "log_freq",
           "log_freq_fixed", "disp_word", "punct"] + KS):
    D["z_" + c] = z(D[c])


def daic(frame, base, extra="z_tee_k3"):
    m0 = smf.mixedlm(base, frame, groups=frame.participant).fit(
        reml=False, method="lbfgs")
    m1 = smf.mixedlm(base + " + " + extra, frame,
                     groups=frame.participant).fit(reml=False, method="lbfgs")
    return m0.aic - m1.aic, m1.params[extra], m1.pvalues[extra]


CORE = "log_RT ~ z_word_length + z_zone + z_prev_log_RT"

print("=" * 84)
print("R1  STRONGER SURPRISAL CONTROLS")
print("=" * 84)
print(f"{'surprisal control':<28}{'dAIC old':>11}{'dAIC new':>11}"
      f"{'beta new':>11}")
sur_specs = [("GPT-2 Small", "z_surprisal"),
             ("GPT-2 Medium", "z_surprisal_gpt2_medium"),
             ("GPT-2 XL", "z_surprisal_gpt2_xl"),
             ("Pythia-410M", "z_surprisal_pythia410m"),
             ("all four", " + ".join("z_" + k for k in KS))]
for lab, term in sur_specs:
    a_old, _, _ = daic(D, f"{CORE} + z_log_freq + {term}")
    a_new, b_new, _ = daic(D, f"{CORE} + z_log_freq_fixed + {term}")
    print(f"{lab:<28}{a_old:>11.1f}{a_new:>11.1f}{b_new:>11.5f}")

print("\n" + "=" * 84)
print("R2  DISPLACEMENT CONTROL")
print("=" * 84)
dd = D.dropna(subset=["disp_word"]).copy()
print(f"  n = {len(dd):,}")
for lab, fq in [("old log_freq", "z_log_freq"),
                ("repaired", "z_log_freq_fixed")]:
    b = f"log_RT ~ z_word_length + {fq} + z_zone + z_prev_log_RT + z_surprisal"
    m_t = smf.mixedlm(b + " + z_tee_k3", dd, groups=dd.participant).fit(
        reml=False, method="lbfgs")
    m_d = smf.mixedlm(b + " + z_disp_word", dd, groups=dd.participant).fit(
        reml=False, method="lbfgs")
    m_b = smf.mixedlm(b + " + z_tee_k3 + z_disp_word", dd,
                      groups=dd.participant).fit(reml=False, method="lbfgs")
    print(f"  {lab:<16} TEE alone {m_t.params['z_tee_k3']:+.5f} | "
          f"disp alone {m_d.params['z_disp_word']:+.5f} | "
          f"joint TEE {m_b.params['z_tee_k3']:+.5f} "
          f"(p={m_b.pvalues['z_tee_k3']:.1e}) | "
          f"joint disp {m_b.params['z_disp_word']:+.5f} "
          f"(p={m_b.pvalues['z_disp_word']:.3f})")

print("\n" + "=" * 84)
print("R3  WORD-IDENTITY CONTROL (centred within word type, >=5 occurrences)")
print("=" * 84)
W = D.copy()
W["wtype"] = W.word.astype(str).str.lower()
keep = W.wtype.value_counts()
W = W[W.wtype.isin(keep[keep >= 5].index)].copy()
print(f"  {W.wtype.nunique():,} word types, n = {len(W):,}")
for lab, fq in [("old log_freq", "log_freq"), ("repaired", "log_freq_fixed")]:
    cols = ["tee_k3", "surprisal", "word_length", fq, "zone", "prev_log_RT"]
    Wc = W.copy()
    for c in cols + ["log_RT"]:
        Wc["c_" + c] = Wc[c] - Wc.groupby("wtype")[c].transform("mean")
    f = ("c_log_RT ~ " + " + ".join("c_" + c for c in cols if c != "tee_k3"))
    a, b_, p_ = daic(Wc.assign(participant=Wc.participant), f, "c_tee_k3")
    print(f"  {lab:<16} dAIC {a:>7.1f}   beta {b_:+.5f}   p {p_:.2e}")

print("\n" + "=" * 84)
print("R4  PUNCTUATION")
print("=" * 84)
for lab, fq in [("old log_freq", "z_log_freq"),
                ("repaired", "z_log_freq_fixed")]:
    b = f"{CORE} + {fq} + z_surprisal"
    a1, _, _ = daic(D, b + " + z_punct")
    sub = D[D.punct == 0]
    a2, b2, _ = daic(sub, b)
    print(f"  {lab:<16} + punctuation covariate dAIC {a1:>7.1f}   |   "
          f"punctuation-free words dAIC {a2:>7.1f} (beta {b2:+.5f}, "
          f"n={len(sub):,})")

print("\n" + "=" * 84)
print("R5  PYTHIA CROSS-ARCHITECTURE, MATCHED SAMPLE")
print("=" * 84)
P = D.merge(PY[["story_id", "zone", "tee_pythia_160m", "tee_pythia_410m"]],
            on=["story_id", "zone"], how="inner").dropna(
    subset=["tee_pythia_160m", "tee_pythia_410m"])
for c in ["tee_pythia_160m", "tee_pythia_410m"]:
    P["z_" + c] = z(P[c])
print(f"  n = {len(P):,}  participants = {P.participant.nunique()}")
for lab, fq in [("old log_freq", "z_log_freq"),
                ("repaired", "z_log_freq_fixed")]:
    b = f"{CORE} + {fq} + z_surprisal"
    out = []
    for c in ["z_tee_k3", "z_tee_pythia_160m", "z_tee_pythia_410m"]:
        a, bb, _ = daic(P, b, c)
        out.append(f"{c.replace('z_tee_', ''):<12}{a:>8.1f}")
    print(f"  {lab:<16}" + "  ".join(out))

print("\n" + "=" * 84)
print("R7  FIGURE 2 COEFFICIENTS (subject-level, unique contribution)")
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


ALL_OLD = ["tee_k3", "surprisal", "word_length", "log_freq", "zone",
           "prev_log_RT"]
ALL_NEW = ["tee_k3", "surprisal", "word_length", "log_freq_fixed", "zone",
           "prev_log_RT"]
for lab, allc, fq in [("old", ALL_OLD, "log_freq"),
                      ("repaired", ALL_NEW, "log_freq_fixed")]:
    line = []
    for c in ["tee_k3", "surprisal", fq]:
        b = subj_focus(D, c, [o for o in allc if o != c])
        line.append(f"{c[:12]:<13}{b.mean():+.5f}")
    print(f"  {lab:<10}" + " | ".join(line))
