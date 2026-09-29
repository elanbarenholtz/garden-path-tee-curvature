"""
F1b -- is the F1 inference calibrated?

Trigger: in a smoke test of F3b, PURE NOISE word-level predictors reached
t = 3.9-4.9 (dAIC ~10) with participant-clustered SEs. Word-level predictors
are shared by every reader of that word, so clustering by participant alone
ignores item dependence and overstates precision.

Checks on the F1 PRIMARY model (log RT):
  A. two-way clustered SEs (participant x word)
  B. SEs clustered by word only
  C. permutation null: curvature_3 shuffled across words within story
     (N_PERM draws); null distribution of t (participant-clustered) and dAIC.
     Reports where the observed values fall.
  D. word-level analysis: mean log RT per word regressed on the same
     predictors (n = 9,840), HC3 SEs; no participant pseudo-replication.
"""
import os, hashlib, time
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency

N_PERM = 100
GP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
P = ["curvature_3", "surprisal", "entropy", "log_freq_fixed", "word_length", "from_start"]
d = rt.merge(S[["story_id", "zone"] + P], on=["story_id", "zone"]).dropna(subset=P)
d["log_RT"] = np.log(d.RT)
for c in P:
    d["z_" + c] = (d[c] - d[c].mean()) / d[c].std()
d["pid"] = d.participant.astype("category").cat.codes
d["wid"] = (d.story_id * 10000 + d.zone).astype("category").cat.codes
CTRL = "z_surprisal + z_entropy + z_log_freq_fixed + z_word_length + z_from_start + C(story_id)"
F = f"log_RT ~ {CTRL} + z_curvature_3"
print(f"RT rows {len(d):,}")


def show(label, m):
    print(f"  {label:<34} beta {m.params['z_curvature_3']:+.5f}  SE {m.bse['z_curvature_3']:.5f}"
          f"  t {m.tvalues['z_curvature_3']:6.2f}  p {m.pvalues['z_curvature_3']:.1e}")


t0 = time.time()
m_p = smf.ols(F, d).fit(cov_type="cluster", cov_kwds={"groups": d.pid.values})
show("participant-clustered (F1 spec)", m_p)
m_w = smf.ols(F, d).fit(cov_type="cluster", cov_kwds={"groups": d.wid.values})
show("word-clustered", m_w)
m_2 = smf.ols(F, d).fit(cov_type="cluster",
                        cov_kwds={"groups": np.column_stack([d.pid.values, d.wid.values])})
show("two-way (participant x word)", m_2)
aic0 = smf.ols(f"log_RT ~ {CTRL}", d).fit().aic
obs_daic = aic0 - m_p.aic
print(f"  observed dAIC {obs_daic:.1f}   ({time.time()-t0:.0f}s)")

# D. word-level
W = d.groupby(["story_id", "zone"]).agg(log_RT=("log_RT", "mean"),
        **{"z_" + c: ("z_" + c, "first") for c in P}).reset_index()
m_word = smf.ols(F, W).fit(cov_type="HC3")
show(f"word-level means (n={len(W):,}), HC3", m_word)
print(f"  word-level dAIC {smf.ols(f'log_RT ~ {CTRL}', W).fit().aic - m_word.aic:.1f}")

# C. permutation null (shuffle curvature across words within story)
rng = np.random.default_rng(0)
wkey = S[["story_id", "zone", "curvature_3"]].dropna().copy()
null_t, null_daic = [], []
for i in range(N_PERM):
    sh_ = wkey.copy()
    sh_["curv_perm"] = sh_.groupby("story_id").curvature_3.transform(
        lambda x: rng.permutation(x.values))
    dd = d[["story_id", "zone", "log_RT", "pid"] + ["z_" + c for c in P[1:]]].merge(
        sh_[["story_id", "zone", "curv_perm"]], on=["story_id", "zone"])
    dd["z_curvature_3"] = (dd.curv_perm - dd.curv_perm.mean()) / dd.curv_perm.std()
    m = smf.ols(F, dd).fit(cov_type="cluster", cov_kwds={"groups": dd.pid.values})
    null_t.append(m.tvalues["z_curvature_3"]); null_daic.append(aic0 - m.aic)
    if (i + 1) % 10 == 0:
        print(f"    perm {i+1}/{N_PERM}  ({time.time()-t0:.0f}s)", flush=True)
null_t, null_daic = np.array(null_t), np.array(null_daic)
print(f"\nPERMUTATION NULL (n={N_PERM}):")
print(f"  |t| participant-clustered: median {np.median(np.abs(null_t)):.2f}  95th pct "
      f"{np.percentile(np.abs(null_t), 95):.2f}  max {np.abs(null_t).max():.2f}   observed "
      f"{m_p.tvalues['z_curvature_3']:.2f}")
print(f"  dAIC: median {np.median(null_daic):.1f}  95th pct {np.percentile(null_daic, 95):.1f}"
      f"  max {null_daic.max():.1f}   observed {obs_daic:.1f}")
print(f"  fraction of null |t| > 1.96: {(np.abs(null_t) > 1.96).mean():.2f}  (calibrated = 0.05)")
pd.DataFrame(dict(null_t=null_t, null_daic=null_daic)).to_csv(
    os.path.join(GP, "curvature_followups", "f1b_perm_null.csv"), index=False)
