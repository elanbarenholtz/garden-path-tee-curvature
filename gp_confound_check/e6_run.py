"""
E6a -- analysis specified in PREREG_E6_production_latency.md (commit ab1145b,
before any timing extraction). Do speakers pause longer before launching
intonation units whose first word departs from the recent trajectory?

Stage 1 (preparation, permitted): parse TRN with IU timing + speakers;
  reproduce the cleaned word sequence and VALIDATE it against the committed
  sbcsae_texts.csv (must match exactly); extract within-speaker turn-internal
  transitions; report counts. No model measure touches timing here.
Stage 2: GPT-2 Small word-level measures over the interleaved text (paper's
  TEE convention: token window k=3 ending at the word's last subword),
  surprisal (subword sum), E7 functionals at the first subword. Streaming
  softmax per chunk (no stored logit matrix).
Stage 3 (criterion): within-speaker demeaning, per-conversation OLS,
  Wilcoxon p < .01 AND >= 65% of conversations positive.

Usage: e6_run.py prepare | measures | analyze
"""
import os, re, sys, glob
import numpy as np
import pandas as pd
from scipy import stats
from wordfreq import zipf_frequency

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import GP, GPC, first_write_ranges, load_model

TRN = f"{GP}/sbcsae/TRN"
TRANS_CSV = f"{GPC}/e6_transitions.csv"
MEAS_CSV = f"{GPC}/e6_word_measures.csv"


def clean_line(t):
    """Identical cleaning to e5b_prepare.py (validated against its output)."""
    t = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", t)  # embedded NUL etc.
    t = re.sub(r"\(\(.*?\)\)", " ", t)
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"<{1,2}\s*[A-Z%@]{1,6}\b", " ", t)
    t = re.sub(r"\b[A-Z%@]{1,6}\s*>{1,2}", " ", t)
    t = t.replace("<", " ").replace(">", " ")
    t = re.sub(r"\[\d?", " ", t)
    t = re.sub(r"\d?\]", " ", t)
    t = t.replace("=", "").replace("~", "")
    t = re.sub(r"@+", " ", t)
    t = re.sub(r"\.\.+", " ", t)
    t = t.replace("--", " ").replace("%", " ")
    out = []
    for w in t.split():
        wl = w.strip(",.?!;:\"`'")
        core = re.sub(r"[^A-Za-z']", "", wl)
        if not core or re.fullmatch(r"X{1,4}", core):
            continue
        out.append(wl.rstrip("-"))
    return [w for w in out if w]


def prepare():
    T = pd.read_csv(f"{GPC}/sbcsae_texts.csv")
    ref = {int(r.conv_id): r.text.split() for r in T.itertuples()}
    rows, bad = [], 0
    for f in sorted(glob.glob(f"{TRN}/SBC*.trn")):
        conv = int(re.search(r"SBC(\d+)", f).group(1))
        if conv not in ref:
            continue
        for enc in ("utf-8", "latin-1"):
            try:
                lines = open(f, encoding=enc).read().splitlines(); break
            except UnicodeDecodeError:
                continue
        ius, spk, wpos = [], None, 0
        for ln in lines:
            parts = ln.split("\t")
            if len(parts) < 2:
                continue
            p0 = parts[0].strip()
            if (re.fullmatch(r"[\d.]+", p0) and len(parts) >= 3
                    and re.fullmatch(r"[\d.]+", parts[1].strip())):
                # tab-separated format (SBC014+): start \t end \t spk \t text
                on, off = float(p0), float(parts[1])
                lab = parts[2].strip()
            else:
                m = re.match(r"\s*([\d.]+)\s+([\d.]+)", parts[0])
                if not m:
                    # e5b_prepare kept these lines' words; keep alignment
                    wpos += len(clean_line(parts[-1]))
                    continue
                on, off = float(m.group(1)), float(m.group(2))
                lab = parts[1].strip() if len(parts) >= 3 else ""
            if lab.endswith(":"):
                spk = lab[:-1]
            raw = parts[-1]
            lead = re.sub(r"^(\s|\[\d?|\([^)]*\))*", "", raw)
            pdots = re.match(r"(\.\.+)", lead)
            words = clean_line(raw)
            ius.append({"on": on, "off": off, "spk": spk,
                        "w0": wpos, "n": len(words),
                        "pmark": int(bool(pdots)),
                        "plen": len(pdots.group(1)) if pdots else 0})
            wpos += len(words)
        got = wpos
        want = len(ref[conv])
        if got != want:
            print(f"SBC{conv:03d}: word count {got} != texts {want} -- SKIP")
            bad += 1
            continue
        for i in range(1, len(ius)):
            a, b = ius[i - 1], ius[i]
            if (b["spk"] != a["spk"] or b["spk"] is None or b["n"] == 0):
                continue
            gap = (b["on"] - a["off"]) * 1000.0
            rows.append({"conv_id": conv, "speaker": f"{conv}_{b['spk']}",
                         "word_pos": b["w0"], "pause_ms": gap,
                         "pause_mark": b["pmark"], "pause_len": b["plen"],
                         "iu_len": b["n"], "iu_len_prev": a["n"],
                         "on": b["on"]})
    D = pd.DataFrame(rows)
    D.to_csv(TRANS_CSV, index=False)
    print(f"\nALIGNMENT GATE: {60 - bad}/60 conversations reproduce the "
          f"committed word sequence exactly ({'PASS' if bad == 0 else 'FAIL'})")
    print(f"{len(D):,} within-speaker turn-internal transitions "
          f"({len(D) / max(1, D.conv_id.nunique()):.0f}/conversation)")
    print(f"negative gaps (overlap-latched): {(D.pause_ms < 0).mean():.1%}"
          f"   > 200 ms: {(D.pause_ms > 200).mean():.1%}")
    print(f"pause_mark rate (AMENDMENT 1 primary DV): "
          f"{D.pause_mark.mean():.1%}   long (3+ dots): "
          f"{(D.pause_len >= 3).mean():.1%}")


def measures():
    import torch
    tok, model = load_model("gpt2", "cpu")
    T = pd.read_csv(f"{GPC}/sbcsae_texts.csv")
    out = []
    for r in T.itertuples():
        conv, text = int(r.conv_id), r.text
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
        assert (first_sub >= 0).all(), f"conv {conv}: unmapped words"
        H = np.full((n, 768), np.nan, dtype=np.float32)
        surp = np.full(n, np.nan)
        fent = np.full(n, np.nan); fren = np.full(n, np.nan)
        ftop1 = np.full(n, np.nan); ftop10 = np.full(n, np.nan)
        written = np.zeros(n, bool)
        tt = torch.tensor(ids)
        for p, end, lo, hi in first_write_ranges(n):
            with torch.no_grad():
                o = model(tt[p:end].unsqueeze(0), output_hidden_states=True)
            hs = o.hidden_states[6][0].float().numpy()
            lg = o.logits[0].double()
            lp = torch.log_softmax(lg, dim=-1).numpy()
            for g in range(p, end):
                if not written[g]:
                    H[g] = hs[g - p]; written[g] = True
            for t in range(max(lo, 1), hi):
                if np.isnan(surp[t]):
                    row = lp[t - 1 - p]
                    surp[t] = -row[ids[t]]
                    pr = np.exp(row)
                    fent[t] = float(-(pr * row).sum())
                    fren[t] = float(-np.log((pr ** 2).sum()))
                    ftop1[t] = float(row.max())
                    ftop10[t] = float(np.log(np.sort(pr)[-10:].sum()))
            del o
        for w in range(len(words)):
            t = last_sub[w]
            fs = first_sub[w]
            tee = np.nan
            if t - 3 >= 1:
                W = H[t - 3:t].astype(np.float64)
                A = np.column_stack([np.ones(3), np.arange(3.0)])
                cf, *_ = np.linalg.lstsq(A, W, rcond=None)
                tee = float(np.linalg.norm(H[t] - (cf[0] + cf[1] * 3)))
            ssum = np.nansum(surp[first_sub[w]:last_sub[w] + 1]) \
                if fs >= 1 else np.nan
            out.append({"conv_id": conv, "word_pos": w, "tee": tee,
                        "surprisal": ssum, "f_entropy": fent[fs],
                        "f_renyi2": fren[fs], "f_top1": ftop1[fs],
                        "f_top10": ftop10[fs],
                        "word_length": len(words[w]),
                        "zipf": zipf_frequency(
                            words[w].strip(",.?!;:\"'").lower(), "en")})
        print(f"conv {conv} done", flush=True)
    pd.DataFrame(out).to_csv(MEAS_CSV, index=False)
    print(f"wrote {MEAS_CSV}")


def analyze():
    D = pd.read_csv(TRANS_CSV)
    M = pd.read_csv(MEAS_CSV)
    D = D.merge(M, on=["conv_id", "word_pos"], how="left")
    # AMENDMENT 1: primary DV = transcriber-coded hesitation mark
    D["dv"] = D.pause_mark.astype(float)
    D = D.sort_values(["conv_id", "on"])
    D["turn_pos"] = np.log1p(D.groupby(
        (D.speaker != D.speaker.shift()).cumsum()).cumcount())
    D["cum_words"] = np.log1p(D.word_pos)
    D["l_iu"] = np.log1p(D.iu_len); D["l_iup"] = np.log1p(D.iu_len_prev)
    CTRL = ["surprisal", "f_entropy", "f_renyi2", "f_top1", "f_top10",
            "zipf", "word_length", "l_iu", "l_iup", "turn_pos", "cum_words"]
    use = ["dv", "tee"] + CTRL
    D = D[np.isfinite(D[use]).all(axis=1)].copy()
    for c in ["dv", "tee"] + CTRL:
        D[c] = D[c] - D.groupby("speaker")[c].transform("mean")
    print(f"usable transitions after demeaning/NaN: {len(D):,}  "
          f"conversations {D.conv_id.nunique()}  "
          f"speakers {D.speaker.nunique()}")
    betas, ns = [], []
    for cid, s in D.groupby("conv_id"):
        if len(s) < 50:
            continue
        X = np.column_stack([np.ones(len(s))] +
                            [(s[c] - s[c].mean()).values /
                             (s[c].std() if s[c].std() > 0 else 1)
                             for c in ["tee"] + CTRL])
        b, *_ = np.linalg.lstsq(X, s.dv.values, rcond=None)
        betas.append(b[1]); ns.append(len(s))
    betas = np.array(betas)
    pos = (betas > 0).mean()
    w = stats.wilcoxon(betas)
    print(f"\nconversations >= 50 transitions: {len(betas)} "
          f"(median n {int(np.median(ns))})")
    print(f"TEE coefficient: mean {betas.mean():+.5f}  %pos {pos:.1%}  "
          f"Wilcoxon p {w.pvalue:.2e}")
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"\nPREREGISTERED CRITERION: {'PASS' if ok else 'FAIL'}")
    # secondary, no gate
    r1 = np.corrcoef(D.tee, (D.pause_len >= 3).astype(float))[0, 1]
    r2 = np.corrcoef(D.tee, D.dv)[0, 1]
    print(f"secondary (descriptive): r(tee, pause_mark) {r2:+.4f}; "
          f"r(tee, long pause 3+ dots) {r1:+.4f}")


if __name__ == "__main__":
    {"prepare": prepare, "measures": measures,
     "analyze": analyze}[sys.argv[1]]()
