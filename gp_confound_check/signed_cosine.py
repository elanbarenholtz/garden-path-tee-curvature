"""
THE PIVOTAL NUMBER: SIGNED fitted-direction cosine
==================================================
The manuscript's direction-preservation statistic is |cos| between the OLS
direction fitted to the preceding 3 word states and the current step (0.436,
baseline 0.029). Absolute value cannot distinguish continuation (+.44) from
reversal (-.44). Given that raw successive-step cosine is -0.40 (anti-
persistent noise), the sign of the fitted-direction quantity is genuinely
open, and the word "momentum" hangs on it.

Computed here, identical convention to v2_table4_dirpres / syntax_control_A2,
WITHOUT abs(). Interpretation fixed before running:
  strongly positive  -> momentum earned; |cos| understated the claim.
  near zero          -> directional AXIS structure without preferred
                        orientation; "momentum" must be reworded.
  strongly negative  -> stable axis with overshoot/oscillation; "momentum"
                        is the wrong word and the framing changes.

Also reported: the sign split (% of transitions positive), the signed value by
syntactic transition class, and the same at +1/+2/+3 steps ahead (signed
analogue of Table 4's decay row), since the abstract's "predicts the next
representational step" wording rests on these.
"""

import numpy as np
import pandas as pd
import hashlib

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
X = pd.read_csv(f"{GPC}/syntax_vars_8a6087341e.csv")
S = S.merge(X[["story_id", "word_idx", "lca_dist"]],
            on=["story_id", "word_idx"], how="left", validate="one_to_one")

rows = []
for sid, sub in S.groupby("story_id"):
    zf = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
    H, ls = zf["H"].astype(np.float64), zf["last_sub"]
    nw = len(ls)
    for r in sub.itertuples():
        w = r.word_idx
        lo = max(w - 3, 1)
        if w < 4 or (w - lo) < 2:
            continue
        Y = np.stack([H[ls[j]] for j in range(lo, w)])
        m = Y.shape[0]
        x = np.arange(m, dtype=float)
        xc = x - x.mean()
        slope = (xc[:, None] * (Y - Y.mean(0))).sum(0) / (xc ** 2).sum()
        sn = np.linalg.norm(slope)
        if sn < 1e-9:
            continue
        u = slope / sn
        rec = {"story_id": sid, "word_idx": w, "lca_dist": r.lca_dist}
        for k, lab in [(0, "c0"), (1, "c1"), (2, "c2"), (3, "c3")]:
            if w + k < nw:
                step = H[ls[w + k]] - H[ls[w + k - 1]]
                stn = np.linalg.norm(step)
                if stn > 1e-9:
                    rec[lab] = float(np.dot(u, step) / stn)
        rows.append(rec)
D = pd.DataFrame(rows)
print(f"locked sample {sh}   n = {len(D):,} transitions\n")

print("=" * 72)
print("THE NUMBER: signed cos(fitted direction, current step), layer 6 k=3")
print("=" * 72)
c = D.c0.dropna()
print(f"  mean signed cos      = {c.mean():+.4f}")
print(f"  median               = {c.median():+.4f}")
print(f"  %% positive           = {(c > 0).mean():.1%}")
print(f"  mean |cos| (check)   = {c.abs().mean():.4f}   (paper: 0.436)")
print(f"  sd                   = {c.std():.4f}")

print("\n  signed value by steps ahead (decay profile):")
for k, lab in [(0, "current"), (1, "+1"), (2, "+2"), (3, "+3")]:
    v = D[f"c{k}"].dropna()
    print(f"    {lab:>8}: signed {v.mean():+.4f}   |cos| {v.abs().mean():.4f}"
          f"   %pos {(v > 0).mean():.1%}   n={len(v):,}")

print("\n  signed cos by syntactic transition class:")
sub = D.dropna(subset=["lca_dist", "c0"]).copy()
sub["lca_class"] = np.minimum(sub.lca_dist, 3).astype(int)
for cl, g in sub.groupby("lca_class"):
    lab = f"{cl}" if cl < 3 else "3+"
    print(f"    lca {lab:>2}: signed {g.c0.mean():+.4f}   "
          f"%pos {(g.c0 > 0).mean():.1%}   n={len(g):,}")
