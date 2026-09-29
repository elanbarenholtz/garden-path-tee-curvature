"""
E2b -- per-word model measures for the Erlangen audiobook, from a German
autoregressive LM, at EVERY layer.

Per word (anchored at the word's final subword, as on Natural Stories):
  surprisal      sum over the word's subwords of -log p (nats)
  entropy        entropy of the next-token distribution just before the
                 word's first subword (nats)
  curv1_L{l}     angle between successive step vectors at the final subword
  curv3_L{l}     mean of that angle over the final three subwords
                 (King/Fedorenko/Hosseini definition; = curvature_3 on NS)
  for l = 1..n_layers (hidden_states[l] = output of block l).
A priori layer = n_layers // 2 (midpoint), written to measures_meta.json.

Text: the transcript tokens (punctuated, from the .txt via e2a) in
PRESENTATION order, i.e. the order the listener heard, with context carried
across chapter boundaries (the listener's context). --reset-per-chapter
restarts context at each excerpt instead (robustness).
Chunking: CHUNK = model max length, STRIDE = CHUNK/2, first write wins
(the NS convention).

Usage: python3 e2b_german_measures.py [--model dbmdz/german-gpt2] [--ref-subject 1]
Output: measures/<model-slug>_words.csv, measures/measures_meta.json
"""
import argparse, json, os, sys
import numpy as np, pandas as pd, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--model", default="dbmdz/german-gpt2")
ap.add_argument("--ref-subject", type=int, default=1)
ap.add_argument("--reset-per-chapter", action="store_true")
ap.add_argument("--chunk", type=int, default=None)
args = ap.parse_args()
os.makedirs(f"{HERE}/measures", exist_ok=True)

tok = AutoTokenizer.from_pretrained(args.model, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(args.model).eval()
torch.set_num_threads(os.cpu_count() or 4)
NL = model.config.num_hidden_layers
CHUNK = args.chunk or min(getattr(model.config, "n_positions",
                          getattr(model.config, "max_position_embeddings", 1024)), 1024)
STRIDE = CHUNK // 2
print(f"{args.model}: {NL} layers, chunk {CHUNK}, a priori layer {NL // 2}")

W = pd.read_csv(f"{HERE}/onsets/sub-{args.ref_subject}_words.csv").sort_values("pres_order")
W["tok"] = W.token.fillna(W.word).astype(str).str.replace(r"\s+", "", regex=True)
segments = ([g for _, g in W.groupby((W.audio_file != W.audio_file.shift()).cumsum())]
            if args.reset_per_chapter else [W])


def measures(seg):
    wl = seg.tok.tolist(); text = " ".join(wl)
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    ids = torch.tensor(enc["input_ids"]); n = len(ids)
    spans, cur = [], 0
    for w in wl:
        spans.append((cur, cur + len(w))); cur += len(w) + 1
    bw = np.full(n, -1); wi = 0
    for bi, (cs, ce) in enumerate(enc["offset_mapping"]):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if not (wi < len(spans) and spans[wi][0] <= cs and ce <= spans[wi][1]):
            sys.exit(f"subword {bi} outside word span")
        bw[bi] = wi
    H = np.zeros((NL + 1, n, model.config.hidden_size), np.float32)
    lp_tok = np.full(n, np.nan); ent_before = np.full(n, np.nan)
    done = np.zeros(n, bool); pos = 0
    while True:
        end = min(pos + CHUNK, n)
        with torch.no_grad():
            o = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        lg = torch.log_softmax(o.logits[0].float(), -1)
        ent = -(lg.exp() * lg).sum(-1).numpy()
        for i in range(end - pos):
            g = pos + i
            if done[g]:
                continue
            done[g] = True
            for l in range(NL + 1):
                H[l, g] = o.hidden_states[l][0, i].float().numpy()
            if i >= 1:                       # prediction of g from g-1, same chunk
                lp_tok[g] = float(lg[i - 1, ids[g]]); ent_before[g] = float(ent[i - 1])
        if end >= n:
            break
        pos += STRIDE

    def ang(l, i):
        if i < 2:
            return np.nan
        a, b = H[l, i] - H[l, i - 1], H[l, i - 1] - H[l, i - 2]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        return np.nan if min(na, nb) < 1e-8 else float(np.arccos(np.clip(a @ b / (na * nb), -1, 1)))

    rows = []
    for w in range(len(wl)):
        sub = np.where(bw == w)[0]; f, ls = sub[0], sub[-1]
        r = dict(surprisal=float(-lp_tok[sub].sum()), entropy=ent_before[f],
                 n_subwords=len(sub))
        for l in range(1, NL + 1):
            a = [ang(l, ls - 2), ang(l, ls - 1), ang(l, ls)]
            r[f"curv1_L{l}"] = a[2]
            r[f"curv3_L{l}"] = float(np.mean(a)) if np.all(np.isfinite(a)) else np.nan
        rows.append(r)
    out = seg[["audio_file", "word_i", "pres_order", "word", "tok"]].reset_index(drop=True)
    return pd.concat([out, pd.DataFrame(rows)], axis=1)


M = pd.concat([measures(s) for s in segments], ignore_index=True)
slug = args.model.replace("/", "__") + ("_reset" if args.reset_per_chapter else "")
M.to_csv(f"{HERE}/measures/{slug}_words.csv", index=False)
meta = dict(model=args.model, n_layers=NL, a_priori_layer=NL // 2, chunk=CHUNK,
            stride=STRIDE, reset_per_chapter=args.reset_per_chapter,
            n_words=len(M))
json.dump(meta, open(f"{HERE}/measures/measures_meta.json", "w"), indent=1)
print(M[["surprisal", "entropy", f"curv3_L{NL//2}"]].describe().round(3))
print("corr at a priori layer:")
print(M[["surprisal", "entropy", f"curv3_L{NL//2}"]].corr().round(3))
print(f"wrote measures/{slug}_words.csv")
