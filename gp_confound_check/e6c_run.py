"""
E6c -- Buckeye word-level production latency (PREREG_E6_production_latency
Amendment 2 + Amendment 4, commits 5fb76e8 / latest; operationalization
fixed before any .words file was read).

Transitions: consecutive words by the talker with ONLY <SIL> (or nothing)
between them; <IVER>/noise/laughter intervening -> excluded (not
floor-holding). DV = log(1 + silence ms), clip [0, 5000]. Cluster = session
(>= 100 transitions); criterion Wilcoxon p < .01 AND >= 65% sessions
positive. Demeaning within talker. Context = talker's words per session.

Usage: e6c_run.py prepare | measures | analyze
"""
import os, re, sys, glob
import numpy as np
import pandas as pd
from scipy import stats
from wordfreq import zipf_frequency

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import GP, GPC, first_write_ranges, load_model

BW = f"{GP}/buckeye/words"
TRANS_CSV = f"{GPC}/e6c_transitions.csv"
TEXTS_CSV = f"{GPC}/e6c_texts.csv"
MEAS_CSV = f"{GPC}/e6c_word_measures.csv"


def parse_session(path):
    lines = open(path, encoding="latin-1").read().splitlines()
    started, prev_t, out = False, 0.0, []
    for ln in lines:
        if not started:
            if ln.strip() == "#":
                started = True
            continue
        m = re.match(r"\s*([\d.]+)\s+\d+\s+([^;]+)", ln)
        if not m:
            continue
        t, lab = float(m.group(1)), m.group(2).strip()
        out.append({"on": prev_t, "off": t, "lab": lab,
                    "word": not (lab.startswith("<") or lab.startswith("{"))})
        prev_t = t
    return out


def prepare():
    trows, texts = [], []
    for f in sorted(glob.glob(f"{BW}/*.words")):
        sess = os.path.basename(f).replace(".words", "")
        talker = sess[:3]
        ents = parse_session(f)
        words = [e for e in ents if e["word"] and e["lab"]]
        if len(words) < 200:
            print(f"{sess}: only {len(words)} words -- excluded")
            continue
        for i, w in enumerate(words):
            w["word_pos"] = i
        texts.append({"session": sess, "talker": talker,
                      "n_words": len(words),
                      "text": " ".join(w["lab"] for w in words)})
        idx = {id(e): k for k, e in enumerate(ents)}
        wlist = [(idx[id(w)], w) for w in words]
        run_pos = 0
        for (ka, a), (kb, b) in zip(wlist, wlist[1:]):
            between = ents[ka + 1:kb]
            clean = all(e["lab"] == "<SIL>" for e in between)
            if clean:
                run_pos += 1
            else:
                run_pos = 0
            if not clean:
                continue
            gap = (b["on"] - a["off"]) * 1000.0
            if gap < 0 or gap > 5000:
                continue
            trows.append({"session": sess, "talker": talker,
                          "word_pos": b["word_pos"], "gap_ms": gap,
                          "run_pos": run_pos})
    pd.DataFrame(texts).to_csv(TEXTS_CSV, index=False)
    D = pd.DataFrame(trows)
    D.to_csv(TRANS_CSV, index=False)
    print(f"{len(texts)} sessions, {sum(t['n_words'] for t in texts):,} "
          f"words, {len(D):,} clean transitions")
    print(f"gap: =0 {(D.gap_ms == 0).mean():.1%}   >0 "
          f"{(D.gap_ms > 0).mean():.1%}   >200 ms {(D.gap_ms>200).mean():.1%}"
          f"   median-of-positive "
          f"{D[D.gap_ms>0].gap_ms.median():.0f} ms")
    sess = D.groupby("session").size()
    print(f"sessions >= 100 transitions: {(sess >= 100).sum()}/{len(sess)}")
    print("DV SANITY GATE:",
          "PASS" if (D.gap_ms > 200).mean() > 0.02 else "FAIL")


def measures():
    import torch
    tok, model = load_model("gpt2", "cpu")
    T = pd.read_csv(TEXTS_CSV)
    first = not os.path.exists(MEAS_CSV)
    done = set() if first else set(pd.read_csv(MEAS_CSV).session.unique())
    for r in T.itertuples():
        if r.session in done:
            continue
        text = r.text
        words = text.split()
        spans, c = [], 0
        for w in words:
            spans.append((c, c + len(w))); c += len(w) + 1
        enc = tok(text, return_offsets_mapping=True)
        ids, offs = enc["input_ids"], enc["offset_mapping"]
        n = len(ids)
        bpe_word = np.full(n, -1); wi = 0
        for bi, (cs, ce) in enumerate(offs):
            while cs < ce and text[cs].isspace():
                cs += 1
            if ce <= cs:
                continue
            while wi < len(spans) and cs >= spans[wi][1]:
                wi += 1
            if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
                bpe_word[bi] = wi
        first_sub = np.full(len(words), -1); last_sub = np.full(len(words), -1)
        for bi, w in enumerate(bpe_word):
            if w >= 0:
                if first_sub[w] < 0:
                    first_sub[w] = bi
                last_sub[w] = bi
        assert (first_sub >= 0).all(), f"{r.session}: unmapped words"
        H = np.full((n, 768), np.nan, dtype=np.float32)
        surp = np.full(n, np.nan)
        F = {k: np.full(n, np.nan) for k in ("ent", "ren", "t1", "t10")}
        written = np.zeros(n, bool)
        tt = torch.tensor(ids)
        for p, end, lo, hi in first_write_ranges(n):
            with torch.no_grad():
                o = model(tt[p:end].unsqueeze(0), output_hidden_states=True)
            hs = o.hidden_states[6][0].float().numpy()
            lp = torch.log_softmax(o.logits[0].double(), dim=-1).numpy()
            for g in range(p, end):
                if not written[g]:
                    H[g] = hs[g - p]; written[g] = True
            for t in range(max(lo, 1), hi):
                if np.isnan(surp[t]):
                    row = lp[t - 1 - p]
                    surp[t] = -row[ids[t]]
                    pr = np.exp(row)
                    F["ent"][t] = float(-(pr * row).sum())
                    F["ren"][t] = float(-np.log((pr ** 2).sum()))
                    F["t1"][t] = float(row.max())
                    F["t10"][t] = float(np.log(np.sort(pr)[-10:].sum()))
            del o
        out = []
        for w in range(len(words)):
            t, fs = last_sub[w], first_sub[w]
            tee = np.nan
            if t - 3 >= 1:
                W = H[t - 3:t].astype(np.float64)
                A = np.column_stack([np.ones(3), np.arange(3.0)])
                cf, *_ = np.linalg.lstsq(A, W, rcond=None)
                tee = float(np.linalg.norm(H[t] - (cf[0] + cf[1] * 3)))
            out.append({"session": r.session, "word_pos": w, "tee": tee,
                        "surprisal": (np.nansum(surp[fs:t + 1])
                                      if fs >= 1 else np.nan),
                        "f_entropy": F["ent"][fs], "f_renyi2": F["ren"][fs],
                        "f_top1": F["t1"][fs], "f_top10": F["t10"][fs],
                        "word_length": len(words[w]),
                        "zipf": zipf_frequency(words[w].lower(), "en")})
        pd.DataFrame(out).to_csv(MEAS_CSV, mode="a", header=first,
                                 index=False)
        first = False
        print(f"{r.session} done", flush=True)


def analyze():
    D = pd.read_csv(TRANS_CSV)
    M = pd.read_csv(MEAS_CSV)
    D = D.merge(M, on=["session", "word_pos"], how="left")
    D["dv"] = np.log1p(D.gap_ms)
    D["l_run"] = np.log1p(D.run_pos)
    D["cum_words"] = np.log1p(D.word_pos)
    CTRL = ["surprisal", "f_entropy", "f_renyi2", "f_top1", "f_top10",
            "zipf", "word_length", "l_run", "cum_words"]
    use = ["dv", "tee"] + CTRL
    D = D[np.isfinite(D[use]).all(axis=1)].copy()
    for c in use:
        D[c] = D[c] - D.groupby("talker")[c].transform("mean")
    print(f"usable transitions: {len(D):,}   sessions "
          f"{D.session.nunique()}   talkers {D.talker.nunique()}")
    betas, ns = [], []
    for sess, s in D.groupby("session"):
        if len(s) < 100:
            continue
        X = np.column_stack([np.ones(len(s))] +
                            [(s[c] - s[c].mean()).values /
                             (s[c].std() if s[c].std() > 0 else 1)
                             for c in ["tee"] + CTRL])
        try:
            b, *_ = np.linalg.lstsq(X, s.dv.values, rcond=None)
        except np.linalg.LinAlgError:
            continue
        betas.append(b[1]); ns.append(len(s))
    betas = np.array(betas)
    pos = (betas > 0).mean()
    w = stats.wilcoxon(betas)
    print(f"\nsessions >= 100: {len(betas)} (median n {int(np.median(ns))})")
    print(f"TEE coefficient: mean {betas.mean():+.5f}  %pos {pos:.1%}  "
          f"Wilcoxon p {w.pvalue:.2e}")
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"\nPREREGISTERED CRITERION (Amendment 4): "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"descriptive: raw r(tee, dv) "
          f"{np.corrcoef(D.tee, D.dv)[0, 1]:+.4f}   "
          f"r(tee, gap>200ms) "
          f"{np.corrcoef(D.tee, (D.gap_ms > 200))[0, 1]:+.4f}")


if __name__ == "__main__":
    {"prepare": prepare, "measures": measures,
     "analyze": analyze}[sys.argv[1]]()
