"""
x11: Discourse validation for deep-layer neighborhood TEE (GPT-2 small,
layer 9 — the wake-peak layer from x8). Does deep ntee align with discourse-
level transitions better than surprisal / frequency / fine TEE?
Proxies for discourse transition (no human event norms exist for Natural
Stories):
  sent_initial     word starts a new sentence (from_start == min within sent)
  disc_marker      word (lowercased, punct-stripped) in a standard connective
                   list (but, however, then, meanwhile, later, suddenly, ...)
  sem_shift        cross-sentence semantic shift: 1 - cos(mean layer-9 anchor
                   state of previous sentence, current sentence) assigned to
                   sentence-initial words
Tests:
  T1 logistic: proxy ~ z(ntee_l9) + z(surprisal) + z(entropy) + z(tee_k3)
               + z(log_freq) + z(word_length) (+story FE), punct-free
  T2 OLS on sentence-initial words: z(sem_shift) ~ z(ntee_l9) + controls
  T3 descriptive: top-decile ntee_l9 words — rate of sent_initial/disc_marker
     vs bottom decile
"""
import os, sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, load_states, zscore
from sklearn.cluster import KMeans

RES = f"{GP}/extensions/results"
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())

LAYER = 9   # wake-peak layer from x8
# recompute layer-9 anchors (word grain) with x8 conventions
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
CHUNK_SIZE, STRIDE = 1024, 512
words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna() &
              (words["id"].str.split(".").str[-1] == "whole")].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
story_words = {s: words.loc[words.story_id == s, "word"].tolist()
               for s in story_ids}
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(os.cpu_count() or 4)

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c + len(w))); c += len(w) + 1
    return spans

anchor = {}
for sid in story_ids:
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
    n = ids.size(0); hidden = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().numpy()
        for i in range(end - pos):
            if (pos + i) not in hidden:
                hidden[pos + i] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE
    spans = word_char_spans(story_words[sid]); wi = 0; last_sub = {}
    for bi, (cs, ce) in enumerate(offsets):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            last_sub[wi] = bi
    anchor[sid] = np.stack([hidden[last_sub[w]]
                            for w in range(len(spans))]).astype(np.float64)
    print(f"story {sid} anchors done", flush=True)

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

ALL = np.vstack([anchor[sid] for sid in story_ids])
km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(ALL)
sig = float(np.median(np.linalg.norm(
    ALL[:, None, :] - km.cluster_centers_[None], axis=-1).min(1)))
rows = []
for sid in story_ids:
    A_ = anchor[sid]
    d = np.linalg.norm(A_[:, None, :] - km.cluster_centers_[None], axis=-1)
    p = np.exp(-(d ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
    sq = np.sqrt(p)
    rows += [{"story_id": sid, "word_idx": w, "ntee_l9": lin_err(sq, w, 3)}
             for w in range(A_.shape[0])]
M = S.merge(pd.DataFrame(rows), on=["story_id", "word_idx"],
            validate="one_to_one")

# ---- discourse proxies ----
M = M.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
M["sent_initial"] = (M.groupby("story_id")["sent_uid"].diff() != 0) \
    .astype(float)
MARKERS = {"but", "however", "then", "meanwhile", "later", "suddenly",
           "afterwards", "finally", "eventually", "moreover", "instead",
           "nevertheless", "next", "soon", "now", "once", "still", "yet",
           "though", "although", "because", "so", "thus", "therefore",
           "anyway", "besides", "afterward"}
M["word_clean"] = M["word"].astype(str).str.lower() \
    .str.replace(r"[^a-z]", "", regex=True)
M["disc_marker"] = M["word_clean"].isin(MARKERS).astype(float)

# semantic shift between adjacent sentences (layer-9 sentence centroids)
cent = {}
for sid in story_ids:
    sub = M[M.story_id == sid]
    for su in sub.sent_uid.unique():
        wis = sub[sub.sent_uid == su].word_idx.values
        cent[(sid, su)] = anchor[sid][wis].mean(0)
def semshift(r):
    if r.sent_initial != 1:
        return np.nan
    prev = (r.story_id, r.sent_uid - 1)
    cur = (r.story_id, r.sent_uid)
    if prev not in cent or cur not in cent:
        return np.nan
    a, b = cent[prev], cent[cur]
    return 1 - float(np.dot(a, b) /
                     (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
M["sem_shift"] = M.apply(semshift, axis=1)

Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
print(f"\nSAMPLE: hash={sh} punct-free n={len(Mpf)}  "
      f"sent_initial={int(Mpf.sent_initial.sum())} "
      f"markers={int(Mpf.disc_marker.sum())}")

# T1: logistic
for dv in ("sent_initial", "disc_marker"):
    Z = Mpf.copy()
    for c in ["ntee_l9", "surprisal", "entropy", "tee_k3", "log_freq",
              "word_length"]:
        Z[c] = zscore(Mpf[c])
    m = smf.logit(f"{dv} ~ ntee_l9 + surprisal + entropy + tee_k3"
                  " + log_freq + word_length", data=Z).fit(disp=0)
    print(f"\nT1 logistic {dv}:")
    for t in ["ntee_l9", "surprisal", "entropy", "tee_k3"]:
        print(f"  {t:10s} b={m.params[t]:+.3f} p={m.pvalues[t]:.1e}"
              f"{'*' if m.pvalues[t] < .05 else ''}")

# T2: semantic shift on sentence-initial words
Si = Mpf[(Mpf.sent_initial == 1) & Mpf.sem_shift.notna()] \
    .reset_index(drop=True)
Z = Si.copy()
for c in ["sem_shift", "ntee_l9", "surprisal", "entropy", "tee_k3",
          "log_freq", "word_length"]:
    Z[c] = zscore(Si[c])
m = smf.ols("sem_shift ~ ntee_l9 + surprisal + entropy + tee_k3 + log_freq"
            " + word_length + C(story_id)", data=Z).fit()
print(f"\nT2 OLS sem_shift (sentence-initial, n={len(Si)}):")
for t in ["ntee_l9", "surprisal", "entropy", "tee_k3"]:
    print(f"  {t:10s} b={m.params[t]:+.3f} p={m.pvalues[t]:.1e}"
          f"{'*' if m.pvalues[t] < .05 else ''}")

# T3: deciles
q = Mpf.ntee_l9.quantile([0.9, 0.1])
top = Mpf[Mpf.ntee_l9 >= q[0.9]]; bot = Mpf[Mpf.ntee_l9 <= q[0.1]]
print(f"\nT3 top vs bottom ntee_l9 decile (punct-free):")
print(f"  sent_initial: {top.sent_initial.mean():.3f} vs "
      f"{bot.sent_initial.mean():.3f}")
print(f"  disc_marker:  {top.disc_marker.mean():.3f} vs "
      f"{bot.disc_marker.mean():.3f}")
print(f"  example top words: "
      f"{top.nlargest(25, 'ntee_l9').word.tolist()}")
M[["story_id", "word_idx", "ntee_l9", "sent_initial", "disc_marker",
   "sem_shift"]].to_csv(f"{RES}/x11_discourse.csv", index=False)
print(f"\nDONE hash={sh}")
