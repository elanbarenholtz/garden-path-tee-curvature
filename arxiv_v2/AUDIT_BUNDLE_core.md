# Independent audit request — arXiv:2606.05346v2

You are auditing a manuscript against the analysis outputs that produced it. Do
not recompute the analyses. Your job is to determine whether every claim in the
paper is actually supported by the material in this repository, and to find the
places where it is not.

**Assume there is at least one unsupported claim. Your task is to find it.** A
report that finds nothing will be treated as a failed audit, not a clean bill of
health.

---

## Why this is being asked

This manuscript is a correction of a previous version. Four substantive errors
have already been found and fixed in it, and knowing their shape will help you
look in the right places:

1. **A sample-construction error.** A lagged control was computed *after*
   filtering to a region of interest, silently dropping every observation at the
   first position. The reported N was correct arithmetic on the wrong sample.
2. **A mislabelled quantity.** The paper's framing claim was "nearly orthogonal
   to surprisal (r = .044)". The true correlation with surprisal is .31; .044
   was the correlation with *entropy*. The number was real, attached to the
   wrong variable.
3. **A corrupted control.** Word frequency was computed without lowercasing or
   stripping attached punctuation, and was zero for 19.7% of tokens. It partly
   functioned as a punctuation indicator. Every dependent number changed.
4. **A stale qualitative claim.** A Discussion paragraph described which words
   populate certain cells of a matrix; three of its examples occurred zero times
   in the cell they were attributed to.

The common thread is that **arithmetic was never the problem**. Numbers were
correct and attached to the wrong claim, or computed on the wrong rows, or
inherited from a superseded pipeline. Look for that, not for typos.

---

## Materials

| what | where |
|---|---|
| manuscript source | `manuscript.tex` (new/changed text is wrapped in `\new{}`) |
| compiled PDF | `manuscript.pdf` |
| references | `references.bib` |
| figures | `fig1_schematic.png`, `fig_core.png`, `fig3_dissociation.png`, `fig4_direction.png` |
| figure-generating code | `make_fig_core3.py`, `make_fig3.py` |
| analysis scripts | `../gp_confound_check/*.py` |
| analysis outputs | `../gp_confound_check/*_out.txt`, `*.txt`, `RESULTS_*.md` |
| locked samples | `../rebuild_v2_outputs/sample_8a6087341e.csv`, `../gp_confound_check/sap_measures_L6k3.csv` |
| existing weak check | `verify_numbers.py` — confirms each number appears *somewhere* in the outputs; it cannot tell whether it is attached to the right claim |

The garden-path reading-time corpus (`ClassicGardenPathSet.csv`, 180 MB) is not
included; it is third-party data available from the SAP Benchmark authors.

---

## What to check, in priority order

### 1. Provenance of every numeric claim

For each number in the manuscript, identify the specific output file and line it
came from, and confirm it is attached to the same quantity there. This is the
check that would have caught the `r = .044` error, and the one
`verify_numbers.py` cannot do.

Produce a table: `claim (with location) | value | source file:line | verdict |
note`. Verdicts: **matches** / **mismatch** / **not found** / **found but
describes a different quantity**.

### 2. Verbal claims that assert a result without a number

Phrases like "survives", "does not replicate", "strengthens", "is unaffected",
"reproduces". Each asserts an empirical outcome. Find the analysis behind it and
say whether it supports the wording. Pay attention to directional words —
*strengthens* and *weakens* have been wrong in this manuscript before.

### 3. Do the Methods describe what the code does?

Read the Methods section against the scripts. Check in particular:
- the specification of each model (which predictors, which random effects)
- how the measure is computed (layer, window, word-state convention, whether the
  first token can enter a fit window)
- filtering and exclusion rules, and their order relative to any lagged variable
- how word frequency is computed

Any discrepancy between description and code is a finding.

### 4. Internal consistency

The same quantity should agree wherever it appears — abstract, results text,
tables, figure captions, figures. Sample sizes and participant counts should be
consistent and should match the outputs.

### 5. Claims that outrun their evidence

Statements where the analysis supports something narrower than the sentence
says. Two specific things to weigh:
- the paper reports results from **two self-paced reading corpora** and claims
  the second is an out-of-sample application of decisions fixed on the first.
  Check whether the two specifications are in fact identical, and whether the
  text's characterisation of that is accurate.
- the paper reports a **pre-specified criterion** (65% sign agreement with group
  p < .01) and reports where it is not met. Check that it is applied
  consistently and that no result is described as supported where the criterion
  fails.

### 6. Anything the paper should report and does not

Analyses present in the scripts and outputs whose results do not appear in the
manuscript. For each, judge whether the omission is reasonable scoping or
selective reporting. Note that eye-tracking analyses were deliberately excluded
and deferred to separate work; that decision is documented in
`../GEOMETRY_PAPER_NOTES.md` and is not the kind of omission being asked about.

---

## Output

A single report with:

1. **Findings**, ordered by severity, each with: the claim, its location, what
   the evidence actually shows, and what would fix it.
2. **The provenance table** from step 1.
3. **A list of claims you could not verify**, and what would be needed.
4. **Your judgement** on whether the manuscript is safe to post, with reasons.

Be specific and quote the manuscript. Do not soften findings. If a claim is
unsupported, say so plainly rather than describing it as "potentially
overstated".


##############################################################################
# MANUSCRIPT
##############################################################################


==============================================================================
### FILE: manuscript.tex
==============================================================================

```
    1 | \documentclass[12pt]{article}
    2 | 
    3 | % Packages
    4 | \usepackage{amsmath}
    5 | \usepackage{graphicx}
    6 | \usepackage{booktabs}
    7 | \usepackage{natbib}
    8 | \usepackage{hyperref}
    9 | \usepackage{geometry}
   10 | \usepackage{mathptmx} % Times font
   11 | \usepackage{multirow}
   12 | \usepackage{array}
   13 | \usepackage{placeins}
   14 | 
   15 | % Page setup
   16 | \geometry{margin=1in}
   17 | 
   18 | % Hyperref setup
   19 | \hypersetup{
   20 |   colorlinks=true,
   21 |   linkcolor=blue,
   22 |   citecolor=blue,
   23 |   urlcolor=blue
   24 | }
   25 | 
   26 | \title{Trajectory Dynamics in Language Model Hidden States Predict Human Processing Costs Beyond Surprisal}
   27 | 
   28 | \author{Elan Barenholtz\\
   29 | Machine Perception \& Cognitive Robotics Laboratory\\
   30 | Department of Psychology / Center for Complex Systems\\
   31 | Florida Atlantic University\\
   32 | \texttt{elan.barenholtz@fau.edu}}
   33 | 
   34 | \date{}
   35 | 
   36 | % ---- REVIEW AID: new/changed text in v2 is wrapped in \new{...} and set bold.
   37 | % ---- To turn the highlighting off, change the definition to \newcommand{\new}[1]{#1}
   38 | \newcommand{\new}[1]{{\bfseries #1}}
   39 | 
   40 | \begin{document}
   41 | 
   42 | \maketitle
   43 | 
   44 | \begin{abstract}
   45 | Human language comprehension unfolds sequentially: each word is processed in the context of those that came before, and the interpretation builds incrementally over time. Surprisal, the negative log probability of a word given its context, has been the dominant predictor of incremental processing cost. But surprisal reduces rich sequential representations to a single scalar at each word, discarding information about the direction in which the interpretation has been evolving. Dynamical-systems approaches suggest that the trajectory of the evolving interpretive state, not just its position at each moment, should shape processing, and language itself may have short-horizon continuity, since speakers plan utterances a few words at a time. We introduce trajectory extrapolation error: at each word, we fit a linear trajectory to the preceding hidden states of a transformer language model and measure deviation from the extrapolated path. On the Natural Stories corpus, this measure is \new{correlated with but not reducible to} surprisal (\new{$r = .31$}) and independently predicts self-paced reading times. The effect \new{holds in a second self-paced corpus of 2,000 participants, survives a control built from four surprisal estimates across three model families, and replicates across model scale and} across architectures with different positional encoding schemes (GPT-2 vs.\ Pythia/RoPE). A displacement control shows the effect is not reducible to representational change magnitude\new{: entered together, extrapolation error retains its effect and displacement does not}. \new{Neither extrapolation error nor surprisal accounts for the magnitude of garden-path difficulty at the item level, consistent with prior benchmark findings.} These findings reveal two dissociable components of \new{self-paced reading} cost: word-level prediction error (surprisal) and sensitivity to local continuity in the evolving interpretive representation (trajectory extrapolation error).
   46 | 
   47 | \end{abstract}
   48 | 
   49 | \newpage
   50 | 
   51 | \section{Introduction}
   52 | 
   53 | Human language comprehension unfolds sequentially. Words arrive one at a time, and the reader or listener must build an interpretation incrementally, each word updating and extending the representation constructed from those that came before. Understanding this incremental process is a central problem in psycholinguistics, and the word-by-word variation in reading times has long served as its primary empirical signature. A core regularity in this signature is that words predictable in context are processed more quickly than words that are not. The dominant computational framework for explaining this regularity is surprisal theory \citep{hale2001,levy2008}, which holds that the cost of processing a word is proportional to its negative log probability given the preceding context. % [v2] DELETED: the v1 sentence beginning "The framework follows naturally from
   54 | % information-theoretic considerations..." committed to a belief-updating
   55 | % mechanism (comprehender maintains a probability distribution; low-probability
   56 | % words impose an update cost). Removed rather than rewritten.
   57 | Surprisal has been remarkably successful as a predictor of reading times across self-paced reading \citep{smith2013}, eye-tracking \citep{demberg2008}, and neural measures \citep{frank2015}.
   58 | 
   59 | Computing surprisal requires an underlying predictive model. Early work used n-gram models and probabilistic grammars \citep{hale2001,demberg2008,roark2009}, which provided useful but limited estimates of word predictability. Transformer-based language models have since become the standard tool \citep{goodkind2018,wilcox2020,schrimpf2021}, largely because their surprisal estimates are better predictors of human reading times than those from earlier models, and because they can condition on arbitrarily long contexts rather than fixed windows. They are also a natural fit because they are themselves sequential processors: trained to predict the next token given the preceding sequence, they build rich internal representations that update incrementally as each word is encountered. Because these models are trained on human-produced text, the statistical structure they capture --- sensitivity to context, coherence, discourse --- is the same structure latent in that production, which is what makes their surprisal a useful index of the predictive regularities to which human comprehenders are sensitive.
   60 | 
   61 | But sequential processing may involve more than step-by-step prediction. An alternative theoretical tradition treats comprehension not as a series of independent predictions but as a dynamical process in which the interpretive state evolves through a continuous representational space \citep{tabor1999,spivey2007,cho2017}. Under this account, the trajectory of the evolving state, not just its position at each moment, carries information that shapes processing. This is especially likely for language, because human language production itself is a sequential, locally planned process. Speakers and writers plan a few words ahead, execute that plan, and then re-plan \citep{levelt1989,ferreira2002}, creating text with local momentum: stretches over which the context evolves in a coherent direction before shifting. If this momentum is a real property of natural language, and if comprehenders are sensitive to it, then the direction in which the interpretation has been evolving, not just the probability of the next word, should matter for processing.
   62 | 
   63 | Testing whether trajectory dynamics shape human processing requires a way to measure trajectory structure in an evolving interpretive representation. Modern transformer language models like GPT-2 \citep{radford2019} provide one. Their hidden states encode a rich, incrementally updated representation of the context processed so far, and because the model is trained on human-produced text, these representations come to reflect not only the predictive structure that surprisal captures, but also other latent regularities of production --- including the short-horizon continuity of how each word's representation extends from those of its predecessors. Here, we introduce a simple measure that we call trajectory extrapolation error. At each word position, we fit a linear trajectory to the hidden states of the preceding $k$ words (typically $k = 3$), extrapolate one step forward, and measure the Euclidean distance between this predicted position and the actual hidden state. The measure captures the degree to which the current word deviates from where the representation was heading: high extrapolation error means the representation was moving in one direction and the current word forced it somewhere else; low error means the current word continued the established drift.
   64 | 
   65 | The logic of comparing trajectory extrapolation error against surprisal is asymmetric. Surprisal is expected to predict processing cost under either tradition, since improbable words tend to disrupt trajectories; finding that surprisal matters does not distinguish between the frameworks. Finding that trajectory extrapolation error adds independent explanatory power beyond surprisal would, by contrast, be informative: it would suggest that the dynamical character of comprehension contributes to processing cost in a way that word-level prediction error does not capture. Two words with identical conditional probability receive identical surprisal even if one continues an established interpretive trajectory and the other forces a sharp representational turn, and any cost difference between such words is evidence for directional dynamics in comprehension. This asymmetry is not a limitation of the language models from which surprisal is derived: their hidden states already carry the trajectory information, but surprisal as an output measure collapses it to a scalar.
   66 | 
   67 | \new{This paper is concerned with whether the dynamics that surprisal discards are psychologically relevant.} Human processing unfolds under strong constraints of recency and local influence \citep{gibson1998,lewis2005}, meaning that recent words dominate the current interpretive state. Under such constraints, the trajectory of the interpretation over the last few words is the comprehender's best available signal about where things are heading. Sensitivity to this trajectory, tracking the recent drift of the interpretation rather than treating each word as an independent event, would constitute an efficient processing strategy that exploits the local momentum of natural language. Garden-path sentences provide an intuitive illustration: in ``The horse raced past the barn fell,'' each word after ``raced'' reinforces the main-verb interpretation, building momentum in one direction, and the cost at ``fell'' reflects not just the word's unexpectedness but the reversal of accumulated interpretive direction. But if trajectory sensitivity is a general feature of human processing, the phenomenon should not be limited to garden paths. Any word that forces the interpretation off its recent trajectory should incur a cost, even in ordinary text, and this cost should be measurable independently of surprisal.
   68 | 
   69 | 
   70 | \new{Our primary dataset is the Natural Stories corpus \citep{futrell2018}, where the measure can be evaluated over thousands of word positions of naturalistic connected text read by 181 participants. This is the larger and less constrained test, and it is where our analytic decisions---the model specification, the use of subject-level inference, and the criteria for judging an effect reliable---were made. We then turn to the Classic Garden Path materials of the SAP Benchmark \citep{huang2024}, applying those decisions without modification. These materials were of interest for a specific reason: the disambiguating word of a garden-path sentence is a theoretically motivated locus of trajectory disruption, a point at which the interpretation is known to reverse, and if the measure indexes the cost of such reversals it should register there in particular. We ask two questions of them. The first concerns the ambiguity manipulation: does the difference in extrapolation error between a garden-path sentence and its unambiguous control predict the difference in reading time, across items? The second sets the manipulation aside and treats the materials as what they also are---a second self-paced reading corpus, 144 syntactically difficult sentences read by 2,000 participants---and asks whether the Natural Stories result holds there.}
   71 | 
   72 | \new{Both corpora use self-paced reading, which delivers words serially, one at a time and only on request. We take up the question of whether the effect extends to reading with free eye movements separately; the evidence reported here concerns serial presentation.}
   73 | 
   74 | Three additional analyses clarify what the measure captures. A displacement control assesses whether the contribution of extrapolation error reduces to the magnitude of representational change at each word. A direction-preservation analysis on the Natural Stories corpus characterizes the temporal scale of the underlying trajectory structure in the model. Finally, \new{a cross-architecture replication using Pythia (which uses Rotary Position Embeddings rather than the absolute positional embeddings of GPT-2) tests whether any effect of trajectory structure generalizes across model scale and positional encoding scheme, and a series of surprisal controls drawn from larger models tests whether the effect is a residual of poor predictability estimation by any one model}.
   75 | 
   76 | \section{Method}
   77 | 
   78 | \subsection{Materials}
   79 | 
   80 | \paragraph{Garden-path sentences.} To test the trajectory effect at a controlled, theoretically motivated locus of disruption, we used the Classic Garden Path subset of the SAP Benchmark \citep{huang2024}, a large-scale syntactic ambiguity processing dataset. The subset contains 24 items covering three structural types: main-verb/reduced-relative (MVRR; e.g., ``The horse raced past the barn fell''), NP/S direct-object/sentential-complement (e.g., ``The suspect showed the file deserved more attention''), and NP/Z transitive/intransitive (e.g., ``While the man hunted the deer ran into the woods''). Each item appeared in ambiguous and unambiguous conditions, where the unambiguous version included an overt syntactic marker (e.g., a relative pronoun) that prevents the garden-path misparse. Human reading-time data were collected via self-paced word-by-word reading from over 2,000 participants. Reaction times were filtered to exclude responses below 100 ms or above 5,000 ms.\new{\footnote{An earlier version of this paper (arXiv:2606.05346v1) reported a reading-time analysis restricted to the critical region of these materials. That analysis contained a sample-construction error and is withdrawn; see the version note. The materials are analysed here in two ways: as an ambiguity manipulation at the item level, and as a corpus of connected text.}} \new{These sentences were presented in isolation rather than embedded in running text, so fit windows near the start of a sentence could in principle include the first token, whose hidden-state magnitude is anomalously large in transformer models \citep{xiao2023}. We therefore begin every fit window at the second token, which excludes that position by construction and restricts the analysis to word positions 5 and later.}
   81 | 
   82 | \paragraph{Natural Stories.} To evaluate the same measure across thousands of word positions in naturalistic text, we used the Natural Stories corpus \citep{futrell2018}, which consists of 10 naturalistic narratives totaling approximately 10,000 words. Self-paced reading times were collected from 181 participants, yielding 845,479 observations after filtering to 100--3,000 ms\new{; 813,621 observations from 178 participants remain after the measure and its controls are defined}. We processed each story through GPT-2 in overlapping chunks to accommodate the model's 1,024-token context limit, computing hidden states and surprisal at every word position.
   83 | 
   84 | \subsection{Trajectory Extrapolation Error}
   85 | 
   86 | \paragraph{Definition.} Let $h_t$ denote the hidden-state vector at word position $t$ in a given layer of a transformer language model. For a window of size $k$, we fit a linear trajectory to the hidden states at positions $t{-}k$ through $t{-}1$ by ordinary least squares. The extrapolated position at the next time step is the linear prediction at time $k$, and trajectory extrapolation error is defined as the Euclidean distance between the extrapolated and actual hidden states (see Figure~\ref{fig:schematic} for a schematic illustration). This quantity measures how far the representation landed from where it was heading, given the trajectory established by the preceding $k$ words.
   87 | 
   88 | \begin{figure}[!ht]
   89 | \centering
   90 | \includegraphics[width=\textwidth]{fig1_schematic.png}
   91 | \caption{Schematic illustration of trajectory extrapolation error. Each point $h_t$ represents the model's hidden-state vector at word position $t$, projected into a two-dimensional principal-component space for visualization. A linear trajectory is fit to the hidden states at the preceding $k$ positions (here $k = 3$: $h_{t-3}$ through $h_{t-1}$) and extrapolated one step forward to produce a predicted position (open circle, $\hat{h}_t$). Trajectory extrapolation error is the Euclidean distance between this predicted position and the actual hidden state $h_t$ (filled orange circle). (a) Low error: the current word's hidden state falls near the extrapolated position, continuing the established trajectory. (b) High error: the current word (e.g., a garden-path disambiguator) forces the hidden state far from the extrapolated position.}
   92 | \label{fig:schematic}
   93 | \end{figure}
   94 | 
   95 | \paragraph{Parameter selection.} We computed extrapolation error using GPT-2 (117M parameters; \citealp{radford2019}), which sits near the sweet spot for reading-time prediction identified by \citet{oh2023a}. We tested two layers: layer 6 (an intermediate layer) and the final layer (layer 12). We focus primarily on layer 6 because intermediate layers are known to capture syntactic representations more effectively than output layers in transformer models \citep{hewitt2019,jawahar2019}. We swept window sizes of 3, 5, and 7 words with both linear and quadratic polynomial fits. The 3-word linear fit at layer 6 consistently outperformed longer windows and higher-degree fits, consistent with the subsequent finding that trajectory structure in the hidden states is strictly local. For sentences with subword tokenization, we used the hidden state at the last subword token of each word.
   96 | 
   97 | \subsection{Direction Preservation Analysis}
   98 | 
   99 | To characterize the trajectory structure underlying extrapolation error, we computed a direction preservation measure on the Natural Stories corpus. At each word position, we measured the absolute cosine similarity between the fitted trajectory direction (from the preceding $k$ words) and the actual displacement vector at the current word and at 1, 2, and 3 steps ahead. This measures whether the direction of representational change at one position predicts the direction of change at subsequent positions. For random vectors in 768-dimensional space, the expected absolute cosine similarity is approximately 0.029, providing a chance baseline.
  100 | 
  101 | \subsection{Statistical Analyses}
  102 | 
  103 | We fit linear mixed-effects models predicting log-transformed reading times, with random intercepts for participants. All continuous predictors were $z$-scored prior to entry. \new{Word frequency is the Zipf value of the lowercased word with attached punctuation removed. We note this explicitly because the frequency values used in v1 were derived without that normalisation and were zero for 19.7\% of tokens, including ordinary words carrying attached punctuation and words differing only in case; all frequency-dependent analyses reported here have been recomputed.} The baseline model (M0) included word length, word position, previous log RT, and log word frequency (Zipf score; standard psycholinguistic control, e.g., \citealp{smith2013}) as lexical controls. We then tested a series of nested models: M1 added surprisal; M2 added trajectory extrapolation error. Model comparisons were evaluated using the Akaike Information Criterion (AIC), the Bayesian Information Criterion (BIC), and likelihood ratio tests. AIC estimates out-of-sample prediction error, with lower values indicating better fit; BIC applies a stronger penalty for model complexity and is more conservative. For the Natural Stories analysis, we additionally included log word frequency as a control and tested the independence of surprisal and extrapolation error via correlation and a tercile-based dissociation analysis. As a further control, we tested whether extrapolation error reduces to simple one-step representational change by comparing it with embedding displacement ($\|h_t - h_{t-1}\|$) in a joint model including both measures alongside surprisal and lexical controls.
  104 | 
  105 | \new{Because a pooled model over hundreds of thousands of observations can register an effect that no individual reader shows, all reported effects were additionally estimated separately within each participant and tested across participants. We treat an effect as reliable when the group-level test reaches $p < .01$ and at least 65\% of participants share the sign of the coefficient. These criteria were fixed on Natural Stories and applied unchanged thereafter. Where sign agreement is reported, it is accompanied by a permutation floor obtained by shuffling the measure within participant and refitting.}
  106 | 
  107 | \new{To test the robustness of the effect across model scale and architecture, we repeated the Natural Stories analysis using Pythia-160M and Pythia-410M \citep{biderman2023}, which use Rotary Position Embeddings rather than the learned absolute position embeddings of GPT-2, testing the proportionally equivalent mid-layer of each. All models were evaluated on identical rows and identical participants.}
  108 | 
  109 | \new{Two comparisons were run on the garden-path materials. The first treats them as an ambiguity manipulation: for each item we computed the ambiguous-minus-unambiguous difference in extrapolation error, in surprisal, and in mean log reading time at the disambiguating word, and asked whether the model-derived differences predict the behavioural one across items, with and without fixed effects for construction. The second sets the manipulation aside and treats the materials as a reading-time corpus, using the same specification developed on Natural Stories.}
  110 | 
  111 | \section{Results}
  112 | 
  113 | \new{Figure~\ref{fig:contrib} summarises the central result in advance of the
  114 | detail. In both self-paced corpora, trajectory extrapolation error accounts for
  115 | reading-time variance that surprisal and lexical frequency do not, at roughly a
  116 | third the magnitude of surprisal in Natural Stories and comparably to it in the
  117 | garden-path corpus. The sections below establish that result on the Natural
  118 | Stories corpus, apply the same specification to the garden-path materials, and
  119 | then examine what the measure is and is not capturing.}
  120 | 
  121 | \subsection{Natural Stories}
  122 | 
  123 | \new{\paragraph{Reading-time prediction.} Trajectory extrapolation error predicts self-paced reading time beyond surprisal and lexical controls ($\Delta\text{AIC} = 78.4$, $\beta = +0.0030$, $p = 3.1 \times 10^{-19}$, $N = 812{,}730$, 178 participants). For scale, in the same model $\beta(\text{surprisal}) = +0.0103$, $\beta(\text{word length}) = +0.0134$ and $\beta(\text{log frequency}) = +0.0045$: the trajectory effect is a little under a third the magnitude of surprisal, and is a second-order effect on reading time rather than a competitor to it (Figure~\ref{fig:contrib}).}
  124 | 
  125 | \new{\paragraph{Subject-level inference.} Because a pooled model over 813,621 observations can register an effect that no individual reader exhibits, we estimated the model separately within each participant. Of 171 participants with sufficient data, 115 (67.3\%) showed a positive coefficient (sign test $p = 7.6 \times 10^{-6}$; Wilcoxon $p = 2.4 \times 10^{-9}$; $t(170) = 6.74$). Thirty-two participants reached individual significance. We adopt this form of inference throughout, and take 65\% sign agreement together with a group-level $p < .01$ as the criterion for a reliable effect.}
  126 | 
  127 | \new{\begin{figure}[!htbp]
  128 | \centering
  129 | \includegraphics[width=0.72\textwidth]{fig_core.png}
  130 | \caption{Unique contribution of each predictor to self-paced reading time, in
  131 | both corpora. Each coefficient is estimated within participant with every other
  132 | predictor in the model, and averaged across participants; bars are 95\%
  133 | confidence intervals over participants. Trajectory extrapolation error accounts
  134 | for reading-time variance that surprisal and lexical frequency do not, at
  135 | roughly a third the size of surprisal in Natural Stories and comparably to it in
  136 | the garden-path corpus. Nuisance controls (previous reading time, sentence
  137 | position and its quadratic terms) are included in every model but omitted from
  138 | the plot; word length is likewise omitted, being large enough in the garden-path
  139 | corpus ($+0.135$) to compress the remaining bars. Coefficients are standardised
  140 | within participant, so magnitudes are not directly comparable across corpora.}
  141 | \label{fig:contrib}
  142 | \end{figure}}
  143 | 
  144 | \new{\paragraph{Robustness.} The effect survives a control for word identity, centring the outcome and the remaining predictors within word type (2,919 types occurring five or more times; word length and frequency are constant within type and therefore drop out): it attenuates substantially but remains ($\Delta\text{AIC} = 23.1$, $p = 5.3 \times 10^{-7}$). A substantial share of the raw effect is therefore lexical, and a trajectory-specific component survives. Adding a punctuation covariate reduces it ($\Delta\text{AIC} = 70.0$), while restricting to punctuation-free words strengthens it ($\Delta\text{AIC} = 114.9$, $\beta = +0.0038$, $n = 716{,}641$).}
  145 | 
  146 | \paragraph{Independence of measures.} \new{Having established that the two measures contribute jointly, we turn to what distinguishes them.} The correlation between surprisal and extrapolation error at the word level was \new{$r = .31$, indicating that the two measures share roughly ten percent of their variance}. Whatever trajectory extrapolation error captures, it is not a nonlinear transformation of surprisal. \new{Because the measures are correlated, the evidence that each contributes independently rests on the analyses below rather than on the correlation.}
  147 | 
  148 | \paragraph{Dissociation analysis.} We split words into terciles on both surprisal and extrapolation error and examined mean log reading times in each cell of the resulting $3 \times 3$ matrix (Table~\ref{tab:dissociation}; Figure~\ref{fig:dissociation}). Words with high surprisal but low extrapolation error (surprising words that continue the trajectory) showed an increase of \new{$+0.029$} in log RT over the low/low baseline (\new{$t = 14.38$, $p = 8 \times 10^{-47}$}). Words with low surprisal but high extrapolation error (unsurprising words that disrupt the trajectory) showed an increase of \new{$+0.010$} (\new{$t = 5.43$, $p = 6 \times 10^{-8}$}). Both effects are significant, confirming that each measure captures unique variance in reading times.
  149 | 
  150 | \paragraph{Regression.} A mixed-effects model including both $z$-scored surprisal and $z$-scored extrapolation error confirmed independent\new{, additive contributions from each ($\beta_{\text{surprisal}} = +0.0102$, $\beta_{\text{extrapolation}} = +0.0030$). The additive model was preferred over one including their interaction ($\Delta\text{AIC} = 1.5$ in favour of the simpler model; interaction $\beta = +0.0002$, $p = .49$), indicating that surprisal and extrapolation error combine without amplifying or dampening each other. The margin is small, and we would not read the additivity as established, but there is no evidence of interaction.}
  151 | 
  152 | \begin{table}[!htbp]
  153 | \centering
  154 | \caption{Dissociation Matrix: Mean Log Reading Time by Surprisal $\times$ Extrapolation Error Tercile (Natural Stories)}
  155 | \label{tab:dissociation}
  156 | \begin{tabular}{lccc}
  157 | \toprule
  158 |  & \textbf{Low extrap error} & \textbf{Mid extrap error} & \textbf{High extrap error} \\
  159 | \midrule
  160 | \textbf{Low surprisal} & \new{baseline} & \new{+0.005} & \new{+0.010} \\
  161 | \textbf{Mid surprisal} & \new{+0.016} & \new{+0.016} & \new{+0.028} \\
  162 | \textbf{High surprisal} & \new{+0.029} & \new{+0.031} & \new{+0.041} \\
  163 | \bottomrule
  164 | \end{tabular}
  165 | 
  166 | \smallskip
  167 | \footnotesize
  168 | \textit{Note.} \new{Values are differences in mean log reading time from the low-surprisal / low-extrapolation baseline (5.717).} Off-diagonal cells represent the key dissociation: high surprisal / low extrapolation error reflects surprise without trajectory disruption; low surprisal / high extrapolation error reflects trajectory disruption without surprise. Both off-diagonal effects are independently significant (see text).
  169 | \end{table}
  170 | 
  171 | \begin{figure}[!htbp]
  172 | \centering
  173 | \includegraphics[width=0.8\textwidth]{fig3_dissociation.png}
  174 | \caption{Dissociation between surprisal and trajectory extrapolation error in Natural Stories. Heatmap shows mean log reading time in each cell of the $3 \times 3$ tercile matrix. The off-diagonal cells demonstrate that each measure captures unique variance: high surprisal / low extrapolation error (surprise without trajectory disruption) and low surprisal / high extrapolation error (trajectory disruption without surprise) both produce elevated reading times relative to the low/low baseline.}
  175 | \label{fig:dissociation}
  176 | \end{figure}
  177 | 
  178 | \FloatBarrier
  179 | 
  180 | \new{\subsection{Garden-Path Materials}
  181 | 
  182 | \paragraph{The ambiguity contrast.} Extrapolation error at the disambiguating word is higher in ambiguous than unambiguous sentences for NP/S ($+2.55$, 20 of 24 items) and NP/Z items ($+4.25$, 23 of 24), but reverses for main-verb/reduced-relative items ($-1.72$, 17 of 24, $t(23) = -3.26$, $p = .003$). Surprisal does not reverse for these items ($+5.23$, 23 of 24). The reversal reflects the item set rather than the measure. At the disambiguating word the three constructions produce nearly identical extrapolation error in the ambiguous condition (99.2, 98.3, 99.1), but the MV/RR unambiguous control sits at 101.0 against 95.7 and 94.8 for the other two. That control restores a full passive relative clause (``the horse \emph{that was} raced past the barn fell''), a low-frequency and structurally heavy construction that perturbs the trajectory about as much as the garden path does, so the difference score for these items compares two disrupted states rather than a disrupted state against a baseline. The disambiguating word and the three words entering its fit window are identical across conditions, so the difference is carried entirely by earlier context.
  183 | 
  184 | \paragraph{Item-level prediction.} Neither measure predicts the size of the human garden-path effect. Across 72 item $\times$ construction pairs, the ambiguous-minus-unambiguous difference in extrapolation error does not predict the corresponding difference in reading time once construction is controlled ($\beta = -0.019$, $p = .89$); surprisal does no better ($\beta = -0.035$, $p = .78$). This reproduces the central finding of \citet{huang2024} on their own materials.
  185 | 
  186 | \paragraph{Reading-time prediction across the corpus.} Setting the ambiguity manipulation aside, these 144 sentences constitute a self-paced reading corpus of syntactically difficult material read by 2,000 participants, and we analysed it as such: all words, all conditions, no region selection. Words whose fit window is undefined are excluded, restricting the analysis to word positions 5 and later and leaving 444,737 observations. Estimating the model separately within each participant and testing the coefficients across participants, extrapolation error predicted log reading time with word length, log frequency, punctuation, and position within the sentence entered flexibly (distance from sentence start and end, each with a quadratic term): $\beta = +0.0224$, 61.1\% of participants positive, Wilcoxon $p = 2.7 \times 10^{-32}$. Adding a sentence-final indicator to absorb wrap-up effects strengthens it slightly ($\beta = +0.0251$, 62.7\%). Permuting the measure within participant and refitting gives 50.7\% sign agreement (pooled over ten shuffles, range 49.5--51.9\%), which is the baseline against which those values should be read. The corresponding floor in Natural Stories is 48.9\% (range 45.6--57.3\%; the wider spread reflects the smaller participant sample). Entering the trajectory term as a B-spline rather than linearly does not improve fit in either corpus ($\Delta$AIC $-0.5$ to $-4.6$ in Natural Stories and $-2.0$ to $-6.8$ in the garden-path corpus, for 3 to 8 degrees of freedom), so we report it linearly throughout.
  187 | 
  188 | Replacing linear surprisal with a spline leaves the estimate essentially unchanged ($df = 3$: $+0.0202$; $df = 5$: $+0.0207$; $df = 8$: $+0.0209$). Read from the same per-participant fits, extrapolation error is the more consistent of the two measures across participants (61.1\% against surprisal's 56.6\%) but the smaller in magnitude: within participants $|\beta(\text{extrapolation})|$ exceeded $|\beta(\text{surprisal})|$ in 42.1\% of cases (paired $p = 3.7 \times 10^{-21}$). As in Natural Stories, it is a second-order contribution alongside surprisal rather than a competitor to it.
  189 | 
  190 | A threshold of 65\% sign agreement was fixed in advance of these analyses, carried over from Natural Stories. Neither measure meets it here under flexible position controls. Participants in this corpus contribute roughly 220 observations each against thousands in Natural Stories, so per-participant coefficients are correspondingly noisy, and we report sign agreement descriptively against the permutation floor rather than as a criterion.
  191 | 
  192 | \paragraph{Stronger surprisal controls.} Because the trajectory measure and the surprisal control are both derived from GPT-2 Small, the effect could in principle mark the words at which that model's probability estimate is poor rather than any property of the trajectory; controlling for the same model's surprisal cannot remove such a confound. Substituting surprisal from GPT-2 XL ($\beta = +0.0255$) or Pythia-410M ($+0.0255$), entering all three together ($+0.0254$), or splining all three at $df = 4$ ($+0.0246$) leaves the estimate unchanged. The same holds in Natural Stories, where the effect survives GPT-2 Medium ($\Delta\text{AIC} = 90.7$), GPT-2 XL ($95.7$) and Pythia-410M ($87.9$) surprisal entered singly, and all four jointly ($82.1$), against $78.4$ for the original specification.}
  193 | 
  194 | \subsection{Displacement Control}
  195 | 
  196 | To test whether extrapolation error reduced to simple representational change, we compared it with one-step displacement, $\|h_t - h_{t-1}\|$. \new{The two measures are strongly correlated ($r = .80$), and each predicts slower reading when entered alone (extrapolation error $\beta = +0.0030$; displacement $\beta = +0.0021$). Entered jointly with surprisal and lexical controls, however, extrapolation error retains its effect and in fact strengthens ($\beta = +0.0033$, $p = 2.8 \times 10^{-11}$), while displacement contributes nothing ($\beta = -0.0005$, $p = .35$; Table~\ref{tab:displacement}). Given how closely the two measures track each other, this is informative: what predicts reading time is not representational movement as such, but the component of that movement which departs from the established trajectory. This rules out the simplest alternative interpretation, that extrapolation error merely indexes the magnitude of representational change.}
  197 | 
  198 | \begin{table}[!htbp]
  199 | \centering
  200 | \caption{Displacement Control: Joint Model of One-Step Displacement and Extrapolation Error on Natural Stories Reading Times}
  201 | \label{tab:displacement}
  202 | \begin{tabular}{lrrr}
  203 | \toprule
  204 | \textbf{Predictor} & $\boldsymbol{\beta}$ & $\boldsymbol{\chi^2(1)}$ & $\boldsymbol{p}$ \\
  205 | \midrule
  206 | \new{Extrapolation error, alone} & \new{$+0.0030$} & \new{---} & \new{$3.1 \times 10^{-19}$} \\
  207 | \new{Displacement, alone} & \new{$+0.0021$} & \new{---} & \new{---} \\
  208 | \new{Extrapolation error, joint} & \new{$+0.0033$} & \new{---} & \new{$2.8 \times 10^{-11}$} \\
  209 | \new{Displacement, joint} & \new{$-0.0005$} & \new{---} & \new{$.35$} \\
  210 | \bottomrule
  211 | \end{tabular}
  212 | 
  213 | \smallskip
  214 | \footnotesize
  215 | \textit{Note.} \new{Mixed-effects models with by-participant random intercepts, alongside surprisal and lexical controls; $n = 812{,}730$. Correlation between displacement and extrapolation error: $r = .80$. Entered jointly, extrapolation error retains its effect and displacement falls to non-significance.}
  216 | \end{table}
  217 | 
  218 | \subsection{Direction Preservation}
  219 | 
  220 | The results reveal a clear dissociation across layers (Table~\ref{tab:direction}; Figure~\ref{fig:direction}). At layer 6, direction preservation at the current word position is 0.44, well above the random baseline of 0.029. However, preservation drops to 0.10 at one step ahead and remains at approximately 0.08 for two and three steps ahead. Direction effectively dies after a single word. At the final layer, direction preservation at the current step is 0.61 and remains at 0.54 across one, two, and three steps ahead. The final layer maintains persistent directional structure that the intermediate layer does not.
  221 | 
  222 | This finding clarifies what extrapolation error captures at layer 6. Because direction dies after one step, the linear fit over 3 words does not capture a persistent trajectory; rather, it captures local positional continuity --- the smooth displacement of hidden states due to the incremental nature of contextual updating. Higher-surprisal words showed lower direction preservation ($r = -0.10$ at layer 6), confirming that surprising words disrupt the trajectory at both positional and directional levels.
  223 | 
  224 | \begin{table}[!htbp]
  225 | \centering
  226 | \caption{Direction Preservation in Natural Stories by Layer and Steps Ahead}
  227 | \label{tab:direction}
  228 | \begin{tabular}{lccccc}
  229 | \toprule
  230 | \textbf{Layer} & \textbf{Current step} & \textbf{+1 step} & \textbf{+2 steps} & \textbf{+3 steps} & \textbf{Random baseline} \\
  231 | \midrule
  232 | Layer 6 ($w = 3$) & 0.44 & 0.10 & 0.08 & 0.08 & 0.029 \\
  233 | Layer 12 ($w = 3$) & 0.61 & 0.54 & 0.54 & 0.54 & 0.029 \\
  234 | Layer 6 ($w = 5$) & 0.39 & 0.09 & 0.08 & 0.07 & 0.029 \\
  235 | Layer 12 ($w = 5$) & 0.58 & 0.53 & 0.53 & 0.53 & 0.029 \\
  236 | \bottomrule
  237 | \end{tabular}
  238 | 
  239 | \smallskip
  240 | \footnotesize
  241 | \textit{Note.} Values represent mean absolute cosine similarity between the fitted trajectory direction and the displacement vector at each word position. Random baseline is the expected absolute cosine similarity between random vectors in 768-dimensional space.
  242 | \end{table}
  243 | 
  244 | \begin{figure}[t]
  245 | \centering
  246 | \includegraphics[width=0.8\textwidth]{fig4_direction.png}
  247 | \caption{Direction preservation decay by layer and steps ahead (Natural Stories). At layer 6, direction preservation drops from 0.44 at the current step to near-random levels (0.10) at one step ahead, indicating that the trajectory structure is strictly local. At the final layer (layer 12), direction preservation remains elevated (0.54) across all steps ahead, indicating persistent directional structure. Dashed horizontal line indicates the random baseline for 768-dimensional vectors (0.029).}
  248 | \label{fig:direction}
  249 | \end{figure}
  250 | 
  251 | \subsection{\new{Model Scale and Architecture}}
  252 | 
  253 | The preceding analyses all use GPT-2 variants, which share the same architecture and learned absolute positional embeddings. To test whether the trajectory extrapolation effect depends on this specific positional encoding scheme, we replicated the Natural Stories analysis using Pythia models \citep{biderman2023}, which use Rotary Position Embeddings (RoPE), a fundamentally different approach that encodes position through rotation of the hidden-state vectors rather than through additive position embeddings. We tested Pythia-160M (comparable to GPT-2 Small; mid-layer 6 of 12) and Pythia-410M (comparable to GPT-2 Medium; mid-layer 12 of 24).
  254 | 
  255 | The core finding replicated across both architectures (Table~\ref{tab:crossarch}). \new{All three models were evaluated on identical rows and identical participants ($n = 812{,}730$, 178 participants). Trajectory extrapolation error predicted reading times beyond surprisal in both Pythia-160M ($\Delta\text{AIC} = 88.3$, $\beta = +0.0029$, $p = 2.0 \times 10^{-21}$) and Pythia-410M ($\Delta\text{AIC} = 400.2$, $\beta = +0.0065$, $p = 1.7 \times 10^{-89}$), against $78.4$ for GPT-2 Small on the same data.} Direction preservation showed the same rapid decay at the mid-layer, dropping from 0.42 to near-random levels within a single step for both Pythia models, confirming that the strictly local trajectory structure is not an artifact of GPT-2's coordinate system.
  256 | 
  257 | \begin{table}[!htbp]
  258 | \centering
  259 | \caption{Cross-Architecture Replication: Pythia (RoPE) vs.\ GPT-2 (Absolute Position Embeddings)}
  260 | \label{tab:crossarch}
  261 | \begin{tabular}{lccrcc}
  262 | \toprule
  263 | \textbf{Model} & \textbf{Pos.\ enc.} & \new{$\boldsymbol{\beta}$} & \textbf{$\Delta$AIC} & \textbf{Dir.\ pres.\ +0} & \textbf{Dir.\ pres.\ +1} \\
  264 | \midrule
  265 | GPT-2 Small (117M) & Absolute & \new{$+0.0030$} & \new{78.4} & 0.44 & 0.10 \\
  266 | Pythia-160M & RoPE & \new{$+0.0029$} & \new{88.3} & 0.42 & 0.13 \\
  267 | Pythia-410M & RoPE & \new{$+0.0065$} & \new{400.2} & 0.42 & 0.11 \\
  268 | \bottomrule
  269 | \end{tabular}
  270 | 
  271 | \smallskip
  272 | \footnotesize
  273 | \textit{Note.} $\Delta$AIC extrap / surprisal = improvement from adding trajectory extrapolation error to the model already containing surprisal and lexical controls. \new{All three models are evaluated on identical rows and identical participants ($n = 812{,}730$, 178 participants).} Direction preservation values are mean absolute cosine similarity between the fitted trajectory direction and the displacement vector at the current (+0) and next (+1) word positions.
  274 | \end{table}
  275 | 
  276 | \FloatBarrier
  277 | 
  278 | \section{Discussion}
  279 | 
  280 | \subsection{Two Dimensions of Sequential Processing}
  281 | 
  282 | Surprisal-based accounts have been remarkably productive at predicting incremental processing costs, but they treat comprehension as a sequence of evaluations against a probability distribution and discard the temporal structure of how the interpretation has been evolving. The results presented here suggest that human readers are sensitive to that dynamical structure as well. Specifically, our results show that human language processing times are impacted by two dissociable properties of the incoming signal: the probability of each word given its context (surprisal) as well as the degree to which each word deviates from the short-horizon trajectory of the evolving representation (trajectory extrapolation error). Critically, the effect of trajectory extrapolation replicates across multiple datasets as well as diverse model architectures with fundamentally different positional encoding schemes (GPT-2's absolute embeddings and Pythia's Rotary Position Embeddings), confirming that it reflects genuine properties of the hidden-state dynamics rather than an artifact of any particular model's coordinate system.
  283 | 
  284 | Interestingly, surprisal and trajectory extrapolation error are \new{correlated but far from redundant ($r = .31$ in Natural Stories)}, making independent contributions to reading times. If both measures are derived from the same model processing the same text, why are they \new{not more closely aligned}? The answer is that they capture errors at different levels of the sequential process. Surprisal reflects the model's token-level prediction error: how unlikely was this specific word, given the full context? Trajectory extrapolation error reflects the representational reorientation cost: how much did the hidden state change direction, given where it had been heading? A word can be probable but trajectory-breaking (it was expected but redirects the interpretation), or improbable but trajectory-continuing (it was unlikely but keeps the representation moving in the same direction). The two dimensions are logically independent, and the \new{dissociation matrix shows that the distinction has consequences for reading time in both directions}.
  285 | 
  286 | \new{This does not mean that either measure resolves the standing difficulties for surprisal-based accounts. \citet{huang2024} report that language model surprisal does not explain the magnitude of syntactic disambiguation difficulty, with garden-path constructions showing the largest misalignment. Our item-level analysis of their materials reproduces this. Across 72 item $\times$ construction pairs, the ambiguous-minus-unambiguous difference in surprisal does not predict the corresponding difference in reading time once construction is controlled ($\beta = -0.035$, $p = .78$), and extrapolation error does no better ($\beta = -0.019$, $p = .89$). Moving from a model's output probabilities to the geometry of its internal states does not repair that misalignment.}
  287 | 
  288 | \new{One methodological point follows from the surprisal controls. Surprisal from larger, lower-perplexity language models is a \textit{weaker} predictor of human reading times \citep{oh2023b}, so substituting a larger model's surprisal makes for a less stringent control rather than a more stringent one: it absorbs less of the outcome variance, and any predictor entered alongside it will appear correspondingly stronger. We therefore evaluate extrapolation error against a control containing all four surprisal estimates entered together.}
  289 | 
  290 | The displacement control analysis in GPT-2 rules out the simplest alternative interpretation of the trajectory-extrapolation error finding: that it merely indexes the magnitude of representational change in the embedding space. In GPT-2, displacement and extrapolation error predict in opposite directions: large representational changes facilitate processing when they continue the trajectory, while deviations from the trajectory impede it. This confirms that the measure captures something specifically about local trajectory continuity rather than change magnitude. This opposite-sign pattern did not replicate in Pythia, where both measures predict in the same direction, suggesting that the specific relationship between displacement and trajectory deviation depends on the representational geometry of the model. However, the core finding, that trajectory extrapolation error contributes to reading-time prediction beyond surprisal, is robust across architectures.
  291 | 
  292 | The trajectory effect in Natural Stories is small in absolute terms (the coefficient is modest and the variance explained is a fraction of what surprisal contributes), but it is theoretically diagnostic: it is consistent, independent of surprisal, and directionally specific in a way that the simplest alternatives do not predict. The effect is more pronounced at controlled loci of trajectory disruption: in the garden-path data, trajectory extrapolation error contributes to reading-time prediction beyond surprisal and lexical controls at the disambiguation point and spillover ($\Delta\text{AIC} \approx 10\text{--}13$ in GPT-2 Small and Large after frequency control). This is consistent with the interpretation that what the measure indexes is the cost of trajectory deviation: garden-path sentences epitomize this kind of disruption, with the ambiguous region building an interpretive trajectory in one direction and the disambiguating word forcing a sharp reversal of that direction. At minimum, the data point to two dissociable components operating at different timescales: one that evaluates each word against a probability distribution, and another that is sensitive to the short-horizon trajectory structure of the interpretation as it evolves across words.
  293 | 
  294 | These results support a more dynamical process of language comprehension in which the trajectory of the evolving interpretive state, not just its position at each moment, shapes how each new word is processed. However, our results specifically support local representational continuity over a few-word window, not long-range directional momentum: the direction-preservation analysis confirms that directional structure dies within a single word at the predictive layer, so the trajectory the measure captures is strictly short-horizon. This pattern suggests that a single mechanism, whether framed as prediction error, information-theoretic surprise, or Bayesian updating, does not fully account for the costs of incremental comprehension.
  295 | 
  296 | \subsection{Trajectory as a Functional Property of Language}
  297 | 
  298 | Why might language comprehension track this short-term trajectory structure? The answer, we suggest, lies in both how language is produced and processed. Human language production is a sequential, locally planned process: speakers and writers plan a few words ahead, execute that plan, and then re-plan \citep{levelt1989,ferreira2002}. This creates text with local momentum: stretches over which the context evolves coherently in a particular direction before shifting. This momentum is not incidental. It is what maintains local coherence in the signal. The direction in which the interpretation has been moving carries information about the topic, the argument, the narrative arc, and this information would be lost if the representation were recomputed from scratch at every word. In this sense, trajectory is not merely a statistical regularity of text; it is a functional property of language that serves coherence. The 3-word window that dominates our results may correspond roughly to the planning horizon of human language production, and the trajectory structure at this timescale may reflect the sequential footprint of the production process itself.
  299 | 
  300 | Language models learn this short-horizon trajectory structure because it is present in their training data: human-produced text carries the local continuity of human production planning. The model's hidden states come to reflect this structure as a statistical byproduct of learning to predict the next word well. But the model does not use trajectory for its own processing; the direction-preservation analysis shows that at the predictive layer, each word is effectively a fresh computation, with near-zero directional persistence from one step to the next. The model recomputes from full context at every position. The trajectory is in the representation, not in the processing strategy.
  301 | 
  302 | From the standpoint of comprehension, language processing also proceeds under strong recency constraints and limited working memory \citep{gibson1998,lewis2005}, so re-deriving the full interpretation from the entire preceding context at every word is not a tractable strategy. Some compressed summary of recent context is computationally necessary, and the local trajectory of the evolving interpretation is a natural candidate: it summarizes where the interpretation has been going over the last few words. A word that continues this local trajectory is cheap to integrate; a word that forces a deviation is expensive. The empirical question we addressed is whether human reading times are sensitive to this kind of local-continuity signal beyond what surprisal already captures.
  303 | 
  304 | Garden-path sentences are where the local continuity fails most dramatically. The local trajectory established by the ambiguous region points in the wrong direction, and the disambiguating word reveals that what looked like a coherent local trajectory was misleading. Thus, we observed the strongest effect for these sentence types. But the phenomenon is not limited to garden paths. Any word that forces the representation off its recent trajectory incurs a cost, even in ordinary text, as demonstrated by the Natural Stories analysis.
  305 | 
  306 | This framing connects to lossy-context surprisal \citep{futrell2020}, which proposes that comprehenders work with a lossy representation of context rather than a perfect one. Trajectory extrapolation is a specific, extreme form of lossy context, perhaps the lossiest summary imaginable: a linear fit to three points in high-dimensional space. It also connects to the surprisal scaling paradox \citep{oh2023b}: as language models grow larger, their surprisal estimates reflect better full-context prediction, diverging from the recency-dominated processing that humans actually do. Our multi-model comparison offers a complementary perspective: while Oh and Schuler varied training data size, we varied model capacity within the same training data and found that the effect remains detectable across model sizes.
  307 | 
  308 | The kinds of words that populate the off-diagonal cells (reported in the Results) point to what the two measures are tracking. The low-surprisal / high-extrapolation cell is enriched for coordinators and complementizers (\new{``and'' at 3.9 times the corpus rate, ``as'' 3.6, ``had'' 3.5}), which are lexically routine connectives that open a new syntactic constituent whose hidden-state trajectory will be different in kind from the preceding one\new{, and for recurring story-specific proper nouns and content words (``bird'' 15.0, ``Elvis'' 14.9, ``manor'' 11.9), which are highly predictable within their narrative context but likewise begin a new constituent}. The high-surprisal / low-extrapolation cell is \new{depleted of closed-class items (31.6\% against a corpus baseline of 45.8\%) and enriched for} discourse pivots (\new{``now'', ``when'',} ``then''\new{)} that are lexically unexpected at that position but whose structural role the trajectory has already begun to accommodate. The pattern suggests that the trajectory dimension is sensitive to structural continuity (frame, theme, syntactic commitment), whereas surprisal indexes lexical identifiability over the full context. These appear to be different psycholinguistic constructs, and the dissociation observed in our regressions is consistent with that distinction.
  309 | 
  310 | \subsection{Prediction, Trajectory, and the Nature of Comprehension}
  311 | 
  312 | An intriguing question raised by these findings concerns the causal relationship between prediction and trajectory. In language models, trajectory structure is a byproduct of optimizing next-token prediction. The model learns to predict words, and trajectory emerges in the hidden states because human-produced text has momentum. Surprisal is the primary quantity; trajectory is secondary.
  313 | 
  314 | Whether the same priority holds in human comprehenders is an open question. One possibility is that prediction and trajectory sensitivity are genuinely independent components of processing, each contributing its own cost. Another, more speculative possibility is that the causal direction differs in humans: that comprehension is fundamentally a dynamical process in which the evolving representational state carries local trajectory continuity that is actively maintained and exploited, and that sensitivity to word-level probability arises partly as a consequence of this process rather than as a fully independent computation. Words that are improbable tend to be trajectory-breaking, which is why surprisal predicts processing costs; but some portion of what surprisal captures may reflect trajectory disruption rather than prediction error per se. The present data are consistent with both interpretations, and with intermediate accounts in which prediction and trajectory interact in ways that neither tradition has fully specified.
  315 | 
  316 | What the data do establish is that the two measures are dissociable \new{(correlated at $r = .31$ in Natural Stories, but with independent contributions to reading times)} and that this dissociation calls for explanation. A direct experimental test, constructing stimuli matched on surprisal but varying in trajectory disruption or vice versa, would provide sharper evidence about the relationship. The theoretical question of how prediction and trajectory relate in human processing remains open and experimentally tractable.
  317 | 
  318 | \subsection{Limitations and Future Directions}
  319 | 
  320 | \new{Several limitations should be noted. First, the effect is second-order relative to surprisal and to lexical frequency, and a substantial share of it is lexical: controlling word identity attenuates it by roughly 40\%. It is a contribution to processing cost, not a rival account of it. Second, the garden-path materials comprise 24 items in each of three constructions, which is too few to support the item-level test those materials were included for; neither our measure nor surprisal predicts item-level variation in the size of the garden-path effect, and with three constructions the between-construction comparison rests on three points. Third, all of the behavioural evidence reported here comes from self-paced reading, which delivers words serially and permits neither regressions nor parafoveal preview. Whether the effect extends to reading with free eye movements is not tested here, and claims about trajectory sensitivity in human processing should be confined to serial presentation until it is.}
  321 | 
  322 | The most promising future directions test the theoretical claims more directly. Constructing stimuli matched on surprisal but varying in trajectory disruption would provide the cleanest test of whether trajectory sensitivity is independent of word-level prediction\new{, and the tercile analysis reported above identifies where in the corpus such items are to be found}. Neural measures (EEG, MEG) could establish whether trajectory extrapolation error predicts brain responses independently of surprisal, moving the evidence from behavior to mechanism. \new{The restriction to serial presentation invites a specific design: presenting the same materials to the same readers under self-paced reading, serial visual presentation, and free eye movements would establish whether the effect depends on preview, on serial delivery, or on neither. Spoken presentation, which affords no preview either, would extend the same logic to the modality in which comprehension ordinarily occurs.}
  323 | 
  324 | A further implication concerns language generation. If local trajectory continuity contributes to processing ease, then human-produced and machine-produced text may differ in their trajectory statistics, and models or decoding strategies that preserve local trajectory coherence may yield text that is easier for humans to process. This remains speculative, but it offers a testable extension of the present framework.
  325 | 
  326 | \bibliographystyle{apalike}
  327 | \bibliography{references}
  328 | 
  329 | \end{document}
```


##############################################################################
# ANALYSIS OUTPUTS
##############################################################################


==============================================================================
### FILE: gp_confound_check/RESULTS_bridge.md
==============================================================================

```
    1 | # Bridge test: does uncertainty now predict extrapolation failure next? (2026-07-27)
    2 | 
    3 | Locked sample 8a6087341e, GPT-2 Small layer 6, 9,830 adjacent word pairs,
    4 | position + story FE, cluster-robust SEs by sentence.
    5 | Script `bridge_entropy_to_tee.py`.
    6 | 
    7 | The prediction, from taking King/Fedorenko/Hosseini's mechanism seriously: if a
    8 | bendy path leaves the model uncertain where to go next, then uncertainty at
    9 | word t should forecast a larger extrapolation error at word t+1. Neither paper
   10 | makes this prediction.
   11 | 
   12 | ## 1. The bridge holds
   13 | 
   14 | | model | β | p |
   15 | |---|---|---|
   16 | | entropy(t−1) → TEE(t), position + story FE | +0.137 | 9e-43 |
   17 | | + punctuation at t and t−1 | +0.134 | 8e-47 |
   18 | | + lexical properties of word t | +0.130 | 2e-57 |
   19 | | **+ surprisal at t (strict)** | **+0.123** | 3e-53 |
   20 | | + surprisal at t−1 as well | +0.056 | 4e-08 |
   21 | 
   22 | The effect survives controlling how surprising word t actually turned out to be
   23 | (+0.123). That matters: it is not merely that uncertain contexts contain
   24 | surprising words. Uncertainty *before* the word arrives forecasts how far the
   25 | representation lands from its extrapolated heading, over and above the word's
   26 | own surprisal.
   27 | 
   28 | Adding surprisal at t−1 cuts it to +0.056 (still p = 4e-8). Entropy and
   29 | surprisal at the same position share variance by construction, so this is the
   30 | conservative bound rather than a refutation.
   31 | 
   32 | **This links the two papers empirically: their prospective measure predicts my
   33 | retrospective one.**
   34 | 
   35 | ## 2. It is specifically the along-heading component
   36 | 
   37 | | outcome at word t | β from entropy(t−1) | p |
   38 | |---|---|---|
   39 | | **tee3_par** (along-heading: overshoot/undershoot) | **+0.149** | 3e-69 |
   40 | | **tee3_perp** (lateral: veering onto a new direction) | +0.005 | .52 (null) |
   41 | 
   42 | A clean dissociation. Uncertainty forecasts *mis-scaling of the step along the
   43 | direction of travel* — the model does not know how far to go — and has nothing
   44 | to say about whether the trajectory turns.
   45 | 
   46 | This is the sharpest result here. It says uncertainty and direction-change are
   47 | different things, which is exactly the structure/uncertainty split, now expressed
   48 | predictively across adjacent positions rather than as a same-position
   49 | correlation.
   50 | 
   51 | ## 3. Their measure forecasts TEE in the *opposite* direction
   52 | 
   53 | | model | β | p |
   54 | |---|---|---|
   55 | | curvature_3(t−1) → TEE(t) | **−0.151** | 2e-58 |
   56 | | curvature_1(t−1) → TEE(t) | **−0.225** | 1e-142 |
   57 | | joint: entropy(t−1) coefficient | +0.114 | 3e-44 |
   58 | | joint: curvature_3(t−1) coefficient | −0.137 | 2e-47 |
   59 | 
   60 | Both survive together with opposite signs. If the chain were simply
   61 | curvature → uncertainty → extrapolation failure, curvature should forecast TEE
   62 | *positively*. It does the reverse.
   63 | 
   64 | **Important caveat: this may be mechanical rather than meaningful.** A highly
   65 | bent recent path produces a fitted direction with a small norm — the steps
   66 | partly cancel — so the extrapolation lands near the recent centroid and cannot
   67 | overshoot far. A straight path yields a long extrapolation vector with more room
   68 | to miss. So curvature and TEE are plausibly coupled through the geometry of the
   69 | fit itself, independent of anything about language or uncertainty.
   70 | 
   71 | This needs a null model before it is interpreted: simulate random walks with
   72 | matched step-size distributions and varying curvature, and check whether the
   73 | negative curvature→TEE relationship appears there too. If it does, it is an
   74 | artifact of the measures and should be reported as such. **Do not put this in a
   75 | paper before running that check.**
   76 | 
   77 | ## 4. Same-position relationships are control-sensitive — handle with care
   78 | 
   79 | | specification | r or β for TEE × entropy |
   80 | |---|---|
   81 | | partial r, position + story FE | **+0.051** |
   82 | | partial r, + punctuation | +0.050 |
   83 | | regression, + punctuation + frequency + length | **−0.127** |
   84 | 
   85 | Adding word frequency flips the sign. Given r(TEE, log frequency) = −0.438,
   86 | frequency is a large shared influence on both measures. Any claim about the
   87 | same-position TEE–entropy relationship depends on the control set and should not
   88 | be made without stating it. This also bears on the v2 abstract: the honest
   89 | statement is that TEE and entropy are weakly and unstably related, not that they
   90 | are independent.
   91 | 
   92 | ## 5. What to take from this
   93 | 
   94 | **Solid:** uncertainty at one word forecasts extrapolation error at the next
   95 | (+0.123 with surprisal controlled), and it does so entirely through the
   96 | along-heading channel, not the lateral one.
   97 | 
   98 | **Interesting but unverified:** curvature forecasts extrapolation error
   99 | negatively. Likely mechanical; test with a null model first.
  100 | 
  101 | **Cautionary:** the same-position TEE–entropy correlation flips sign with
  102 | frequency controls, so the "nearly orthogonal to surprisal" framing was fragile
  103 | in more ways than the r = .31 finding already showed.
  104 | 
  105 | ## 6. Why this is worth writing up
  106 | 
  107 | It converts the relationship between the two papers from a rhetorical comparison
  108 | into a measured one. Their claim is that bendy paths make the model uncertain.
  109 | The bridge shows that when the model is uncertain, the representation
  110 | subsequently fails to land where its heading pointed — and specifically fails by
  111 | mis-scaling along the heading rather than by turning. That is a mechanistic
  112 | elaboration of their result using the more direct instrument, and it belongs in
  113 | the geometry paper as a section rather than in a dispute.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_displacement_control.md
==============================================================================

```
    1 | # Displacement control on the causal wake (2026-07-27)
    2 | 
    3 | The objection: the wake is measured by ablating word w and observing how much
    4 | downstream representations shift. A word that simply moves the hidden state a
    5 | long way — regardless of direction — removes more representational mass when
    6 | deleted, so it would produce a larger downstream shift mechanically. The
    7 | extensions wake models control surprisal, length, frequency and punctuation at
    8 | w, but nothing about the raw magnitude of w's own state change.
    9 | 
   10 | Scripts: `compute_displacement.py` (state recomputation), output
   11 | `displacement_output.txt`; displacement values in `displacement_8a6087341e.csv`.
   12 | 
   13 | ## Recomputation and validation gate
   14 | 
   15 | Layer-6 states recomputed with the project's conventions (CHUNK 1024,
   16 | STRIDE 512, first-write-wins, word = final subword), then validated against the
   17 | locked sample before any displacement value was used:
   18 | 
   19 | - closure_depth mismatches: **0 / 9,840**
   20 | - final_bpe mismatches: **0 / 9,840**
   21 | - max |tee_k3 − recomputed|: 1.0e-4 (cross-machine float32 GEMM variation, the
   22 |   same order the extensions run reports)
   23 | 
   24 | Three measures emitted: `disp_step` = ‖h[ls] − h[ls−1]‖ (last BPE step),
   25 | `disp_word` = ‖h[ls] − h[prev word's ls]‖ (word-to-word displacement, the
   26 | quantity of interest), `state_norm` = ‖h[ls]‖.
   27 | 
   28 | ## Displacement is strongly correlated with TEE — the control was worth running
   29 | 
   30 | | pair | r |
   31 | |---|---|
   32 | | disp_word × tee_k3 | **+0.80** |
   33 | | disp_word × tee3_perp | +0.76 |
   34 | | disp_word × ntee_k100 | see output |
   35 | 
   36 | This is much higher than I expected and is the reason the control matters: at
   37 | r = 0.80 with tee_k3, "how far the state moved" and "how far off-heading it
   38 | moved" are largely the same variable in this corpus. Any claim that TEE is not
   39 | reducible to displacement needs to be made carefully, and the arXiv paper's
   40 | opposite-signs dissociation for reading time becomes a more important result,
   41 | not a lesser one.
   42 | 
   43 | ## The neighborhood wake survives, essentially untouched
   44 | 
   45 | Punct-free, DV = wake_rel, with target controls throughout; displacement added
   46 | as a covariate at w.
   47 | 
   48 | | lag | ntee_k100 without disp | ntee_k100 with disp | disp_word |
   49 | |---|---|---|---|
   50 | | L1 | +0.1997 (7.4e-19) | **+0.1983 (1.2e-18)** | +0.1038 (.044)* |
   51 | | L2 | +0.1754 (1.2e-09) | +0.1750 (1.2e-09) | +0.0324 (.65) |
   52 | | L3 | +0.1715 (1.6e-09) | +0.1695 (1.9e-09) | +0.1443 (.028)* |
   53 | | L4 | +0.1672 (6.1e-08) | +0.1662 (6.3e-08) | +0.0698 (.30) |
   54 | | L5 | +0.1628 (1.5e-08) | +0.1621 (1.4e-08) | +0.0539 (.41) |
   55 | | L6 | +0.1331 (1.7e-06) | +0.1314 (1.8e-06) | +0.1178 (.063) |
   56 | | L7 | +0.1162 (2.3e-05) | +0.1156 (2.3e-05) | +0.0459 (.53) |
   57 | | L8 | +0.1326 (1.4e-06) | +0.1322 (1.2e-06) | +0.0285 (.70) |
   58 | | L9 | +0.1404 (3.1e-07) | +0.1400 (2.8e-07) | +0.0214 (.75) |
   59 | | L10 | +0.1298 (1.6e-06) | +0.1289 (1.5e-06) | +0.0623 (.39) |
   60 | 
   61 | The largest change at any lag is 0.0017 in β. Displacement itself is significant
   62 | at only 2 of 10 lags and never approaches ntee's magnitude.
   63 | 
   64 | **Interpretation.** The long-range causal wake is carried by *where* the
   65 | trajectory was relocated, not by *how much* the state moved. That is the
   66 | strongest form of the claim, and it is now defended against the obvious
   67 | mechanical objection. Given that displacement and the fine-grained TEE measures
   68 | are collinear at r ≈ 0.8, it is notable that neighborhood TEE is not — the
   69 | neighborhood construction evidently captures something displacement does not.
   70 | 
   71 | ## Recommendation
   72 | 
   73 | Add `disp_word` to the published wake specification alongside the target
   74 | controls. Both are free — neither changes a coefficient meaningfully — and
   75 | together they close the two most likely referee objections to a causal claim.
   76 | 
   77 | Report the r = 0.80 displacement–TEE correlation openly rather than letting a
   78 | reviewer discover it. It makes the dissociations that do hold more impressive,
   79 | and concealing it would be the kind of thing that looks worse than it is.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_extensions_audit.md
==============================================================================

```
    1 | # Extensions / tee_vs_curvature audit (2026-07-27)
    2 | 
    3 | Audited for the class of error that broke the garden-path analysis, then
    4 | stress-tested the headline claim. Scripts: `ext_wake_targetctrl.py`, output
    5 | `ext_wake_output.txt`.
    6 | 
    7 | ## Structural audit: this code is written to a different standard
    8 | 
    9 | | check | tee_vs_curvature + extensions |
   10 | |---|---|
   11 | | sample identity | MD5 hash of (story_id, word_idx) asserted before every table (`assert sh == "8a6087341e"`) |
   12 | | merge integrity | every merge uses `validate="one_to_one"`; row counts asserted (`assert len(D) == 9840`) |
   13 | | lag construction | lags computed on the full frame, **then** filtered — the correct order, and the exact inverse of the garden-path bug |
   14 | | punct-free subsets | derived after lagging, with predictors re-z-scored within subset |
   15 | | inference | cluster-robust SEs by sentence, position + story fixed effects throughout |
   16 | 
   17 | The garden-path failure mode is structurally impossible in this code. The
   18 | `validate="one_to_one"` calls alone would have raised on the merge patterns that
   19 | went wrong there.
   20 | 
   21 | Reproduction check: `analyze_dissociation.py` and `analyze_wake.py` were rerun
   22 | from the repo and reproduce their published tables exactly (dissociation:
   23 | TEE×closure +0.134, curvature×closure −0.029, curvature×entropy −0.116; wake:
   24 | perp significant at L1 only punct-free, surprisal persisting to L5).
   25 | 
   26 | ## The one real gap: missing target controls — and the claim survives it
   27 | 
   28 | The parent `analyze_wake.py` controls properties of the word being measured at
   29 | lag L (surprisal, length, frequency at w+L), on the reasoning that a
   30 | high-surprisal target has a more volatile state and will show a larger relative
   31 | change under any perturbation. The extensions version `x3b_analyze_wake.py`,
   32 | which produced the headline "neighborhood TEE has a causal wake at every lag
   33 | 1–10", **omits those controls**. No extensions script includes them.
   34 | 
   35 | Added back (punct-free, DV = wake_rel):
   36 | 
   37 | | lag | ntee_k100 as published | ntee_k100 + target controls |
   38 | |---|---|---|
   39 | | L1 | +0.1997 (8.7e-13) | +0.1997 (7.4e-19) |
   40 | | L2 | +0.1877 (2.0e-10) | +0.1754 (1.2e-09) |
   41 | | L3 | +0.1724 (2.5e-09) | +0.1715 (1.6e-09) |
   42 | | L4 | +0.1687 (5.8e-08) | +0.1672 (6.1e-08) |
   43 | | L5 | +0.1676 (6.8e-09) | +0.1628 (1.5e-08) |
   44 | | L6 | +0.1330 (2.0e-06) | +0.1331 (1.7e-06) |
   45 | | L7 | +0.1148 (3.1e-05) | +0.1162 (2.3e-05) |
   46 | | L8 | +0.1328 (1.1e-06) | +0.1326 (1.4e-06) |
   47 | | L9 | +0.1434 (1.6e-07) | +0.1404 (3.1e-07) |
   48 | | L10 | +0.1287 (2.0e-06) | — |
   49 | 
   50 | Essentially unchanged at every lag. The neighborhood wake is not an artifact of
   51 | target-word properties. Add the controls to the published spec anyway — it costs
   52 | nothing and closes an obvious reviewer question.
   53 | 
   54 | The same table also reproduces the parent dissociation cleanly: `tee3_perp`
   55 | (fine-grained reorientation) is significant at L1 and gone thereafter, while
   56 | `ntee_k100` persists to L10. That contrast — local at the point level,
   57 | propagating at the neighborhood level — is the substantive finding, and it holds
   58 | under the stricter spec.
   59 | 
   60 | ## Remaining caveats, none fatal
   61 | 
   62 | - **Wake n = 1,627** words (the ablation is expensive, computed on a STEP=6
   63 |   subsample of the locked sample). Smaller than the RT analyses by two orders of
   64 |   magnitude. Worth stating plainly; the effects are large enough to carry it.
   65 | - **No displacement control in any wake model.** The models control surprisal,
   66 |   length, frequency and punctuation at w, but not the raw magnitude of w's own
   67 |   state change. A reviewer could ask whether an unusual word mechanically
   68 |   produces a larger downstream perturbation regardless of trajectory geometry.
   69 |   The arXiv paper has a displacement control for the RT analyses; the analogous
   70 |   control for the wake analyses does not exist and would need hidden states to
   71 |   compute. **This is the one check I would run before submitting.**
   72 | - **Clustering circularity** was anticipated and handled — `x7_heldout_ntee.py`
   73 |   builds a held-out-clustering version (`ntee_ho`) and `x10_robustness_table.py`
   74 |   reruns the headline regressions with it. Good practice, already in place.
   75 | 
   76 | ## Bottom line
   77 | 
   78 | The newer pipelines are sound. The one methodological gap I found does not change
   79 | the result. Combined with the Natural Stories audit, a paper built on
   80 | locked-sample material — TEE/curvature dissociation, the par/perp cancellation,
   81 | neighborhood wake, and the reading-time result with its lexical and punctuation
   82 | robustness checks — rests on code I could not break.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_gp_sink_check.md
==============================================================================

```
    1 | # Garden path sink/punctuation diagnostic — results (2026-07-27)
    2 | 
    3 | SAP ClassicGP, 24 items × 3 constructions × {amb, unamb} = 144 sentences.
    4 | GPT-2 small, word-level TEE (final-subword states, linear fit, Euclidean error)
    5 | at the disambiguating word. Presentations: A isolated (presumed paper condition),
    6 | B neutral 10-word prefix, C isolated with word 0 dropped from fit windows.
    7 | Paired t on amb − unamb per item. Script: `gp_sink_check.py`;
    8 | full table: `gp_sink_check_results.csv`.
    9 | 
   10 | **The sink is present and large:** token-0 norm is ~36× the interior-token norm
   11 | at layer 6.
   12 | 
   13 | ## Verdict by configuration
   14 | 
   15 | | config | isolated | prefix | drop-tok0 | sink exposure (amb/unamb windows containing word 0) |
   16 | |---|---|---|---|---|
   17 | | L6 k=3 | +1.73, p=1e-4 | +1.76, p=6e-5 | identical | 0 / 0 — clean |
   18 | | L6 k=5 | **+458, p=7e-10** | −1.18, n.s. | +1.88, p=1e-3 | **0.42 / 0.00 — asymmetric** |
   19 | | L6 k=7 | −2.39, n.s. | +5.92, p=4e-5 | +4.94, p=4e-27 | 1.00 / 0.79 — asymmetric |
   20 | | L12 k=3 | −6.84, p=.008 | −5.11, n.s. | identical | 0 / 0 |
   21 | | L12 k=5 | +7.98, p=.01 | −4.38, p=.05 | −1.83, n.s. | 0.42 / 0.00 — asymmetric |
   22 | | L12 k=7 | −3.49, n.s. | −2.22, n.s. | −1.46, n.s. | 1.00 / 0.79 |
   23 | 
   24 | 1. **The headline configuration (L6, k=3) survives.** Fit windows at the
   25 |    disambiguator never reach token 0, and the amb>unamb effect is unchanged
   26 |    under context-prepending. The core validation claim is sink-clean.
   27 | 2. **k=5 and k=7 on isolated sentences are contaminated.** Window-sink
   28 |    exposure differs by condition (amb disambiguators sit 1–2 words earlier),
   29 |    and at k=5 the isolated "effect" is inflated ~200× (d=+458 vs +1.9 clean).
   30 |    Any manuscript result from w=5/w=7 — including the Table 1 L12/w=5 model,
   31 |    the strongest RT result — must be rerun with prefix or token-0 exclusion.
   32 | 3. **L12 does not support the validation claim** in any clean configuration
   33 |    (null or reversed).
   34 | 
   35 | ## Per-construction (L6, k=3, all presentations agree)
   36 | 
   37 | - NPS: +2.55, p=3e-6 — robust, punctuation-clean. Best exemplar.
   38 | - NPZ: +4.35, p=4e-7 — robust, BUT unambiguous versions contain the
   39 |   disambiguating comma inside the fit window (33% of unamb windows contain a
   40 |   punct-final state vs 0% amb); given punct tokens are rest states, part of
   41 |   this effect may be punctuation asymmetry. Needs a punct-matched control.
   42 | - **MVRR: −1.72, p=.003 — REVERSED.** "The horse raced…"-type items show
   43 |   *lower* TEE at disambiguation in the ambiguous condition. Contradicts the
   44 |   manuscript's blanket "higher extrapolation error across all configurations"
   45 |   sentence (which reports no numbers).
   46 | 
   47 | ## Implications for the Cognition submission
   48 | 
   49 | - The paper survives the sink at its central configuration — no withdrawal
   50 |   scenario — but the Methods must state presentation format and report this
   51 |   control, and the w=5/7 and L12 analyses must be rerun clean or dropped.
   52 | - The validation section should report numbers per construction and address
   53 |   the MVRR reversal and the NPZ comma confound rather than the current
   54 |   unquantified blanket claim.
   55 | - Caveat: this is a reconstruction of the paper's spec from its text
   56 |   (word-level windows, final-subword states, disambiguating word only, no
   57 |   ROI 1–2 spillover); if the original pipeline differed (token-level windows,
   58 |   BOS handling, ROI pooling), rerun this script with that spec before editing
   59 |   the manuscript.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_ns_audit.md
==============================================================================

```
    1 | # Natural Stories audit — looking for the garden-path failure mode (2026-07-27)
    2 | 
    3 | Checked the Natural Stories reading-time pipeline for the *class* of error that
    4 | broke the garden-path analysis. Run on the locked sample (8a6087341e, 9,840
    5 | words) merged to `processed_RTs.tsv` (848,875 rows, 180 participants),
    6 | replicating the prep in `garden-path-p1/ns_crossed_re.py`.
    7 | Scripts: `ns_audit.py`, output `ns_audit_output.txt`, `ns_pos_output.txt`.
    8 | 
    9 | ## Verdict: the Natural Stories result is sound. It does not have the bug.
   10 | 
   11 | | check | result |
   12 | |---|---|
   13 | | A. merge integrity | **clean** — 0 duplicate (story, zone) keys; 848,875 rows in, 848,875 out, no multiplication; 4.2% unmatched (words outside the locked sample, expected) |
   14 | | B. lagged control | **minor, harmless** — 99.4% of `prev_log_RT` values are the genuinely adjacent word; 4,868 rows (0.6%) point 2+ zones back because the RT filter ran first. Repairing it changes nothing: ΔAIC 109.8 → 107.0, β +0.00351 → +0.00344 |
   15 | | C. sample equality | **clean** — M1 and M2 are fit on identical rows, so the AIC comparison is legitimate |
   16 | | D. heterogeneity | **passes** — 9/10 stories positive; position effect varies in size but not in sign except at sentence-initial words |
   17 | 
   18 | The critical contrast with the garden-path analysis: there, filtering happened
   19 | *before* the lag was computed and deleted an entire condition (all ROI-0 rows).
   20 | Here the same ordering costs 0.6% of rows and mislabels rather than deletes.
   21 | Repairing it moves the headline by 3 AIC units out of 110.
   22 | 
   23 | ## Effect size on the locked sample
   24 | 
   25 | ΔAIC = **109.8**, β(TEE) = **+0.0035**, p = 4.0e-26, N = 813,621.
   26 | 
   27 | This is much stronger than the ΔAIC = 2.5 reported in the paper (Table 6,
   28 | GPT-2 Small), which came from `ns_crossed_re.py` with β = +0.00063, p = .034.
   29 | The locked-sample rebuild gives an effect five times larger and overwhelmingly
   30 | significant. Worth understanding which is right before either number is
   31 | published — most likely the locked sample has better word alignment (the
   32 | rebuild was specifically constructed to fix alignment bugs), but this should be
   33 | run down.
   34 | 
   35 | For scale, in the same model: β(surprisal) = +0.0112, β(log_freq) = +0.0072,
   36 | β(prev_log_RT) = +0.1396. TEE is about a third the size of surprisal — a real
   37 | but second-order effect, consistent with what the extensions writeups say.
   38 | 
   39 | ## One thing to disclose, not fix
   40 | 
   41 | The effect grows with distance into the sentence and reverses at sentence-initial
   42 | words:
   43 | 
   44 | | position from sentence start | n | β | p |
   45 | |---|---|---|---|
   46 | | 0–2 | 100,705 | **−0.0027** | .022 |
   47 | | 3–5 | 100,948 | +0.0031 | 9.8e-4 |
   48 | | 6–10 | 157,927 | +0.0053 | 6.6e-14 |
   49 | | 11–20 | 253,602 | +0.0033 | 7.0e-9 |
   50 | | 21+ | 200,439 | +0.0080 | 9.6e-33 |
   51 | 
   52 | TEE × position interaction: χ²(4) = 220.8, p = 1.3e-46.
   53 | 
   54 | This is *not* the garden-path problem. There, two adjacent positions inside a
   55 | three-word region disagreed and the pooled estimate exceeded both — the number
   56 | described nothing real. Here 4 of 5 bins agree, the pooled estimate sits inside
   57 | the range of its parts, and the one negative bin is sentence-initial words where
   58 | a 3-word backward window is partly undefined or spans a sentence boundary. That
   59 | is an interpretable boundary condition, and arguably the same first-token
   60 | geometry the sink work is about.
   61 | 
   62 | Recommended handling: report the position profile, exclude or flag
   63 | sentence-initial words, and note that the effect strengthens mid-sentence. A
   64 | reviewer who finds this unreported will be far more troubled than one who reads
   65 | it in the paper.
   66 | 
   67 | ## Still outstanding
   68 | 
   69 | - Reconcile ΔAIC 2.5 (paper) vs 109.8 (locked sample). Do not publish either
   70 |   until it is known why they differ.
   71 | - The `word_type` random-effect robustness check in `ns_crossed_re.py` never
   72 |   completed — `ns_crossed_re_results.csv` has only two rows, and the lexical
   73 |   baseline model is the missing one. Since word frequency is the dominant
   74 |   predictor of TEE, that is the check most worth having.
   75 | - The tee_vs_curvature and extensions pipelines have not yet been audited to
   76 |   this standard (task 7).
```


==============================================================================
### FILE: gp_confound_check/RESULTS_ns_robustness.md
==============================================================================

```
    1 | # Natural Stories: reconciliation and the two missing robustness checks (2026-07-27)
    2 | 
    3 | Scripts: `ns_robustness.py`, output `ns_robustness_output.txt`; reconciliation
    4 | in `ns_reconcile.txt`.
    5 | 
    6 | ## Reconciliation: why the paper says 2.5 and the locked sample says 112
    7 | 
    8 | Not a sample-size difference, and not a control difference.
    9 | 
   10 | | | paper (`ns_crossed_re.py`) | locked sample (8a6087341e) |
   11 | |---|---|---|
   12 | | N | ~800k RT observations | 812,730 |
   13 | | M1 AIC | 189,030.9 | 161,314.6 |
   14 | | controls | word length, log freq, zone, prev log RT, surprisal | identical |
   15 | | RT filter | 100–3000 ms | identical |
   16 | | **ΔAIC** | **2.5** | **111.8** |
   17 | | **β(TEE)** | **+0.00063** | **+0.00354** |
   18 | 
   19 | Same rows, same specification. The only thing that differs is the TEE values
   20 | themselves. The paper's came from `naturalstories_extrap.py` (pre-rebuild,
   21 | chunked GPT-2 passes); the locked sample came from the REBUILD_V2 pipeline that
   22 | was written *because* the earlier pipeline had alignment bugs — the same rebuild
   23 | that overturned the k=15 optimality claim in `AUDIT_FOR_FABLE.md`.
   24 | 
   25 | The locked sample is the reproducible one: it is hash-fingerprinted, and its TEE
   26 | has been independently recomputed twice (matching to 1.4e-14 in-repo, and to
   27 | r = 0.9999999999991 on a different machine in the extensions run). The paper's
   28 | `naturalstories_extrap_metrics.csv` is not in the repo and cannot currently be
   29 | reproduced at all.
   30 | 
   31 | **Conclusion: the published 2.5 is a superseded number.** Use the locked sample.
   32 | This should be stated explicitly somewhere in the record, because the direction
   33 | of the correction is favourable to the author and that is exactly when it needs
   34 | the clearest paper trail.
   35 | 
   36 | ## The two robustness checks the paper is missing — both pass
   37 | 
   38 | | model | n | ΔAIC | β(TEE) | p |
   39 | |---|---|---|---|---|
   40 | | headline | 812,730 | 111.8 | +0.00354 | 1.4e-26 |
   41 | | + punctuation covariate | 812,730 | 115.4 | +0.00359 | 2.4e-27 |
   42 | | punctuation-free words only | 716,641 | **138.3** | +0.00411 | 2.3e-32 |
   43 | | **word-identity demeaned** | 812,730 | **23.1** | +0.00218 | 5.3e-7 |
   44 | | punct-free + word-identity demeaned | 716,641 | 23.7 | +0.00220 | 4.1e-7 |
   45 | 
   46 | **Punctuation:** no threat. 11.8% of observations are punctuation-final; adding a
   47 | covariate slightly *strengthens* the effect, and restricting to punctuation-free
   48 | words strengthens it further (ΔAIC 138.3). This is the confound that produced
   49 | spurious effects in four separate analyses elsewhere in the project — it does not
   50 | do so here.
   51 | 
   52 | **Lexical baseline:** this is the check `ns_crossed_re.py` attempted with a
   53 | `(1|word_type)` random effect and never completed. Implemented instead by
   54 | centering the outcome and all predictors within word identity (2,919 word types
   55 | occurring 5+ times), which asks whether TEE predicts reading time **for the same
   56 | word in different contexts**. It does: ΔAIC 23.1, p = 5.3e-7. The effect
   57 | attenuates by ~40%, which is expected and honest — a good part of the raw effect
   58 | is lexical — but it does not vanish. This is the single most important result
   59 | for the paper's claim, because it rules out the objection that TEE is a proxy
   60 | for word identity or frequency.
   61 | 
   62 | ## Where this leaves the paper
   63 | 
   64 | The Natural Stories result is stronger than published, survives the punctuation
   65 | confound, and survives word identity. Combined with the tee_vs_curvature
   66 | dissociation and the extensions (neighborhood TEE causal wake, manifold split),
   67 | there is a publishable paper here that does not depend on garden paths at all.
   68 | 
   69 | Remaining: the tee_vs_curvature and extensions pipelines have not been audited to
   70 | this standard. They are the other half of any reframed submission and should get
   71 | the same treatment before anything is written.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_onestop.md
==============================================================================

```
    1 | # OneStop: TEE does not replicate, and reverses (2026-07-27)
    2 | 
    3 | OneStop Ordinary Reading, 360-participant corpus (180 participants in this
    4 | sub-corpus), 1,104,883 word-level observations, 128 paragraphs, 15,650 words
    5 | with usable TEE. Subject-level inference throughout: one regression per
    6 | participant, group test across participants — the standard that Natural Stories
    7 | passed and ZuCo failed.
    8 | 
    9 | Scripts: `onestop_compute_tee.py`, `onestop_analyze.py`; output
   10 | `onestop_results.txt`, `onestop_prevctrl.txt`.
   11 | 
   12 | ## Pipeline validation (done before interpreting anything)
   13 | 
   14 | - IA_LABEL ↔ reconstructed word match rate: **100%**
   15 | - reconstructed text reads correctly, punctuation attached as in the corpus
   16 | - my GPT-2 surprisal vs OneStop's precomputed `gpt2_surprisal`: **r = 0.80**
   17 |   (not 1.0 — they likely use a different context window or variant; close
   18 |   enough to confirm alignment, not close enough to ignore)
   19 | - TEE computed with the sink excluded from every fit window (windows start at
   20 |   word index 1; only words at index ≥ 4 emitted)
   21 | 
   22 | The alignment is sound. What follows is a property of the data, not a merge bug.
   23 | 
   24 | ## Result: significant effects in the OPPOSITE direction
   25 | 
   26 | | DV | positive betas | mean β | Wilcoxon |
   27 | |---|---|---|---|
   28 | | first fixation duration | 76/180 (42%) | −0.00199 | .005 |
   29 | | gaze duration | 70/180 (39%) | −0.00421 | 4.1e-6 |
   30 | | total reading time | 54/180 (30%) | **−0.00601** | 1.5e-8 |
   31 | 
   32 | Higher TEE predicts **shorter** fixations. Natural Stories gives +0.0039 with
   33 | 73% of participants positive; OneStop gives −0.0060 with 30% positive on the
   34 | comparable measure. This is not a null — it is a reversal, at n = 180, under the
   35 | inferential standard we adopted precisely because it is strict.
   36 | 
   37 | ### It is not the missing eye-tracking controls
   38 | 
   39 | The first-pass spec lacked the previous-word terms that dominate the Natural
   40 | Stories model. Adding them progressively:
   41 | 
   42 | | spec | FFD | GD | TRT |
   43 | |---|---|---|---|
   44 | | A first-pass | −0.00199 (.005) | −0.00421 (4e-6) | −0.00601 (1e-8) |
   45 | | B + prev length/freq/surprisal | −0.00069 (.25) | −0.00292 (.002) | −0.00584 (1e-7) |
   46 | | C + prev dwell time | −0.00057 (.33) | −0.00272 (.003) | −0.00620 (2e-8) |
   47 | | D + prev TEE | −0.00015 (.67) | −0.00248 (.011) | −0.00646 (4e-8) |
   48 | 
   49 | First-fixation duration goes null once preview controls are added — fine, FFD is
   50 | the earliest and noisiest measure. But gaze duration and total reading time keep
   51 | the negative effect at every level of control, and TRT gets slightly *stronger*.
   52 | 
   53 | ### The position gradient replicates — with the sign inverted
   54 | 
   55 | | slice | Natural Stories | OneStop (TRT) |
   56 | |---|---|---|
   57 | | first 5 words of sentence | −0.0022 (null) | −0.0016 (null) |
   58 | | beyond word 10 | **+0.0056** (3.9e-15) | **−0.0074** (6.5e-8) |
   59 | 
   60 | Both corpora show the same profile — nothing at sentence onset, growing with
   61 | depth into the sentence — but Natural Stories grows positive and OneStop grows
   62 | negative. Whatever TEE indexes, it is being read out with opposite sign by the
   63 | two paradigms, and the *shape* of the position dependence is the same in both.
   64 | That is a strange and interesting pattern; it is also a serious problem.
   65 | 
   66 | ## What this does to the story
   67 | 
   68 | The ZuCo null is no longer the thing to explain. ZuCo's trends were negative
   69 | too (its betas were positive in raw ms but the analysis was underpowered);
   70 | OneStop now shows a well-powered, controlled, significant reversal.
   71 | 
   72 | The honest reading is one of:
   73 | 
   74 | 1. **Paradigm difference, real.** Self-paced reading meters a button press per
   75 |    word and is sensitive to integration cost; eye movements permit skipping,
   76 |    regression and preview. A word that is off-trajectory may attract a shorter
   77 |    first-pass fixation and a regression later — the total-time measure here
   78 |    includes regressions, which complicates that story rather than saving it.
   79 | 2. **The self-paced effect is task-specific.** TEE may index something about
   80 |    button-press rhythm or motor pacing in SPR that has no counterpart in free
   81 |    reading. That would substantially deflate the claim that TEE indexes human
   82 |    processing cost.
   83 | 3. **Something about my OneStop TEE differs from the Natural Stories TEE.**
   84 |    Paragraph-level context vs story-level, different text genre (Guardian vs
   85 |    narrative), different length. The r = 0.80 surprisal agreement is a hint that
   86 |    my forward pass is not identical to theirs and deserves a look.
   87 | 
   88 | I cannot currently distinguish these, and I do not want to guess after two wrong
   89 | calls in this session.
   90 | 
   91 | ## Recommendation
   92 | 
   93 | **Do not submit a reading-time-led paper until this is resolved.** A referee
   94 | with OneStop — a public, popular, 360-participant corpus — can run this in an
   95 | afternoon, and a significant reversal found by a referee is far worse than one
   96 | disclosed by the author.
   97 | 
   98 | Concrete next steps, in order:
   99 | 1. Reconcile the surprisal discrepancy (r = 0.80): match OneStop's exact
  100 |    surprisal procedure and confirm the TEE forward pass matches it.
  101 | 2. Check whether the reversal holds for *skipping rate* and *regression
  102 |    probability*, which are the eye-tracking measures with no self-paced analogue.
  103 | 3. Run the Natural Stories words through an eye-tracking corpus if one exists
  104 |    for the same texts, isolating paradigm from stimulus.
  105 | 
  106 | Framing B (model-internal geometry: structure vs uncertainty, causal wake) is
  107 | untouched by any of this. Its evidence is model-internal and does not depend on
  108 | which behavioral corpus reads out with which sign.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_onestop_followup.md
==============================================================================

```
    1 | # OneStop follow-up: the reversal shrinks a lot under a fair spec (2026-07-27)
    2 | 
    3 | Chasing the r = 0.80 surprisal discrepancy and the missing-context hypothesis.
    4 | Scripts: `onestop_context_tee.py`, output `onestop_ctx_log.txt`,
    5 | `onestop_final.txt`.
    6 | 
    7 | ## Context is not the explanation
    8 | 
    9 | Natural Stories TEE used whole-story forward passes (1024-token chunks, stride
   10 | 512); my first OneStop pass used isolated paragraphs. Recomputing OneStop with
   11 | article-level context (paragraphs of an article concatenated in order):
   12 | 
   13 | - **r(TEE isolated, TEE article-context) = 0.988** — context barely moves TEE
   14 | - r(OneStop surprisal, mine): 0.802 isolated → 0.812 with context
   15 | - no position-in-paragraph signature of a context mismatch
   16 | 
   17 | So the two pipelines do not differ meaningfully in context, and the surprisal
   18 | discrepancy is not a context effect. It remains unexplained — most likely a
   19 | different GPT-2 variant or a different word-level aggregation on their side.
   20 | It is worth one email to the authors, but it is not what is driving anything.
   21 | 
   22 | ## Under a fair specification, the reversal largely dissolves
   23 | 
   24 | Progressive replacement of my pipeline choices with theirs, all with previous-word
   25 | controls (length, frequency, surprisal, dwell time):
   26 | 
   27 | | DV | my surprisal + isolated TEE | their surprisal + isolated TEE | their surprisal + context TEE |
   28 | |---|---|---|---|
   29 | | FFD | −0.00029 (.70) | +0.00030 (.58) | **+0.00061 (.27)** |
   30 | | GD | −0.00230 (.016) | −0.00108 (.35) | **−0.00058 (.71)** |
   31 | | TRT | −0.00522 (1.1e-6) | −0.00295 (.004) | **−0.00225 (.029)** |
   32 | 
   33 | Two of three measures go null once their surprisal and context-based TEE are
   34 | used. First-fixation duration even turns (non-significantly) positive.
   35 | 
   36 | **What survives:** total reading time, β = −0.0023, p = .029. Attenuated by more
   37 | than half from the first-pass estimate, and now at a p-value that would not
   38 | survive correction for three dependent measures × several specifications.
   39 | 
   40 | ## Revised reading
   41 | 
   42 | My earlier framing — "a significant reversal at n = 180" — was too strong. What
   43 | the data support is:
   44 | 
   45 | 1. **TEE does not predict eye movements in OneStop.** Two of three measures are
   46 |    null under the fair spec. This is a failure to replicate, not a reversal.
   47 | 2. **There is a residual negative trend in total reading time**, which is the
   48 |    measure that includes regressions and re-reading. That is worth a sentence
   49 |    and worth understanding, not worth a headline in either direction.
   50 | 3. **The self-paced result stands on its own** but now clearly does not
   51 |    generalise to eye movements. Two eye-tracking corpora (ZuCo, OneStop) fail to
   52 |    show the effect; ZuCo underpowered, OneStop well-powered and null-to-slightly-
   53 |    negative.
   54 | 
   55 | I overstated the first-pass result. The specification I ran initially lacked
   56 | previous-word controls and used my own surprisal; both mattered. The corrected
   57 | picture is less dramatic and more ordinary: an effect that appears in self-paced
   58 | reading and does not appear in eye tracking.
   59 | 
   60 | ## What this means for the paper
   61 | 
   62 | The claim "TEE indexes human processing cost" cannot be supported in general
   63 | form. What can be supported: TEE predicts self-paced reading time, robustly and
   64 | at the subject level, and does not predict eye-movement measures in two
   65 | independent corpora. That is a real and reportable pattern — self-paced reading
   66 | meters processing serially and is known to be more sensitive to integration
   67 | difficulty than first-pass fixation measures — but it is a narrower claim than
   68 | the arXiv paper makes, and it must be stated with the eye-tracking nulls in
   69 | plain view.
   70 | 
   71 | Framing B (model-internal geometry) remains unaffected and is now clearly the
   72 | stronger paper.
   73 | 
   74 | ## Outstanding
   75 | 
   76 | - The r = 0.80 surprisal disagreement with OneStop's published values is still
   77 |   unexplained. Not load-bearing, but it should be resolved before citing their
   78 |   annotations.
   79 | - Skipping rate and regression probability were not analysed; they are the
   80 |   eye-tracking measures with no self-paced analogue and would sharpen the
   81 |   paradigm story.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_regression_confound.md
==============================================================================

```
    1 | # Is the TEE-regression effect oculomotor? (2026-07-27)
    2 | 
    3 | The concern: regressions are strongly driven by where a word sits on screen, and
    4 | OneStop displays multi-line paragraphs. If TEE correlates with line position,
    5 | the effect could be an artifact of eye-movement mechanics rather than language.
    6 | Output: `onestop_oculo.txt`, `onestop_oculo2.txt`.
    7 | 
    8 | ## Screen position matters enormously — and TEE is orthogonal to it
    9 | 
   10 | P(regression out) by line position:
   11 | 
   12 | | position | P(regress) |
   13 | |---|---|
   14 | | line-initial | 0.056 |
   15 | | line-medial | 0.182 |
   16 | | **line-final** | **0.264** |
   17 | 
   18 | A near-5× swing. So the confound was worth taking seriously. But TEE barely
   19 | correlates with any spatial variable:
   20 | 
   21 | | variable | r with TEE |
   22 | |---|---|
   23 | | x-position within line | −0.001 |
   24 | | is line-final | +0.009 |
   25 | | is line-initial | +0.001 |
   26 | | line number | −0.010 |
   27 | | (word length, for scale) | +0.120 |
   28 | 
   29 | The two are cleanly separable: screen position drives regressions hard, TEE
   30 | doesn't track screen position at all.
   31 | 
   32 | ## The effect survives the controls
   33 | 
   34 | | model | β | sign test | Wilcoxon |
   35 | |---|---|---|---|
   36 | | linguistic controls only | +0.0165 | .002 | 3.4e-5 |
   37 | | + line number, x-in-line | +0.0153 | .002 | 1.0e-4 |
   38 | | + launch site, landing position | +0.0162 | .006 | 6.6e-5 |
   39 | 
   40 | Essentially unchanged, and it clears both the sign test and the Wilcoxon.
   41 | 
   42 | ## But it weakens on line-medial words
   43 | 
   44 | Dropping line-initial and line-final words entirely (957,902 of 1,104,883 rows
   45 | retained):
   46 | 
   47 | | model | β | sign test | Wilcoxon |
   48 | |---|---|---|---|
   49 | | line-medial only, linguistic controls | **+0.0080** | .21 | .031 |
   50 | | line-medial only, + spatial controls | +0.0079 | .33 | .038 |
   51 | 
   52 | The coefficient halves (+0.0165 → +0.0080) and the sign test goes null, though
   53 | Wilcoxon stays marginal. So roughly half the effect lives at line boundaries —
   54 | which the covariate-adjusted models were apparently not fully absorbing.
   55 | 
   56 | That is not the same as the effect being an artifact: TEE is uncorrelated with
   57 | line-final status (r = 0.009), so it is hard to see how line position alone
   58 | manufactures a TEE coefficient. But the honest reading is that the effect is
   59 | **smaller and less certain than the headline number**, and part of it is
   60 | carried by words in positions where regressions are most frequent and most
   61 | mechanically determined.
   62 | 
   63 | ## Verdict
   64 | 
   65 | Is it real? **Probably, but half the size I first reported, and I would not build
   66 | a paper on it yet.**
   67 | 
   68 | What it survives: fair specification, surprisal controls, previous-word
   69 | controls, punctuation-free subsetting, position-in-text, Bonferroni across the
   70 | eight eye-movement measures tested, oculomotor covariates, and a weak
   71 | same-direction replication in ZuCo (8/12).
   72 | 
   73 | What still concerns me: line-medial β is half the full-sample β with a null sign
   74 | test; the ZuCo replication does not clear its preregistered bar; there is no
   75 | time-cost mechanism (conditional go-past is null); and 62% of participants
   76 | positive is a modest majority.
   77 | 
   78 | The genuinely interesting part remains that surprisal predicts regressions not
   79 | at all (p = .22) while TEE does. If that dissociation holds up in a
   80 | preregistered test on new data, it is worth a paper on its own. Right now it is
   81 | one well-powered corpus, one weak partial replication, and a coefficient that
   82 | halves under the most conservative subsetting.
   83 | 
   84 | ## What would settle it
   85 | 
   86 | A preregistered test on a fresh eye-tracking corpus with single-line or
   87 | sentence-at-a-time presentation, which removes line-boundary mechanics from the
   88 | picture entirely. Provo (84 participants, short passages) or GECO (14
   89 | participants, whole novel) would both work. CELER presents isolated sentences
   90 | and would be the cleanest for this specific question despite its other
   91 | limitations.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_roi_signflip.md
==============================================================================

```
    1 | # The sign flip: it is position heterogeneity, not the disambiguating word (2026-07-27)
    2 | 
    3 | Original spec throughout (mixedlm, by-participant random intercept, ML; controls
    4 | = word length, word position, previous log RT, surprisal; TEE = L6 w=3, isolated
    5 | presentation). `prev_log_RT` taken from the full sentence so ROI 0 survives.
    6 | Script `gp_roi_signflip.py`, output `roi_signflip_output.txt`.
    7 | 
    8 | ## Per-position coefficients
    9 | 
   10 | | ROI | n | β TEE | p | β surprisal | p |
   11 | |---|---|---|---|---|---|
   12 | | −2 | 47,642 | −0.0051 | .012 | +0.0029 | .036 |
   13 | | −1 | 47,645 | −0.0054 | 2.3e-4 | −0.0004 | .77 |
   14 | | **0 (disambiguating word)** | 47,610 | **−0.0034** | **.084 (n.s.)** | +0.0341 | 1.8e-65 |
   15 | | **1 (spillover 1)** | 47,614 | **−0.0085** | **6.6e-5** | +0.0405 | 1.8e-79 |
   16 | | **2 (spillover 2)** | 47,647 | **+0.0102** | **5.5e-10** | −0.0022 | .19 |
   17 | | 3 (outside region) | 47,669 | +0.0207 | 2.4e-44 | +0.0125 | 2.3e-19 |
   18 | 
   19 | TEE × ROI interaction across the critical region: **χ²(2) = 36.8, p = 1.0e-8**.
   20 | The effect is not homogeneous across ROI 0/1/2 — it reverses between spillover 1
   21 | and spillover 2.
   22 | 
   23 | ## What this means
   24 | 
   25 | 1. **At the disambiguating word, TEE contributes nothing** once surprisal is in
   26 |    the model (p = .084, and negative in direction). Surprisal is doing all the
   27 |    work there (β = +0.034, p = 1.8e-65). The paper's framing — that TEE captures
   28 |    processing cost at the point of reanalysis — is not supported at the point of
   29 |    reanalysis.
   30 | 2. **The published positive effect comes from ROI 2 alone.** At ROI 1 the
   31 |    coefficient is *negative* and significant (−0.0085); at ROI 2 it is positive
   32 |    (+0.0102). Pooling ROI 1+2 without a ROI term yields +0.0079, which is larger
   33 |    than either constituent estimate — the pooled number is partly between-position
   34 |    variance, not a within-position relationship. Adding ROI as a factor to the
   35 |    same rows drops it to +0.0064; splitting it shows the two halves disagree.
   36 | 3. **My earlier "restoring ROI 0 flips the sign" was the wrong diagnosis.**
   37 |    Pooling ROI 0+1+2 goes negative because two of three positions are negative.
   38 |    The real problem is that the three positions do not share a sign, so *any*
   39 |    pooled estimate over this region is an artifact of which positions are in it.
   40 | 4. **Pre-critical positions also show negative TEE effects** (ROI −2, −1), before
   41 |    any disambiguation has occurred. Whatever TEE is tracking here, it is not
   42 |    specific to reanalysis.
   43 | 5. **The largest effect is outside the critical region** (ROI 3, +0.0207,
   44 |    p = 2.4e-44), which the paper never examined.
   45 | 
   46 | ## Not explained by
   47 | 
   48 | - **Frequency:** adding log frequency barely moves any coefficient (ROI 1:
   49 |   −0.0085 → −0.0071; ROI 2: +0.0102 → +0.0060). The flip survives.
   50 | - **Punctuation:** 0% of words at any of these positions are punctuation-final.
   51 | - **The attention sink:** w=3 windows never reach word 0 at these positions.
   52 | - **Construction:** at ROI 0 no construction is individually significant
   53 |   (MVRR −0.0009, NPS −0.0057, NPZ +0.0080); the pattern is not one item type.
   54 | 
   55 | ## What TEE is correlated with, position by position
   56 | 
   57 | | ROI | r(TEE, word length) | r(TEE, log freq) | r(TEE, surprisal) |
   58 | |---|---|---|---|
   59 | | −1 | −0.26 | −0.44 | +0.12 |
   60 | | 0 | −0.17 | −0.21 | **+0.42** |
   61 | | 1 | −0.29 | +0.13 | +0.26 |
   62 | | 2 | +0.12 | −0.25 | −0.06 |
   63 | | 3 | +0.38 | −0.37 | +0.34 |
   64 | 
   65 | TEE's relationship to lexical properties and to surprisal is itself unstable
   66 | across adjacent positions — which is the likely source of the coefficient
   67 | instability. Note r(TEE, surprisal) = +0.42 at ROI 0, far above the r = .044
   68 | orthogonality reported for Natural Stories; in this stimulus set at this
   69 | position the two measures are substantially entangled.
   70 | 
   71 | ## Recommendation
   72 | 
   73 | This is more serious than the sink issue, and it is not fixable by a control.
   74 | The garden-path reading-time claim as stated does not hold: TEE does not predict
   75 | processing cost at the disambiguating word, and its apparent effect over the
   76 | spillover region depends on pooling two positions whose coefficients have
   77 | opposite signs.
   78 | 
   79 | Options, in order of preference:
   80 | 
   81 | 1. **Report the position-resolved analysis honestly.** State that the effect is
   82 |    carried by later spillover (ROI 2–3) and is absent or reversed at
   83 |    disambiguation. This is a weaker but defensible claim, and the ROI 3 result
   84 |    suggests the region should have extended further.
   85 | 2. **Drop the garden-path reading-time analysis** and keep garden paths as a
   86 |    measure-validation demonstration only (ambiguous vs unambiguous TEE, which
   87 |    does hold for NPS and NPZ though not MVRR).
   88 | 3. Do not submit the current version — the pooled positive coefficient is not a
   89 |    stable description of the data.
   90 | 
   91 | The Natural Stories reading-time result is untouched by any of this.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_subject_level.md
==============================================================================

```
    1 | # Subject-level inference: does the Natural Stories effect survive the ZuCo standard? (2026-07-27)
    2 | 
    3 | The ZuCo eye-tracking analysis returned a null using subject-level inference —
    4 | one beta per subject, group test across subjects, explicitly to avoid
    5 | pseudoreplication. The Natural Stories result pools 813,621 observations with a
    6 | by-participant random intercept. Applying the stricter standard to Natural
    7 | Stories decides whether ΔAIC = 112 is a real effect or a large-N artifact.
    8 | 
    9 | Script `ns_subject_level.py`; per-participant coefficients in
   10 | `subject_betas_*.csv`.
   11 | 
   12 | ## Result: it survives, comfortably
   13 | 
   14 | One OLS per participant (171 of 178 with enough data), then a group test on the
   15 | distribution of TEE coefficients.
   16 | 
   17 | | specification | positive betas | mean β | Wilcoxon p | t-test | individually sig |
   18 | |---|---|---|---|---|---|
   19 | | FULL controls (length, freq, position, prevRT, surprisal) | **125/171 (73.1%)** | +0.00388 | 5.1e-12 | t(170) = 7.46, p = 4.2e-12 | 39/171 |
   20 | | ZuCo-style controls (length, freq only) | **136/171 (79.5%)** | +0.00577 | 3.3e-16 | t(170) = 9.29, p = 7.4e-17 | 44/171 |
   21 | | punctuation-free, FULL controls | **128/171 (74.9%)** | +0.00442 | 3.5e-13 | t(170) = 7.83, p = 5.0e-13 | 43/171 |
   22 | 
   23 | Three-quarters of participants show a positive effect independently, sign test
   24 | p = 1.2e-9. The per-participant mean β (+0.0039) closely matches the pooled
   25 | estimate (+0.0035), which is what a genuine effect looks like and what a
   26 | large-N artifact does not.
   27 | 
   28 | **The pooled Natural Stories result is not pseudoreplication.** It holds under
   29 | the same inferential standard that produced the ZuCo null.
   30 | 
   31 | ## So why is ZuCo null?
   32 | 
   33 | Not because the analysis standard differs — Natural Stories passes that standard.
   34 | Candidate explanations, in the order I would argue them:
   35 | 
   36 | 1. **Power.** ZuCo has 10 subjects; Natural Stories has 171. Only 23% of
   37 |    individual Natural Stories participants reach p < .05 on their own, so with
   38 |    n = 10 a group test would frequently miss. Note ZuCo's FFD (p = .084) and TRT
   39 |    (p = .065) both trend positive — consistent with a real but small effect the
   40 |    study is underpowered to resolve.
   41 | 2. **Paradigm.** Self-paced reading forces a button press per word and is
   42 |    sensitive to integration difficulty; free eye movement allows skipping,
   43 |    regressions, and parafoveal preview. A trajectory-integration cost has an
   44 |    obvious route into button-press latency and a much less direct route into
   45 |    first-fixation duration.
   46 | 3. **Stimuli.** ZuCo sentences are isolated, short, and drawn from movie reviews
   47 |    and Wikipedia; Natural Stories are long connected narratives. A 3-word
   48 |    backward window behaves differently in each — and per the position analysis,
   49 |    the TEE effect is weakest at sentence-initial positions and strongest deep
   50 |    into a sentence. ZuCo is disproportionately made of the positions where the
   51 |    effect is weak.
   52 | 
   53 | Point 3 is testable on the existing data: restrict Natural Stories to
   54 | sentence-initial and early positions and see whether the effect drops toward the
   55 | ZuCo null. If it does, that is a genuine, publishable reconciliation rather than
   56 | a hand-wave.
   57 | 
   58 | ## Recommendation
   59 | 
   60 | Report ZuCo. A null in a second paradigm, disclosed and explained, is far
   61 | stronger than a paper that quietly uses only the corpus that worked — and the
   62 | position-profile explanation is empirically checkable rather than rhetorical.
   63 | 
   64 | This also removes the main obstacle to Framing A: the reading-time claim now
   65 | rests on 171 independently-estimated participant effects, not on a single pooled
   66 | model with a large denominator.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_table1_exact.md
==============================================================================

```
    1 | # Table 1 under the original spec, with sink controls (2026-07-27)
    2 | 
    3 | Now run against the real pipeline (`garden-path-p1/model_comparison_stats.py`
    4 | and `window_sweep.py`), not a reconstruction: mixedlm with a by-participant
    5 | random intercept, ML fit, controls = word length + word position + previous log
    6 | RT, TEE = word-level states at the last subword, linear fit over the k preceding
    7 | word states, one-step extrapolation, Euclidean error. Script
    8 | `gp_table1_exact.py`, output `table1_exact_output.txt`.
    9 | 
   10 | **Sample reproduces exactly: N = 95,173.** Betas are positive, matching the
   11 | published +0.005 direction. (My earlier reconstruction's negative sign came from
   12 | including ROI 0 and a frequency control — see below.)
   13 | 
   14 | ## Finding 1: the published RT models exclude the disambiguating word
   15 | 
   16 | `model_comparison_stats.py` filters to ROI 0/1/2 and *then* computes
   17 | `prev_log_RT` by shifting within (participant, Sentence). ROI 0 is the first row
   18 | of every group, so it gets NaN and is dropped at the `dropna`. The published
   19 | N = 95,173 is exactly ROI 1 (47,532) + ROI 2 (47,641) — the total ROI 0/1/2 pool
   20 | is 142,886.
   21 | 
   22 | The Methods say the critical region "included the disambiguating word and two
   23 | spillover positions (ROI codes 0, 1, and 2)". For the RT models that is not what
   24 | was fit. **The garden-path reading-time effect is a spillover effect**, measured
   25 | one and two words after disambiguation, with the disambiguating word absent.
   26 | 
   27 | This is fixable two ways — restate the region as spillover-only, or take
   28 | prev_log_RT from the full sentence so ROI 0 survives — but it cannot stay as is.
   29 | 
   30 | ## Finding 2: restoring ROI 0 flips the sign
   31 | 
   32 | | | ROI 1+2 (published) | ROI 0+1+2 (restored) |
   33 | |---|---|---|
   34 | | L6 w=3 β | **+0.0080** (p = 1.4e-9) | **−0.0081** (p = 1.9e-14) |
   35 | 
   36 | At spillover positions, higher TEE predicts *longer* reading time. At the
   37 | disambiguating word itself, higher TEE predicts *shorter* reading time, about as
   38 | strongly. The published positive effect exists only because the negative-signed
   39 | positions were dropped. This needs an explanation before the paper goes out —
   40 | it is not a sink artifact (0% window exposure at w=3 either way) and it is not
   41 | small.
   42 | 
   43 | ## Finding 3: the sink barely matters for the published table
   44 | 
   45 | Because ROI 0 is excluded, the critical rows sit further from the sentence start
   46 | than I assumed, and sink exposure largely disappears.
   47 | 
   48 | | config | window touches word 0 | isolated (published) | prefix | drop-tok0 |
   49 | |---|---|---|---|---|
   50 | | L6 w=3 | 0.0% | +34.7 | +56.8 | +34.7 (identical) |
   51 | | L12 w=5 | 0.0% | +11.3 | +42.9 | +11.3 (identical) |
   52 | | L6 w=5 | 0.0% | −0.7 (n.s.) | −1.9 (n.s.) | −0.7 (n.s.) |
   53 | | L6 w=7 | 35.5% | +26.4 | +39.6 | **+18.9, p = 5e-6** |
   54 | 
   55 | Every significant configuration stays significant under clean handling, and two
   56 | get stronger with context prepended. **My earlier conclusion that M5 (w=7) should
   57 | be dropped was wrong** — that was based on a sample including ROI 0, where w=7 is
   58 | 44% exposed and does collapse. On the published sample it survives at +18.9.
   59 | 
   60 | So: no withdrawal, no dropped rows on sink grounds. Report the control, state
   61 | the presentation format, and note that w=7 attenuates ~30% when the first token
   62 | is excluded.
   63 | 
   64 | ## Discrepancies worth resolving
   65 | 
   66 | - ΔAIC values partially reproduce: L6/w5 (−0.7 vs published 0.0) and L6/w7
   67 |   (+26.4 vs +31.4) are close; L6/w3 (+34.7 vs +10.7) and L12/w5 (+11.3 vs +56.4)
   68 |   are not. Most likely cause: the committed script's controls do **not** include
   69 |   log word frequency, while the paper text says the control model "included log
   70 |   word frequency" and Table 1 labels M0 "Controls (incl. log freq)". There is
   71 |   probably a later version of the script that was actually used for the table.
   72 |   Worth locating — it changes two of four published ΔAICs.
   73 | - `zou_stimuli.csv` and the Matters Arising drafts are in the same repo; the
   74 |   withdrawal there was the right call and is unaffected by any of this.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_table1_rerun.md
==============================================================================

```
    1 | # Table 1 rerun with sink-clean TEE (2026-07-27)
    2 | 
    3 | SAP ClassicGP self-paced reading, N = 2,000 participants, 24 items × 6 types,
    4 | critical region ROI 0/1/2. Controls: word length, word position, previous log
    5 | RT, log word frequency (all z-scored); outcome log RT; surprisal computed under
    6 | the matching presentation. Each configuration uses its own sample — the rows
    7 | where that measure is defined under all three presentations — because a global
    8 | intersection deletes the sentence-initial rows, which is exactly where the sink
    9 | bites. Script `gp_table1_rerun.py`, raw output `table1_rerun_output.txt`.
   10 | 
   11 | Presentations: **A** isolated sentence (presumed original), **B** neutral prefix
   12 | prepended, **C** isolated with word 0 excluded from fit windows.
   13 | 
   14 | ## Reconstruction fidelity
   15 | 
   16 | Participant-demeaned M1 (surprisal over frequency controls) gives ΔAIC = **−2.0,
   17 | p = .84** against the paper's **−1.9, p = .71** — the baseline reproduces almost
   18 | exactly, and only under participant-level structure with isolated presentation.
   19 | That is good evidence the pipeline and the presentation assumption are right.
   20 | The individual TEE configurations do **not** reproduce numerically (see below),
   21 | and the L6/k=3 coefficient comes out negative here vs +0.005 in the paper, so
   22 | treat absolute values as a reconstruction, not a replication. The
   23 | presentation-to-presentation *contrasts* — same rows, same controls, only the
   24 | sink handling changes — are the trustworthy part.
   25 | 
   26 | ## Sink exposure per configuration
   27 | 
   28 | | config | rows whose window touches word 0 | r(isolated, droptok0) | r(isolated, prefix) | mean TEE isolated → clean |
   29 | |---|---|---|---|---|
   30 | | L6 k=3 | **0.0%** | 1.000 | 0.984 | 94.9 → 94.9 |
   31 | | L12 k=5 | 7.2% | 0.883 | 0.712 | 50.2 → 48.4 |
   32 | | L6 k=5 | 7.2% | 0.265 | **−0.067** | 153.0 → 74.5 |
   33 | | L6 k=7 | **43.8%** | 0.192 | **−0.030** | 409.4 → 69.4 |
   34 | 
   35 | At w=5 and w=7 the isolated measure is essentially *uncorrelated* with its own
   36 | clean counterpart. It is not a noisy version of the intended quantity; it is a
   37 | different quantity, dominated by distance to a 36×-norm outlier.
   38 | 
   39 | ## ΔAIC for the TEE term (over controls + surprisal)
   40 | 
   41 | Participant-demeaned models; OLS in the raw output tells the same story.
   42 | 
   43 | | config | A isolated | B prefix | C droptok0 | verdict |
   44 | |---|---|---|---|---|
   45 | | L6 k=3 | +102.5 | +109.2 | +102.5 | **unaffected — sink-immune by construction** |
   46 | | L12 k=5 | −0.1 (n.s.) | +67.9 | +35.1 | **survives; stronger when cleaned** |
   47 | | L6 k=5 | +90.2 | −0.4 (n.s.) | +17.2 | **mostly artifact** |
   48 | | L6 k=7 | −1.0 (n.s.) | −0.6 (n.s.) | −1.7 (n.s.) | **nothing there under any handling** |
   49 | 
   50 | ## What this means for the manuscript
   51 | 
   52 | 1. **The headline configuration is safe.** L6/k=3 windows never reach word 0 —
   53 |    0.0% exposure, r = 1.000 with the drop-token-0 version. Its RT contribution
   54 |    is large and unchanged under every presentation. Model M2 needs no revision
   55 |    on sink grounds.
   56 | 2. **M5 (L6, w=7, paper ΔAIC = +31.4) should be dropped.** 44% of its rows are
   57 |    sink-exposed, its measure is uncorrelated with the clean version (r = −0.03,
   58 |    mean 409 vs 69), and it is null under every clean handling.
   59 | 3. **M4 (L6, w=5) is not a usable robustness check.** The paper reported it as
   60 |    null (ΔAIC 0.0), which happens to be the right conclusion, but for the wrong
   61 |    reason — in this reconstruction the isolated version looks strong (+90) and
   62 |    collapses to null once cleaned. Either way it should not be cited as
   63 |    independent support.
   64 | 4. **M3 (L12, w=5, paper ΔAIC = +56.4) survives and improves.** Cleaning makes
   65 |    it stronger (+67.9 with prefix), so the strongest RT result is not a sink
   66 |    artifact. It is, however, the configuration with the largest gap between
   67 |    presentations, so report which one was used.
   68 | 5. **Methods must state the presentation format.** The paper never says whether
   69 |    garden-path stimuli were run in isolation. Given that w=5/w=7 results depend
   70 |    entirely on that choice, it cannot stay implicit.
   71 | 
   72 | ## Caveats
   73 | 
   74 | - Reconstruction, not the original pipeline: the surprisal baseline matches the
   75 |   paper closely but the TEE coefficients do not, including a sign difference at
   76 |   L6/k=3. Rerunning with the original garden-path code (not yet located) is the
   77 |   right next step before editing the manuscript.
   78 | - Sample is 142,681 (k=3/k=5) or 102,290 (k=7) ROI 0–2 observations vs the
   79 |   paper's 95,173; the paper applied additional exclusions not documented in the
   80 |   text.
   81 | - Participant-demeaning approximates a by-participant random intercept; it does
   82 |   not include by-item random effects, which the paper notes absorb much of the
   83 |   TEE variance at the disambiguation point.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_zuco_reconcile.md
==============================================================================

```
    1 | # Reconciling the ZuCo null with the Natural Stories effect (2026-07-27)
    2 | 
    3 | Subject-level inference throughout (one beta per participant, group Wilcoxon),
    4 | matching the ZuCo standard. Script `ns_zuco_reconcile.py`.
    5 | 
    6 | ## Headline: it is power, quantitatively
    7 | 
    8 | Resampling 10 participants at a time from the 171 Natural Stories readers and
    9 | running the same group test ZuCo ran:
   10 | 
   11 | | sample | detection rate at n = 10 |
   12 | |---|---|
   13 | | full corpus | **41.8%** |
   14 | | ZuCo-like slice | 22.4% |
   15 | 
   16 | A 10-subject study would miss this effect **more than half the time**. ZuCo's
   17 | observed values — FFD p = .084, TRT p = .065, both trending positive, 0/10
   18 | individually significant — are precisely what an underpowered true effect looks
   19 | like. This is a quantitative answer to "why didn't it replicate," not a
   20 | rhetorical one, and it can go in the paper as a sentence with a number attached.
   21 | 
   22 | ## Position: real, and it matters
   23 | 
   24 | | slice | positive betas | mean β | Wilcoxon |
   25 | |---|---|---|---|
   26 | | first 5 words of a sentence | 79/168 | **−0.00219** | .187 (null) |
   27 | | first 10 words | 103/171 | +0.00169 | 5.8e-3 |
   28 | | beyond word 10 | 131/171 | **+0.00560** | 3.9e-15 |
   29 | 
   30 | The effect is absent — slightly negative — in the first five words of a sentence
   31 | and strong deep into one. This confirms the position profile found earlier, now
   32 | under subject-level inference. It is a genuine boundary condition and should be
   33 | reported: a three-word backward window is partly undefined or spans a sentence
   34 | boundary at those positions, which is also where the first-token geometry lives.
   35 | 
   36 | ## My sentence-length hypothesis was wrong
   37 | 
   38 | I predicted the effect would be weaker in short sentences, since ZuCo uses short
   39 | isolated ones. The opposite is true:
   40 | 
   41 | | sentence length | mean β | Wilcoxon |
   42 | |---|---|---|
   43 | | ≤ 15 words | **+0.00810** | 1.6e-9 |
   44 | | 16–25 words | +0.00318 | 7.6e-5 |
   45 | | > 25 words | +0.00362 | 3.4e-9 |
   46 | 
   47 | Short sentences show the *strongest* effect. And the combined "most ZuCo-like"
   48 | slice (short sentences, first 10 words) is still clearly significant
   49 | (+0.0074, p = 2.3e-7). So stimulus length does not explain the ZuCo null and
   50 | should not be offered as an explanation — it is checkable, and a referee who
   51 | checks it will find the opposite.
   52 | 
   53 | What survives is: position within sentence matters, sentence length does not.
   54 | 
   55 | ## What to write
   56 | 
   57 | 1. Report the ZuCo null plainly.
   58 | 2. Explain it with the power simulation — 42% detection at n = 10 — not with
   59 |    speculation about stimuli.
   60 | 3. Report the position boundary condition on its own merits, since it is real
   61 |    and interesting, without leaning on it to explain ZuCo.
   62 | 4. Do not claim short/isolated stimuli weaken the effect. They do not.
   63 | 
   64 | The remaining honest possibility, which cannot be settled with these data, is a
   65 | paradigm difference: self-paced reading forces a button press per word and is
   66 | sensitive to integration cost; free eye movement permits skipping, regression
   67 | and parafoveal preview. Worth one sentence as a hypothesis, flagged as such.
```


==============================================================================
### FILE: gp_confound_check/RESULTS_zuco_regressions.md
==============================================================================

```
    1 | # ZuCo test of the regression prediction — mixed, and it breaks my account (2026-07-27)
    2 | 
    3 | Preregistered in `PREREG_zuco_regressions.md` before running. 12 subjects,
    4 | 30,708 fixated words, regression flag derived as GPT > GD (pre-specified),
    5 | subject-level inference, controls = word length, log frequency, surprisal.
    6 | Output: `zuco_regress.txt`.
    7 | 
    8 | ## Results against the pre-specified predictions
    9 | 
   10 | | prediction | pre-specified criterion | result | verdict |
   11 | |---|---|---|---|
   12 | | **P1** TEE → regression probability | ≥ 7/10 positive | 8/12 (67%), β = +0.034, sign p = .39, Wilcoxon p = .034 | **weakly supportive, does not clear the bar** |
   13 | | **P2** TEE does NOT predict durations | 4–6/10 positive | TRT **11/12**, β = +0.0079, sign p = .006; GD 10/12, p = .042 | **CONTRADICTED** |
   14 | | **P3** surprisal predicts durations, not regressions | — | surprisal GD p = .68, TRT p = .052; regression model failed to converge | **untestable / surprisal weak here** |
   15 | 
   16 | Punctuation-free P1: 9/12 positive, β = +0.037, Wilcoxon p = .034.
   17 | 
   18 | ## What this does to the account
   19 | 
   20 | The story I proposed — trajectory departure produces a look-back rather than a
   21 | longer look, so TEE predicts regressions and not durations — required P2. P2 is
   22 | contradicted in the opposite direction: in ZuCo, TEE predicts **total reading
   23 | time** in 11 of 12 subjects. That is the cleanest duration effect in any
   24 | eye-tracking data I have run, and it is exactly what the account said should not
   25 | happen.
   26 | 
   27 | So the account is dead. I am not going to construct a third one.
   28 | 
   29 | ## The actual state of the evidence
   30 | 
   31 | Three behavioral corpora, and they do not agree:
   32 | 
   33 | | corpus | paradigm | n | TEE → reading time |
   34 | |---|---|---|---|
   35 | | Natural Stories | self-paced | 171 | **positive**, 73% of participants, p = 5e-12 |
   36 | | ZuCo | eye-tracking, isolated sentences | 12 | **positive** (TRT), 11/12, p = .003 |
   37 | | OneStop | eye-tracking, paragraphs | 180 | **null to negative**, TRT β = −0.0023, p = .029 |
   38 | 
   39 | The mismatch is therefore **not** self-paced versus eye-tracking — ZuCo is free
   40 | reading and shows a positive duration effect agreeing with Natural Stories. The
   41 | odd one out is OneStop, which is also the best-powered.
   42 | 
   43 | Candidate differences for OneStop specifically, none tested:
   44 | - Guardian news prose vs narrative (Natural Stories) and mixed sentences (ZuCo)
   45 | - multi-line paragraph display vs single sentences
   46 | - a comprehension-question task after every paragraph
   47 | - 360 participants recruited across two sites (MIT / Technion)
   48 | 
   49 | Note also that ZuCo's earlier in-house analysis found a *null* on the same data
   50 | (`HONEST_RESULTS_behavioral.md`: TRT Wilcoxon p = .065, 10 subjects). The
   51 | difference here is log-transformed durations, a surprisal control, and all 12
   52 | subjects rather than 10. That is a defensible spec, but it means the ZuCo result
   53 | is sensitive to analysis choices in a way the Natural Stories result is not.
   54 | 
   55 | ## Honest summary
   56 | 
   57 | - The OneStop regression effect (β = +0.017, p = 3.4e-5, n = 180, surprisal
   58 |   null on the same measure) is real and interesting, and it replicates weakly in
   59 |   ZuCo (8/12, p = .034 by Wilcoxon, not by sign test).
   60 | - The duration effects are inconsistent across corpora and the inconsistency is
   61 |   not explained by paradigm.
   62 | - Nothing here supports a confident claim that TEE indexes human processing cost
   63 |   in general. It supports "TEE predicts reading behaviour in some corpora and not
   64 |   others, for reasons not currently understood."
   65 | 
   66 | ## Recommendation
   67 | 
   68 | Do not build the paper on the behavioral results. Framing B — the model-internal
   69 | geometry, where the dissociation and the causal wake are large, controlled and
   70 | audited — does not depend on any of this. The behavioral work becomes a section
   71 | reporting a mixed picture honestly, or a separate paper once the OneStop
   72 | discrepancy is understood.
```


==============================================================================
### FILE: gp_confound_check/VERIFY_eyetracking_out.txt
==============================================================================

```
    1 | ==============================================================================
    2 | ONESTOP
    3 | ==============================================================================
    4 |   raw rows 1,104,883   participants 180
    5 |   [PASS] TEE merge preserves rows: 1,104,883
    6 |   after lag construction 1,104,883
    7 |   [PASS] participants: 180
    8 | 
    9 |   total reading time, lag 0:
   10 |     TEE                                n= 180  beta= -0.00515  41.1% positive  p=3.165e-03
   11 |   [PASS] OneStop TEE is negative: beta = -0.00515 (target -0.0023)
   12 |   [FAIL] OneStop TEE magnitude: -0.00515 vs -0.00230
   13 |     surprisal [sanity]                 n= 180  beta= +0.11838  99.4% positive  p=2.828e-31
   14 |   [PASS] OneStop surprisal is strongly positive: beta = +0.11838, 99.4% positive (target +0.031, 178/180)
   15 | 
   16 |   total reading time, lag 1:
   17 |     TEE at lag 1                       n= 180  beta= +0.00288  54.4% positive  p=1.246e-01
   18 |   [PASS] OneStop lag-1 fails the replication criterion: beta +0.00288, 54.4% positive, p = 0.125
   19 | 
   20 | ==============================================================================
   21 | ZUCO
   22 | ==============================================================================
   23 |   rows 30,708   subjects 12
   24 |     TEE                                n=  12  beta= +0.01237  83.3% positive  p=9.277e-03
   25 |   [PASS] ZuCo subjects: 12 with sufficient data
   26 |   [FAIL] ZuCo TEE positive in 11 of 12: 10 of 12 positive, beta +0.01237 (target +0.0079)
   27 | 
   28 | ==============================================================================
   29 | VERDICT
   30 | ==============================================================================
   31 |   2 CHECK(S) FAILED: OneStop TEE magnitude, ZuCo TEE positive in 11 of 12
   32 |   The eye-tracking claims must be resolved before upload.
```


==============================================================================
### FILE: gp_confound_check/VERIFY_sap_out.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | [transformers] The following generation flags are not valid and may be ignored: ['output_hidden_states']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
    3 | 
    4 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 10311.41it/s]
    6 | raw rows 636,266   participants 2,000
    7 | sentence-word inventory: 1,923 rows   hash e9fd2c547a
    8 | 
    9 | ==============================================================================
   10 | 1. MEASURE AGREEMENT WITH THE CACHED PIPELINE
   11 | ==============================================================================
   12 |   [PASS] row count: 1,923 vs 1,923
   13 |   [PASS] TEE values: max relative diff 4.68e-16  (n=1,347, r=1.0000000000)
   14 |   [PASS] surprisal values: max relative diff 6.07e-08  (n=1,923, r=1.0000000000)
   15 |   [PASS] sentence length values: max relative diff 0.00e+00  (n=1,923, r=1.0000000000)
   16 |   [PASS] TEE missingness pattern: 576 vs 576 undefined, identical positions
   17 | 
   18 | ==============================================================================
   19 | 2. SINK EXCLUSION AND POSITION FLOOR
   20 | ==============================================================================
   21 |   [PASS] first usable WordPosition is 5: min = 5
   22 |   [PASS] no fit window includes token 0: earliest window start index across all sentences = 1 (must be >= 1)
   23 | 
   24 | ==============================================================================
   25 | 3. ANALYSIS SAMPLE REBUILD (counts asserted at every step)
   26 | ==============================================================================
   27 |   [PASS] merge preserves rows: 636,266
   28 |   after lags 636,266 -> after filters 444,737
   29 |   [PASS] analysis rows: 444,737 vs target 444,737
   30 |   [PASS] participants: 2,000
   31 | 
   32 | ==============================================================================
   33 | 4. HEADLINE MODELS REFIT FROM THE INDEPENDENT MEASURES
   34 | ==============================================================================
   35 | spec                             beta   % pos  target beta  target %
   36 | A1 flexible position         +0.02238   61.1%     +0.02238     61.1%
   37 |   [PASS] A1 beta: +0.02238 vs +0.02238
   38 |   [PASS] A1 sign agreement: 61.1% vs 61.1%
   39 | A2 + final flag              +0.02505   62.7%     +0.02505     62.7%
   40 |   [PASS] A2 beta: +0.02505 vs +0.02505
   41 |   [PASS] A2 sign agreement: 62.7% vs 62.7%
   42 |   [PASS] permutation floor: 52.1% positive, p = 0.231 (target ~52.1%, n.s.)
   43 | 
   44 | ==============================================================================
   45 | 5. UNION-SURPRISAL SPEC AND POOLED dAIC
   46 | ==============================================================================
   47 |   [PASS] union-surprisal beta: +0.02543 vs +0.02543 (62.6% positive)
   48 |   [PASS] pooled dAIC, df=8 spline surprisal: 121.9 vs target 121.9
   49 | 
   50 | ==============================================================================
   51 | VERDICT
   52 | ==============================================================================
   53 |   ALL CHECKS PASSED.
   54 |   Sentence-word inventory hash: e9fd2c547a
   55 |   Analysis sample: 444,737 rows, 2,000 participants
   56 |   Sections 4b/4c are independently verified and may be published.
   57 |   Verified measures written to sap_measures_VERIFIED_e9fd2c547a.csv
```


==============================================================================
### FILE: gp_confound_check/decay_out.txt
==============================================================================

```
    1 | hash 8a6087341e verified | rows 813,621 | participants 178
    2 | participants with both profiles: 170
    3 | excluded by positivity guard: 42 (24.7%)   analysed: 128
    4 | 
    5 | ==============================================================================
    6 | P2 (PRIMARY): late/early ratio, TEE vs surprisal
    7 | ==============================================================================
    8 |   mean R(TEE)       = -0.1686   median +0.1709
    9 |   mean R(surprisal) = +1.0070   median +0.4773
   10 | 
   11 |   mean difference (TEE - surprisal) = -1.1756
   12 |   participants with R_TEE < R_surprisal: 67.2%
   13 |   paired Wilcoxon: p = 3.432e-05
   14 | 
   15 |   PRE-SPECIFIED CRITERIA: MET
   16 | 
   17 | ==============================================================================
   18 | S5: half-life (first lag where |beta| < 50% of that measure's peak)
   19 | ==============================================================================
   20 |   median half-life TEE       = 1.0 words
   21 |   median half-life surprisal = 0.5 words
   22 |   participants with TEE shorter: 44.5%
   23 |   paired Wilcoxon: p = 1.187e-01
   24 | 
   25 | ==============================================================================
   26 | S6: bootstrap 95% CI on mean(R_TEE - R_surprisal)
   27 | ==============================================================================
   28 |   mean difference -1.1756   95% CI [-2.6192, -0.3311]
   29 | 
   30 | ==============================================================================
   31 | Mean profiles (for the record)
   32 | ==============================================================================
   33 |  lag         TEE    surprisal
   34 |    0    +0.02267     +0.05064
   35 |    1    +0.02846     +0.08630
   36 |    2    +0.01379     +0.07396
   37 |    3    +0.00730     +0.04767
   38 |    4    +0.00590     +0.02946
   39 |    5    +0.00235     +0.02492
```


==============================================================================
### FILE: gp_confound_check/displacement_output.txt
==============================================================================

```
    1 | corpus: 10256 words, stories [np.int64(1), np.int64(2), np.int64(3), np.int64(4), np.int64(5), np.int64(6), np.int64(7), np.int64(8), np.int64(9), np.int64(10)]
    2 | parsed 485 trees, 11729 leaves
    3 | aligned 10256 words
    4 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    5 | 
    6 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    7 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 10642.89it/s]
    8 | story 1: forward pass...
    9 | [transformers] Token indices sequence length is longer than the specified maximum sequence length for this model (1289 > 1024). Running this sequence through the model will result in indexing errors
   10 | story 1: done
   11 | story 2: forward pass...
   12 | story 2: done
   13 | story 3: forward pass...
   14 | story 3: done
   15 | story 4: forward pass...
   16 | story 4: done
   17 | story 5: forward pass...
   18 | story 5: done
   19 | story 6: forward pass...
   20 | story 6: done
   21 | story 7: forward pass...
   22 | story 7: done
   23 | story 8: forward pass...
   24 | story 8: done
   25 | story 9: forward pass...
   26 | story 9: done
   27 | story 10: forward pass...
   28 | story 10: done
   29 | 
   30 | VALIDATION (locked sample, hash 8a6087341e, n=9840):
   31 |   closure_depth mismatches: 0
   32 |   final_bpe mismatches:     0
   33 |   max |tee_k50 - re|:       6.002e-05
   34 |   max |tee_k3  - re|:       1.029e-04
   35 |   curvature_1 NaNs:         0
   36 |   curvature_3 NaNs:         0
   37 |   curvature_1 mean/sd:      1.9978 / 0.1712
   38 |   curvature_3 mean/sd:      1.9942 / 0.0736
   39 |   disp_word mean/sd:        64.009 / 9.438
   40 |   r(disp_word, tee_k3):     0.7998
   41 |   r(disp_word, tee3_perp):  0.7627
   42 | 
   43 | DONE -> displacement_8a6087341e.csv
```


==============================================================================
### FILE: gp_confound_check/dynrep_out.txt
==============================================================================

```
    1 | Loading OneStop ...
    2 |   rows 710,927  participants 180
    3 | 
    4 | ==============================================================================
    5 | P3 (PRIMARY): OneStop total reading time, TEE impulse response
    6 | ==============================================================================
    7 |  lag     n   mean beta  % same sign   Wilcoxon p    NS ref
    8 |    0   127    -0.00868       64.6%     1.57e-05   +0.0160
    9 |    1   127    +0.00139       52.0%     4.63e-01   +0.0205
   10 |    2   127    +0.00117       52.0%     7.40e-01   +0.0085
   11 |    3   127    +0.00112       52.8%     8.17e-01   +0.0041
   12 |    4   127    +0.00446       55.1%     2.74e-01   +0.0028
   13 |    5   127    +0.01285       65.4%     3.56e-04   -0.0005
   14 | 
   15 |   PRE-SPECIFIED REPLICATION CRITERION (lag 1): NOT MET
   16 |     beta +0.00139, 52.0% positive, p = 4.63e-01, threshold p < 0.0017 and >= 65% positive
   17 | 
   18 | ==============================================================================
   19 | P4: decay ratio TEE vs surprisal (OneStop)
   20 | ==============================================================================
   21 |   excluded by positivity guard: 75/127 (59.1%)
   22 |   median R(TEE) +0.3651   median R(surprisal) +0.1949
   23 |   R_TEE < R_surprisal in 38.5% of participants, p = 1.216e-01
   24 | 
   25 | Loading ZuCo ...
   26 |   rows 30,708  subjects 12
   27 | 
   28 | ==============================================================================
   29 | P5 (secondary): ZuCo total reading time, 12 subjects
   30 | ==============================================================================
   31 |  lag     n   mean beta  % same sign   Wilcoxon p    NS ref
   32 |    0     6    +0.01172       83.3%     6.25e-02   +0.0160
   33 |    1     6    -0.02874      100.0%     3.12e-02   +0.0205
   34 |    2     6    -0.00872       66.7%     5.62e-01   +0.0085
   35 |    3     6    +0.00208       66.7%     8.44e-01   +0.0041
   36 |    4     6    -0.01124       66.7%     5.62e-01   +0.0028
   37 |    5     6    +0.00024       50.0%     1.00e+00   -0.0005
```


==============================================================================
### FILE: gp_confound_check/ext_wake_output.txt
==============================================================================

```
    1 | SAMPLE hash=8a6087341e  wake n=1627  punct-final=213
    2 | 
    3 | ==============================================================================
    4 | PUNCT-FREE | DV=wake_rel | target controls: NO (as published)
    5 | ==============================================================================
    6 |  lag           ntee_k100           tee3_perp        surprisal(w)      n
    7 | L1     +0.1997(8.7e-13)*   +0.1005(1.2e-02)*   +0.1097(2.1e-03)*   1414
    8 | L2     +0.1877(2.0e-10)*   -0.0197(6.0e-01)    +0.2025(4.6e-09)*   1414
    9 | L3     +0.1724(2.5e-09)*   -0.0436(2.6e-01)    +0.1474(8.5e-06)*   1414
   10 | L4     +0.1687(5.8e-08)*   -0.0657(8.3e-02)    +0.1031(5.3e-04)*   1414
   11 | L5     +0.1676(6.8e-09)*   -0.0681(4.8e-02)*   +0.0848(1.2e-03)*   1414
   12 | L6     +0.1330(2.0e-06)*   -0.0744(2.0e-02)*   +0.1174(3.0e-05)*   1414
   13 | L7     +0.1148(3.1e-05)*   -0.0872(1.2e-02)*   +0.1192(1.2e-03)*   1414
   14 | L8     +0.1328(1.1e-06)*   -0.0100(7.8e-01)    +0.0978(1.2e-03)*   1414
   15 | L9     +0.1434(1.6e-07)*   -0.0729(5.8e-02)    +0.0961(1.9e-03)*   1414
   16 | L10    +0.1287(2.0e-06)*   -0.0397(3.1e-01)    +0.0602(4.8e-02)*   1414
   17 | 
   18 | ==============================================================================
   19 | PUNCT-FREE | DV=wake_rel | target controls: YES
   20 | ==============================================================================
   21 |  lag           ntee_k100           tee3_perp        surprisal(w)      n
   22 | L1     +0.1997(7.4e-19)*   +0.0363(2.3e-01)    +0.1632(9.9e-09)*   1414
   23 | L2     +0.1754(1.2e-09)*   -0.0081(8.3e-01)    +0.1887(5.9e-08)*   1414
   24 | L3     +0.1715(1.6e-09)*   -0.0356(3.5e-01)    +0.1521(2.7e-06)*   1414
   25 | L4     +0.1672(6.1e-08)*   -0.0699(5.9e-02)    +0.0989(6.3e-04)*   1414
   26 | L5     +0.1628(1.5e-08)*   -0.0679(4.9e-02)*   +0.0917(4.7e-04)*   1414
   27 | L6     +0.1331(1.7e-06)*   -0.0796(1.3e-02)*   +0.1202(2.2e-05)*   1414
   28 | L7     +0.1162(2.3e-05)*   -0.0892(9.2e-03)*   +0.1173(1.4e-03)*   1414
   29 | L8     +0.1326(1.4e-06)*   -0.0105(7.7e-01)    +0.0988(1.2e-03)*   1414
   30 | L9     +0.1404(3.1e-07)*   -0.0703(6.5e-02)    +0.1003(1.4e-03)*   1414
   31 | L10    +0.1298(1.6e-06)*   -0.0373(3.4e-01)    +0.0585(5.8e-02)    1414
   32 | 
   33 | ==============================================================================
   34 | PUNCT-FREE | DV=wake_coarse | target controls: NO (as published)
   35 | ==============================================================================
   36 |  lag           ntee_k100           tee3_perp        surprisal(w)      n
   37 | L1     +0.1997(8.7e-13)*   +0.1005(1.2e-02)*   +0.1097(2.1e-03)*   1414
   38 | L2     +0.1994(5.5e-12)*   +0.0657(9.2e-02)    +0.1596(1.0e-05)*   1414
   39 | L3     +0.2115(2.4e-13)*   +0.0363(3.4e-01)    +0.1600(7.5e-06)*   1414
   40 | L4     +0.2168(5.8e-14)*   +0.0207(5.8e-01)    +0.1569(6.8e-06)*   1414
   41 | L5     +0.2196(1.2e-14)*   +0.0107(7.7e-01)    +0.1568(4.1e-06)*   1414
   42 | L6     +0.2085(1.2e-13)*   -0.0634(7.0e-02)    +0.1688(8.4e-08)*   1414
   43 | L7     +0.1859(4.9e-12)*   -0.0796(2.1e-02)*   +0.1361(3.0e-06)*   1414
   44 | L8     +0.1764(3.3e-11)*   -0.0809(1.8e-02)*   +0.1229(1.1e-05)*   1414
   45 | L9     +0.1711(6.7e-11)*   -0.0737(2.8e-02)*   +0.1208(2.0e-05)*   1414
   46 | L10    +0.1609(4.7e-10)*   -0.0642(5.8e-02)    +0.1225(3.4e-05)*   1414
   47 | 
   48 | ==============================================================================
   49 | PUNCT-FREE | DV=wake_coarse | target controls: YES
   50 | ==============================================================================
   51 |  lag           ntee_k100           tee3_perp        surprisal(w)      n
   52 | L1     +0.1997(7.4e-19)*   +0.0363(2.3e-01)    +0.1632(9.9e-09)*   1414
   53 | L2     +0.2013(3.5e-12)*   +0.0632(1.1e-01)    +0.1568(1.2e-05)*   1414
   54 | L3     +0.2095(3.4e-13)*   +0.0347(3.6e-01)    +0.1607(8.1e-06)*   1414
   55 | L4     +0.2162(6.3e-14)*   +0.0190(6.1e-01)    +0.1544(9.3e-06)*   1414
   56 | L5     +0.2183(1.6e-14)*   +0.0111(7.6e-01)    +0.1596(3.0e-06)*   1414
   57 | L6     +0.2084(1.1e-13)*   -0.0679(5.2e-02)    +0.1707(6.6e-08)*   1414
   58 | L7     +0.1864(4.5e-12)*   -0.0800(2.1e-02)*   +0.1366(3.1e-06)*   1414
   59 | L8     +0.1768(4.7e-11)*   -0.0810(1.7e-02)*   +0.1213(1.4e-05)*   1414
   60 | L9     +0.1680(1.7e-10)*   -0.0714(3.2e-02)*   +0.1239(1.4e-05)*   1414
   61 | L10    +0.1615(4.8e-10)*   -0.0642(5.8e-02)    +0.1231(3.6e-05)*   1414
```


==============================================================================
### FILE: gp_confound_check/freq_sign_check_out.txt
==============================================================================

```
    1 | ==============================================================================
    2 | (a) IS THE VARIABLE WHAT IT SAYS IT IS?
    3 | ==============================================================================
    4 |   highest log_freq words in the Natural Stories sample:
    5 |     the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67), the(6.67)
    6 |   lowest log_freq words:
    7 |     hummed(0.00), clattered(0.00), spun(0.00), wool(0.00), long-bearded(0.00), owners.(0.00), beavers(0.00), successful(0.00), residents(0.00), stately(0.00), Hall,(0.00), Crest(0.00)
    8 | 
    9 |   range 0.00 to 6.67, mean 2.76
   10 |   reference Zipf values: {'the': 7.73, 'of': 7.4, 'and': 7.41, 'manor': 3.81, 'ocean': 4.7, 'tics': 2.64}
   11 |   r(log_freq, word_length) = -0.701   (should be NEGATIVE: frequent words are short)
   12 |   r(log_freq, surprisal)   = -0.536   (should be NEGATIVE: frequent words are predictable)
   13 | 
   14 | ==============================================================================
   15 | (b) WHERE DOES THE SIGN FLIP?  Natural Stories
   16 | ==============================================================================
   17 |   raw r(log_freq, log_RT) = -0.0278   (NEGATIVE as expected)
   18 | 
   19 |   model                       beta(log_freq)   % positive
   20 |   log_freq alone                    -0.03425       17.5%
   21 |   + word_length                     +0.00505       55.0%
   22 |   + surprisal                       +0.02286       73.7%
   23 |   + trajectory error                +0.02864       77.8%
   24 |   + remaining controls              +0.02229       77.2%
   25 | 
   26 | ==============================================================================
   27 | (b) WHERE DOES THE SIGN FLIP?  Garden-path corpus
   28 | ==============================================================================
   29 |   raw r(log_freq, log_RT) = -0.1310   (NEGATIVE as expected)
   30 | 
   31 |   model                       beta(log_freq)   % positive
   32 |   log_freq alone                    -0.15953        4.6%
   33 |   + word_length                     -0.01980       43.2%
   34 |   + surprisal                       -0.00977       47.5%
   35 |   + trajectory error                -0.00127       50.4%
   36 |   + remaining controls              +0.02347       58.9%
   37 | 
   38 | ==============================================================================
   39 | READING
   40 | ==============================================================================
   41 |   If log_freq alone is NEGATIVE and turns positive only once surprisal
   42 |   enters, this is suppression: surprisal absorbs the predictability component of
   43 |   frequency and what remains carries the opposite sign. Legitimate, but it must
   44 |   be stated in the text.
   45 | 
   46 |   If log_freq is POSITIVE even on its own, the variable is not measuring what
   47 |   its name says and every model in the paper needs rechecking.
```


==============================================================================
### FILE: gp_confound_check/gp_allwords_matched_out.txt
==============================================================================

```
    1 | rows 444,737   participants 2,000
    2 | 
    3 | participants with data: 2,000
    4 | ==============================================================================
    5 | A. BOTH MEASURES FROM THE SAME FIT (identical rows and controls)
    6 | ==============================================================================
    7 | spec / measure                         n       beta   % pos          p
    8 | A1  flexible position  [TEE]        2000   +0.02238   61.1%   2.67e-32
    9 |                                 [surprisal]  2000   +0.02653   56.6%   2.51e-20
   10 | 
   11 | A2  A1 + final flag  [TEE]          2000   +0.02505   62.7%   5.51e-39
   12 |                                 [surprisal]  2000   +0.02832   57.8%   4.12e-23
   13 | 
   14 | A3  A2 + previous log RT  [TEE]     2000   +0.01362   57.5%   4.89e-16
   15 |                                 [surprisal]  2000   +0.04483   64.7%   1.40e-60
   16 | 
   17 | ==============================================================================
   18 | B. EACH MEASURE LINEAR WHILE THE OTHER IS SPLINED (df=5)
   19 | ==============================================================================
   20 | spec                                   n       beta   % pos          p
   21 | B1  TEE, spline surprisal           2000   +0.02067   60.3%   5.36e-28
   22 | B2  surprisal, spline TEE           2000   +0.02676   57.1%   3.71e-20
   23 | 
   24 | ==============================================================================
   25 | C. FLOOR: A1 with TEE permuted within participant
   26 | ==============================================================================
   27 | spec                                   n       beta   % pos          p
   28 | C   permuted TEE (null floor)       2000   +0.00146   52.1%   2.31e-01
   29 | 
   30 | ==============================================================================
   31 | D. PAIRED, WITHIN PARTICIPANT: is |beta_TEE| > |beta_surprisal|?
   32 | ==============================================================================
   33 |   A1  flexible position          |TEE|>|surp| in 42.1% of participants   paired p = 3.66e-21
   34 |                                  mean |beta| TEE 0.06873  surprisal 0.09074
   35 |   A2  A1 + final flag            |TEE|>|surp| in 42.8% of participants   paired p = 5.54e-20
   36 |                                  mean |beta| TEE 0.06963  surprisal 0.09119
   37 |   A3  A2 + previous log RT       |TEE|>|surp| in 39.0% of participants   paired p = 9.18e-43
   38 |                                  mean |beta| TEE 0.06239  surprisal 0.09353
```


==============================================================================
### FILE: gp_confound_check/gp_allwords_out.txt
==============================================================================

```
    1 | raw rows                636,266
    2 | participants            2,000
    3 | sentences               144   types 6
    4 | after measure merge     636,266
    5 | after lag construction  636,266
    6 | after RT filter         635,201
    7 | after dropping undefined TEE etc  444,737
    8 |   usable WordPositions: [np.int64(5), np.int64(6), np.int64(7), np.int64(8), np.int64(9), np.int64(10), np.int64(11), np.int64(12), np.int64(13), np.int64(14), np.int64(15), np.int64(16), np.int64(17)]
    9 |   participants remaining: 2,000
   10 | 
   11 | ==============================================================================
   12 | P1 (PRIMARY): TEE -> log RT, all words, all conditions
   13 | ==============================================================================
   14 |   TEE
   15 |     n = 2000   mean beta = +0.03402   67.2% positive   Wilcoxon p = 2.662e-67   SUPPORT
   16 | 
   17 | S3 reference -- surprisal from the same models:
   18 |     mean beta = +0.02414   56.8% positive   Wilcoxon p = 6.973e-17
   19 |     TEE / surprisal magnitude ratio = 1.41
   20 | 
   21 | ==============================================================================
   22 | S1: same, controlling previous log RT
   23 | ==============================================================================
   24 |   TEE
   25 |     n = 2000   mean beta = +0.01677   59.7% positive   Wilcoxon p = 1.047e-22   null
   26 | 
   27 | ==============================================================================
   28 | S2: lag 1 -- TEE at word t -> log RT at word t+1
   29 | ==============================================================================
   30 |   TEE
   31 |     n = 1657   mean beta = -0.00656   46.3% positive   Wilcoxon p = 3.046e-03   null
   32 | 
   33 | ==============================================================================
   34 | S4 (descriptive): breakdown -- is any effect carried by one cell?
   35 | ==============================================================================
   36 | subset                  n subj   mean beta    % pos           p
   37 | construction MVRR         2000    +0.05670   66.5%    1.08e-70
   38 | construction NPS          2000    +0.06372   66.3%    1.22e-70
   39 | construction NPZ          2000    -0.00669   49.0%    4.99e-02
   40 | ambiguous                 2000    +0.02509   58.7%    5.75e-21
   41 | unambiguous               2000    +0.03018   59.9%    9.22e-28
   42 | 
   43 | ==============================================================================
   44 | S5: pooled mixedlm dAIC  [PSEUDOREPLICATED -- comparability only]
   45 | ==============================================================================
   46 |   n = 444,737   participants = 2,000
   47 |   AIC without TEE 320895.3   with TEE 320514.8   dAIC = +380.5
   48 |   z_tee beta = +0.01186   p = 3.319e-85
```


==============================================================================
### FILE: gp_confound_check/gp_allwords_robust_out.txt
==============================================================================

```
    1 | measures computed and cached (1,923 rows)
    2 | rows 444,737   participants 2,000
    3 | 
    4 | ==============================================================================
    5 | THREAT 1 EVIDENCE: does TEE covary with position?
    6 | ==============================================================================
    7 |   r(TEE, from_start) = -0.094
    8 |   r(TEE, from_end)   = +0.045
    9 |   r(TEE, is_final)   = -0.003
   10 | 
   11 |   mean TEE and mean log RT by position from sentence end:
   12 |              tee  logRT      n
   13 | from_end
   14 | 0.0       89.118  6.114  47632
   15 | 1.0       85.404  5.844  47688
   16 | 2.0       85.543  5.870  47686
   17 | 3.0       91.150  5.950  47670
   18 | 4.0       91.492  5.999  47647
   19 | 5.0       92.968  6.006  47641
   20 | 6.0       92.872  5.969  47625
   21 | 7.0       88.327  5.941  45537
   22 | 8.0       87.577  5.934  32098
   23 | 
   24 | ==============================================================================
   25 | PER-PARTICIPANT MODELS  (criterion: p<.01 AND >=65% same sign)
   26 | ==============================================================================
   27 | model                                      n       beta   % pos          p  verdict
   28 | M0  linear pos, linear surp (= P1)      2000   +0.03402   67.2%   2.66e-67  SUPPORT
   29 | M1  + flexible position                 2000   +0.02238   61.1%   2.67e-32     null
   30 | M2  M1 + sentence-final flag            2000   +0.02505   62.7%   5.51e-39     null
   31 | M3  M1, spline surprisal df=3           2000   +0.02024   60.2%   3.60e-27     null
   32 | M4  M1, spline surprisal df=5           2000   +0.02067   60.3%   5.36e-28     null
   33 | M5  M1, spline surprisal df=8           2000   +0.02086   60.4%   1.92e-28     null
   34 | M6  M5 + final flag + prev log RT       2000   +0.01140   56.5%   2.67e-12     null
   35 | 
   36 | ==============================================================================
   37 | Was the LINEAR surprisal form actually wrong here? (pooled AIC)
   38 | ==============================================================================
   39 |   linear surprisal         AIC  1060932.7   +TEE  1060779.6   dAIC(TEE)   +153.2
   40 |   spline surprisal df=5    AIC  1059432.2   +TEE  1059311.7   dAIC(TEE)   +120.4
   41 |   spline surprisal df=8    AIC  1059422.0   +TEE  1059300.1   dAIC(TEE)   +121.9
```


==============================================================================
### FILE: gp_confound_check/gp_item_level_out.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | [transformers] The following generation flags are not valid and may be ignored: ['output_hidden_states']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
    3 | 
    4 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 11953.96it/s]
    6 | items=24  constructions=3  types=6
    7 | 
    8 | ==========================================================================
    9 | ROI 0 only (the disambiguating word)   n = 72 item x construction pairs
   10 | ==========================================================================
   11 |   mean human GP effect (dRT)  = +0.0751 log-ms  (66/72 positive)
   12 |   mean dTEE                   = +1.69
   13 |   mean dSurp                  = +4.89 bits
   14 | 
   15 |   r(dTEE,  dRT) = +0.280   p = 0.017
   16 |   r(dSurp, dRT) = +0.241   p = 0.041
   17 | 
   18 |   joint model (construction fixed effects):
   19 |     dSurp beta = -0.035  p = 0.784
   20 |     dTEE  beta = -0.019  p = 0.894
   21 |     R^2 = 0.317
   22 | 
   23 |   by construction:
   24 |     MVRR   n= 24  r(dTEE,dRT) = -0.168  p = 0.433  mean dRT = +0.0487
   25 |     NPS    n= 24  r(dTEE,dRT) = -0.113  p = 0.598  mean dRT = +0.0511
   26 |     NPZ    n= 24  r(dTEE,dRT) = +0.210  p = 0.324  mean dRT = +0.1254
   27 | 
   28 | ==========================================================================
   29 | critical region (ROI 0+1+2 pooled)   n = 72 item x construction pairs
   30 | ==========================================================================
   31 |   mean human GP effect (dRT)  = +0.1143 log-ms  (71/72 positive)
   32 |   mean dTEE                   = +0.66
   33 |   mean dSurp                  = +2.03 bits
   34 | 
   35 |   r(dTEE,  dRT) = -0.259   p = 0.028
   36 |   r(dSurp, dRT) = +0.331   p = 0.005
   37 | 
   38 |   joint model (construction fixed effects):
   39 |     dSurp beta = +0.143  p = 0.128
   40 |     dTEE  beta = -0.144  p = 0.222
   41 |     R^2 = 0.542
   42 | 
   43 |   by construction:
   44 |     MVRR   n= 24  r(dTEE,dRT) = -0.149  p = 0.489  mean dRT = +0.1537
   45 |     NPS    n= 24  r(dTEE,dRT) = -0.077  p = 0.722  mean dRT = +0.0566
   46 |     NPZ    n= 24  r(dTEE,dRT) = -0.087  p = 0.687  mean dRT = +0.1326
   47 | 
   48 | ==========================================================================
   49 | spillover only (ROI 1+2) - the published sample   n = 72 item x construction pairs
   50 | ==========================================================================
   51 |   mean human GP effect (dRT)  = +0.1339 log-ms  (71/72 positive)
   52 |   mean dTEE                   = +0.14
   53 |   mean dSurp                  = +0.60 bits
   54 | 
   55 |   r(dTEE,  dRT) = -0.193   p = 0.104
   56 |   r(dSurp, dRT) = +0.073   p = 0.543
   57 | 
   58 |   joint model (construction fixed effects):
   59 |     dSurp beta = +0.070  p = 0.381
   60 |     dTEE  beta = -0.010  p = 0.913
   61 |     R^2 = 0.638
   62 | 
   63 |   by construction:
   64 |     MVRR   n= 24  r(dTEE,dRT) = +0.021  p = 0.921  mean dRT = +0.2062
   65 |     NPS    n= 24  r(dTEE,dRT) = -0.022  p = 0.919  mean dRT = +0.0594
   66 |     NPZ    n= 24  r(dTEE,dRT) = +0.084  p = 0.698  mean dRT = +0.1362
```


==============================================================================
### FILE: gp_confound_check/gp_item_nofe_out.txt
==============================================================================

```
    1 | ==========================================================================
    2 | GUARD: reproduce published ROI-0 item-level numbers
    3 | ==========================================================================
    4 |   n pairs      72          expected 72
    5 |   mean dTEE    +1.69   expected +1.69
    6 |   mean dSurp   +4.89   expected +4.89
    7 |   r(dTEE,dRT)  +0.280   expected +0.280
    8 | 
    9 |   MATCH: YES
   10 | 
   11 | ==========================================================================
   12 | ROI 0 (disambiguating word)   n = 72
   13 | ==========================================================================
   14 | 
   15 | (a) POOLED, no construction fixed effects, classical SEs
   16 |     z_dSurp   beta = +0.213   SE = 0.113   p = 0.0650
   17 |     z_dTEE    beta = +0.256   SE = 0.113   p = 0.0271
   18 |     R^2 = 0.123
   19 | 
   20 | (b) same model, SEs clustered by construction (G = 3)
   21 |     z_dSurp   beta = +0.213   SE = 0.141   p = 0.1316
   22 |     z_dTEE    beta = +0.256   SE = 0.126   p = 0.0428
   23 | 
   24 | (c) leave-one-construction-out (pooled, no FE)
   25 |     drop MVRR  n= 48  dTEE +0.138 (p=0.328)   dSurp +0.387 (p=0.008)
   26 |     drop NPS   n= 48  dTEE +0.408 (p=0.006)   dSurp +0.076 (p=0.591)
   27 |     drop NPZ   n= 48  dTEE -0.145 (p=0.353)   dSurp -0.162 (p=0.300)
   28 | 
   29 | (d) construction means (the 3 points a pooled slope rests on)
   30 |                 dTEE   dSurp     dRT
   31 | construction
   32 | MVRR         -1.7223  5.2270  0.0487
   33 | NPS           2.5480  2.5540  0.0511
   34 | NPZ           4.2525  6.8978  0.1254
   35 | 
   36 | (e) WITH construction fixed effects (within-construction only)
   37 |     z_dSurp   beta = -0.035   p = 0.7839
   38 |     z_dTEE    beta = -0.019   p = 0.8942
   39 | 
   40 | (f) variance decomposition
   41 |     dTEE   between-construction share = 49.2%
   42 |     dSurp  between-construction share = 36.8%
   43 |     dRT    between-construction share = 31.6%
   44 | 
   45 | ==========================================================================
   46 | critical region ROI 0+1+2   n = 72
   47 | ==========================================================================
   48 | 
   49 | (a) POOLED, no construction fixed effects, classical SEs
   50 |     z_dSurp   beta = +0.401   SE = 0.109   p = 0.0004
   51 |     z_dTEE    beta = -0.342   SE = 0.109   p = 0.0024
   52 |     R^2 = 0.222
   53 | 
   54 | (b) same model, SEs clustered by construction (G = 3)
   55 |     z_dSurp   beta = +0.401   SE = 0.124   p = 0.0012
   56 |     z_dTEE    beta = -0.342   SE = 0.171   p = 0.0453
   57 | 
   58 | (c) leave-one-construction-out (pooled, no FE)
   59 |     drop MVRR  n= 48  dTEE +0.039 (p=0.791)   dSurp +0.408 (p=0.007)
   60 |     drop NPS   n= 48  dTEE -0.324 (p=0.039)   dSurp +0.137 (p=0.375)
   61 |     drop NPZ   n= 48  dTEE -0.507 (p=0.000)   dSurp +0.322 (p=0.009)
   62 | 
   63 | (d) construction means (the 3 points a pooled slope rests on)
   64 |                 dTEE   dSurp     dRT
   65 | construction
   66 | MVRR         -1.0292  2.1610  0.1537
   67 | NPS           1.0559  1.2491  0.0566
   68 | NPZ           1.9556  2.6756  0.1326
   69 | 
   70 | (e) WITH construction fixed effects (within-construction only)
   71 |     z_dSurp   beta = +0.143   p = 0.1282
   72 |     z_dTEE    beta = -0.144   p = 0.2216
   73 | 
   74 | (f) variance decomposition
   75 |     dTEE   between-construction share = 46.4%
   76 |     dSurp  between-construction share = 14.9%
   77 |     dRT    between-construction share = 52.1%
   78 | 
   79 | ==========================================================================
   80 | spillover ROI 1+2 (published sample)   n = 72
   81 | ==========================================================================
   82 | 
   83 | (a) POOLED, no construction fixed effects, classical SEs
   84 |     z_dSurp   beta = +0.158   SE = 0.124   p = 0.2077
   85 |     z_dTEE    beta = -0.248   SE = 0.124   p = 0.0505
   86 |     R^2 = 0.059
   87 | 
   88 | (b) same model, SEs clustered by construction (G = 3)
   89 |     z_dSurp   beta = +0.158   SE = 0.131   p = 0.2271
   90 |     z_dTEE    beta = -0.248   SE = 0.183   p = 0.1766
   91 | 
   92 | (c) leave-one-construction-out (pooled, no FE)
   93 |     drop MVRR  n= 48  dTEE +0.153 (p=0.324)   dSurp +0.017 (p=0.914)
   94 |     drop NPS   n= 48  dTEE -0.314 (p=0.055)   dSurp +0.159 (p=0.325)
   95 |     drop NPZ   n= 48  dTEE -0.369 (p=0.015)   dSurp +0.245 (p=0.098)
   96 | 
   97 | (d) construction means (the 3 points a pooled slope rests on)
   98 |                 dTEE   dSurp     dRT
   99 | construction
  100 | MVRR         -0.6826  0.6280  0.2062
  101 | NPS           0.3099  0.5967  0.0594
  102 | NPZ           0.8071  0.5645  0.1362
  103 | 
  104 | (e) WITH construction fixed effects (within-construction only)
  105 |     z_dSurp   beta = +0.070   p = 0.3809
  106 |     z_dTEE    beta = -0.010   p = 0.9128
  107 | 
  108 | (f) variance decomposition
  109 |     dTEE   between-construction share = 17.3%
  110 |     dSurp  between-construction share = 0.0%
  111 |     dRT    between-construction share = 63.3%
```


==============================================================================
### FILE: gp_confound_check/gp_mvrr_check_out.txt
==============================================================================

```
    1 | ==============================================================================
    2 | ROI 0: is dTEE reliably negative for MVRR?
    3 | ==============================================================================
    4 | constr    n  mean dTEE    neg       t         p   Wilcox p
    5 | MVRR     24      -1.72  17/24    -3.26    0.0034     0.0035
    6 | NPS      24      +2.55   4/24     6.08    0.0000     0.0000
    7 | NPZ      24      +4.25   1/24     6.77    0.0000     0.0000
    8 | 
    9 | ==============================================================================
   10 | same for SURPRISAL (is the ambiguous version 'easier' by that too?)
   11 | ==============================================================================
   12 | constr    n  mean dSurp     neg         p
   13 | MVRR     24       +5.23    1/24     0.0000
   14 | NPS      24       +2.55    0/24     0.0000
   15 | NPZ      24       +6.90    0/24     0.0000
   16 | 
   17 | ==============================================================================
   18 | RAW LEVELS: which side moves?
   19 | ==============================================================================
   20 |               tee_unamb  tee_amb  surp_unamb  surp_amb
   21 | construction
   22 | MVRR             100.97    99.24       12.70     17.93
   23 | NPS               95.73    98.27       11.68     14.24
   24 | NPZ               94.83    99.08       10.77     17.67
   25 | 
   26 | ==============================================================================
   27 | FIT-WINDOW WORDS at the disambiguator (first 6 MVRR items)
   28 | k=3 window = the three preceding words; if identical across conditions
   29 | the dTEE difference comes from earlier context, not different words.
   30 | ==============================================================================
   31 |   item  1 AMB   window=[sent the file] -> 'deserved'   TEE=106.0
   32 |   item  1 UNAMB window=[sent the file] -> 'deserved'   TEE=107.8
   33 | 
   34 |   item  2 AMB   window=[handed the bill] -> 'received'   TEE=101.4
   35 |   item  2 UNAMB window=[handed the bill] -> 'received'   TEE=100.4
   36 | 
   37 |   item  3 AMB   window=[brought the mail] -> 'disappeared'   TEE=94.7
   38 |   item  3 UNAMB window=[brought the mail] -> 'disappeared'   TEE=99.3
   39 | 
   40 |   item  4 AMB   window=[fed the chicken] -> 'stayed'   TEE=102.0
   41 |   item  4 UNAMB window=[fed the chicken] -> 'stayed'   TEE=101.8
   42 | 
   43 |   item  5 AMB   window=[offered the operation] -> 'appeared'   TEE=95.7
   44 |   item  5 UNAMB window=[offered the operation] -> 'appeared'   TEE=102.3
   45 | 
   46 |   item  6 AMB   window=[awarded the grant] -> 'gained'   TEE=96.4
   47 |   item  6 UNAMB window=[awarded the grant] -> 'gained'   TEE=96.9
   48 | 
   49 | ==============================================================================
   50 | PER-ITEM MVRR (sorted by dTEE) - look for outlier domination
   51 | ==============================================================================
   52 |  item  tee_unamb  tee_amb  dTEE  dSurp
   53 |     5     102.33    95.74 -6.59   5.81
   54 |    17     101.49    96.21 -5.28   8.38
   55 |     3      99.31    94.71 -4.60   8.20
   56 |    20     100.68    96.30 -4.38   4.21
   57 |    23      98.44    94.66 -3.78  -2.87
   58 |    13      94.92    91.39 -3.53   5.62
   59 |     7      98.81    95.63 -3.18   7.26
   60 |    15      90.14    87.00 -3.15   4.50
   61 |    18      97.49    94.50 -2.99   7.77
   62 |     9     105.57   102.58 -2.99   5.51
   63 |    11     112.80   109.98 -2.82   2.15
   64 |    16     108.14   105.75 -2.39   4.47
   65 |     1     107.83   105.99 -1.84   6.77
   66 |    19     105.02   103.23 -1.78   6.15
   67 |    12     101.58    99.87 -1.72   3.43
   68 |    21     102.09   101.22 -0.88   0.22
   69 |     6      96.90    96.38 -0.52   5.37
   70 |     4     101.81   102.02  0.21   4.52
   71 |    22      89.48    89.87  0.40   8.06
   72 |     2     100.37   101.41  1.04   7.44
   73 |    24     101.10   102.43  1.33   2.35
   74 |    14     102.61   105.21  2.59   7.06
   75 |     8     105.45   108.08  2.63   6.84
   76 |    10      98.85   101.71  2.87   6.21
   77 | 
   78 | saved per-item table -> gp_roi0_item_diffs.csv
```


==============================================================================
### FILE: gp_confound_check/make_fig_core3_out.txt
==============================================================================

```
    1 | Natural Stories: tee beta=+0.01277 73.1% pos  floor 48.9%
    2 | Garden-path corpus: tee beta=+0.02238 61.1% pos  floor 50.7%
    3 | 
    4 | wrote fig_core.png
    5 |   Natural Stories     trajectory error   +0.01277
    6 |   Natural Stories     surprisal          +0.03627
    7 |   Natural Stories     log frequency      +0.02229
    8 |   Garden-path corpus  trajectory error   +0.02238
    9 |   Garden-path corpus  surprisal          +0.02653
   10 |   Garden-path corpus  log frequency      +0.02347
```


==============================================================================
### FILE: gp_confound_check/make_fig_core_out.txt
==============================================================================

```
    1 | Natural Stories: 812,730 rows, 178 participants
    2 |     floor over 10 shuffles: 48.9% positive (range 45.6%-57.3%)
    3 | SAP: 444,737 rows, 2,000 participants
    4 |     floor over 10 shuffles: 50.7% positive (range 49.5%-51.9%)
    5 | 
    6 | wrote fig_core.png
    7 |   GPT-2 Small surprisal      beta=+0.01277  73.1% positive  n=171
    8 |   GPT-2 XL surprisal         beta=+0.01387  75.4% positive  n=171
    9 |   all four surprisals        beta=+0.01303  75.4% positive  n=171
   10 |   GPT-2 Small surprisal      beta=+0.02238  61.1% positive  n=2000
   11 |   + sentence-final flag      beta=+0.02505  62.7% positive  n=2000
   12 |   all three surprisals       beta=+0.02543  62.6% positive  n=2000
   13 |   NS  permuted floor          48.9% positive
   14 |   SAP permuted floor          50.7% positive
```


==============================================================================
### FILE: gp_confound_check/ns_audit_output.txt
==============================================================================

```
    1 | locked sample: 9,840 words | RT file: 848,875 rows, 180 participants
    2 | 
    3 | ========================================================================
    4 | A. MERGE INTEGRITY
    5 | ========================================================================
    6 | duplicate (story_id, zone) keys in word table: 0
    7 | RT rows before merge 848,875 -> after 848,875 (OK, no multiplication)
    8 | rows with no matching word record: 35,254 (4.2%)
    9 | 
   10 | ========================================================================
   11 | B. LAGGED CONTROL (prev_log_RT)
   12 | ========================================================================
   13 | prev_log_RT rows where previous row is the ADJACENT word: 843,108 / 847,976 (99.4%)
   14 | rows where the 'previous' word is 2+ zones back (filtered-out neighbour): 4,868
   15 |   -> same shape as the garden-path bug: the lag is computed AFTER row filtering.
   16 |      Milder here: it mislabels the control on a minority of rows rather than deleting a whole condition.
   17 | 
   18 | ========================================================================
   19 | C. SAMPLE EQUALITY FOR THE AIC COMPARISON
   20 | ========================================================================
   21 | analysis N = 813,621  participants = 178  stories = 10
   22 | M1 and M2 are both fit on this frame (M2 adds a term that is already non-null here), so the nested comparison is on identical rows: OK.
   23 | 
   24 | headline: dAIC = 109.8   beta(TEE) = +0.00351   p = 3.989e-26
   25 | for scale: beta(surprisal) = +0.01118, beta(log_freq) = +0.00720, beta(prev_log_RT) = +0.13954
   26 | 
   27 | with the lag control repaired (adjacent-word rows only, n = 809,101):
   28 |   dAIC = 107.0   beta(TEE) = +0.00344   p = 1.648e-25
   29 | 
   30 | ========================================================================
   31 | D. HETEROGENEITY -- does the effect hold its sign across subsets?
   32 | ========================================================================
   33 | 
   34 | by story:
   35 |   story  1  n= 87,176  beta=+0.00422  p=0.000
   36 |   story  2  n= 86,252  beta=+0.00530  p=0.000
   37 |   story  3  n= 90,409  beta=+0.00467  p=0.000
   38 |   story  4  n= 90,784  beta=-0.00098  p=0.321
   39 |   story  5  n= 90,533  beta=+0.00326  p=0.001
   40 |   story  6  n= 87,211  beta=+0.00589  p=0.000
   41 |   story  7  n= 70,945  beta=+0.00358  p=0.000
   42 |   story  8  n= 68,560  beta=+0.00434  p=0.000
   43 |   story  9  n= 77,118  beta=+0.00716  p=0.000
   44 |   story 10  n= 64,633  beta=+0.00380  p=0.001
   45 |   -> 9/10 stories positive
   46 | 
   47 | by sentence position (from_start bucket):
   48 | Traceback (most recent call last):
   49 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/ns_audit.py", line 149, in <module>
   50 |     main()
   51 |     ~~~~^^
   52 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/ns_audit.py", line 130, in main
   53 |     d["pos_bin"] = pd.cut(d.from_start, [-1, 2, 5, 10, 20, 999],
   54 |                           ^^^^^^^^^^^^
   55 |   File "/opt/homebrew/lib/python3.14/site-packages/pandas/core/generic.py", line 6206, in __getattr__
   56 |     return object.__getattribute__(self, name)
   57 |            ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
   58 | AttributeError: 'DataFrame' object has no attribute 'from_start'
```


==============================================================================
### FILE: gp_confound_check/ns_base_fit_check_out.txt
==============================================================================

```
    1 | n = 812,730   participants = 178
    2 | 
    3 | ================================================================================
    4 | HOW WELL DOES EACH SURPRISAL PREDICT READING TIME, ON ITS OWN?
    5 | ================================================================================
    6 |   controls only (no surprisal)      AIC     162331.1
    7 | surprisal source               base AIC  dAIC vs ctrl   dAIC(TEE)
    8 | GPT-2 Small                    161314.6        1016.4       111.8
    9 | GPT-2 Medium                   161326.4        1004.6       129.0
   10 | GPT-2 XL                       161444.9         886.2       136.9
   11 | Pythia-410M                    161341.1         990.0       125.6
   12 | all four together              161273.4        1057.6       116.8
   13 | 
   14 | ================================================================================
   15 | READING
   16 | ================================================================================
   17 |   best single RT-predicting surprisal: GPT-2 Small
   18 |   If GPT-2 Small is best, the scaling paradox is present in this corpus,
   19 |   and a rise in dAIC(TEE) under larger-model surprisal reflects a WEAKER
   20 |   control, not a stronger one. The union spec is then the honest one:
   21 |   it contains the best single predictor plus the others.
```


==============================================================================
### FILE: gp_confound_check/ns_bigsurp_refit_out.txt
==============================================================================

```
    1 | sample hash 8a6087341e verified   words 9,840
    2 |   merged surprisal_gpt2_medium: 9,840 non-missing
    3 |   merged surprisal_gpt2_xl: 9,840 non-missing
    4 |   merged surprisal_pythia410m: 9,840 non-missing
    5 | 
    6 | word-level agreement between surprisal estimates:
    7 |   r(surprisal, surprisal_gpt2_medium) = +0.946
    8 |   r(surprisal, surprisal_gpt2_xl) = +0.899
    9 |   r(surprisal, surprisal_pythia410m) = +0.927
   10 |   r(surprisal_gpt2_medium, surprisal_gpt2_xl) = +0.946
   11 |   r(surprisal_gpt2_medium, surprisal_pythia410m) = +0.950
   12 |   r(surprisal_gpt2_xl, surprisal_pythia410m) = +0.940
   13 | 
   14 | mean surprisal (bits) and correlation with TEE:
   15 |   GPT-2 Small    mean  3.728   r(TEE, surp) = +0.310
   16 |   GPT-2 Medium   mean  3.422   r(TEE, surp) = +0.271
   17 |   GPT-2 XL       mean  3.160   r(TEE, surp) = +0.254
   18 |   Pythia-410M    mean  4.826   r(TEE, surp) = +0.275
   19 | 
   20 | MATCHED SAMPLE (all surprisals non-missing): n = 812,730   participants = 178
   21 | 
   22 | ==================================================================================
   23 | POOLED: dAIC and beta for TEE under each surprisal control
   24 | ==================================================================================
   25 | spec                                 dAIC(TEE)       beta            p
   26 | N0  GPT-2 Small surprisal [ref]          111.8    0.00354     1.42e-26
   27 | N1  GPT-2 Medium surprisal               129.0    0.00378     2.49e-30
   28 | N2  GPT-2 XL surprisal                   136.9    0.00390     4.69e-32
   29 | N3  all three GPT-2 surprisals           117.9    0.00363     6.66e-28
   30 | N4  N3, GPT-2 XL splined df=5            124.3    0.00374     2.58e-29
   31 | N5  Pythia-410M surprisal                125.6    0.00374     1.34e-29
   32 | N6  all four surprisals                  116.8    0.00362     1.15e-27
   33 | N7  all four, XL+Pythia splined df=4       125.2    0.00375     1.65e-29
   34 | 
   35 | ==================================================================================
   36 | SUBJECT-LEVEL: per-participant TEE coefficient
   37 | ==================================================================================
   38 | spec                                   n   mean beta   % pos   Wilcoxon p
   39 | N0  GPT-2 Small surprisal [ref]      171    +0.01277   73.1%     4.59e-12
   40 | N2  GPT-2 XL surprisal               171    +0.01387   75.4%     1.62e-13
   41 | N5  Pythia-410M surprisal            171    +0.01339   74.3%     8.84e-13
   42 | N6  all four surprisals              171    +0.01303   75.4%     2.28e-12
   43 | F   permuted TEE (floor)             171    +0.00035   55.0%     2.96e-01
```


==============================================================================
### FILE: gp_confound_check/ns_final_numbers_out.txt
==============================================================================

```
    1 | ============================================================================
    2 | HEADLINE MODEL (repaired frequency)
    3 | ============================================================================
    4 |   n = 812,730   participants = 178
    5 |   dAIC(TEE)            = 78.4
    6 |   beta(TEE)            = +0.00298  p = 3.11e-19
    7 |   beta(surprisal)      = +0.01032
    8 |   beta(log frequency)  = +0.00452
    9 |   beta(word length)    = +0.01340
   10 |   ratio TEE/surprisal  = 0.29
   11 | 
   12 | ============================================================================
   13 | SUBJECT-LEVEL (repaired frequency)
   14 | ============================================================================
   15 |   participants with sufficient data : 171
   16 |   positive coefficients             : 115 (67.3%)
   17 |   mean per-participant coefficient  : +0.01095
   18 |   sign test p                       : 7.55e-06
   19 |   Wilcoxon p                        : 2.43e-09
   20 |   t(170)                          : 6.74
   21 |   individually significant, positive: 32
   22 | 
   23 | ============================================================================
   24 | PYTHIA CROSS-ARCHITECTURE (repaired frequency, matched sample)
   25 | ============================================================================
   26 |   n = 812,730   participants = 178
   27 |   GPT-2 Small    dAIC    78.4   beta +0.00298   p 3.11e-19
   28 |   Pythia-160M    dAIC    88.3   beta +0.00289   p 2.01e-21
   29 |   Pythia-410M    dAIC   400.2   beta +0.00654   p 1.71e-89
```


==============================================================================
### FILE: gp_confound_check/ns_freq_repair_out.txt
==============================================================================

```
    1 | locked sample 8a6087341e   9,840 words
    2 |   old log_freq  : zeros 1,937 (19.7%)  mean 2.761
    3 |   repaired      : zeros 7 (0.1%)  mean 5.792
    4 |   r(old, repaired) = +0.8367
    5 |   r(TEE, old)      = -0.4381
    6 |   r(TEE, repaired) = -0.4403
    7 |   r(surprisal, old)      = -0.5361
    8 |   r(surprisal, repaired) = -0.5329
    9 | 
   10 | n = 812,730   participants = 178
   11 | 
   12 | ================================================================================
   13 | H1  POOLED HEADLINE: dAIC and beta for the trajectory term
   14 | ================================================================================
   15 | frequency control                dAIC(TEE)   beta(TEE)           p
   16 | old log_freq (as published)          111.8     0.00354    1.42e-26
   17 | repaired log_freq                     78.4     0.00298    3.11e-19
   18 | both frequencies                     109.6     0.00354    4.29e-26
   19 | 
   20 | ================================================================================
   21 | H2  SUBJECT-LEVEL
   22 | ================================================================================
   23 | frequency control                    beta   % positive           p
   24 | old log_freq (as published)      +0.01277       73.1%    4.59e-12
   25 | repaired log_freq                +0.01095       67.3%    2.43e-09
   26 | both frequencies                 +0.01274       71.9%    9.57e-12
   27 | 
   28 | ================================================================================
   29 | H4  THE FREQUENCY COEFFICIENT ITSELF (subject-level)
   30 | ================================================================================
   31 |   old log_freq         alone -0.0343 | +length +0.0050 | full model +0.0223
   32 |   repaired log_freq    alone -0.0410 | +length -0.0043 | full model +0.0142
```


==============================================================================
### FILE: gp_confound_check/ns_pos_output.txt
==============================================================================

```
    1 | by sentence position:
    2 |   pos    0-2 n= 100705 beta=-0.00267 p=2.16e-02
    3 |   pos    3-5 n= 100948 beta=+0.00307 p=9.80e-04
    4 |   pos   6-10 n= 157927 beta=+0.00526 p=6.56e-14
    5 |   pos  11-20 n= 253602 beta=+0.00331 p=7.02e-09
    6 |   pos    21+ n= 200439 beta=+0.00804 p=9.63e-33
    7 | interaction chi2(4)=220.8 p=1.25e-46
```


==============================================================================
### FILE: gp_confound_check/ns_pythia_surp_out.txt
==============================================================================

```
    1 | corpus: 10,256 words, 10 stories
    2 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    3 | 
    4 | Loading weights:   0%|          | 0/292 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 292/292 [00:00<00:00, 19057.60it/s]
    6 | loaded EleutherAI/pythia-410m on mps
    7 |   story 1: 1,073 words -> 1,072 scored
    8 |   story 2: 990 words -> 989 scored
    9 |   story 3: 1,040 words -> 1,039 scored
   10 |   story 4: 1,085 words -> 1,084 scored
   11 |   story 5: 1,013 words -> 1,012 scored
   12 |   story 6: 1,099 words -> 1,098 scored
   13 |   story 7: 999 words -> 998 scored
   14 |   story 8: 980 words -> 979 scored
   15 |   story 9: 1,038 words -> 1,037 scored
   16 |   story 10: 939 words -> 938 scored
   17 | 
   18 | total scored words: 10,246
   19 | locked sample hash 8a6087341e verified (9,840 words)
   20 | coverage: 9,840/9,840 sample words scored (0 missing)
   21 | 
   22 | agreement with existing surprisal estimates on the sample:
   23 |   r(pythia410m, surprisal             ) = +0.927
   24 |   r(pythia410m, surprisal_gpt2_medium ) = +0.950
   25 |   r(pythia410m, surprisal_gpt2_xl     ) = +0.940
   26 | 
   27 | mean surprisal (bits): small 3.728  medium 3.422  xl 3.160  pythia410m 4.826
   28 | r(TEE, pythia410m surprisal) = +0.275   [small +0.310, medium +0.271, xl +0.254]
   29 | 
   30 | saved -> /Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv
```


==============================================================================
### FILE: gp_confound_check/ns_reconcile.txt
==============================================================================

```
    1 | words.tsv rows: 32351 | locked sample words: 9840 | coverage 30.4%
    2 | RT rows after filter: 848875
    3 | RT rows matching locked-sample words: 813621
    4 | 
    5 | LOCKED SAMPLE: N=812730  M1 AIC=161314.6  M2 AIC=161202.8  dAIC=111.8  beta=+0.00354
    6 | PAPER (ns_crossed_re_results.csv): M1 AIC=189030.9  M2 AIC=189028.4  dAIC=2.5  beta=+0.00063
    7 | 
    8 | implied N of paper analysis, scaling by AIC-per-observation: 952369
```


==============================================================================
### FILE: gp_confound_check/ns_rerun_all_out.txt
==============================================================================

```
    1 | n = 812,730  participants = 178
    2 | 
    3 | ====================================================================================
    4 | R1  STRONGER SURPRISAL CONTROLS
    5 | ====================================================================================
    6 | surprisal control              dAIC old   dAIC new   beta new
    7 | GPT-2 Small                       111.8       78.4    0.00298
    8 | GPT-2 Medium                      129.0       90.7    0.00319
    9 | GPT-2 XL                          136.9       95.7    0.00328
   10 | Pythia-410M                       125.6       87.9    0.00314
   11 | all four                          116.8       82.1    0.00305
   12 | 
   13 | ====================================================================================
   14 | R2  DISPLACEMENT CONTROL
   15 | ====================================================================================
   16 |   n = 812,730
   17 |   old log_freq     TEE alone +0.00354 | disp alone +0.00315 | joint TEE +0.00287 (p=8.9e-09) | joint disp +0.00092 (p=0.075)
   18 |   repaired         TEE alone +0.00298 | disp alone +0.00205 | joint TEE +0.00333 (p=2.8e-11) | joint disp -0.00047 (p=0.351)
   19 | 
   20 | ====================================================================================
   21 | R3  WORD-IDENTITY CONTROL (centred within word type, >=5 occurrences)
   22 | ====================================================================================
   23 |   2,919 word types, n = 812,730
   24 | Traceback (most recent call last):
   25 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/ns_rerun_all_fixedfreq.py", line 155, in <module>
   26 |     a, b_, p_ = daic(Wc.assign(participant=Wc.participant), f, "c_tee_k3")
   27 |                 ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   28 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/ns_rerun_all_fixedfreq.py", line 96, in daic
   29 |     m0 = smf.mixedlm(base, frame, groups=frame.participant).fit(
   30 |         reml=False, method="lbfgs")
   31 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/regression/mixed_linear_model.py", line 2191, in fit
   32 |     rslt = super().fit(start_params=packed,
   33 |                        skip_hessian=True,
   34 |                        method=method[j],
   35 |                        **fit_kwargs)
   36 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/base/model.py", line 566, in fit
   37 |     xopt, retvals, optim_settings = optimizer._fit(f, score, start_params,
   38 |                                     ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
   39 |                                                    fargs, kwargs,
   40 |                                                    ^^^^^^^^^^^^^^
   41 |     ...<5 lines>...
   42 |                                                    retall=retall,
   43 |                                                    ^^^^^^^^^^^^^^
   44 |                                                    full_output=full_output)
   45 |                                                    ^^^^^^^^^^^^^^^^^^^^^^^^
   46 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/base/optimizer.py", line 245, in _fit
   47 |     xopt, retvals = func(objective, gradient, start_params, fargs, kwargs,
   48 |                     ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   49 |                          disp=disp, maxiter=maxiter, callback=callback,
   50 |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   51 |                          retall=retall, full_output=full_output,
   52 |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   53 |                          hess=hessian)
   54 |                          ^^^^^^^^^^^^^
   55 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/base/optimizer.py", line 665, in _fit_lbfgs
   56 |     retvals = optimize.fmin_l_bfgs_b(
   57 |         func,
   58 |     ...<5 lines>...
   59 |         **extended_kwargs
   60 |     )
   61 |   File "/opt/homebrew/lib/python3.14/site-packages/scipy/optimize/_lbfgsb_py.py", line 281, in fmin_l_bfgs_b
   62 |     res = _minimize_lbfgsb(fun, x0, args=args, jac=jac, bounds=bounds,
   63 |                            **opts)
   64 |   File "/opt/homebrew/lib/python3.14/site-packages/scipy/optimize/_lbfgsb_py.py", line 413, in _minimize_lbfgsb
   65 |     sf = _prepare_scalar_function(fun, x0, jac=jac, args=args, epsilon=eps,
   66 |                                   bounds=bounds,
   67 |                                   finite_diff_rel_step=finite_diff_rel_step,
   68 |                                   workers=workers)
   69 |   File "/opt/homebrew/lib/python3.14/site-packages/scipy/optimize/_optimize.py", line 310, in _prepare_scalar_function
   70 |     sf = ScalarFunction(fun, x0, args, grad, hess,
   71 |                         finite_diff_rel_step, bounds, epsilon=epsilon,
   72 |                         workers=workers)
   73 |   File "/opt/homebrew/lib/python3.14/site-packages/scipy/optimize/_differentiable_functions.py", line 283, in __init__
   74 |     self._update_fun()
   75 |     ~~~~~~~~~~~~~~~~^^
   76 |   File "/opt/homebrew/lib/python3.14/site-packages/scipy/optimize/_differentiable_functions.py", line 362, in _update_fun
   77 |     fx = self._wrapped_fun(self.x)
   78 |   File "/opt/homebrew/lib/python3.14/site-packages/scipy/_lib/_util.py", line 603, in __call__
   79 |     fx = self.f(np.copy(x), *self.args)
   80 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/base/model.py", line 534, in f
   81 |     return -self.loglike(params, *args) / nobs
   82 |             ~~~~~~~~~~~~^^^^^^^^^^^^^^^
   83 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/regression/mixed_linear_model.py", line 1498, in loglike
   84 |     fe_params, sing = self.get_fe_params(cov_re, vcomp)
   85 |                       ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
   86 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/regression/mixed_linear_model.py", line 1345, in get_fe_params
   87 |     fe_params = np.linalg.solve(xtxy[:, 0:-1], xtxy[:, -1])
   88 |   File "/opt/homebrew/lib/python3.14/site-packages/numpy/linalg/_linalg.py", line 452, in solve
   89 |     r = gufunc(a, b, signature=signature)
   90 |   File "/opt/homebrew/lib/python3.14/site-packages/numpy/linalg/_linalg.py", line 145, in _raise_linalgerror_singular
   91 |     raise LinAlgError("Singular matrix")
   92 | numpy.linalg.LinAlgError: Singular matrix
```


==============================================================================
### FILE: gp_confound_check/ns_rerun_part2_out.txt
==============================================================================

```
    1 | n = 812,730  participants = 178
    2 | 
    3 | ====================================================================================
    4 | R3  WORD-IDENTITY CONTROL
    5 | ====================================================================================
    6 |   2,919 word types, n = 812,730
    7 |   word length and log frequency are constant within word type, so they
    8 |   are necessarily absent from this model; the repair cannot affect it.
    9 |   dAIC 23.1   beta +0.00021   p 5.31e-07   (published: dAIC 23.1, beta +0.0022, p 5.3e-7)
   10 | 
   11 | ====================================================================================
   12 | R4  PUNCTUATION
   13 | ====================================================================================
   14 |   old log_freq     +punct covariate dAIC   115.4  |  punct-free dAIC   138.3 (beta +0.00409, n=716,641)
   15 |   repaired         +punct covariate dAIC    70.0  |  punct-free dAIC   114.9 (beta +0.00376, n=716,641)
   16 | 
   17 | ====================================================================================
   18 | R5  PYTHIA CROSS-ARCHITECTURE, MATCHED SAMPLE
   19 | ====================================================================================
   20 |   n = 812,730  participants = 178
   21 |   frequency          GPT-2 Small   Pythia-160M   Pythia-410M
   22 |   old log_freq             111.8         115.5         487.6
   23 |   repaired                  78.4          88.3         400.2
   24 | 
   25 | ====================================================================================
   26 | R7  FIGURE 2 COEFFICIENTS (subject-level unique contribution)
   27 | ====================================================================================
   28 |   old       tee_k3         +0.01277 (73%) | surprisal      +0.03627 (87%) | log_freq       +0.02229 (77%)
   29 |   repaired  tee_k3         +0.01095 (67%) | surprisal      +0.03416 (86%) | log_freq_fixed +0.01422 (71%)
```


==============================================================================
### FILE: gp_confound_check/ns_robustness_output.txt
==============================================================================

```
    1 | punct-final words in sample: 11.8% of observations
    2 | 
    3 | ================================================================================================
    4 | 1. PUNCTUATION
    5 | ================================================================================================
    6 | headline (no punctuation control)           n= 812,730  dAIC=   111.8  beta=+0.00354  p=1.42e-26
    7 | + punctuation covariate                     n= 812,730  dAIC=   115.4  beta=+0.00359  p=2.36e-27
    8 | punctuation-free words only                 n= 716,641  dAIC=   138.3  beta=+0.00411  p=2.25e-32
    9 | 
   10 | ================================================================================================
   11 | 2. LEXICAL BASELINE (does TEE predict RT for the SAME word across contexts?)
   12 | ================================================================================================
   13 | word types retained (>=5 occurrences): 2,919
   14 | word-identity demeaned                      n= 812,730  dAIC=    23.1  beta=+0.00218  p=5.31e-07
   15 | 
   16 | ================================================================================================
   17 | 3. BOTH (punctuation-free AND word-identity demeaned)
   18 | ================================================================================================
   19 | punct-free + word-identity demeaned         n= 716,641  dAIC=    23.7  beta=+0.00220  p=4.05e-07
```


==============================================================================
### FILE: gp_confound_check/onestop_ctx_log.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | 
    3 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    4 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 10734.73it/s]
    5 |   10/21 documents
    6 |   20/21 documents
    7 | 
    8 | n = 16,162
    9 | r(OneStop surprisal, mine ISOLATED)        = 0.8017
   10 | r(OneStop surprisal, mine ARTICLE CONTEXT) = 0.8121
   11 | r(TEE isolated, TEE article-context)       = 0.9881
   12 | 
   13 | by position within paragraph:
   14 |      0-9  n= 1,280  r(iso)=0.811   r(ctx)=0.780
   15 |    10-29  n= 2,560  r(iso)=0.862   r(ctx)=0.856
   16 |    30-59  n= 3,840  r(iso)=0.843   r(ctx)=0.887
   17 |      60+  n= 8,482  r(iso)=0.764   r(ctx)=0.789
```


==============================================================================
### FILE: gp_confound_check/onestop_final.txt
==============================================================================

```
    1 | ==== FFD ====
    2 |   mine: own surprisal + isolated TEE           n=180 pos= 91/180 mean b=-0.00029 Wilcoxon p=6.95e-01
    3 |   theirs: OneStop surprisal + isolated TEE     n=180 pos= 98/180 mean b=+0.00030 Wilcoxon p=5.75e-01
    4 |   theirs: OneStop surprisal + CONTEXT TEE      n=180 pos=101/180 mean b=+0.00061 Wilcoxon p=2.71e-01
    5 | 
    6 | ==== GD ====
    7 |   mine: own surprisal + isolated TEE           n=180 pos= 75/180 mean b=-0.00230 Wilcoxon p=1.56e-02
    8 |   theirs: OneStop surprisal + isolated TEE     n=180 pos= 92/180 mean b=-0.00108 Wilcoxon p=3.52e-01
    9 |   theirs: OneStop surprisal + CONTEXT TEE      n=180 pos= 91/180 mean b=-0.00058 Wilcoxon p=7.05e-01
   10 | 
   11 | ==== TRT ====
   12 |   mine: own surprisal + isolated TEE           n=180 pos= 65/180 mean b=-0.00522 Wilcoxon p=1.10e-06
   13 |   theirs: OneStop surprisal + isolated TEE     n=180 pos= 76/180 mean b=-0.00295 Wilcoxon p=4.18e-03
   14 |   theirs: OneStop surprisal + CONTEXT TEE      n=180 pos= 79/180 mean b=-0.00225 Wilcoxon p=2.86e-02
   15 | 
```


==============================================================================
### FILE: gp_confound_check/onestop_geometry_out.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | 
    3 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    4 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 8093.10it/s]
    5 |   10/21 documents
    6 |   20/21 documents
    7 | 
    8 | wrote onestop_geometry.csv  (16,162 rows, 16,078 with defined geometry)
    9 | 
   10 | SANITY vs onestop_tee_ctx.csv:  n = 16,078   r = 1.0000000000   max|diff| = 1.42e-14
   11 | 
   12 | component correlations (word level):
   13 |               tee  slope_norm  curv_prev  runup_disp  last_step  resid_par  resid_perp
   14 | tee         1.000       0.616     -0.347       0.616      0.338     -0.847       0.560
   15 | slope_norm  0.616       1.000     -0.604       1.000      0.401     -0.734       0.049
   16 | curv_prev  -0.347      -0.604      1.000      -0.604      0.294      0.400      -0.050
   17 | runup_disp  0.616       1.000     -0.604       1.000      0.401     -0.734       0.049
   18 | last_step   0.338       0.401      0.294       0.401      1.000     -0.433      -0.033
   19 | resid_par  -0.847      -0.734      0.400      -0.734     -0.433      1.000      -0.042
   20 | resid_perp  0.560       0.049     -0.050       0.049     -0.033     -0.042       1.000
   21 | 
   22 |   note: slope_norm and curv_prev should be strongly negatively
   23 |   related if the geometric mechanism is as described (a bent run-up
   24 |   produces a short fitted step).
```


==============================================================================
### FILE: gp_confound_check/onestop_geometry_test_out.txt
==============================================================================

```
    1 | rows 1,104,883   participants 180
    2 | mean P(skip) = 0.357
    3 | 
    4 | ========================================================================================
    5 | OUTCOME: P(skip)          [* = p<.01 and >=65% sign agreement]
    6 | ========================================================================================
    7 | 
    8 |   G1  the reported effect
    9 |     tee                                    beta= +0.00803  66.1% pos  p=4.58e-08    *
   10 | 
   11 |   G2  run-up geometry only (pre-fixation information)
   12 |     slope_norm                             beta= +0.00660  62.2% pos  p=9.43e-06
   13 |     curv_prev                              beta= +0.00328  56.1% pos  p=3.60e-02
   14 | 
   15 |   G3  target deviation only (post-fixation information)
   16 |     resid_perp                             beta= -0.00906  28.9% pos  p=3.21e-10    *
   17 |     resid_par                              beta= -0.01374  27.2% pos  p=5.94e-15    *
   18 | 
   19 |   G4  head to head, all four entered
   20 |     slope_norm                             beta= -0.00933  36.7% pos  p=1.07e-06
   21 |     curv_prev                              beta= +0.00193  53.3% pos  p=2.30e-01
   22 |     resid_perp                             beta= -0.00896  28.9% pos  p=4.19e-10    *
   23 |     resid_par                              beta= -0.02156  21.1% pos  p=1.09e-18    *
   24 | 
   25 |   G5  G4 + previous-word length, frequency, surprisal
   26 |     slope_norm                             beta= -0.00713  38.3% pos  p=1.43e-04
   27 |     curv_prev                              beta= +0.00146  53.3% pos  p=2.60e-01
   28 |     resid_perp                             beta= -0.00580  38.3% pos  p=4.56e-05
   29 |     resid_par                              beta= -0.00732  41.1% pos  p=4.83e-04
   30 | 
   31 | ========================================================================================
   32 | OUTCOME: first fixation duration (contrast)
   33 | ========================================================================================
   34 |     slope_norm                             beta= +0.00232  55.0% pos  p=1.52e-01
   35 |     curv_prev                              beta= -0.00143  47.8% pos  p=4.72e-01
   36 |     resid_perp                             beta= +0.00279  60.6% pos  p=2.91e-02
   37 |     resid_par                              beta= +0.00583  57.2% pos  p=3.79e-03
   38 | 
   39 | ========================================================================================
   40 | READING
   41 | ========================================================================================
   42 |   Run-up terms surviving in G4/G5 -> the skipping effect is about the
   43 |   coherence of the preceding context, which the reader has already read. The
   44 |   timing objection to the skipping result dissolves, and the measure's
   45 |   behavioural signature in free reading is not about the target word at all.
   46 | 
   47 |   resid_perp surviving instead -> the reader is responding to the target word,
   48 |   and how they could do so before fixating it remains to be explained.
```


==============================================================================
### FILE: gp_confound_check/onestop_gopast.txt
==============================================================================

```
    1 | PREDICTION: if TEE triggers regressions, go-past time should be POSITIVE
    2 | (go-past = first fixation on word until eyes move PAST it, incl. re-reading)
    3 | 
    4 |   regression-path (go-past) duration ~ TEE             n=180 pos= 95/180 mean b=+0.00122 Wilcoxon p=2.92e-01
    5 |   selective regression-path duration ~ TEE             n=180 pos= 84/180 mean b=-0.00104 Wilcoxon p=2.41e-01
    6 |   first-run dwell (gaze) ~ TEE                         n=180 pos= 91/180 mean b=-0.00058 Wilcoxon p=7.05e-01
    7 |   total reading time ~ TEE                             n=180 pos= 79/180 mean b=-0.00225 Wilcoxon p=2.86e-02
    8 | 
    9 |   regression-path duration ~ surprisal                 n=180 pos=152/180 mean b=+0.01334 Wilcoxon p=1.42e-22
```


==============================================================================
### FILE: gp_confound_check/onestop_mechanism.txt
==============================================================================

```
    1 | === IS THE PARADIGM ASYMMETRY SPECIFIC TO TEE? ===
    2 | (same spec; focus predictor swapped)
    3 |   TRT ~ ... + TEE                                n=180 pos= 79/180 mean b=-0.00225 Wilcoxon p=2.86e-02
    4 |   TRT ~ ... + surprisal                          n=180 pos=178/180 mean b=+0.03130 Wilcoxon p=2.88e-31
    5 | 
    6 | === EYE-MOVEMENT-SPECIFIC BEHAVIOURS (no self-paced analogue) ===
    7 |   P(skip) ~ ... + TEE                            n=180 pos= 88/180 mean b=-0.00256 Wilcoxon p=4.70e-01
    8 |   P(skip) ~ ... + surprisal                      n=157 pos= 26/157 mean b=-0.03152 Wilcoxon p=1.38e-20
    9 |   P(regress out) ~ ... + TEE                     n=180 pos=111/180 mean b=+0.01653 Wilcoxon p=3.39e-05
   10 |   P(regress in) ~ ... + TEE                      n=180 pos= 78/180 mean b=-0.01018 Wilcoxon p=9.17e-03
   11 |   run count ~ ... + TEE                          n=180 pos= 88/180 mean b=-0.00116 Wilcoxon p=9.87e-02
```


==============================================================================
### FILE: gp_confound_check/onestop_negative_probe_out.txt
==============================================================================

```
    1 | columns available: ['IA_DWELL_TIME', 'word_length', 'wordfreq_frequency', 'gpt2_surprisal', 'IA_FIRST_FIXATION_DURATION', 'IA_FIRST_RUN_DWELL_TIME', 'IA_FIXATION_COUNT', 'IA_SKIP', 'IA_FIRST_RUN_FIXATION_COUNT']
    2 | rows 1,104,883   participants 180
    3 | 
    4 | ========================================================================================
    5 | DECOMPOSING THE NEGATIVE
    6 | ========================================================================================
    7 | 
    8 |   [1] does TEE predict SKIPPING?  (all rows, incl. unfixated)
    9 |   P(skip)                            n= 180  beta= +0.00803  66.1% pos  p=4.58e-08   <- positive = high TEE skipped more
   10 | 
   11 |   [2-4] durations, conditional on being fixated
   12 |   first fixation duration            n= 180  beta= -0.00199  49.4% pos  p=3.96e-01
   13 |   gaze duration (first pass)         n= 180  beta= -0.00536  46.1% pos  p=1.17e-02
   14 |   total reading time                 n= 180  beta= -0.00515  41.1% pos  p=3.16e-03   <- the reported negative
   15 | 
   16 |   [5-6] the part of TRT that is not first pass
   17 |   P(any re-reading)                  n= 180  beta= -0.00002  53.3% pos  p=9.67e-01
   18 |   log re-reading time | any          n= 179  beta= -0.00259  44.7% pos  p=3.48e-01
   19 |   P(refixation in first pass)        n= 180  beta= -0.00590  42.2% pos  p=6.07e-04
   20 |   fixation count                     n= 180  beta= -0.00528  38.9% pos  p=7.56e-04
   21 | 
   22 | ========================================================================================
   23 | READING
   24 | ========================================================================================
   25 |   If the negative is concentrated in skipping, re-reading, or fixation
   26 |   count, it reflects where the eyes go rather than how fast a word is read,
   27 |   and total reading time is the wrong summary statistic for this measure.
   28 |   If first fixation and gaze duration are also negative, it is a genuine
   29 |   speed-up and the Discussion owes an account of it.
```


==============================================================================
### FILE: gp_confound_check/onestop_oculo.txt
==============================================================================

```
    1 | correlations with TEE:
    2 |    r(tee, x_in_line      ) = -0.0012
    3 |    r(tee, is_line_final  ) = +0.0094
    4 |    r(tee, is_line_initial) = +0.0008
    5 |    r(tee, line           ) = -0.0103
    6 |    r(tee, word_length    ) = +0.1202
    7 |    P(regress) by line position: initial 0.056  medial 0.182  final 0.264
    8 | 
    9 | === P(regression out) ~ TEE, adding oculomotor controls ===
   10 |   linguistic controls only (as before)           n=180 pos=111/180 b=+0.0165 sign p=0.002 Wilcoxon p=3.39e-05
   11 |   + line position / x-in-line                    n=180 pos=111/180 b=+0.0153 sign p=0.002 Wilcoxon p=1.04e-04
   12 |   + launch site & landing position               n=180 pos=109/180 b=+0.0162 sign p=0.006 Wilcoxon p=6.57e-05
   13 | 
   14 | === excluding line-final and line-initial words entirely ===
   15 |   line-medial words only, full controls          too few
```


==============================================================================
### FILE: gp_confound_check/onestop_oculo2.txt
==============================================================================

```
    1 | line-medial words: 957902 of 1104883 rows
    2 |   line-medial only, linguistic controls          n=180 pos= 99/180 b=+0.0080 sign p=0.2050 Wilcoxon p=3.11e-02
    3 |   line-medial only, + x_in_line + line           n=180 pos= 97/180 b=+0.0079 sign p=0.3326 Wilcoxon p=3.78e-02
```


==============================================================================
### FILE: gp_confound_check/onestop_prevctrl.txt
==============================================================================

```
    1 | ==== DV = FFD ====
    2 |   A first-pass spec (no prev terms)    n=180  pos= 76/180  mean b=-0.00199  Wilcoxon p=5.02e-03
    3 |   B + prev word length/freq/surp       n=180  pos= 83/180  mean b=-0.00069  Wilcoxon p=2.50e-01
    4 |   C + prev terms + prev dwell          n=180  pos= 85/180  mean b=-0.00057  Wilcoxon p=3.32e-01
    5 |   D + prev TEE (spillover)             n=180  pos= 84/180  mean b=-0.00015  Wilcoxon p=6.71e-01
    6 | 
    7 | ==== DV = GD ====
    8 |   A first-pass spec (no prev terms)    n=180  pos= 70/180  mean b=-0.00421  Wilcoxon p=4.06e-06
    9 |   B + prev word length/freq/surp       n=180  pos= 76/180  mean b=-0.00292  Wilcoxon p=1.77e-03
   10 |   C + prev terms + prev dwell          n=180  pos= 77/180  mean b=-0.00272  Wilcoxon p=3.15e-03
   11 |   D + prev TEE (spillover)             n=180  pos= 78/180  mean b=-0.00248  Wilcoxon p=1.10e-02
   12 | 
   13 | ==== DV = TRT ====
   14 |   A first-pass spec (no prev terms)    n=180  pos= 54/180  mean b=-0.00601  Wilcoxon p=1.49e-08
   15 |   B + prev word length/freq/surp       n=180  pos= 58/180  mean b=-0.00584  Wilcoxon p=1.21e-07
   16 |   C + prev terms + prev dwell          n=180  pos= 58/180  mean b=-0.00620  Wilcoxon p=2.06e-08
   17 |   D + prev TEE (spillover)             n=180  pos= 57/180  mean b=-0.00646  Wilcoxon p=3.59e-08
   18 | 
```


==============================================================================
### FILE: gp_confound_check/onestop_regress.txt
==============================================================================

```
    1 | === how special is TEE for regressions? ===
    2 |   P(regress out) ~ TEE                               n=180 pos=111/180 b=+0.01653 p=3.39e-05
    3 |   P(regress out) ~ surprisal                         n=172 pos= 85/172 b=-0.00331 p=2.21e-01
    4 | 
    5 | === robustness of the TEE regression effect ===
    6 |   punctuation-free words only                        n=180 pos=109/180 b=+0.01888 p=1.85e-05
    7 |   beyond word 10 of paragraph                        n=180 pos=115/180 b=+0.02264 p=1.92e-07
    8 |   regression-out COUNT (not binary)                  n=180 pos= 85/180 b=-0.00086 p=1.23e-01
    9 | 
   10 | === go-past CONDITIONAL on a regression having occurred ===
   11 |   go-past | regressed out                            n=180 pos= 84/180 b=-0.00509 p=9.87e-02
   12 |   go-past | no regression                            n=180 pos= 90/180 b=-0.00022 p=9.93e-01
```


==============================================================================
### FILE: gp_confound_check/onestop_results.txt
==============================================================================

```
    1 | rows=1,104,883  participants=180  words with TEE=1,064,571
    2 | 
    3 | ============================================================================================================
    4 | MAIN: TEE beyond length, frequency, surprisal (subject-level)
    5 | ============================================================================================================
    6 |   FFD  (full controls)                     n= 180  pos= 76/180  (42.2%)  mean b=-0.00199  Wilcoxon p=5.02e-03  t= -3.12  sig=26
    7 |   GD  (full controls)                      n= 180  pos= 70/180  (38.9%)  mean b=-0.00421  Wilcoxon p=4.06e-06  t= -5.34  sig=36
    8 |   TRT  (full controls)                     n= 180  pos= 54/180  (30.0%)  mean b=-0.00601  Wilcoxon p=1.49e-08  t= -6.28  sig=36
    9 | 
   10 | ============================================================================================================
   11 | ZuCo-style controls (length + frequency only), for direct comparison
   12 | ============================================================================================================
   13 |   FFD  (length+freq only)                  n= 180  pos= 80/180  (44.4%)  mean b=-0.00153  Wilcoxon p=3.15e-02  t= -2.50  sig=21
   14 |   GD  (length+freq only)                   n= 180  pos= 77/180  (42.8%)  mean b=-0.00330  Wilcoxon p=2.43e-04  t= -4.34  sig=37
   15 |   TRT  (length+freq only)                  n= 180  pos= 61/180  (33.9%)  mean b=-0.00423  Wilcoxon p=1.68e-05  t= -4.62  sig=30
   16 | 
   17 | ============================================================================================================
   18 | PUNCTUATION-FREE (word not punctuation-final)
   19 | ============================================================================================================
   20 |   FFD  (punct-free)                        n= 180  pos= 84/180  (46.7%)  mean b=-0.00071  Wilcoxon p=2.54e-01  t= -1.02  sig=18
   21 |   GD  (punct-free)                         n= 180  pos= 80/180  (44.4%)  mean b=-0.00230  Wilcoxon p=1.10e-02  t= -2.79  sig=31
   22 |   TRT  (punct-free)                        n= 180  pos= 67/180  (37.2%)  mean b=-0.00347  Wilcoxon p=3.03e-04  t= -3.47  sig=29
   23 | 
   24 | ============================================================================================================
   25 | POSITION BOUNDARY CONDITION (predicted: null early, present later)
   26 | ============================================================================================================
   27 |   -- FFD --
   28 |   first 5 words of sentence                n= 180  pos= 89/180  (49.4%)  mean b=+0.00008  Wilcoxon p=8.13e-01  t=  0.07  sig=8
   29 |   beyond word 10                           n= 180  pos= 73/180  (40.6%)  mean b=-0.00290  Wilcoxon p=1.14e-03  t= -3.55  sig=19
   30 |   -- GD --
   31 |   first 5 words of sentence                n= 180  pos= 87/180  (48.3%)  mean b=-0.00155  Wilcoxon p=4.03e-01  t= -1.19  sig=13
   32 |   beyond word 10                           n= 180  pos= 72/180  (40.0%)  mean b=-0.00520  Wilcoxon p=2.70e-06  t= -5.34  sig=31
   33 |   -- TRT --
   34 |   first 5 words of sentence                n= 180  pos= 83/180  (46.1%)  mean b=-0.00160  Wilcoxon p=2.81e-01  t= -1.04  sig=9
   35 |   beyond word 10                           n= 180  pos= 63/180  (35.0%)  mean b=-0.00743  Wilcoxon p=6.52e-08  t= -5.98  sig=23
```


==============================================================================
### FILE: gp_confound_check/onestop_runup_probe_out.txt
==============================================================================

```
    1 | rows 1,104,883   participants 180
    2 | mean P(skip) = 0.357
    3 | r(tee(t), tee(t-1)) = +0.248   r(tee(t), log_freq) = +0.179   r(tee(t), word_length) = +0.120
    4 | r(tee(t-1), len(t-1)) = +0.117
    5 | 
    6 | ============================================================================================
    7 | OUTCOME: P(skip)
    8 | ============================================================================================
    9 |   S1  tee(t) alone                         n= 180  beta= +0.00803  66.1% pos  p=4.58e-08    *
   10 |   S2  tee(t-1) alone                       n= 180  beta= +0.01191  70.0% pos  p=1.76e-12    *
   11 |   S3  tee(t)   [both entered]              n= 180  beta= +0.00385  57.8% pos  p=1.84e-02
   12 |   S3  tee(t-1) [both entered]              n= 180  beta= +0.01094  70.0% pos  p=1.89e-10    *
   13 |   S4  tee(t-1) [t-1 and t-2]               n= 180  beta= +0.01367  72.8% pos  p=1.68e-13    *
   14 |   S4  tee(t-2) [t-1 and t-2]               n= 180  beta= -0.00730  32.2% pos  p=1.40e-09    *
   15 | 
   16 |   with previous-word lexical controls added (length, frequency, surprisal of t-1):
   17 |   S3b tee(t)   + prev lexical              n= 180  beta= -0.00244  44.4% pos  p=9.49e-02
   18 |   S3b tee(t-1) + prev lexical              n= 180  beta= +0.00393  60.0% pos  p=4.28e-03
   19 | 
   20 | ============================================================================================
   21 | OUTCOME: first fixation duration (for contrast)
   22 | ============================================================================================
   23 |   tee(t)                                   n= 180  beta= -0.00106  47.8% pos  p=5.49e-01
   24 |   tee(t-1)                                 n= 180  beta= -0.00575  36.7% pos  p=1.24e-04
   25 | 
   26 | ============================================================================================
   27 | READING
   28 | ============================================================================================
   29 |   tee(t-1) predicting skipping, and surviving alongside tee(t), supports the
   30 |   run-up account: the measure partly indexes how coherently the preceding
   31 |   context was moving, which is information the reader has before fixating.
   32 |   If tee(t-1) dies once previous-word length and frequency are controlled, the
   33 |   effect is launch-site lexical properties and the account is deflationary.
```


==============================================================================
### FILE: gp_confound_check/onestop_tee_log.txt
==============================================================================

```
    1 | reading interest-area report (label columns only)...
    2 |   1,104,883 rows
    3 |   128 unique paragraphs, 16,162 paragraph-word slots
    4 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    5 | 
    6 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    7 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 8841.18it/s]
    8 |   50/128 paragraphs
    9 |   100/128 paragraphs
   10 | 
   11 | DONE -> /Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/onestop_tee.csv
   12 |   16,162 paragraph-word rows; usable TEE: 15,650
   13 |   mean TEE 85.63  sd 11.05
```


==============================================================================
### FILE: gp_confound_check/preview_out.txt
==============================================================================

```
    1 | launch site: median 159.2  IQR 94.5-260.4  n=701233
    2 | line-initial words: 10.3%
    3 | 
    4 | === EXPLORATORY: preview x TEE ===
    5 |   TEE x launch-site interaction: n=180  beta=+0.00004  53.9% positive  p=0.783
    6 |   (positive = TEE effect stronger when preview was poor)
    7 |   line-initial (no preview)  n=180  beta=-0.00346  42.8% positive  p=0.314
    8 |   line-medial                n=180  beta=-0.00417  42.2% positive  p=0.014
    9 | 
   10 |   TEE effect by launch-distance quartile (longer = less preview):
   11 |     shortest  n=174  beta=+0.00562  54.6% positive  p=0.052
   12 |     2         n=180  beta=-0.00060  44.4% positive  p=0.328
   13 |     3         n=180  beta=-0.00418  47.8% positive  p=0.296
   14 |     longest   n=180  beta=-0.00866  37.2% positive  p=0.000
```


==============================================================================
### FILE: gp_confound_check/roi_signflip_output.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | [transformers] The following generation flags are not valid and may be ignored: ['output_hidden_states']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
    3 | 
    4 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 13690.85it/s]
    6 | device mps
    7 | 
    8 | ==========================================================================
    9 | 1. PER-ROI: TEE and surprisal coefficients (L6 w=3, isolated)
   10 | ==========================================================================
   11 |   ROI        n    beta TEE           p   beta surp           p
   12 |    -2   47,642     -0.0051    1.20e-02      0.0029    3.56e-02
   13 |    -1   47,645     -0.0054    2.33e-04     -0.0004    7.65e-01
   14 |     0   47,610     -0.0034    8.41e-02      0.0341    1.81e-65
   15 |     1   47,614     -0.0085    6.56e-05      0.0405    1.75e-79
   16 |     2   47,647      0.0102    5.48e-10     -0.0022    1.85e-01
   17 |     3   47,669      0.0207    2.37e-44      0.0125    2.25e-19
   18 | 
   19 | ==========================================================================
   20 | 2. ROI 0 by construction and by ambiguity
   21 | ==========================================================================
   22 |   construction MVRR     n= 15,847  beta= -0.0009  p=7.98e-01
   23 |   construction NPS      n= 15,876  beta= -0.0057  p=1.01e-01
   24 |   construction NPZ      n= 15,887  beta=  0.0080  p=5.33e-02
   25 |   AMBUAMB 0             n= 23,829  beta=  0.0041  p=1.12e-01
   26 |   AMBUAMB 1             n= 23,781  beta= -0.0057  p=6.07e-02
   27 | 
   28 | ==========================================================================
   29 | 3. Does a frequency control remove the ROI-0 flip?
   30 | ==========================================================================
   31 |   ROI 0: without freq  -0.0034 (p=8.4e-02)   with freq  -0.0032 (p=1.0e-01)
   32 |   ROI 1: without freq  -0.0085 (p=6.6e-05)   with freq  -0.0071 (p=1.3e-03)
   33 |   ROI 2: without freq   0.0102 (p=5.5e-10)   with freq   0.0060 (p=4.1e-04)
   34 | 
   35 | ==========================================================================
   36 | 4. What is TEE correlated with at each ROI? (word-level, n=144 sents)
   37 | ==========================================================================
   38 |   ROI   r(tee,len)  r(tee,freq)  r(tee,surp)  % punct-final  mean tee
   39 |    -2          nan       -0.000       -0.038          0.0%     469.5
   40 |    -1       -0.255       -0.442        0.115          0.0%      93.0
   41 |     0       -0.166       -0.207        0.416          0.0%      98.0
   42 |     1       -0.288        0.127        0.255          0.0%      89.6
   43 |     2        0.117       -0.245       -0.056          0.0%      96.6
   44 |     3        0.384       -0.368        0.341          0.0%      91.3
   45 | 
   46 | ==========================================================================
   47 | 5. Descriptive: mean logRT by TEE quintile, per ROI (raw, no controls)
   48 | ==========================================================================
   49 |   ROI 0: Q1 5.968  Q2 6.005  Q3 6.007  Q4 5.978  Q5 5.989
   50 |   ROI 1: Q1 6.091  Q2 6.085  Q3 6.099  Q4 6.060  Q5 6.087
   51 |   ROI 2: Q1 5.998  Q2 6.054  Q3 6.045  Q4 6.062  Q5 6.033
```


==============================================================================
### FILE: gp_confound_check/rt_dynamics_out.txt
==============================================================================

```
    1 | hash 8a6087341e verified | raw RT rows 848,875
    2 | after RT filter          848,875
    3 | after merge to measures  813,621
    4 | after lag construction   813,621
    5 | participants 178   words 1067
    6 | 
    7 | 
    8 | ==============================================================================
    9 | P1 (PRIMARY): impulse response of log RT to TEE, lags 0-5
   10 | ==============================================================================
   11 |  lag  n subj   mean beta  % same sign   Wilcoxon p   sig?
   12 |    0     171    +0.01595       74.9%     5.32e-13    YES
   13 |    1     171    +0.02046       81.9%     1.88e-19    YES
   14 |    2     170    +0.00849       64.7%     1.38e-05
   15 |    3     170    +0.00405       55.9%     9.91e-03
   16 |    4     170    +0.00284       53.5%     9.39e-02
   17 |    5     170    -0.00054       55.9%     3.93e-01
   18 | 
   19 |   omnibus (profile differs from flat): chi2 = 105.2, p = 4.229e-21   PASS
   20 | 
   21 | ==============================================================================
   22 | S1: same, with prev_log_RT included
   23 | ==============================================================================
   24 |  lag  n subj   mean beta  % same sign   Wilcoxon p   sig?
   25 |    0     171    +0.01375       75.4%     2.65e-13    YES
   26 |    1     170    +0.01883       82.9%     5.16e-19    YES
   27 |    2     170    +0.00670       60.6%     3.76e-04
   28 |    3     170    +0.00234       53.5%     1.10e-01
   29 |    4     170    +0.00111       52.4%     5.13e-01
   30 |    5     170    -0.00235       58.2%     3.71e-02
   31 | 
   32 |   omnibus (profile differs from flat): chi2 = 157.5, p = 3.365e-32   PASS
   33 | 
   34 | ==============================================================================
   35 | S2 (reference): impulse response to SURPRISAL
   36 | ==============================================================================
   37 |  lag  n subj   mean beta  % same sign   Wilcoxon p   sig?
   38 |    0     171    +0.02263       87.1%     1.45e-22    YES
   39 |    1     171    +0.03844       92.4%     5.09e-28    YES
   40 |    2     170    +0.03324       94.1%     2.80e-28    YES
   41 |    3     170    +0.02104       86.5%     1.23e-23    YES
   42 |    4     170    +0.01292       77.6%     3.25e-16    YES
   43 |    5     170    +0.01116       77.6%     4.80e-15    YES
   44 | 
   45 |   omnibus (profile differs from flat): chi2 = 291.0, p = 8.523e-61   PASS
   46 | 
   47 | ==============================================================================
   48 | S3: does TEE predict RT-extrapolation error at the same word?
   49 | ==============================================================================
   50 |   n = 171  mean beta = +0.00162  same sign 52.0%  Wilcoxon p = 5.54e-01
   51 | 
   52 | ==============================================================================
   53 | S4: does TEE predict the residual of an AR(2) model of log RT?
   54 | ==============================================================================
   55 |   n = 171  mean beta = +0.00558  same sign 63.7%  Wilcoxon p = 7.56e-05
```


==============================================================================
### FILE: gp_confound_check/sap_bigsurp_out.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | sentences: 144   sentence-words: 1,923
    3 | 
    4 | loading gpt2-xl ...
    5 | 
    6 | Loading weights:   0%|          | 0/580 [00:00<?, ?it/s]
    7 | Loading weights: 100%|██████████| 580/580 [00:00<00:00, 9114.06it/s]
    8 |   gpt2-xl: mean 7.46 bits   sd 5.40   missing 0
    9 | 
   10 | loading EleutherAI/pythia-410m ...
   11 | 
   12 | Loading weights:   0%|          | 0/292 [00:00<?, ?it/s]
   13 | Loading weights: 100%|██████████| 292/292 [00:00<00:00, 10040.88it/s]
   14 |   EleutherAI/pythia-410m: mean 7.59 bits   sd 5.46   missing 0
   15 | 
   16 | ======================================================================
   17 | SANITY: agreement between surprisal estimates (sentence-word level)
   18 | ======================================================================
   19 |   r(GPT-2 Small, GPT-2 XL)      = +0.967
   20 |   r(GPT-2 Small, Pythia-410M)   = +0.969
   21 |   r(GPT-2 XL,    Pythia-410M)   = +0.971
   22 | 
   23 |   mean surprisal (bits): small 7.56  xl 7.46  pythia 7.59
   24 |   (a stronger model should assign LOWER surprisal on average)
   25 | 
   26 |   correlation of each surprisal with TEE (GPT-2 Small L6 k=3):
   27 |     r(TEE, surp            ) = +0.386
   28 |     r(TEE, surp_xl         ) = +0.374
   29 |     r(TEE, surp_pythia410m ) = +0.376
   30 | 
   31 | saved -> /Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/sap_bigsurp.csv   (1,923 rows)
```


==============================================================================
### FILE: gp_confound_check/sap_bigsurp_refit_out.txt
==============================================================================

```
    1 | rows 444,737   participants 2,000
    2 | 
    3 | ========================================================================================
    4 | TEE COEFFICIENT UNDER INCREASINGLY STRONG SURPRISAL CONTROLS
    5 | ========================================================================================
    6 | spec                                     n   TEE beta   % pos          p   surp beta
    7 | S0  GPT-2 Small surprisal  [ref]      2000   +0.02505   62.7%   5.51e-39    +0.02832
    8 | S1  GPT-2 XL surprisal                2000   +0.02550   63.1%   2.97e-40    +0.02219
    9 | S2  Pythia-410M surprisal             2000   +0.02546   63.1%   3.25e-40    +0.02634
   10 | S3  all three surprisals              2000   +0.02543   62.6%   1.05e-39    -0.03626
   11 | S5  S3 + previous log RT              2000   +0.01415   57.8%   4.16e-17    -0.01373
   12 | 
   13 | ========================================================================================
   14 | S4  all three surprisals splined (df=4 each)
   15 | ========================================================================================
   16 | spec                                     n   TEE beta   % pos          p
   17 | S4  three splined surprisals          2000   +0.02458   62.0%   5.33e-37
   18 | 
   19 | ========================================================================================
   20 | FLOOR: S3 spec with TEE permuted within participant
   21 | ========================================================================================
   22 | spec                                     n   TEE beta   % pos          p
   23 | F   permuted TEE                      2000   +0.00124   52.2%   2.71e-01
   24 | 
   25 | ========================================================================================
   26 | POOLED dAIC: gain from adding TEE to each surprisal specification
   27 | ========================================================================================
   28 |   GPT-2 Small only             AIC  1059844.5  +TEE  1059641.3  dAIC(TEE)   +203.2  beta +0.02024
   29 |   GPT-2 XL only                AIC  1059935.3  +TEE  1059723.6  dAIC(TEE)   +211.7  beta +0.02064
   30 |   Pythia-410M only             AIC  1059877.1  +TEE  1059667.0  dAIC(TEE)   +210.1  beta +0.02056
   31 |   all three                    AIC  1059827.1  +TEE  1059623.7  dAIC(TEE)   +203.4  beta +0.02025
   32 |   all three, XL splined df=5   AIC  1058784.6  +TEE  1058630.9  dAIC(TEE)   +153.7  beta +0.01768
```


==============================================================================
### FILE: gp_confound_check/spline_out.txt
==============================================================================

```
    1 | n = 812,730   participants = 178
    2 | r(TEE, surprisal) = +0.312   r(TEE, log_freq) = -0.439
    3 | 
    4 | ================================================================================
    5 | Does TEE survive as surprisal/frequency/length are given more freedom?
    6 | ================================================================================
    7 | control specification                       dAIC(TEE)      beta           p
    8 | linear (published spec)                         111.8   0.00354    1.42e-26
    9 | splines df=3 on surp/freq/len                    93.0   0.00324    1.91e-22
   10 | splines df=5 on surp/freq/len                    97.9   0.00334    1.56e-23
   11 | splines df=8 on surp/freq/len                   106.8   0.00351    1.78e-25
   12 | splines df=12 on surp/freq/len                  102.9   0.00345    1.27e-24
   13 | df=8 splines + entropy + punctuation            108.4   0.00358    8.09e-26
   14 | 
   15 | ================================================================================
   16 | How curved IS the surprisal-RT relationship? (is the worry real?)
   17 | ================================================================================
   18 |   linear surprisal   AIC = 161314.6
   19 |   spline surprisal   AIC = 160968.2   improvement = 346.4
   20 |   (large improvement => surprisal really is nonlinear here, so the
   21 |    misspecification worry was well founded)
```


==============================================================================
### FILE: gp_confound_check/table1_exact_output.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | [transformers] The following generation flags are not valid and may be ignored: ['output_hidden_states']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
    3 | 
    4 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 10835.16it/s]
    6 | 
    7 | ======================================================================
    8 | ROI 1+2 (original sample)
    9 | ======================================================================
   10 | 
   11 | #### L6_w3 ####
   12 | presentation         N     dAIC      beta           p  win touches w0
   13 | A_isolated      95,173     34.7    0.0080    1.36e-09           0.0%
   14 | B_prefix        95,173     56.8    0.0103    1.69e-14           0.0%
   15 | C_droptok0      95,173     34.7    0.0080    1.36e-09           0.0%
   16 | 
   17 | #### L12_w5 ####
   18 | presentation         N     dAIC      beta           p  win touches w0
   19 | A_isolated      95,173     11.3    0.0048    2.67e-04           0.0%
   20 | B_prefix        95,173     42.9    0.0087    2.06e-11           0.0%
   21 | C_droptok0      95,173     11.3    0.0048    2.67e-04           0.0%
   22 | 
   23 | #### L6_w5 ####
   24 | presentation         N     dAIC      beta           p  win touches w0
   25 | A_isolated      95,173     -0.7   -0.0015    2.62e-01           0.0%
   26 | B_prefix        95,173     -1.9   -0.0005    7.19e-01           0.0%
   27 | C_droptok0      95,173     -0.7   -0.0015    2.62e-01           0.0%
   28 | 
   29 | #### L6_w7 ####
   30 | presentation         N     dAIC      beta           p  win touches w0
   31 | A_isolated      84,959     26.4    0.0121    9.99e-08          35.5%
   32 | B_prefix        95,173     39.6    0.0088    1.13e-10          42.4%
   33 | C_droptok0      84,959     18.9    0.0064    4.92e-06          35.5%
   34 | 
   35 | Published Table 1: L6/w3 +10.7 | L12/w5 +56.4 | L6/w5 0.0 | L6/w7 +31.4
   36 | 
   37 | ======================================================================
   38 | ROI 0+1+2 (ROI 0 restored)
   39 | ======================================================================
   40 | 
   41 | #### L6_w3 ####
   42 | presentation         N     dAIC      beta           p  win touches w0
   43 | A_isolated     142,871     56.6   -0.0081    1.92e-14           0.0%
   44 | B_prefix       142,871     65.1   -0.0087    2.53e-16           0.0%
   45 | C_droptok0     142,871     56.6   -0.0081    1.92e-14           0.0%
   46 | 
   47 | #### L12_w5 ####
   48 | presentation         N     dAIC      beta           p  win touches w0
   49 | A_isolated     142,871      2.3   -0.0022    3.85e-02           7.2%
   50 | B_prefix       142,871     17.3    0.0047    1.11e-05           7.2%
   51 | C_droptok0     142,871      2.8    0.0023    2.77e-02           7.2%
   52 | 
   53 | #### L6_w5 ####
   54 | presentation         N     dAIC      beta           p  win touches w0
   55 | A_isolated     142,871     84.6   -0.0113    1.30e-20           7.2%
   56 | B_prefix       142,871     -1.8    0.0005    6.50e-01           7.2%
   57 | C_droptok0     142,871      7.2   -0.0034    2.40e-03           7.2%
   58 | 
   59 | #### L6_w7 ####
   60 | presentation         N     dAIC      beta           p  win touches w0
   61 | A_isolated     102,424     -1.8    0.0011    6.24e-01          43.8%
   62 | B_prefix       142,871     36.5    0.0071    5.41e-10          59.7%
   63 | C_droptok0     102,424      3.9    0.0031    1.55e-02          43.8%
   64 | 
   65 | Published Table 1: L6/w3 +10.7 | L12/w5 +56.4 | L6/w5 0.0 | L6/w7 +31.4
```


==============================================================================
### FILE: gp_confound_check/table1_rerun_output.txt
==============================================================================

```
    1 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    2 | [transformers] The following generation flags are not valid and may be ignored: ['output_hidden_states']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
    3 | 
    4 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 13261.49it/s]
    6 | 
    7 | ################ L6_k3  (n = 142,681, 2000 participants) ################
    8 | rows whose fit window touches word 0: 0.0%   r(isolated, droptok0) = 1.000   r(isolated, prefix) = 0.984
    9 | mean TEE  isolated 94.9 | prefix 93.6 | droptok0 94.9
   10 | 
   11 |   --- OLS ---
   12 |   presentation       dAIC surp   dAIC TEE      beta           p
   13 |   A_isolated             136.9       63.9   -0.0095    4.67e-16
   14 |   B_prefix               167.7       61.1   -0.0093    1.92e-15
   15 |   C_droptok0             136.9       63.9   -0.0095    4.67e-16
   16 | 
   17 |   --- participant-demeaned ---
   18 |   presentation       dAIC surp   dAIC TEE      beta           p
   19 |   A_isolated               8.2      102.5   -0.0108    1.60e-24
   20 |   B_prefix                26.9      109.2   -0.0111    5.26e-26
   21 |   C_droptok0               8.2      102.5   -0.0108    1.60e-24
   22 | 
   23 | ################ L12_k5  (n = 142,681, 2000 participants) ################
   24 | rows whose fit window touches word 0: 7.2%   r(isolated, droptok0) = 0.883   r(isolated, prefix) = 0.712
   25 | mean TEE  isolated 50.2 | prefix 50.8 | droptok0 48.4
   26 | 
   27 |   --- OLS ---
   28 |   presentation       dAIC surp   dAIC TEE      beta           p
   29 |   A_isolated             136.9        4.1   -0.0029    1.36e-02
   30 |   B_prefix               167.7        6.1    0.0033    4.39e-03
   31 |   C_droptok0             136.9       -0.2    0.0016    1.85e-01
   32 | 
   33 |   --- participant-demeaned ---
   34 |   presentation       dAIC surp   dAIC TEE      beta           p
   35 |   A_isolated               8.2       -0.1    0.0014    1.70e-01
   36 |   B_prefix                26.9       67.9    0.0088    6.28e-17
   37 |   C_droptok0               8.2       35.1    0.0064    1.10e-09
   38 | 
   39 | ################ L6_k5  (n = 142,681, 2000 participants) ################
   40 | rows whose fit window touches word 0: 7.2%   r(isolated, droptok0) = 0.265   r(isolated, prefix) = -0.067
   41 | mean TEE  isolated 153.0 | prefix 72.8 | droptok0 74.5
   42 | 
   43 |   --- OLS ---
   44 |   presentation       dAIC surp   dAIC TEE      beta           p
   45 |   A_isolated             136.9       57.4   -0.0103    1.29e-14
   46 |   B_prefix               167.7       -2.0    0.0001    9.18e-01
   47 |   C_droptok0             136.9        7.9   -0.0038    1.70e-03
   48 | 
   49 |   --- participant-demeaned ---
   50 |   presentation       dAIC surp   dAIC TEE      beta           p
   51 |   A_isolated               8.2       90.2   -0.0115    8.05e-22
   52 |   B_prefix                26.9       -0.4   -0.0014    2.04e-01
   53 |   C_droptok0               8.2       17.2   -0.0048    1.20e-05
   54 | 
   55 | ################ L6_k7  (n = 102,290, 2000 participants) ################
   56 | rows whose fit window touches word 0: 43.8%   r(isolated, droptok0) = 0.192   r(isolated, prefix) = -0.030
   57 | mean TEE  isolated 409.4 | prefix 67.1 | droptok0 69.4
   58 | 
   59 |   --- OLS ---
   60 |   presentation       dAIC surp   dAIC TEE      beta           p
   61 |   A_isolated              73.6        3.3    0.0056    2.15e-02
   62 |   B_prefix               124.9       -0.1    0.0020    1.65e-01
   63 |   C_droptok0              73.6       -2.0    0.0003    8.30e-01
   64 | 
   65 |   --- participant-demeaned ---
   66 |   presentation       dAIC surp   dAIC TEE      beta           p
   67 |   A_isolated              -2.0       -1.0   -0.0022    3.23e-01
   68 |   B_prefix                13.3       -0.6    0.0015    2.35e-01
   69 |   C_droptok0              -2.0       -1.7   -0.0007    5.98e-01
   70 | 
   71 | Paper Table 1 (for reference): M1 dAIC -1.9 (n.s.); L6/w3 +10.7; L12/w5 +56.4; L6/w5 0.0; L6/w7 +31.4; N = 95,173
```


==============================================================================
### FILE: gp_confound_check/tee_functional_form_out.txt
==============================================================================

```
    1 | ====================================================================================
    2 | Natural Stories
    3 | ====================================================================================
    4 |   812,730 rows, 178 participants
    5 | 
    6 |   F1  linear vs spline in TEE  (positive = spline fits better)
    7 |       df=3:  mean dAIC =   -0.50   spline better in 30.4% of participants   n=171
    8 |       df=5:  mean dAIC =   -2.29   spline better in 22.8% of participants   n=171
    9 |       df=8:  mean dAIC =   -4.64   spline better in 15.8% of participants   n=171
   10 | 
   11 |   F2  monotonicity across deciles
   12 |       mean Spearman rho(decile, residual) = +0.197   positive in 73.7% of participants
   13 |       strictly monotone increasing profiles: 0.0%
   14 |       grand profile rho = +0.636
   15 |       grand profile: [-0.0109  0.0065 -0.0142 -0.0127 -0.0016 -0.0137 -0.0037  0.0075  0.0118
   16 |   0.0308]
   17 | 
   18 |   F3  split-half shape stability: r = +0.879 (sd 0.056) over 50 splits
   19 | 
   20 |   F4  effect without the extreme deciles
   21 |       full     beta = +0.01277  73.1% positive
   22 |       trimmed  beta = +0.00603  59.1% positive  (47% of full)
   23 | 
   24 | ====================================================================================
   25 | Garden-path corpus
   26 | ====================================================================================
   27 |   444,737 rows, 2,000 participants
   28 | 
   29 |   F1  linear vs spline in TEE  (positive = spline fits better)
   30 |       df=3:  mean dAIC =   -1.95   spline better in 13.4% of participants   n=2000
   31 |       df=5:  mean dAIC =   -4.00   spline better in  9.8% of participants   n=2000
   32 |       df=8:  mean dAIC =   -6.77   spline better in  6.7% of participants   n=2000
   33 | 
   34 |   F2  monotonicity across deciles
   35 |       mean Spearman rho(decile, residual) = +0.079   positive in 60.8% of participants
   36 |       strictly monotone increasing profiles: 0.0%
   37 |       grand profile rho = +0.745
   38 |       grand profile: [-0.0154 -0.0128 -0.0326 -0.002   0.009  -0.0261 -0.0006  0.0302  0.0288
   39 |   0.0217]
   40 | 
   41 |   F3  split-half shape stability: r = +0.932 (sd 0.028) over 50 splits
   42 | 
   43 |   F4  effect without the extreme deciles
   44 |       full     beta = +0.02238  61.1% positive
   45 |       trimmed  beta = +0.01715  59.1% positive  (77% of full)
   46 | 
```


==============================================================================
### FILE: gp_confound_check/tee_threshold_out.txt
==============================================================================

```
    1 | ======================================================================================
    2 | Natural Stories
    3 | ======================================================================================
    4 |   171 participants
    5 | 
    6 |   T1  per-decile residual mean (across participants)
    7 |        decile      mean              95% CI       t         p
    8 |             1   -0.0109   [-0.0183, -0.0036]   -2.92   3.9e-03 *
    9 |             2   +0.0065   [-0.0005, +0.0136]    1.81   7.1e-02
   10 |             3   -0.0142   [-0.0214, -0.0070]   -3.85   1.7e-04 *
   11 |             4   -0.0127   [-0.0188, -0.0067]   -4.12   6.0e-05 *
   12 |             5   -0.0016   [-0.0091, +0.0059]   -0.41   6.8e-01
   13 |             6   -0.0137   [-0.0206, -0.0068]   -3.89   1.4e-04 *
   14 |             7   -0.0037   [-0.0126, +0.0052]   -0.81   4.2e-01
   15 |             8   +0.0075   [-0.0003, +0.0153]    1.89   6.0e-02
   16 |             9   +0.0118   [+0.0047, +0.0190]    3.23   1.5e-03 *
   17 |            10   +0.0308   [+0.0241, +0.0376]    8.95   5.9e-16 *
   18 | 
   19 |   T2  split-half shape stability
   20 |       all deciles      r = +0.874 (sd 0.057)
   21 |       deciles 1-7 only r = +0.650 (sd 0.172)   <- is the flat region real structure?
   22 | 
   23 |   T3  shape of the trajectory term (AIC, lower is better)
   24 |       linear                   mean dAIC vs linear =   +0.00   better in  0.0% of participants
   25 |       top-decile indicator     mean dAIC vs linear =   -0.61   better in 42.7% of participants
   26 |       hinge                    mean dAIC vs linear =   +0.21   better in 54.4% of participants
   27 | 
   28 | ======================================================================================
   29 | Garden-path corpus
   30 | ======================================================================================
   31 |   2000 participants
   32 | 
   33 |   T1  per-decile residual mean (across participants)
   34 |        decile      mean              95% CI       t         p
   35 |             1   -0.0154   [-0.0220, -0.0089]   -4.61   4.2e-06 *
   36 |             2   -0.0128   [-0.0200, -0.0056]   -3.50   4.7e-04 *
   37 |             3   -0.0326   [-0.0403, -0.0248]   -8.24   3.1e-16 *
   38 |             4   -0.0020   [-0.0097, +0.0057]   -0.50   6.2e-01
   39 |             5   +0.0090   [+0.0005, +0.0175]    2.08   3.7e-02 *
   40 |             6   -0.0261   [-0.0342, -0.0180]   -6.33   3.0e-10 *
   41 |             7   -0.0006   [-0.0092, +0.0079]   -0.14   8.9e-01
   42 |             8   +0.0302   [+0.0214, +0.0390]    6.72   2.3e-11 *
   43 |             9   +0.0288   [+0.0202, +0.0374]    6.53   8.2e-11 *
   44 |            10   +0.0217   [+0.0131, +0.0304]    4.94   8.5e-07 *
   45 | 
   46 |   T2  split-half shape stability
   47 |       all deciles      r = +0.932 (sd 0.034)
   48 |       deciles 1-7 only r = +0.880 (sd 0.064)   <- is the flat region real structure?
   49 | 
   50 |   T3  shape of the trajectory term (AIC, lower is better)
   51 |       linear                   mean dAIC vs linear =   +0.00   better in  0.0% of participants
   52 |       top-decile indicator     mean dAIC vs linear =   -0.06   better in 48.9% of participants
   53 |       hinge                    mean dAIC vs linear =   +0.08   better in 52.2% of participants
   54 | 
```


==============================================================================
### FILE: gp_confound_check/transfer_out.txt
==============================================================================

```
    1 | Natural Stories (self-paced): 171 participants
    2 | OneStop (eye tracking, TRT):  180 participants
    3 | 
    4 | ==============================================================================
    5 | STANDARDISED EFFECTS IN BOTH PARADIGMS (subject-level means)
    6 | ==============================================================================
    7 | predictor          NS self-paced     OneStop TRT   transfer ratio
    8 | word_length        +0.01265 *     +0.08798*            6.95
    9 | log_freq           +0.00687 *     +0.04588*            6.68
   10 | surprisal          +0.01104 *     +0.06344*            5.74
   11 | tee                +0.00395 *     -0.00504*           -1.27
   12 | 
   13 |   mean transfer ratio of the three established predictors: 6.46
   14 |   (surprisal 5.74, frequency 6.68, length 6.95)
   15 | 
   16 | ==============================================================================
   17 | IS TEE'S ONESTOP ESTIMATE WHAT THE BENCHMARK PREDICTS?
   18 | ==============================================================================
   19 |   TEE beta in Natural Stories            = +0.00395
   20 |   predicted OneStop beta at that ratio   = +0.02553
   21 |   observed OneStop beta                  = -0.00504  (SE 0.00095)
   22 |   observed vs predicted                  = -32.25 SE  (p = 0.0000)
   23 | 
   24 |   If the established predictors transfer but TEE lands far below its
   25 |   predicted value, the non-replication is specific to TEE rather than
   26 |   a general property of the paradigm shift.
```


==============================================================================
### FILE: gp_confound_check/v2_interaction_out.txt
==============================================================================

```
    1 | locked sample 8a6087341e verified
    2 | n = 812,730   participants = 178
    3 | 
    4 | ==========================================================================
    5 | ADDITIVE vs INTERACTION
    6 | ==========================================================================
    7 |   additive     AIC     161353.9
    8 |   interaction  AIC     161355.4
    9 | 
   10 |   dAIC (additive - interaction) = -1.5
   11 |   ADDITIVE favoured by 1.5
   12 | 
   13 |   interaction coefficient = +0.00019   p = 4.911e-01
   14 |   main effects in the interaction model: surprisal +0.01023, TEE +0.00299
   15 | 
   16 | ==========================================================================
   17 | v1 CLAIM CHECK
   18 | ==========================================================================
   19 |   v1: 'additive model preferred over interaction, dAIC = -2.0'
   20 |   -> reproduces in direction and roughly in magnitude.
```


==============================================================================
### FILE: gp_confound_check/v2_offdiag_out.txt
==============================================================================

```
    1 | locked sample 8a6087341e   9,840 words
    2 | columns available: ['id', 'word', 'story_id', 'zone', 'word_idx', 'closure_depth', 'sent_uid', 'from_start', 'from_end', 'sent_len', 'n_leaves', 'final_bpe', 'surprisal', 'entropy', 'tee_k2', 'teeN_k2', 'tee_k3', 'teeN_k3', 'tee_k4', 'teeN_k4', 'tee_k5', 'teeN_k5', 'tee_k7', 'teeN_k7', 'tee_k10', 'teeN_k10', 'tee_k15', 'teeN_k15', 'tee_k20', 'teeN_k20', 'tee_k30', 'teeN_k30', 'tee_k50', 'teeN_k50', 'word_length', 'log_freq', 'fs2', 'fe2']
    3 | 
    4 | ==============================================================================
    5 | (B) WHERE DOES r = .044 COME FROM?
    6 | ==============================================================================
    7 | TEE-like columns in the locked sample: ['tee_k2', 'teeN_k2', 'tee_k3', 'teeN_k3', 'tee_k4', 'teeN_k4', 'tee_k5', 'teeN_k5', 'tee_k7', 'teeN_k7', 'tee_k10', 'teeN_k10', 'tee_k15', 'teeN_k15', 'tee_k20', 'teeN_k20', 'tee_k30', 'teeN_k30', 'tee_k50', 'teeN_k50']
    8 | 
    9 | measure            r(x, surprisal)    Spearman   r(x, entropy)
   10 | tee_k2                      0.1860      0.1419         -0.0910
   11 | teeN_k2                     0.2615      0.2771          0.1573
   12 | tee_k3                      0.3100      0.2810          0.0429
   13 | teeN_k3                     0.2486      0.2638          0.1519
   14 | tee_k4                      0.3429      0.3340          0.1083
   15 | teeN_k4                     0.2724      0.2993          0.1698
   16 | tee_k5                      0.3493      0.3593          0.1499
   17 | teeN_k5                     0.2902      0.3243          0.1866
   18 | tee_k7                      0.3401      0.3690          0.1963
   19 | teeN_k7                     0.2900      0.3307          0.2067
   20 | tee_k10                     0.3125      0.3513          0.2316
   21 | teeN_k10                    0.2781      0.3250          0.2360
   22 | tee_k15                     0.2808      0.3237          0.2380
   23 | teeN_k15                    0.2575      0.3030          0.2358
   24 | tee_k20                     0.2687      0.3089          0.2365
   25 | teeN_k20                    0.2491      0.2915          0.2318
   26 | tee_k30                     0.2499      0.2873          0.2254
   27 | teeN_k30                    0.2377      0.2768          0.2219
   28 | tee_k50                     0.2292      0.2651          0.2046
   29 | teeN_k50                    0.2262      0.2592          0.2056
   30 | 
   31 | values landing within .015 of .044:
   32 |   tee_k3                            pearson-entropy       +0.0429
   33 | 
   34 | VERDICT (B):
   35 |   headline measure tee_k3:  r(surprisal) = +0.3100   r(entropy) = +0.0429
   36 |   The entropy correlation reproduces .044 to within .005 while the
   37 |   surprisal correlation is nowhere near it. Mislabelling in the v1
   38 |   pipeline is the parsimonious account. v2 should state this.
   39 | 
   40 | ==============================================================================
   41 | (A) COMPOSITION OF THE OFF-DIAGONAL CELLS, RECOMPUTED
   42 | ==============================================================================
   43 | analysis rows 812,730   participants 178
   44 | distinct corpus positions in the matrix: 9,830
   45 | 
   46 | 
   47 | v1 claimed: low-surprisal / high-TEE is enriched for coordinators and
   48 | complementizers ('and', 'as', 'that', 'had').
   49 | ------------------------------------------------------------------------------
   50 | LOW SURPRISAL / HIGH TEE   n = 810 corpus positions, 306 word types
   51 |   mean surprisal 0.95   mean TEE 95.9   mean log freq 2.95
   52 |   closed-class share 48.5%  (corpus overall 45.8%)
   53 | 
   54 |   most frequent words in the cell:
   55 |     and (49), of (44), to (37), that (17), was (15), as (15), had (15), the (13), bird (12), for (11), in (11), abby (11), her (10), at (9), king (9), is (8), you (8), he (7), out (7), she (7), bulbs (7), bradford (6), me (6), a (6), on (6)
   56 | 
   57 |   most ENRICHED words (count >= 5, cell rate / corpus rate):
   58 |     bird (15.0x), elvis (14.9x), well (13.2x), bradford (13.0x), bulbs (12.8x), manor (11.9x), king (11.9x), prices (10.8x), roswell (9.2x), abby (7.9x), me (7.5x), you (5.8x), is (4.9x), of (4.8x), at (4.0x), and (3.9x), out (3.9x), one (3.9x), for (3.7x), to (3.6x), as (3.6x), had (3.5x), they (3.0x), on (2.5x), her (2.5x)
   59 | 
   60 | v1 claimed: high-surprisal / low-TEE holds rare content words ('ocean',
   61 | 'manor', 'tics') and discourse pivots ('then', 'however', 'now', 'first').
   62 | ------------------------------------------------------------------------------
   63 | HIGH SURPRISAL / LOW TEE   n = 610 corpus positions, 388 word types
   64 |   mean surprisal 6.25   mean TEE 76.5   mean log freq 1.92
   65 |   closed-class share 31.6%  (corpus overall 45.8%)
   66 | 
   67 |   most frequent words in the cell:
   68 |     that (14), the (12), for (9), and (9), in (8), as (8), when (7), a (6), at (6), who (6), then (6), on (6), now (5), no (5), not (5), many (5), you (5), new (5), often (4), people (4), like (4), we (4), it's (4), even (4), with (4)
   69 | 
   70 |   most ENRICHED words (count >= 5, cell rate / corpus rate):
   71 |     now (27.6x), new (22.8x), many (22.8x), when (18.1x), no (13.8x), then (12.9x), you (11.7x), for (9.8x), at (8.6x), on (8.1x), who (7.3x), not (7.0x), that (6.5x), as (6.3x), in (4.2x), and (2.3x), a (2.3x), the (1.2x)
   72 | 
   73 | ==============================================================================
   74 | CHECK OF v1'S SPECIFIC EXAMPLES ON THE VERIFIED SAMPLE
   75 | ==============================================================================
   76 | 
   77 | low/high (coordinators/complementizers):
   78 |   and          49/297  occurrences in cell (16.5%, chance 8.2%)   ENRICHED
   79 |   as           15/99   occurrences in cell (15.2%, chance 8.2%)   ENRICHED
   80 |   that         17/168  occurrences in cell (10.1%, chance 8.2%)
   81 |   had          15/103  occurrences in cell (14.6%, chance 8.2%)   ENRICHED
   82 | 
   83 | high/low (rare content + pivots):
   84 |   ocean         0/7    occurrences in cell ( 0.0%, chance 6.2%)
   85 |   manor         0/10   occurrences in cell ( 0.0%, chance 6.2%)
   86 |   tics          0/22   occurrences in cell ( 0.0%, chance 6.2%)
   87 |   then          6/36   occurrences in cell (16.7%, chance 6.2%)   ENRICHED
   88 |   however       1/13   occurrences in cell ( 7.7%, chance 6.2%)
   89 |   now           5/14   occurrences in cell (35.7%, chance 6.2%)   ENRICHED
   90 |   first         3/22   occurrences in cell (13.6%, chance 6.2%)   ENRICHED
```


==============================================================================
### FILE: gp_confound_check/v2_t3.txt
==============================================================================

```
    1 | ==========================================================================
    2 | ORTHOGONALITY (v1 claim: r = .044)
    3 | ==========================================================================
    4 |   word-level r(TEE, surprisal)      = +0.3100  (n = 9,840)
    5 |   word-level r(TEE, entropy)        = +0.0429
    6 |   word-level r(TEE, log_freq)       = -0.4381
    7 |   word-level r(TEE, displacement)   = +0.7998
    8 |   word-level r(displacement, surp)  = +0.3139
    9 | 
   10 | ==========================================================================
   11 | TABLE 2: dissociation matrix, mean log RT by surprisal x TEE tercile
   12 | ==========================================================================
   13 | 
   14 | mean log RT:
   15 | e_t      low     mid    high
   16 | s_t
   17 | low   5.7167  5.7217  5.7262
   18 | mid   5.7324  5.7323  5.7447
   19 | high  5.7456  5.7472  5.7579
   20 | 
   21 | cell n:
   22 | e_t      low    mid    high
   23 | s_t
   24 | low   123424  80926   66620
   25 | mid    97275  90884   82722
   26 | high   50260  99113  121506
   27 | 
   28 | relative to low/low baseline (5.7167):
   29 | e_t      low     mid    high
   30 | s_t
   31 | low   0.0000  0.0050  0.0095
   32 | mid   0.0157  0.0157  0.0280
   33 | high  0.0289  0.0306  0.0412
   34 | 
   35 | key off-diagonal cells (v1: high-surp/low-TEE +0.039; low-surp/high-TEE +0.008):
   36 |   high surprisal, low TEE    delta = +0.0289  n = 50,260  t = 14.38  p = 8.25e-47
   37 |   low surprisal, high TEE    delta = +0.0095  n = 66,620  t = 5.43  p = 5.70e-08
   38 | 
   39 | ==========================================================================
   40 | TABLE 3: displacement control
   41 | ==========================================================================
   42 | v1 claim: displacement and extrapolation error predict in OPPOSITE directions
   43 | 
   44 | model                           beta             p
   45 | TEE alone                    0.00354      1.42e-26
   46 | displacement alone           0.00315      5.18e-20
   47 | both: TEE                    0.00287      8.86e-09
   48 | both: displacement           0.00092      7.54e-02
   49 | 
   50 | n = 812,730   participants = 178
```


==============================================================================
### FILE: gp_confound_check/v2_t4.txt
==============================================================================

```
    1 | corpus: 10256 words, stories [np.int64(1), np.int64(2), np.int64(3), np.int64(4), np.int64(5), np.int64(6), np.int64(7), np.int64(8), np.int64(9), np.int64(10)]
    2 | parsed 485 trees, 11729 leaves
    3 | aligned 10256 words
    4 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    5 | 
    6 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    7 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 9718.31it/s]
    8 | story 1: forward pass...
    9 | [transformers] Token indices sequence length is longer than the specified maximum sequence length for this model (1289 > 1024). Running this sequence through the model will result in indexing errors
   10 | story 1: done
   11 | story 2: forward pass...
   12 | story 2: done
   13 | story 3: forward pass...
   14 | story 3: done
   15 | story 4: forward pass...
   16 | story 4: done
   17 | story 5: forward pass...
   18 | story 5: done
   19 | story 6: forward pass...
   20 | story 6: done
   21 | story 7: forward pass...
   22 | story 7: done
   23 | story 8: forward pass...
   24 | story 8: done
   25 | story 9: forward pass...
   26 | story 9: done
   27 | story 10: forward pass...
   28 | story 10: done
   29 | 
   30 | VALIDATION (locked sample, hash 8a6087341e, n=9840):
   31 |   closure_depth mismatches: 0
   32 |   final_bpe mismatches:     0
   33 |   max |tee_k50 - re|:       6.002e-05
   34 |   max |tee_k3  - re|:       1.029e-04
   35 |   curvature_1 NaNs:         0
   36 |   curvature_3 NaNs:         0
   37 |   curvature_1 mean/sd:      1.9978 / 0.1712
   38 |   curvature_3 mean/sd:      1.9942 / 0.0736
   39 |   disp_word mean/sd:        64.009 / 9.438
   40 |   r(disp_word, tee_k3):     0.7998
   41 |   r(disp_word, tee3_perp):  0.7627
   42 | 
   43 | ========================================================================
   44 | TABLE 4 (recomputed on verified states): direction preservation
   45 | ========================================================================
   46 |  layer  window   current       +1       +2       +3         n
   47 |    L12       3     0.615    0.541    0.540    0.539    10,216
   48 |    L12       5     0.602    0.547    0.543    0.544    10,196
   49 |     L6       3     0.436    0.099    0.078    0.077    10,216
   50 |     L6       5     0.396    0.097    0.076    0.073    10,196
   51 | 
   52 | v1 reported: L6 current .44, +1 .10, +2/+3 ~.08; L12 ~.54 across all
   53 | 
   54 | DONE -> displacement_8a6087341e.csv
```


==============================================================================
### FILE: gp_confound_check/v2_t6.txt
==============================================================================

```
    1 | corpus: 10256 words, 10 stories
    2 | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
    3 | 
    4 | Loading weights:   0%|          | 0/148 [00:00<?, ?it/s]
    5 | Loading weights: 100%|██████████| 148/148 [00:00<00:00, 16599.11it/s]
    6 |   EleutherAI/pythia-160m story 1 done
    7 |   EleutherAI/pythia-160m story 2 done
    8 |   EleutherAI/pythia-160m story 3 done
    9 |   EleutherAI/pythia-160m story 4 done
   10 |   EleutherAI/pythia-160m story 5 done
   11 |   EleutherAI/pythia-160m story 6 done
   12 |   EleutherAI/pythia-160m story 7 done
   13 |   EleutherAI/pythia-160m story 8 done
   14 |   EleutherAI/pythia-160m story 9 done
   15 |   EleutherAI/pythia-160m story 10 done
   16 | EleutherAI/pythia-160m: 9,840 words with TEE
   17 | 
   18 | Loading weights:   0%|          | 0/292 [00:00<?, ?it/s]
   19 | Loading weights: 100%|██████████| 292/292 [00:00<00:00, 24206.20it/s]
   20 |   EleutherAI/pythia-410m story 1 done
   21 |   EleutherAI/pythia-410m story 2 done
   22 |   EleutherAI/pythia-410m story 3 done
   23 |   EleutherAI/pythia-410m story 4 done
   24 |   EleutherAI/pythia-410m story 5 done
   25 |   EleutherAI/pythia-410m story 6 done
   26 |   EleutherAI/pythia-410m story 7 done
   27 |   EleutherAI/pythia-410m story 8 done
   28 |   EleutherAI/pythia-410m story 9 done
   29 |   EleutherAI/pythia-410m story 10 done
   30 | EleutherAI/pythia-410m: 9,840 words with TEE
   31 | 
   32 | MATCHED SAMPLE: n = 812,730, participants = 178
   33 | 
   34 | model               positional enc          dAIC       beta            p
   35 | gpt2                absolute               111.8    0.00354     1.42e-26
   36 | pythia_160m         rotary (RoPE)          115.5    0.00332     2.23e-27
   37 | pythia_410m         rotary (RoPE)          487.6    0.00726    1.65e-108
   38 | 
   39 | All rows and participants identical across models (v1 compared GPT-2 on 180 participants vs Pythia on 100).
```


==============================================================================
### FILE: gp_confound_check/v2_tables_23_out.txt
==============================================================================

```
    1 | ==========================================================================
    2 | ORTHOGONALITY (v1 claim: r = .044)
    3 | ==========================================================================
    4 |   word-level r(TEE, surprisal)      = +0.3100  (n = 9,840)
    5 |   word-level r(TEE, entropy)        = +0.0429
    6 |   word-level r(TEE, log_freq)       = -0.4381
    7 |   word-level r(TEE, displacement)   = +0.7998
    8 |   word-level r(displacement, surp)  = +0.3139
    9 | 
   10 | ==========================================================================
   11 | TABLE 2: dissociation matrix, mean log RT by surprisal x TEE tercile
   12 | ==========================================================================
   13 | 
   14 | mean log RT:
   15 | e_t      low     mid    high
   16 | s_t
   17 | low   5.7167  5.7217  5.7262
   18 | mid   5.7324  5.7323  5.7447
   19 | high  5.7456  5.7472  5.7579
   20 | 
   21 | cell n:
   22 | e_t      low    mid    high
   23 | s_t
   24 | low   123424  80926   66620
   25 | mid    97275  90884   82722
   26 | high   50260  99113  121506
   27 | 
   28 | relative to low/low baseline (5.7167):
   29 | e_t      low     mid    high
   30 | s_t
   31 | low   0.0000  0.0050  0.0095
   32 | mid   0.0157  0.0157  0.0280
   33 | high  0.0289  0.0306  0.0412
   34 | 
   35 | key off-diagonal cells (v1: high-surp/low-TEE +0.039; low-surp/high-TEE +0.008):
   36 |   high surprisal, low TEE    delta = +0.0289  n = 50,260  t = 14.38  p = 8.25e-47
   37 |   low surprisal, high TEE    delta = +0.0095  n = 66,620  t = 5.43  p = 5.70e-08
   38 | 
   39 | ==========================================================================
   40 | TABLE 3: displacement control
   41 | ==========================================================================
   42 | v1 claim: displacement and extrapolation error predict in OPPOSITE directions
   43 | 
   44 | model                           beta             p
   45 | Traceback (most recent call last):
   46 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/v2_tables_23.py", line 110, in <module>
   47 |     main()
   48 |     ~~~~^^
   49 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check/v2_tables_23.py", line 104, in main
   50 |     m = smf.mixedlm(f, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
   51 |         ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   52 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/regression/mixed_linear_model.py", line 1046, in from_formula
   53 |     mod = super().from_formula(formula, data, *args, **kwargs)
   54 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/base/model.py", line 203, in from_formula
   55 |     tmp = handle_formula_data(data, None, formula, depth=eval_env,
   56 |                               missing=missing)
   57 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/statsmodels/formula/formulatools.py", line 68, in handle_formula_data
   58 |     result = dmatrices(
   59 |         formula, Y, depth, return_type="dataframe", NA_action=na_action
   60 |     )
   61 |   File "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/.venv/lib/python3.14/site-packages/patsy/highlevel.py", line 321, in dmatrices
   62 |     raise PatsyError("model is missing required outcome variables")
   63 | patsy.PatsyError: model is missing required outcome variables
```


==============================================================================
### FILE: gp_confound_check/zuco_regress.txt
==============================================================================

```
    1 | subjects=12  words=30708  mean P(regress)=0.237
    2 | 
    3 | P1 (PRIMARY): TEE -> regression probability   [supportive if >=7/10 positive]
    4 |   P(regress) ~ TEE                             n=12 pos= 8/12  b=+0.0339  sign p=0.388  Wilcoxon p=0.034
    5 | 
    6 | P2: TEE should NOT predict durations
    7 |   FFD ~ TEE                                    n=12 pos= 6/12  b=+0.0004  sign p=1.000  Wilcoxon p=0.910
    8 |   GD  ~ TEE                                    n=12 pos=10/12  b=+0.0050  sign p=0.039  Wilcoxon p=0.042
    9 |   TRT ~ TEE                                    n=12 pos=11/12  b=+0.0079  sign p=0.006  Wilcoxon p=0.003
   10 | 
   11 | P3: surprisal should predict durations but NOT regressions
   12 |   P(regress) ~ surprisal                       too few
   13 |   GD  ~ surprisal                              n=12 pos= 5/12  b=+0.0005  sign p=0.774  Wilcoxon p=0.677
   14 |   TRT ~ surprisal                              n=12 pos= 8/12  b=+0.0048  sign p=0.388  Wilcoxon p=0.052
   15 | 
   16 | robustness: punctuation-free
   17 |   P(regress) ~ TEE (punct-free)                n=12 pos= 9/12  b=+0.0370  sign p=0.146  Wilcoxon p=0.034
```
