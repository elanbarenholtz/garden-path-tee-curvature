"""
E10 -- cross-domain straightening survey (EXPERIMENTS.md E10; readout fixed
before any non-language model was run).

For each (model, corpus): mean token-step curvature at every layer, trained
and random-init of the same architecture. Downloads (stated): codeparrot-
small ~500 MB, ProtGPT2 ~3 GB, Swiss-Prot sample ~1 MB.
"""
import os, sys, glob, random
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import GP, load_stories

MAXTOK, NSEQ, SEED = 512, 100, 20260814
OUT = f"{GP}/gp_confound_check/e10_domains_out.txt"


def curvature_by_layer(model, ids_list, device="cpu"):
    """Mean angle between successive steps, per layer, over all sequences."""
    nl = model.config.num_hidden_layers if hasattr(
        model.config, "num_hidden_layers") else model.config.n_layer
    sums = np.zeros(nl + 1)
    cnts = np.zeros(nl + 1)
    for ids in ids_list:
        tt = torch.tensor(ids[:MAXTOK]).unsqueeze(0)
        with torch.no_grad():
            o = model(tt, output_hidden_states=True)
        for L, h in enumerate(o.hidden_states):
            H = h[0].double().numpy()
            seg = np.diff(H, axis=0)
            nn = np.linalg.norm(seg, axis=1)
            ok = (nn[1:] > 1e-9) & (nn[:-1] > 1e-9)
            cosv = (seg[1:] * seg[:-1]).sum(1)[ok] / (nn[1:] * nn[:-1])[ok]
            ang = np.arccos(np.clip(cosv, -1, 1))
            sums[L] += ang.sum(); cnts[L] += len(ang)
        del o
    return sums / np.maximum(cnts, 1)


def report(name, model_id, ids_list):
    tok_note = f"{len(ids_list)} seqs, " \
               f"{sum(min(len(i), MAXTOK) for i in ids_list):,} tokens"
    model = AutoModelForCausalLM.from_pretrained(model_id).eval().float()
    trained = curvature_by_layer(model, ids_list)
    del model
    torch.manual_seed(SEED)
    cfg = AutoConfig.from_pretrained(model_id)
    rmodel = AutoModelForCausalLM.from_config(cfg).eval().float()
    untrained = curvature_by_layer(rmodel, ids_list)
    del rmodel
    lines = [f"\n=== {name}  ({model_id}; {tok_note}) ===",
             "layer   trained   untrained   (radians)"]
    for L in range(len(trained)):
        lines.append(f"  {L:>3}   {trained[L]:.4f}    {untrained[L]:.4f}")
    st = trained[1] - trained[1:].min()
    su = untrained[1] - untrained[1:].min()
    lines.append(f"STRAIGHTENING INDEX (layer1 - min deeper): "
                 f"trained {st:+.4f}   untrained {su:+.4f}")
    txt = "\n".join(lines)
    print(txt, flush=True)
    with open(OUT, "a") as f:
        f.write(txt + "\n")


random.seed(SEED)

# ---- English: GPT-2 on Natural Stories
tok = AutoTokenizer.from_pretrained("gpt2")
texts = load_stories("ns")
eng = [tok(t)["input_ids"] for t in list(texts.values())]
report("ENGLISH (Natural Stories)", "gpt2", eng)

# ---- Code: CodeParrot-small on human-written Python from site-packages
ctok = AutoTokenizer.from_pretrained("codeparrot/codeparrot-small")
site = glob.glob(os.path.expanduser(
    "~/Projects/ZuCo_TEE_Analysis/venv/lib/python*/site-packages/"
    "pandas/core/*.py"))
random.shuffle(site)
code_ids = []
for f in site:
    src = open(f, encoding="utf-8", errors="ignore").read()
    if len(src) < 2000:
        continue
    code_ids.append(ctok(src)["input_ids"])
    if len(code_ids) >= NSEQ:
        break
report("CODE (human-written Python)", "codeparrot/codeparrot-small",
       code_ids)

# ---- Protein: ProtGPT2 on Swiss-Prot sequences
import urllib.request
FASTA = f"{GP}/gp_confound_check/e10_swissprot.fasta"
if not os.path.exists(FASTA):
    url = ("https://rest.uniprot.org/uniprotkb/stream?format=fasta"
           "&query=reviewed:true+AND+length:[200 TO 400]&size=500")
    urllib.request.urlretrieve(url.replace(" ", "%20"), FASTA)
seqs, cur = [], []
for ln in open(FASTA):
    if ln.startswith(">"):
        if cur:
            seqs.append("".join(cur)); cur = []
    else:
        cur.append(ln.strip())
if cur:
    seqs.append("".join(cur))
random.shuffle(seqs)
seqs = seqs[:NSEQ]
ptok = AutoTokenizer.from_pretrained("nferruz/ProtGPT2")
# ProtGPT2 was trained on newline-broken FASTA-style sequences
prot_ids = [ptok("\n".join(s[i:i + 60] for i in range(0, len(s), 60))
                 )["input_ids"] for s in seqs]
report("PROTEIN (Swiss-Prot)", "nferruz/ProtGPT2", prot_ids)
