"""
x15: HUMAN event-boundary validation on HippoCorpus (Wang, Jafarpour & Sap
2022, story_events repo; 240 diary stories, 3925 sentences, 8 crowdworker
event-boundary labels each). Does deep neighborhood TEE predict HUMAN event
boundaries better than surprisal and fine TEE?

Pipeline (GPT-2 small, matching the parent conventions):
  - reconstruct each story from its ordered sentences; whitespace words.
  - GPT-2 forward (chunk 1024/stride 512, first-write-wins); per word: layer-6
    and layer-9 final-subword anchor states, model surprisal (sum subword
    NLL), entropy (at the position predicting the word's first subword),
    fine tee_k3 (layer 6).
  - deep neighborhood TEE ntee9 = k=3 extrapolation error on the sqrt-soft
    k-means (k=100, layer 9) assignment trajectory; also ntee6. All-story fit
    (primary) + leave-half-out held-out fit (leakage-safe robustness).
  - aggregate to the sentence: ntee9_first (sentence-initial word = the
    transition INTO the sentence; the boundary anchor), plus sentence means.
Human labels per sentence:
  boundary_prop = fraction of 8 annotators marking any event (expected or
    surprising); human_bnd = majority label != noEvent; surprising_prop.
Tests (cluster-robust by story):
  T1 logistic human_bnd ~ z(ntee9_first)+z(surprisal)+z(entropy)+z(tee6)
     +z(nwords); AUC per predictor.
  T2 graded OLS boundary_prop ~ same.
  T3 held-out ntee9 rerun of T1.
"""
import os, sys, ast
import numpy as np
import pandas as pd
import torch
import statsmodels.formula.api as smf
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
DATA = "/tmp/story_events/data/" \
       "all_features_including_annotations_prev_sent_with_prior_confidence.csv"
RES = f"{GP}/extensions/results"
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
CHUNK, STRIDE = 1024, 512

d = pd.read_csv(DATA)
d["sentence"] = d["sentence"].astype(str)
stories = list(dict.fromkeys(d.story_ids.tolist()))
print(f"{len(d)} sentences, {len(stories)} stories on {DEV}", flush=True)

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEV)

def zscore(s):
    return (s - np.nanmean(s)) / np.nanstd(s)

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

# ---- per-story forward pass; collect word-level records ----
records = []          # one row per word
anchors6, anchors9 = [], []
for si, sid in enumerate(stories):
    sub = d[d.story_ids == sid]
    sent_words, sent_idx = [], []
    for j, s in enumerate(sub.sentence.tolist()):
        ws = s.split()
        sent_words += ws; sent_idx += [j] * len(ws)
    if not sent_words:
        continue
    text = " ".join(sent_words)
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offs = enc["offset_mapping"]
    n = ids.size(0)
    h6, h9, ent, logp = {}, {}, {}, {}
    pos = 0
    while pos < n:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0).to(DEV),
                        output_hidden_states=True)
            hs6 = out.hidden_states[6][0].float().cpu().numpy()
            hs9 = out.hidden_states[9][0].float().cpu().numpy()
            lsm = torch.log_softmax(out.logits[0].float(), -1).cpu()
        for i in range(end - pos):
            g = pos + i
            if g not in h6:
                h6[g] = hs6[i]; h9[g] = hs9[i]
                ent[g] = float(-(lsm[i].exp() * lsm[i]).sum())
            if i < end - pos - 1:
                nx = int(ids[g + 1])
                if (g + 1) not in logp:
                    logp[g + 1] = float(lsm[i, nx])
        del out
        if end >= n:
            break
        pos += STRIDE
    # char spans of words
    spans, cur = [], 0
    for w in sent_words:
        spans.append((cur, cur + len(w))); cur += len(w) + 1
    bpe_word = np.full(n, -1); wi = 0
    for bi, (cs, ce) in enumerate(offs):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            bpe_word[bi] = wi
    first_sub = {}; last_sub = {}
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            first_sub.setdefault(w, bi); last_sub[w] = bi
    base = len(anchors6)
    for w in range(len(sent_words)):
        ls = last_sub.get(w); fs = first_sub.get(w)
        if ls is None:
            anchors6.append(np.zeros(768)); anchors9.append(np.zeros(768))
            records.append(None); continue
        anchors6.append(h6[ls]); anchors9.append(h9[ls])
        srp = np.nan if fs == 0 else \
            -sum(logp.get(b, np.nan) for b in range(fs, ls + 1))
        records.append({"sid": sid, "sent": sent_idx[w], "w_in_story": w,
                        "row6": base + w, "surprisal": srp,
                        "entropy": ent.get(fs, np.nan),
                        "wlen": len(sent_words[w])})
    if si % 40 == 0:
        print(f"  story {si}/{len(stories)}", flush=True)

A6 = np.stack(anchors6); A9 = np.stack(anchors9)
R = pd.DataFrame([r for r in records if r is not None]).reset_index(drop=True)
print(f"words: {len(R)}; states {A9.shape}", flush=True)

# ---- fine tee_k3 (layer 6) + ntee per word, within-story trajectories ----
def compute_ntee(states, fit_mask=None, seed=0):
    """k=100 soft-assignment trajectory TEE per word, within story order."""
    fit = states if fit_mask is None else states[fit_mask]
    km = KMeans(n_clusters=100, n_init=4, random_state=seed).fit(fit)
    sig = float(np.median(km.transform(fit).min(1)))   # memory-safe
    dd = km.transform(states)                          # (n, 100) distances
    p = np.exp(-(dd ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
    return np.sqrt(p)

R["rowidx"] = R.row6.values
SQ9 = compute_ntee(A9)
SQ6 = compute_ntee(A6)
tee6, ntee9, ntee6 = [], [], []
for sid in stories:
    idx = R.index[R.sid == sid].tolist()
    if not idx:
        continue
    rows = R.loc[idx, "rowidx"].values
    H6 = A6[rows]; s9 = SQ9[rows]; s6 = SQ6[rows]
    for j in range(len(idx)):
        tee6.append(lin_err(H6, j, 3))
        ntee9.append(lin_err(s9, j, 3))
        ntee6.append(lin_err(s6, j, 3))
R["tee6"] = tee6; R["ntee9"] = ntee9; R["ntee6"] = ntee6

# leave-half-out held-out ntee9 (fit on even-indexed stories, etc.)
story_half = {s: (i % 2) for i, s in enumerate(stories)}
R["half"] = R.sid.map(story_half)
ntee9_ho = np.full(len(R), np.nan)
for h in (0, 1):
    fit_rows = R.index[R.half != h].to_list()
    fitA = A9[R.loc[fit_rows, "rowidx"].values]
    km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(fitA)
    sig = float(np.median(km.transform(fitA).min(1)))
    for sid in [s for s in stories if story_half[s] == h]:
        idx = R.index[R.sid == sid].tolist()
        rows = R.loc[idx, "rowidx"].values
        dd = km.transform(A9[rows])
        p = np.exp(-(dd ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
        sq = np.sqrt(p)
        for j, ii in enumerate(idx):
            ntee9_ho[ii] = lin_err(sq, j, 3)
R["ntee9_ho"] = ntee9_ho

# ---- aggregate to sentence ----
def agg(df):
    g = df.sort_values("w_in_story")
    return pd.Series({
        "ntee9_first": g.ntee9.iloc[0] if len(g) else np.nan,
        "ntee9_ho_first": g.ntee9_ho.iloc[0] if len(g) else np.nan,
        "ntee6_first": g.ntee6.iloc[0] if len(g) else np.nan,
        "ntee9_mean": g.ntee9.mean(), "tee6_mean": g.tee6.mean(),
        "surprisal": g.surprisal.mean(), "entropy": g.entropy.mean(),
        "nwords": len(g)})
SENT = R.groupby(["sid", "sent"]).apply(agg).reset_index()

# ---- human labels ----
d2 = d.copy()
d2["sent"] = d2.groupby("story_ids").cumcount()
d2 = d2.rename(columns={"story_ids": "sid"})
def blab(s):
    labs = ast.literal_eval(s)
    return (np.mean([l != "noEvent" for l in labs]),
            np.mean([l == "major-surprising" for l in labs]))
bp = d2.uncollated_annotation.apply(blab)
d2["boundary_prop"] = [x[0] for x in bp]
d2["surprising_prop"] = [x[1] for x in bp]
d2["human_bnd"] = (d2.surprise_annotation != "noEvent").astype(float)
M = SENT.merge(d2[["sid", "sent", "boundary_prop", "surprising_prop",
                   "human_bnd"]], on=["sid", "sent"])
M = M.dropna(subset=["ntee9_first", "surprisal", "tee6_mean"]) \
    .reset_index(drop=True)
M.to_csv(f"{RES}/x15_hippocorpus_sentences.csv", index=False)
print(f"\nmerged sentences with features + human labels: n={len(M)}; "
      f"human boundary rate={M.human_bnd.mean():.2f}", flush=True)

PRED = ["ntee9_first", "surprisal", "entropy", "tee6_mean", "nwords"]
Z = M.copy()
for c in PRED + ["ntee9_ho_first", "boundary_prop", "surprising_prop"]:
    Z[c] = zscore(M[c])

def clus(formula, data, logit=False):
    f = smf.logit if logit else smf.ols
    return f(formula, data=data).fit(disp=0, cov_type="cluster",
        cov_kwds={"groups": data["sid"]}) if logit else \
        f(formula, data=data).fit(cov_type="cluster",
        cov_kwds={"groups": data["sid"]})

print("\nT1 logistic: human_bnd ~ deep ntee + surprisal + entropy + fine TEE"
      " + nwords")
m1 = clus("human_bnd ~ ntee9_first + surprisal + entropy + tee6_mean"
          " + nwords", Z, logit=True)
for t in PRED:
    print(f"  {t:14s} b={m1.params[t]:+.3f} p={m1.pvalues[t]:.1e}"
          f"{'*' if m1.pvalues[t]<.05 else ''}")
for c in ["ntee9_first", "surprisal", "tee6_mean"]:
    print(f"  AUC({c}) = {roc_auc_score(M.human_bnd, M[c]):.3f}")

print("\nT2 graded OLS: boundary_prop ~ same")
m2 = clus("boundary_prop ~ ntee9_first + surprisal + entropy + tee6_mean"
          " + nwords", Z)
for t in PRED:
    print(f"  {t:14s} b={m2.params[t]:+.3f} p={m2.pvalues[t]:.1e}"
          f"{'*' if m2.pvalues[t]<.05 else ''}")

print("\nT3 held-out (leave-half-out) deep ntee, logistic:")
m3 = clus("human_bnd ~ ntee9_ho_first + surprisal + entropy + tee6_mean"
          " + nwords", Z, logit=True)
for t in ["ntee9_ho_first", "surprisal", "tee6_mean"]:
    print(f"  {t:14s} b={m3.params[t]:+.3f} p={m3.pvalues[t]:.1e}"
          f"{'*' if m3.pvalues[t]<.05 else ''}")
print(f"  AUC(ntee9_ho_first) = {roc_auc_score(M.human_bnd, M.ntee9_ho_first):.3f}")

print("\nT4 surprising-only vs expected (does deep ntee track surprising?):")
m4 = clus("surprising_prop ~ ntee9_first + surprisal + entropy + tee6_mean"
          " + nwords", Z)
for t in ["ntee9_first", "surprisal", "entropy"]:
    print(f"  {t:14s} b={m4.params[t]:+.3f} p={m4.pvalues[t]:.1e}"
          f"{'*' if m4.pvalues[t]<.05 else ''}")
print(f"\nDONE HippoCorpus human validation")
