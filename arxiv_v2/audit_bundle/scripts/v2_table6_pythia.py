"""
TABLE 6 RECOMPUTED: cross-architecture replication on MATCHED samples
=====================================================================
v1's Table 6 compared GPT-2 Small on the full Natural Stories sample (180
participants) against Pythia on a 100-participant subsample. That is not a
like-for-like architecture comparison. Here all models are evaluated on
identical rows and identical participants.

Pythia uses Rotary Position Embeddings; GPT-2 uses learned absolute position
embeddings. The question is whether the trajectory effect depends on the
positional encoding scheme.

Conventions match the verified GPT-2 pipeline: chunked forward passes
(1024 / stride 512, first-write-wins), word state = final subword, TEE_k3 =
distance from a one-step linear extrapolation over the 3 preceding word states,
mid-network layer. Words are restricted to the locked sample 8a6087341e.
"""

import numpy as np
import pandas as pd
import torch
import statsmodels.formula.api as smf
from transformers import AutoTokenizer, AutoModelForCausalLM
import os, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
CHUNK, STRIDE, K = 1024, 512, 3
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

MODELS = [("EleutherAI/pythia-160m", 6), ("EleutherAI/pythia-410m", 12)]

# ---------------- corpus (same construction as the verified pipeline) --------
words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
                    names=["id", "word"], dtype={"id": str, "word": str})
words = words[words.word.notna()].copy()
words = words[words.id.str.split(".").str[-1] == "whole"].copy()
words["word"] = words.word.str.strip().str.replace(r"\s+", "", regex=True)
words["story_id"] = words.id.str.split(".").str[0].astype(int)
words["word_idx"] = words.groupby("story_id").cumcount()
story_words = {s: g.word.tolist() for s, g in words.groupby("story_id")}
print(f"corpus: {len(words)} words, {len(story_words)} stories", flush=True)


def spans_for(wl):
    out, cur = [], 0
    for w in wl:
        out.append((cur, cur + len(w)))
        cur += len(w) + 1
    return out


def tee_for_model(name, layer):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name).eval().to(DEVICE)
    rows = []
    for sid, wl in story_words.items():
        text = " ".join(wl)
        enc = tok(text, return_offsets_mapping=True)
        ids = torch.tensor(enc["input_ids"])
        offs = enc["offset_mapping"]
        n = ids.size(0)
        hidden, pos = {}, 0
        while pos < n:
            end = min(pos + CHUNK, n)
            with torch.no_grad():
                out = model(ids[pos:end].unsqueeze(0).to(DEVICE),
                            output_hidden_states=True)
            hs = out.hidden_states[layer][0].float().cpu().numpy()
            for i in range(end - pos):
                g = pos + i
                if g not in hidden:
                    hidden[g] = hs[i]
            del out
            if end >= n:
                break
            pos += STRIDE
        sp = spans_for(wl)
        last_sub, wi = {}, 0
        for bi, (cs, ce) in enumerate(offs):
            if ce <= cs:
                continue
            while wi < len(sp) and cs >= sp[wi][1]:
                wi += 1
            if wi < len(sp) and cs >= sp[wi][0] and ce <= sp[wi][1]:
                last_sub[wi] = bi
        for w in range(len(sp)):
            if w not in last_sub:
                continue
            t = last_sub[w]
            idxs = [last_sub.get(w - j) for j in range(K, 0, -1)]
            if any(x is None for x in idxs) or any(x not in hidden for x in idxs):
                continue
            Y = np.stack([hidden[x] for x in idxs])
            m = Y.shape[0]
            A = np.column_stack([np.ones(m), np.arange(m)])
            c, *_ = np.linalg.lstsq(A, Y, rcond=None)
            rows.append({"story_id": sid, "word_idx": w,
                         "tee": float(np.linalg.norm(hidden[t] - (c[0] + c[1] * m)))})
        print(f"  {name} story {sid} done", flush=True)
    del model
    return pd.DataFrame(rows)


# ---------------- assemble ----------------
S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
base = S[["story_id", "word_idx", "zone", "surprisal", "word_length", "log_freq",
          "tee_k3"]].rename(columns={"tee_k3": "tee_gpt2"})

meas = base.copy()
for name, layer in MODELS:
    t = tee_for_model(name, layer)
    short = name.split("/")[-1].replace("-", "_")
    meas = meas.merge(t.rename(columns={"tee": f"tee_{short}"}),
                      on=["story_id", "word_idx"], how="left")
    print(f"{name}: {meas[f'tee_{short}'].notna().sum():,} words with TEE",
          flush=True)

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(meas, on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)

teecols = ["tee_gpt2"] + [f"tee_{n.split('/')[-1].replace('-', '_')}" for n, _ in MODELS]
d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone", "prev_log_RT",
                     "surprisal"] + teecols)
print(f"\nMATCHED SAMPLE: n = {len(d):,}, participants = {d.participant.nunique()}")


def z(s):
    v = s.dropna()
    return (s - v.mean()) / v.std()


for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal"] + teecols:
    d["z_" + c] = z(d[c])
CTRL = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_surprisal"
m1 = smf.mixedlm(CTRL, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
print(f"\n{'model':<20}{'positional enc':<18}{'dAIC':>10}{'beta':>11}{'p':>13}")
for c in teecols:
    mk = smf.mixedlm(CTRL + f" + z_{c}", d, groups=d["participant"]).fit(
        reml=False, method="lbfgs")
    enc = "absolute" if "gpt2" in c else "rotary (RoPE)"
    print(f"{c.replace('tee_',''):<20}{enc:<18}{m1.aic-mk.aic:>10.1f}"
          f"{mk.params['z_'+c]:>11.5f}{mk.pvalues['z_'+c]:>13.2e}")
print("\nAll rows and participants identical across models "
      "(v1 compared GPT-2 on 180 participants vs Pythia on 100).")
meas.to_csv(f"{GP}/gp_confound_check/pythia_tee_8a6087341e.csv", index=False)
