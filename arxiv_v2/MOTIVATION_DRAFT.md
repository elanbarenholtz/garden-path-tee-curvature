# Reframed abstract and introduction opening

Motivation rebuilt around momentum in the representational sequence and the
failure of first-order Markov structure. Every premise is measured in the paper
rather than asserted from the literature.

The abstract's second half is unchanged from the audited version — those
sentences carry hedges that two independent audits forced in, and they should
not be touched while rewriting the opening.

---

## Abstract

Language comprehension unfolds sequentially, with each word processed against a
context that the preceding words have already built. Reading times are well
predicted by surprisal: the negative log probability of a word given that
context. But surprisal compresses the entire preceding context into a single
number attached to a single word, and in doing so discards the shape of the
process that produced it. It records how unexpected a word was, not whether that
word continued the direction in which the interpretation had been moving or
turned it.

That distinction would be idle if the interpretive sequence had no direction to
speak of. It does. Passing text through a transformer language model and
tracking its hidden states, we find that successive steps through
representational space are directionally aligned far above chance (0.44 against
a random baseline of 0.03), and that this alignment decays within a word or two.
Language, so represented, has short-range momentum. It follows that the sequence
of interpretive states is not a first-order Markov process: where the
representation currently sits underdetermines where it goes next, and the recent
path carries information that the current position does not. Surprisal cannot
express that information, because a scalar over the next word has no direction.

We therefore ask whether human processing cost is sensitive to it. At each word
we fit a line to the preceding hidden states, extrapolate one step, and measure
how far the actual state lands from that prediction. On the Natural Stories
corpus, this measure is correlated with but not reducible to surprisal (r = .31)
and independently predicts self-paced reading times. The effect survives a
control built from four surprisal estimates spanning GPT-2 and Pythia and
replicates across model scale and across architectures with different positional
encoding schemes (GPT-2 vs. Pythia/RoPE). In a second self-paced corpus of 2,000
participants the effect is present in the same direction but falls short of our
pre-specified reliability criterion on participant sign agreement (61%, against a
threshold of 65%); we report it as partial rather than full replication. A
displacement control shows the effect is not reducible to representational change
magnitude: entered together, extrapolation error retains its effect and
displacement does not. Neither extrapolation error nor surprisal accounts for the
magnitude of garden-path difficulty at the item level, consistent with prior
benchmark findings. The results point to two partly separable sources of
self-paced reading cost: how unexpected a word is, and how far it departs from
the direction the interpretation was already travelling.

---

## Introduction, opening paragraphs

**¶1 — the phenomenon and the standard account.** *(largely unchanged)*

Language comes in a sequence. The reader never receives the whole sentence at
once; each word modifies an interpretation already underway, and word-by-word
reading time gives a fairly direct behavioural trace of that process. Its most
robust regularity is also its simplest: predictable words are read faster than
unpredictable ones. The dominant account is surprisal theory
\citep{hale2001,levy2008}, on which the cost of a word is proportional to its
negative log probability given the preceding context. Surprisal predicts reading
times across self-paced reading \citep{smith2013}, eye tracking
\citep{demberg2008}, and neural measures \citep{frank2015}.

**¶2 — what surprisal is committed to.** *(new)*

Surprisal is computed from the entire preceding context, so it is not a
memoryless quantity in the way an n-gram statistic would be. Its commitment lies
elsewhere. Surprisal reduces the context to a distribution over the next word,
and then to a single number drawn from that distribution, and surprisal theory
treats that number as sufficient: given how unexpected a word was, nothing
further about how the interpretation reached its current state should bear on
the cost of processing it. The history is used to compute the statistic and then
discarded. This is a substantive assumption rather than a technical convenience,
and it is testable.

**¶3 — why the discarded information might not be noise.** *(new — the premise)*

Whether anything is lost depends on whether the interpretive sequence has
structure that a scalar cannot carry. A sequence of states can be characterised
not only by where it is but by how it is moving, and those are independent
properties only if the movement is not random. If the representation performed a
random walk, each step would be independent of the last, the current state would
be a complete summary, and nothing would remain for a trajectory to add.

It does not. Using a transformer's hidden states as a proxy for the evolving
interpretation, successive steps through representational space are directionally
aligned well above chance, and that alignment falls off sharply after one word
(Section~\ref{sec:direction}). Language, so represented, carries short-range
momentum. The consequence is that the state sequence is not first-order Markov.
Were it so, the current state would render earlier states irrelevant to what
comes next; instead, knowing where the representation was two words ago tells you
something about where it is heading that knowing where it is now does not.

**¶4 — why this should be true of language, not just of models.** *(revised
from the existing production paragraph)*

There is a reason to expect exactly this, and to expect it at short range.
Language production is itself sequential and locally planned: speakers and
writers plan a few words ahead, execute, and re-plan
\citep{levelt1989,ferreira2002}. A process of that kind leaves stretches over
which the context evolves coherently in one direction before turning — momentum
with a horizon of a few words, which is what the representational measurements
show. On this view the structure is a trace of production left in the signal, not
an artefact of any particular model, and a comprehender able to track it would be
exploiting a real regularity of the input rather than imposing one.

**¶5 — the prediction and the measure.** *(bridge into the existing text)*

If readers are sensitive to that regularity, processing cost should depend on
departures from the established direction, over and above word-level
predictability. Detecting such a departure requires something surprisal does not:
the recent states must still be available when the current word arrives, so that
the comparison can be made at all. We operationalise this as trajectory
extrapolation error. At each word position we fit a linear trajectory to the
hidden states of the preceding k words (typically k = 3), extrapolate one step
forward, and measure the Euclidean distance between the predicted position and
the actual hidden state...

*(continues into the existing Introduction from "The measure captures the degree
to which the current word deviates...")*

---

## Notes

**On the Markov vocabulary.** The claim is made about the *state sequence*, not
about the language or about surprisal. Surprisal conditions on the full prefix
and is not Markov of any fixed order; saying otherwise invites an immediate
objection. What is at issue is whether the current state is a sufficient summary
— the Markov property for the cost function — and the direction-preservation
result says it is not.

**What the premise rests on.** ¶3 asserts momentum on the strength of the
direction-preservation analysis (0.436 at the current step against a 0.029
random baseline, falling to 0.099 at one step ahead). That analysis currently
appears in the Results as a characterisation of the measure. Under this framing
it becomes a premise for the whole argument and probably needs to move earlier,
or at minimum be forward-referenced from the Introduction.

**One weakness to be aware of.** The momentum is measured in GPT-2's
representation of language, not in language directly. ¶4 argues that production
is the source, which is plausible but not shown here. A reviewer may press on
whether the alignment is a property of text or of transformers — the Pythia
replication helps, since the structure appears under a different architecture and
positional encoding, but it does not fully settle it.
