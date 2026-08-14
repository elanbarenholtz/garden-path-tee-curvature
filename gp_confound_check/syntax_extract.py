"""
EXTRACT SYNTACTIC TRANSITION VARIABLES FROM THE NATURAL STORIES PARSES
======================================================================
Implements the data step of PREREG_syntax_control.md. No analysis here; this
only builds the per-word syntactic variables and validates alignment.

Parse file: naturalstories/parses/penn/all-parses-aligned.txt.penn.
Terminals are word/STORY.TOKEN (e.g. "If/1.1"), so alignment to the corpus is
by explicit index, not by position guessing.

Per word w_t (aligned to story_id, token index):
  open_t        brackets opened immediately before w_t
  close_t       brackets closed immediately after w_t   [cross-checked against
                the locked sample's closure_depth]
  depth_t       bracket depth at w_t
  same_parent   1 if w_{t-1} and w_t share their immediately dominating
                constituent (computed from gorn addresses)
  lca_dist      steps from w_t's parent up to the lowest common ancestor with
                w_{t-1} (0 = same parent)

Validation per prereg:
  - terminal word forms must match sample word forms on >= 99% of words
  - close_t must agree with the sample's existing closure_depth column
Output: syntax_vars_8a6087341e.csv
"""

import re
import numpy as np
import pandas as pd
import hashlib

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
PENN = f"{GP}/naturalstories/parses/penn/all-parses-aligned.txt.penn"


def parse_trees(path):
    """Yield one bracketed tree string per ROOT."""
    buf, depth = [], 0
    for line in open(path):
        for ch in line:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        buf.append(line)
        if depth == 0 and any(l.strip() for l in buf):
            s = "".join(buf).strip()
            if s:
                yield s
            buf = []


TOKEN = re.compile(r"\(|\)|[^\s()]+")


def terminals_with_context(tree):
    """Walk one tree; emit per terminal:
       (word, story, tokidx, opens_before, closes_after, depth, gorn)"""
    toks = TOKEN.findall(tree)
    out = []
    stack = []            # gorn address: child index at each level
    child_counts = [0]
    opens_since_last = 0
    pending = None        # last terminal awaiting its closes_after count
    closes_after_last = 0
    i = 0
    while i < len(toks):
        t = toks[i]
        if t == "(":
            # label follows
            i += 1
            stack.append(child_counts[-1])
            child_counts[-1] += 1
            child_counts.append(0)
            opens_since_last += 1
        elif t == ")":
            child_counts.pop()
            if stack:
                stack.pop()
            if pending is not None:
                closes_after_last += 1
        else:
            # after a label token comes either "(" (non-terminal) or a terminal
            if "/" in t and re.search(r"/\d+\.\d+$", t):
                word, idx = t.rsplit("/", 1)
                story, tok = idx.split(".")
                if pending is not None:
                    out.append(pending + (closes_after_last,))
                pending = (word, int(story), int(tok), opens_since_last,
                           len(stack), tuple(stack))
                opens_since_last = 0
                closes_after_last = 0
            # else it's a phrase label; ignore
        i += 1
    if pending is not None:
        out.append(pending + (closes_after_last,))
    return out


rows = []
ntrees = 0
for tree in parse_trees(PENN):
    ntrees += 1
    for (word, story, tok, opens, depth, gorn, closes) in \
            terminals_with_context(tree):
        rows.append({"story_id": story, "tok_idx": tok, "parse_word": word,
                     "open_t": opens, "close_t": closes, "depth_t": depth,
                     "gorn": gorn})
P = pd.DataFrame(rows)
print(f"trees {ntrees}   terminals {len(P):,}   stories "
      f"{sorted(P.story_id.unique())}")

# transitions within sentence (gorn resets per tree, so compute within story
# by consecutive tok_idx; sentence boundaries handled by lca on ROOT resets)
P = P.sort_values(["story_id", "tok_idx"]).reset_index(drop=True)
same_parent = np.full(len(P), np.nan)
lca_dist = np.full(len(P), np.nan)
prev = None
for i, r in enumerate(P.itertuples()):
    if prev is not None and prev.story_id == r.story_id \
            and r.tok_idx == prev.tok_idx + 1:
        a, b = prev.gorn, r.gorn
        if len(a) == len(b) and a[:-1] == b[:-1]:
            same_parent[i] = 1.0
            lca_dist[i] = 0.0
        else:
            same_parent[i] = 0.0
            k = 0
            for x, y in zip(a, b):
                if x == y:
                    k += 1
                else:
                    break
            lca_dist[i] = max(len(b) - 1 - k, 0)
    prev = r
P["same_parent"] = same_parent
P["lca_dist"] = lca_dist

# ---------------- align to the locked sample ----------------
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

# corpus word_idx is 0-based per story; parse tok_idx is 1-based
P["word_idx"] = P.tok_idx - 1
M = S[["story_id", "word_idx", "word", "closure_depth"]].merge(
    P[["story_id", "word_idx", "parse_word", "open_t", "close_t", "depth_t",
       "same_parent", "lca_dist"]],
    on=["story_id", "word_idx"], how="left", validate="one_to_one")

matched = M.parse_word.notna()
print(f"\nsample words with a parse terminal: {matched.sum():,} / {len(M):,} "
      f"({matched.mean():.1%})")


def norm(w):
    return re.sub(r"[^A-Za-z0-9]", "", str(w)).lower()


ok = M[matched].apply(lambda r: norm(r.word) == norm(r.parse_word), axis=1)
print(f"word-form agreement: {ok.mean():.2%}  "
      f"({'PASS' if ok.mean() >= .99 else 'FAIL'} vs 99% prereg criterion)")
if not ok.all():
    bad = M[matched][~ok].head(8)
    print("  examples of mismatch:",
          [(r.word, r.parse_word) for r in bad.itertuples()])

agree = (M[matched].closure_depth == M[matched].close_t)
print(f"close_t vs sample closure_depth: {agree.mean():.2%} agreement")

M.drop(columns=["parse_word"]).to_csv(
    f"{GP}/gp_confound_check/syntax_vars_8a6087341e.csv", index=False)
print(f"\nwrote syntax_vars_8a6087341e.csv")
print("\ntransition class distribution (sample words with a preceding word):")
sub = M.dropna(subset=["lca_dist"])
print(sub.lca_dist.value_counts().sort_index().head(8).to_string())
print(f"  same_parent = 1: {sub.same_parent.mean():.1%}")
