"""
CORE RESULTS FIGURE: the shift, and the magnitude
==================================================
Panel A plots what is actually diagnostic in the per-participant coefficient
distributions: the DIFFERENCE between observed and shuffled counts across the
coefficient range. Overlaying the two histograms buries the signal, because the
distributions have similar gross shape and the eye reads "these look the same".
The signal is the asymmetry -- a deficit of participants below zero and an
excess above -- and differencing makes that the thing you see rather than
something to be inferred.

Shuffled counts come from ten within-participant permutations, averaged, so the
comparison is against a stable floor rather than one draw.

Panel B places the effect against predictors readers already have intuitions
about. Word length is excluded: at +0.135 in the garden-path corpus it sets the
axis and compresses everything of interest, the same problem previous reading
time had. It is in every model and reported in the text. Log frequency is kept
because it sits on a comparable scale in both corpora.

Nuisance controls (previous reading time, sentence position and its polynomial
terms) are in every model and not plotted.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"
RNG = np.random.default_rng(20260810)
RED, BLUE, GREY = "#B03030", "#25506B", "0.55"
NPERM = 10


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def betas(df, subj, focus, others, outcome, minn, permute=False):
    out = []
    for pid, s in df.groupby(subj):
        s = s.dropna(subset=[focus] + others + [outcome])
        if len(s) < minn:
            continue
        f = (RNG.permutation(s[focus].values) if permute else s[focus].values)
        X = np.column_stack([zs(f)] + [zs(s[c].values) for c in others])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s[outcome].values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
ns = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                 "log_freq"]], on=["story_id", "zone"], how="inner")
ns["log_RT"] = np.log(ns.RT)
ns = ns.sort_values(["participant", "story_id", "zone"])
ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                       "prev_log_RT", "tee_k3", "surprisal"]).rename(
    columns={"tee_k3": "tee"})
NS_ALL = ["tee", "surprisal", "word_length", "log_freq", "zone", "prev_log_RT"]

d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
d = d.merge(pd.read_csv(f"{GPC}/sap_measures_L6k3.csv"),
            on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
d["word_length"] = d.EachWord.str.len()
d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
d["from_start"] = d.WordPosition.astype(float)
d["fs2"] = d.from_start ** 2
d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
d["fe2"] = d.from_end ** 2
d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
d["log_RT"] = np.log(d.RT)
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq",
                     "log_RT"]).rename(columns={"surp": "surprisal"})
SAP_ALL = ["tee", "surprisal", "word_length", "log_freq", "punct",
           "from_start", "fs2", "from_end", "fe2"]

SHOW = ["tee", "surprisal", "log_freq"]
PRETTY = {"tee": "trajectory error", "surprisal": "surprisal",
          "log_freq": "log frequency"}
CORP = [("Natural Stories", ns, NS_ALL, 300, "178 participants"),
        ("Garden-path corpus", d, SAP_ALL, 100, "2,000 participants")]

R = {}
for name, df, allc, minn, sub in CORP:
    R[name] = {c: betas(df, "participant", c, [o for o in allc if o != c],
                        "log_RT", minn) for c in SHOW}
    perms = [betas(df, "participant", "tee", [o for o in allc if o != "tee"],
                   "log_RT", minn, permute=True) for _ in range(NPERM)]
    R[name]["_perm"] = perms
    b = R[name]["tee"]
    print(f"{name}: beta={b.mean():+.5f} {(b>0).mean():.1%} pos, "
          f"floor {np.mean([(p>0).mean() for p in perms]):.1%}")

fig = plt.figure(figsize=(11.6, 4.6))
gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.0], hspace=0.62, wspace=0.26)

for i, (name, df, allc, minn, sub) in enumerate(CORP):
    # Cumulative distributions. A difference histogram was misleading here: it
    # has to be clipped to be readable, which breaks the requirement that the
    # bars sum to zero, and colouring by sign of the difference puts grey bars
    # just above zero. Overlaid ECDFs show a location shift with no binning,
    # no clipping and no sign convention -- the shifted curve lies to the right.
    ax = fig.add_subplot(gs[i, 0])
    b = np.sort(R[name]["tee"])
    perm = np.sort(np.concatenate(R[name]["_perm"]))
    ax.step(perm, np.arange(1, len(perm) + 1) / len(perm), where="post",
            color="0.55", lw=1.8, label="shuffled")
    ax.step(b, np.arange(1, len(b) + 1) / len(b), where="post",
            color=RED, lw=2.0, label="observed")
    ax.axvline(0, color="k", lw=.9, ls=":")
    ax.axhline(.5, color="k", lw=.6, ls=":", alpha=.5)
    lo, hi = np.percentile(np.concatenate([b, perm]), [0.5, 99.5])
    ax.set_xlim(lo, hi)
    ax.set_ylim(0, 1)
    ax.set_title(f"{name}   ({sub})", fontsize=9.5, loc="left")
    ax.set_ylabel("cumulative\nproportion", fontsize=8)
    ax.tick_params(labelsize=7.5)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    med_o, med_p = np.median(b), np.median(perm)
    ax.annotate("", xy=(med_o, .5), xytext=(med_p, .5),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))
    ax.text((med_o + med_p) / 2, .555,
            f"median shift\n{med_o - med_p:+.4f}", fontsize=7,
            color=RED, ha="center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
ax.set_xlabel("per-participant coefficient, trajectory error", fontsize=8.5)

ax = fig.add_subplot(gs[:, 1])
ticks, labels, cols, y = [], [], [], 0.0
for name, df, allc, minn, sub in CORP:
    for c in SHOW:
        b = R[name][c]
        ci = 1.96 * b.std(ddof=1) / np.sqrt(len(b))
        col = RED if c == "tee" else (BLUE if c == "surprisal" else GREY)
        ax.barh(-y, b.mean(), xerr=ci, color=col, height=.66,
                error_kw=dict(lw=1, capsize=2.5))
        ticks.append(-y)
        labels.append(PRETTY[c])
        cols.append(col)
        y += 1
    y += 1.4
ax.axvline(0, color="k", lw=.8)
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=8.5)
for t, c in zip(ax.get_yticklabels(), cols):
    t.set_color(c if c != GREY else "0.3")
ax.set_xlabel("standardised coefficient,\ncontrolling for all other predictors",
              fontsize=8.5)
ax.tick_params(labelsize=8)
ax.text(0.99, 0.99, "Natural Stories", transform=ax.transAxes, ha="right",
        va="top", fontsize=8.5, style="italic")
ax.text(0.99, 0.44, "Garden-path corpus", transform=ax.transAxes, ha="right",
        va="top", fontsize=8.5, style="italic")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig(f"{GP}/arxiv_v2/fig_core.png", dpi=300)
print("\nwrote fig_core.png")
