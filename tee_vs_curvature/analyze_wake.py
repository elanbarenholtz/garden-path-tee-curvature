"""
Does a reorientation leave a causal downstream wake in the model, beyond
surprisal, and how far does it persist? Regress wake(w,L) on w's channels.

For each lag L in 1..5:
  wake_rel_L ~ tee3_perp(w) + tee3_par(w) + surprisal(w) + word_length(w)
             + log_freq(w) + has_trailing_punct(w)
             + surprisal(w+L) + word_length(w+L) + log_freq(w+L)   [target controls]
             + from_start + fs2 + from_end + fe2 + C(story_id)
z-scored (ddof=0); cluster-robust SE by sent_uid(w). Also punct-free (w not
punct-final). Read: if perp/par predict wake only at small L and vanish by
L3+, the reorientation footprint is short-range (matches behavior). If they
persist to L4/L5 beyond surprisal, there is a long-range model-internal wake
that self-paced RT could not see.
"""
import sys, hashlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

GP = "/Users/elansmini/Research/Garden_Path"
WAKE = sys.argv[1] if len(sys.argv) > 1 else f"{GP}/tee_vs_curvature/wake_step6.csv"
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
W = pd.read_csv(WAKE)
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id","word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

F = S.merge(CUR[["story_id","word_idx","tee3_par","tee3_perp"]],
            on=["story_id","word_idx"], validate="one_to_one")
F["has_trailing_punct"] = F["word"].astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)

# w features
base = F[["story_id","word_idx","sent_uid","tee3_par","tee3_perp","surprisal",
          "word_length","log_freq","has_trailing_punct",
          "from_start","fs2","from_end","fe2"]]
D = W.merge(base, on=["story_id","word_idx"], validate="one_to_one")

# target (w+L) controls, merged per L
tgt = F[["story_id","word_idx","surprisal","word_length","log_freq"]]
for L in range(1, 6):
    t = tgt.rename(columns={"word_idx":"wl","surprisal":f"tsurp_{L}",
                            "word_length":f"tlen_{L}","log_freq":f"tfreq_{L}"})
    t["word_idx"] = t["wl"] - L
    D = D.merge(t[["story_id","word_idx",f"tsurp_{L}",f"tlen_{L}",f"tfreq_{L}"]],
                on=["story_id","word_idx"], how="left")
print(f"SAMPLE: hash = {sh}   wake words n = {len(D)}   file = {WAKE.split('/')[-1]}")
npc = int(D.has_trailing_punct.sum())
print(f"punct-final targets: {npc} / {len(D)-npc} non-punct\n")

def z(s): return (s - s.mean())/s.std(ddof=0)
def fit(f, d): return smf.ols(f, d).fit(cov_type="cluster",
                                        cov_kwds={"groups": d["sent_uid"]})
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"

def run(dat, label):
    print("="*70); print(label); print("="*70)
    print(f"{'lag':4s} {'perp beta':>18s} {'par beta':>18s} {'surprisal(w)':>18s}")
    for L in range(1, 6):
        d = dat.dropna(subset=[f"wake_rel_{L}",f"tsurp_{L}",f"tlen_{L}",f"tfreq_{L}"]).copy()
        for c in ["tee3_perp","tee3_par","surprisal","word_length","log_freq",
                  "has_trailing_punct",f"tsurp_{L}",f"tlen_{L}",f"tfreq_{L}",
                  f"wake_rel_{L}"]:
            d[c] = z(d[c])
        pf = " + has_trailing_punct" if dat is D else ""
        m = fit(f"wake_rel_{L} ~ tee3_perp + tee3_par + surprisal + word_length"
                f" + log_freq{pf} + {f'tsurp_{L}'} + {f'tlen_{L}'} + {f'tfreq_{L}'}"
                f" + {CTRL}", d)
        def cell(k):
            b,p = m.params[k], m.pvalues[k]
            return f"{b:+.4f}({p:.1e}){'*' if p<.05 else ' '}"
        print(f"L{L:<3d} {cell('tee3_perp'):>18s} {cell('tee3_par'):>18s} "
              f"{cell('surprisal'):>18s}   n={int(m.nobs)}")
    print()

run(D, "FULL: causal wake_rel(w,L) ~ perp + par + surprisal(w) + controls")
run(D[D.has_trailing_punct==0].reset_index(drop=True),
    "PUNCT-FREE (w not punct-final; drops punct term)")
print(f"All results: hash = {sh}")
