"""
BUILD THE AUDIT BUNDLE
======================
Produces three things so the audit can be handed to another model whatever the
interface allows:

  audit_bundle/                  organised folder, for upload or a repo
  AUDIT_BUNDLE_core.md           single file: request + manuscript + every
                                 analysis output. ~180 KB. Sufficient for the
                                 provenance check, which is the main task.
  AUDIT_BUNDLE_full.md           the above plus every analysis script. Larger;
                                 use where context allows, since checking the
                                 Methods against the code needs the code.

Each embedded file is delimited with an explicit header so the auditor can cite
`file:line` precisely, and line numbers are added inside code and output blocks
for the same reason.
"""

import os, shutil, glob

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
ARX = f"{GP}/arxiv_v2"
GPC = f"{GP}/gp_confound_check"
OUT = f"{ARX}/audit_bundle"

MANUSCRIPT = ["manuscript.tex", "references.bib", "AUDIT_REQUEST.md",
              "verify_numbers.py", "make_fig_core3.py", "make_fig3.py"]
FIGS = ["fig1_schematic.png", "fig_core.png", "fig3_dissociation.png",
        "fig4_direction.png", "manuscript.pdf"]

shutil.rmtree(OUT, ignore_errors=True)
for sub in ["", "outputs", "scripts", "figures", "samples"]:
    os.makedirs(f"{OUT}/{sub}", exist_ok=True)

for f in MANUSCRIPT:
    if os.path.exists(f"{ARX}/{f}"):
        shutil.copy(f"{ARX}/{f}", f"{OUT}/{f}")
for f in FIGS:
    if os.path.exists(f"{ARX}/{f}"):
        shutil.copy(f"{ARX}/{f}", f"{OUT}/figures/{f}")

outs = sorted(set(glob.glob(f"{GPC}/*.txt") + glob.glob(f"{GPC}/RESULTS*.md")))
for f in outs:
    shutil.copy(f, f"{OUT}/outputs/{os.path.basename(f)}")
scripts = sorted(glob.glob(f"{GPC}/*.py"))
for f in scripts:
    shutil.copy(f, f"{OUT}/scripts/{os.path.basename(f)}")

# locked samples: the small ones only, so the auditor can check row counts
for src, name in [(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv",
                   "sample_8a6087341e.csv"),
                  (f"{GPC}/sap_measures_L6k3.csv", "sap_measures_L6k3.csv"),
                  (f"{GPC}/sap_bigsurp.csv", "sap_bigsurp.csv"),
                  (f"{GPC}/ns_pythia410m_surp_8a6087341e.csv",
                   "ns_pythia410m_surp_8a6087341e.csv")]:
    if os.path.exists(src):
        shutil.copy(src, f"{OUT}/samples/{name}")

with open(f"{OUT}/README.md", "w") as fh:
    fh.write("""# Audit bundle — arXiv:2606.05346v2

Start with `AUDIT_REQUEST.md`. It states the task and, importantly, the shape of
the four errors already found in this manuscript.

```
manuscript.tex        the paper; text new in v2 is wrapped in \\new{}
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
""")


def emit(fh, path, label, numbered=True):
    fh.write(f"\n\n{'=' * 78}\n### FILE: {label}\n{'=' * 78}\n\n```\n")
    try:
        for i, line in enumerate(open(path, errors="ignore"), 1):
            fh.write(f"{i:>5} | {line.rstrip()}\n" if numbered else line)
    except Exception as e:
        fh.write(f"[unreadable: {e}]\n")
    fh.write("```\n")


def build(target, include_scripts):
    with open(target, "w") as fh:
        fh.write(open(f"{ARX}/AUDIT_REQUEST.md").read())
        fh.write("\n\n" + "#" * 78 + "\n# MANUSCRIPT\n" + "#" * 78 + "\n")
        emit(fh, f"{ARX}/manuscript.tex", "manuscript.tex")
        fh.write("\n\n" + "#" * 78 + "\n# ANALYSIS OUTPUTS\n" + "#" * 78 + "\n")
        for f in outs:
            emit(fh, f, f"gp_confound_check/{os.path.basename(f)}")
        if include_scripts:
            fh.write("\n\n" + "#" * 78 + "\n# ANALYSIS SCRIPTS\n"
                     + "#" * 78 + "\n")
            for f in scripts:
                emit(fh, f, f"gp_confound_check/{os.path.basename(f)}")
    kb = os.path.getsize(target) / 1024
    print(f"  {os.path.basename(target):<26} {kb:>8.0f} KB  "
          f"(~{kb * 1024 / 4 / 1000:.0f}k tokens)")


print("bundle contents:")
print(f"  outputs {len(outs)}   scripts {len(scripts)}   "
      f"figures {len(FIGS)}")
build(f"{ARX}/AUDIT_BUNDLE_core.md", False)
build(f"{ARX}/AUDIT_BUNDLE_full.md", True)
shutil.make_archive(f"{ARX}/audit_bundle", "zip", OUT)
print(f"  audit_bundle.zip           "
      f"{os.path.getsize(f'{ARX}/audit_bundle.zip')/1024:>8.0f} KB")
