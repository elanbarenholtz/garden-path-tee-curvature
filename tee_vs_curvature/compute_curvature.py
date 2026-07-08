"""
Compute King-style contextual curvature (angular change) on the SAME layer-6
GPT-2 hidden states as the locked sample 8a6087341e, anchored at each word's
final subword (same anchor as tee_k in the locked sample).

Hidden-state conventions copied verbatim from excursion_tests/e_compute.py:
  layer 6, CHUNK 1024, STRIDE 512, first-write-wins chunking, offset-based
  BPE->word map with leading-whitespace shim, word = final subword.

Curvature (angle between successive step vectors of the path):
  step(i)      = h[i] - h[i-1]
  angle(i)     = arccos( cos( step(i), step(i-1) ) )   in [0, pi]
  curvature_1  = angle(ls)                     single-step (matches the earlier
                                               compare_tee_vs_angular.py head-to-head)
  curvature_3  = mean( angle(ls-2..ls) )       King, Fedorenko & Hosseini style:
                                               "angle between successive steps,
                                               averaged over the last three tokens"
  ls = final subword BPE index of the word.

Validation before the curvature values are trusted (same gate as e_compute):
  recomputed closure/final_bpe/tee_k50/tee_k3 must match the locked sample.

Output: curvature_merged_8a6087341e.csv  (locked sample rows + curvature cols)
No locked file is modified.
"""
import hashlib, os, sys, unicodedata
import numpy as np
import pandas as pd
from nltk import Tree
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

GP = "/Users/elansmini/Research/Garden_Path"
STORIES_DIR = f"{GP}/naturalstories"
PARSE_FILE = f"{STORIES_DIR}/parses/penn/all-parses-aligned.txt.penn"
OUT_DIR = f"{GP}/tee_vs_curvature"
LAYER, CHUNK_SIZE, STRIDE = 6, 1024, 512

# ------------------------------------------------------------------ corpus
words = pd.read_csv(f"{STORIES_DIR}/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna()].copy()
words = words[words["id"].str.split(".").str[-1] == "whole"].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
assert (words["word"].str.len() > 0).all()
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
words["word_idx"] = words.groupby("story_id").cumcount()
story_ids = sorted(words["story_id"].unique())
assert len(story_ids) == 10
story_words = {sid: words.loc[words.story_id == sid, "word"].tolist()
               for sid in story_ids}
story_texts = {sid: " ".join(ws) for sid, ws in story_words.items()}
print(f"corpus: {len(words)} words, stories {story_ids}", flush=True)

# ------------------------------------------------------------------ parses
PTB_TOKEN_MAP = {"-LRB-": "(", "-RRB-": ")", "-LCB-": "{", "-RCB-": "}",
                 "-LSB-": "[", "-RSB-": "]", "``": "'", "''": "'",
                 "`": "'", '"': "'", "-NONE-": ""}

def norm_chars(s):
    s = unicodedata.normalize("NFKC", s)
    for c in ["‘", "’", "“", "”", "`"]:
        s = s.replace(c, "Q")
    s = s.replace("''", "Q").replace("Q", "'")
    for c in ["—", "–"]:
        s = s.replace(c, "-")
    return "".join(ch for ch in s if not ch.isspace())

def leaf_records(tree):
    def prune(t):
        if isinstance(t, str):
            return t
        kids = [prune(k) for k in t]
        kids = [k for k in kids
                if not (isinstance(k, Tree) and k.label() == "-NONE-")
                and not (isinstance(k, Tree) and len(k) == 0)]
        return Tree(t.label(), kids)
    t = prune(tree)
    if not isinstance(t, Tree) or len(t.leaves()) == 0:
        return []
    leaves = t.leaves(); n = len(leaves)
    closures = np.zeros(n, dtype=int); openings = np.zeros(n, dtype=int)
    def walk(node, start):
        if isinstance(node, str):
            return start + 1
        pos = start
        has_tree_child = any(isinstance(k, Tree) for k in node)
        for k in node:
            pos = walk(k, pos)
        end = pos - 1
        if has_tree_child and 0 <= end < n:
            closures[end] += 1; openings[start] += 1
        return pos
    walk(t, 0)
    toks = []
    for l in leaves:
        if "/" in l:
            l = l.split("/")[0]
        toks.append(PTB_TOKEN_MAP.get(l, l))
    return list(zip(toks, closures, openings))

def read_trees_balanced(path):
    trees, depth, buf = [], 0, []
    with open(path) as fh:
        for ch in fh.read():
            if ch == "(":
                depth += 1
            if depth > 0:
                buf.append(ch)
            if ch == ")":
                depth -= 1
                if depth == 0 and buf:
                    try:
                        trees.append(Tree.fromstring("".join(buf)))
                    except (ValueError, IndexError):
                        pass
                    buf = []
    assert depth == 0
    return trees

all_trees = read_trees_balanced(PARSE_FILE)
leaf_stream = []
for s_uid, tr in enumerate(all_trees):
    for li, (tok_, clo, opn) in enumerate(leaf_records(tr)):
        leaf_stream.append((s_uid, li, tok_, clo, opn))
print(f"parsed {len(all_trees)} trees, {len(leaf_stream)} leaves", flush=True)

word_rows, li = [], 0
for story_id, word_idx, word in words[["story_id", "word_idx", "word"]].itertuples(index=False):
    target = norm_chars(word); buf, consumed = "", []
    while len(buf) < len(target) and li < len(leaf_stream):
        rec = leaf_stream[li]; buf += norm_chars(rec[2]); consumed.append(rec); li += 1
    if buf != target:
        sys.exit(f"ALIGN FAIL story {story_id} w{word_idx} {word!r} buf={buf!r}")
    word_rows.append({"story_id": story_id, "word_idx": word_idx,
                      "closure_depth_re": int(sum(r[3] for r in consumed))})
assert li == len(leaf_stream)
ptb = pd.DataFrame(word_rows)
print(f"aligned {len(ptb)} words", flush=True)

# ------------------------------------------------------------------ model
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(os.cpu_count() or 4)

def story_pass(text):
    enc = tok(text, return_offsets_mapping=True)
    ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
    n = ids.size(0); hidden = {}; pos = 0
    while pos < n:
        end = min(pos + CHUNK_SIZE, n)
        with torch.no_grad():
            out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[LAYER][0].float().cpu().numpy()
        for i in range(end - pos):
            g = pos + i
            if g not in hidden:
                hidden[g] = hs[i]
        del out
        if end >= n:
            break
        pos += STRIDE
    return hidden, offsets, n

def word_char_spans(word_list):
    spans, cursor = [], 0
    for w in word_list:
        spans.append((cursor, cursor + len(w))); cursor += len(w) + 1
    return spans

def tee_at(hidden, t, k):
    idxs = range(t - k, t)
    if any(i not in hidden for i in idxs) or t not in hidden:
        return np.nan
    W = np.stack([hidden[i] for i in idxs])
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    return float(np.linalg.norm(hidden[t] - (coefs[0] + coefs[1] * k)))

def tee_decomp(hidden, t, k=3):
    """Decompose the k-window extrapolation residual r = h_t - pred into
    along-heading (parallel to fitted slope) and lateral (perpendicular)
    magnitudes. tee = sqrt(par^2 + perp^2)."""
    idxs = range(t - k, t)
    if any(i not in hidden for i in idxs) or t not in hidden:
        return np.nan, np.nan, np.nan
    W = np.stack([hidden[i] for i in idxs])
    A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    a, b = coefs[0], coefs[1]
    r = hidden[t] - (a + b * k)
    nb = np.linalg.norm(b)
    if nb <= 0 or not np.isfinite(nb):
        return float(np.linalg.norm(r)), np.nan, np.nan
    bhat = b / nb
    par = float(np.dot(r, bhat))                       # signed along-heading
    perp = float(np.linalg.norm(r - par * bhat))       # lateral magnitude
    return abs(par), perp, par                         # par_abs, perp, par_signed

def angle(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-8 or nb < 1e-8:
        return np.nan
    return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0)))

def curvature(hidden, ls):
    """curvature_1 (angle at ls) and curvature_3 (mean angle over ls-2..ls)."""
    def step(i):
        return hidden[i] - hidden[i - 1] if (i in hidden and i - 1 in hidden) else None
    def ang_at(i):  # angle between step(i) and step(i-1); needs i, i-1, i-2
        s1, s0 = step(i), step(i - 1)
        return np.nan if (s1 is None or s0 is None) else angle(s1, s0)
    c1 = ang_at(ls)
    a = [ang_at(ls - 2), ang_at(ls - 1), ang_at(ls)]
    c3 = float(np.mean(a)) if all(np.isfinite(x) for x in a) else np.nan
    return c1, c3

frames = []
for sid in story_ids:
    print(f"story {sid}: forward pass...", flush=True)
    text = story_texts[sid]
    hidden, offsets, n_bpe = story_pass(text)
    spans = word_char_spans(story_words[sid])
    bpe_word = np.full(n_bpe, -1); wi = 0
    for bi, (cs, ce) in enumerate(offsets):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
            bpe_word[bi] = wi
        else:
            sys.exit(f"BPE offset outside span story {sid} bpe {bi}")
    assert len(np.unique(bpe_word[bpe_word >= 0])) == len(spans)
    last_sub = {}
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            last_sub[w] = bi
    rows = []
    for w in range(len(spans)):
        ls = last_sub[w]
        c1, c3 = curvature(hidden, ls)
        par_abs, perp, par_signed = tee_decomp(hidden, ls, 3)
        rows.append({"story_id": sid, "word_idx": w, "final_bpe_re": ls,
                     "closure_depth_re": ptb[(ptb.story_id == sid) &
                        (ptb.word_idx == w)].closure_depth_re.iloc[0],
                     "tee_k3_re": tee_at(hidden, ls, 3),
                     "tee_k50_re": tee_at(hidden, ls, 50),
                     "curvature_1": c1, "curvature_3": c3,
                     "tee3_par": par_abs, "tee3_perp": perp,
                     "tee3_par_signed": par_signed})
    frames.append(pd.DataFrame(rows))
    print(f"story {sid}: done", flush=True)

E = pd.concat(frames, ignore_index=True)

# ------------------------------------------------------------------ validate
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sample_hash = hashlib.md5(
    "|".join(f"{r.story_id}.{r.word_idx}" for r in
             S[["story_id", "word_idx"]].itertuples(index=False)).encode()
).hexdigest()[:10]
assert sample_hash == "8a6087341e", sample_hash
M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
assert len(M) == len(S) == 9840

print(f"\nVALIDATION (locked sample, hash {sample_hash}, n={len(M)}):", flush=True)
print(f"  closure_depth mismatches: {(M.closure_depth != M.closure_depth_re).sum()}")
print(f"  final_bpe mismatches:     {(M.final_bpe != M.final_bpe_re).sum()}")
print(f"  max |tee_k50 - re|:       {np.nanmax(np.abs(M.tee_k50 - M.tee_k50_re)):.3e}")
print(f"  max |tee_k3  - re|:       {np.nanmax(np.abs(M.tee_k3  - M.tee_k3_re)):.3e}")
print(f"  curvature_1 NaNs:         {M.curvature_1.isna().sum()}")
print(f"  curvature_3 NaNs:         {M.curvature_3.isna().sum()}")
print(f"  curvature_1 mean/sd:      {M.curvature_1.mean():.4f} / {M.curvature_1.std():.4f}")
print(f"  curvature_3 mean/sd:      {M.curvature_3.mean():.4f} / {M.curvature_3.std():.4f}")

M.to_csv(f"{OUT_DIR}/curvature_merged_8a6087341e.csv", index=False)
print(f"\nDONE -> curvature_merged_8a6087341e.csv", flush=True)
