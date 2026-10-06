"""
F5 -- Natural Stories: which geometric property of the layer-6 trajectory does
reading time follow? Same battery as frank2015/f4_geometry.py (N400).
Spec fixed before results were seen (2026-10-06).

Measures at each word's final subword (locked sample 8a6087341e):
  step_norm    ||h[ls]-h[ls-1]||, from extensions/gpt2_states H_mid (verified to
               reproduce curvature_1 for 9840/9840 words)
  curvature_1, curvature_3, tee_k3, tee3_par, tee3_perp  (locked columns)
Frame: F1 primary (log RT; surprisal, entropy, log freq, length, position,
story FE), SEs two-way clustered (participant x word).
  A. measures at word w                  (M: each alone; J: joint)
  B. measures at word w-1 (spillover), with w-1 surprisal/entropy controls,
     since F1/F1c showed most of curvature's RT effect lands one word later.
"""
import os, numpy as np, pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.abspath(os.path.join(HERE, ".."))
S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
step = []
for sid in range(1, 11):
    d = np.load(f"{GP}/extensions/gpt2_states/story{sid}.npz"); H = d["H_mid"]
    for w, t in enumerate(d["last_sub"]):
        step.append(dict(story_id=sid, word_idx=w, step_norm=float(np.linalg.norm(H[t] - H[t - 1])) if t >= 1 else np.nan))
S = S.merge(pd.DataFrame(step), on=["story_id", "word_idx"], how="left", validate="one_to_one")
from wordfreq import zipf_frequency
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]').str.lower()
                       .map(lambda w: zipf_frequency(w, "en")))
MEAS = ["step_norm", "curvature_1", "curvature_3", "tee_k3", "tee3_par", "tee3_perp"]
S = S.sort_values(["story_id", "word_idx"])
g = S.groupby("story_id"); contig = g.word_idx.shift(1) == S.word_idx - 1
for c in MEAS + ["surprisal", "entropy"]:
    S[c + "_prev"] = g[c].shift(1).where(contig)
print("word-level correlations:")
print(S[MEAS].corr().round(2).to_string())

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv", sep="\t") \
    .rename(columns={"item": "story_id", "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)]
CTRLV = ["surprisal", "entropy", "log_freq_fixed", "word_length", "from_start"]
keep = ["story_id", "zone", "word_idx"] + CTRLV + MEAS + [c + "_prev" for c in MEAS + ["surprisal", "entropy"]]
d = rt.merge(S[keep], on=["story_id", "zone"])
d["log_RT"] = np.log(d.RT)
d["pid"] = d.participant.astype("category").cat.codes
d["wid"] = (d.story_id * 10000 + d.zone).astype("category").cat.codes
ALL = CTRLV + MEAS + [c + "_prev" for c in MEAS + ["surprisal", "entropy"]]
D = d.dropna(subset=["log_RT"] + ALL).copy()
for c in ALL:
    D["z_" + c] = (D[c] - D[c].mean()) / D[c].std()
print(f"\nRT rows {len(D):,}, words {D.wid.nunique():,}")


def fit(rhs):
    return smf.ols(f"log_RT ~ {rhs} + C(story_id)", D).fit(cov_type="cluster", cov_kwds={
        "groups": np.column_stack([D.pid.values, D.wid.values])})


res = []
for block, base, sfx in [("A. at word w", " + ".join("z_" + c for c in CTRLV), ""),
                         ("B. at word w-1 (spillover)", " + ".join("z_" + c for c in CTRLV)
                          + " + z_surprisal_prev + z_entropy_prev", "_prev")]:
    print(f"\n{'=' * 100}\n{block}\n{'=' * 100}")
    m0 = fit(base)
    specs = [(f"M {k}", [k]) for k in MEAS] + [
        ("J1 step + curv3", ["step_norm", "curvature_3"]), ("J2 step + curv1", ["step_norm", "curvature_1"]),
        ("J3 tee + curv3", ["tee_k3", "curvature_3"]), ("J4 par + perp", ["tee3_par", "tee3_perp"])]
    for lab, terms in specs:
        tt = [t + sfx for t in terms]
        q = fit(base + " + " + " + ".join("z_" + t for t in tt))
        s_ = "   ".join(f"{t} {q.params['z_' + t]:+.5f} (t {q.tvalues['z_' + t]:6.2f})" for t in tt)
        print(f"  {lab:<18} dAIC {m0.aic - q.aic:7.1f}   {s_}")
        for t in tt:
            res.append(dict(block=block, model=lab, term=t, beta=q.params["z_" + t], t=q.tvalues["z_" + t],
                            p=q.pvalues["z_" + t], dAIC=m0.aic - q.aic))
pd.DataFrame(res).to_csv(f"{HERE}/f5_results.csv", index=False)
