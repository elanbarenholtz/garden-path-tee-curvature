"""
x9e: Fine-TEE layer sweep on gpt2-xl. One more states pass saving full BPE
states (fp16) at the 13 sampled layers; per layer compute tee_k3 (locked
anchor) and report closure/entropy partial rs (punct-free) + on-word RT beta
(surprisal_xl + lexical + prevRT controls). Answers: does the small-model
fine-TEE signature (structure-coupled, RT-positive) exist at ANY XL layer?
"""
import os, sys
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import (GP, load_locked, load_rt, zscore, fit_cluster, build_ctrl,
                  partial_r)

TAG = "gpt2_xl"
CHUNK_SIZE, STRIDE = 1024, 512
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
S, sh = load_locked()
story_ids = sorted(S.story_id.unique())
SE = pd.read_csv(f"{GP}/extensions/{TAG}_surp_ent.csv")

words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna() &
              (words["id"].str.split(".").str[-1] == "whole")].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
story_words = {s: words.loc[words.story_id == s, "word"].tolist()
               for s in story_ids}
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2-xl").eval().to(DEV)
NLAYER = model.config.n_layer
step = max(1, NLAYER // 12)
LAYERS = list(range(0, NLAYER + 1, step))
if LAYERS[-1] != NLAYER:
    LAYERS.append(NLAYER)
print(f"fine sweep layers {LAYERS} on {DEV}", flush=True)

def word_char_spans(wl):
    spans, c = [], 0
    for w in wl:
        spans.append((c, c + len(w))); c += len(w) + 1
    return spans

def lin_err(H, t, k=3):
    if t - k < 0:
        return np.nan
    W = H[t - k:t].astype(np.float64)
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    c, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(H[t].astype(np.float64) - (c[0] + c[1] * k)))

rows = []
for sid in story_ids:
    text = " ".join(story_words[sid])
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
    n = ids.size(0); hid = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0).to(DEV),
                        output_hidden_states=True)
            hs = np.stack([out.hidden_states[l][0].half().cpu().numpy()
                           for l in LAYERS], axis=1)  # (chunk, 13, d)
        for i in range(end - pos):
            if (pos + i) not in hid:
                hid[pos + i] = hs[i]
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
    Hfull = {li: np.stack([hid[i][li] for i in range(n)])
             for li in range(len(LAYERS))}
    for w in range(len(spans)):
        rec = {"story_id": sid, "word_idx": w}
        for li in range(len(LAYERS)):
            rec[f"ftee_l{li}"] = lin_err(Hfull[li], last_sub[w], 3)
        rows.append(rec)
    print(f"story {sid} done", flush=True)

F = pd.DataFrame(rows)
M = S.merge(F, on=["story_id", "word_idx"], validate="one_to_one") \
     .merge(SE, on=["story_id", "word_idx"], validate="one_to_one")
M.to_csv(f"{GP}/extensions/{TAG}_fine_sweep_8a6087341e.csv", index=False)
Mpf = M[M.has_trailing_punct == 0].reset_index(drop=True)
Cm = build_ctrl(Mpf)
D = M.merge(load_rt(), on=["story_id", "zone"], validate="one_to_one")
D = D.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
D["prev_logRT"] = D.groupby("story_id")["mean_logRT"].shift(1)
Dpf = D[D.has_trailing_punct == 0].dropna(subset=["prev_logRT"]) \
    .reset_index(drop=True)
print(f"\nlayer | r_closure | r_entropy | RT beta (punct-free)")
for li, lay in enumerate(LAYERS):
    meas = f"ftee_l{li}"
    rc, _ = partial_r(Mpf, Cm, meas, "closure_depth")
    re_, _ = partial_r(Mpf, Cm, meas, f"entropy_{TAG}")
    Z = Dpf.copy()
    for c in [meas, f"surprisal_{TAG}", "word_length", "log_freq",
              "prev_logRT"]:
        Z[c] = zscore(Dpf[c])
    m = fit_cluster(f"mean_logRT ~ {meas} + surprisal_{TAG} + word_length"
                    f" + log_freq + prev_logRT + from_start + fs2 + from_end"
                    f" + fe2 + C(story_id)", Z)
    print(f"  {lay:2d} | {rc:+.4f} | {re_:+.4f} | "
          f"{m.params[meas]:+.4f} (p={m.pvalues[meas]:.0e})")
print(f"\nDONE {TAG} hash={sh}")
