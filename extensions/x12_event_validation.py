"""
x12: Event-segmentation validation for deep neighborhood TEE.
Boundaries from event_boundaries.py (LLM annotation, blind to per-sentence
ntee). Deep ntee = layer-9 neighborhood TEE from x11's csv. Fine TEE = tee_k3.

Key discriminating test (T_EVENT): among SENTENCE-INITIAL words only (so the
sentence-restart confound is held constant), does deep ntee distinguish EVENT-
boundary sentence-starts from non-boundary sentence-starts, beyond surprisal,
fine TEE, entropy, length, frequency? This is exactly "predicts human-perceived
event boundaries better than surprisal and fine TEE."

Also:
  T_ALL   logistic over all words: boundary(word's sentence-initial & event)
  T_WAKE  does the ntee long causal wake survive an event-boundary control,
          and does it survive EXCLUDING event-boundary target words?
"""
import os, sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, zscore, fit_cluster
from event_boundaries import BOUNDARIES

RES = f"{GP}/extensions/results"
S, sh = load_locked()
disc = pd.read_csv(f"{RES}/x11_discourse.csv")   # ntee_l9, sent_initial, ...
M = S.merge(disc[["story_id", "word_idx", "ntee_l9", "sent_initial"]],
            on=["story_id", "word_idx"], validate="one_to_one")
M["event_bnd"] = [1.0 if r.sent_uid in BOUNDARIES.get(r.story_id, set())
                  else 0.0 for r in M.itertuples()]
nb = int(M.groupby(["story_id", "sent_uid"]).event_bnd.first().sum())
nsent = M.groupby(["story_id", "sent_uid"]).ngroups
print(f"SAMPLE hash={sh}: {nsent} sentences, {nb} event boundaries "
      f"({nb/nsent:.0%})")

# ---- T_EVENT: sentence-initial words only, boundary vs non-boundary ----
SI = M[(M.sent_initial == 1) & (M.has_trailing_punct == 0)] \
    .reset_index(drop=True)
# drop each story's truncated first sentence (no prior context)
first_sent = M.groupby("story_id").sent_uid.min().to_dict()
SI = SI[SI.apply(lambda r: r.sent_uid != first_sent[r.story_id], axis=1)] \
    .reset_index(drop=True)
print(f"\nT_EVENT: sentence-initial words (punct-free, non-truncated) "
      f"n={len(SI)}, event-boundary starts={int(SI.event_bnd.sum())}")
Z = SI.copy()
for c in ["ntee_l9", "surprisal", "entropy", "tee_k3", "log_freq",
          "word_length"]:
    Z[c] = zscore(SI[c])
m = smf.logit("event_bnd ~ ntee_l9 + surprisal + entropy + tee_k3"
              " + log_freq + word_length", data=Z).fit(disp=0)
for t in ["ntee_l9", "surprisal", "entropy", "tee_k3"]:
    print(f"  {t:10s} b={m.params[t]:+.3f}  p={m.pvalues[t]:.1e}"
          f"{'*' if m.pvalues[t] < .05 else ''}")
# AUC of ntee alone vs surprisal alone among sentence starts
from sklearn.metrics import roc_auc_score
for c in ["ntee_l9", "surprisal", "tee_k3"]:
    try:
        auc = roc_auc_score(SI.event_bnd, SI[c])
    except ValueError:
        auc = np.nan
    print(f"  AUC({c}) discriminating event-boundary sentence starts = "
          f"{auc:.3f}")

# ---- T_ALL: over all punct-free words ----
Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
Z = Mpf.copy()
for c in ["ntee_l9", "surprisal", "entropy", "tee_k3", "log_freq",
          "word_length"]:
    Z[c] = zscore(Mpf[c])
m2 = smf.logit("event_bnd ~ ntee_l9 + surprisal + entropy + tee_k3"
               " + log_freq + word_length", data=Z).fit(disp=0)
print(f"\nT_ALL: all punct-free words (n={len(Mpf)}, "
      f"{int(Mpf.event_bnd.sum())} event-boundary words):")
for t in ["ntee_l9", "surprisal", "entropy", "tee_k3"]:
    print(f"  {t:10s} b={m2.params[t]:+.3f}  p={m2.pvalues[t]:.1e}"
          f"{'*' if m2.pvalues[t] < .05 else ''}")

# ---- T_WAKE: does the long wake survive an event-boundary control? ----
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
DW = W.merge(M[["story_id", "word_idx", "event_bnd", "sent_initial"]],
             on=["story_id", "word_idx"]) \
      .merge(S.drop(columns=[c for c in S.columns
                             if c in ("event_bnd",)]),
             on=["story_id", "word_idx"]) \
      .merge(C[["story_id", "word_idx", "ntee_k100", "ctee_m5"]],
             on=["story_id", "word_idx"]) \
      .merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp",
                  "curvature_3"]], on=["story_id", "word_idx"])
DWpf = DW[DW.has_trailing_punct == 0].reset_index(drop=True)
PRED = ["ntee_k100", "event_bnd", "entropy", "curvature_3", "surprisal",
        "tee3_perp", "tee3_par", "ctee_m5", "word_length", "log_freq"]
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"
print("\nT_WAKE: wake_rel_L with event-boundary control (punct-free "
      f"n={len(DWpf)}):")
for L in (1, 2, 5, 10):
    dv = f"wake_rel_{L}"
    Dl = DWpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p in PRED:
        Z[p] = zscore(Dl[p])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
    print(f"  L{L:>2}: ntee={mod.params['ntee_k100']:+.3f}"
          f"(p={mod.pvalues['ntee_k100']:.0e}) "
          f"event_bnd={mod.params['event_bnd']:+.3f}"
          f"(p={mod.pvalues['event_bnd']:.0e})")

# exclude event-boundary target words
D2 = DWpf[DWpf.event_bnd == 0].reset_index(drop=True)
PRED2 = [p for p in PRED if p != "event_bnd"]
print(f"\nT_WAKE excluding event-boundary targets (n={len(D2)}):")
for L in (1, 2, 5, 10):
    dv = f"wake_rel_{L}"
    Dl = D2.dropna(subset=[dv] + PRED2).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p in PRED2:
        Z[p] = zscore(Dl[p])
    mod = fit_cluster(f"y ~ {' + '.join(PRED2)} + {CTRL}", Z)
    print(f"  L{L:>2}: ntee={mod.params['ntee_k100']:+.3f}"
          f"(p={mod.pvalues['ntee_k100']:.0e})")

M[["story_id", "word_idx", "ntee_l9", "sent_initial", "event_bnd"]] \
    .to_csv(f"{RES}/x12_event_validation.csv", index=False)
print(f"\nDONE hash={sh}")
