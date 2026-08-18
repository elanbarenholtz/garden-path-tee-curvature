# Theoretical framework — the two-property account
Written 2026-08-14, end of the E5–E10 program. This is the conceptual spine
for the paper (and the NHB framing). Every claim here is tagged with the
evidence that carries it and the caveat that bounds it.

## 1. Two orthogonal properties

**Autoregressive (a factorization claim).** Generation produces the next
element conditional on the sequence so far, iterated: P(w_t | w_1..t-1).
Says nothing about internal implementation.

**History-preserving (an implementation claim).** The system carries a
computational state forward through time and updates it, rather than
recomputing from the raw prefix at each step; past internal states are
causally present in current processing.

The four quadrants are all occupied:

|                    | stateless                  | stateful            |
|--------------------|----------------------------|---------------------|
| **autoregressive** | transformer LLMs           | RNNs; (humans, per this work) |
| **non-autoreg.**   | diffusion LMs              | —                   |

Transformers are autoregressive and stateless: each forward pass recomputes
from the full context; KV caching is a speedup, not a memory (results are
identical to recomputation). Nothing of the previous step's computation is
causally carried.

## 2. The claims and their evidence

**Claim 1 — human production is consistent with the autoregressive
factorization.** Evidence: E5. Human word choice is statistically
indistinguishable from autoregressive sampling once the conditional model is
strong (GPT-2 XL: control 0.500, human 0.501; under the weak model humans
were MORE trajectory-coherent than samples, 0.485). The best next-word-
given-context factorization exhausts the content of what humans produce.
Read positively: what looked like "the momentum framing dying" is direct
corpus evidence for the sufficiency of the autoregressive factorization for
content. Caveats: one corpus, one strong model, rank-test power; content
only.

**Claim 2 — human processing is history-preserving.** Evidence: the timing
program (E9 across all corpora + E6 + E7). Curvature of the representational
trajectory predicts reading time (NS 86.8% of 174; SAP 86.8% of 2,000) and
speech pauses (Buckeye 90.0% of 40 talkers; Switchboard 67.1% of 4,747
sides), beyond surprisal AND beyond the full predictive distribution
(functional covariates; distribution-matched cells, 85.6%), strongest where
no constituent closes (81.4%), and only in LEARNED coordinates (untrained-
network control: trained intact at 86.2% with untrained controlled;
untrained residual fails at 60.3%).

**The key argument connecting timing to statefulness (the constant-cost
contrast).** A transformer's compute per token is constant — identical FLOPs
whether the next word continues the trajectory or bends it. That is the
signature of stateless recomputation: no state, no update, no update cost.
Human time cost per word varies with the geometry of the state transition —
larger at bends, in comprehension and production. A cost that scales with
the relation between where the state was heading and where it must go makes
mechanistic sense only if a persistent state is being updated: cheap when
the new state falls near the extrapolation of the carried past, expensive
when it does not. Geometry-dependent timing is the behavioral fingerprint of
a stateful incremental system. (Honest residue: this is an inference from
cost to architecture; a stateless system with a path-sensitive cost function
is logically constructible, just unmotivated. The neural version of the
measurement is the decisive test.)

**The two claims are NOT the same, and their independence is the point.**
LLMs prove autoregressivity does not require history-preservation. The
human data indicate humans have both. Full statement: human language
behavior shares the transformers' generative factorization (E5) and, unlike
transformers, is implemented by a history-preserving processor (E6/E7/E9).
Same class by generation, different class by mechanism — the RNN quadrant,
measured with a transformer's ruler.

## 3. The double finding (paper structure)

**Finding A (model-side, novel):** trajectory straightening is not a fact
about language models; it is the signature geometry of autoregressive
prediction on any learnable domain. E10: English +0.115, code +0.122,
protein +0.248 (ProtGPT2 on Swiss-Prot — no cognitive producer anywhere);
untrained twins flat (≤ +0.006); same U-shaped layer profile everywhere.
Nobody has claimed this for autoregressive systems generally (lit check
2026-08-14; two adjacent papers to read before asserting priority: arXiv
2604.23985 curvature↔model uncertainty; arXiv 2601.22364 context structure
and geometry).

**Finding B (human-side, novel):** human processing bears the behavioral
signature of membership in the class — costs concentrate at the bends,
beyond the entire predictive distribution, in learned coordinates only,
comprehension and production alike.

A and B need each other: A alone is an incremental extension of Hosseini &
Fedorenko; B alone is "beyond surprisal, again." Together: straightening is
the universal signature of autoregressive prediction; human timing tracks
that signature; the human system behaves like a member of the class — and
(constant-cost contrast) like a STATEFUL member.

## 4. The inversion (anti-circularity)

The models supply the measuring instrument for a property they themselves
lack. Trajectory structure is IN the transformer's representations —
installed by autoregressive training in any domain (E10) — but the
transformer does not USE it as a trajectory: it pays nothing at the bends
(constant per-token compute; direction preservation dies within a word at
the predictive layer). Humans, given the same signal, pay at exactly those
points. We are not finding the model in the human; we are finding in the
human something the model provably lacks.

Circularity resolution, in full: (i) the model is trained on content and
predicts timing it never saw; (ii) the trained-for statistics (the
distribution) are controlled and matched, and the effect survives — the
"humans in, humans out" loop closes at the distribution, and the result
lives outside it; (iii) the geometry is cognitively real only via learning
(untrained control); (iv) instrument dependence remains: the claim is
"as parameterized by prediction-trained representations," mitigated by
cross-architecture replication (Pythia/RoPE) and ultimately settled by
neural measurement.

## 5. Standing caveats (the ones a reviewer should find already stated)

1. Correlational, corpus-based; the paradigm experiment (E1) and neural
   data are the escalation path.
2. Integration-account residual: bend-words may be harder to COMPOSE, not
   harder to predict. Beyond-distribution results cut against standard
   versions (entropy/competition controlled), and production timing has no
   natural integration story — a speaker pausing before a bend is
   generation behaving extrapolatively. Not fully excluded in comprehension.
3. Cost→architecture is an inference (see constant-cost contrast).
4. E10 currently one checkpoint per domain; needs a second (RITA/ProGen2;
   second code model) + per-sequence CIs before Figure 1 hardens.
5. Effect sizes are modest; the claim is about consistency and specificity,
   not magnitude.
6. MVRR ambiguity-contrast reversal persists under curvature (0/24): a
   materials problem (the unambiguous control bends the trajectory as much
   as the garden path), reported as such. Item-level garden-path prediction
   remains null for all measures (Huang et al. stands).

## 6. Relation to the LRTIA program (three levels of memory)

Level 1 — how history enters the predictive state: LRTIA memory curves /
half-lives (context ablation). Level 2 — the predictive state exhausts
CONTENT: E5. Level 3 — the predictive state does not exhaust PROCESSING:
E7/E9/E6. One program: language systems carry memory in the distribution,
never in excess of it in content, and in excess of it in processing.
Cross-project bridge available in Buckeye (memory half-lives and pause
effects in the same corpus).

## 7. One-sentence versions

- The current predictive distribution is sufficient for what people write
  and insufficient for what it costs them to read or speak.
- Straightening is the geometry of autoregressive prediction; humans pay
  its behavioral price — which only a system that carries its past would pay.
- Models manifest the constraint as geometry; humans manifest it as time.
- Humans share the transformers' factorization but not their forgetting.
