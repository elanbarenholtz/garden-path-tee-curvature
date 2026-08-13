"""
CORE RESULTS FIGURE, v2: SHOW THE EFFECT, NOT JUST ITS RELIABILITY
===================================================================
The first attempt plotted observed vs shuffled per-participant coefficients.
That establishes the effect is not noise but never shows the effect itself, and
says nothing about how it compares with surprisal -- which is what a reader needs
in order to calibrate the claim.

This shows partial effects. For each measure, log reading time is residualised
within participant on every other predictor (including the competing measure),
then averaged by decile of the focus measure. So the TEE curve is the reading-time
variation that surprisal, frequency, length, position and previous reading time
do NOT account for, and the surprisal curve is the reverse. Plotted on shared
axes, the two curves show relative contribution directly.

  Panel A  Natural Stories: partial effect of TEE and of surprisal
  Panel B  Garden-path corpus: same
  Panel C  Coefficients for all predictors, both corpora, so the trajectory
           effect is placed against the standard lexical controls rather than
           against surprisal alone

Procedure per participant:
  1. fit z(log RT) ~ all predictors except the focus
  2. take residuals
  3. bin by within-participant decile of the focus predictor
  4. mean residual per decile
Then average across participants; error bars are standard errors across
participants. Binning within participant avoids between-reader differences in
speed driving the curve.

Everything recomputed from the verified pipelines.
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
NBIN = 10


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def partial_profile(df, subj, focus, others, outcome, minn):
    """Per-participant residual profile of `outcome` across deciles of `focus`,
    residualising on `others`."""
    prof, betas = [], []
    for pid, s in df.groupby(subj):
        s = s.dropna(subset=[focus] + others + [outcome])
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in others])
        if (X.std(axis=0) == 0).any():
            continue
        y = zs(s[outcome].values)
        res = y - sm.OLS(y, sm.add_constant(X)).fit().fittedvalues
        f = s[focus].values
        try:
            q = pd.qcut(f, NBIN, labels=False, duplicates="drop")
        except ValueError:
            continue
        if pd.isna(q).any() or len(np.unique(q)) < NBIN:
            continue
        prof.append([res[q == b].mean() for b in range(NBIN)])
        Xf = np.column_stack([zs(f)] + [zs(s[c].values) for c in others])
        betas.append(sm.OLS(y, sm.add_constant(Xf)).fit().params[1])
    P = np.array(prof)
    return P.mean(0), P.std(0) / np.sqrt(len(P)), np.array(betas), len(P)


# ---------------------------------------------------------------- corpora
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
                       "prev_log_RT", "tee_k3", "surprisal"])
NS_ALL = ["tee_k3", "surprisal", "word_length", "log_freq", "zone",
          "prev_log_RT"]
print(f"Natural Stories {len(ns):,} rows / {ns.participant.nunique()} participants")

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
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
SAP_ALL = ["tee", "surp", "word_length", "log_freq", "punct",
           "from_start", "fs2", "from_end", "fe2"]
print(f"SAP {len(d):,} rows / {d.participant.nunique():,} participants")

CORPORA = [
    ("Natural Stories", ns, "participant", NS_ALL, "log_RT", 300,
     [("tee_k3", "trajectory extrapolation error", "#B03030"),
      ("surprisal", "surprisal", "#25506B")],
     {"tee_k3": "trajectory error", "surprisal": "surprisal",
      "log_freq": "log frequency", "word_length": "word length",
      "prev_log_RT": "previous RT", "zone": "position"}),
    ("Garden-path corpus", d, "participant", SAP_ALL, "log_RT", 100,
     [("tee", "trajectory extrapolation error", "#B03030"),
      ("surp", "surprisal", "#25506B")],
     {"tee": "trajectory error", "surp": "surprisal",
      "log_freq": "log frequency", "word_length": "word length",
      "punct": "punctuation", "from_start": "position"}),
]

results = {}
for name, df, subj, allc, outc, minn, foci, _ in CORPORA:
    results[name] = {}
    for f, lab, col in foci:
        others = [c for c in allc if c != f]
        m, se, betas, n = partial_profile(df, subj, f, others, outc, minn)
        results[name][f] = (m, se, betas, n, lab, col)
        print(f"  {name:<20} {lab:<34} beta={betas.mean():+.5f}  n={n}")

# ---------------------------------------------------------------- figure
fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.3))
x = np.arange(1, NBIN + 1)

for ax, (name, df, subj, allc, outc, minn, foci, _) in zip(axes[:2], CORPORA):
    for f, lab, col in foci:
        m, se, betas, n, lab, col = results[name][f]
        ax.errorbar(x, m, yerr=1.96 * se, color=col, lw=2, marker="o", ms=4.5,
                    capsize=2, label=f"{lab}")
    ax.axhline(0, color="k", lw=.7, ls=":")
    ax.set_title(name, fontsize=11, loc="left")
    ax.set_xlabel("decile of predictor (within participant)", fontsize=9.5)
    ax.set_xticks([1, 5, 10])
    ax.tick_params(labelsize=8.5)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
axes[0].set_ylabel("residual log reading time\n(all other predictors removed)",
                   fontsize=9.5)

ax = axes[2]
ypos, ticks, labels, cols = [], [], [], []
y = 0.0
# Only predictors that are candidate accounts of processing difficulty.
# Previous reading time, sentence position and their polynomial terms are
# nuisance controls -- previous RT in particular is an autocorrelation term and
# dominates any model it appears in, which makes it meaningless to compare
# against. All remain IN the models; they are simply not plotted.
SHOW = {"Natural Stories": ["tee_k3", "surprisal", "log_freq", "word_length"],
        "Garden-path corpus": ["tee", "surp", "log_freq", "word_length"]}
for name, df, subj, allc, outc, minn, foci, pretty in CORPORA:
    order = SHOW[name]
    for c in order:
        others = [o for o in allc if o != c]
        _, _, betas, n = partial_profile(df, subj, c, others, outc, minn)
        col = "#B03030" if c in ("tee_k3", "tee") else "0.45"
        ci = 1.96 * betas.std() / np.sqrt(len(betas))
        ax.barh(-y, betas.mean(), xerr=ci, color=col, height=.62,
                error_kw=dict(lw=1, capsize=2))
        ticks.append(-y)
        labels.append(pretty.get(c, c))
        cols.append(col)
        y += 1
    y += 1.1
ax.axvline(0, color="k", lw=.7)
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=8)
for t, c in zip(ax.get_yticklabels(), cols):
    t.set_color(c if c != "0.45" else "0.25")
ax.set_xlabel("standardised coefficient", fontsize=9.5)
ax.set_title("Unique contribution of each predictor", fontsize=11, loc="left")
ax.tick_params(labelsize=8.5)
ax.text(0.99, 0.99, "Natural Stories", transform=ax.transAxes, ha="right",
        va="top", fontsize=8.5, style="italic")
ax.text(0.99, 0.47, "Garden-path corpus", transform=ax.transAxes, ha="right",
        va="top", fontsize=8.5, style="italic")
ax.text(0.99, 0.02, "nuisance controls (previous RT, position)\nare in the "
        "models but not plotted", transform=ax.transAxes, ha="right",
        va="bottom", fontsize=7, color="0.45")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig(f"{GP}/arxiv_v2/fig_core.png", dpi=300)
print("\nwrote fig_core.png")
