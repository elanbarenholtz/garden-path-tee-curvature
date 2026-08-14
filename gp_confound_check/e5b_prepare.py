"""
E5b corpus preparation: Santa Barbara Corpus (SBCSAE) TRN -> clean text.
Committed BEFORE any E5b analysis runs (PREREG_E5_history_sufficiency.md,
E5b section). Cleaning decisions, fixed here:

KEEP  words as produced, including fillers (uh, um, mhm), repetitions, and
      truncated fragments (dash stripped: "y-" -> "y"); prereg: the primary
      analysis retains disfluencies.
DROP  transcription apparatus only: timestamps, speaker labels, overlap
      brackets [ ] [2 2], vocal-noise parentheticals (H) (Hx) (TSK) (COUGH)
      etc., researcher comments ((...)), quality-span markers <YWN ...> <Q>
      <VOX> etc. (words inside are kept), pause dots (.. / ...), lengthening
      equals (ti=red -> tired), pseudonym tildes (~Mae -> Mae), laughter @
      pulses, unintelligible X/XX/XXX tokens, glottal %, latching/truncation
      markers (--), and stray punctuation-only tokens.
UNIT  conversation (SBC001..SBC060) = bootstrap cluster; prefix = the
      interleaved transcript in file (temporal) order, words joined by
      single spaces, no speaker tags.

Output: gp_confound_check/sbcsae_texts.csv  (conv_id, n_words, text)
"""
import os, re, glob
import pandas as pd

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
TRN = f"{GP}/sbcsae/TRN"

rows = []
for f in sorted(glob.glob(f"{TRN}/SBC*.trn")):
    conv = int(re.search(r"SBC(\d+)", f).group(1))
    words_all = []
    for enc in ("utf-8", "latin-1"):
        try:
            lines = open(f, encoding=enc).read().splitlines()
            break
        except UnicodeDecodeError:
            continue
    for ln in lines:
        # text column: after the last tab (timestamps/speaker before)
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        t = parts[-1]
        t = re.sub(r"\(\(.*?\)\)", " ", t)          # researcher comments
        t = re.sub(r"\([^)]*\)", " ", t)            # vocal noises (H) (TSK)..
        t = re.sub(r"<{1,2}\s*[A-Z%@]{1,6}\b", " ", t)  # open quality marker
        t = re.sub(r"\b[A-Z%@]{1,6}\s*>{1,2}", " ", t)  # close quality marker
        t = t.replace("<", " ").replace(">", " ")
        t = re.sub(r"\[\d?", " ", t)                # overlap opens [ [2
        t = re.sub(r"\d?\]", " ", t)                # overlap closes ] 2]
        t = t.replace("=", "")                      # lengthening
        t = t.replace("~", "")                      # pseudonym marker
        t = re.sub(r"@+", " ", t)                   # laughter pulses
        t = re.sub(r"\.\.+", " ", t)                # pause dots .. ...
        t = t.replace("--", " ")                    # truncated intonation unit
        t = t.replace("%", " ")                     # glottal stop
        out = []
        for w in t.split():
            wl = w.strip(",.?!;:\"`'")
            core = re.sub(r"[^A-Za-z']", "", wl)
            if not core:
                continue
            if re.fullmatch(r"X{1,4}", core):       # unintelligible
                continue
            # truncated fragment: keep, dash already stripped by core regex
            out.append(wl.rstrip("-"))
        words_all.extend([w for w in out if w])
    if len(words_all) >= 500:
        rows.append({"conv_id": conv, "n_words": len(words_all),
                     "text": " ".join(words_all)})
    else:
        print(f"SBC{conv:03d}: only {len(words_all)} words -- excluded")

df = pd.DataFrame(rows)
df.to_csv(f"{GP}/gp_confound_check/sbcsae_texts.csv", index=False)
print(f"\n{len(df)} conversations kept, {df.n_words.sum():,} words total "
      f"(median {int(df.n_words.median()):,}/conv)")
print(df.n_words.describe().round(0).to_string())
print("\nsample (SBC001, first 60 words):")
print(" ".join(df[df.conv_id == 1].text.iloc[0].split()[:60]))
