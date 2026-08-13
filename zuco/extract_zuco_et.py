#!/usr/bin/env python3
"""
Resumable ZuCo 1.0 eye-tracking extractor (run on the laptop, where the data is).

ZuCo 'Preprocessed' .mat files are MATLAB v7.3 == HDF5, so scipy.io.loadmat
CANNOT read them (it errors or hangs -- this is what interrupted the first
reformat). We read them with h5py instead.

This pulls ONLY the per-word eye-tracking fields (no EEG dereferencing), which is
all we need for the first deliverable: does sink-controlled TEE predict fixation
duration during natural reading. One CSV per subject; already-done subjects are
skipped, so it safely resumes an interrupted run.

Usage:
    python3 extract_zuco_et.py [SRC_DIR] [OUT_DIR]
      SRC_DIR  folder holding the downloaded .mat files (default: zuco_data)
      OUT_DIR  where per-subject CSVs go            (default: zuco_et)

Output CSV columns per row (one row per word token, in reading order):
    subject, sent_idx, word_idx, word, nFix, FFD, GD, TRT, GPT, SFD
  FFD first-fixation dur, GD gaze dur, TRT total reading time, GPT go-past,
  SFD single-fixation dur (ms). NaN = word not fixated / field absent.

If a file fails to parse, the script prints that file's HDF5 tree and keeps
going -- paste that tree back and the field names get fixed in one shot.
"""
import os, sys, glob, csv
import numpy as np
import h5py

SRC = sys.argv[1] if len(sys.argv) > 1 else "zuco_data"
OUT = sys.argv[2] if len(sys.argv) > 2 else "zuco_et"
os.makedirs(OUT, exist_ok=True)

# per-word ET fields to try; missing ones are filled with NaN, not fatal
ET_FIELDS = ["nFixations", "FFD", "GD", "TRT", "GPT", "SFD"]


def refs_of(dset):
    """Flatten an HDF5 dataset of object references into a python list."""
    return list(np.array(dset).flatten())


def decode_str(f, ref):
    """ZuCo stores char arrays as uint16; deref + decode to str."""
    try:
        a = np.array(f[ref]).flatten()
    except Exception:
        return ""
    return "".join(chr(int(c)) for c in a if c != 0)


def scalar(f, ref):
    """Deref a numeric field to a float; empty (unfixated) -> NaN."""
    try:
        a = np.array(f[ref]).flatten()
    except Exception:
        return float("nan")
    return float(a[0]) if a.size else float("nan")


def dump_tree(path):
    print(f"---- HDF5 tree of {path} ----")
    with h5py.File(path, "r") as f:
        f.visit(lambda n: print("   ", n))
        print("   sentenceData keys:",
              list(f["sentenceData"].keys()) if "sentenceData" in f else "(no sentenceData)")


def extract_one(path):
    rows = []
    with h5py.File(path, "r") as f:
        sd = f["sentenceData"]
        word_refs = refs_of(sd["word"])          # one ref per sentence
        avail = [k for k in ET_FIELDS if False]  # decided per-sentence-group below
        for si, wref in enumerate(word_refs):
            wg = f[wref]                          # this sentence's word struct
            if "content" not in wg:
                continue
            wc = refs_of(wg["content"])           # one ref per word
            # which ET fields exist in this group
            fields = {k: refs_of(wg[k]) for k in ET_FIELDS if k in wg}
            for wi, cref in enumerate(wc):
                word = decode_str(f, cref)
                row = {"subject": "", "sent_idx": si, "word_idx": wi, "word": word}
                for k in ET_FIELDS:
                    v = fields.get(k)
                    row[k] = scalar(f, v[wi]) if (v is not None and wi < len(v)) else float("nan")
                rows.append(row)
    return rows


def main():
    mats = sorted(glob.glob(os.path.join(SRC, "**", "*.mat"), recursive=True))
    if not mats:
        sys.exit(f"no .mat files under {SRC!r} -- is that the right SRC dir?")
    print(f"{len(mats)} .mat files under {SRC}/\n", flush=True)
    ok = 0
    for m in mats:
        subj = os.path.splitext(os.path.basename(m))[0]
        out = os.path.join(OUT, subj + ".csv")
        if os.path.exists(out):
            print(f"skip (done)  {subj}", flush=True)
            ok += 1
            continue
        print(f"extract      {subj} ...", end="", flush=True)
        try:
            rows = extract_one(m)
            for r in rows:
                r["subject"] = subj
            cols = ["subject", "sent_idx", "word_idx", "word"] + ET_FIELDS
            tmp = out + ".part"
            with open(tmp, "w", newline="") as w:
                wr = csv.DictWriter(w, fieldnames=cols)
                wr.writeheader()
                wr.writerows(rows)
            os.replace(tmp, out)
            print(f" {len(rows)} word-rows -> {out}", flush=True)
            ok += 1
        except Exception as e:
            print(f" FAILED: {type(e).__name__}: {e}", flush=True)
            try:
                dump_tree(m)
            except Exception as e2:
                print("   (could not dump tree:", e2, ")")
            print("   ^ paste this tree back to fix the field names.\n", flush=True)
    print(f"\nDONE: {ok}/{len(mats)} subjects extracted into {OUT}/")


if __name__ == "__main__":
    main()
