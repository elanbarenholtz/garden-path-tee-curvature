"""
x10: The locked robustness package, one table. Rows = the two headline claims;
columns = every pre-specified robustness variant. Values pulled/recomputed
from the session's results CSVs and data files. Output:
results/ROBUSTNESS_TABLE.md (+ .csv)
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, load_rt, zscore, fit_cluster

RES = f"{GP}/extensions/results"
S, sh = load_locked()
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
HO = pd.read_csv(f"{GP}/extensions/ntee_heldout_8a6087341e.csv")
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")

M = S.merge(C[["story_id", "word_idx", "ntee_k30", "ntee_k100", "ntee_k300",
               "ctee_m5", "nswitch_k100"]], on=["story_id", "word_idx"]) \
     .merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp",
                 "curvature_3"]], on=["story_id", "word_idx"]) \
     .merge(HO, on=["story_id", "word_idx"])
DW = W.merge(M, on=["story_id", "word_idx"], validate="one_to_one")
CTRL2 = "from_start + fs2 + from_end + fe2 + C(story_id)"
BASE = ["entropy", "curvature_3", "surprisal", "tee3_perp", "tee3_par",
        "ctee_m5", "word_length", "log_freq"]

def wake_beta(D, meas, L, extra_punct=True):
    preds = [meas] + BASE + (["has_trailing_punct"] if extra_punct else [])
    Dl = D.dropna(subset=[f"wake_rel_{L}"] + preds).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[f"wake_rel_{L}"])
    for p in preds:
        Z[p] = zscore(Dl[p])
    mod = fit_cluster(f"y ~ {' + '.join(preds)} + {CTRL2}", Z)
    return mod.params[meas], mod.pvalues[meas], int(mod.nobs)

def fmt(b, p, n):
    star = "*" if p < .05 else ""
    return f"+{b:.3f} (p={p:.0e}){star} n={n}" if b >= 0 else \
           f"{b:.3f} (p={p:.0e}){star} n={n}"

rows = []
DWpf = DW[DW.has_trailing_punct == 0].reset_index(drop=True)
S2 = S.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
S2["down_punct"] = 0.0
for sid in sorted(S2.story_id.unique()):
    idx = S2.story_id == sid
    p = S2.loc[idx, "has_trailing_punct"].values
    S2.loc[idx, "down_punct"] = [p[i + 1:i + 6].sum() for i in range(len(p))]
DW3 = DWpf.merge(S2[["story_id", "word_idx", "down_punct"]],
                 on=["story_id", "word_idx"])
DW3 = DW3[DW3.down_punct == 0].reset_index(drop=True)

print("CLAIM 1: ntee long causal wake (DV = wake_rel_L, full controls)")
for label, D_, meas, ep in [
        ("punct-controlled (all)", DW, "ntee_k100", True),
        ("punct-free", DWpf, "ntee_k100", False),
        ("held-out clustering (punct-free)", DWpf, "ntee_ho", False),
        ("k=30 (punct-free)", DWpf, "ntee_k30", False),
        ("k=300 (punct-free)", DWpf, "ntee_k300", False),
        ("no punct in w+1..w+5 (punct-free)", DW3, "ntee_k100", False)]:
    cells = {}
    for L in (1, 5, 10):
        b, p, n = wake_beta(D_, meas, L, ep)
        cells[f"L{L}"] = fmt(b, p, n)
    rows.append({"claim": "ntee wake", "variant": label, **cells})
    print(f"  {label:38s} L1={cells['L1']}  L5={cells['L5']}  "
          f"L10={cells['L10']}")

print("\nNULLS / CONTRASTS (punct-free, L5): geometry terms in same model")
for meas in ("tee3_perp", "tee3_par", "ctee_m5", "nswitch_k100",
             "curvature_3", "entropy", "surprisal"):
    Dl = DWpf.dropna(subset=["wake_rel_5", "ntee_k100"] + BASE
                     + ["nswitch_k100"]).reset_index(drop=True)
    preds = ["ntee_k100", "nswitch_k100"] + BASE
    Z = Dl.copy(); Z["y"] = zscore(Dl["wake_rel_5"])
    for p_ in set(preds):
        Z[p_] = zscore(Dl[p_])
    mod = fit_cluster(f"y ~ {' + '.join(dict.fromkeys(preds))} + {CTRL2}", Z)
    if meas in mod.params:
        b, p = mod.params[meas], mod.pvalues[meas]
        rows.append({"claim": "wake L5 competitors", "variant": meas,
                     "L5": fmt(b, p, int(mod.nobs))})
        print(f"  {meas:14s} {fmt(b, p, int(mod.nobs))}")

# CLAIM 2: ntee on-word RT
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
FINE = ["tee3_perp", "tee3_par", "surprisal", "word_length", "log_freq",
        "has_trailing_punct"]
for v in FINE:
    D[f"{v}_L1"] = D.groupby("story_id")[v].shift(1)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
CTRL = "prev_logRT + from_start + fs2 + from_end + fe2 + C(story_id)"

def rt_beta(D_, meas, pf):
    Dl = D_.dropna(subset=[meas, "prev_logRT"]
                   + [f"{v}_L1" for v in FINE]).reset_index(drop=True)
    if pf:
        Dl = Dl[Dl.has_trailing_punct == 0].reset_index(drop=True)
    Z = Dl.copy(); terms = [meas]
    Z[meas] = zscore(Dl[meas])
    for v in FINE:
        if not (pf and v == "has_trailing_punct"):
            Z[v] = zscore(Dl[v]); terms.append(v)
        Z[f"{v}_L1"] = zscore(Dl[f"{v}_L1"]); terms.append(f"{v}_L1")
    Z["prev_logRT"] = zscore(Dl["prev_logRT"])
    mod = fit_cluster(f"mean_logRT ~ {' + '.join(terms)} + {CTRL}", Z)
    return mod.params[meas], mod.pvalues[meas], int(mod.nobs)

print("\nCLAIM 2: ntee on-word RT (full fine-TEE + surprisal battery)")
for label, meas, pf in [("punct-controlled (all)", "ntee_k100", False),
                        ("punct-free", "ntee_k100", True),
                        ("held-out (punct-free)", "ntee_ho", True),
                        ("k=30 (punct-free)", "ntee_k30", True),
                        ("k=300 (punct-free)", "ntee_k300", True),
                        ("NULL: ctee_m5 (punct-free)", "ctee_m5", True),
                        ("NULL: nswitch (punct-free)", "nswitch_k100", True)]:
    b, p, n = rt_beta(D, meas, pf)
    rows.append({"claim": "ntee on-word RT", "variant": label,
                 "L0": fmt(b, p, n)})
    print(f"  {label:38s} {fmt(b, p, n)}")

T = pd.DataFrame(rows)
T.to_csv(f"{RES}/ROBUSTNESS_TABLE.csv", index=False)
with open(f"{RES}/ROBUSTNESS_TABLE.md", "w") as fh:
    fh.write(f"# Locked robustness package (hash {sh})\n\n"
             "All models: position + story FE, cluster-robust SE by sent_uid, "
             "z-scored predictors (ddof=0). Wake models control for entropy, "
             "curvature, surprisal, tee3_perp/par, ctee_m5, length, freq. RT "
             "models control for fine TEE channels, surprisal, lexical, "
             "punct, prev-RT, at L0 and L1.\n\n")
    fh.write(T.to_markdown(index=False))
print(f"\nDONE -> results/ROBUSTNESS_TABLE.md  hash={sh}")
