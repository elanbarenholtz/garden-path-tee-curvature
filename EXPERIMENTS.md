# Experiment notebook — trajectory extrapolation error

Running list of experiments worth doing. Add freely; nothing here is committed to.
Each entry: what it tests, what would count as an answer, what it costs.

Status key: **open** · **designed** · **piloting** · **running** · **done** · **dropped**

Last updated 2026-08-10.

---

## Where the open questions actually are

Two days of reanalysis narrowed things to a short list. The measure predicts
self-paced reading time in two corpora (Natural Stories, 178 participants;
SAP, 2,000 participants), survives every control we have thrown at it, and does
not transfer to eye movements — where the coefficient is not merely absent but
reliably *negative* across every specification tried. Nothing correlational is
going to resolve that. The experiments below exist because the corpus data have
been exhausted.

Equipment on hand: eye tracker.

---

## E1. Presentation mode, within subject — **the one to run first**

**Question.** Is the self-paced/eye-tracking dissociation a property of *preview*,
of *serial delivery*, or of neither?

**Design.** Same participants, same texts, three presentation conditions,
counterbalanced:

1. self-paced reading (serial, no preview, self-timed)
2. RSVP at fixed rate (serial, no preview, not self-timed)
3. free reading with eye tracking (parallel, preview available)

**Why it settles something.** Every claim about paradigms in the paper is
currently inferred *across* corpora with different materials, participants and
genres. This removes all of that in one study. It also separates two things the
current data conflate: preview and self-pacing. RSVP is the critical cell — it
removes preview while keeping reading, and it is not self-timed.

**Predictions, worth fixing before running.**
- If preview is the explanation: effect present in 1 and 2, absent in 3.
- If self-pacing is the explanation: present in 1, absent in 2 and 3.
- If neither: present in 1 only, and the account is something we have not named.

**Dependent measure problem.** RSVP has no natural per-word latency. Options:
comprehension probes at varying positions, pupillometry, or EEG. Unresolved —
this is the design's weak point and should be settled before anything else.

**Cost.** Moderate. 60+ participants for adequate power (see P1 below).

**Status: open.** Highest priority.

---

## E2. Matched-item experiment — turns correlation into manipulation

**Question.** Does trajectory disruption *cause* processing cost, holding
predictability constant?

**Design.** Construct or select sentence pairs matched on surprisal, frequency,
length and position but differing sharply in extrapolation error — and the
reverse. The tercile analysis in the paper identifies where such items live in
the corpus: the low-surprisal/high-TEE cell (n = 66,620) and the
high-surprisal/low-TEE cell (n = 50,260).

**Why it matters.** Everything to date is correlational on natural text with
correlated predictors. This is the only design on the list that supports a causal
claim, and it is the experiment the garden-path work was trying to be — except
the manipulation is driven by the measure rather than by a linguistic intuition
about reanalysis.

**Design constraint learned the hard way.** Controls must be matched on
*model-internal* baseline, not just on grammaticality and length. The MV/RR
failure in the SAP set happened because the unambiguous control
("the horse *that was* raced past the barn fell") is itself trajectory-disruptive:
baseline TEE 101.0 against 94.8–95.7 for the other constructions. A difference
score against an unmatched control is uninterpretable regardless of the measure.

**Status: open.** Second priority. Could be run in self-paced reading first,
which is cheap, before committing eye-tracker time.

---

## E3. Self-paced listening — the modality test

**Question.** Is the effect about *serial delivery* or about *reading*?

**Design.** Participants press to hear the next segment of spoken narrative.
A real paradigm, serial, no preview, auditory.

**Why it matters.** Speech is the modality comprehension is presumably adapted
for, and it affords no preview. If the measure predicts self-paced listening,
the "self-paced reading is an artificial task" objection largely dissolves, and
the paper's framing — that free reading is the unusual case rather than the
baseline — gains direct support rather than resting on an argument.

**Status: open.** Would pair well with E1 as a follow-up.

---

## E4. Boundary-paradigm preview manipulation

**Question.** Does removing parafoveal preview restore the effect in eye
movements?

**Design.** Gaze-contingent boundary manipulation: mask the upcoming word until
the eyes cross a boundary. Compare trajectory effects under normal vs denied
preview, within subject.

**Why it is not first.** More technically demanding than E1, and E1's RSVP cell
answers a similar question more cheaply. Worth it if E1 implicates preview and a
sharper test is wanted.

**Note.** The corpus proxy version of this test (launch-site distance, line-initial
position) was run and failed — the interaction was null and the gradient ran
opposite to prediction. That is weak evidence against the preview account, since
preview varies over a narrow range in ordinary reading, but it is evidence and it
should be stated when this is written up.

**Status: open.**

---

## P1. Power — needed before any of the above

Natural Stories gives β ≈ 0.004 with 73% of participants positive; resampling
says n = 10 detects that only 42% of the time. SAP gives β ≈ 0.025 with 61–63%
positive against a 52% permutation floor.

E2 should produce a substantially larger effect than either, since it contrasts
extremes rather than sampling continuous variation. E1 and E3 should not be
assumed to.

**To do:** run the power analysis against the observed per-participant
distribution rather than the mean, separately for each design. Plan for 60+
until that is done.

**Status: open.** Blocking for all of the above.

---

## E5. History beyond the current predictive distribution — **designed, preregistered**

**Question.** Does recent sequential history carry information about the actual
human continuation beyond the model's current next-token distribution P_t?

**Design.** At every eligible token position in Natural Stories: sample 20
candidate next tokens from P_t (temperature 1, no truncation), compute each
candidate's one-step deviation from the fit to the preceding 3 token states,
and take the mid-rank percentile of the *human* token's deviation among the 21.
Null: uniform ranks (mean 0.5). Negative control, run first and gating: an
extra P_t-sample designated as pseudo-target must be uniform by construction.
Model ladder is primary (GPT-2 Small / GPT-2 XL / Pythia-410M), in two
versions: fixed geometry with escalating P_t, and matched-model replication.

**Interpretation ceiling, fixed in advance.** A positive result shows the
*model's* output distribution is not a sufficient statistic relative to its own
trajectory — not that human production exceeds the human predictive state. If
the effect shrinks up the ladder, it was model weakness.

**Why this replaces the momentum geometry.** The rank test is a test of
exchangeability, not of any geometric story, so it is immune to the mechanical
sign structure that killed the signed-cosine analysis, and it carries its own
built-in falsification (the AI-sampled control).

**Cost.** ~13k positions × 22 single-token extensions per ladder rung, with
cached context: hours, not days.

**Status: running.** Full prereg: `gp_confound_check/PREREG_E5_history_sufficiency.md`.
v2 stays untouched until E5 is known to be null, model-limited, or strong.
Base rung: control gate PASS (0.502); human U = 0.4847, all 10 stories < 0.5
(humans land CLOSER to the extrapolation than the model's own samples);
XL P_t rung: 0.4919, survives but attenuates ~50%. Ladder completing.

**E5b — spontaneous speech.** Natural Stories is edited prose, so E5 cannot
separate brain-history from edit-history: the revision loop is non-Markovian
by construction. Identical pipeline on speech transcripts (Buckeye / Santa
Barbara / Switchboard / verified-unscripted monologue), fillers retained,
same gates. Decisions preregistered in the E5 prereg before acquiring data.
If prose is positive and speech is positive, the editing account dies; if
speech is null, the effect is a signature of composition and the brain
reading is dropped. **Status: designed.**

---

## Parked

- **Neural measures (EEG/MEG).** Would move the evidence from behaviour to
  mechanism. Also the natural home for a trajectory account, since the claim is
  about representational dynamics. Deferred: expensive, and the behavioural
  boundary should be pinned down first.
- **ECoG re-analysis.** Looked at; surprisal effects were weak in that dataset,
  so a smaller measure failing there was uninformative.
- **Generation-side test.** If local trajectory continuity contributes to
  processing ease, human- and machine-produced text may differ in trajectory
  statistics, and decoding strategies preserving trajectory coherence may
  produce text that is easier to read. Speculative; a testable extension rather
  than a next step.

---

## Things not to repeat

- Do not use an off-the-shelf item set without checking the *controls* on the
  measure. See E2.
- Do not test a hypothesis using a proxy that varies over a narrow range and
  treat the null as informative. See E4.
- Fix the criterion before running, and report it when it fails. The 65% sign
  agreement threshold was set on Natural Stories and is not met in the SAP
  corpus; that is reported rather than adjusted.
