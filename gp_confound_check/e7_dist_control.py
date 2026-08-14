"""
E7 -- analysis specified in PREREG_E7_distribution_sufficiency.md (commit
1e86015, before first run). Is the TEE-RT effect reducible to functionals of
the current next-token distribution?

Stage 1  distribution functionals (entropy, renyi2, top1, top10) from GPT-2
         Small logits at the word's FIRST subword, chunked convention;
         validated against the locked sample's existing entropy column.
Stage 2  Part A: headline model + functionals; pooled and subject-level.
Stage 3  Part B: quintile(surprisal) x quintile(entropy) x quintile(top1)
         cells; within-cell demeaning; subject-level TEE effect.
"""
import os, sys, hashlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from wordfreq import zipf_frequency

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import GP, GPC, load_stories, load_model, \
    chunk_states_and_logits

FUNC_CSV = f"{GPC}/e7_functionals_8a6087341e.csv"

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()
     ).hexdigest()[:10]
assert sh == "8a6087341e", sh

# ---------------- stage 1: functionals ----------------
if not os.path.exists(FUNC_CSV):
    texts = load_stories("ns")
    tok, model = load_model("gpt2", "cpu")
    rows = []
    for sid, text in texts.items():
        z = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
        first_sub = z["first_sub"]
        ids = tok(text)["input_ids"]
        _, logits_rows = chunk_states_and_logits(model, ids, 1, "cpu",
                                                 want_logits=True)
        for r in S[S.story_id == sid].itertuples():
            fs = int(first_sub[r.word_idx])
            if fs not in logits_rows:
                continue
            lg = logits_rows[fs].astype(np.float64)
            lg -= lg.max()
            p = np.exp(lg); p /= p.sum()
            ent = float(-(p * np.log(p + 1e-300)).sum())
            rows.append({"story_id": sid, "word_idx": r.word_idx,
                         "f_entropy": ent,
                         "f_renyi2": float(-np.log((p ** 2).sum())),
                         "f_top1": float(np.log(p.max())),
                         "f_top10": float(np.log(np.sort(p)[-10:].sum()))})
        print(f"story {sid} done", flush=True)
    pd.DataFrame(rows).to_csv(FUNC_CSV, index=False)

F = pd.read_csv(FUNC_CSV)
S = S.merge(F, on=["story_id", "word_idx"], how="inner", validate="one_to_one")
print(f"locked sample {sh}: {len(S):,} words with functionals")
r_nats = np.corrcoef(S.entropy, S.f_entropy)[0, 1]
r_bits = np.corrcoef(S.entropy, S.f_entropy / np.log(2))[0, 1]
print(f"VALIDATION vs sample entropy column: r = {max(r_nats, r_bits):.4f} "
      f"({'nats' if r_nats >= r_bits else 'bits'})")

print("\nCorrelation matrix (prereg: reported before any model):")
cm = S[["tee_k3", "surprisal", "f_entropy", "f_renyi2", "f_top1",
        "f_top10"]].corr().round(3)
print(cm.to_string())
if (cm.loc["tee_k3"].drop("tee_k3").abs() > .9).any():
    print("NOTE: |r| > .9 with TEE present; reported, model still run.")

# ---------------- RT data, headline spec ----------------
S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                "log_freq_fixed", "f_entropy", "f_renyi2", "f_top1",
                "f_top10"]], on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
BASE_COLS = ["word_length", "log_freq_fixed", "zone", "prev_log_RT",
             "surprisal"]
FUNCS = ["f_entropy", "f_renyi2", "f_top1", "f_top10"]
D = d.dropna(subset=["log_RT", "tee_k3"] + BASE_COLS + FUNCS).copy()


def z(s):
    v = s.dropna(); return (s - v.mean()) / v.std()


for c in BASE_COLS + FUNCS + ["tee_k3"]:
    D["z_" + c] = z(D[c])
print(f"\nRT rows: {len(D):,}   participants {D.participant.nunique()}")


def zs(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def subj_criterion(frame, ycol, xcol, covcols, minn=100, label=""):
    betas = []
    for pid, s in frame.groupby("participant"):
        s = s.dropna(subset=[ycol, xcol] + covcols)
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in [xcol] + covcols])
        if (X.std(axis=0) == 0).any():
            continue
        X = np.column_stack([np.ones(len(s)), X])
        b, *_ = np.linalg.lstsq(X, s[ycol].values, rcond=None)
        betas.append(b[1])
    betas = np.array(betas)
    pos = (betas > 0).mean()
    w = stats.wilcoxon(betas)
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"  {label}: n_subj {len(betas)}  mean beta {betas.mean():+.5f}  "
          f"%pos {pos:.1%}  Wilcoxon p {w.pvalue:.2e}  "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok, len(betas)


print("\n" + "=" * 72)
print("PART A  TEE WITH DISTRIBUTION FUNCTIONALS IN THE MODEL")
print("=" * 72)
BASE = ("log_RT ~ z_word_length + z_log_freq_fixed + z_zone + z_prev_log_RT"
        " + z_surprisal")
FULL = BASE + " + z_f_entropy + z_f_renyi2 + z_f_top1 + z_f_top10"
for lab, f in [("headline (no functionals)", BASE),
               ("with functionals", FULL)]:
    m0 = smf.mixedlm(f, D, groups=D.participant).fit(reml=False,
                                                     method="lbfgs")
    m1 = smf.mixedlm(f + " + z_tee_k3", D, groups=D.participant
                     ).fit(reml=False, method="lbfgs")
    print(f"  {lab:<26} dAIC(TEE) {m0.aic - m1.aic:>7.1f}   "
          f"beta {m1.params['z_tee_k3']:+.5f}   "
          f"p {m1.pvalues['z_tee_k3']:.2e}")
print("\n  subject-level (CRITERION A):")
subj_criterion(D, "log_RT", "tee_k3", BASE_COLS, label="no functionals ")
okA, _ = subj_criterion(D, "log_RT", "tee_k3", BASE_COLS + FUNCS,
                        label="with functionals")

print("\n" + "=" * 72)
print("PART B  WITHIN DISTRIBUTION-MATCHED CELLS (quintile s x H x top1)")
print("=" * 72)
for c, qc in [("surprisal", "q_s"), ("f_entropy", "q_h"), ("f_top1", "q_t")]:
    D[qc] = pd.qcut(D[c], 5, labels=False, duplicates="drop")
D["cell"] = (D.q_s.astype(int) * 25 + D.q_h.astype(int) * 5
             + D.q_t.astype(int))
dm_cols = ["log_RT", "tee_k3", "word_length", "log_freq_fixed", "zone",
           "prev_log_RT"]
for c in dm_cols:
    D["dm_" + c] = D[c] - D.groupby("cell")[c].transform("mean")
med_n = D.groupby("participant").size().median()
print(f"  cells: {D.cell.nunique()}   median obs/participant {med_n:.0f}")
okB, nB = subj_criterion(
    D, "dm_log_RT", "dm_tee_k3",
    ["dm_" + c for c in dm_cols[2:]], label="within-cell TEE ")
under = med_n < 100

print("\n" + "=" * 72)
print("PREREGISTERED OUTCOME")
print("=" * 72)
if okA and okB and not under:
    print("  1: A and B pass -> cost tracks trajectory BEYOND the current"
          " distribution.")
elif okA and under:
    print("  4: A passes, B underpowered -> claim rests on A.")
elif okA:
    print("  2: A passes, B fails -> limited claim; H-dist/H-hist open.")
else:
    print("  3: A fails -> TEE-RT effect reducible to distribution shape;"
          " reinterpret the measure.")
