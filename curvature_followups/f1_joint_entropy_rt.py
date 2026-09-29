"""
F1 -- Joint regression: does curvature_3 survive entropy as a competing
predictor of Natural Stories self-paced reading time?

Spec fixed before results were seen (2026-09-28):
  RT ~ curvature_3 + surprisal + entropy + log_freq + word_length
       + within-sentence position + C(story_id)
  OLS, standard errors clustered by participant.
  Comparison: same model minus curvature_3. Report dAIC and curvature beta.

Primary DV: log RT (the repo's headline convention). Raw RT reported too.
All continuous predictors z-scored at the word-token level of the RT frame.

Data: locked sample 8a6087341e (9,840 words) with curvature_3 from
tee_vs_curvature/curvature_merged_8a6087341e.csv; RT trimmed 100-3000 ms.
log_freq is the repaired zipf frequency (log_freq_fixed), as in E7/E8.

Robustness rows (secondary, labelled as such):
  R1  + prev_log_RT (the E8 headline carries this)
  R2  + next-word entropy (entropy of the distribution over word w+1,
      i.e. the forward-looking uncertainty at word w)
  R3  entropy -> the four E7 distribution functionals
  R4  spillover: surprisal/entropy/curvature of word w-1 added
"""
import os, hashlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency

GP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(GP, "curvature_followups")

S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()
     ).hexdigest()[:10]
assert sh == "8a6087341e", sh
F = pd.read_csv(f"{GP}/gp_confound_check/e7_functionals_8a6087341e.csv")
S = S.merge(F, on=["story_id", "word_idx"], how="left", validate="one_to_one")
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
S = S.sort_values(["story_id", "word_idx"])
g = S.groupby("story_id")
# forward-looking entropy: the distribution the model holds AT word w over
# word w+1 is the pre-word entropy of word w+1 (contiguous word_idx only)
nxt_contig = g.word_idx.shift(-1) == S.word_idx + 1
S["entropy_next"] = g.entropy.shift(-1).where(nxt_contig)
prv_contig = g.word_idx.shift(1) == S.word_idx - 1
for c in ["surprisal", "entropy", "curvature_3"]:
    S[c + "_prev"] = g[c].shift(1).where(prv_contig)

print(f"locked sample {sh}: {len(S):,} words")
print("word-level correlations:")
print(S[["curvature_3", "surprisal", "entropy", "entropy_next",
         "log_freq_fixed", "word_length", "from_start"]].corr()
      .round(3).to_string())

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
keep = ["story_id", "zone", "curvature_3", "surprisal", "entropy",
        "entropy_next", "log_freq_fixed", "word_length", "from_start",
        "f_entropy", "f_renyi2", "f_top1", "f_top10",
        "surprisal_prev", "entropy_prev", "curvature_3_prev"]
d = rt.merge(S[keep], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"]).log_RT.shift(1)

PRIMARY = ["curvature_3", "surprisal", "entropy", "log_freq_fixed",
           "word_length", "from_start"]
D = d.dropna(subset=["log_RT"] + PRIMARY).copy()
ZC = PRIMARY + ["prev_log_RT", "entropy_next", "f_entropy", "f_renyi2",
                "f_top1", "f_top10", "surprisal_prev", "entropy_prev",
                "curvature_3_prev"]
for c in ZC:
    v = D[c].dropna(); D["z_" + c] = (D[c] - v.mean()) / v.std()
D["pid"] = D.participant.astype("category").cat.codes
print(f"\nRT rows: {len(D):,}   participants {D.participant.nunique()}   "
      f"words {D.groupby(['story_id','zone']).ngroups:,}")

CTRL = ("z_surprisal + z_entropy + z_log_freq_fixed + z_word_length"
        " + z_from_start + C(story_id)")
rows = []


def fit(dv, rhs, frame):
    return smf.ols(f"{dv} ~ {rhs}", frame).fit(
        cov_type="cluster", cov_kwds={"groups": frame.pid.values})


def compare(label, dv, ctrl, frame, term="z_curvature_3"):
    frame = frame.dropna(subset=[dv] + [t for t in
                         ctrl.replace("C(story_id)", "").replace("+", " ")
                         .split() if t.startswith("z_")] + [term])
    m0 = fit(dv, ctrl, frame)
    m1 = fit(dv, ctrl + f" + {term}", frame)
    b, se, p = m1.params[term], m1.bse[term], m1.pvalues[term]
    r = dict(spec=label, dv=dv, n=int(m1.nobs), dAIC=m0.aic - m1.aic,
             beta=b, se=se, t=b / se, p=p,
             beta_entropy=m1.params.get("z_entropy", np.nan),
             p_entropy=m1.pvalues.get("z_entropy", np.nan),
             beta_surprisal=m1.params.get("z_surprisal", np.nan),
             beta_entropy_without_curv=m0.params.get("z_entropy", np.nan))
    rows.append(r)
    print(f"  {label:<44} n {r['n']:>7,}  dAIC {r['dAIC']:>8.1f}  "
          f"beta {b:+.5f} (SE {se:.5f}, t {b/se:5.1f}, p {p:.1e})  "
          f"entropy {r['beta_entropy_without_curv']:+.5f} -> "
          f"{r['beta_entropy']:+.5f}")
    return m1


print("\n" + "=" * 100)
print("PRIMARY: OLS, story FE, participant-clustered SEs; dAIC = AIC(no curv) - AIC(with curv)")
print("=" * 100)
m_log = compare("PRIMARY  log RT", "log_RT", CTRL, D)
m_raw = compare("PRIMARY  raw RT (ms)", "RT", CTRL, D)
print("\nFull primary model (log RT):")
print(m_log.summary().tables[1].as_text())

print("\n" + "=" * 100)
print("ROBUSTNESS (secondary)")
print("=" * 100)
compare("R1  + prev_log_RT", "log_RT", CTRL + " + z_prev_log_RT", D)
compare("R2  + next-word entropy", "log_RT", CTRL + " + z_entropy_next", D)
compare("R3  entropy -> 4 E7 functionals", "log_RT",
        CTRL.replace("z_entropy", "z_f_entropy + z_f_renyi2 + z_f_top1"
                     " + z_f_top10"), D)
compare("R4  + spillover (w-1 surp, ent, curv)", "log_RT",
        CTRL + " + z_surprisal_prev + z_entropy_prev + z_curvature_3_prev", D)
compare("R5  all of R1+R2+R4", "log_RT",
        CTRL + " + z_prev_log_RT + z_entropy_next + z_surprisal_prev"
        " + z_entropy_prev + z_curvature_3_prev", D)

# entropy mediation check: does adding entropy change curvature's beta?
print("\n" + "=" * 100)
print("MEDIATION CHECK: curvature beta with vs without entropy in the model")
print("=" * 100)
noent = CTRL.replace(" + z_entropy", "")
m_ne = fit("log_RT", noent + " + z_curvature_3", D)
b_ne, b_e = m_ne.params["z_curvature_3"], m_log.params["z_curvature_3"]
print(f"  curvature beta, no entropy:   {b_ne:+.5f}")
print(f"  curvature beta, with entropy: {b_e:+.5f}   "
      f"change {100*(b_e-b_ne)/b_ne:+.1f}%")
rows.append(dict(spec="MEDIATION curvature beta without entropy",
                 dv="log_RT", n=int(m_ne.nobs), beta=b_ne))

pd.DataFrame(rows).to_csv(f"{OUT}/f1_results.csv", index=False)
print(f"\nwrote {OUT}/f1_results.csv")

# ---- R4 detail: where does the curvature effect sit, w or w-1? ----
print("\n" + "=" * 100)
print("R4 DETAIL: curvature at w and w-1 jointly")
print("=" * 100)
Dd = D.dropna(subset=["z_curvature_3_prev", "z_surprisal_prev",
                      "z_entropy_prev"])
print(f"  word-level r(curv3_w, curv3_w-1) = "
      f"{S.curvature_3.corr(S.curvature_3_prev):+.3f}")
for lab, rhs in [("curv_prev only (no w-1 surp/ent)",
                  CTRL + " + z_curvature_3_prev"),
                 ("curv_w + curv_prev + w-1 surp/ent",
                  CTRL + " + z_surprisal_prev + z_entropy_prev"
                  " + z_curvature_3_prev + z_curvature_3")]:
    m = fit("log_RT", rhs, Dd)
    print(f"  {lab:<36} curv_w {m.params.get('z_curvature_3', np.nan):+.5f}"
          f"  curv_w-1 {m.params['z_curvature_3_prev']:+.5f} "
          f"(t {m.tvalues['z_curvature_3_prev']:.1f})  AIC {m.aic:.1f}")
m_both0 = fit("log_RT", CTRL + " + z_surprisal_prev + z_entropy_prev", Dd)
m_both1 = fit("log_RT", CTRL + " + z_surprisal_prev + z_entropy_prev"
              " + z_curvature_3 + z_curvature_3_prev", Dd)
print(f"  dAIC for curvature (w and w-1 together) beyond surp/ent at w and w-1:"
      f" {m_both0.aic - m_both1.aic:.1f}")
