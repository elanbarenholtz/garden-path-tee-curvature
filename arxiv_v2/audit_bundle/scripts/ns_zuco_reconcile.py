"""
RECONCILING THE ZUCO NULL WITH THE NATURAL STORIES EFFECT
=========================================================
Two candidate explanations, both testable on Natural Stories alone:

  POWER    -- ZuCo has 10 subjects; Natural Stories has 171, of which only ~23%
              are individually significant. Subsample Natural Stories down to 10
              participants and ask how often the group test would detect the
              effect. If it is near ZuCo's hit rate, power explains the null.

  POSITION -- ZuCo uses short isolated sentences; Natural Stories are long
              connected narratives. The TEE effect is weakest at sentence-initial
              positions. Restrict Natural Stories to ZuCo-like material (early
              positions / short sentences) and see whether it approaches null.

Both use subject-level inference throughout (one beta per participant, group
test across participants) to match the ZuCo standard.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
PUNCT = set(".,;:!?\"'`)(-—")
COLS = ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"]
RNG = np.random.default_rng(20260727)


def build():
    w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    w["punct_final"] = w.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
    rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                     sep="\t").rename(columns={"item": "story_id",
                                               "WorkerId": "participant"})
    rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
    m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                    "log_freq", "punct_final", "from_start", "sent_len"]],
                 on=["story_id", "zone"], how="inner")
    m["log_RT"] = np.log(m.RT)
    m = m.sort_values(["participant", "story_id", "zone"])
    m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
    return m


def per_subject(d, min_n=100):
    out = []
    for pid, sub in d.groupby("participant"):
        s = sub.dropna(subset=COLS + ["log_RT"])
        if len(s) < min_n:
            continue
        X = s[COLS].astype(float)
        sd = X.std(ddof=0)
        if (sd == 0).any():
            continue
        X = (X - X.mean()) / sd
        X = sm.add_constant(X)
        r = sm.OLS(s.log_RT.values, X.values).fit()
        out.append({"participant": pid, "n": len(s),
                    "beta": r.params[-1], "p": r.pvalues[-1]})
    return pd.DataFrame(out)


def group(B, label):
    if len(B) < 5:
        print(f"  {label:<44} too few participants")
        return None
    w = stats.wilcoxon(B.beta)
    pos = int((B.beta > 0).sum())
    print(f"  {label:<44} n={len(B):>4}  pos={pos:>3}/{len(B):<4}"
          f"  mean b={B.beta.mean():+.5f}  Wilcoxon p={w.pvalue:.2e}"
          f"  sig={int((B.p<.05).sum())}")
    return w.pvalue


def main():
    d = build()
    print(f"rows={len(d):,}  participants={d.participant.nunique()}\n")

    # ---------------- POSITION ----------------
    print("=" * 92)
    print("POSITION: is the effect weaker on ZuCo-like material? "
          "(subject-level inference throughout)")
    print("=" * 92)
    print("\nby position from sentence start:")
    bins = [("first 5 words", d[d.from_start <= 4]),
            ("first 10 words", d[d.from_start <= 9]),
            ("beyond word 10", d[d.from_start > 9])]
    for lab, sub in bins:
        group(per_subject(sub), lab)

    print("\nby sentence length (ZuCo sentences are short/isolated):")
    for lab, sub in [("short sentences (<=15 words)", d[d.sent_len <= 15]),
                     ("medium (16-25)", d[(d.sent_len > 15) & (d.sent_len <= 25)]),
                     ("long (>25)", d[d.sent_len > 25])]:
        group(per_subject(sub), lab)

    print("\nmost ZuCo-like slice (short sentences AND first 10 words):")
    zl = d[(d.sent_len <= 15) & (d.from_start <= 9)]
    group(per_subject(zl, min_n=50), "short & early")

    # ---------------- POWER ----------------
    print("\n" + "=" * 92)
    print("POWER: how often would a 10-participant study detect this effect?")
    print("=" * 92)
    B_full = per_subject(d)
    B_zuco = per_subject(zl, min_n=50)
    for label, B in [("full corpus", B_full), ("ZuCo-like slice", B_zuco)]:
        if B is None or len(B) < 10:
            continue
        hits = []
        for _ in range(4000):
            s = B.sample(10, replace=False, random_state=RNG.integers(1 << 31))
            hits.append(stats.wilcoxon(s.beta).pvalue < .05)
        print(f"  {label:<20} detection rate with n=10 subjects: "
              f"{np.mean(hits):.1%}   (ZuCo observed: 0/3 measures significant, "
              f"p = .065-.160)")


if __name__ == "__main__":
    main()
