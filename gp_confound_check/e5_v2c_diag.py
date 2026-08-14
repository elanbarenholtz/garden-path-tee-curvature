"""
E5 v2c control-gate diagnostic (prose, Pythia matched-model).
The preregistered pseudo-target control failed on this rung: U = 0.5049,
CI [0.503, 0.507], all 10 stories > 0.5. Per prereg the rung is
uninterpretable until diagnosed. Hypotheses, interpretation fixed now:

  H1 same-stream pseudo (21st draw of the CANDIDATE stream) also shifted
     -> machinery or statistic artifact, streams irrelevant.
  H2 only the separate-stream pseudo shifted -> RNG-stream related (would
     be bizarre; both are PCG64 with different seed words).
  H3 neither shifted -> the original failure was noise + an anti-conservative
     10-cluster bootstrap; gate criterion needs a stricter variance estimate,
     not the pipeline.
  H4 shift driven by positions where a sampled token falls in Pythia's
     untrained vocab padding (ids >= 50277 of 50304): report U with and
     without those positions.

Runs the identical machinery as e5_rank_test run v2c, with 22 sampled tokens
per position: 20 candidates + pseudoA (same stream, 21st draw) + pseudoB
(separate stream, as preregistered). No human token involved.
"""
import os, sys, time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import (GP, GPC, MODES, SEED_CAND, SEED_PSEUDO, M,
                          load_stories, chunk_states_and_logits,
                          candidate_states, deviation, midrank_u, load_model)

UNTRAINED_MIN = 50277  # pythia-410m tokenizer size; embedding rows beyond
                       # this are vocab padding, never trained

def main(device="cpu"):
    name, _, layer = MODES["v2c"]
    texts = load_stories("ns")
    tok, model = load_model(name, device)
    rows = []
    for sid, text in texts.items():
        t0 = time.time()
        rng_c = np.random.default_rng([SEED_CAND, sid])
        rng_p = np.random.default_rng([SEED_PSEUDO, sid])
        ids = tok(text)["input_ids"]
        n = len(ids)
        H, logits_rows = chunk_states_and_logits(model, ids, layer, device,
                                                 want_logits=True)
        eligible = [t for t in range(4, n) if t in logits_rows]
        tasks, draws = {}, {}
        for t in sorted(eligible):
            row = logits_rows[t].astype(np.float64)
            row -= row.max()
            p = np.exp(row); p /= p.sum()
            d21 = rng_c.choice(len(p), size=M + 1, replace=True, p=p)
            pB = int(rng_p.choice(len(p), p=p))
            draws[t] = (d21[:M], int(d21[M]), pB)
            tasks[t] = list(d21) + [pB]
        st = candidate_states(model, ids, layer, device, tasks, B=22)
        for t in eligible:
            cands, pA, pB = draws[t]
            S = st[t]
            d = np.array([deviation(H, t, s) for s in S])
            d_c, d_A, d_B = d[:M], d[M], d[M + 1]
            rows.append({
                "story_id": sid, "t": t,
                "u_pseudoA": midrank_u(d_A, d_c),
                "u_pseudoB": midrank_u(d_B, d_c),
                "any_untrained": int((np.concatenate([cands, [pA, pB]])
                                      >= UNTRAINED_MIN).any()),
                "D_A_minus_cmean": float(d_A - d_c.mean()),
                "D_B_minus_cmean": float(d_B - d_c.mean())})
        print(f"story {sid}: {len(eligible):,} in {time.time()-t0:.0f}s",
              flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(f"{GPC}/e5_v2c_diag.csv", index=False)

    rng = np.random.default_rng(20260817)
    sids = sorted(df.story_id.unique())
    print(f"\nn = {len(df):,}   positions with any untrained token: "
          f"{df.any_untrained.mean():.2%}")
    for lab, col, sub in [
            ("pseudoA (same stream)", "u_pseudoA", df),
            ("pseudoB (separate stream, prereg)", "u_pseudoB", df),
            ("pseudoB, untrained-token positions excluded", "u_pseudoB",
             df[df.any_untrained == 0])]:
        g = sub.groupby("story_id")[col]
        ssum, scnt = g.sum(), g.count()
        boots = np.empty(10000)
        for b in range(10000):
            pick = rng.choice(sids, size=len(sids), replace=True)
            boots[b] = ssum.loc[pick].sum() / scnt.loc[pick].sum()
        lo, hi = np.percentile(boots, [2.5, 97.5])
        print(f"  {lab}: U = {sub[col].mean():.4f}  CI [{lo:.4f}, {hi:.4f}]"
              f"  {'EXCLUDES 0.5' if not (lo <= .5 <= hi) else 'includes 0.5'}"
              f"  (D-cmean {sub['D_'+col[8]+'_minus_cmean'].mean():+.4f})")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cpu")
