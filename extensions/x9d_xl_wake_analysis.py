"""
x9d: XL wake regressions + layer-sweep wake betas.
Usage: python3 x9d_xl_wake_analysis.py [gpt2_xl] [STEP=12]
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, zscore, fit_cluster

TAG = sys.argv[1] if len(sys.argv) > 1 else "gpt2_xl"
STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 12
S, sh = load_locked()
M = pd.read_csv(f"{GP}/extensions/{TAG}_measures_8a6087341e.csv")
W = pd.read_csv(f"{GP}/extensions/{TAG}_wake_step{STEP}.csv")
NLAY = len([c for c in M.columns if c.startswith("ntee_l")])
MIDI = NLAY // 2
NTEE = f"ntee_l{MIDI}_xl"
D = W.merge(M, on=["story_id", "word_idx"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
D["sent_initial"] = (D.groupby("story_id")["sent_uid"].diff() != 0) \
    .astype(float)
Dpf = D[D.has_trailing_punct == 0].reset_index(drop=True)
print(f"{TAG} wake n={len(D)} (punct-free {len(Dpf)}), mid slot {MIDI}")

PRED = [NTEE, f"entropy_{TAG}", "curvature_3_xl", f"surprisal_{TAG}",
        "tee_k3_xl", "sent_initial", "word_length", "log_freq"]
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"
print("\nPUNCT-FREE wake_rel_L (XL mid layer), full controls:")
print(f"{'lag':>3s} {'ntee_mid':>16s} {'entropy':>16s} {'surprisal':>16s} "
      f"{'tee_k3_xl':>16s}")
for L in range(1, 11):
    dv = f"wake_rel_{L}"
    Dl = Dpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p in PRED:
        Z[p] = zscore(Dl[p])
    m = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
    cells = []
    for p in [NTEE, f"entropy_{TAG}", f"surprisal_{TAG}", "tee_k3_xl"]:
        b, pv = m.params[p], m.pvalues[p]
        cells.append(f"{b:+.3f}({pv:.0e}){'*' if pv < .05 else ' '}")
    print(f"{L:>3d} " + " ".join(f"{c:>16s}" for c in cells))

print("\nlayer-slot sweep: wake_rel_5 beta per ntee layer (punct-free, "
      "entropy+surprisal+lexical controls):")
for li in range(NLAY):
    meas = f"ntee_l{li}_xl"
    Dl = Dpf.dropna(subset=["wake_rel_5", meas]).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl["wake_rel_5"])
    for c in [meas, f"entropy_{TAG}", f"surprisal_{TAG}", "word_length",
              "log_freq"]:
        Z[c] = zscore(Dl[c])
    m = fit_cluster(f"y ~ {meas} + entropy_{TAG} + surprisal_{TAG}"
                    f" + word_length + log_freq + {CTRL}", Z)
    print(f"  slot {li:2d}: beta={m.params[meas]:+.3f} "
          f"p={m.pvalues[meas]:.0e}")
print(f"\nDONE {TAG} hash={sh}")
