"""
Analyze human event-segmentation annotations once collected. Reads every
extensions/human_annotation_kit/annotator_*.csv, builds a graded boundary-
agreement score per sentence, and runs the confirmatory deep-ntee event test
against the human consensus — mirroring x13 exactly, but with human labels.

Outputs (when annotators are present):
  results/human_boundary_agreement.csv
  results/x14_human_event_validation.txt

If no annotator files are found, prints how to produce them and exits 0.
"""
import glob, os, sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, zscore

KIT = f"{GP}/extensions/human_annotation_kit"
RES = f"{GP}/extensions/results"
files = sorted(glob.glob(f"{KIT}/annotator_*.csv"))
if not files:
    print("No annotator_*.csv found. Run make_annotation_kit.py, distribute "
          "annotation_sheet.csv with INSTRUCTIONS.md, collect completed files "
          "as annotator_<id>.csv here, then re-run this script.")
    sys.exit(0)

def load_one(f):
    a = pd.read_csv(f)
    a["b"] = pd.to_numeric(a["boundary_1_if_new_event"], errors="coerce") \
        .fillna(0).clip(0, 1)
    return a[["story_id", "sent_uid", "b"]].rename(
        columns={"b": os.path.basename(f)})

A = load_one(files[0])
for f in files[1:]:
    A = A.merge(load_one(f), on=["story_id", "sent_uid"])
bcols = [c for c in A.columns if c.startswith("annotator_")]
A["boundary_agreement"] = A[bcols].mean(axis=1)
A["human_bnd"] = (A["boundary_agreement"] >= 0.5).astype(float)
# inter-annotator agreement (mean pairwise Cohen kappa-ish: mean pairwise
# proportion agreement above chance)
from itertools import combinations
ag = [np.mean(A[i].values == A[j].values) for i, j in combinations(bcols, 2)]
print(f"{len(files)} annotators; mean pairwise raw agreement = "
      f"{np.mean(ag):.3f}; boundaries (>=50% consensus) = "
      f"{int(A.human_bnd.sum())}/{len(A)}")
A.to_csv(f"{RES}/human_boundary_agreement.csv", index=False)

# merge onto deep-ntee (held-out) and rerun the confirmatory test
S, sh = load_locked()
HO = pd.read_csv(f"{GP}/extensions/ntee_l9_heldout_8a6087341e.csv")
M = S.merge(HO, on=["story_id", "word_idx"]).sort_values(
    ["story_id", "word_idx"]).reset_index(drop=True)
M["sent_initial"] = (M.groupby("story_id")["sent_uid"].diff() != 0) \
    .astype(float)
M = M.merge(A[["story_id", "sent_uid", "boundary_agreement", "human_bnd"]],
            on=["story_id", "sent_uid"], how="left")
SI = M[(M.sent_initial == 1) & (M.has_trailing_punct == 0)].dropna(
    subset=["human_bnd"]).reset_index(drop=True)
first_sent = M.groupby("story_id").sent_uid.min().to_dict()
SI = SI[SI.apply(lambda r: r.sent_uid != first_sent[r.story_id], axis=1)] \
    .reset_index(drop=True)
Z = SI.copy()
for c in ["ntee_l9_ho", "surprisal", "entropy", "tee_k3", "log_freq",
          "word_length"]:
    Z[c] = zscore(SI[c])
out = [f"n={len(SI)} sentence-initial words; human boundaries="
       f"{int(SI.human_bnd.sum())}"]
m = smf.logit("human_bnd ~ ntee_l9_ho + surprisal + entropy + tee_k3"
              " + log_freq + word_length", data=Z).fit(disp=0)
for t in ["ntee_l9_ho", "surprisal", "entropy", "tee_k3"]:
    out.append(f"  {t:12s} b={m.params[t]:+.3f} p={m.pvalues[t]:.1e}")
for c in ["ntee_l9_ho", "surprisal", "tee_k3"]:
    out.append(f"  AUC({c}) = {roc_auc_score(SI.human_bnd, SI[c]):.3f}")
# graded: correlation of ntee with boundary_agreement
r = np.corrcoef(SI.ntee_l9_ho, SI.boundary_agreement)[0, 1]
out.append(f"  r(ntee_l9_ho, boundary_agreement) = {r:+.3f}")
txt = "\n".join(out)
print("\n" + txt)
open(f"{RES}/x14_human_event_validation.txt", "w").write(txt + "\n")
print(f"\nDONE hash={sh}")
