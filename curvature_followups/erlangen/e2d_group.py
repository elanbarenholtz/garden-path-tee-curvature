"""
E2d -- group inference (subject = unit, as in the ECoG analysis).

PRIMARY (EEG): curvature beta at the a priori (midpoint) layer, averaged over
  CP1 CPz CP2 P1 Pz P2 and 300-450 ms; one-sample t-test and Wilcoxon across
  subjects. Surprisal beta in the same model = the benchmark (should reproduce
  the published N400 predictability effect).
DEPTH PROFILE: the same statistic at every layer (a priori layer marked; Holm
  across layers reported as secondary).
MEG: no sensor names are specified in the paper for its 248-channel system, so
  the ROI is data-driven WITHOUT circularity: for each subject, the 20 sensors
  with the largest |group t| for SURPRISAL in 500-650 ms computed on the OTHER
  subjects (leave-one-subject-out). Each sensor is sign-aligned to that
  surprisal effect, so a positive curvature value means "same polarity as the
  surprisal effect". Channels are matched by name across subjects.
TIME-RESOLVED: spatio-temporal cluster permutation (0-800 ms, all channels)
  for curvature and surprisal at the a priori layer, if --data points at the
  FIF files (needed for sensor adjacency).

Output: E2_RESULTS.md, e2_depth_profile.csv
"""
import argparse, glob, os, re
import numpy as np, pandas as pd, mne
from scipy import stats
mne.set_log_level("ERROR")
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=os.environ.get("ERLANGEN_DATA", f"{HERE}/data"))
ap.add_argument("--n-perm", type=int, default=1000)
ap.add_argument("--meg-roi-size", type=int, default=20)
args = ap.parse_args()


def load(kind):
    fs = sorted(glob.glob(f"{HERE}/betas/sub-*_{kind}.npz"))
    return {int(re.search(r"sub-(\d+)_", f).group(1)): dict(np.load(f, allow_pickle=True))
            for f in fs}


def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m)
    adj[o] = np.maximum.accumulate(np.minimum(1, (m - np.arange(m)) * p[o]))
    return adj


def summarise(vals, label):
    v = np.asarray(vals)
    t = stats.ttest_1samp(v, 0)
    w = stats.wilcoxon(v).pvalue if len(v) >= 6 else np.nan
    return dict(label=label, mean=v.mean(), sem=v.std(ddof=1) / np.sqrt(len(v)),
                t=t.statistic, p_t=t.pvalue, p_wilcoxon=w, n_pos=int((v > 0).sum()), n=len(v))


rows, lines = [], ["# E2 Erlangen post-onset results\n"]
TERMS = ["surprisal", "entropy", "curv"]

# ------------------------------------------------------------------ EEG
E = load("eeg")
if E:
    any_ = next(iter(E.values())); LA = int(any_["a_priori"]); layers = any_["layers"]
    lines.append(f"## EEG (n = {len(E)} subjects), ROI CP1 CPz CP2 P1 Pz P2, "
                 f"{any_['window'][0]*1000:.0f}-{any_['window'][1]*1000:.0f} ms\n")
    for li, l in enumerate(layers):
        for ti, term in enumerate(TERMS):
            vals = [d["B_layers"][li, ti, d["roi_idx"]].mean() for d in E.values()]
            r = summarise(vals, f"EEG L{l} {term}"); r.update(modality="eeg", layer=l, term=term,
                                                            a_priori=(l == LA)); rows.append(r)
# ------------------------------------------------------------------ MEG
M = load("meg")
if M:
    any_ = next(iter(M.values())); LA = int(any_["a_priori"]); layers = any_["layers"]
    common = sorted(set.intersection(*[set(d["ch_names"]) for d in M.values()]))
    ix = {s: np.array([list(d["ch_names"]).index(c) for c in common]) for s, d in M.items()}
    surp_la = {s: d["B_layers"][LA - 1, 0, ix[s]] for s, d in M.items()}
    subs = list(M)
    roi = {}
    for s in subs:
        others = np.stack([surp_la[o] for o in subs if o != s])
        tt = stats.ttest_1samp(others, 0).statistic
        top = np.argsort(-np.abs(tt))[:args.meg_roi_size]
        roi[s] = (top, np.sign(tt[top]))
    lines.append(f"## MEG (n = {len(M)} subjects), LOSO surprisal ROI "
                 f"({args.meg_roi_size} sensors, sign-aligned), "
                 f"{any_['window'][0]*1000:.0f}-{any_['window'][1]*1000:.0f} ms\n")
    for li, l in enumerate(layers):
        for ti, term in enumerate(TERMS):
            vals = [(M[s]["B_layers"][li, ti, ix[s]][roi[s][0]] * roi[s][1]).mean() for s in subs]
            r = summarise(vals, f"MEG L{l} {term}"); r.update(modality="meg", layer=l, term=term,
                                                            a_priori=(l == LA)); rows.append(r)

R = pd.DataFrame(rows)
if R.empty:
    raise SystemExit("no betas/*.npz found: run e2c_post_onset.py first")
for mod in R.modality.unique():
    sel = (R.modality == mod) & (R.term == "curv")
    R.loc[sel, "p_holm_layers"] = holm(R.loc[sel, "p_t"])
R.to_csv(f"{HERE}/e2_depth_profile.csv", index=False)

for mod in R.modality.unique():
    lines.append(f"\n### {mod.upper()} primary (a priori layer)\n")
    lines.append("| term | mean beta | SEM | t | p (t) | p (Wilcoxon) | subjects > 0 |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in R[(R.modality == mod) & R.a_priori].iterrows():
        lines.append(f"| {r['term']} | {r['mean']:+.4f} | {r['sem']:.4f} | {r['t']:+.2f} | {r['p_t']:.2g} | "
                     f"{r['p_wilcoxon']:.2g} | {r['n_pos']}/{r['n']} |")
    lines.append(f"\n### {mod.upper()} depth profile (curvature)\n")
    lines.append("| layer | mean beta | t | p (t) | p (Holm across layers) |")
    lines.append("|---|---|---|---|---|")
    for _, r in R[(R.modality == mod) & (R.term == "curv")].iterrows():
        lines.append(f"| {r['layer']}{' (a priori)' if r['a_priori'] else ''} | {r['mean']:+.4f} | "
                     f"{r['t']:+.2f} | {r['p_t']:.2g} | {r['p_holm_layers']:.2g} |")

# ------------------------------------------------------------------ clusters
for kind, D in (("eeg", E), ("meg", M)):
    if not D:
        continue
    fifs = glob.glob(f"{args.data}/Prob*_{'EEGdata_raw' if kind == 'eeg' else 'fixed_ICA_prep_raw'}.fif")
    if not fifs:
        lines.append(f"\n({kind.upper()} cluster test skipped: FIF files not found for adjacency)")
        continue
    info = mne.io.read_raw_fif(fifs[0], preload=False).info
    common = sorted(set.intersection(*[set(d["ch_names"]) for d in D.values()]) & set(info.ch_names))
    info = mne.pick_info(info, [info.ch_names.index(c) for c in common])
    adj = None
    try:
        adj_t, names = mne.channels.find_ch_adjacency(info, "eeg" if kind == "eeg" else "mag")
        if set(common) <= set(names):
            o = [names.index(c) for c in common]
            adj = adj_t.tocsr()[o][:, o]
    except Exception as e:
        print(f"  template adjacency failed ({e}); using sensor positions")
    if adj is None:                  # geometric fallback: hull edges, distance-limited
        from scipy.spatial import ConvexHull, cKDTree
        from scipy.sparse import coo_matrix
        P = np.array([ch["loc"][:3] for ch in info["chs"]])
        nn = cKDTree(P).query(P, 2)[0][:, 1]; lim = 2.5 * np.median(nn)
        E = set()
        for s in ConvexHull(P).simplices:
            for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
                if np.linalg.norm(P[a] - P[b]) < lim:
                    E |= {(a, b), (b, a)}
        i, j = zip(*E) if E else ((), ())
        adj = coo_matrix((np.ones(len(i)), (i, j)), shape=(len(P), len(P))).tocsr()
        print(f"  {kind}: geometric adjacency, {len(E)//2} edges over {len(P)} sensors")
    times = next(iter(D.values()))["times"]
    lines.append(f"\n### {kind.upper()} spatio-temporal clusters, a priori layer, 0-{times[-1]*1000:.0f} ms\n")
    for ti, term in enumerate(TERMS):
        X = np.stack([d["B_time"][ti][[list(d["ch_names"]).index(c) for c in common]].T
                      for d in D.values()])                   # (subj, t, ch)
        T, cl, pv, _ = mne.stats.spatio_temporal_cluster_1samp_test(
            X, adjacency=adj, n_permutations=args.n_perm, tail=0, seed=0)
        sig = [(i, p) for i, p in enumerate(pv) if p < 0.05]
        if not sig:
            lines.append(f"- {term}: no cluster p < .05 (min p {pv.min() if len(pv) else 1:.2f})")
        for i, p in sig:
            tt, cc = cl[i]
            lines.append(f"- {term}: cluster p = {p:.3f}, {times[tt.min()]*1000:.0f}-"
                         f"{times[tt.max()]*1000:.0f} ms, {len(np.unique(cc))} channels, "
                         f"sum t {T[tt, cc].sum():+.1f}")

open(f"{HERE}/E2_RESULTS.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
