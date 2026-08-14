"""
E6b -- word-level production latency, AMI corpus (PREREG_E6_production_latency
Amendment 2, commit 5fb76e8, written before the corpus was downloaded).

Stage 1 prepare: parse words/*.xml (+ segments), build per-meeting
  onset-ordered context text; transitions = consecutive non-punctuation
  words by the same speaker within the same segment. DV sanity reported
  (fraction of gaps > 200 ms) -- degenerate DV stops the tier, per prereg.
Stage 2 measures: GPT-2 Small TEE / surprisal / four functionals over the
  onset-ordered meeting text (paper conventions; as e6_run.py).
Stage 3 analyze: within-speaker demeaning; per-speaker OLS (speaker =
  meeting x channel, i.e. speaker-session; >= 200 transitions);
  CRITERION: Wilcoxon p < .01 AND >= 65% of speakers positive.

Usage: e6b_run.py prepare | measures | analyze
"""
import os, re, sys, glob
import numpy as np
import pandas as pd
from scipy import stats
from wordfreq import zipf_frequency
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_rank_test import GP, GPC, first_write_ranges, load_model

AMI = f"{GP}/ami"
TRANS_CSV = f"{GPC}/e6b_transitions.csv"
TEXTS_CSV = f"{GPC}/e6b_texts.csv"
MEAS_CSV = f"{GPC}/e6b_word_measures.csv"
NS = {"nite": "http://nite.sourceforge.net/"}


def parse_meeting_words():
    files = sorted(glob.glob(f"{AMI}/words/*.words.xml"))
    allw = {}
    for f in files:
        base = os.path.basename(f)
        m = re.match(r"(.+)\.([A-E])\.words\.xml", base)
        if not m:
            continue
        meet, ch = m.group(1), m.group(2)
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            print(f"PARSE FAIL {base}")
            continue
        rows = []
        for w in root.findall("w"):
            wid = w.get("{http://nite.sourceforge.net/}id")
            n = int(re.search(r"words(\d+)$", wid).group(1))
            st, en = w.get("starttime"), w.get("endtime")
            if st is None or en is None:
                continue
            rows.append({"n": n, "start": float(st), "end": float(en),
                         "text": (w.text or "").strip(),
                         "punc": w.get("punc") == "true"})
        segf = f"{AMI}/segments/{meet}.{ch}.segments.xml"
        seg_of = {}
        if os.path.exists(segf):
            sroot = ET.parse(segf).getroot()
            for si, seg in enumerate(sroot.findall("segment")):
                for child in seg.findall("nite:child", NS):
                    href = child.get("href")
                    ids = re.findall(r"words(\d+)\)", href)
                    if not ids:
                        continue
                    a, b = int(ids[0]), int(ids[-1])
                    for k in range(a, b + 1):
                        seg_of[k] = si
        for r in rows:
            r["seg"] = seg_of.get(r["n"], -1)
        allw.setdefault(meet, {})[ch] = rows
    return allw


def prepare():
    allw = parse_meeting_words()
    trows, texts = [], []
    for meet, chans in sorted(allw.items()):
        pool = []
        for ch, rows in chans.items():
            for r in rows:
                if not r["punc"] and r["text"]:
                    pool.append({"ch": ch, **r})
        pool.sort(key=lambda r: (r["start"], r["ch"], r["n"]))
        if len(pool) < 500:
            continue
        for i, r in enumerate(pool):
            r["word_pos"] = i
        texts.append({"meeting": meet, "n_words": len(pool),
                      "text": " ".join(r["text"] for r in pool)})
        bysp = {}
        for r in pool:
            bysp.setdefault(r["ch"], []).append(r)
        for ch, rows in bysp.items():
            rows.sort(key=lambda r: r["n"])
            for a, b in zip(rows, rows[1:]):
                if b["seg"] < 0 or a["seg"] != b["seg"]:
                    continue
                gap = (b["start"] - a["end"]) * 1000.0
                trows.append({"meeting": meet,
                              "speaker": f"{meet}.{ch}",
                              "word_pos": b["word_pos"],
                              "gap_ms": gap, "seg": b["seg"],
                              "prev_end": a["end"]})
    T = pd.DataFrame(texts)
    D = pd.DataFrame(trows)
    T.to_csv(TEXTS_CSV, index=False)
    D.to_csv(TRANS_CSV, index=False)
    tot = T.n_words.sum()
    print(f"{len(T)} meetings, {tot:,} words, {len(D):,} within-segment "
          f"same-speaker word transitions")
    print(f"gap distribution: <0 (overlap/misalign) {(D.gap_ms<0).mean():.1%}"
          f"   =0 {(D.gap_ms==0).mean():.1%}   >200 ms "
          f"{(D.gap_ms>200).mean():.1%}   median "
          f"{D.gap_ms.median():.0f} ms")
    spk = D.groupby("speaker").size()
    print(f"speakers (meeting x channel): {len(spk)}; "
          f">= 200 transitions: {(spk >= 200).sum()}")
    print("DV SANITY GATE:",
          "PASS" if (D.gap_ms > 200).mean() > 0.02 else
          "FAIL -- degenerate, stop per prereg")


def measures():
    import torch
    tok, model = load_model("gpt2", "cpu")
    T = pd.read_csv(TEXTS_CSV)
    first = not os.path.exists(MEAS_CSV)
    done = set()
    if not first:
        done = set(pd.read_csv(MEAS_CSV).meeting.unique())
    for r in T.itertuples():
        meet, text = r.meeting, r.text
        if meet in done:
            continue
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
        assert (first_sub >= 0).all(), f"{meet}: unmapped words"
        H = np.full((n, 768), np.nan, dtype=np.float32)
        surp = np.full(n, np.nan)
        F = {k: np.full(n, np.nan) for k in
             ("ent", "ren", "t1", "t10")}
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
            out.append({"meeting": meet, "word_pos": w, "tee": tee,
                        "surprisal": (np.nansum(surp[fs:t + 1])
                                      if fs >= 1 else np.nan),
                        "f_entropy": F["ent"][fs], "f_renyi2": F["ren"][fs],
                        "f_top1": F["t1"][fs], "f_top10": F["t10"][fs],
                        "word_length": len(words[w]),
                        "zipf": zipf_frequency(
                            words[w].strip(",.?!;:\"'").lower(), "en")})
        pd.DataFrame(out).to_csv(MEAS_CSV, mode="a", header=first,
                                 index=False)
        first = False
        print(f"{meet} done ({len(words):,} words)", flush=True)


def analyze():
    D = pd.read_csv(TRANS_CSV)
    M = pd.read_csv(MEAS_CSV)
    D = D.merge(M, on=["meeting", "word_pos"], how="left")
    D["dv"] = np.log1p(D.gap_ms.clip(0, 5000))
    D = D.sort_values(["speaker", "prev_end"])
    D["seg_pos"] = np.log1p(D.groupby(["speaker", "seg"]).cumcount())
    D["cum_words"] = np.log1p(D.word_pos)
    CTRL = ["surprisal", "f_entropy", "f_renyi2", "f_top1", "f_top10",
            "zipf", "word_length", "seg_pos", "cum_words"]
    use = ["dv", "tee"] + CTRL
    D = D[np.isfinite(D[use]).all(axis=1)].copy()
    for c in use:
        D[c] = D[c] - D.groupby("speaker")[c].transform("mean")
    print(f"usable transitions: {len(D):,}   speakers "
          f"{D.speaker.nunique()}   meetings {D.meeting.nunique()}")
    betas, ns = [], []
    for sp, s in D.groupby("speaker"):
        if len(s) < 200:
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
    print(f"\nspeakers >= 200 transitions: {len(betas)} "
          f"(median n {int(np.median(ns))})")
    print(f"TEE coefficient: mean {betas.mean():+.5f}  %pos {pos:.1%}  "
          f"Wilcoxon p {w.pvalue:.2e}")
    ok = (w.pvalue < .01) and (pos >= .65)
    print(f"\nPREREGISTERED CRITERION: {'PASS' if ok else 'FAIL'}")
    r = np.corrcoef(D.tee, D.dv)[0, 1]
    print(f"descriptive: raw r(tee, dv) {r:+.4f}")


if __name__ == "__main__":
    {"prepare": prepare, "measures": measures,
     "analyze": analyze}[sys.argv[1]]()
