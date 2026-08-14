"""Probe 2: does batch_repeat_interleave return a new cache? Time batched
candidate step vs crop-loop."""
import time
import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

tok = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
LAYER = 6
text = "The quick brown fox jumps over the lazy dog. " * 60
ids = torch.tensor(tok(text)["input_ids"])[:900]
cand = ids[400:422]

with torch.no_grad():
    out = model(ids[:400].unsqueeze(0), use_cache=True)
c = out.past_key_values
with torch.no_grad():
    full = model(torch.cat([ids[:400], cand[:1]]).unsqueeze(0),
                 output_hidden_states=True)
ref = full.hidden_states[LAYER][0, -1].numpy()

r = c.batch_repeat_interleave(22)
print("returns:", type(r).__name__ if r is not None else None,
      "orig batch now:", c.layers[0].keys.shape[0])
cc = r if r is not None else c
try:
    with torch.no_grad():
        step = model(cand.unsqueeze(1), past_key_values=cc,
                     output_hidden_states=True)
    h = step.hidden_states[LAYER][:, 0, :].numpy()
    print("batched step OK, err", np.abs(h[0] - ref).max())
    # timing: 50 positions, rebuild cache by cropping master each time
    with torch.no_grad():
        o = model(ids.unsqueeze(0), use_cache=True)
    master = o.past_key_values
    t0 = time.time()
    for t in range(890, 840, -1):
        master.crop(t)
        mm = master.batch_repeat_interleave(22)
        mm = mm if mm is not None else master
        with torch.no_grad():
            st = model(cand.unsqueeze(1), past_key_values=mm,
                       output_hidden_states=True)
        _ = st.hidden_states[LAYER][:, 0, :].numpy()
        if mm is master:
            master.crop(t)
    print(f"batched: 50 positions x 22 cands in {time.time()-t0:.1f}s")
except Exception as e:
    print("batched failed:", repr(e))

# crop-loop timing for the same 50 positions
with torch.no_grad():
    o = model(ids.unsqueeze(0), use_cache=True)
master = o.past_key_values
t0 = time.time()
for t in range(890, 840, -1):
    master.crop(t)
    for cd in cand:
        with torch.no_grad():
            st = model(cd.view(1, 1), past_key_values=master,
                       output_hidden_states=True)
        _ = st.hidden_states[LAYER][0, 0].numpy()
        master.crop(t)
print(f"crop-loop: 50 positions x 22 cands in {time.time()-t0:.1f}s")
