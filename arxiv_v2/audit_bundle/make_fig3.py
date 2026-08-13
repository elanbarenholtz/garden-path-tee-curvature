"""
REGENERATE FIGURE 3 (dissociation heatmap) FROM THE VERIFIED PIPELINE
=====================================================================
fig3_dissociation.png was produced from the superseded measure file. The tercile
cell means have changed, so the figure no longer matches Table 2 or the text.
This rebuilds it from locked sample 8a6087341e with the same cell definition
used for the table.

Target values (V2_DRAFT 8c), deviation from the low/low baseline of 5.7167:
        TEE low   TEE mid   TEE high
  low    0.0000    +0.0050    +0.0095
  mid   +0.0157    +0.0157    +0.0280
  high  +0.0289    +0.0306    +0.0412
The script asserts it reproduces these before writing the figure.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
OUT = f"{GP}/arxiv_v2/fig3_dissociation.png"

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                "log_freq"]], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                     "prev_log_RT", "surprisal", "tee_k3"])
d["s_t"] = pd.qcut(d.surprisal, 3, labels=["Low", "Mid", "High"])
d["e_t"] = pd.qcut(d.tee_k3, 3, labels=["Low", "Mid", "High"])

piv = d.pivot_table(index="s_t", columns="e_t", values="log_RT",
                    aggfunc="mean", observed=True)
cnt = d.pivot_table(index="s_t", columns="e_t", values="log_RT",
                    aggfunc="size", observed=True)
base = piv.loc["Low", "Low"]
dev = piv - base
print(f"n = {len(d):,}   baseline log RT = {base:.4f}")
print(dev.round(4).to_string())

TARGET = np.array([[0.0000, 0.0050, 0.0095],
                   [0.0157, 0.0157, 0.0280],
                   [0.0289, 0.0306, 0.0412]])
assert np.allclose(dev.values, TARGET, atol=5e-4), \
    f"cell means do not match the reported table:\n{dev.round(4)}"
print("\nmatches Table 2 to 5e-4 -- writing figure")

fig, ax = plt.subplots(figsize=(6.4, 5.0))
im = ax.imshow(dev.values, cmap="YlOrRd", vmin=0, vmax=dev.values.max())
ax.set_xticks(range(3), [f"Low\n(n={cnt.iloc[0,0]:,})".split("\n")[0],
                         "Mid", "High"])
ax.set_yticks(range(3), ["Low", "Mid", "High"])
ax.set_xlabel("Trajectory extrapolation error tercile", fontsize=11)
ax.set_ylabel("Surprisal tercile", fontsize=11)
ax.set_title("Mean log reading time relative to low/low baseline\n"
             "(Natural Stories)", fontsize=11)

for i in range(3):
    for j in range(3):
        v = dev.values[i, j]
        txt = "baseline" if (i == 0 and j == 0) else f"+{v:.3f}"
        ax.text(j, i, f"{txt}\n$n$={cnt.values[i, j]:,}",
                ha="center", va="center", fontsize=9,
                color="black" if v < dev.values.max() * 0.6 else "white")

cb = fig.colorbar(im, ax=ax, shrink=0.85)
cb.set_label("$\\Delta$ log reading time", fontsize=10)
fig.tight_layout()
fig.savefig(OUT, dpi=300)
print(f"wrote {OUT}")
