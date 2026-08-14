# Pre-registration — E6: Do producers pay the trajectory cost in time?

Written 2026-08-14, after E5 (production content is distribution-sufficient
under a strong model) and E7 (reading cost tracks the trajectory beyond the
current distribution). No timing variable has been extracted from any speech
corpus at the time of writing; no relation between any timing variable and
any model-derived measure has been examined. Committed before first run.

## Rationale

Compiled corpus statistics explain WHAT gets produced (E5): any lawful
history-dependence in production is absorbed into a strong model's
conditional distribution, so content cannot distinguish a trajectory
mechanism from a lookup implementing the same statistics. But a mechanism
costs TIME, and a lookup does not hesitate. E7 showed the comprehension
system pays a real-time trajectory cost beyond the current distribution.
E6 asks whether producers pay the same cost: do speakers hesitate before
words that depart from the recent representational trajectory?

## Corpora, two tiers

E6a (primary here): SBCSAE .trn transcripts, already in the repo, timed at
the INTONATION-UNIT (IU) level — each line carries onset/offset. Word-level
timing does not exist in these files; the design below is IU-level and says
so plainly.

E6b (registered now, run when available): Buckeye, word-level alignments,
pre-word gap and word duration — the clean version. Requires registration
(Elan). Same logic, word-level DV; its own implementation appendix will be
added BEFORE any Buckeye analysis runs.

## E6a design

Unit: within-speaker IU transitions — IU_j follows IU_{j-1} by the SAME
speaker with no intervening speech by another speaker (turn-internal).
Cross-speaker gaps are turn-taking, excluded from the primary analysis.

DV: pre-launch pause = onset(IU_j) − offset(IU_{j-1}), clipped to
[0, 5000] ms; primary DV = log(1 + pause_ms). (Speech commonly latches;
zero-inflation is handled by the two-part secondary below, and the primary
stays simple.)

Predictor: TEE of the FIRST word of IU_j — the word being launched after
the gap — computed with the paper's convention (GPT-2 Small layer 6, k = 3
word-level windows, last-subword states) over the conversation's interleaved
cleaned text (e5b_prepare.py output; word-to-token alignment by character
offsets, the E5 machinery).

Controls, all fixed now: surprisal of the launched word (GPT-2 Small, same
convention); the four E7 distribution functionals at the launched word;
Zipf frequency; word length; log word-count of IU_j (upcoming planning
load); log word-count of IU_{j-1}; position of the IU within the speaker's
turn (log); conversation-level position (log cumulative words). All
variables demeaned WITHIN SPEAKER before analysis (removes idiosyncratic
pause style and speech rate).

Model and criterion: per-conversation OLS of the demeaned DV on demeaned
TEE + demeaned controls (conversations with < 50 usable transitions
excluded and counted). CRITERION: Wilcoxon over conversation-level TEE
coefficients p < .01 AND >= 65% of conversations positive. Supporting:
pooled mixed model (conversation random intercepts), cluster-robust p.

Secondary (reported, no gate): two-part model — (i) P(pause > 200 ms),
logistic, same predictors; (ii) log pause among pauses > 200 ms.
Exploratory (labelled): IU articulation duration per word vs mean TEE.

## What is permitted before analysis

Counting usable transitions, inspecting timing-format quirks, and
validating the word-token alignment are preparation, permitted. Any look at
the relation between timing and TEE (or any model measure) before the
criterion run is not.

## Outcome logic (fixed now)

1. Criterion passes -> producers hesitate before trajectory departures:
   a real-time trajectory cost on the production side, beyond the current
   distribution (functionals controlled). With E7, mechanism on both sides
   of the channel; the compiled-statistics account cannot produce it.
   E6b (Buckeye, word-level) is then run as confirmation before anything
   is claimed in a manuscript.
2. Criterion fails at IU level -> no measurable trajectory cost at IU
   launches. Constrains but does not kill the mechanism (IU boundaries are
   planning-dominated; word-level E6b remains the decisive test). E7 is
   untouched either way.
3. Alignment or timing quality fails preparation checks -> reported;
   analysis not run on degraded data.

## Not permitted

Other DV transforms, other pause clips or thresholds, dropping controls,
switching to cross-speaker gaps, other TEE conventions, or subsetting
conversations beyond the stated minimum, in order to move the criterion.

---

## AMENDMENT 1 (2026-08-14, preparation stage; before any DV-TEE relation
has been examined)

Preparation findings, as permitted above: (1) the TRN files use two line
formats (space-separated and tab-separated timestamps); the parser handles
both. (2) The IU timestamps TILE — within a speaker's turn, each IU's onset
equals the previous IU's offset almost everywhere (98% of within-speaker
gaps < 200 ms; no timed pause parentheticals exist in these files). Silent
pauses are not in the timestamp gaps: the Du Bois convention transcribes
them as leading pause dots inside the FOLLOWING IU (".. " short, "..." long),
whose span absorbs the silence. The pre-launch gap DV is therefore
degenerate — preregistered outcome 3 for that DV, reported here.

REPLACEMENT PRIMARY DV, fixed before any analysis: the transcriber-coded
hesitation mark.

---

## RESULTS (2026-08-14) — E6a: OUTCOME 2, criterion FAILS (null)

Preparation gates: after fixing embedded NUL bytes in 5 TRN files (which
pandas' C parser silently truncated fields at) the alignment gate passed
60/60. 38,696 usable within-speaker turn-internal transitions, 59
conversations >= 50 (median n = 646), 228 speakers. Pause-mark rate 39.9%.

Criterion run: conversation-level TEE coefficients mean -0.00046, 49.2%
positive, Wilcoxon p = .78. Raw r(TEE, pause_mark) = +0.011. FAIL — a flat
null, not a marginal miss.

Preregistered interpretation (outcome 2): no measurable trajectory cost at
IU launches in spontaneous conversation, on the transcriber-coded hesitation
DV. This constrains the production side but does not kill the mechanism:
IU launches are planning-dominated, the DV is a coarse binary, and E7 is
untouched. The day's asymmetry is now itself the finding — the trajectory
cost is demonstrated in comprehension (E7: 74.7% of readers, p 7.9e-14) and
absent in production content (E5) and coarse production timing (E6a).
E6b (Buckeye, word-level acoustic gaps and durations) remains the decisive
production test and is the only path left to a production-side claim. pause_mark = 1 if the IU's raw text (before cleaning)
begins with pause dots after stripping leading overlap brackets and
vocal-noise parentheticals, else 0. Ordinal length (.. vs ...) is a
descriptive secondary. Model: per-conversation linear probability model of
demeaned pause_mark on demeaned TEE + the identical control set and
demeaning; identical criterion (Wilcoxon p < .01 AND >= 65% of conversations
positive). Everything else in this document is unchanged. E6b (Buckeye)
retains the acoustic word-level DV and remains the decisive tier.
