# Event-segmentation annotation — instructions

Thank you for helping annotate these stories. Your task is to mark **event
boundaries**.

You will read ten short stories, presented one sentence per row in
`annotation_sheet.csv` (column `sentence`, in order, grouped by `story_id`).

For each sentence, decide: **does this sentence begin a new, natural, meaningful
unit of the story?** In other words, does the story move here into a new event,
scene, action, time, place, or (for the factual/expository stories) a new
sub-topic?

- If YES — a new unit begins at this sentence — put **1** in the
  `boundary_1_if_new_event` column.
- If NO — this sentence continues the current unit — leave it **blank** or put
  **0**.

Guidance (from the standard event-segmentation paradigm, Zacks & colleagues):
- Segment at the level of "natural and meaningful units." Aim for coarse-grained
  events, not a boundary at every sentence.
- Use your own judgment; there is no single right answer. We combine several
  people's judgments.
- Read each story through in order. The first sentence of each story is a
  partial fragment (the excerpt starts mid-sentence) — you may skip judging it.
- Typical rate is roughly one boundary every 3–5 sentences, but follow the
  story, not a quota.

Please annotate independently — do not discuss with other annotators until you
are done.

Save your completed file as `annotator_<yourID>.csv` (keep all columns) and
return it. Analysis then runs `analyze_human_boundaries.py`, which builds a
graded boundary-agreement score per sentence (fraction of annotators marking a
boundary) and re-runs the deep-ntee event test against the human consensus.
