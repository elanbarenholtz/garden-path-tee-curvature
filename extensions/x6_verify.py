"""
x6: Verification pass for the headline claims.
V1. ntee_k100 long wake: rerun wake regressions with ENTROPY and curvature_3
    added as competitors (ntee is entropy-coupled; entropy could carry its
    own long wake). Punct-free. Report ntee/entropy/surprisal betas by lag.
V2. Per-story sign consistency: story-by-story betas for (a) ntee_k100 ->
    wake_rel_5, (b) ntee_k100 -> on-word RT, (c) ftee_n50 -> RT at L1.
V3. Leave-out robustness for ntee wake: drop targets whose downstream 5 words
    contain any punct-final word.
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, load_rt, zscore, fit_cluster

RES = f"{GP}/extensions/results"; os.makedirs(RES, exist_ok=True)
S, sh = load_locked()
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
NL = pd.read_csv(f"{GP}/extensions/nonlinear_tee_8a6087341e.csv")

D = W.merge(S, on=["story_id", "word_idx"], validate="one_to_one") \
     .merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp",
                 "curvature_3"]], on=["story_id", "word_idx"]) \
     .merge(C[["story_id", "word_idx", "ctee_m5", "ntee_k100"]],
            on=["story_id", "word_idx"])
print(f"SAMPLE: hash={sh} wake n={len(D)}")
Dpf = D[D.has_trailing_punct == 0].reset_index(drop=True)

PRED = ["ntee_k100", "entropy", "curvature_3", "surprisal", "tee3_perp",
        "tee3_par", "ctee_m5", "word_length", "log_freq"]
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"
print("\nV1. PUNCT-FREE wake_rel with entropy + curvature competitors "
      f"(n={len(Dpf)})")
print(f"{'lag':>3s} " + " ".join(f"{p:>16s}" for p in PRED[:4]))
v1 = []
for L in range(1, 11):
    dv = f"wake_rel_{L}"
    Dl = Dpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p in PRED:
        Z[p] = zscore(Dl[p])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
    cells = []
    for p in PRED[:4]:
        b, pv = mod.params[p], mod.pvalues[p]
        star = "*" if pv < .05 else " "
        cells.append(f"{b:+.3f}({pv:.0e}){star}")
        v1.append({"lag": L, "term": p, "beta": b, "p": pv})
    print(f"{L:>3d} " + " ".join(f"{c:>16s}" for c in cells))
pd.DataFrame(v1).to_csv(f"{RES}/x6_v1_entropy_control.csv", index=False)

# same for wake_coarse
print("\nV1b. same, DV = wake_coarse_L")
for L in (2, 5, 10):
    dv = f"wake_coarse_{L}"
    Dl = Dpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p in PRED:
        Z[p] = zscore(Dl[p])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
    print(f" L{L}: " + " ".join(
        f"{p}={mod.params[p]:+.3f}(p={mod.pvalues[p]:.0e})"
        for p in PRED[:4]))

# V2a. per-story ntee -> wake_rel_5 (punct-free, simple OLS per story)
import statsmodels.formula.api as smf
print("\nV2a. per-story beta: z(wake_rel_5) ~ z(ntee_k100) + z(surprisal) "
      "+ z(entropy) + pos")
for sid in sorted(Dpf.story_id.unique()):
    Ds = Dpf[Dpf.story_id == sid].dropna(
        subset=["wake_rel_5", "ntee_k100", "surprisal", "entropy"])
    Zs = Ds.copy()
    for c in ["wake_rel_5", "ntee_k100", "surprisal", "entropy"]:
        Zs[c] = zscore(Ds[c])
    m = smf.ols("wake_rel_5 ~ ntee_k100 + surprisal + entropy + from_start"
                " + fs2 + from_end + fe2", data=Zs).fit()
    print(f"  story {sid:2d}: beta_ntee={m.params['ntee_k100']:+.3f} "
          f"(n={len(Ds)})")

# V2b/c. per-story RT effects
RT = load_rt()
DRS = S.merge(C[["story_id", "word_idx", "ntee_k100"]],
              on=["story_id", "word_idx"]) \
       .merge(NL[["story_id", "word_idx", "ftee_n50"]],
              on=["story_id", "word_idx"]) \
       .merge(RT, on=["story_id", "zone"])
DRS = DRS.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
for v in ["ftee_n50", "surprisal", "word_length", "log_freq",
          "has_trailing_punct"]:
    DRS[f"{v}_L1"] = DRS.groupby("story_id")[v].shift(1)
DRS["prev_logRT"] = DRS.groupby("story_id")["mean_logRT"].shift(1)
print("\nV2b. per-story beta: on-word RT ~ ntee_k100 (+surprisal, lexical, "
      "punct, prevRT, pos)")
for sid in sorted(DRS.story_id.unique()):
    Ds = DRS[DRS.story_id == sid].dropna(
        subset=["ntee_k100", "prev_logRT"]).copy()
    for c in ["ntee_k100", "surprisal", "word_length", "log_freq",
              "has_trailing_punct", "prev_logRT"]:
        Ds[c] = zscore(Ds[c])
    m = smf.ols("mean_logRT ~ ntee_k100 + surprisal + word_length + log_freq"
                " + has_trailing_punct + prev_logRT + from_start + fs2"
                " + from_end + fe2", data=Ds).fit()
    print(f"  story {sid:2d}: beta_ntee={m.params['ntee_k100']:+.4f}")
print("\nV2c. per-story beta: RT ~ ftee_n50_L1 (+controls at L1)")
for sid in sorted(DRS.story_id.unique()):
    Ds = DRS[DRS.story_id == sid].dropna(
        subset=["ftee_n50_L1", "prev_logRT"]).copy()
    for c in ["ftee_n50_L1", "surprisal_L1", "word_length_L1", "log_freq_L1",
              "has_trailing_punct_L1", "prev_logRT"]:
        Ds[c] = zscore(Ds[c])
    m = smf.ols("mean_logRT ~ ftee_n50_L1 + surprisal_L1 + word_length_L1"
                " + log_freq_L1 + has_trailing_punct_L1 + prev_logRT"
                " + from_start + fs2 + from_end + fe2", data=Ds).fit()
    print(f"  story {sid:2d}: beta_ftee_L1={m.params['ftee_n50_L1']:+.4f}")

# V3. drop targets with punct in downstream window
S2 = S.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
S2["down_punct"] = 0.0
for sid in sorted(S2.story_id.unique()):
    idx = S2.story_id == sid
    p = S2.loc[idx, "has_trailing_punct"].values
    dp = np.array([p[i + 1:i + 6].sum() for i in range(len(p))])
    S2.loc[idx, "down_punct"] = dp
D3 = Dpf.merge(S2[["story_id", "word_idx", "down_punct"]],
               on=["story_id", "word_idx"])
D3 = D3[D3.down_punct == 0].reset_index(drop=True)
print(f"\nV3. targets with NO punct-final word in w+1..w+5 (n={len(D3)})")
for L in (2, 5):
    dv = f"wake_rel_{L}"
    Dl = D3.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p in PRED:
        Z[p] = zscore(Dl[p])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
    print(f" L{L}: ntee={mod.params['ntee_k100']:+.3f}"
          f"(p={mod.pvalues['ntee_k100']:.0e}) "
          f"entropy={mod.params['entropy']:+.3f}"
          f"(p={mod.pvalues['entropy']:.0e}) "
          f"surprisal={mod.params['surprisal']:+.3f}"
          f"(p={mod.pvalues['surprisal']:.0e})")
print(f"\nDONE hash={sh}")
