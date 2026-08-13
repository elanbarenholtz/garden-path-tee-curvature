"""
TWO REMAINING BLOCKERS FOR v2
=============================
(A) v1 paragraph 47 (manuscript.tex line 298): the claim about WHICH WORDS
    populate the off-diagonal cells of the surprisal x TEE tercile matrix.
    v1 asserts:
      low-surprisal / high-TEE  -> coordinators and complementizers
                                   ("and", "as", "that", "had")
      high-surprisal / low-TEE  -> rare content words ("ocean", "manor", "tics")
                                   plus discourse pivots ("then", "however",
                                   "now", "first")
    Tercile membership changed when the measure pipeline was rebuilt, so this
    paragraph's content is stale and must be recomputed or dropped.

(B) v1's r = .044 orthogonality claim (abstract, line 129, line 278, Table 5,
    and the Pythia values .046/.047 at line 247). On the verified pipeline
    r(TEE, surprisal) = +0.310, while r(TEE, entropy) = +0.043. The suspicion is
    that .044 was the ENTROPY correlation, mislabelled. This script tries to
    falsify that: it sweeps TEE variants (layers, window sizes, normalised
    forms) and correlation types, asking whether ANY plausible TEE-vs-surprisal
    configuration lands near .044. If none does and entropy does, mislabelling
    is the parsimonious explanation and v2 should say so.

Locked sample 8a6087341e throughout, hash asserted.
"""

import numpy as np
import pandas as pd
from scipy import stats
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
print(f"locked sample {sh}   {len(S):,} words")
print(f"columns available: {[c for c in S.columns][:40]}\n")

# =============================================================== (B) the r=.044
print("=" * 78)
print("(B) WHERE DOES r = .044 COME FROM?")
print("=" * 78)

cand = [c for c in S.columns
        if c.startswith("tee") or c.startswith("teeN") or c == "curvature_3"]
print(f"TEE-like columns in the locked sample: {cand}\n")

print(f"{'measure':<16}{'r(x, surprisal)':>18}{'Spearman':>12}"
      f"{'r(x, entropy)':>16}")
hits = []
for c in cand:
    if S[c].notna().sum() < 100:
        continue
    both = S[[c, "surprisal"]].dropna()
    r = both[c].corr(both.surprisal)
    rho = stats.spearmanr(both[c], both.surprisal).statistic
    re_ = S[[c, "entropy"]].dropna().corr().iloc[0, 1] if "entropy" in S else np.nan
    print(f"{c:<16}{r:>18.4f}{rho:>12.4f}{re_:>16.4f}")
    if abs(r - .044) < .015:
        hits.append((c, "pearson-surprisal", r))
    if abs(rho - .044) < .015:
        hits.append((c, "spearman-surprisal", rho))
    if not np.isnan(re_) and abs(re_ - .044) < .015:
        hits.append((c, "pearson-entropy", re_))

# also try the extensions files, which hold other layers/models
import os
for f, note in [("extensions/nonlinear_tee_8a6087341e.csv", "nonlinear variants"),
                ("extensions/coarse_tee_8a6087341e.csv", "coarse/normalised"),
                ("gp_confound_check/pythia_tee_8a6087341e.csv", "pythia")]:
    p = f"{GP}/{f}"
    if not os.path.exists(p):
        continue
    E = pd.read_csv(p)
    if "surprisal" not in E.columns:
        E = E.merge(S[["story_id", "word_idx", "surprisal"]],
                    on=["story_id", "word_idx"], how="left")
    ec = [c for c in E.columns if ("tee" in c.lower() or "curv" in c.lower())]
    for c in ec:
        b = E[[c, "surprisal"]].dropna()
        if len(b) < 100:
            continue
        r = b[c].corr(b.surprisal)
        if abs(r - .044) < .015:
            hits.append((f"{c} [{note}]", "pearson-surprisal", r))

print("\nvalues landing within .015 of .044:")
if hits:
    for h in hits:
        print(f"  {h[0]:<34}{h[1]:<22}{h[2]:+.4f}")
else:
    print("  none")

print("\nVERDICT (B):")
r_surp = S.tee_k3.corr(S.surprisal)
r_ent = S.tee_k3.corr(S.entropy)
print(f"  headline measure tee_k3:  r(surprisal) = {r_surp:+.4f}   "
      f"r(entropy) = {r_ent:+.4f}")
if abs(r_ent - .044) < .005 and abs(r_surp - .044) > .1:
    print("  The entropy correlation reproduces .044 to within .005 while the")
    print("  surprisal correlation is nowhere near it. Mislabelling in the v1")
    print("  pipeline is the parsimonious account. v2 should state this.")

# ====================================================== (A) off-diagonal cells
print("\n" + "=" * 78)
print("(A) COMPOSITION OF THE OFF-DIAGONAL CELLS, RECOMPUTED")
print("=" * 78)

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
# NOTE: processed_RTs.tsv has its own `word` column, so the sample's word form
# is renamed before merging. An unsuffixed merge silently produces word_x/word_y
# and has bitten this project before.
d = rt.merge(S[["story_id", "zone", "word", "tee_k3", "surprisal",
                "word_length", "log_freq"]].rename(columns={"word": "wordform"}),
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                     "prev_log_RT", "surprisal", "tee_k3"])
d["s_t"] = pd.qcut(d.surprisal, 3, labels=["low", "mid", "high"])
d["e_t"] = pd.qcut(d.tee_k3, 3, labels=["low", "mid", "high"])
print(f"analysis rows {len(d):,}   participants {d.participant.nunique()}")

# composition over DISTINCT WORD TOKENS (each corpus position counted once),
# using the tercile assignment from the RT sample
W = d.drop_duplicates(subset=["story_id", "zone"])[
    ["story_id", "zone", "wordform", "s_t", "e_t", "surprisal", "tee_k3",
     "log_freq"]].copy()
W["w"] = W.wordform.astype(str).str.lower().str.strip(".,;:!?\"'")
print(f"distinct corpus positions in the matrix: {len(W):,}\n")

overall = W.w.value_counts(normalize=True)

FUNCTION = set("""the a an and or but so as that which who whom whose if then
than of to in on at by for with from into over under about after before while
when where because since although though unless until is was were are be been
being have has had do does did will would can could shall should may might must
not no nor it its he she they them his her their we us our you your i me my this
these those there here""".split())


def profile(s_lab, e_lab, title, n=25):
    cell = W[(W.s_t == s_lab) & (W.e_t == e_lab)]
    print("-" * 78)
    print(f"{title}   n = {len(cell):,} corpus positions, "
          f"{cell.w.nunique():,} word types")
    print(f"  mean surprisal {cell.surprisal.mean():.2f}   "
          f"mean TEE {cell.tee_k3.mean():.1f}   "
          f"mean log freq {cell.log_freq.mean():.2f}")
    fn = cell.w.isin(FUNCTION).mean()
    fn_all = W.w.isin(FUNCTION).mean()
    print(f"  closed-class share {fn:.1%}  (corpus overall {fn_all:.1%})")
    vc = cell.w.value_counts()
    print(f"\n  most frequent words in the cell:")
    print("   ", ", ".join(f"{w} ({c})" for w, c in vc.head(n).items()))
    # enrichment: cell rate / corpus rate, for words with enough support
    sub = vc[vc >= 5]
    enr = (sub / sub.sum()) / overall.reindex(sub.index)
    enr = enr.dropna().sort_values(ascending=False)
    print(f"\n  most ENRICHED words (count >= 5, cell rate / corpus rate):")
    print("   ", ", ".join(f"{w} ({e:.1f}x)" for w, e in enr.head(n).items()))
    print()
    return cell


print("\nv1 claimed: low-surprisal / high-TEE is enriched for coordinators and")
print("complementizers ('and', 'as', 'that', 'had').")
c1 = profile("low", "high", "LOW SURPRISAL / HIGH TEE")

print("v1 claimed: high-surprisal / low-TEE holds rare content words ('ocean',")
print("'manor', 'tics') and discourse pivots ('then', 'however', 'now', 'first').")
c2 = profile("high", "low", "HIGH SURPRISAL / LOW TEE")

print("=" * 78)
print("CHECK OF v1'S SPECIFIC EXAMPLES ON THE VERIFIED SAMPLE")
print("=" * 78)
claims = {"low/high (coordinators/complementizers)":
          (("low", "high"), ["and", "as", "that", "had"]),
          "high/low (rare content + pivots)":
          (("high", "low"), ["ocean", "manor", "tics", "then", "however",
                             "now", "first"])}
for lab, ((s_lab, e_lab), wl) in claims.items():
    print(f"\n{lab}:")
    for w in wl:
        tot = (W.w == w).sum()
        inc = ((W.w == w) & (W.s_t == s_lab) & (W.e_t == e_lab)).sum()
        share = inc / tot if tot else np.nan
        base = len(W[(W.s_t == s_lab) & (W.e_t == e_lab)]) / len(W)
        print(f"  {w:<10} {inc:>4}/{tot:<4} occurrences in cell "
              f"({share:5.1%}, chance {base:.1%})"
              f"{'   ENRICHED' if tot and share > 1.5 * base else ''}")
