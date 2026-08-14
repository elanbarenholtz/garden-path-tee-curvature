"""E5 build probe: cache API surface + candidate-forward strategy check.
Verifies that the incremental candidate forward reproduces the full-sequence
hidden state, and times the options. Not an analysis; no corpus statistics.
"""
import time
import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

torch.manual_seed(0)
tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
LAYER = 6

text = "The quick brown fox jumps over the lazy dog. " * 40
ids = torch.tensor(tok(text)["input_ids"])[:600]
prefix = ids[:400]

with torch.no_grad():
    out = model(prefix.unsqueeze(0), use_cache=True)
cache = out.past_key_values
print("cache type:", type(cache).__name__)
print("methods:", [m for m in dir(cache) if not m.startswith("_")])

# reference: full-sequence forward, hidden state of appended token
cand = ids[400:422]  # 22 "candidates"
with torch.no_grad():
    full = model(torch.cat([prefix, cand[:1]]).unsqueeze(0),
                 output_hidden_states=True)
ref = full.hidden_states[LAYER][0, -1].numpy()

# Strategy A: batch_repeat_interleave on the cache, one batched step
okA = False
try:
    with torch.no_grad():
        o2 = model(prefix.unsqueeze(0), use_cache=True)
    c2 = o2.past_key_values
    c2.batch_repeat_interleave(22)
    with torch.no_grad():
        step = model(cand.unsqueeze(1), past_key_values=c2,
                     output_hidden_states=True)
    hA = step.hidden_states[LAYER][:, 0, :].numpy()
    errA = np.abs(hA[0] - ref).max()
    print(f"A batch_repeat_interleave: OK, max err vs ref {errA:.2e}")
    okA = errA < 1e-3
except Exception as e:
    print("A failed:", repr(e))

# Strategy B: sequential single-token forwards with crop-back
okB = False
try:
    with torch.no_grad():
        o3 = model(prefix.unsqueeze(0), use_cache=True)
    c3 = o3.past_key_values
    L = prefix.shape[0]
    hs = []
    t0 = time.time()
    for cd in cand:
        with torch.no_grad():
            st = model(cd.view(1, 1), past_key_values=c3,
                       output_hidden_states=True)
        hs.append(st.hidden_states[LAYER][0, 0].numpy().copy())
        c3.crop(L)
    tB = time.time() - t0
    errB = np.abs(hs[0] - ref).max()
    print(f"B crop-loop: OK, max err {errB:.2e}, 22 cands in {tB:.2f}s")
    okB = errB < 1e-3
except Exception as e:
    print("B failed:", repr(e))

# timing: chunk forward + per-position prefix forward, cpu vs mps
for dev in ["cpu", "mps"]:
    try:
        m = model.to(dev)
        idsd = ids.to(dev)
        t0 = time.time()
        for _ in range(3):
            with torch.no_grad():
                m(idsd[:400].unsqueeze(0), use_cache=True)
        print(f"{dev}: prefix-400 forward {(time.time()-t0)/3*1000:.0f} ms")
    except Exception as e:
        print(dev, "failed:", repr(e))
model.to("cpu")
print("verdict: A" if okA else ("verdict: B" if okB else "verdict: NONE"))
