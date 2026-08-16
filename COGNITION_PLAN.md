# Cognition submission — architecture (2026-08-14)

Decision: the submission carries the full arc — comprehension, distribution
sufficiency, production timing, and the content null. One thesis:

> The cost of processing a word tracks the relation between that word and
> the recent trajectory of the system's internal states — beyond the entire
> current predictive distribution — on both sides of the channel. The
> corresponding structure in TEXT is fully absorbed by a strong model's
> conditional distribution: the effect lives in the processor, not the
> artifact.

## Structure

**1. Introduction.** Surprisal theory's operational commitment: cost is a
function of the current predictive distribution. Two distinct ways the data
could exceed it: richer functionals of the same distribution (still a
"current-state" theory), or genuine dependence on how the state was
reached. The trajectory measure (TEE) as a candidate probe of the second.
Preview of the four results. (Keeps the existing v1/v2 intro spine —
surprisal framing, measure definition — with the momentum-in-text material
removed; no result values stated in the intro, per house style.)

**2. Study 1 — Comprehension.** The existing behavioral core, unchanged
numbers: Natural Stories headline (dAIC 78.4, beta +0.00298, p 3.1e-19;
67.3% of 171, Wilcoxon 2.4e-9), SAP partial replication (beta +0.0224,
61.1% vs the 65% bar, reported as partial), union surprisal control,
displacement control, window-sweep disclosure, syntax control incl. B2
within-constituent 79.5%. Figure 2 (unique-contribution bars) stays.

**3. Study 2 — Beyond the current distribution (E7).** TEE near-orthogonal
to distribution shape (r .04-.07). Effect with entropy/Renyi/top1/top10 in
the model: 74.7% of 174, p 1.3e-11; within distribution-matched cells
(91 cells, median 4,853 obs/participant): 74.7%, p 7.9e-14. This converts
Study 1's "beyond surprisal" into "beyond the current predictive
distribution" — the claim a Cognition reviewer would have demanded.

**4. Study 3 — Production timing (E6).** Primary: full Buckeye, 40
speakers, 252,401 transitions; speakers pause longer before high-TEE words
(mean +0.037, 67.5% of speakers, p 2.9e-3), controls incl. all four
distribution functionals. Discovery sequence disclosed: 7-talker subset
pass, then exact replication on the 33 unseen speakers. Switchboard: 4,747
sides, mean +0.032, p 5e-73, 61.5% vs the 65% bar -> partial replication,
mirroring NS->SAP. Boundary conditions reported: null at unit launches
(SBCSAE hesitation marks; AMI segment pauses) — the effect is word-grain.
The comprehension/production consistency table (67.3/61.1 vs 67.5/61.5).

**5. Study 4 — The content null (E5).** Rank-of-human-continuation test
with the AI-sampled gate and the model ladder; matched-model effect goes
0.4847 -> null at GPT-2 XL. Human text contains no trajectory information
beyond a strong model's conditional distribution. Placed AFTER the positive
results so it does the work it's actually doing: (a) killing the "it's just
text statistics" deflation of Studies 1-3 — if the cost merely reflected
corpus structure, a model that fully absorbs that structure (Study 4)
should absorb the cost predictors too, and it does not; (b) locating the
phenomenon: mechanism in the processor, statistics in the text.

**6. General discussion.** The two-sided cost and its grain (word-level,
not unit-level); what "beyond the current distribution" does and does not
license about memory/history in the processor; the E5 interpretation
ceiling stated plainly; relation to surprisal theory (a friendly amendment:
the cost function takes more than the distribution); limits: GPT-2 geometry
dependence, modest effect sizes, register attenuation in dialogue,
eye-tracking domain not addressed here (one sentence; separate line of
work); future: neural data, paradigm experiments (E1 in the notebook).

## What is NOT in the paper
- Momentum-in-text framing, direction-preservation geometry, Table 4 of the
  old draft (dead per signed-cosine + shuffle).
- Eye-tracking results (cut from v2; separate paper).
- Residual-logit E5 escalation (never run).

## Assets ready
- All numbers verified + committed under preregs (E5/E6/E7 files in
  gp_confound_check/); verify_numbers.py to be extended to the new claims.
- Base manuscript: the pre-momentum behavioral v2 (manuscript_preswap /
  audited text) is the prose spine for Intro + Study 1.

## Decisions taken (2026-08-14, Elan)
- Title: (a) "Processing cost tracks representational trajectory beyond the
  predictive distribution, in comprehension and production".
- E5: compressed control section before the General Discussion.
- arXiv v2 = this full manuscript.
- Drafting: keep audited prose; every new passage marked \new{}.

## Open decisions (Elan)
1. Title. Candidates:
   a. "Processing cost tracks representational trajectory beyond the
      predictive distribution, in comprehension and production"
   b. "The trajectory cost: reading and speaking slow before departures
      from a language model's representational path"
   c. "Beyond the current distribution: a two-sided trajectory cost in
      language processing"
2. Study 4 as full study vs. compressed "content control" section.
3. arXiv v2 = this full manuscript (replace the frozen momentum draft), or
   post the behavioral v2 first and make this the journal version.
4. Drafting mode: I draft into manuscript.tex keeping his audited prose and
   marking every new passage \new{} for his voice pass (as before).
