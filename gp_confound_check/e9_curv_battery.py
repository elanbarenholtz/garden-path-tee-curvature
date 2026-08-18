"""
E9 parts A + C -- curvature through distribution sufficiency and the syntax
B2 subset (PREREG_E9_curvature.md, committed before this run).
"""
import os, sys, hashlib
import numpy as np
import pandas as pd
from scipy import stats
from wordfreq import zipf_frequency

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
GPC = f"{GP}/gp_confound_check"

S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()
     ).hexdigest()[:10]
assert sh == "8a6087341e", sh
F = pd.read_csv(f"{GPC}/e7_functionals_8a6087341e.csv")
S = S.merge(F, on=["story_id", "word_idx"], how="left")
X = pd.read_csv(f"{GPC}/syntax_vars_8a6087341e.csv")
S = S.merge(X[["story_id", "word_idx", "close_t", "same_parent"]],
            on=["story_id", "word_idx"], how="left")
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "curvature_3", "tee_k3", "surprisal",
                "word_length", "log_freq_fixed", "f_entropy", "f_renyi2",
                "f_top1", "f_top10", "close_t", "same_parent"]],
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
BASE = ["word_length", "log_freq_fixed", "zone", "prev_log_RT", "surprisal"]
FUNCS = ["f_entropy", "f_renyi2", "f_top1", "f_top10"]
D = d.dropna(subset=["log_RT", "curvature_3"] + BASE + FUNCS).copy()
print(f"rows {len(D):,}  participants {D.participant.nunique()}")


def zs(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def subj(frame, ycol, xcol, cov, minn=100, label=""):
    bs = []
    for pid, s in frame.groupby("participant"):
        s = s.dropna(subset=[ycol, xcol] + cov)
        if len(s) < minn:
            continue
        Xm = np.column_stack([zs(s[c].values) for c in [xcol] + cov])
        if (Xm.std(axis=0) == 0).any():
            continue
        Xm = np.column_stack([np.ones(len(s)), Xm])
        b, *_ = np.linalg.lstsq(Xm, s[ycol].values, rcond=None)
        bs.append(b[1])
    bs = np.array(bs)
    pos = (bs > 0).mean()
    w = stats.wilcoxon(bs)
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"  {label:<40} n {len(bs)}  beta {bs.mean():+.5f}  "
          f"%pos {pos:.1%}  p {w.pvalue:.2e}  {'PASS' if ok else 'FAIL'}")
    return ok


print("\nA. DISTRIBUTION SUFFICIENCY (E7-analog, criterion as E7)")
subj(D, "log_RT", "curvature_3", BASE, label="curv3 | base")
subj(D, "log_RT", "curvature_3", BASE + FUNCS,
     label="curv3 | base + functionals")
for c, qc in [("surprisal", "q_s"), ("f_entropy", "q_h"),
              ("f_top1", "q_t")]:
    D[qc] = pd.qcut(D[c], 5, labels=False, duplicates="drop")
D["cell"] = (D.q_s.astype(int) * 25 + D.q_h.astype(int) * 5
             + D.q_t.astype(int))
dm = ["log_RT", "curvature_3", "word_length", "log_freq_fixed", "zone",
      "prev_log_RT"]
for c in dm:
    D["dm_" + c] = D[c] - D.groupby("cell")[c].transform("mean")
subj(D, "dm_log_RT", "dm_curvature_3", ["dm_" + c for c in dm[2:]],
     label="curv3 | distribution-matched cells")

print("\nC. SYNTAX B2 (within-constituent subset: close=0, same parent)")
B2 = D[(D.close_t == 0) & (D.same_parent == 1)].copy()
print(f"  subset rows {len(B2):,}")
subj(B2, "log_RT", "curvature_3", BASE, label="curv3 | base, B2 subset")
subj(B2, "log_RT", "tee_k3", BASE, label="TEE   | base, B2 subset (ref)")
