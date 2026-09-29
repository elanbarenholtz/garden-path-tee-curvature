"""
F3a -- compute anticipated curvature on Natural Stories (GPT-2 small, layer 6),
anchored at each word's final subword, the same anchor as curvature_3.

At the final subword t of word w, the model's next-token distribution is its
forecast of the first subword of word w+1. For the top-k candidates we compute
the angle each would produce at t+1 (see anticipated.py), weight by
probability, and keep mean, variance, and dispersion for k in K_LIST.

Chunking matches compute_curvature.py (CHUNK 1024, STRIDE 512, first write
wins), with one unavoidable change: a candidate occupies position t+1, so t
must sit at local index <= CHUNK-2. A t at local index CHUNK-1 is evaluated in
the next chunk instead (where it sits mid-window). Affects at most 1 position
per chunk boundary.

Gates before anything is written:
  * locked sample hash 8a6087341e, final_bpe re-derived and matched 9840/9840
  * cached candidate state for the realised next token equals the full-pass
    state at t+1 (max abs diff < 1e-3) at every checked position

Output: f3_anticipated_8a6087341e.csv
Runtime: roughly 5-15 min on a laptop CPU for kmax=100.
Usage: python3 f3_anticipated_ns.py [--kmax-list 5,10,20,50,100]
"""
import os, sys, time, hashlib, argparse
import numpy as np, pandas as pd, torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anticipated import chunk_anticipated

ap = argparse.ArgumentParser()
ap.add_argument("--k-list", default="5,10,20,50,100")
ap.add_argument("--layer", type=int, default=6)
args = ap.parse_args()
K_LIST = [int(x) for x in args.k_list.split(",")]
LAYER, CHUNK, STRIDE = args.layer, 1024, 512

GP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(GP, "curvature_followups")

# ---------------------------------------------------------------- corpus
words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words["word"].notna()].copy()
words = words[words["id"].str.split(".").str[-1] == "whole"].copy()
words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words["id"].str.split(".").str[0].astype(int)
words["word_idx"] = words.groupby("story_id").cumcount()
story_ids = sorted(words.story_id.unique())
story_words = {s: words.loc[words.story_id == s, "word"].tolist() for s in story_ids}

S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
torch.set_num_threads(os.cpu_count() or 4)


def last_subwords(text, wlist):
    enc = tok(text, return_offsets_mapping=True)
    spans, cur = [], 0
    for w in wlist:
        spans.append((cur, cur + len(w))); cur += len(w) + 1
    bpe_word = np.full(len(enc["input_ids"]), -1); wi = 0
    for bi, (cs, ce) in enumerate(enc["offset_mapping"]):
        while cs < ce and text[cs].isspace():
            cs += 1
        if ce <= cs:
            continue
        while wi < len(spans) and cs >= spans[wi][1]:
            wi += 1
        assert wi < len(spans) and spans[wi][0] <= cs and ce <= spans[wi][1]
        bpe_word[bi] = wi
    last = {}
    for bi, w in enumerate(bpe_word):
        if w >= 0:
            last[w] = bi
    assert len(last) == len(wlist)
    return torch.tensor(enc["input_ids"]), last


def chunk_starts(n):
    starts, pos = [], 0
    while True:
        starts.append(pos)
        if pos + CHUNK >= n:
            return starts
        pos += STRIDE


def assign(t, starts, n):
    """first chunk that has t at local index in [1, CHUNK-2]"""
    for s in starts:
        end = min(s + CHUNK, n)
        loc = t - s
        if 1 <= loc <= CHUNK - 2 and t < end:
            return s
    return None


frames, all_checks, t0 = [], [], time.time()
for sid in story_ids:
    text = " ".join(story_words[sid])
    ids, last = last_subwords(text, story_words[sid])
    n = len(ids); starts = chunk_starts(n)
    by_chunk = {}
    for w, t in last.items():
        s = assign(t, starts, n)
        if s is not None:
            by_chunk.setdefault(s, []).append((w, t))
    recs = []
    for s, items in sorted(by_chunk.items()):
        chunk = ids[s:min(s + CHUNK, n)]
        locs = [t - s for _, t in items]
        rows, checks = chunk_anticipated(model, chunk, locs, LAYER, K_LIST,
                                         check_positions=set(locs))
        all_checks += list(checks.values())
        # realised angle at t+1 (same chunk) for the sanity correlation
        with torch.no_grad():
            H = model(chunk.unsqueeze(0), output_hidden_states=True
                      ).hidden_states[LAYER][0].float().numpy()
        for (w, t), loc in zip(items, locs):
            r = dict(story_id=sid, word_idx=w, final_bpe_re=t, **rows[loc])
            if loc + 1 < len(chunk):
                a, b = H[loc + 1] - H[loc], H[loc] - H[loc - 1]
                r["angle_next_realised"] = float(np.arccos(np.clip(
                    a @ b / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))
            recs.append(r)
    frames.append(pd.DataFrame(recs))
    print(f"story {sid}: {len(recs)} words  ({time.time()-t0:.0f}s)", flush=True)

A = pd.concat(frames, ignore_index=True)
M = S[["story_id", "word_idx", "final_bpe", "curvature_1", "curvature_3",
       "entropy"]].merge(A, on=["story_id", "word_idx"], how="left",
                         validate="one_to_one")
print(f"\nGATES")
print(f"  words with anticipated values: {M.ac_mean_k50.notna().sum()}/{len(M)}")
print(f"  final_bpe mismatches: {(M.final_bpe != M.final_bpe_re).sum()}")
print(f"  cache check max |h_v - h_full|: {max(all_checks):.2e}  "
      f"(n={len(all_checks)})")
assert (M.final_bpe == M.final_bpe_re).all()
assert max(all_checks) < 1e-3

kmax = max(K_LIST)
print(f"\nk-STABILITY (correlation with k={kmax}; mean top-k mass)")
for k in K_LIST:
    print(f"  k={k:>4}  r(mean) {M[f'ac_mean_k{k}'].corr(M[f'ac_mean_k{kmax}']):.3f}"
          f"  r(var) {M[f'ac_var_k{k}'].corr(M[f'ac_var_k{kmax}']):.3f}"
          f"  r(disp) {M[f'ac_disp_k{k}'].corr(M[f'ac_disp_k{kmax}']):.3f}"
          f"  mass {M[f'mass_k{k}'].mean():.3f}")
print("\nSANITY / DISTINCTNESS (k=50)")
print(M[["ac_mean_k50", "ac_var_k50", "ac_disp_k50", "ent_full",
         "angle_next_realised", "curvature_1", "curvature_3"]]
      .corr().round(3).to_string())
M.to_csv(f"{OUT}/f3_anticipated_8a6087341e.csv", index=False)
print(f"\nwrote {OUT}/f3_anticipated_8a6087341e.csv")
