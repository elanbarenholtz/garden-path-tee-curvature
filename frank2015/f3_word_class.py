"""
F3 -- word-class check for the Frank N400 curvature effect.
Spec fixed before results were seen (2026-10-06).

Question: is the positive curvature -> N400 effect (smaller N400 with higher
curvature) a function/content word confound? Function words have small N400s;
if they also produce sharper turns, curvature could be proxying word class.

Word class: closed-class list below (determiners, pronouns, prepositions,
conjunctions, auxiliaries/copulas, modals, particles, negation). Everything
else = content. Punctuation stripped, lower-cased before lookup.

Tests (same sample, covariates, two-way clustering as F2 PRIMARY):
  T1  PRIMARY model + function_word dummy        does curvature survive?
  T2  content words only                          is the effect there?
  T3  function words only
  T4  T1 + curvature x function_word interaction
Same for curvature_1 (F2 secondary b), since that was the stronger effect.
"""
import os, re, numpy as np, pandas as pd
import statsmodels.formula.api as smf

FUNCTION = set("""
a an the this that these those some any no every each either neither all both half
much many more most few fewer little less least several enough such what which whose
i me my mine myself you your yours yourself yourselves he him his himself she her hers herself
it its itself we us our ours ourselves they them their theirs themselves one ones
who whom whoever whatever whichever someone somebody something anyone anybody anything
everyone everybody everything nobody nothing none there here
of in on at by for with from to into onto upon about above across after against along
among around as before behind below beneath beside besides between beyond but despite down
during except inside like near off out outside over past since than through throughout till
toward towards under underneath until up via within without
and or nor so yet if because although though while whereas unless whether when where why how
once then also not n't never just only even too very
be am is are was were been being have has had having do does did done doing
will would shall should can could may might must ought
's 're 've 'd 'll 'm
""".split())

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/f2_n400_regression.py").read()
src = src.split("out = []")[0]                      # reuse F2's data prep verbatim
exec(src)


def clean(w): return re.sub(r"[^a-z']", "", str(w).lower())


L["function_word"] = L.word.map(lambda w: int(clean(w) in FUNCTION))
Wl = L.drop_duplicates("wid")
print(f"function words: {Wl.function_word.mean():.1%} of {len(Wl)} word tokens")
print("examples function:", sorted(set(Wl[Wl.function_word == 1].word.map(clean)))[:25])
print("examples content :", sorted(set(Wl[Wl.function_word == 0].word.map(clean)))[:15])
for c in ("curvature_3", "curvature_1"):
    g = Wl.groupby("function_word")[c].agg(["mean", "std", "count"])
    print(f"\n{c} by class (0=content, 1=function):\n{g.round(4)}")
g = L.groupby("function_word").n400.mean()
print(f"\nmean N400 by class: content {g[0]:+.3f}   function {g[1]:+.3f}")

rows = []
for curv in ("curvature_3", "curvature_1"):
    S = L[(L.final == 0) & L[curv].notna()]
    print(f"\n{'=' * 90}\n{curv}\n{'=' * 90}")
    specs = [("T0 F2 model (reference)", S, ""),
             ("T1 + function_word", S, " + function_word"),
             ("T2 content words only", S[S.function_word == 0], ""),
             ("T3 function words only", S[S.function_word == 1], ""),
             ("T4 + function_word + interaction", S, f" + function_word + z_{curv}:function_word")]
    for lab, F, add in specs:
        F = prep(F, COV + ["surprisal", "entropy", curv])
        rhs = zs(["surprisal", "entropy"] + COV) + f" + z_{curv}" + add
        q = fit(F, rhs)
        k = f"z_{curv}"
        extra = ""
        if "function_word" in add:
            extra += f"   fw {q.params['function_word']:+.3f} (t {q.tvalues['function_word']:.1f})"
        ik = f"z_{curv}:function_word"
        if ik in q.params:
            extra += f"   curv x fw {q.params[ik]:+.4f} (t {q.tvalues[ik]:.2f})"
        print(f"  {lab:<34} words {F.wid.nunique():>5}  beta {q.params[k]:+.4f}  "
              f"t {q.tvalues[k]:5.2f}  p {q.pvalues[k]:.2g}{extra}")
        rows.append(dict(measure=curv, test=lab, words=F.wid.nunique(), beta=q.params[k],
                         t=q.tvalues[k], p=q.pvalues[k]))
pd.DataFrame(rows).to_csv(f"{HERE}/f3_results.csv", index=False)
