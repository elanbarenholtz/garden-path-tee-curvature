"""
WHY IS THE FREQUENCY COEFFICIENT POSITIVE?
===========================================
The manuscript reports beta(log frequency) = +0.0072 in Natural Stories, and the
new figure puts it at +0.022. Positive means MORE FREQUENT WORDS ARE READ MORE
SLOWLY, which is backwards from one of the most robust effects in reading
research.

Three possible explanations, distinguished below:

  (a) CODING ERROR. The variable is not what it is labelled -- inverted, or a
      rank, or something other than a frequency. Diagnosed by inspecting the
      values directly: "the" and "of" must have HIGH log_freq, rare content
      words LOW.

  (b) SUPPRESSION. The raw effect is negative as expected, but flips once
      surprisal and word length are in the model. This is documented for
      frequency, which is heavily collinear with predictability, and would be
      legitimate -- but it must be explained in the text rather than reported
      bare.

  (c) SOMETHING ELSE, in which case the diagnostics below should show it.

The test is a build-up: raw correlation, then the coefficient with predictors
added one at a time, so the exact point at which the sign flips is visible.
Run on both corpora, since the figure shows a positive coefficient in each.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from wordfreq import zipf_frequency
import hashlib, warnings
warnings.filterwarnings("ignore")

GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
GPC = f"{GP}/gp_confound_check"


def zs(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
     S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
assert sh == "8a6087341e", sh

print("=" * 78)
print("(a) IS THE VARIABLE WHAT IT SAYS IT IS?")
print("=" * 78)
print("  highest log_freq words in the Natural Stories sample:")
top = S.dropna(subset=["log_freq"]).nlargest(12, "log_freq")[["word", "log_freq"]]
print("   ", ", ".join(f"{r.word}({r.log_freq:.2f})" for r in top.itertuples()))
print("  lowest log_freq words:")
bot = S.dropna(subset=["log_freq"]).nsmallest(12, "log_freq")[["word", "log_freq"]]
print("   ", ", ".join(f"{r.word}({r.log_freq:.2f})" for r in bot.itertuples()))
print(f"\n  range {S.log_freq.min():.2f} to {S.log_freq.max():.2f}, "
      f"mean {S.log_freq.mean():.2f}")
chk = {w: zipf_frequency(w, "en") for w in ["the", "of", "and", "manor",
                                            "ocean", "tics"]}
print(f"  reference Zipf values: {chk}")
print(f"  r(log_freq, word_length) = "
      f"{S.log_freq.corr(S.word_length):+.3f}   (should be NEGATIVE: frequent "
      f"words are short)")
print(f"  r(log_freq, surprisal)   = {S.log_freq.corr(S.surprisal):+.3f}"
      f"   (should be NEGATIVE: frequent words are predictable)")

rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
                 sep="\t").rename(columns={"item": "story_id",
                                           "WorkerId": "participant"})
rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
ns = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
                 "log_freq"]], on=["story_id", "zone"], how="inner")
ns["log_RT"] = np.log(ns.RT)
ns = ns.sort_values(["participant", "story_id", "zone"])
ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
                       "prev_log_RT", "tee_k3", "surprisal"]).rename(
    columns={"tee_k3": "tee"})

d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
d = d.rename(columns={"MD5": "participant"})
d = d.merge(pd.read_csv(f"{GPC}/sap_measures_L6k3.csv"),
            on=["item", "Type", "WordPosition"], how="left",
            validate="many_to_one")
d["word_length"] = d.EachWord.str.len()
d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
    lambda x: zipf_frequency(x, "en"))
d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
d["from_start"] = d.WordPosition.astype(float)
d["fs2"] = d.from_start ** 2
d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
d["fe2"] = d.from_end ** 2
d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
d["log_RT"] = np.log(d.RT)
d = d.dropna(subset=["tee", "surp", "word_length", "log_freq",
                     "log_RT"]).rename(columns={"surp": "surprisal"})


def subj(df, cols, minn):
    out = []
    for pid, s in df.groupby("participant"):
        s = s.dropna(subset=cols + ["log_RT"])
        if len(s) < minn:
            continue
        X = np.column_stack([zs(s[c].values) for c in cols])
        if (X.std(axis=0) == 0).any():
            continue
        out.append(sm.OLS(zs(s.log_RT.values),
                          sm.add_constant(X)).fit().params[1])
    return np.array(out)


for name, df, extra, minn in [
        ("Natural Stories", ns, ["zone", "prev_log_RT"], 300),
        ("Garden-path corpus", d, ["punct", "from_start", "fs2", "from_end",
                                   "fe2"], 100)]:
    print("\n" + "=" * 78)
    print(f"(b) WHERE DOES THE SIGN FLIP?  {name}")
    print("=" * 78)
    r = df.log_freq.corr(df.log_RT)
    print(f"  raw r(log_freq, log_RT) = {r:+.4f}   "
          f"({'NEGATIVE as expected' if r < 0 else 'POSITIVE -- unexpected'})")
    steps = [
        ("log_freq alone", ["log_freq"]),
        ("+ word_length", ["log_freq", "word_length"]),
        ("+ surprisal", ["log_freq", "word_length", "surprisal"]),
        ("+ trajectory error", ["log_freq", "word_length", "surprisal", "tee"]),
        ("+ remaining controls", ["log_freq", "word_length", "surprisal",
                                  "tee"] + extra),
    ]
    print(f"\n  {'model':<26}{'beta(log_freq)':>16}{'% positive':>13}")
    for lab, cols in steps:
        b = subj(df, cols, minn)
        print(f"  {lab:<26}{b.mean():>+16.5f}{(b > 0).mean():>12.1%}")

print("\n" + "=" * 78)
print("READING")
print("=" * 78)
print("""  If log_freq alone is NEGATIVE and turns positive only once surprisal
  enters, this is suppression: surprisal absorbs the predictability component of
  frequency and what remains carries the opposite sign. Legitimate, but it must
  be stated in the text.

  If log_freq is POSITIVE even on its own, the variable is not measuring what
  its name says and every model in the paper needs rechecking.""")
