"""
P3/P4/P5: does the lag-1 TEE response replicate in eye tracking?
===============================================================
Specified in PREREG_dynamics_replication.md before the held-out data were run.

P3 OneStop: impulse response of log total reading time to TEE, lags 0-5.
   Replication iff lag 1 positive, p < .0017, >= 65% sign agreement.
P4 OneStop: late/early decay ratio, TEE vs surprisal, paired.
P5 ZuCo:    same as P3, 12 participants, direction only.

Natural Stories reference (already fixed):
   lag 0 +0.0160 (74.9%)   lag 1 +0.0205 (81.9%)   lag 2 +0.0085
   lag 3 +0.0041            lag 4 +0.0028           lag 5 -0.0005
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import glob, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
LAGS = list(range(6))
ALPHA = .01 / 6


def zs(x):
    s = x.std(ddof=0)
    return (x - x.mean()) / s if s > 0 else x * 0


def irf(d, subj, trial, order, focus, ctrl, dv, minn=250):
    """Per-participant impulse response of log(dv) to focus at lags 0..5."""
    d = d.sort_values([subj] + trial + [order]).reset_index(drop=True)
    g = d.groupby([subj] + trial)
    for L in LAGS:
        d[f"y{L}"] = g["_y"].shift(-L)
        d[f"o{L}"] = g[order].shift(-L)
        bad = (d[f"o{L}"] - d[order]) != L
        d.loc[bad, f"y{L}"] = np.nan
    cols = [focus] + ctrl
    out = {L: [] for L in LAGS}
    per_subj = {}
    for pid, sub in d.groupby(subj):
        b, ok = [], True
        for L in LAGS:
            s = sub.dropna(subset=cols + [f"y{L}"])
            if len(s) < minn:
                ok = False
                break
            X = s[cols].astype(float).apply(zs)
            if (X.std(ddof=0) == 0).any():
                ok = False
                break
            r = sm.OLS(zs(s[f"y{L}"]).values, sm.add_constant(X.values)).fit()
            b.append(r.params[1])
        if ok:
            per_subj[pid] = np.array(b)
            for L in LAGS:
                out[L].append(b[L])
    return {L: np.array(v) for L, v in out.items()}, per_subj


def report(res, title, ns_ref=None):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    hdr = f"{'lag':>4}{'n':>6}{'mean beta':>12}{'% same sign':>13}{'Wilcoxon p':>13}"
    if ns_ref is not None:
        hdr += f"{'NS ref':>10}"
    print(hdr)
    for L in LAGS:
        b = res[L]
        if len(b) < 5:
            print(f"{L:>4}{len(b):>6}   too few")
            continue
        pos = (b > 0).mean()
        agree = max(pos, 1 - pos)
        p = stats.wilcoxon(b).pvalue if len(b) > 5 else np.nan
        line = f"{L:>4}{len(b):>6}{b.mean():>+12.5f}{agree:>12.1%}{p:>13.2e}"
        if ns_ref is not None:
            line += f"{ns_ref[L]:>+10.4f}"
        print(line)


NS_REF = {0: .0160, 1: .0205, 2: .0085, 3: .0041, 4: .0028, 5: -.0005}

# ---------------------------------------------------------------- OneStop
print("Loading OneStop ...")
use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
                                  "wordfreq_frequency", "gpt2_surprisal"]
os_ = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
os_ = os_.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
                on=KEY, how="left")
tw = pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[KEY + ["word"]]
os_ = os_.merge(tw, on=KEY, how="left")
for c in ["IA_DWELL_TIME", "word_length", "wordfreq_frequency", "gpt2_surprisal"]:
    os_[c] = pd.to_numeric(os_[c], errors="coerce")
os_ = os_[os_.IA_DWELL_TIME > 0].copy()
os_["_y"] = np.log(os_.IA_DWELL_TIME)
os_["log_freq"] = np.log(os_.wordfreq_frequency.clip(lower=1e-9))
os_["punct"] = os_.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
os_ = os_.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
print(f"  rows {len(os_):,}  participants {os_.participant_id.nunique()}")

CTRL_OS = ["surprisal", "log_freq", "word_length", "punct"]
res_os, per_os = irf(os_, "participant_id",
                     ["article_id", "paragraph_id", "difficulty_level"],
                     "IA_ID", "tee", CTRL_OS, "IA_DWELL_TIME")
report(res_os, "P3 (PRIMARY): OneStop total reading time, TEE impulse response",
       ns_ref=NS_REF)

b1 = res_os[1]
pos1 = (b1 > 0).mean()
p1 = stats.wilcoxon(b1).pvalue
ok = (b1.mean() > 0) and (p1 < ALPHA) and (max(pos1, 1 - pos1) >= .65) and pos1 >= .65
print(f"\n  PRE-SPECIFIED REPLICATION CRITERION (lag 1): "
      f"{'MET' if ok else 'NOT MET'}")
print(f"    beta {b1.mean():+.5f}, {pos1:.1%} positive, p = {p1:.2e}, "
      f"threshold p < {ALPHA:.4f} and >= 65% positive")

# ---- P4 decay comparison in OneStop ----
res_su, per_su = irf(os_, "participant_id",
                     ["article_id", "paragraph_id", "difficulty_level"],
                     "IA_ID", "surprisal",
                     ["log_freq", "word_length", "punct"], "IA_DWELL_TIME")
shared = sorted(set(per_os) & set(per_su))
et = np.array([per_os[p][:3].sum() for p in shared])
lt = np.array([per_os[p][3:].sum() for p in shared])
es = np.array([per_su[p][:3].sum() for p in shared])
ls_ = np.array([per_su[p][3:].sum() for p in shared])
keep = (et > 0) & (es > 0)
print("\n" + "=" * 78)
print("P4: decay ratio TEE vs surprisal (OneStop)")
print("=" * 78)
print(f"  excluded by positivity guard: {(~keep).sum()}/{len(keep)} "
      f"({(~keep).mean():.1%})")
if keep.sum() > 10:
    R_t, R_s = lt[keep] / et[keep], ls_[keep] / es[keep]
    w = stats.wilcoxon(R_t, R_s)
    print(f"  median R(TEE) {np.median(R_t):+.4f}   "
          f"median R(surprisal) {np.median(R_s):+.4f}")
    print(f"  R_TEE < R_surprisal in {(R_t < R_s).mean():.1%} of participants, "
          f"p = {w.pvalue:.3e}")

# ---------------------------------------------------------------- ZuCo
print("\nLoading ZuCo ...")
Z = "/Users/elanbarenholtz/ZuCo_TEE_Analysis"
T = pd.read_csv(f"{Z}/zuco_tee.csv")
et_files = sorted(glob.glob(f"{Z}/zuco_et/*_et.csv"))
zu = pd.concat([pd.read_csv(f) for f in et_files], ignore_index=True)
zu = zu.merge(T, on=["sent_idx", "word_idx"], how="inner", suffixes=("", "_t"))
zu["TRT"] = pd.to_numeric(zu.TRT, errors="coerce")
zu = zu[zu.TRT > 0].copy()
zu["_y"] = np.log(zu.TRT)
zu["word_length"] = zu.word.astype(str).str.len()
from wordfreq import zipf_frequency
zu["log_freq"] = zu.word.astype(str).str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
zu = zu.rename(columns={"surp": "surprisal", "tee_k3": "tee",
                        "has_trailing_punct": "punct"})
print(f"  rows {len(zu):,}  subjects {zu.subject.nunique()}")
res_z, _ = irf(zu, "subject", ["sent_idx"], "word_idx", "tee",
               ["surprisal", "log_freq", "word_length", "punct"], "TRT",
               minn=150)
report(res_z, "P5 (secondary): ZuCo total reading time, 12 subjects",
       ns_ref=NS_REF)
