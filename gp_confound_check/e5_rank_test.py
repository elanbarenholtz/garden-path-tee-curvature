"""
E5: History Beyond the Current Predictive Distribution — rank test.
Preregistered in PREREG_E5_history_sufficiency.md (commits bcc9098, d9f59e4).

Per eligible token position t: sample 20 candidates from P_t (temp 1, no
truncation) + 1 pseudo-target (separate seed stream); compute each
continuation's deviation from the one-step OLS extrapolation of the preceding
3 token states (tee_at convention, k=3, token level); mid-rank percentile of
the human token (and, control, of the pseudo-target) among {target + 20}.

Modes (P_t model / geometry model+layer):
  v2a  gpt2        / gpt2 L6          (= V1a; the base rung)
  v1b  gpt2-xl     / gpt2 L6          (fixed geometry, stronger P_t)
  v2b  gpt2-xl     / gpt2-xl L24      (matched-model)
  v2c  pythia-410m / pythia-410m L12  (matched-model)
  v1c  pythia-410m / gpt2 L6          (cross-tokenizer rule, prereg clar. 6)

Usage:  e5_rank_test.py run <mode> [cpu|mps]     -> e5_positions_<mode>.csv
        e5_rank_test.py analyze <mode ...>       -> statistics + gates
"""
import os, sys, time, hashlib
import numpy as np
import pandas as pd

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
GPC = f"{GP}/gp_confound_check"
CHUNK, STRIDE, M = 1024, 512, 20
SEED_CAND, SEED_PSEUDO, SEED_BOOT = 20260814, 20260815, 20260816

MODES = {  # p_model, g_model, g_layer
    "v2a": ("gpt2", "gpt2", 6),
    "v1b": ("gpt2-xl", "gpt2", 6),
    "v2b": ("gpt2-xl", "gpt2-xl", 24),
    "v2c": ("EleutherAI/pythia-410m", "EleutherAI/pythia-410m", 12),
    "v1c": ("EleutherAI/pythia-410m", "gpt2", 6),
}


def load_stories(corpus="ns"):
    if corpus == "sbcsae":
        # E5b: Santa Barbara spontaneous speech, prepared by e5b_prepare.py
        # (cleaning decisions preregistered; cluster = conversation)
        df = pd.read_csv(f"{GPC}/sbcsae_texts.csv")
        return {int(r.conv_id): r.text for r in df.itertuples()}
    words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t",
                        header=None, names=["id", "word"],
                        dtype={"id": str, "word": str})
    words = words[words["word"].notna()].copy()
    words = words[words["id"].str.split(".").str[-1] == "whole"].copy()
    words["word"] = (words["word"].str.strip()
                     .str.replace(r"\s+", "", regex=True))
    words["story_id"] = words["id"].str.split(".").str[0].astype(int)
    sids = sorted(words["story_id"].unique())
    return {sid: " ".join(words.loc[words.story_id == sid, "word"])
            for sid in sids}


def first_write_ranges(n):
    p = 0
    while p < n:
        end = min(p + CHUNK, n)
        lo = 0 if p == 0 else p + STRIDE
        yield p, end, lo, min(end, n)
        if end >= n:
            break
        p += STRIDE


def chunk_states_and_logits(model, ids, layer, device, want_logits):
    """First-write-wins layer states for all tokens; per-position logits
    callback data: dict t -> softmax64 probs is too big, so we return
    (H, logits_rows) where logits_rows maps t -> np.float32 row."""
    import torch
    n = len(ids)
    H = np.full((n, model.config.hidden_size
                 if hasattr(model.config, "hidden_size")
                 else model.config.n_embd), np.nan, dtype=np.float32)
    written = np.zeros(n, dtype=bool)
    logits_rows = {}
    tt = torch.tensor(ids, device=device)
    for p, end, lo, hi in first_write_ranges(n):
        with torch.no_grad():
            out = model(tt[p:end].unsqueeze(0), output_hidden_states=True)
        hs = out.hidden_states[layer][0].float().cpu().numpy()
        lg = out.logits[0].float().cpu().numpy() if want_logits else None
        for g in range(p, end):
            if not written[g]:
                H[g] = hs[g - p]
                written[g] = True
        if want_logits:
            for t in range(max(lo, 1), hi):
                if t not in logits_rows:
                    logits_rows[t] = lg[t - 1 - p]
        del out
    assert written.all()
    return H, logits_rows


def sample_all(logits_rows, eligible, rng_c, rng_p):
    """Draw 20 candidates + 1 pseudo per eligible position, position order."""
    out = {}
    for t in sorted(eligible):
        row = logits_rows[t].astype(np.float64)
        row -= row.max()
        p = np.exp(row)
        p /= p.sum()
        cands = rng_c.choice(len(p), size=M, replace=True, p=p)
        pseudo = int(rng_p.choice(len(p), p=p))
        out[t] = (cands, pseudo)
    return out


def candidate_states(model, ids, layer, device, tasks, B=22):
    """tasks: dict t -> list of token ids (order preserved).
    Returns dict t -> np.ndarray [len, d] of layer states. Master chunk
    cache expanded to batch B (batch_repeat_interleave mutates in place,
    e5_probe2.py; batched step exact to ~1e-5); positions processed in
    descending order within each chunk's first-write range, cropping the
    cache back after every step (crop only shrinks)."""
    import torch
    n = len(ids)
    tt = torch.tensor(ids, device=device)
    res = {}
    for p, end, lo, hi in first_write_ranges(n):
        ts = sorted([t for t in tasks if max(lo, 1) <= t < hi
                     and t not in res], reverse=True)
        if not ts:
            continue
        with torch.no_grad():
            out = model(tt[p:end].unsqueeze(0), use_cache=True)
        cache = out.past_key_values
        del out
        cache.batch_repeat_interleave(B)
        for t in ts:
            toks = tasks[t]
            states = []
            for i in range(0, len(toks), B):
                grp = list(toks[i:i + B])
                npad = B - len(grp)
                inp = torch.tensor(grp + [grp[-1]] * npad,
                                   device=device).view(B, 1)
                cache.crop(t - p)
                with torch.no_grad():
                    st = model(inp, past_key_values=cache,
                               output_hidden_states=True)
                h = st.hidden_states[layer][:, 0, :].float().cpu().numpy()
                states.append(h[:len(grp)].copy())
                del st
            res[t] = np.concatenate(states, axis=0)
        del cache
    return res


def deviation(H, t, state):
    W = H[t - 3:t].astype(np.float64)
    A = np.column_stack([np.ones(3), np.arange(3, dtype=np.float64)])
    coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
    pred = coefs[0] + coefs[1] * 3
    return float(np.linalg.norm(state.astype(np.float64) - pred))


def midrank_u(d_target, d_others):
    less = float((d_others < d_target).sum())
    eq = float((d_others == d_target).sum())
    return (less + eq / 2.0 + 0.5) / (len(d_others) + 1)


def load_model(name, device):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(name)
    model = (AutoModelForCausalLM.from_pretrained(name)
             .eval().float().to(device))
    torch.set_num_threads(os.cpu_count() or 4)
    return tok, model


def run(mode, device, corpus="ns"):
    import torch
    p_name, g_name, g_layer = MODES[mode]
    cross = (mode == "v1c")
    pref = "e5" if corpus == "ns" else "e5b"
    texts = load_stories(corpus)
    p_tok, p_model = load_model(p_name, device)
    if g_name == p_name:
        g_tok, g_model = p_tok, p_model
    else:
        g_tok, g_model = load_model(g_name, device)

    rows = []
    val_max = 0.0
    for sid, text in texts.items():
        t0 = time.time()
        rng_c = np.random.default_rng([SEED_CAND, sid])
        rng_p = np.random.default_rng([SEED_PSEUDO, sid])
        g_enc = g_tok(text, return_offsets_mapping=True)
        g_ids = g_enc["input_ids"]
        nG = len(g_ids)
        # geometry states (fit windows) + validation source
        Hg, _ = chunk_states_and_logits(g_model, g_ids, g_layer, device,
                                        want_logits=False)
        if not cross:
            # sampling positions == geometry positions (same tokenizer)
            if p_name == g_name:
                p_ids = g_ids
            else:
                p_ids = p_tok(text)["input_ids"]
                assert p_ids == g_ids  # gpt2 family shares the tokenizer
            _, logits_rows = chunk_states_and_logits(
                p_model, p_ids, g_layer if p_name == g_name else 1,
                device, want_logits=True)
            eligible = [t for t in range(4, nG) if t in logits_rows]
            samples = sample_all(logits_rows, eligible, rng_c, rng_p)
            tasks = {t: [g_ids[t]] + list(samples[t][0]) + [samples[t][1]]
                     for t in eligible}
            st = candidate_states(g_model, g_ids, g_layer, device, tasks,
                                  B=8 if "xl" in g_name else 22)
            for t in eligible:
                S = st[t]
                d = np.array([deviation(Hg, t, s) for s in S])
                d_h, d_c, d_p = d[0], d[1:1 + M], d[1 + M]
                rows.append({
                    "story_id": sid, "t": t,
                    "u_human": midrank_u(d_h, d_c),
                    "u_pseudo": midrank_u(d_p, d_c),
                    "D_human": d_h, "D_pseudo": d_p,
                    "D_cand_mean": float(d_c.mean()),
                    "n_cand": M, "n_excl": 0,
                    "human_in_cands": int((np.array(samples[t][0])
                                           == g_ids[t]).sum())})
                # validation: human incremental state vs chunk-pass state
                val_max = max(val_max,
                              float(np.abs(S[0] - Hg[t]).max()))
        else:
            # v1c: Pythia P_t, GPT-2 geometry, boundary-aligned positions
            p_enc = p_tok(text, return_offsets_mapping=True)
            p_ids = p_enc["input_ids"]
            p_off = p_enc["offset_mapping"]
            g_off = g_enc["offset_mapping"]
            g_start = {s: i for i, (s, e) in enumerate(g_off)}
            _, logits_rows = chunk_states_and_logits(
                p_model, p_ids, 1, device, want_logits=True)
            aligned = {}
            for tp in range(1, len(p_ids)):
                s = p_off[tp][0]
                if tp in logits_rows and s in g_start and g_start[s] >= 4:
                    aligned[tp] = g_start[s]
            eligible = sorted(aligned)
            samples = sample_all(logits_rows, eligible, rng_c, rng_p)
            tasks, meta = {}, {}
            for tp in eligible:
                tg = aligned[tp]
                conts = [p_ids[tp]] + list(samples[tp][0]) + [samples[tp][1]]
                gtoks, keep = [], []
                for ci, cid in enumerate(conts):
                    txt = p_tok.decode([int(cid)])
                    gg = g_tok(txt)["input_ids"] if txt else []
                    if gg:
                        gtoks.append(gg[0])
                        keep.append(ci)
                if 0 not in keep or len(keep) < 5:
                    continue
                tasks.setdefault(tg, [])
                meta[tp] = (tg, len(tasks[tg]), gtoks, keep)
                tasks[tg].extend(gtoks)
            st = candidate_states(g_model, g_ids, 6, device, tasks)
            for tp in eligible:
                if tp not in meta:
                    continue
                tg, base, gtoks, keep = meta[tp]
                S = st[tg][base:base + len(gtoks)]
                d = np.array([deviation(Hg, tg, s) for s in S])
                pos = {ci: j for j, ci in enumerate(keep)}
                d_h = d[pos[0]]
                cand_idx = [pos[ci] for ci in range(1, 1 + M) if ci in pos]
                d_c = d[cand_idx]
                have_p = (1 + M) in pos
                d_p = d[pos[1 + M]] if have_p else np.nan
                rows.append({
                    "story_id": sid, "t": tp,
                    "u_human": midrank_u(d_h, d_c),
                    "u_pseudo": (midrank_u(d_p, d_c) if have_p else np.nan),
                    "D_human": d_h,
                    "D_pseudo": (d_p if have_p else np.nan),
                    "D_cand_mean": float(d_c.mean()),
                    "n_cand": len(d_c),
                    "n_excl": (1 + M + 1) - len(keep),
                    "human_in_cands": int((np.array(samples[tp][0])
                                           == p_ids[tp]).sum())})
        print(f"story {sid}: {sum(r['story_id'] == sid for r in rows):,} "
              f"positions in {time.time() - t0:.0f}s", flush=True)

    df = pd.DataFrame(rows)
    out = f"{GPC}/{pref}_positions_{mode}.csv"
    df.to_csv(out, index=False)
    print(f"\nwrote {out}  ({len(df):,} positions)")
    if not cross:
        print(f"VALIDATION (incremental vs chunk-pass human state): "
              f"max |diff| = {val_max:.2e}  "
              f"({'PASS' if val_max < 1e-3 else 'FAIL'})")
    if mode == "v2a" and corpus == "ns":
        vmax = 0.0
        for sid in texts:
            z = np.load(f"{GP}/extensions/states/story{sid}_states.npz")
            Hs = z["H"]
            g_ids = g_tok(texts[sid])["input_ids"]
            Hg, _ = chunk_states_and_logits(g_model, g_ids, 6, device, False)
            vmax = max(vmax, float(np.abs(Hs - Hg).max()))
        print(f"VALIDATION (chunk-pass states vs stored extensions/states): "
              f"max |diff| = {vmax:.2e}  "
              f"({'PASS' if vmax < 1e-3 else 'FAIL'})")


def analyze(modes, corpus="ns"):
    from scipy import stats
    rng = np.random.default_rng(SEED_BOOT)
    pref = "e5" if corpus == "ns" else "e5b"
    for mode in modes:
        f = f"{GPC}/{pref}_positions_{mode}.csv"
        if not os.path.exists(f):
            print(f"[{mode}] no output yet"); continue
        df = pd.read_csv(f)
        print("\n" + "=" * 72)
        print(f"{pref.upper()} [{mode}]  P_t = {MODES[mode][0]}   geometry = "
              f"{MODES[mode][1]} L{MODES[mode][2]}   n = {len(df):,}")
        print("=" * 72)
        sids = sorted(df.story_id.unique())
        for lab, col in [("CONTROL (pseudo-target)", "u_pseudo"),
                         ("HUMAN", "u_human")]:
            u = df[col].dropna()
            g = df.dropna(subset=[col]).groupby("story_id")[col]
            ssum, scnt = g.sum(), g.count()
            boots = np.empty(10000)
            for b in range(10000):
                pick = rng.choice(sids, size=len(sids), replace=True)
                boots[b] = (ssum.loc[pick].sum() / scnt.loc[pick].sum())
            lo_, hi_ = np.percentile(boots, [2.5, 97.5])
            w = stats.wilcoxon(u - 0.5)
            ks = stats.kstest(u, "uniform")
            excl = not (lo_ <= 0.5 <= hi_)
            print(f"\n  {lab}")
            print(f"    U = {u.mean():.4f}   95% story-bootstrap CI "
                  f"[{lo_:.4f}, {hi_:.4f}]"
                  f"   -> {'EXCLUDES 0.5' if excl else 'includes 0.5'}")
            print(f"    per-story U: " + " ".join(
                f"{(ssum/scnt).loc[s]:.3f}" for s in sids))
            print(f"    Wilcoxon p = {w.pvalue:.2e}   KS D = "
                  f"{ks.statistic:.4f} (p = {ks.pvalue:.2e})")
            if col == "u_pseudo":
                print(f"    GATE: {'PASS (uniform)' if not excl else 'FAIL — pipeline invalid, do not interpret human result'}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "run":
        run(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "cpu",
            sys.argv[4] if len(sys.argv) > 4 else "ns")
    elif cmd == "analyze":
        args = sys.argv[2:]
        corpus = "sbcsae" if "sbcsae" in args else "ns"
        modes = [a for a in args if a in MODES] or list(MODES)
        analyze(modes, corpus)
