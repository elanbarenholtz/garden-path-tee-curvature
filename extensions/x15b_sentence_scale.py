"""
x15b (EXPLORATORY): sentence-SCALE neighborhood TEE on HippoCorpus. The x15
test used word-trajectory ntee at the sentence-initial word; sentence-level
events may instead need a trajectory through SENTENCE neighborhoods. For each
story, represent each sentence by its layer-9 mean word-state, cluster
sentence-states (k=60, soft/Hellinger), and compute k=2 extrapolation error on
the SENTENCE trajectory (stee). Also a simple sentence-to-sentence cosine-shift
baseline. Test both against human event boundaries. Clearly exploratory:
not in the pre-registered spec.
"""
import os, sys, ast
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
RES = f"{GP}/extensions/results"
M = pd.read_csv(f"{RES}/x15_hippocorpus_sentences.csv")
# need sentence-mean layer-9 states: recompute cheaply from saved? x15 didn't
# save states. Rebuild sentence states from the word CSV is not available;
# instead reload the per-word states quickly via a compact recompute.
# --- lightweight recompute of sentence-mean layer-9 states ---
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
DATA = "/tmp/story_events/data/" \
       "all_features_including_annotations_prev_sent_with_prior_confidence.csv"
d = pd.read_csv(DATA); d["sentence"] = d["sentence"].astype(str)
d["sent"] = d.groupby("story_ids").cumcount()
stories = list(dict.fromkeys(d.story_ids.tolist()))
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEV)
CHUNK, STRIDE = 1024, 512

def blab(s):
    labs = ast.literal_eval(s)
    return np.mean([l != "noEvent" for l in labs])

rows = []
for si, sid in enumerate(stories):
    sub = d[d.story_ids == sid].sort_values("sent")
    sent_words, sent_idx = [], []
    for j, s in zip(sub.sent.tolist(), sub.sentence.tolist()):
        ws = s.split(); sent_words += ws; sent_idx += [j] * len(ws)
    if not sent_words:
        continue
    text = " ".join(sent_words); enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offs = enc["offset_mapping"]
    n = ids.size(0); h9 = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0).to(DEV),
                        output_hidden_states=True)
            hs9 = out.hidden_states[9][0].float().cpu().numpy()
        for i in range(end - pos):
            if (pos + i) not in h9:
                h9[pos + i] = hs9[i]
        del out
        if end >= n:
            break
        pos += STRIDE
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
    # sentence-mean state = mean of its word states
    from collections import defaultdict
    byword = defaultdict(list)
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            byword[w].append(h9[bi])
    wstate = {w: np.mean(v, 0) for w, v in byword.items()}
    sent_state = defaultdict(list)
    for w in range(len(sent_words)):
        if w in wstate:
            sent_state[sent_idx[w]].append(wstate[w])
    for j in sorted(sent_state):
        rows.append({"sid": sid, "sent": j,
                     "sstate": np.mean(sent_state[j], 0)})
    if si % 60 == 0:
        print(f"  story {si}/{len(stories)}", flush=True)

SS = pd.DataFrame(rows)
allS = np.stack(SS.sstate.values)
km = KMeans(n_clusters=60, n_init=4, random_state=0).fit(allS)
sig = float(np.median(km.transform(allS).min(1)))

def stee_and_shift(states):
    dd = km.transform(states)
    p = np.exp(-(dd ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
    sq = np.sqrt(p)
    stee = np.full(len(states), np.nan)
    shift = np.full(len(states), np.nan)
    for j in range(len(states)):
        if j >= 2:
            pred = 2 * sq[j - 1] - sq[j - 2]   # k=2 linear extrapolation
            stee[j] = np.linalg.norm(sq[j] - pred)
        if j >= 1:
            a, b = states[j - 1], states[j]
            shift[j] = 1 - float(np.dot(a, b) /
                (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    return stee, shift

SS["stee"] = np.nan; SS["shift"] = np.nan
for sid in stories:
    idx = SS.index[SS.sid == sid].tolist()
    if not idx:
        continue
    st, sh = stee_and_shift(np.stack(SS.loc[idx, "sstate"].values))
    SS.loc[idx, "stee"] = st; SS.loc[idx, "shift"] = sh

d["boundary_prop"] = d.uncollated_annotation.apply(blab)
d["human_bnd"] = (d.surprise_annotation != "noEvent").astype(float)
M2 = SS.merge(d[["story_ids", "sent", "human_bnd", "boundary_prop"]]
              .rename(columns={"story_ids": "sid"}), on=["sid", "sent"])
M2 = M2.dropna(subset=["stee", "shift"]).reset_index(drop=True)

def z(s):
    return (s - s.mean()) / s.std()
for c in ["stee", "shift"]:
    M2[c + "_z"] = z(M2[c])
print(f"\nEXPLORATORY sentence-scale test (n={len(M2)}, "
      f"human boundary rate={M2.human_bnd.mean():.2f}):")
for c in ["stee", "shift"]:
    m = smf.logit(f"human_bnd ~ {c}_z", data=M2).fit(disp=0,
        cov_type="cluster", cov_kwds={"groups": M2["sid"]})
    auc = roc_auc_score(M2.human_bnd, M2[c])
    print(f"  {c:6s}: b={m.params[c+'_z']:+.3f} p={m.pvalues[c+'_z']:.1e}"
          f"  AUC={auc:.3f}")
print("\nDONE exploratory sentence-scale")
