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

## AMENDMENT 2 — E6b implementation (2026-08-14, written BEFORE any
word-aligned corpus has been downloaded or inspected)

E6b uses word-level acoustic timing. Two corpora, decisions fixed now:

  Buckeye  (registration required — Elan): interview monologue, word-level
           forced alignment. The flagship tier.
  AMI      (free, CC BY 4.0; manual annotations archive with word-level
           start/end times): spontaneous multi-party meetings. Runs first
           if its download precedes Buckeye access.

Design, both corpora:
- Unit: consecutive word pairs (w_{j-1}, w_j) by the SAME speaker within the
  SAME transcribed segment/turn (no segment boundary between them).
- Primary DV: pre-word gap = onset(w_j) − offset(w_{j-1}), clipped to
  [0, 5000] ms, log(1 + gap_ms). Secondary (no gate): log word duration of
  w_j, with word length and syllable proxies added to its controls.
- Context for model measures: all corpus words of the recording ordered by
  onset (ties by speaker label), joined by spaces — the producer's context
  includes the interlocutors. TEE, surprisal, and the four functionals per
  the paper's conventions (as E6a).
- Controls: as E6a (surprisal, four functionals, Zipf frequency, word
  length, log position in segment, log cumulative words), demeaned within
  speaker.
- Cluster: speaker (>= 200 usable transitions; excluded-and-counted below
  that). CRITERION: Wilcoxon over speaker-level TEE coefficients p < .01
  AND >= 65% of speakers positive. Per the E5b lesson, any gate-style
  auxiliary check must also show a minimal deviation, not significance
  alone.
- Preparation (permitted before any DV-TEE contact): parsing, alignment
  validation, transition counts, gap distribution sanity (fraction > 200 ms
  reported; if the DV is degenerate as in E6a, that is reported and the
  corpus tier stops there).

Outcome logic: pass in either corpus -> producers hesitate before
trajectory departures at the word level; run the other corpus as
confirmation before any manuscript claim. Null in both word-level corpora,
given E6a's null -> production shows no measurable trajectory cost in
timing; the trajectory cost is comprehension-specific until neural or
paradigm data say otherwise.

### AMENDMENT 4 — Buckeye availability and operationalization (2026-08-14;
written after locating the archives on disk, BEFORE extracting or reading
any .words file)

Seven of forty Buckeye speakers are on disk from earlier licensed access
(s22, s25, s30, s32, s34, s35, s36 — determined by what was previously
downloaded, not by anything about the data). With 7 speakers the
preregistered speaker-level criterion is unsatisfiable (Wilcoxon n=7 min
p = .016 > .01), so the cluster unit is amended to SESSION (recording;
~5-6 per speaker, ~35-40 clusters expected): per-session OLS (>= 100
usable transitions), CRITERION: Wilcoxon over session coefficients p < .01
AND >= 65% of sessions positive.

Operationalization, fixed from the corpus documentation before reading any
file: .words lines give interval END times; a word's onset is the previous
entry's time. Transitions = consecutive words by the talker with ONLY
silence (<SIL>) or nothing between them; any intervening interviewer
speech (<IVER>), noise, or laughter excludes the transition (not
floor-holding). DV = log(1 + silence ms), clipped [0, 5000]. Context for
model measures: the talker's own words per session, in order (interviewer
speech is untranscribed in this corpus). Controls and demeaning as
Amendment 2 (within talker); word-level TEE/surprisal/functionals as E6a.

---

## RESULTS — E6b/E6c (2026-08-14)

**E6c Buckeye (word level, the decisive tier): CRITERION PASSES.**
40 sessions, 7 talkers, 43,028 clean same-talker word transitions (only
silence intervening; interviewer speech excludes). All 40 sessions >= 100
(median n = 1,067). Session-level TEE coefficients: mean +0.0558, **82.5%
of sessions positive**, Wilcoxon p = 8.7e-07. Every one of the 7 talkers is
positive individually (+0.005 to +0.110). Raw r(TEE, log gap) = +0.064;
the binary version r(TEE, gap > 200 ms) = +0.059. Controls included
surprisal and all four distribution functionals: the effect is beyond the
current predictive distribution, mirroring E7.

**AMI segment-launch variant (Amendment 3): FAIL.** 155 meetings >= 30
launches: mean -0.0026, 47.1% positive, p = .71. Null, consistent with
E6a's null at the same grain.

**The dissociation, read together with E6a:** the trajectory cost in
production appears at the WORD level within fluent speech — speakers pause
a beat before words that depart from the recent representational trajectory
— and does NOT appear at unit launches (SBCSAE hesitation marks, AMI
segment pauses), where whole-unit planning dominates and the first word's
TEE is a weak probe. This is the same grain at which the comprehension
effect lives (word-by-word RT).

**Claims licensed and limits.** Preregistered pass, single corpus, 7
talkers (subset fixed by prior availability), zero-inflated DV (4.5%
nonzero — though the binary version agrees). Amendment 2's outcome logic
asked for cross-corpus confirmation at word level; no second word-aligned
corpus with real gaps is available (both free corpora tile), so the Buckeye
result stands as a preregistered single-corpus finding pending the full
40-speaker corpus or another aligned corpus. Together with E7: a real-time
trajectory cost beyond the current predictive distribution now has evidence
on BOTH sides of the channel — comprehension (74.7% of 174 readers) and
production (82.5% of 40 sessions, 7/7 talkers) — while E5 shows the
CONTENT of production is distribution-sufficient. Mechanism in the
processor, statistics in the text.

### AMENDMENT 3 — AMI findings at preparation, and the segment-launch
variant (2026-08-14; before any DV-TEE relation has been examined)

Preparation findings: AMI's word-level times TILE within segments (100% of
894,727 within-segment same-speaker gaps are exactly 0 ms — the alignment
distributes segment time contiguously across words). The word-level DV is
degenerate in AMI; that tier stops here, as specified. Word-level acoustic
gaps now rest solely on Buckeye (silences are explicit entries there).

AMI does measure pauses at SEGMENT boundaries (segments are split at real
silences). Registered variant, decisions fixed now: unit = consecutive
segments by the same speaker where NO other speaker's word onset falls
inside the silence (floor-holding pauses; 11,050 such launches, median
1,510 ms, 99.3% > 200 ms — a live continuous DV). DV = log(1 + pause_ms),
pause clipped [0, 5000]. Predictor: TEE of the launched segment's first
word. Controls: as Amendment 2, plus log word-counts of the launched and
previous segments. Demeaning within speaker-session (meeting x channel).
Cluster for the criterion: MEETING (per-meeting OLS, >= 30 usable
launches; per-speaker cells are too small at ~16 median). CRITERION:
Wilcoxon over meeting-level TEE coefficients p < .01 AND >= 65% of
meetings positive. This variant is E6a's design with an acoustic
continuous DV; it is stronger than E6a but remains a unit-launch test —
Buckeye remains the word-level tier.

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
