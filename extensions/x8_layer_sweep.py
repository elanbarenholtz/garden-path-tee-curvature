"""
x8: Layer sweep. Where in the network does the neighborhood-TEE signal live?
Recompute story passes saving WORD-ANCHOR (final-subword) states for all 13
GPT-2 layers (embedding=0 .. 12), same chunking conventions. Per layer:
  - ntee_L{layer}: k-means k=100 soft-assignment (Hellinger) TEE, all-story
    fit (matching x1; x7 shows held-out equivalence at layer 6)
  - partial r vs closure/entropy (punct-free)
  - beta on on-word RT (punct-free, surprisal+lexical+prevRT controls)
  - beta on wake_rel_5 (layer-6 DV, punct-free, entropy/surprisal controls)
Output: results/x8_layer_sweep.csv
"""
import os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import (GP, load_locked, load_rt, zscore, fit_cluster, build_ctrl,
                  partial_r)
from sklearn.cluster import KMeans

RES = f"{GP}/extensions/results"
CHUNK_SIZE, STRIDE = 1024, 512
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
NL = 13

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c + len(w))); c += len(w) + 1
    return spans

anchor = {}   # sid -> (n_words, 13, 768)
for sid in story_ids:
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
    n = ids.size(0); hidden = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        hs = np.stack([out.hidden_states[l][0].float().numpy()
                       for l in range(NL)], axis=1)   # (chunk, 13, 768)
        for i in range(end - pos):
            g = pos + i
            if g not in hidden:
                hidden[g] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE
    spans = word_char_spans(story_words[sid])
    wi = 0; last_sub = {}
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
                            for w in range(len(spans))])
    print(f"story {sid}: anchors {anchor[sid].shape}", flush=True)

def lin_err(traj, w, k=3):
    if w - k < 0 or w >= traj.shape[0]:
        return np.nan
    W = traj[w - k:w]
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(traj[w] - (c[0] + c[1] * k)))

W6 = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
RT = load_rt()
out = []
for layer in range(NL):
    ALL = np.vstack([anchor[sid][:, layer, :] for sid in story_ids])
    km = KMeans(n_clusters=100, n_init=4, random_state=0).fit(ALL)
    dnn = np.linalg.norm(ALL[:, None, :] - km.cluster_centers_[None],
                         axis=-1).min(1)
    sig = float(np.median(dnn))
    rows = []
    for sid in story_ids:
        A_ = anchor[sid][:, layer, :]
        d = np.linalg.norm(A_[:, None, :] - km.cluster_centers_[None],
                           axis=-1)
        p = np.exp(-(d ** 2) / (2 * sig ** 2)); p /= p.sum(1, keepdims=True)
        sq = np.sqrt(p)
        for w in range(A_.shape[0]):
            rows.append({"story_id": sid, "word_idx": w,
                         "ntee_l": lin_err(sq, w, 3)})
    E = pd.DataFrame(rows)
    M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
    Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
    Cm = build_ctrl(Mpf)
    r_clo, _ = partial_r(Mpf, Cm, "ntee_l", "closure_depth")
    r_ent, _ = partial_r(Mpf, Cm, "ntee_l", "entropy")
    # RT
    D = M.merge(RT, on=["story_id", "zone"], validate="one_to_one")
    D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
    D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
    Dpf = D[D.has_trailing_punct == 0].dropna(
        subset=["prev_logRT", "ntee_l"]).reset_index(drop=True)
    Z = Dpf.copy()
    for c in ["ntee_l", "surprisal", "word_length", "log_freq",
              "prev_logRT"]:
        Z[c] = zscore(Dpf[c])
    m1 = fit_cluster("mean_logRT ~ ntee_l + surprisal + word_length"
                     " + log_freq + prev_logRT + from_start + fs2 + from_end"
                     " + fe2 + C(story_id)", Z)
    # wake
    DW = W6.merge(M, on=["story_id", "word_idx"], validate="one_to_one")
    DWpf = DW[DW.has_trailing_punct == 0].dropna(
        subset=["wake_rel_5", "ntee_l"]).reset_index(drop=True)
    Z2 = DWpf.copy(); Z2["y"] = zscore(DWpf["wake_rel_5"])
    for c in ["ntee_l", "entropy", "surprisal", "word_length", "log_freq"]:
        Z2[c] = zscore(DWpf[c])
    m2 = fit_cluster("y ~ ntee_l + entropy + surprisal + word_length"
                     " + log_freq + from_start + fs2 + from_end + fe2"
                     " + C(story_id)", Z2)
    rec = {"layer": layer, "r_closure": r_clo, "r_entropy": r_ent,
           "rt_beta": m1.params["ntee_l"], "rt_p": m1.pvalues["ntee_l"],
           "wake5_beta": m2.params["ntee_l"],
           "wake5_p": m2.pvalues["ntee_l"]}
    out.append(rec)
    print(f"layer {layer:2d}: closure={r_clo:+.3f} entropy={r_ent:+.3f} "
          f"RT={rec['rt_beta']:+.4f}(p={rec['rt_p']:.0e}) "
          f"wake5={rec['wake5_beta']:+.3f}(p={rec['wake5_p']:.0e})",
          flush=True)

pd.DataFrame(out).to_csv(f"{RES}/x8_layer_sweep.csv", index=False)
print(f"\nDONE hash={sh}")
