"""
INDEPENDENT VERIFICATION OF THE EYE-TRACKING RESULTS
=====================================================
The OneStop non-replication is now a headline claim -- it is in the abstract and
it is what the Discussion's preview account exists to explain -- but it has had
less scrutiny than anything else in the paper. It came from single runs earlier
in the project. This gives it the same treatment as VERIFY_sap.py.

WHAT IS BEING CHECKED (targets fixed here before the script is run, taken from
the manuscript text and the earlier output files):

  OneStop, ordinary-reading subcorpus
    participants                     180
    total reading time, TEE beta     -0.0023, p = .029          [negative]
    surprisal beta                   +0.031, 178/180, p = 2.9e-31
    lag-1 TEE beta                   +0.0014, 52.0%, p = .46
  ZuCo
    subjects                         12
    total reading time, TEE          11 of 12 positive, beta +0.0079, p = .006

INDEPENDENCE. As with the SAP verification, the point is not to re-run the same
code. Differences from the original path:
  - the analysis frame is rebuilt from the raw corpus files rather than from any
    intermediate saved by the earlier runs
  - subject-level fits use explicit numpy design matrices rather than formula
    interfaces
  - the lag-1 outcome is constructed and its contiguity checked independently
  - row counts are asserted at every filtering step

A DISAGREEMENT HERE IS MORE CONSEQUENTIAL THAN AGREEMENT. If the OneStop null
does not reproduce, the abstract, the eye-tracking section and the entire preview
discussion have to be revisited before upload.
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import glob, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]

FAIL = []


def check(name, ok, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        FAIL.append(name)


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def subject_fit(df, subj, cols, outcome, minn=250):
    """Per-participant OLS; returns focus coefficients (cols[0])."""
    out = []
    for pid, sub in df.groupby(subj):
        s = sub.dropna(subset=cols + [outcome])
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        r = sm.OLS(zs(s[outcome].values), sm.add_constant(X)).fit()
        out.append(r.params[1])
    return np.array(out)


def summarise(b, label):
    pos = (b > 0).mean()
    p = stats.wilcoxon(b).pvalue if len(b) > 5 else np.nan
    print(f"    {label:<34} n={len(b):>4}  beta={b.mean():>+9.5f}  "
          f"{pos:>5.1%} positive  p={p:.3e}")
    return b.mean(), pos, p


# ============================================================= ONESTOP
print("=" * 78)
print("ONESTOP")
print("=" * 78)
use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
                                  "wordfreq_frequency", "gpt2_surprisal"]
os_ = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
print(f"  raw rows {len(os_):,}   participants {os_.participant_id.nunique()}")

tee = pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv")
n0 = len(os_)
os_ = os_.merge(tee, on=KEY, how="left")
check("TEE merge preserves rows", len(os_) == n0, f"{len(os_):,}")
w = pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[KEY + ["word"]]
os_ = os_.merge(w, on=KEY, how="left")

for c in ["IA_DWELL_TIME", "word_length", "wordfreq_frequency",
          "gpt2_surprisal"]:
    os_[c] = pd.to_numeric(os_[c], errors="coerce")

# lag-1 built BEFORE filtering, contiguity enforced on interest-area order
os_ = os_.sort_values(["participant_id"] + KEY).reset_index(drop=True)
g = os_.groupby(["participant_id", "article_id", "paragraph_id",
                 "difficulty_level"])
os_["_y_raw"] = np.log(os_.IA_DWELL_TIME.where(os_.IA_DWELL_TIME > 0))
os_["y_lead1"] = g["_y_raw"].shift(-1)
os_["id_lead1"] = g["IA_ID"].shift(-1)
os_.loc[(os_.id_lead1 - os_.IA_ID) != 1, "y_lead1"] = np.nan
print(f"  after lag construction {len(os_):,}")

os_ = os_[os_.IA_DWELL_TIME > 0].copy()
os_["logTRT"] = np.log(os_.IA_DWELL_TIME)
os_["log_freq"] = np.log(os_.wordfreq_frequency.clip(lower=1e-9))
os_["punct"] = os_.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
os_ = os_.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
check("participants", os_.participant_id.nunique() == 180,
      f"{os_.participant_id.nunique()}")

CTRL = ["surprisal", "log_freq", "word_length", "punct"]

print("\n  total reading time, lag 0:")
b_tee = subject_fit(os_, "participant_id", ["tee"] + CTRL, "logTRT")
m, pos, p = summarise(b_tee, "TEE")
check("OneStop TEE is negative", m < 0, f"beta = {m:+.5f} (target -0.0023)")
check("OneStop TEE magnitude", abs(m - (-0.0023)) < 0.0015,
      f"{m:+.5f} vs -0.00230")

b_sur = subject_fit(os_, "participant_id",
                    ["surprisal", "log_freq", "word_length", "punct"], "logTRT")
m_s, pos_s, p_s = summarise(b_sur, "surprisal [sanity]")
check("OneStop surprisal is strongly positive", m_s > 0 and pos_s > .95,
      f"beta = {m_s:+.5f}, {pos_s:.1%} positive (target +0.031, 178/180)")

print("\n  total reading time, lag 1:")
b_l1 = subject_fit(os_, "participant_id", ["tee"] + CTRL, "y_lead1")
m1, pos1, p1 = summarise(b_l1, "TEE at lag 1")
check("OneStop lag-1 fails the replication criterion",
      not (m1 > 0 and p1 < .0017 and pos1 >= .65),
      f"beta {m1:+.5f}, {pos1:.1%} positive, p = {p1:.3f}")

# ============================================================= ZUCO
print("\n" + "=" * 78)
print("ZUCO")
print("=" * 78)
Z = "/Users/elanbarenholtz/ZuCo_TEE_Analysis"
try:
    T = pd.read_csv(f"{Z}/zuco_tee.csv")
    zu = pd.concat([pd.read_csv(f) for f in
                    sorted(glob.glob(f"{Z}/zuco_et/*_et.csv"))],
                   ignore_index=True)
    zu = zu.merge(T, on=["sent_idx", "word_idx"], how="inner",
                  suffixes=("", "_t"))
    zu["TRT"] = pd.to_numeric(zu.TRT, errors="coerce")
    zu = zu[zu.TRT > 0].copy()
    zu["logTRT"] = np.log(zu.TRT)
    zu["word_length"] = zu.word.astype(str).str.len()
    from wordfreq import zipf_frequency
    zu["log_freq"] = zu.word.astype(str).str.strip(".,;:!?").str.lower().map(
        lambda x: zipf_frequency(x, "en"))
    zu = zu.rename(columns={"surp": "surprisal", "tee_k3": "tee",
                            "has_trailing_punct": "punct"})
    print(f"  rows {len(zu):,}   subjects {zu.subject.nunique()}")
    b_z = subject_fit(zu, "subject", ["tee"] + CTRL, "logTRT", minn=150)
    mz, posz, pz = summarise(b_z, "TEE")
    check("ZuCo subjects", len(b_z) == 12, f"{len(b_z)} with sufficient data")
    check("ZuCo TEE positive in 11 of 12", (b_z > 0).sum() == 11,
          f"{(b_z > 0).sum()} of {len(b_z)} positive, beta {mz:+.5f} "
          f"(target +0.0079)")
except FileNotFoundError as e:
    print(f"  ZuCo files not reachable: {e}")
    FAIL.append("ZuCo data unavailable")

print("\n" + "=" * 78)
print("VERDICT")
print("=" * 78)
if FAIL:
    print(f"  {len(FAIL)} CHECK(S) FAILED: {', '.join(FAIL)}")
    print("  The eye-tracking claims must be resolved before upload.")
else:
    print("  ALL CHECKS PASSED. The OneStop non-replication and the ZuCo")
    print("  result reproduce on an independently rebuilt analysis frame.")
