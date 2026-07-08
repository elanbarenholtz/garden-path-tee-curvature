"""Shared conventions for the extension analyses (inherited from parent)."""
import hashlib, os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

GP = os.path.expanduser("~/Projects/garden-path-tee-curvature")
STATES = f"{GP}/extensions/states"

def load_locked():
    S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
    sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
        S[["story_id", "word_idx"]].itertuples(index=False)).encode()
        ).hexdigest()[:10]
    assert sh == "8a6087341e", sh
    S["has_trailing_punct"] = (S["word"].astype(str)
        .str.match(r".*[^A-Za-z0-9]$").astype(float))
    return S, sh

def load_states(sid):
    z = np.load(f"{STATES}/story{sid}_states.npz")
    return (z["H"].astype(np.float64), z["bpe_word"], z["first_sub"],
            z["last_sub"])

def zscore(s):
    return (s - s.mean()) / s.std(ddof=0)

def build_ctrl(D, with_punct=False):
    ctrl = pd.get_dummies(D["story_id"], prefix="st",
                          drop_first=True).astype(float)
    cols = ["from_start", "fs2", "from_end", "fe2"]
    if with_punct:
        cols = cols + ["has_trailing_punct"]
    ctrl[cols] = D[cols].values
    return np.column_stack([np.ones(len(D)), ctrl.values])

def partial_r(D, Cm, xcol, ycol):
    def res(v):
        beta, *_ = np.linalg.lstsq(Cm, v, rcond=None)
        return v - Cm @ beta
    x = D[xcol].values.astype(float); y = D[ycol].values.astype(float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < len(D):
        Cs, x, y = Cm[m], x[m], y[m]
    else:
        Cs = Cm
    def res2(v, C):
        beta, *_ = np.linalg.lstsq(C, v, rcond=None)
        return v - C @ beta
    r = float(np.corrcoef(res2(x, Cs), res2(y, Cs))[0, 1])
    dfree = m.sum() - Cs.shape[1] - 2
    t = r * np.sqrt(dfree / max(1e-12, 1 - r ** 2))
    return r, 2 * stats.t.sf(abs(t), dfree)

def fit_cluster(formula, data):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["sent_uid"]})

def dissociation_table(M, measures, targets=("closure_depth", "entropy"),
                       label=""):
    """C2/C3/C4-style partial-r tables: position+story FE; +punct; punct-free."""
    out = []
    for tag, D, wp in [("posFE", M, False), ("posFE+punct", M, True),
                       ("punct-free", M[M.has_trailing_punct == 0]
                        .reset_index(drop=True), False)]:
        Cm = build_ctrl(D, with_punct=wp)
        print(f"\n--- {label} [{tag}] n={len(D)} ---")
        print(f"{'measure':22s} | " + " | ".join(f"x {t:>15s}" for t in targets)
              + " |     x surprisal |        x tee_k3")
        for m in measures:
            cells = []
            for t in list(targets) + ["surprisal", "tee_k3"]:
                r, p = partial_r(D, Cm, m, t)
                s = "*" if p < .05 else " "
                cells.append(f"{r:+.4f}({p:.0e}){s}")
                out.append({"table": tag, "measure": m, "target": t,
                            "r": r, "p": p, "n": len(D)})
            print(f"{m:22s} | " + " | ".join(f"{c:>15s}" for c in cells))
    return pd.DataFrame(out)

def load_rt():
    R = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/"
                    "processed_RTs.tsv", sep="\t")
    R = R[(R.RT >= 100) & (R.RT <= 3000)].copy()
    R["logRT"] = np.log(R["RT"])
    agg = R.groupby(["item", "zone"]).agg(
        mean_logRT=("logRT", "mean"), n_obs=("logRT", "size")).reset_index()
    return agg.rename(columns={"item": "story_id"})
