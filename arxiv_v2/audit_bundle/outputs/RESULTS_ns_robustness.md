# Natural Stories: reconciliation and the two missing robustness checks (2026-07-27)

Scripts: `ns_robustness.py`, output `ns_robustness_output.txt`; reconciliation
in `ns_reconcile.txt`.

## Reconciliation: why the paper says 2.5 and the locked sample says 112

Not a sample-size difference, and not a control difference.

| | paper (`ns_crossed_re.py`) | locked sample (8a6087341e) |
|---|---|---|
| N | ~800k RT observations | 812,730 |
| M1 AIC | 189,030.9 | 161,314.6 |
| controls | word length, log freq, zone, prev log RT, surprisal | identical |
| RT filter | 100–3000 ms | identical |
| **ΔAIC** | **2.5** | **111.8** |
| **β(TEE)** | **+0.00063** | **+0.00354** |

Same rows, same specification. The only thing that differs is the TEE values
themselves. The paper's came from `naturalstories_extrap.py` (pre-rebuild,
chunked GPT-2 passes); the locked sample came from the REBUILD_V2 pipeline that
was written *because* the earlier pipeline had alignment bugs — the same rebuild
that overturned the k=15 optimality claim in `AUDIT_FOR_FABLE.md`.

The locked sample is the reproducible one: it is hash-fingerprinted, and its TEE
has been independently recomputed twice (matching to 1.4e-14 in-repo, and to
r = 0.9999999999991 on a different machine in the extensions run). The paper's
`naturalstories_extrap_metrics.csv` is not in the repo and cannot currently be
reproduced at all.

**Conclusion: the published 2.5 is a superseded number.** Use the locked sample.
This should be stated explicitly somewhere in the record, because the direction
of the correction is favourable to the author and that is exactly when it needs
the clearest paper trail.

## The two robustness checks the paper is missing — both pass

| model | n | ΔAIC | β(TEE) | p |
|---|---|---|---|---|
| headline | 812,730 | 111.8 | +0.00354 | 1.4e-26 |
| + punctuation covariate | 812,730 | 115.4 | +0.00359 | 2.4e-27 |
| punctuation-free words only | 716,641 | **138.3** | +0.00411 | 2.3e-32 |
| **word-identity demeaned** | 812,730 | **23.1** | +0.00218 | 5.3e-7 |
| punct-free + word-identity demeaned | 716,641 | 23.7 | +0.00220 | 4.1e-7 |

**Punctuation:** no threat. 11.8% of observations are punctuation-final; adding a
covariate slightly *strengthens* the effect, and restricting to punctuation-free
words strengthens it further (ΔAIC 138.3). This is the confound that produced
spurious effects in four separate analyses elsewhere in the project — it does not
do so here.

**Lexical baseline:** this is the check `ns_crossed_re.py` attempted with a
`(1|word_type)` random effect and never completed. Implemented instead by
centering the outcome and all predictors within word identity (2,919 word types
occurring 5+ times), which asks whether TEE predicts reading time **for the same
word in different contexts**. It does: ΔAIC 23.1, p = 5.3e-7. The effect
attenuates by ~40%, which is expected and honest — a good part of the raw effect
is lexical — but it does not vanish. This is the single most important result
for the paper's claim, because it rules out the objection that TEE is a proxy
for word identity or frequency.

## Where this leaves the paper

The Natural Stories result is stronger than published, survives the punctuation
confound, and survives word identity. Combined with the tee_vs_curvature
dissociation and the extensions (neighborhood TEE causal wake, manifold split),
there is a publishable paper here that does not depend on garden paths at all.

Remaining: the tee_vs_curvature and extensions pipelines have not been audited to
this standard. They are the other half of any reframed submission and should get
the same treatment before anything is written.
