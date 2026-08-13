"""
BRIDGE TEST: does uncertainty NOW predict extrapolation failure NEXT?
=====================================================================
King, Fedorenko & Hosseini: a bendy recent path leaves the model uncertain
about where to go next (curvature at k -> entropy at k).

If that is right, then when the model is uncertain it should also be a poorer
guide to where the representation actually lands. So:

    entropy at word t   should predict   TEE at word t+1

Neither paper makes this prediction. It links the prospective measure
(uncertainty about the next word) to the retrospective one (how far the
extrapolated heading missed).

Controls throughout: position + story fixed effects, punctuation at both t and
t+1, and the lexical properties of word t+1 (length, frequency) — because a
rare or long next word would inflate TEE for reasons unrelated to uncertainty.
The strict test also controls surprisal at t+1: entropy is uncertainty BEFORE
the word arrives, surprisal is how surprising it turned out to be. If entropy
predicts TEE only through surprisal, the bridge is not independent.

Locked sample 8a6087341e, GPT-2 small layer 6, cluster-robust SEs by sentence.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
S = S.merge(CUR[["story_id", "word_idx", "curvature_1", "curvature_3",
                 "tee3_par", "tee3_perp"]],
            on=["story_id", "word_idx"], validate="one_to_one")
S["punct"] = S.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
S = S.sort_values(["story_id", "word_idx"]).reset_index(drop=True)

# ---- build the t -> t+1 pairing (within story, strictly adjacent) ----
prev = S[["story_id", "word_idx", "entropy", "surprisal", "curvature_1",
          "curvature_3", "tee_k3", "punct", "log_freq", "word_length"]].copy()
prev.columns = ["story_id", "word_idx"] + [c + "_prev" for c in prev.columns[2:]]
prev["word_idx"] = prev["word_idx"] + 1          # align onto the NEXT word
D = S.merge(prev, on=["story_id", "word_idx"], how="inner")
print(f"hash {sh}   adjacent pairs: n = {len(D):,}")


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


for c in ["entropy_prev", "surprisal_prev", "curvature_1_prev", "curvature_3_prev",
          "tee_k3_prev", "punct_prev", "log_freq_prev", "word_length_prev",
          "tee_k3", "entropy", "surprisal", "log_freq", "word_length", "punct",
          "tee3_par", "tee3_perp", "curvature_3"]:
    D["z_" + c] = z(D[c].astype(float))

POS = "from_start + fs2 + from_end + fe2 + C(story_id)"


def fit(formula, label, term):
    m = smf.ols(formula, D).fit(cov_type="cluster",
                                cov_kwds={"groups": D["sent_uid"]})
    print(f"  {label:<52}{m.params[term]:>+9.4f}{m.pvalues[term]:>12.2e}")
    return m


print("\n" + "=" * 78)
print("BRIDGE: entropy at t  ->  TEE at t+1")
print("=" * 78)
print(f"  {'model':<52}{'beta':>9}{'p':>12}")
fit(f"z_tee_k3 ~ z_entropy_prev + {POS}",
    "raw (position + story FE only)", "z_entropy_prev")
fit(f"z_tee_k3 ~ z_entropy_prev + z_punct + z_punct_prev + {POS}",
    "+ punctuation at t and t-1", "z_entropy_prev")
fit(f"z_tee_k3 ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
    f"+ z_word_length + {POS}",
    "+ lexical properties of word t", "z_entropy_prev")
fit(f"z_tee_k3 ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
    f"+ z_word_length + z_surprisal + {POS}",
    "+ surprisal at t  (STRICT: is it independent?)", "z_entropy_prev")
fit(f"z_tee_k3 ~ z_entropy_prev + z_surprisal_prev + z_punct + z_punct_prev "
    f"+ z_log_freq + z_word_length + z_surprisal + {POS}",
    "+ surprisal at t-1 too", "z_entropy_prev")

print("\n" + "=" * 78)
print("SAME TEST WITH THEIR MEASURE: curvature at t-1 -> TEE at t")
print("(their claim is curvature -> entropy; this asks whether curvature also")
print(" forecasts the extrapolation failure directly)")
print("=" * 78)
print(f"  {'model':<52}{'beta':>9}{'p':>12}")
fit(f"z_tee_k3 ~ z_curvature_3_prev + z_punct + z_punct_prev + z_log_freq "
    f"+ z_word_length + {POS}", "curvature_3 at t-1 -> TEE at t", "z_curvature_3_prev")
fit(f"z_tee_k3 ~ z_curvature_1_prev + z_punct + z_punct_prev + z_log_freq "
    f"+ z_word_length + {POS}", "curvature_1 at t-1 -> TEE at t", "z_curvature_1_prev")
fit(f"z_tee_k3 ~ z_entropy_prev + z_curvature_3_prev + z_punct + z_punct_prev "
    f"+ z_log_freq + z_word_length + {POS}",
    "both: entropy_prev coefficient", "z_entropy_prev")
fit(f"z_tee_k3 ~ z_entropy_prev + z_curvature_3_prev + z_punct + z_punct_prev "
    f"+ z_log_freq + z_word_length + {POS}",
    "both: curvature_3_prev coefficient", "z_curvature_3_prev")

print("\n" + "=" * 78)
print("WHICH COMPONENT DOES UNCERTAINTY FORECAST? (par vs perp at t)")
print("=" * 78)
print(f"  {'model':<52}{'beta':>9}{'p':>12}")
fit(f"z_tee3_par ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
    f"+ z_word_length + {POS}", "entropy at t-1 -> along-heading (par) at t", "z_entropy_prev")
fit(f"z_tee3_perp ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
    f"+ z_word_length + {POS}", "entropy at t-1 -> lateral (perp) at t", "z_entropy_prev")

print("\n" + "=" * 78)
print("REVERSE DIRECTION (control): TEE at t -> entropy at t")
print("=" * 78)
print(f"  {'model':<52}{'beta':>9}{'p':>12}")
fit(f"z_entropy ~ z_tee_k3 + z_punct + z_log_freq + z_word_length + {POS}",
    "TEE at t -> entropy at t (same position)", "z_tee_k3")
print(f"\nAll results: hash = {sh}")
