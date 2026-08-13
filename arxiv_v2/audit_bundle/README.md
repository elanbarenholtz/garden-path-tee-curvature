# Audit bundle — arXiv:2606.05346v2

Start with `AUDIT_REQUEST.md`. It states the task and, importantly, the shape of
the four errors already found in this manuscript.

```
manuscript.tex        the paper; text new in v2 is wrapped in \new{}
manuscript.pdf        compiled, in figures/
references.bib
verify_numbers.py     an existing weak check: confirms each number appears
                      SOMEWHERE in the outputs. It cannot tell whether a number
                      is attached to the right claim, which is the failure mode
                      that matters here.
outputs/              every analysis output the manuscript draws on
scripts/              the analysis code
samples/              locked measure samples, for checking row counts
figures/
```

Not included: `ClassicGardenPathSet.csv` (180 MB, third-party, from the SAP
Benchmark authors). Garden-path row counts therefore cannot be verified directly
from this bundle; Natural Stories can.
