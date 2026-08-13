#!/usr/bin/env python3
"""
Download a subfolder of a ZuCo (or any) OSF project via the OSF API.
Pure stdlib, resumable (skips files already present with matching size),
preserves folder structure, retries per file.

ZuCo 1.0 project id = q3zws.
Default target = "task2 - NR/Preprocessed" (Normal Reading, ICA-preprocessed
EEG + corrected eye-tracking; ~6.2 GB, 159 files). Change PATH below for other
subfolders, e.g. ["task2 - NR", "Matlab files"] for the word-level sentenceData
structs, or ["task1 - SR", "Preprocessed"] for sentiment reading. Avoid
"task3 - TSR" (task-directed reading, not natural reading).

Usage:
    python3 download_zuco.py                 # default target -> ./zuco_data/
    python3 download_zuco.py OUTDIR          # custom output dir
Edit NODE / PATH constants to retarget.
"""
import os, sys, json, time, urllib.request

NODE = "q3zws"                                   # ZuCo 1.0
PATH = ["task2 - NR", "Preprocessed"]            # folder path inside osfstorage
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "zuco_data"
API = f"https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/"

def api_get(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))

def list_folder(url):
    """Yield all entries (handles pagination)."""
    while url:
        d = api_get(url)
        for f in d["data"]:
            yield f
        url = d.get("links", {}).get("next")

def child_link(entry):
    return entry["relationships"]["files"]["links"]["related"]["href"]

def descend(url, path):
    """Walk into nested folders by name; return the listing url of the target."""
    for name in path:
        found = None
        for f in list_folder(url):
            if f["attributes"]["kind"] == "folder" and f["attributes"]["name"] == name:
                found = f
                break
        if found is None:
            sys.exit(f"folder not found: {name!r} (check the PATH constant)")
        url = child_link(found)
    return url

def collect(url, reldir=""):
    """Recursively collect (relative_path, download_url, size) for all files."""
    out = []
    for f in list_folder(url):
        a = f["attributes"]
        rel = os.path.join(reldir, a["name"])
        if a["kind"] == "file":
            out.append((rel, f["links"]["download"], a.get("size") or 0))
        else:
            out.extend(collect(child_link(f), rel))
    return out

def download(url, dest, tries=5):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as w:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    w.write(chunk)
            os.replace(tmp, dest)
            return
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))

def main():
    print(f"OSF node {NODE}, path {'/'.join(PATH)} -> {OUTDIR}/", flush=True)
    target = descend(API, PATH)
    files = collect(target)
    total = sum(s for _, _, s in files)
    print(f"{len(files)} files, {total/1e9:.2f} GB total\n", flush=True)
    done_bytes = 0
    for i, (rel, url, size) in enumerate(files, 1):
        dest = os.path.join(OUTDIR, rel)
        if os.path.exists(dest) and abs(os.path.getsize(dest) - size) <= 1:
            done_bytes += size
            print(f"[{i}/{len(files)}] skip (have) {rel}", flush=True)
            continue
        print(f"[{i}/{len(files)}] get  {rel}  ({size/1e6:.1f} MB)", flush=True)
        download(url, dest)
        done_bytes += size
        print(f"     ... {done_bytes/1e9:.2f}/{total/1e9:.2f} GB", flush=True)
    print(f"\nDONE: {len(files)} files in {OUTDIR}/")

if __name__ == "__main__":
    main()
