"""
E9 part F -- untrained-representation control (PREREG_E9_curvature.md,
section F, committed before this run).

Curvature_3 from a randomly initialized GPT-2 (torch seed 20260814, same
architecture/tokenizer/layer/chunking) on the locked NS sample, in the
headline RT specification. If untrained-model curvature predicts reading
time, the geometry is generic; if it is null while trained-model curvature
stands, learning puts the behaviorally relevant geometry into the
coordinates.
"""
import os, sys, hashlib
import numpy as np
import pandas as pd
import torch
from transformers import GPT2LMHeadModel, GPT2Config, GPT2TokenizerFast
from scipy import stats
from wordfreq import zipf_frequency

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import GP, GPC, load_stories, first_write_ranges

LAYER = 6
torch.manual_seed(20260814)
model = GPT2LMHeadModel(GPT2Config()).eval()
tok = GPT2TokenizerFast.from_pretrained("gpt2")

S = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv"
                ).rename(columns={"curvature_3": "curv3"})
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()
     ).hexdigest()[:10]
assert sh == "8a6087341e", sh

texts = load_stories("ns")
rows = []
for sid, text in texts.items():
    z = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
    last_sub = z["last_sub"]
    ids = tok(text)["input_ids"]
    n = len(ids)
    H = np.full((n, 768), np.nan, dtype=np.float32)
    written = np.zeros(n, bool)
    tt = torch.tensor(ids)
    for p, end, lo, hi in first_write_ranges(n):
        with torch.no_grad():
            o = model(tt[p:end].unsqueeze(0), output_hidden_states=True)
        hs = o.hidden_states[LAYER][0].float().numpy()
        for g in range(p, end):
            if not written[g]:
                H[g] = hs[g - p]; written[g] = True
        del o
    for r in S[S.story_id == sid].itertuples():
        ls = int(last_sub[r.word_idx])
        cu = np.nan
        if ls - 4 >= 1:
            seg = np.diff(H[ls - 4:ls + 1].astype(np.float64), axis=0)
            nn = np.linalg.norm(seg, axis=1)
            if (nn > 1e-9).all():
                cosv = (seg[1:] * seg[:-1]).sum(1) / (nn[1:] * nn[:-1])
                cu = float(np.arccos(np.clip(cosv, -1, 1)).mean())
        rows.append({"story_id": sid, "word_idx": r.word_idx,
                     "curv3_untrained": cu})
    print(f"story {sid} done", flush=True)

U = pd.DataFrame(rows)
S = S.merge(U, on=["story_id", "word_idx"], how="left")
print(f"\nr(trained curv3, untrained curv3) = "
      f"{S.curv3.corr(S.curv3_untrained):+.3f}")
print(f"untrained curv3: mean {S.curv3_untrained.mean():.3f} rad "
      f"(trained: {S.curv3.mean():.3f})")

S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
                       .str.lower().map(lambda w: zipf_frequency(w, "en")))
rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
d = rt.merge(S[["story_id", "zone", "curv3", "curv3_untrained", "surprisal",
                "word_length", "log_freq_fixed"]],
             on=["story_id", "zone"], how="inner")
d["log_RT"] = np.log(d.RT)
d = d.sort_values(["participant", "story_id", "zone"])
d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
BASE = ["word_length", "log_freq_fixed", "zone", "prev_log_RT", "surprisal"]
D = d.dropna(subset=["log_RT", "curv3", "curv3_untrained"] + BASE).copy()
print(f"RT rows {len(D):,}  participants {D.participant.nunique()}")


def zs(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def subj(xcol, cov, label):
    bs = []
    for pid, s in D.groupby("participant"):
        s = s.dropna(subset=["log_RT", xcol] + cov)
        if len(s) < 100:
            continue
        X = np.column_stack([zs(s[c].values) for c in [xcol] + cov])
        if (X.std(axis=0) == 0).any():
            continue
        X = np.column_stack([np.ones(len(s)), X])
        b, *_ = np.linalg.lstsq(X, s.log_RT.values, rcond=None)
        bs.append(b[1])
    bs = np.array(bs)
    pos = (bs > 0).mean()
    w = stats.wilcoxon(bs)
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"  {label:<44} n {len(bs)}  beta {bs.mean():+.5f}  "
          f"%pos {pos:.1%}  p {w.pvalue:.2e}  {'PASS' if ok else 'FAIL'}")


print("\nUNTRAINED-REPRESENTATION CONTROL (headline spec)")
subj("curv3_untrained", BASE, "untrained curv3 | base")
subj("curv3", BASE, "trained curv3 | base (ref)")
subj("curv3", BASE + ["curv3_untrained"], "trained | base + untrained")
subj("curv3_untrained", BASE + ["curv3"], "untrained | base + trained")
