"""
CORE RESULTS FIGURE
===================
The paper has a schematic of the measure and a dissociation heatmap, but no
figure showing the headline result. This builds one.

The headline is two claims:
  (a) individual readers show the effect -- it is not an artifact of pooling
      hundreds of thousands of observations
  (b) it survives increasingly strong controls, in both corpora

Panel A. Distribution of per-participant coefficients, one row per corpus, with
the permutation floor (measure shuffled within participant) drawn underneath.
The floor is the point of the panel: without it, "61% of participants positive"
means nothing.

Panel B. The same coefficient re-estimated under successively stronger
specifications, with bootstrap intervals over participants. Everything is
subject-level so the two panels are on the same footing -- no mixing of pooled
dAIC with per-participant betas.

All values recomputed here from the verified pipelines (Natural Stories locked
sample 8a6087341e; SAP measures cached from the verified run) rather than
transcribed from output files.

Output: fig_core.png
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"
RNG = np.random.default_rng(20260810)


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def subj_betas(df, subj, cols, outcome, minn, permute=False):
    out = []
    for pid, s in df.groupby(subj):
        s = s.dropna(subset=cols + [outcome])
        if len(s) < minn:
            continue
        if permute:
            s = s.assign(**{cols[0]: RNG.permutation(s[cols[0]].values)})
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s[outcome].values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


def boot_ci(b, n=5000):
    m = [np.mean(RNG.choice(b, len(b), replace=True)) for _ in range(n)]
    return np.percentile(m, [2.5, 97.5])


# ============================================================ NATURAL STORIES
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
                   "surprisal_gpt2_medium"),
                  (f"{GP}/extensions/gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl"),
                  (f"{GPC}/ns_pythia410m_surp_8a6087341e.csv",
                   "surprisal_pythia410m")]:
    S = S.merge(pd.read_csv(path)[["story_id", "word_idx", col]],
                on=["story_id", "word_idx"], how="left", validate="one_to_one")
KS = ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl",
      "surprisal_pythia410m"]
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
ns = rt.merge(S[["story_id", "zone", "tee_k3", "word_length", "log_freq"] + KS],
              on=["story_id", "zone"], how="inner")
ns["log_RT"] = np.log(ns.RT)
ns = ns.sort_values(["participant", "story_id", "zone"])
ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                       "prev_log_RT", "tee_k3"] + KS)
NSC = ["word_length", "log_freq", "zone", "prev_log_RT"]
print(f"Natural Stories: {len(ns):,} rows, {ns.participant.nunique()} participants")

ns_specs = [
    ("GPT-2 Small surprisal", ["tee_k3", "surprisal"] + NSC),
    ("GPT-2 XL surprisal", ["tee_k3", "surprisal_gpt2_xl"] + NSC),
    ("all four surprisals", ["tee_k3"] + KS + NSC),
]
NS_B = {lab: subj_betas(ns, "participant", cols, "log_RT", 300)
        for lab, cols in ns_specs}

def pooled_floor(df, subj, cols, outcome, minn, reps=10):
    """Permutation floor pooled over several shuffles. A single shuffle is too
    unstable to report: successive seeds moved the SAP floor between 48.6% and
    52.1% positive."""
    runs = [subj_betas(df, subj, cols, outcome, minn, permute=True)
            for _ in range(reps)]
    pos = [(r > 0).mean() for r in runs]
    print(f"    floor over {reps} shuffles: {np.mean(pos):.1%} positive "
          f"(range {min(pos):.1%}-{max(pos):.1%})")
    return np.concatenate(runs), np.mean(pos)


NS_PERM, NS_FLOOR = pooled_floor(ns, "participant",
                                 ["tee_k3", "surprisal"] + NSC, "log_RT", 300)

# ==================================================================== SAP
d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
M = pd.read_csv(f"{GPC}/sap_measures_L6k3.csv").merge(
    pd.read_csv(f"{GPC}/sap_bigsurp.csv"),
    on=["item", "Type", "WordPosition"], validate="one_to_one")
d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
d["word_length"] = d.EachWord.str.len()
d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
d["from_start"] = d.WordPosition.astype(float)
d["fs2"] = d.from_start ** 2
d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
d["fe2"] = d.from_end ** 2
d["is_final"] = (d.from_end == 0).astype(float)
d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
d["log_RT"] = np.log(d.RT)
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
print(f"SAP: {len(d):,} rows, {d.participant.nunique():,} participants")

LEX = ["word_length", "log_freq", "punct"]
POS = ["from_start", "fs2", "from_end", "fe2"]
sap_specs = [
    ("GPT-2 Small surprisal", ["tee", "surp"] + LEX + POS),
    ("+ sentence-final flag", ["tee", "surp"] + LEX + POS + ["is_final"]),
    ("all three surprisals", ["tee", "surp", "surp_xl", "surp_pythia410m"]
     + LEX + POS + ["is_final"]),
]
SAP_B = {lab: subj_betas(d, "participant", cols, "log_RT", 100)
         for lab, cols in sap_specs}
SAP_PERM, SAP_FLOOR = pooled_floor(d, "participant",
                                   ["tee", "surp"] + LEX + POS, "log_RT", 100)

# =================================================================== FIGURE
fig = plt.figure(figsize=(11.5, 6.4))
gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.45, wspace=0.28)

PANELS = [
    ("Natural Stories", NS_B["GPT-2 Small surprisal"], NS_PERM, NS_FLOOR,
     "178 participants"),
    ("Garden-path corpus", SAP_B["GPT-2 Small surprisal"], SAP_PERM, SAP_FLOOR,
     "2,000 participants"),
]
for i, (title, b, perm, floor, sub) in enumerate(PANELS):
    ax = fig.add_subplot(gs[i, 0])
    lo = np.percentile(np.concatenate([b, perm]), 0.5)
    hi = np.percentile(np.concatenate([b, perm]), 99.5)
    bins = np.linspace(lo, hi, 45)
    ax.hist(perm, bins=bins, color="0.78", alpha=.9,
            weights=np.full(len(perm), len(b) / len(perm)),
            label=f"shuffled ({floor:.0%} positive)")
    ax.hist(b, bins=bins, histtype="step", lw=2.0, color="#B03030",
            label=f"observed ({(b > 0).mean():.0%} positive)")
    ax.axvline(0, color="k", lw=.8)
    ax.axvline(b.mean(), color="#B03030", lw=1.4, ls="--")
    ax.set_title(f"{title}  ({sub})", fontsize=10.5, loc="left")
    ax.set_xlabel("per-participant standardised coefficient", fontsize=9)
    ax.set_ylabel("participants", fontsize=9)
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax.tick_params(labelsize=8)

ax = fig.add_subplot(gs[:, 1])
rows, ticks, labels, tcols, heads, y = [], [], [], [], [], 0.0
for corpus, D, colour in [("Natural Stories", NS_B, "#25506B"),
                          ("Garden-path corpus", SAP_B, "#B03030")]:
    heads.append((-y + 0.72, corpus, colour))
    for lab, b in D.items():
        rows.append((-y, b.mean(), boot_ci(b), colour))
        ticks.append(-y)
        labels.append(lab)
        tcols.append(colour)
        y += 1
    y += 1.5
for yy, m, ci, c in rows:
    ax.plot([ci[0], ci[1]], [yy, yy], color=c, lw=2.2,
            solid_capstyle="butt")
    ax.plot(m, yy, "o", color=c, ms=6.5, zorder=3)
ax.axvline(0, color="k", lw=.8)
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=8.5)
for t, c in zip(ax.get_yticklabels(), tcols):
    t.set_color(c)
ax.set_xlim(0, 0.032)
for yy, txt, c in heads:
    ax.text(0.0008, yy, txt, fontsize=9.5, color=c, weight="bold",
            ha="left", va="center")
ax.set_ylim(-y + 1.0, 1.4)
ax.set_xlabel("standardised coefficient\n(mean over participants, 95% CI)",
              fontsize=9)
ax.set_title("Effect under successively stronger\nsurprisal controls",
             fontsize=10.5, loc="left")
ax.tick_params(labelsize=8)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig(f"{GP}/arxiv_v2/fig_core.png", dpi=300)
print("\nwrote fig_core.png")
for lab, b in list(NS_B.items()) + list(SAP_B.items()):
    print(f"  {lab:<26} beta={b.mean():+.5f}  {(b > 0).mean():.1%} positive  "
          f"n={len(b)}")
print(f"  NS  permuted floor          {(NS_PERM > 0).mean():.1%} positive")
print(f"  SAP permuted floor          {(SAP_PERM > 0).mean():.1%} positive")
