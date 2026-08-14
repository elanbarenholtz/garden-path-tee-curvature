"""
SYNTACTIC TRANSITION VARIABLES, take 2 -- nltk.Tree instead of a hand-rolled
bracket walker. The first extractor silently dropped ~2,800 terminals (86.3%
coverage); the raw file in fact contains every corpus token (10,256 distinct
story.token indices; 11,729 terminals, because punctuation is split into its
own terminals sharing the word's index).

Terminals sharing an index are merged: opens summed, closes summed, and the
gorn/depth taken from the FIRST terminal of the index (the word itself; the
punctuation terminal follows it).

Bracket-counting convention is calibrated against the sample's existing
closure_depth column rather than assumed: we compute phrase-level closes
(excluding each terminal's POS bracket) and report agreement.

Output: syntax_vars_8a6087341e.csv with
  open_t, close_t, depth_t, same_parent, lca_dist
"""

import re
import numpy as np
import pandas as pd
import hashlib
from nltk import Tree

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
PENN = f"{GP}/naturalstories/parses/penn/all-parses-aligned.txt.penn"


def parse_trees(path):
    buf, depth = [], 0
    for line in open(path):
        depth += line.count("(") - line.count(")")
        buf.append(line)
        if depth == 0 and any(l.strip() for l in buf):
            s = "".join(buf).strip()
            if s:
                yield s
            buf = []


rows = []
ntrees = 0
for ts in parse_trees(PENN):
    t = Tree.fromstring(ts)
    ntrees += 1
    leaves = t.leaves()
    positions = t.treepositions("leaves")
    kept_positions = []
    for li, (leaf, pos) in enumerate(zip(leaves, positions)):
        if "/" not in leaf:
            continue          # trace elements (*, *T*-1) and bare symbols
        m = re.search(r"/(\d+)\.(\d+)(?:\.\S+)?$", leaf)
        if not m:
            continue
        word = leaf[:m.start()]
        story, tok = m.group(1), m.group(2)
        # phrase-level structural position: drop leaf index and POS node
        phrase_pos = pos[:-2] if len(pos) >= 2 else ()
        prev_pos = kept_positions[-1] if kept_positions else None
        nxt = None
        for q in positions[li + 1:]:
            leafq = t[q]
            if "/" in leafq and re.search(r"/\d+\.\d+(?:\.\S+)?$", leafq):
                nxt = q
                break
        nxt_pos = nxt
        kept_positions.append(pos)
        # opens before this leaf: new brackets relative to previous leaf,
        # at phrase level (exclude POS): depth(phrase) - common(phrase_prev)
        if prev_pos is None:
            opens = len(phrase_pos)          # start of sentence: all open
        else:
            prev_phrase = prev_pos[:-2] if len(prev_pos) >= 2 else ()
            k = 0
            for a, b in zip(prev_phrase, phrase_pos):
                if a == b:
                    k += 1
                else:
                    break
            opens = len(phrase_pos) - k
        # closes after this leaf, phrase level
        if nxt_pos is None:
            closes = len(phrase_pos)         # end of sentence: all close
        else:
            nxt_phrase = nxt_pos[:-2] if len(nxt_pos) >= 2 else ()
            k = 0
            for a, b in zip(phrase_pos, nxt_phrase):
                if a == b:
                    k += 1
                else:
                    break
            closes = len(phrase_pos) - k
        rows.append({"story_id": int(story), "tok": int(tok),
                     "parse_word": word, "open_raw": opens,
                     "close_raw": closes, "depth_t": len(phrase_pos),
                     "gorn": phrase_pos})

P = pd.DataFrame(rows)
print(f"trees {ntrees}   terminals kept {len(P):,}")

# merge terminals sharing a token index (word + attached punctuation)
agg = (P.groupby(["story_id", "tok"], sort=True)
         .agg(open_t=("open_raw", "sum"), close_t=("close_raw", "sum"),
              depth_t=("depth_t", "first"), gorn=("gorn", "first"),
              parse_word=("parse_word", "first"))
         .reset_index())
print(f"distinct (story, token): {len(agg):,}")

# transitions
agg = agg.sort_values(["story_id", "tok"]).reset_index(drop=True)
same_parent = np.full(len(agg), np.nan)
lca_dist = np.full(len(agg), np.nan)
prev = None
for i, r in enumerate(agg.itertuples()):
    if prev is not None and prev.story_id == r.story_id \
            and r.tok == prev.tok + 1:
        a, b = prev.gorn, r.gorn
        k = 0
        for x, y in zip(a, b):
            if x == y:
                k += 1
            else:
                break
        same_parent[i] = 1.0 if (len(a) == len(b) and k >= len(b) - 0
                                 and a == b) else \
                         (1.0 if a == b else 0.0)
        lca_dist[i] = max(len(b) - k, 0)
    prev = r
# same_parent: identical phrase gorn means same immediately dominating phrase
agg["same_parent"] = [1.0 if (isinstance(g, tuple) and prevg == g) else
                      (np.nan if np.isnan(l) else 0.0)
                      for g, prevg, l in zip(
                          agg.gorn,
                          [None] + list(agg.gorn[:-1]),
                          lca_dist)]
agg["lca_dist"] = lca_dist

S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh
agg["word_idx"] = agg.tok - 1
M = S[["story_id", "word_idx", "word", "closure_depth"]].merge(
    agg[["story_id", "word_idx", "parse_word", "open_t", "close_t",
         "depth_t", "same_parent", "lca_dist"]],
    on=["story_id", "word_idx"], how="left", validate="one_to_one")

matched = M.parse_word.notna()
print(f"\ncoverage: {matched.mean():.2%}  "
      f"({'PASS' if matched.mean() >= .99 else 'FAIL'})")


def norm(w):
    return re.sub(r"[^A-Za-z0-9]", "", str(w)).lower()


ok = M[matched].apply(lambda r: norm(r.word) == norm(r.parse_word), axis=1)
print(f"word-form agreement: {ok.mean():.2%}  "
      f"({'PASS' if ok.mean() >= .99 else 'FAIL'})")

sub = M[matched]
exact = (sub.close_t == sub.closure_depth).mean()
off1 = (sub.close_t == sub.closure_depth + 1).mean()
print(f"close_t vs closure_depth: exact {exact:.1%}, "
      f"offset+1 {off1:.1%}")
r = sub.close_t.corr(sub.closure_depth)
print(f"r(close_t, closure_depth) = {r:.3f}")

M.drop(columns=["parse_word"]).to_csv(
    f"{GP}/gp_confound_check/syntax_vars_8a6087341e.csv", index=False)
tr = M.dropna(subset=["lca_dist"])
print(f"\ntransitions with variables: {len(tr):,}")
print("lca_dist distribution:")
print(tr.lca_dist.value_counts().sort_index().head(8).to_string())
print(f"same_parent = 1: {tr.same_parent.mean():.1%}")
print(f"close_t = 0 and same_parent = 1 (the B2 cell): "
      f"{((tr.close_t == 0) & (tr.same_parent == 1)).mean():.1%}")
