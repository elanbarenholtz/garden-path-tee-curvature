"""
CHECK EVERY REPORTED STATISTIC IN THE MANUSCRIPT AGAINST THE RESULTS FILES
==========================================================================
The recurring failure mode in this project is not bad analysis but bad
transcription: a number computed by one pipeline being reported in prose that
was written against another. r = .044 (an entropy correlation reported as a
surprisal correlation), N = 95,173 (a sample that silently excluded ROI 0), and
the off-diagonal word examples all had this shape. Each was caught by hand,
late.

This does the check mechanically. It extracts every statistic-like number from
manuscript.tex and asks whether that value appears anywhere in the analysis
output files. A number that appears nowhere is either stale (carried over from
v1), mistyped, or computed somewhere that was never saved -- all three are
things to resolve before uploading.

WHAT IT WILL AND WILL NOT CATCH
  catches:  numbers in the text that no analysis produced
  catches:  v1 values left behind after a rewrite
  misses:   a number that is correct in the outputs but attached to the wrong
            claim in the prose (the r = .044 error would NOT have been caught,
            since .044 did exist -- as an entropy correlation)
So this is a necessary check, not a sufficient one. Provenance of a claim still
has to be read by a human.

Scope: numbers with a decimal point, or integers >= 1000. Bare small integers
(layer 6, k = 3, 24 items, years) are excluded as low-information.
"""

import re, glob, os
from collections import defaultdict

ARX = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/arxiv_v2"
GPC = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
TEX = f"{ARX}/manuscript.tex"

SOURCES = sorted(
    glob.glob(f"{GPC}/*_out.txt") + glob.glob(f"{GPC}/*out.txt")
    + glob.glob(f"{GPC}/RESULTS*.md") + glob.glob(f"{GPC}/*.txt")
)
SOURCES = sorted(set(SOURCES))

# values that are definitional / structural rather than results
IGNORE = {
    768.0, 1024.0, 512.0, 3000.0, 5000.0, 100.0,      # dims, context, RT filters
    2023.0, 2024.0, 2025.0, 2018.0, 2019.0, 2013.0,   # years
    117.0, 345.0, 774.0, 160.0, 410.0,                # model sizes
    0.8, 12.0, 6.0, 5.0, 3.0, 2.0, 1.0, 0.5,
    2606.05346,
}

NUM = re.compile(r"[-+]?\d*\.?\d+(?:\s*\\times\s*10\^\{-?\d+\})?")


def parse_tex_numbers(path):
    txt = open(path).read()
    txt = "\n".join(l for l in txt.split("\n") if not l.strip().startswith("%"))
    out = []
    for m in re.finditer(
            r"([-+]?\d[\d{},]*\.?\d*)(\s*\\times\s*10\^\{(-?\d+)\})?", txt):
        raw = m.group(0)
        base = m.group(1).replace("{,}", "").replace(",", "")
        try:
            v = float(base)
        except ValueError:
            continue
        if m.group(3):
            v *= 10 ** int(m.group(3))
        # scope filter
        if "." not in base and abs(v) < 1000:
            continue
        if abs(v) in IGNORE:
            continue
        ctx = txt[max(0, m.start() - 70):m.end() + 40].replace("\n", " ")
        out.append((v, raw.strip(), " ".join(ctx.split())))
    return out


def parse_source_numbers(paths):
    vals = set()
    where = defaultdict(set)
    pat = re.compile(r"[-+]?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?")
    for p in paths:
        try:
            txt = open(p, errors="ignore").read()
        except Exception:
            continue
        for m in pat.finditer(txt):
            s = m.group(0).replace(",", "")
            try:
                v = float(s)
            except ValueError:
                continue
            vals.add(v)
            where[round(v, 6)].add(os.path.basename(p))
    return vals, where


def matches(v, pool):
    """Does any source value equal v to the precision v is reported at?"""
    for cand in (v, v / 100.0, v * 100.0):
        for s in pool:
            if s == 0 and cand == 0:
                return True
            if cand != 0 and abs(s - cand) <= max(abs(cand) * 5e-3, 5e-4):
                return True
            # p-values: compare on a log scale, they're often rounded hard
            if 0 < cand < 1e-3 and 0 < s < 1e-3:
                import math
                if abs(math.log10(s) - math.log10(cand)) < 0.35:
                    return True
    return False


tex_nums = parse_tex_numbers(TEX)
src_vals, src_where = parse_source_numbers(SOURCES)
print(f"source files scanned: {len(SOURCES)}")
for s in SOURCES:
    print(f"   {os.path.basename(s)}")
print(f"\ndistinct numeric values in sources: {len(src_vals):,}")
print(f"statistic-like numbers in manuscript: {len(tex_nums)}\n")

unmatched = []
for v, raw, ctx in tex_nums:
    if not matches(v, src_vals):
        unmatched.append((v, raw, ctx))

print("=" * 78)
print(f"NUMBERS IN THE MANUSCRIPT WITH NO MATCH IN ANY RESULTS FILE: "
      f"{len(unmatched)}")
print("=" * 78)
for v, raw, ctx in unmatched:
    print(f"\n  value: {raw}   (parsed {v:g})")
    print(f"  context: ...{ctx}...")

print("\n" + "=" * 78)
print("VERDICT")
print("=" * 78)
if not unmatched:
    print("  Every statistic-like number in the manuscript appears in an")
    print("  analysis output file.")
else:
    print(f"  {len(unmatched)} number(s) need provenance checked by hand.")
    print("  Each is either (a) carried over from v1, (b) mistyped, or")
    print("  (c) computed in a run whose output was never saved.")
print("\n  NOTE: this cannot detect a correct number attached to the wrong")
print("  claim. The r = .044 error would have passed this check.")
