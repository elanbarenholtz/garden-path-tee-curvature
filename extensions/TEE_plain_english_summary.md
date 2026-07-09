# How language models "move through meaning" — and what it tells us about reading
### A plain-English summary

## The big idea in one paragraph

When you read a sentence, your brain does work: some words are easy, some make you
slow down. For fifty years, the leading explanation has been *surprise* — you slow down
on words you didn't see coming. This project asks whether there's a second kind of work
hiding underneath surprise, having to do not with *what word comes next* but with
*where the meaning has moved*. Using an AI language model as a kind of measuring
instrument, we found that there is — and that it operates at two different scales, like
the difference between a car swerving to avoid a pothole and a car exiting the highway
onto a different road entirely.

## The setup, and the words you need

**Language model.** A program (here, GPT-2, an older and well-understood one) trained to
predict the next word in a text. To do that it builds an internal "state" for every word
— a long list of numbers, 768 of them, that encodes what it has understood so far. You
can think of this state as a *point in a vast space of possible meanings*.

**Trajectory.** As the model reads word by word, that point moves. Word 1 puts it
somewhere; word 2 nudges it; word 3 nudges it again. String those points together and
you get a path — a trajectory — winding through meaning-space. Reading, for the model,
is a journey along this path.

**Surprisal.** The standard measure: how unexpected each word was, given everything
before it. High surprisal = the model (and, it turns out, human readers) didn't see that
word coming. This is the "what comes next" quantity, and it's about *probability*.

**TEE (Trajectory Extrapolation Error).** Our lab's measure, and the star of the show.
The idea: look at the last few steps of the path, draw a straight line continuing in the
same direction (extrapolate), and ask — did the next word land where that line predicted,
or did it veer off? The size of the veer is TEE. It's a *geometric* quantity: it's about
*direction of motion through meaning-space*, not probability. A big TEE means the meaning
suddenly turned.

The key discovery of our earlier work was that TEE predicts human reading times *even
after you account for surprisal*. In other words, the "veer" costs readers extra effort
that surprise alone doesn't explain. Surprise asks "was this word likely?"; TEE asks "did
the meaning have to change course to fit this word?"

## The puzzle this project set out to solve

Our earlier work had found a frustrating limit. The veer is a purely *local* event: the
meaning turns, the reader pays a small cost right then, and it's over within a word.
Meanwhile surprise has *long-range* consequences — an unexpected word keeps reshaping how
the model reads the next five, ten words. So the story seemed to be: geometry (the veer)
is local; only information (surprise) reaches far.

That felt too tidy. The nagging suspicion was that we'd only measured geometry in the
crudest possible way — as *point-to-point* motion, with a *straight-line* prediction.
Real trajectories can be curved, and meaning can move at more than one scale. So we asked
two questions the original measure couldn't: what if we track motion between *regions* of
meaning-space rather than exact points, and what if we allow the predicted path to
*curve*?

## What we did

**Neighborhood scale.** Instead of exact points, we grouped the model's states into 100
"neighborhoods" — clusters of similar meanings, discovered automatically. Now we could
track not just "the point wiggled" but "the meaning moved from *this* region to *that*
region." We call the veer at this coarser scale **neighborhood TEE**. If ordinary TEE is
the car swerving within its lane, neighborhood TEE is the car changing which road it's on.

**Two ways to measure "cost."** For each word we measured two things. One, **reading
time** — how long real people (from a public dataset of many readers) actually paused on
that word; this is the *human* cost. Two, a **causal test inside the model**: we deleted a
word from the model's memory and watched how far downstream its absence changed the
model's understanding — this is the model's *internal* reach, its "wake," like the ripples
behind a boat.

We ran everything with heavy statistical caution: controlling for word length, word
frequency, punctuation quirks, position in the text, and re-checking every result on
independent slices of the data so we couldn't fool ourselves.

## What we found

**1. The neighborhood veer is a genuine, separate cost to readers.** Even after
accounting for surprise *and* ordinary word-level TEE, when a word moves the meaning into
a new neighborhood, people slow down on it. So there's a second geometric signal in
reading, one level up from the first.

**2. And unlike the local veer, the neighborhood veer reaches far — inside the model.**
This is the headline. When we deleted a word that had relocated the meaning to a new
neighborhood, the model's understanding stayed disturbed for ten or more words
downstream. The long-range influence our earlier work thought was missing from geometry
was there all along — we just had to look at the right scale. The tidy story ("geometry
is local, only information travels") was wrong; it was an artifact of measuring geometry
too finely. Long-range structure lives in *neighborhood* geometry.

**3. The two scales live in different parts of the model.** A language model has layers,
like an assembly line that refines meaning in stages. We found the human reading-time cost
comes from *shallow* (early) layers, while the long internal reach comes from *deep*
(late) layers. Two different kinds of "moving through meaning," in two different places.

**4. It replicates.** We repeated the core findings in a medium-sized model and a very
large one. The signals show up in all of them (the largest one shuffles *where* in its
layers they appear, which is interesting in its own right), so this isn't a quirk of one
particular model.

**5. Curved paths matter — but only in one specific place.** Coming back to the "allow the
path to curve" question: letting the predicted path bend (instead of a straight line)
added nothing to the model's internal long-range reach — there, straight-line prediction
already captures everything. But the *curvature* of the deep-layer neighborhood path did
add a distinct sliver of the human reading-time cost that the straight-line version
missed. So nonlinearity earns its keep in exactly one corner: predicting human effort from
the deep, curved motion of meaning.

**6. The honest negative result.** It was tempting to interpret "moving to a new
neighborhood" as the model detecting *narrative events* — a scene change, a new topic, the
kind of boundary a human reader feels. We tested this properly, against a published
dataset where hundreds of people had marked where they felt a new event begins in short
stories. The result was a clean *null*: our neighborhood measure did **not** predict where
humans feel event boundaries. So we do **not** claim the model is tracking discourse the
way people do. We ran the obvious interpretation, it failed, and we changed the claim.
That negative result actually makes the rest more trustworthy — it shows where the
evidence stops.

## What it all means

Reading isn't driven by a single signal. There are at least three, and they separate
cleanly:

- **Surprise** — how unlikely the next word was. About probability. Travels far.
- **Fine (local) trajectory veer** — the meaning turning to fit the current word. A
  small, immediate cost, gone within a word. About structure, like grammar snapping into
  place.
- **Neighborhood relocation** — the meaning moving to a whole new region. Costs the reader
  effort *and* reshapes the model's understanding for many words afterward.

The one-line version: **long-range meaning wasn't absent from the geometry of reading; it
was only absent from the point-by-point version of that geometry.** Zoom out to
neighborhoods, and the far-reaching structure appears.

Importantly, this is a statement about how a language model represents text and about what
predicts human reading *speed* — not a theory of how humans consciously carve stories into
events (that's the part we tested and couldn't support). The contribution is showing that
"moving through meaning" happens at multiple scales at once, and that those scales do
measurably different jobs.

## Why it might matter beyond this paper

If reading effort has separable scales, that's a lever. It could sharpen models of how
people comprehend language, help explain why some texts feel effortful, and give AI
researchers a cleaner picture of what their models are actually doing internally as they
read — including how disturbances propagate, which matters for reliability. And
methodologically, it's a small case study in a good scientific habit: when your
convenient measurement tool (a straight line through single points) hides a phenomenon,
the fix isn't a better statistic, it's looking at the right scale.
