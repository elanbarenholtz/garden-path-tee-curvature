"""
Frank et al. (2015) EEG: does curvature predict N400 amplitude beyond
surprisal and entropy? Spec fixed before results were seen (2026-10-06).

DV: N400 amplitude per trial (participant x word): ERP{s}(w,p,3), the
modulus-transformed component average from the deposited data. More negative
= larger N400.
Sample (PRIMARY): words with curvature_3 defined (window clear of the
<|endoftext|> sink), not sentence-final (wrap-up), not rejected.
Covariates (Frank et al.'s): baseline (ERPbase N400), log word frequency, word
length, word position, sentence position in session. All z-scored.

  BENCHMARK  N400 ~ surprisal + covariates           expect beta < 0
  PRIMARY    N400 ~ surprisal + entropy + covariates + curvature_3
             test: curvature beta (two-sided), dAIC vs the model without it
SEs two-way clustered (participant x word). Calibration: permutation null,
curvature shuffled across eligible words, N_PERM draws; report where the
observed t and dAIC fall. Word-level check: mean N400 per word (n words),
HC3 SEs.
SECONDARY: (a) Frank's RNN surprisal in place of GPT-2's; (b) curvature_1
in place of curvature_3 (defined for more words); (c) previous-word
curvature added.
"""
import os, numpy as np, pandas as pd, scipy.io as sio
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
MAT = os.environ.get("FRANK_MAT", f"{HERE}/stimuli_erp.mat")
N_PERM = int(os.environ.get("N_PERM", 1000))
m = sio.loadmat(MAT, squeeze_me=True, struct_as_record=False)
G = pd.read_csv(f"{HERE}/frank_gpt2_measures.csv")
COMP = 2                                   # ELAN, LAN, N400, EPNP, P600, PNP

rows = []
for si in range(205):
    erp = np.asarray(m["ERP"][si], float); base = np.asarray(m["ERPbase"][si], float)
    rej = np.asarray(m["reject"][si]); nw = erp.shape[0]
    lf = np.atleast_1d(m["logwordfreq"][si]); wl = np.atleast_1d(m["wordlength"][si])
    rnn = np.asarray(m["surp_rnn"][si], float); rnn = rnn[:, -1] if rnn.ndim > 1 else np.atleast_1d(rnn)
    for w in range(nw):
        for p in range(24):
            rows.append(dict(s=si + 1, w=w + 1, p=p + 1, n400=erp[w, p, COMP],
                             base=base[w, p, COMP], reject=int(rej[w, p]),
                             logfreq=float(lf[w]), wlen=float(wl[w]), surp_rnn=float(rnn[w]),
                             sent_pos=int(m["sentence_position"][p, si])))
L = pd.DataFrame(rows).merge(G, on=["s", "w"], validate="many_to_one")
L = L.sort_values(["p", "s", "w"])
L["curv3_prev"] = L.groupby(["p", "s"]).curvature_3.shift(1)
L["final"] = (L.w == L.n_words).astype(int)
L["wid"] = (L.s * 100 + L.w)
L = L[(L.reject == 0) & L.n400.notna()]
print(f"trials after rejection: {len(L):,}")

COV = ["base", "logfreq", "wlen", "w", "sent_pos"]


def prep(F, cols):
    F = F.dropna(subset=["n400"] + cols).copy()
    for c in cols:
        F["z_" + c] = (F[c] - F[c].mean()) / F[c].std()
    return F


def fit(F, rhs):
    return smf.ols(f"n400 ~ {rhs}", F).fit(cov_type="cluster", cov_kwds={
        "groups": np.column_stack([F.p.values, F.wid.values])})


def zs(cols): return " + ".join("z_" + c for c in cols)


out = []
P = prep(L[(L.final == 0) & L.curvature_3.notna()],
         COV + ["surprisal", "entropy", "curvature_3", "curvature_1", "surp_rnn"])
print(f"PRIMARY sample: {len(P):,} trials, {P.wid.nunique()} words, {P.p.nunique()} participants")
print("word-level r:", P.drop_duplicates("wid")[["curvature_3", "surprisal", "entropy",
      "logfreq", "w"]].corr().round(3).loc["curvature_3"].to_dict())

b = fit(P, zs(["surprisal"] + COV))
print(f"\nBENCHMARK surprisal beta {b.params['z_surprisal']:+.4f}  t {b.tvalues['z_surprisal']:.2f}  "
      f"p {b.pvalues['z_surprisal']:.2g}   (Frank: more negative N400 with higher surprisal)")
base_rhs = zs(["surprisal", "entropy"] + COV)
m0, m1 = fit(P, base_rhs), fit(P, base_rhs + " + z_curvature_3")
t_obs, daic_obs = m1.tvalues["z_curvature_3"], m0.aic - m1.aic
print(f"PRIMARY   curvature_3 beta {m1.params['z_curvature_3']:+.4f}  t {t_obs:.2f}  "
      f"p {m1.pvalues['z_curvature_3']:.2g}  dAIC {daic_obs:.1f}   "
      f"(surprisal {m1.params['z_surprisal']:+.4f}, t {m1.tvalues['z_surprisal']:.2f}; "
      f"entropy {m1.params['z_entropy']:+.4f}, t {m1.tvalues['z_entropy']:.2f})")
out.append(dict(test="PRIMARY curvature_3", beta=m1.params["z_curvature_3"], t=t_obs,
                p=m1.pvalues["z_curvature_3"], dAIC=daic_obs))

Wd = P.groupby("wid").agg(n400=("n400", "mean"), **{"z_" + c: ("z_" + c, "first") for c in
       ["surprisal", "entropy", "curvature_3", "logfreq", "wlen", "w"]},
       z_base=("z_base", "mean"), z_sent_pos=("z_sent_pos", "mean")).reset_index()
mw = smf.ols(f"n400 ~ {base_rhs} + z_curvature_3", Wd).fit(cov_type="HC3")
print(f"WORD-LEVEL (n={len(Wd)}) curvature_3 beta {mw.params['z_curvature_3']:+.4f}  "
      f"t {mw.tvalues['z_curvature_3']:.2f}  p {mw.pvalues['z_curvature_3']:.2g}")

rng = np.random.default_rng(0)
words = P.drop_duplicates("wid")[["wid", "z_curvature_3"]]
nt, nd = [], []
for i in range(N_PERM):
    sh = dict(zip(words.wid, rng.permutation(words.z_curvature_3.values)))
    Q = P.assign(z_curvature_3=P.wid.map(sh))
    q = fit(Q, base_rhs + " + z_curvature_3")
    nt.append(q.tvalues["z_curvature_3"]); nd.append(m0.aic - q.aic)
nt, nd = np.abs(np.array(nt)), np.array(nd)
p_perm = (1 + (nt >= abs(t_obs)).sum()) / (1 + N_PERM)
print(f"PERMUTATION (n={N_PERM}): null |t| 95th pct {np.percentile(nt, 95):.2f}, "
      f"null dAIC 95th pct {np.percentile(nd, 95):.1f};  observed |t| {abs(t_obs):.2f}  "
      f"-> permutation p = {p_perm:.3f};  null |t|>1.96 rate {(nt > 1.96).mean():.3f}")

print("\nSECONDARY")
for lab, F, rhs, term in [
    ("(a) Frank RNN surprisal instead of GPT-2", P, zs(["surp_rnn", "entropy"] + COV) + " + z_curvature_3", "z_curvature_3"),
    ("(b) curvature_1 (more words)", prep(L[(L.final == 0) & L.curvature_1.notna()],
         COV + ["surprisal", "entropy", "curvature_1"]), base_rhs + " + z_curvature_1", "z_curvature_1"),
    ("(c) + previous-word curvature", prep(P, ["curv3_prev"]),
         base_rhs + " + z_curvature_3 + z_curv3_prev", "z_curvature_3")]:
    q = fit(F, rhs)
    extra = f"   prev {q.params['z_curv3_prev']:+.4f} (t {q.tvalues['z_curv3_prev']:.2f})" if "prev" in rhs else ""
    print(f"  {lab:<44} n {len(F):>6,}  beta {q.params[term]:+.4f}  t {q.tvalues[term]:.2f}  "
          f"p {q.pvalues[term]:.2g}{extra}")
    out.append(dict(test=lab, beta=q.params[term], t=q.tvalues[term], p=q.pvalues[term]))
pd.DataFrame(out).to_csv(f"{HERE}/f2_results.csv", index=False)
