"""
EXTENSIONS AUDIT: does the ntee_k100 long-range wake survive TARGET controls?
============================================================================
The parent wake analysis (tee_vs_curvature/analyze_wake.py) controls properties
of the word being perturbed AT LAG L -- surprisal(w+L), length(w+L), freq(w+L) --
on the reasoning that a high-surprisal target has a more volatile state and will
show a larger relative change for any perturbation.

The extensions version (extensions/x3b_analyze_wake.py), which produced the
headline claim that neighborhood TEE has a causal wake at every lag 1-10, does
NOT include those target controls. This script adds them back and reports both.

Same conventions otherwise: z-scored (ddof=0), position + story FE,
cluster-robust SE by sent_uid, punct-free pass.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
MAXL = 10

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
CTEE = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")

S["has_trailing_punct"] = S["word"].astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
D = W.merge(S, on=["story_id", "word_idx"], validate="one_to_one")
D = D.merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp"]],
            on=["story_id", "word_idx"], validate="one_to_one")
D = D.merge(CTEE[["story_id", "word_idx", "ctee_m5", "ntee_k100"]],
            on=["story_id", "word_idx"], validate="one_to_one")

# target (w+L) properties
tgt = S[["story_id", "word_idx", "surprisal", "word_length", "log_freq"]]
for L in range(1, MAXL + 1):
    t = tgt.rename(columns={"word_idx": "wl", "surprisal": f"tsurp_{L}",
                            "word_length": f"tlen_{L}", "log_freq": f"tfreq_{L}"})
    t["word_idx"] = t["wl"] - L
    D = D.merge(t[["story_id", "word_idx", f"tsurp_{L}", f"tlen_{L}", f"tfreq_{L}"]],
                on=["story_id", "word_idx"], how="left")

print(f"SAMPLE hash={sh}  wake n={len(D)}  punct-final={int(D.has_trailing_punct.sum())}")

PRED = ["tee3_perp", "tee3_par", "surprisal", "ctee_m5", "ntee_k100",
        "word_length", "log_freq"]
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


def run(dat, fam, with_target, label):
    print(f"\n{'='*78}\n{label} | DV={fam} | target controls: "
          f"{'YES' if with_target else 'NO (as published)'}\n{'='*78}")
    print(f"{'lag':>4}{'ntee_k100':>20}{'tee3_perp':>20}{'surprisal(w)':>20}{'n':>7}")
    for L in range(1, MAXL + 1):
        dv = f"{fam}_{L}"
        tc = [f"tsurp_{L}", f"tlen_{L}", f"tfreq_{L}"] if with_target else []
        need = [dv] + PRED + tc
        d = dat.dropna(subset=need).copy()
        if len(d) < 200:
            continue
        for c in PRED + tc + [dv]:
            d[c] = z(d[c])
        terms = PRED + tc
        m = smf.ols(f"{dv} ~ {' + '.join(terms)} + {CTRL}", d).fit(
            cov_type="cluster", cov_kwds={"groups": d["sent_uid"]})

        def cell(k):
            b, p = m.params[k], m.pvalues[k]
            return f"{b:+.4f}({p:.1e}){'*' if p < .05 else ' '}"
        print(f"L{L:<3d}{cell('ntee_k100'):>20}{cell('tee3_perp'):>20}"
              f"{cell('surprisal'):>20}{int(m.nobs):>7}")


Dpf = D[D.has_trailing_punct == 0].reset_index(drop=True)
for fam in ["wake_rel", "wake_coarse"]:
    run(Dpf, fam, False, "PUNCT-FREE")
    run(Dpf, fam, True, "PUNCT-FREE")
