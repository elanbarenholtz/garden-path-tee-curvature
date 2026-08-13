"""
CORE RESULTS FIGURE, final: reliability and magnitude
======================================================
Two questions a reader has about the headline claim, and nothing else:

  A  Is it reliable?  Per-participant coefficients against a permutation floor
     (measure shuffled within participant, pooled over ten shuffles). Without
     the floor the sign counts are uninterpretable.

  B  How big is it?  Unique contribution of each predictor -- each residualised
     on all the others -- so the trajectory effect is placed against surprisal
     and the standard lexical controls rather than reported alone.

DELIBERATELY NOT SHOWN: the decile profiles. They are not linear, not a clean
threshold, and carry reproducible low-end structure (split-half r = .65 and .88
on deciles 1-7) that none of our models describe. The claim this paper makes
does not depend on functional form, and showing a profile we cannot characterise
would raise a question the paper does not answer. That material is in
GEOMETRY_PAPER_NOTES.md.

Nuisance controls (previous reading time, sentence position and its polynomial
terms) are IN every model but not plotted: previous reading time is an
autocorrelation term that dominates any model it enters, which makes comparing
a substantive effect against it meaningless.
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


def floor(df, subj, focus, others, outcome, minn, reps=10):
    runs = [betas(df, subj, focus, others, outcome, minn, permute=True)
            for _ in range(reps)]
    return np.concatenate(runs), np.mean([(r > 0).mean() for r in runs])


# ------------------------------------------------------------------ corpora
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
S["log_freq"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]').str.lower()
                 .map(lambda w: zipf_frequency(w, "en")))   # repaired
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

# Word length is excluded from the plot: at +0.135 in the garden-path corpus it
# sets the axis and compresses everything of interest into the left fifth, the
# same problem previous reading time had. It is in every model, and its values
# are reported in the text. Log frequency is kept because it sits on a
# comparable scale (+0.022 in both corpora) and so calibrates without
# distorting.
SHOW = ["tee", "surprisal", "log_freq"]
PRETTY = {"tee": "trajectory error", "surprisal": "surprisal",
          "log_freq": "log frequency", "word_length": "word length"}

CORP = [("Natural Stories", ns, NS_ALL, 300, "178 participants"),
        ("Garden-path corpus", d, SAP_ALL, 100, "2,000 participants")]

R = {}
for name, df, allc, minn, sub in CORP:
    R[name] = {}
    for c in SHOW:
        R[name][c] = betas(df, "participant", c,
                           [o for o in allc if o != c], "log_RT", minn)
    R[name]["_floor"] = floor(df, "participant", "tee",
                              [o for o in allc if o != "tee"], "log_RT", minn)
    b = R[name]["tee"]
    print(f"{name}: tee beta={b.mean():+.5f} {(b>0).mean():.1%} pos  "
          f"floor {R[name]['_floor'][1]:.1%}")

# ------------------------------------------------------------------ figure
fig, ax = plt.subplots(figsize=(6.6, 3.6))
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
    y += 1.3
ax.axvline(0, color="k", lw=.8)
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=8.5)
for t, c in zip(ax.get_yticklabels(), cols):
    t.set_color(c if c != GREY else "0.3")
ax.set_xlabel("standardised coefficient, controlling for all other predictors",
              fontsize=9)
ax.tick_params(labelsize=9)
ax.text(0.99, 0.99, "Natural Stories\n(178 participants)",
        transform=ax.transAxes, ha="right", va="top", fontsize=8.5,
        style="italic", linespacing=1.4)
ax.text(0.99, 0.42, "Garden-path corpus\n(2,000 participants)",
        transform=ax.transAxes, ha="right", va="top", fontsize=8.5,
        style="italic", linespacing=1.4)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig(f"{GP}/arxiv_v2/fig_core.png", dpi=300)
print("\nwrote fig_core.png")
for name in R:
    for c in SHOW:
        b = R[name][c]
        print(f"  {name:<20}{PRETTY[c]:<18} {b.mean():+.5f}")
