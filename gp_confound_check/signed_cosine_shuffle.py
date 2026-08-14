"""
IS THE -0.436 MECHANICAL? Shuffle control.
==========================================
The signed fitted-direction cosine is -0.436 with 0% of transitions positive.
A mechanical account predicts exactly this shape: the fit window ends at
h_{t-1} and the step departs from h_{t-1}, so a large idiosyncratic per-word
component e_{t-1} enters the fitted slope positively and the step negatively,
producing negative cosine FOR ANY sequence of states, ordered or not.

The informative comparison is therefore ordered text vs SHUFFLED word order
(same states, same geometry, sequential structure destroyed; shuffled within
story, 20 shuffles). Three possible outcomes, interpretation fixed now:

  observed LESS negative than shuffled  -> the difference is genuine
      sequential structure: ordered language partially cancels the mechanical
      reversal. 'Momentum' survives as a relative quantity (drift above
      chance), and the paper must present it that way.
  observed == shuffled                  -> the direction-preservation statistic
      carries no sequential information at all; Table 4 is a property of the
      state distribution, not of language. Major correction.
  observed MORE negative than shuffled  -> ordered language is anti-persistent
      beyond mechanics. Different paper.

Also computed for the |cos| version, since Table 4 is stated in |cos|, and at
+1..+3 steps ahead.
"""

import numpy as np
import pandas as pd
import hashlib

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
RNG = np.random.default_rng(20260814)
NSHUF = 20

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh


def profile(order_by_story):
    """signed and |cos| at steps 0..3 for a given word ordering per story."""
    out = {k: [] for k in range(4)}
    for sid, idx in order_by_story.items():
        zf = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
        H, ls = zf["H"].astype(np.float64), zf["last_sub"]
        W = H[ls][idx]                      # word states in the given order
        n = len(W)
        for w in range(4, n):
            lo = max(w - 3, 1)
            Y = W[lo:w]
            m = Y.shape[0]
            if m < 2:
                continue
            x = np.arange(m, dtype=float)
            xc = x - x.mean()
            slope = (xc[:, None] * (Y - Y.mean(0))).sum(0) / (xc ** 2).sum()
            sn = np.linalg.norm(slope)
            if sn < 1e-9:
                continue
            u = slope / sn
            for k in range(4):
                if w + k < n:
                    st = W[w + k] - W[w + k - 1]
                    stn = np.linalg.norm(st)
                    if stn > 1e-9:
                        out[k].append(float(np.dot(u, st) / stn))
    return {k: np.array(v) for k, v in out.items()}


stories = sorted(S.story_id.unique())
nwords = {}
for sid in stories:
    zf = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
    nwords[sid] = len(zf["last_sub"])

ordered = profile({sid: np.arange(nwords[sid]) for sid in stories})
print("ORDERED text:")
for k in range(4):
    v = ordered[k]
    print(f"  step +{k}: signed {v.mean():+.4f}   |cos| "
          f"{np.abs(v).mean():.4f}   n={len(v):,}")

sh_signed = {k: [] for k in range(4)}
sh_abs = {k: [] for k in range(4)}
for s in range(NSHUF):
    perm = {sid: RNG.permutation(nwords[sid]) for sid in stories}
    p = profile(perm)
    for k in range(4):
        sh_signed[k].append(p[k].mean())
        sh_abs[k].append(np.abs(p[k]).mean())

print(f"\nSHUFFLED word order ({NSHUF} shuffles):")
for k in range(4):
    m = np.mean(sh_signed[k]); s_ = np.std(sh_signed[k])
    ma = np.mean(sh_abs[k])
    print(f"  step +{k}: signed {m:+.4f} (sd {s_:.4f})   |cos| {ma:.4f}")

print("\n" + "=" * 72)
print("VERDICT INPUTS")
print("=" * 72)
o0 = ordered[0].mean()
s0 = np.mean(sh_signed[0]); ssd = np.std(sh_signed[0])
zscore = (o0 - s0) / ssd if ssd > 0 else float("inf")
print(f"  step 0: ordered {o0:+.4f}  vs shuffled {s0:+.4f} "
      f"(z = {zscore:+.1f})")
print(f"  ordered minus shuffled = {o0 - s0:+.4f}")
print("  positive difference -> ordered text is LESS reversed than chance:")
print("  that difference is the sequential (momentum-like) component.")
for k in (1, 2, 3):
    ok_ = ordered[k].mean(); sk = np.mean(sh_signed[k])
    print(f"  step +{k}: ordered {ok_:+.4f}  shuffled {sk:+.4f}   "
          f"diff {ok_ - sk:+.4f}")
