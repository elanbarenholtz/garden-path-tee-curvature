"""
x3b: Analyze the coarse wake. For each lag L=1..10 and each wake DV
(fine wake_rel, neighborhood-mean wake_coarse, cluster wake_nbhd), regress
z(DV_L) ~ z(tee3_perp)+z(tee3_par)+z(surprisal)+z(ctee_m5)+z(ntee_k100)
        + z(word_length)+z(log_freq)+z(punct) + position + C(story_id),
cluster-robust by sent_uid. KEY QUESTION: does any GEOMETRY term (perp, par,
ctee, ntee) carry a wake past L+1, or does only surprisal propagate — even
when the wake itself is measured at the neighborhood scale?
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, zscore, fit_cluster

RES = f"{GP}/extensions/results"; os.makedirs(RES, exist_ok=True)
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6
S, sh = load_locked()
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step{STEP}.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")

D = W.merge(S, on=["story_id", "word_idx"], validate="one_to_one")
D = D.merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp"]],
            on=["story_id", "word_idx"], validate="one_to_one")
D = D.merge(C[["story_id", "word_idx", "ctee_m5", "ntee_k100",
               "nswitch_k100"]], on=["story_id", "word_idx"],
            validate="one_to_one")
print(f"SAMPLE: hash={sh}  wake n={len(D)} (STEP={STEP})")

PRED = ["tee3_perp", "tee3_par", "surprisal", "ctee_m5", "ntee_k100",
        "word_length", "log_freq", "has_trailing_punct"]
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"
MAXL = 10

def run_block(D0, tag):
    out = []
    for fam in ("wake_rel", "wake_coarse", "wake_nbhd"):
        print(f"\n=== {tag} | DV family {fam} (n={len(D0)}) ===")
        hdr = f"{'lag':>3s} " + " ".join(f"{p:>16s}" for p in PRED[:5])
        print(hdr)
        for L in range(1, MAXL + 1):
            dv = f"{fam}_{L}"
            Dl = D0.dropna(subset=[dv] + PRED).reset_index(drop=True)
            Z = Dl.copy()
            Z["y"] = zscore(Dl[dv])
            for p in PRED:
                Z[p] = zscore(Dl[p])
            mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
            cells = []
            for p in PRED[:5]:
                b, pv = mod.params[p], mod.pvalues[p]
                star = "*" if pv < .05 else " "
                cells.append(f"{b:+.3f}({pv:.0e}){star}")
                out.append({"tag": tag, "family": fam, "lag": L, "term": p,
                            "beta": b, "p": pv, "n": int(mod.nobs)})
            print(f"{L:>3d} " + " ".join(f"{c:>16s}" for c in cells))
    return out

rows = run_block(D, "ALL")
Dpf = D[D.has_trailing_punct == 0].reset_index(drop=True)
PRED.remove("has_trailing_punct")
rows += run_block(Dpf, "PUNCT-FREE")
pd.DataFrame(rows).to_csv(f"{RES}/x3b_wake_regressions.csv", index=False)
print(f"\nDONE hash={sh}")
