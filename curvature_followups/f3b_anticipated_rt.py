"""
F3b -- does anticipated curvature predict Natural Stories reading time beyond
the F1 model AND beyond the entropy of the very same distribution?

Spec fixed before results were seen (2026-09-29):
  Frame, trimming, controls: identical to F1 primary. SEs clustered two-way
  (participant x word), NOT participant-only: see F1b.
  Base  = F1 primary (curvature_3, surprisal, entropy, log_freq, word_length,
          from_start, C(story_id)) + ent_full
          (ent_full = entropy of the next-token distribution at the final
          subword of w: the distribution the anticipated quantities are
          computed from, so the entropy comparison is exact.)
  Test 1 (PRIMARY): + ac_var   (k = 50)         -> dAIC, beta
  Test 2:           + ac_mean + ac_var jointly  -> dAIC
  Test 3:           + ac_disp  (direction-sensitive dispersion)
  DV: log RT at word w (the state is held while reading w).
  Secondary DV: log RT at w+1 with w+1's own F1 predictors, since the
  forecast concerns w+1 and SPR effects spill over (see F1 R4).
  k-robustness: primary test repeated at k = 20 and k = 100.
"""
import os, hashlib
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from wordfreq import zipf_frequency

GP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(GP, "curvature_followups")
S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
A = pd.read_csv(f"{OUT}/f3_anticipated_8a6087341e.csv")
acols = [c for c in A.columns if c.startswith(("ac_", "ent_full", "mass_"))]
S = S.merge(A[["story_id", "word_idx"] + acols], on=["story_id", "word_idx"],
            how="left", validate="one_to_one")
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
rt["log_RT"] = np.log(rt.RT)
BASEV = ["curvature_3", "surprisal", "entropy", "log_freq_fixed",
         "word_length", "from_start"]
d = rt.merge(S[["story_id", "zone"] + BASEV + acols], on=["story_id", "zone"])
# DV at w+1 for the secondary analysis (contiguous zone within participant/story)
d = d.sort_values(["participant", "story_id", "zone"])
g = d.groupby(["participant", "story_id"])
nxt = g.zone.shift(-1) == d.zone + 1
d["log_RT_next"] = g.log_RT.shift(-1).where(nxt)
for c in BASEV:
    d[c + "_next"] = g[c].shift(-1).where(nxt)
d["pid"] = d.participant.astype("category").cat.codes
d["wid"] = (d.story_id * 10000 + d.zone).astype("category").cat.codes

K = [20, 50, 100]
Z = BASEV + [c + "_next" for c in BASEV] + ["ent_full"] + \
    [f"{m}_k{k}" for m in ("ac_mean", "ac_var", "ac_disp") for k in K]
D = d.dropna(subset=["log_RT"] + BASEV + ["ent_full", "ac_var_k50"]).copy()
for c in Z:
    v = D[c].dropna(); D["z_" + c] = (D[c] - v.mean()) / v.std()
print(f"RT rows {len(D):,}  participants {D.participant.nunique()}")
print("\nword-level correlations (k=50):")
print(S[["ac_mean_k50", "ac_var_k50", "ac_disp_k50", "ent_full", "entropy",
         "curvature_3", "surprisal"]].corr().round(3).to_string())

FE = " + C(story_id)"
BASE = " + ".join("z_" + c for c in BASEV) + " + z_ent_full" + FE
BASE_NEXT = " + ".join("z_" + c + "_next" for c in BASEV) + \
    " + z_curvature_3 + z_surprisal + z_ent_full" + FE


def fit(dv, rhs, F):
    # two-way clustered (participant x word): participant-only clustering let
    # pure-noise word-level predictors reach |t| ~ 4-5 in a smoke test (see F1b)
    return smf.ols(f"{dv} ~ {rhs}", F).fit(cov_type="cluster", cov_kwds={
        "groups": np.column_stack([F.pid.values, F.wid.values])})


rows = []
def test(label, dv, base, terms, F):
    F = F.dropna(subset=[dv] + [t for t in (base + " + " + " + ".join(terms))
                 .replace(FE, "").replace("+", " ").split()])
    m0, m1 = fit(dv, base, F), fit(dv, base + " + " + " + ".join(terms), F)
    r = dict(spec=label, dv=dv, n=int(m1.nobs), dAIC=m0.aic - m1.aic)
    for t in terms:
        r[f"beta_{t}"], r[f"t_{t}"], r[f"p_{t}"] = m1.params[t], m1.tvalues[t], m1.pvalues[t]
    r["beta_ent_full"] = m1.params.get("z_ent_full", np.nan)
    rows.append(r)
    tstr = "  ".join(f"{t[2:]} {m1.params[t]:+.5f} (t {m1.tvalues[t]:.1f}, p {m1.pvalues[t]:.1e})"
                     for t in terms)
    print(f"  {label:<38} n {r['n']:>7,}  dAIC {r['dAIC']:>7.1f}  {tstr}")


print("\n" + "=" * 100 + "\nPRIMARY (DV log RT at w; base = F1 primary + ent_full)\n" + "=" * 100)
test("T1  + ac_var (k50)  PRIMARY", "log_RT", BASE, ["z_ac_var_k50"], D)
test("T2  + ac_mean + ac_var (k50)", "log_RT", BASE, ["z_ac_mean_k50", "z_ac_var_k50"], D)
test("T3  + ac_disp (k50)", "log_RT", BASE, ["z_ac_disp_k50"], D)
print("\nk-robustness of T1")
for k in (20, 100):
    test(f"T1  + ac_var (k{k})", "log_RT", BASE, [f"z_ac_var_k{k}"], D)
print("\n" + "=" * 100 + "\nSECONDARY (DV log RT at w+1, w+1 predictors + w curvature/surprisal/ent_full)\n" + "=" * 100)
test("S1  + ac_var (k50) -> RT w+1", "log_RT_next", BASE_NEXT, ["z_ac_var_k50"], D)
test("S2  + ac_mean + ac_var -> RT w+1", "log_RT_next", BASE_NEXT,
     ["z_ac_mean_k50", "z_ac_var_k50"], D)
test("S3  + ac_disp -> RT w+1", "log_RT_next", BASE_NEXT, ["z_ac_disp_k50"], D)
pd.DataFrame(rows).to_csv(f"{OUT}/f3b_results.csv", index=False)
print(f"\nwrote {OUT}/f3b_results.csv")
