"""
x13: Leakage-safe version of the event/discourse validation + blind top-word
audit.
(a) Recompute layer-9 word anchors (x11 conventions), then HELD-OUT ntee_l9_ho:
    for each story, k=100 fit on the OTHER nine stories, sigma from training.
(b) T_EVENT (sentence-initial words) and T_WAKE with ntee_l9_ho — does deep
    ntee still beat surprisal/fine-TEE at event boundaries with story-
    independent neighborhoods?
(c) Blind qualitative audit: top-30 and bottom-30 ntee_l9_ho sentence-initial
    words with their sentences, dumped for inspection.
"""
import os, sys
import numpy as np
import pandas as pd
import torch
import statsmodels.formula.api as smf
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked, zscore, fit_cluster
from event_boundaries import BOUNDARIES

RES = f"{GP}/extensions/results"
LAYER, CHUNK_SIZE, STRIDE = 9, 1024, 512
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
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

def spans_(wl):
    sp, c = [], 0
    for w in wl:
        sp.append((c, c + len(w))); c += len(w) + 1
    return sp

anchor = {}
for sid in story_ids:
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offs = enc["offset_mapping"]
    n = ids.size(0); hid = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().numpy()
        for i in range(end - pos):
            if (pos + i) not in hid:
                hid[pos + i] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE
    sp = spans_(story_words[sid]); wi = 0; last = {}
    for bi, (cs, ce) in enumerate(offs):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(sp) and cs >= sp[wi][1]:
            wi += 1
        if wi < len(sp) and cs >= sp[wi][0] and ce <= sp[wi][1]:
            last[wi] = bi
    anchor[sid] = np.stack([hid[last[w]] for w in range(len(sp))]) \
        .astype(np.float64)
    print(f"story {sid} anchors", flush=True)

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

rows = []
for sid in story_ids:
    TR = np.vstack([anchor[s] for s in story_ids if s != sid])
    km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(TR)
    sig = float(np.median(np.linalg.norm(
        TR[:, None, :] - km.cluster_centers_[None], axis=-1).min(1)))
    A_ = anchor[sid]
    d = np.linalg.norm(A_[:, None, :] - km.cluster_centers_[None], axis=-1)
    p = np.exp(-(d ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
    sq = np.sqrt(p)
    rows += [{"story_id": sid, "word_idx": w, "ntee_l9_ho": lin_err(sq, w, 3)}
             for w in range(A_.shape[0])]
    print(f"story {sid} held-out ntee", flush=True)
HO = pd.DataFrame(rows)
M = S.merge(HO, on=["story_id", "word_idx"], validate="one_to_one")
M = M.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
M["sent_initial"] = (M.groupby("story_id")["sent_uid"].diff() != 0) \
    .astype(float)
M["event_bnd"] = [1.0 if r.sent_uid in BOUNDARIES.get(r.story_id, set())
                  else 0.0 for r in M.itertuples()]

# (b) T_EVENT
SI = M[(M.sent_initial == 1) & (M.has_trailing_punct == 0)] \
    .reset_index(drop=True)
first_sent = M.groupby("story_id").sent_uid.min().to_dict()
SI = SI[SI.apply(lambda r: r.sent_uid != first_sent[r.story_id], axis=1)] \
    .reset_index(drop=True)
Z = SI.copy()
for c in ["ntee_l9_ho", "surprisal", "entropy", "tee_k3", "log_freq",
          "word_length"]:
    Z[c] = zscore(SI[c])
m = smf.logit("event_bnd ~ ntee_l9_ho + surprisal + entropy + tee_k3"
              " + log_freq + word_length", data=Z).fit(disp=0)
print(f"\nT_EVENT held-out (sentence-initial n={len(SI)}, "
      f"boundaries={int(SI.event_bnd.sum())}):")
for t in ["ntee_l9_ho", "surprisal", "entropy", "tee_k3"]:
    print(f"  {t:12s} b={m.params[t]:+.3f} p={m.pvalues[t]:.1e}"
          f"{'*' if m.pvalues[t] < .05 else ''}")
for c in ["ntee_l9_ho", "surprisal", "tee_k3"]:
    print(f"  AUC({c}) = {roc_auc_score(SI.event_bnd, SI[c]):.3f}")

# (c) blind top/bottom audit among sentence-initial words
sent_txt = (M.groupby(["story_id", "sent_uid"])["word"]
            .apply(lambda s: " ".join(s)).to_dict())
SI2 = SI.copy()
SI2["sentence"] = [sent_txt[(r.story_id, r.sent_uid)] for r in
                   SI2.itertuples()]
top = SI2.nlargest(30, "ntee_l9_ho")[["story_id", "sent_uid", "ntee_l9_ho",
                                      "event_bnd", "sentence"]]
bot = SI2.nsmallest(30, "ntee_l9_ho")[["story_id", "sent_uid", "ntee_l9_ho",
                                       "event_bnd", "sentence"]]
top.to_csv(f"{RES}/x13_top30_sentences.csv", index=False)
bot.to_csv(f"{RES}/x13_bottom30_sentences.csv", index=False)
print(f"\nTOP-30 deep-ntee sentence starts: event-boundary rate = "
      f"{top.event_bnd.mean():.2f}")
print(f"BOTTOM-30: event-boundary rate = {bot.event_bnd.mean():.2f}")
print("\nTOP-10 (truncated):")
for r in top.head(10).itertuples():
    print(f"  [{r.event_bnd:.0f}] {r.sentence[:90]}")
print("\nBOTTOM-10 (truncated):")
for r in bot.head(10).itertuples():
    print(f"  [{r.event_bnd:.0f}] {r.sentence[:90]}")

M[["story_id", "word_idx", "ntee_l9_ho", "sent_initial", "event_bnd"]] \
    .to_csv(f"{GP}/extensions/ntee_l9_heldout_8a6087341e.csv", index=False)

# (b2) T_WAKE with held-out layer-9 ntee as the geometry term? The wake DV is
# layer-6; keep the wake test on ntee_k100 (its native scale) but add
# ntee_l9_ho as a covariate to show the event-scale measure doesn't kill it.
W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
C = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
DW = W.merge(M[["story_id", "word_idx", "ntee_l9_ho", "event_bnd",
                "has_trailing_punct", "surprisal", "entropy", "word_length",
                "log_freq", "from_start", "fs2", "from_end", "fe2",
                "sent_uid"]], on=["story_id", "word_idx"]) \
      .merge(C[["story_id", "word_idx", "ntee_k100", "ctee_m5"]],
             on=["story_id", "word_idx"]) \
      .merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp",
                  "curvature_3"]], on=["story_id", "word_idx"])
DWpf = DW[DW.has_trailing_punct == 0].reset_index(drop=True)
PRED = ["ntee_k100", "ntee_l9_ho", "event_bnd", "entropy", "surprisal",
        "tee3_perp", "tee3_par", "ctee_m5", "word_length", "log_freq"]
CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"
print("\nT_WAKE (ntee_k100 + held-out deep ntee + event control), punct-free:")
for L in (1, 5, 10):
    dv = f"wake_rel_{L}"
    Dl = DWpf.dropna(subset=[dv] + PRED).reset_index(drop=True)
    Z = Dl.copy(); Z["y"] = zscore(Dl[dv])
    for p_ in PRED:
        Z[p_] = zscore(Dl[p_])
    mod = fit_cluster(f"y ~ {' + '.join(PRED)} + {CTRL}", Z)
    print(f"  L{L:>2}: ntee_k100={mod.params['ntee_k100']:+.3f}"
          f"(p={mod.pvalues['ntee_k100']:.0e}) "
          f"ntee_l9_ho={mod.params['ntee_l9_ho']:+.3f}"
          f"(p={mod.pvalues['ntee_l9_ho']:.0e})")
print(f"\nDONE hash={sh}")
