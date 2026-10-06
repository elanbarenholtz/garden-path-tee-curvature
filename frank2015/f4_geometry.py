"""
F4 -- which geometric property of the layer-6 trajectory does the N400-window
potential covary with: step size, turning angle, or extrapolation error (TEE)?
Spec fixed before results were seen (2026-10-06).

Per word, at the final subword ls (GPT-2 small, layer 6, sentence-isolated
contexts as in f1; all windows clear of the <|endoftext|> sink state):
  step_norm    ||h[ls] - h[ls-1]||                         (size of the move)
  curvature_1  angle(step ls, step ls-1)                   (turn, as before)
  curvature_3  mean angle over ls-2..ls                    (as before)
  tee_k3       ||h[ls] - linear extrapolation from h[ls-3..ls-1]||
  tee_par      |component of the TEE residual along the fitted heading|  ~ speed change
  tee_perp     component orthogonal to the heading                       ~ lateral turn
  (TEE and its decomposition exactly as tee_vs_curvature/compute_curvature.py)
Sample: words with ls-4 >= 1 (all measures defined, sink-clear), not
sentence-final, not rejected = the F2 PRIMARY sample.

Models (F2 PRIMARY covariates + surprisal + entropy; two-way clustered SEs):
  M1..M6  each measure alone
  J1  step_norm + curvature_3       J2  step_norm + curvature_1
  J3  tee_k3 + curvature_3          J4  tee_par + tee_perp
Also reports the word-level correlation matrix of the measures, and the
share of step_norm carried by GPT-2's outlier ("rogue") dimensions, since raw
Euclidean step size in GPT-2 is known to be dominated by a few dimensions;
step_norm_robust recomputes it with each dimension z-scored over the corpus.
"""
import os, numpy as np, pandas as pd, torch, scipy.io as sio
import statsmodels.formula.api as smf
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.environ.get("GPT2_PATH", "gpt2")
m = sio.loadmat(os.environ.get("FRANK_MAT", f"{HERE}/stimuli_erp.mat"),
                squeeze_me=True, struct_as_record=False)
tok = GPT2TokenizerFast.from_pretrained(P)
model = GPT2LMHeadModel.from_pretrained(P).eval()

# ---- states per sentence (same tokenisation as f1) ----
states, lasts = {}, {}
for s, sent in enumerate(m["sentences"], start=1):
    words = [str(w) for w in np.atleast_1d(sent)]
    ids, last = [tok.bos_token_id], []
    for i, w in enumerate(words):
        ids += tok((" " if i else "") + w)["input_ids"]; last.append(len(ids) - 1)
    with torch.no_grad():
        states[s] = model(torch.tensor([ids]), output_hidden_states=True).hidden_states[6][0].numpy()
    lasts[s] = last
allH = np.concatenate([H[1:] for H in states.values()])        # exclude sink rows
mu, sd = allH.mean(0), allH.std(0) + 1e-6
top = np.argsort(-np.abs(np.diff(allH, axis=0)).mean(0))[:3]


def ang(a, b): return float(np.arccos(np.clip(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))


rows = []
for s, H in states.items():
    Hz = (H - mu) / sd
    for w, ls in enumerate(lasts[s], start=1):
        if ls - 4 < 1:
            continue
        st = H[ls] - H[ls - 1]
        W3 = H[ls - 3:ls]; A = np.column_stack([np.ones(3), np.arange(3.)])
        c, *_ = np.linalg.lstsq(A, W3, rcond=None)
        r = H[ls] - (c[0] + c[1] * 3); bh = c[1] / np.linalg.norm(c[1]); par = r @ bh
        rows.append(dict(s=s, w=w,
                         step_norm=float(np.linalg.norm(st)),
                         step_norm_robust=float(np.linalg.norm(Hz[ls] - Hz[ls - 1])),
                         step_rogue_share=float((st[top] ** 2).sum() / (st ** 2).sum()),
                         tee_k3=float(np.linalg.norm(r)), tee_par=float(abs(par)),
                         tee_perp=float(np.linalg.norm(r - par * bh))))
X = pd.DataFrame(rows)
G = pd.read_csv(f"{HERE}/frank_gpt2_measures.csv")
X = X.merge(G[["s", "w", "curvature_3", "curvature_1"]], on=["s", "w"])
X.to_csv(f"{HERE}/frank_geometry_measures.csv", index=False)
print(f"{len(X)} sink-clear words; mean share of squared step in top-3 dims {X.step_rogue_share.mean():.2f}")
print("word-level correlations:")
print(X[["step_norm", "step_norm_robust", "curvature_1", "curvature_3", "tee_k3", "tee_par", "tee_perp"]]
      .corr().round(2).to_string())

# ---- regressions on the F2 PRIMARY frame ----
src = open(f"{HERE}/f2_n400_regression.py").read().split("out = []")[0]
exec(src)
L2 = L.merge(X.drop(columns=["curvature_3", "curvature_1"]), on=["s", "w"], how="inner")
MEAS = ["step_norm", "step_norm_robust", "curvature_1", "curvature_3", "tee_k3", "tee_par", "tee_perp"]
F = prep(L2[(L2.final == 0)], COV + ["surprisal", "entropy"] + MEAS)
print(f"\nsample: {len(F):,} trials, {F.wid.nunique()} words")
base = zs(["surprisal", "entropy"] + COV)
m0 = fit(F, base)
res = []
specs = [(f"M {k}", [k]) for k in MEAS] + [
    ("J1 step + curv3", ["step_norm", "curvature_3"]),
    ("J1r step_robust + curv3", ["step_norm_robust", "curvature_3"]),
    ("J2 step + curv1", ["step_norm", "curvature_1"]),
    ("J3 tee + curv3", ["tee_k3", "curvature_3"]),
    ("J4 tee_par + tee_perp", ["tee_par", "tee_perp"])]
for lab, terms in specs:
    q = fit(F, base + " + " + zs(terms))
    s_ = "   ".join(f"{t} {q.params['z_' + t]:+.4f} (t {q.tvalues['z_' + t]:5.2f}, p {q.pvalues['z_' + t]:.2g})"
                    for t in terms)
    print(f"  {lab:<26} dAIC {m0.aic - q.aic:6.1f}   {s_}")
    for t in terms:
        res.append(dict(model=lab, term=t, beta=q.params["z_" + t], t=q.tvalues["z_" + t],
                        p=q.pvalues["z_" + t], dAIC=m0.aic - q.aic))
pd.DataFrame(res).to_csv(f"{HERE}/f4_results.csv", index=False)
