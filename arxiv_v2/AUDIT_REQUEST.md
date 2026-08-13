# Independent audit request — arXiv:2606.05346v2

You are auditing a manuscript against the analysis outputs that produced it. Do
not recompute the analyses. Your job is to determine whether every claim in the
paper is actually supported by the material in this repository, and to find the
places where it is not.

**Assume there is at least one unsupported claim. Your task is to find it.** A
report that finds nothing will be treated as a failed audit, not a clean bill of
health.

---

## Why this is being asked

This manuscript is a correction of a previous version. Four substantive errors
have already been found and fixed in it, and knowing their shape will help you
look in the right places:

1. **A sample-construction error.** A lagged control was computed *after*
   filtering to a region of interest, silently dropping every observation at the
   first position. The reported N was correct arithmetic on the wrong sample.
2. **A mislabelled quantity.** The paper's framing claim was "nearly orthogonal
   to surprisal (r = .044)". The true correlation with surprisal is .31; .044
   was the correlation with *entropy*. The number was real, attached to the
   wrong variable.
3. **A corrupted control.** Word frequency was computed without lowercasing or
   stripping attached punctuation, and was zero for 19.7% of tokens. It partly
   functioned as a punctuation indicator. Every dependent number changed.
4. **A stale qualitative claim.** A Discussion paragraph described which words
   populate certain cells of a matrix; three of its examples occurred zero times
   in the cell they were attributed to.

The common thread is that **arithmetic was never the problem**. Numbers were
correct and attached to the wrong claim, or computed on the wrong rows, or
inherited from a superseded pipeline. Look for that, not for typos.

---

## Materials

| what | where |
|---|---|
| manuscript source | `manuscript.tex` (new/changed text is wrapped in `\new{}`) |
| compiled PDF | `manuscript.pdf` |
| references | `references.bib` |
| figures | `fig1_schematic.png`, `fig_core.png`, `fig3_dissociation.png`, `fig4_direction.png` |
| figure-generating code | `make_fig_core3.py`, `make_fig3.py` |
| analysis scripts | `../gp_confound_check/*.py` |
| analysis outputs | `../gp_confound_check/*_out.txt`, `*.txt`, `RESULTS_*.md` |
| locked samples | `../rebuild_v2_outputs/sample_8a6087341e.csv`, `../gp_confound_check/sap_measures_L6k3.csv` |
| existing weak check | `verify_numbers.py` — confirms each number appears *somewhere* in the outputs; it cannot tell whether it is attached to the right claim |

The garden-path reading-time corpus (`ClassicGardenPathSet.csv`, 180 MB) is not
included; it is third-party data available from the SAP Benchmark authors.

---

## What to check, in priority order

### 1. Provenance of every numeric claim

For each number in the manuscript, identify the specific output file and line it
came from, and confirm it is attached to the same quantity there. This is the
check that would have caught the `r = .044` error, and the one
`verify_numbers.py` cannot do.

Produce a table: `claim (with location) | value | source file:line | verdict |
note`. Verdicts: **matches** / **mismatch** / **not found** / **found but
describes a different quantity**.

### 2. Verbal claims that assert a result without a number

Phrases like "survives", "does not replicate", "strengthens", "is unaffected",
"reproduces". Each asserts an empirical outcome. Find the analysis behind it and
say whether it supports the wording. Pay attention to directional words —
*strengthens* and *weakens* have been wrong in this manuscript before.

### 3. Do the Methods describe what the code does?

Read the Methods section against the scripts. Check in particular:
- the specification of each model (which predictors, which random effects)
- how the measure is computed (layer, window, word-state convention, whether the
  first token can enter a fit window)
- filtering and exclusion rules, and their order relative to any lagged variable
- how word frequency is computed

Any discrepancy between description and code is a finding.

### 4. Internal consistency

The same quantity should agree wherever it appears — abstract, results text,
tables, figure captions, figures. Sample sizes and participant counts should be
consistent and should match the outputs.

### 5. Claims that outrun their evidence

Statements where the analysis supports something narrower than the sentence
says. Two specific things to weigh:
- the paper reports results from **two self-paced reading corpora** and claims
  the second is an out-of-sample application of decisions fixed on the first.
  Check whether the two specifications are in fact identical, and whether the
  text's characterisation of that is accurate.
- the paper reports a **pre-specified criterion** (65% sign agreement with group
  p < .01) and reports where it is not met. Check that it is applied
  consistently and that no result is described as supported where the criterion
  fails.

### 6. Anything the paper should report and does not

Analyses present in the scripts and outputs whose results do not appear in the
manuscript. For each, judge whether the omission is reasonable scoping or
selective reporting. Note that eye-tracking analyses were deliberately excluded
and deferred to separate work; that decision is documented in
`../GEOMETRY_PAPER_NOTES.md` and is not the kind of omission being asked about.

---

## Output

A single report with:

1. **Findings**, ordered by severity, each with: the claim, its location, what
   the evidence actually shows, and what would fix it.
2. **The provenance table** from step 1.
3. **A list of claims you could not verify**, and what would be needed.
4. **Your judgement** on whether the manuscript is safe to post, with reasons.

Be specific and quote the manuscript. Do not soften findings. If a claim is
unsupported, say so plainly rather than describing it as "potentially
overstated".
