"""
SYNTAX CONTROL -- analysis specified in PREREG_syntax_control.md
================================================================
Data: syntax_vars_8a6087341e.csv (extraction validated: coverage 100%,
word-form agreement 99.94% once sub-terminals are joined -- the only
mismatches are Penn bracket escapes -LRB-/-RRB-; r(close_t, closure_depth)
= 0.998). Word states from extensions/states/story*_states.npz, previously
validated against the locked sample to 1e-14.

Alignment a_t = cos(h_t - h_{t-1}, h_{t-1} - h_{t-2}), the paper's
direction-preservation quantity at the transition level, computed at layer 6
word states (last subword), windows never touching token 0 (word_idx >= 3).

PART A
  A1  mean alignment by lca_dist class (0 / 1 / 2 / 3+) vs random baseline .029
  A2  OLS: alignment ~ close_t + open_t + same_parent + C(lca_class)
      + position controls (log word_idx, from_start, from_end).
      Report R^2_syntax (vs position-only R^2) and the PRE-SPECIFIED CRITERION:
      mean raw alignment at lca_dist >= 3 must be >= 0.09 (3x baseline).
  A3  same regression with TEE as outcome; R^2 absorbed. Descriptive.

PART B
  B1  headline RT model (repaired frequency) + syntax covariates; TEE beta and
      dAIC before/after. Suggestive only (collinearity acknowledged).
  B2  DECISIVE: within-constituent subset (close_t = 0 AND same_parent = 1).
      Subject-level TEE effect must meet the standing criterion:
      Wilcoxon p < .01 AND >= 65% of participants positive.
  B3  boundary-only complement, same reporting.
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
BASELINE = 0.029


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
X = pd.read_csv(f"{GPC}/syntax_vars_8a6087341e.csv")
S = S.merge(X[["story_id", "word_idx", "open_t", "close_t", "depth_t",
               "same_parent", "lca_dist"]],
            on=["story_id", "word_idx"], how="left", validate="one_to_one")
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))

# ---------------- alignment from stored states ----------------
align = np.full(len(S), np.nan)
Sg = S.reset_index()          # keep row order for writing back
for sid, sub in Sg.groupby("story_id"):
    zf = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
    H, ls = zf["H"].astype(np.float64), zf["last_sub"]
    for r in sub.itertuples():
        w = r.word_idx
        if w < 3:
            continue          # windows must not touch token 0
        h2, h1, h0 = H[ls[w - 2]], H[ls[w - 1]], H[ls[w]]
        s1, s0 = h1 - h2, h0 - h1
        n1, n0 = np.linalg.norm(s1), np.linalg.norm(s0)
        if n1 > 1e-9 and n0 > 1e-9:
            align[r.index] = float(np.dot(s1, s0) / (n1 * n0))
S["algn"] = align
A = S.dropna(subset=["algn", "lca_dist", "close_t", "open_t",
                     "same_parent"]).copy()
A["lca_class"] = np.minimum(A.lca_dist, 3).astype(int)
A["log_pos"] = np.log(A.word_idx + 1)
print(f"locked sample {sh}: {len(A):,} transitions with alignment + syntax")

print("\n" + "=" * 76)
print("A1  MEAN ALIGNMENT BY TRANSITION CLASS   (random baseline 0.029)")
print("=" * 76)
print(f"{'lca_dist':>9}{'n':>8}{'mean align':>13}{'x baseline':>12}")
for c, g in A.groupby("lca_class"):
    lab = f"{c}" if c < 3 else "3+"
    print(f"{lab:>9}{len(g):>8}{g.algn.mean():>13.4f}"
          f"{g.algn.mean()/BASELINE:>11.1f}x")

print("\n" + "=" * 76)
print("A2  HOW MUCH ALIGNMENT VARIANCE DOES SYNTAX ABSORB?")
print("=" * 76)
m_pos = smf.ols("algn ~ log_pos + from_start + from_end", A).fit()
m_syn = smf.ols("algn ~ close_t + open_t + same_parent + C(lca_class) "
                "+ log_pos + from_start + from_end", A).fit()
print(f"  R^2 position controls only : {m_pos.rsquared:.4f}")
print(f"  R^2 + syntax               : {m_syn.rsquared:.4f}")
print(f"  variance absorbed by syntax: {m_syn.rsquared - m_pos.rsquared:.4f}")
deep = A[A.lca_dist >= 3]
crit_a = deep.algn.mean()
print(f"\n  PRE-SPECIFIED CRITERION: mean alignment at lca_dist >= 3")
print(f"    = {crit_a:.4f}  (n = {len(deep)}; threshold 0.09)")
print(f"    -> {'PASS' if crit_a >= 0.09 else 'FAIL'}")

print("\n" + "=" * 76)
print("A3  TEE VARIANCE ABSORBED BY SYNTAX (descriptive)")
print("=" * 76)
t_pos = smf.ols("tee_k3 ~ log_pos + from_start + from_end", A).fit()
t_syn = smf.ols("tee_k3 ~ close_t + open_t + same_parent + C(lca_class) "
                "+ log_pos + from_start + from_end", A).fit()
print(f"  R^2 position only {t_pos.rsquared:.4f}   + syntax "
      f"{t_syn.rsquared:.4f}   absorbed {t_syn.rsquared - t_pos.rsquared:.4f}")

# ---------------- PART B ----------------
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                "log_freq_fixed", "close_t", "open_t", "same_parent",
                "lca_dist"]], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
D = d.dropna(subset=["log_RT", "word_length", "log_freq_fixed", "zone",
                     "prev_log_RT", "tee_k3", "surprisal", "close_t",
                     "same_parent", "lca_dist"]).copy()
D["lca_class"] = np.minimum(D.lca_dist, 3).astype(int)
for c in ["word_length", "log_freq_fixed", "zone", "prev_log_RT",
          "surprisal", "tee_k3", "close_t", "open_t", "lca_dist"]:
    D["z_" + c] = z(D[c])
print(f"\nRT rows with syntax: {len(D):,}  participants "
      f"{D.participant.nunique()}")

print("\n" + "=" * 76)
print("B1  POOLED: TEE WITH AND WITHOUT SYNTAX COVARIATES (suggestive)")
print("=" * 76)
BASE = ("log_RT ~ z_word_length + z_log_freq_fixed + z_zone + z_prev_log_RT "
        "+ z_surprisal")
SYN = " + z_close_t + z_open_t + same_parent + C(lca_class) + z_close_t:z_zone"
for lab, f in [("no syntax", BASE), ("with syntax", BASE + SYN)]:
    m0 = smf.mixedlm(f, D, groups=D.participant).fit(reml=False,
                                                     method="lbfgs")
    m1 = smf.mixedlm(f + " + z_tee_k3", D, groups=D.participant).fit(
        reml=False, method="lbfgs")
    print(f"  {lab:<12} dAIC(TEE) {m0.aic - m1.aic:>7.1f}   "
          f"beta {m1.params['z_tee_k3']:+.5f}   "
          f"p {m1.pvalues['z_tee_k3']:.2e}")


def subj(frame, minn=100):
    out = []
    cols = ["tee_k3", "surprisal", "word_length", "log_freq_fixed", "zone",
            "prev_log_RT"]
    for pid, s in frame.groupby("participant"):
        s = s.dropna(subset=cols + ["log_RT"])
        if len(s) < minn:
            continue
        Xm = np.column_stack([zs(s[c].values) for c in cols])
        if (Xm.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s.log_RT.values),
                          sm.add_constant(Xm)).fit().params[1])
    return np.array(out)


print("\n" + "=" * 76)
print("B2  DECISIVE: WITHIN-CONSTITUENT SUBSET (close_t = 0, same_parent = 1)")
print("=" * 76)
sub = D[(D.close_t == 0) & (D.same_parent == 1)]
print(f"  subset: {len(sub):,} rows "
      f"({len(sub)/len(D):.1%}); mean rows/participant "
      f"{len(sub)/D.participant.nunique():.0f}")
b = subj(sub)
pos = (b > 0).mean()
p = stats.wilcoxon(b).pvalue
print(f"  n participants {len(b)}   beta {b.mean():+.5f}   "
      f"{pos:.1%} positive   Wilcoxon p {p:.2e}")
ok = (b.mean() > 0) and (p < .01) and (pos >= .65)
print(f"  STANDING CRITERION (p < .01 AND >= 65%): "
      f"{'PASS' if ok else 'FAIL'}")

print("\n" + "=" * 76)
print("B3  COMPLEMENT: BOUNDARY TRANSITIONS")
print("=" * 76)
sub2 = D[(D.close_t > 0) | (D.same_parent == 0)]
b2 = subj(sub2)
pos2 = (b2 > 0).mean()
print(f"  n {len(b2)}   beta {b2.mean():+.5f}   {pos2:.1%} positive   "
      f"p {stats.wilcoxon(b2).pvalue:.2e}")

print("\n" + "=" * 76)
print("OUTCOME PER PREREG")
print("=" * 76)
a_pass = crit_a >= 0.09
print(f"  Part A: {'PASS' if a_pass else 'FAIL'}   Part B: "
      f"{'PASS' if ok else 'FAIL'}")
print({(True, True): "  -> Outcome 1: constituent structure organizes the "
                     "trajectory but does not exhaust it.",
       (False, True): "  -> Outcome 2: geometry largely syntactic; RT effect "
                      "richer than wrap-up.",
       (True, False): "  -> Outcome 3: super-syntactic structure in language; "
                      "within-constituent sensitivity not demonstrable.",
       (False, False): "  -> Outcome 4: TEE is a graded boundary signal; "
                       "dynamical interpretation dropped."}[(a_pass, ok)])
