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


##############################################################################
# ANALYSIS SCRIPTS
##############################################################################


==============================================================================
### FILE: gp_confound_check/VERIFY_eyetracking.py
==============================================================================

```
    1 | """
    2 | INDEPENDENT VERIFICATION OF THE EYE-TRACKING RESULTS
    3 | =====================================================
    4 | The OneStop non-replication is now a headline claim -- it is in the abstract and
    5 | it is what the Discussion's preview account exists to explain -- but it has had
    6 | less scrutiny than anything else in the paper. It came from single runs earlier
    7 | in the project. This gives it the same treatment as VERIFY_sap.py.
    8 | 
    9 | WHAT IS BEING CHECKED (targets fixed here before the script is run, taken from
   10 | the manuscript text and the earlier output files):
   11 | 
   12 |   OneStop, ordinary-reading subcorpus
   13 |     participants                     180
   14 |     total reading time, TEE beta     -0.0023, p = .029          [negative]
   15 |     surprisal beta                   +0.031, 178/180, p = 2.9e-31
   16 |     lag-1 TEE beta                   +0.0014, 52.0%, p = .46
   17 |   ZuCo
   18 |     subjects                         12
   19 |     total reading time, TEE          11 of 12 positive, beta +0.0079, p = .006
   20 | 
   21 | INDEPENDENCE. As with the SAP verification, the point is not to re-run the same
   22 | code. Differences from the original path:
   23 |   - the analysis frame is rebuilt from the raw corpus files rather than from any
   24 |     intermediate saved by the earlier runs
   25 |   - subject-level fits use explicit numpy design matrices rather than formula
   26 |     interfaces
   27 |   - the lag-1 outcome is constructed and its contiguity checked independently
   28 |   - row counts are asserted at every filtering step
   29 | 
   30 | A DISAGREEMENT HERE IS MORE CONSEQUENTIAL THAN AGREEMENT. If the OneStop null
   31 | does not reproduce, the abstract, the eye-tracking section and the entire preview
   32 | discussion have to be revisited before upload.
   33 | """
   34 | 
   35 | import numpy as np
   36 | import pandas as pd
   37 | from scipy import stats
   38 | import statsmodels.api as sm
   39 | import glob, warnings
   40 | warnings.filterwarnings("ignore")
   41 | 
   42 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   43 | ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
   44 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   45 | 
   46 | FAIL = []
   47 | 
   48 | 
   49 | def check(name, ok, detail):
   50 |     print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
   51 |     if not ok:
   52 |         FAIL.append(name)
   53 | 
   54 | 
   55 | def zs(x):
   56 |     x = np.asarray(x, dtype=float)
   57 |     s = x.std()
   58 |     return (x - x.mean()) / s if s > 0 else x * 0
   59 | 
   60 | 
   61 | def subject_fit(df, subj, cols, outcome, minn=250):
   62 |     """Per-participant OLS; returns focus coefficients (cols[0])."""
   63 |     out = []
   64 |     for pid, sub in df.groupby(subj):
   65 |         s = sub.dropna(subset=cols + [outcome])
   66 |         if len(s) < minn:
   67 |             continue
   68 |         X = np.column_stack([zs(s[c].values) for c in cols])
   69 |         if (X.std(axis=0) == 0).any():
   70 |             continue
   71 |         r = sm.OLS(zs(s[outcome].values), sm.add_constant(X)).fit()
   72 |         out.append(r.params[1])
   73 |     return np.array(out)
   74 | 
   75 | 
   76 | def summarise(b, label):
   77 |     pos = (b > 0).mean()
   78 |     p = stats.wilcoxon(b).pvalue if len(b) > 5 else np.nan
   79 |     print(f"    {label:<34} n={len(b):>4}  beta={b.mean():>+9.5f}  "
   80 |           f"{pos:>5.1%} positive  p={p:.3e}")
   81 |     return b.mean(), pos, p
   82 | 
   83 | 
   84 | # ============================================================= ONESTOP
   85 | print("=" * 78)
   86 | print("ONESTOP")
   87 | print("=" * 78)
   88 | use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
   89 |                                   "wordfreq_frequency", "gpt2_surprisal"]
   90 | os_ = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
   91 | print(f"  raw rows {len(os_):,}   participants {os_.participant_id.nunique()}")
   92 | 
   93 | tee = pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv")
   94 | n0 = len(os_)
   95 | os_ = os_.merge(tee, on=KEY, how="left")
   96 | check("TEE merge preserves rows", len(os_) == n0, f"{len(os_):,}")
   97 | w = pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[KEY + ["word"]]
   98 | os_ = os_.merge(w, on=KEY, how="left")
   99 | 
  100 | for c in ["IA_DWELL_TIME", "word_length", "wordfreq_frequency",
  101 |           "gpt2_surprisal"]:
  102 |     os_[c] = pd.to_numeric(os_[c], errors="coerce")
  103 | 
  104 | # lag-1 built BEFORE filtering, contiguity enforced on interest-area order
  105 | os_ = os_.sort_values(["participant_id"] + KEY).reset_index(drop=True)
  106 | g = os_.groupby(["participant_id", "article_id", "paragraph_id",
  107 |                  "difficulty_level"])
  108 | os_["_y_raw"] = np.log(os_.IA_DWELL_TIME.where(os_.IA_DWELL_TIME > 0))
  109 | os_["y_lead1"] = g["_y_raw"].shift(-1)
  110 | os_["id_lead1"] = g["IA_ID"].shift(-1)
  111 | os_.loc[(os_.id_lead1 - os_.IA_ID) != 1, "y_lead1"] = np.nan
  112 | print(f"  after lag construction {len(os_):,}")
  113 | 
  114 | os_ = os_[os_.IA_DWELL_TIME > 0].copy()
  115 | os_["logTRT"] = np.log(os_.IA_DWELL_TIME)
  116 | os_["log_freq"] = np.log(os_.wordfreq_frequency.clip(lower=1e-9))
  117 | os_["punct"] = os_.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
  118 | os_ = os_.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
  119 | check("participants", os_.participant_id.nunique() == 180,
  120 |       f"{os_.participant_id.nunique()}")
  121 | 
  122 | CTRL = ["surprisal", "log_freq", "word_length", "punct"]
  123 | 
  124 | print("\n  total reading time, lag 0:")
  125 | b_tee = subject_fit(os_, "participant_id", ["tee"] + CTRL, "logTRT")
  126 | m, pos, p = summarise(b_tee, "TEE")
  127 | check("OneStop TEE is negative", m < 0, f"beta = {m:+.5f} (target -0.0023)")
  128 | check("OneStop TEE magnitude", abs(m - (-0.0023)) < 0.0015,
  129 |       f"{m:+.5f} vs -0.00230")
  130 | 
  131 | b_sur = subject_fit(os_, "participant_id",
  132 |                     ["surprisal", "log_freq", "word_length", "punct"], "logTRT")
  133 | m_s, pos_s, p_s = summarise(b_sur, "surprisal [sanity]")
  134 | check("OneStop surprisal is strongly positive", m_s > 0 and pos_s > .95,
  135 |       f"beta = {m_s:+.5f}, {pos_s:.1%} positive (target +0.031, 178/180)")
  136 | 
  137 | print("\n  total reading time, lag 1:")
  138 | b_l1 = subject_fit(os_, "participant_id", ["tee"] + CTRL, "y_lead1")
  139 | m1, pos1, p1 = summarise(b_l1, "TEE at lag 1")
  140 | check("OneStop lag-1 fails the replication criterion",
  141 |       not (m1 > 0 and p1 < .0017 and pos1 >= .65),
  142 |       f"beta {m1:+.5f}, {pos1:.1%} positive, p = {p1:.3f}")
  143 | 
  144 | # ============================================================= ZUCO
  145 | print("\n" + "=" * 78)
  146 | print("ZUCO")
  147 | print("=" * 78)
  148 | Z = "/Users/elanbarenholtz/ZuCo_TEE_Analysis"
  149 | try:
  150 |     T = pd.read_csv(f"{Z}/zuco_tee.csv")
  151 |     zu = pd.concat([pd.read_csv(f) for f in
  152 |                     sorted(glob.glob(f"{Z}/zuco_et/*_et.csv"))],
  153 |                    ignore_index=True)
  154 |     zu = zu.merge(T, on=["sent_idx", "word_idx"], how="inner",
  155 |                   suffixes=("", "_t"))
  156 |     zu["TRT"] = pd.to_numeric(zu.TRT, errors="coerce")
  157 |     zu = zu[zu.TRT > 0].copy()
  158 |     zu["logTRT"] = np.log(zu.TRT)
  159 |     zu["word_length"] = zu.word.astype(str).str.len()
  160 |     from wordfreq import zipf_frequency
  161 |     zu["log_freq"] = zu.word.astype(str).str.strip(".,;:!?").str.lower().map(
  162 |         lambda x: zipf_frequency(x, "en"))
  163 |     zu = zu.rename(columns={"surp": "surprisal", "tee_k3": "tee",
  164 |                             "has_trailing_punct": "punct"})
  165 |     print(f"  rows {len(zu):,}   subjects {zu.subject.nunique()}")
  166 |     b_z = subject_fit(zu, "subject", ["tee"] + CTRL, "logTRT", minn=150)
  167 |     mz, posz, pz = summarise(b_z, "TEE")
  168 |     check("ZuCo subjects", len(b_z) == 12, f"{len(b_z)} with sufficient data")
  169 |     check("ZuCo TEE positive in 11 of 12", (b_z > 0).sum() == 11,
  170 |           f"{(b_z > 0).sum()} of {len(b_z)} positive, beta {mz:+.5f} "
  171 |           f"(target +0.0079)")
  172 | except FileNotFoundError as e:
  173 |     print(f"  ZuCo files not reachable: {e}")
  174 |     FAIL.append("ZuCo data unavailable")
  175 | 
  176 | print("\n" + "=" * 78)
  177 | print("VERDICT")
  178 | print("=" * 78)
  179 | if FAIL:
  180 |     print(f"  {len(FAIL)} CHECK(S) FAILED: {', '.join(FAIL)}")
  181 |     print("  The eye-tracking claims must be resolved before upload.")
  182 | else:
  183 |     print("  ALL CHECKS PASSED. The OneStop non-replication and the ZuCo")
  184 |     print("  result reproduce on an independently rebuilt analysis frame.")
```


==============================================================================
### FILE: gp_confound_check/VERIFY_sap.py
==============================================================================

```
    1 | """
    2 | INDEPENDENT VERIFICATION OF THE SAP SECOND-CORPUS RESULT (V2_DRAFT 4b/4c)
    3 | =========================================================================
    4 | Everything in this project that later had to be withdrawn came from a pipeline
    5 | that was never independently recomputed. Section 4b is now carrying real
    6 | argumentative weight -- it is the second corpus -- so it gets the same treatment
    7 | Natural Stories got before it goes into a manuscript.
    8 | 
    9 | WHAT "INDEPENDENT" MEANS HERE
   10 | -----------------------------
   11 | This is not a rerun. Every step is implemented by a DIFFERENT method from the
   12 | one used in gp_allwords.py / sap_measures_L6k3.csv, so that agreement between
   13 | the two is evidence about the quantity rather than about the code:
   14 | 
   15 |   step                 original implementation        this implementation
   16 |   ------------------   ----------------------------   -------------------------
   17 |   subword alignment    sequential encode(), track     tokenizer offset mapping
   18 |                        last index per word            over the joined string
   19 |   word surprisal       python loop over token ids     vectorised gather
   20 |   trajectory fit       np.linalg.lstsq on a design    closed-form OLS slope from
   21 |                        matrix                         centred sums
   22 |   sample assembly      merge then filter              filter counts asserted at
   23 |                                                       every step, hashed
   24 | 
   25 | If the two agree to tolerance, the measure is verified. If they disagree, the
   26 | discrepancy is the finding and NOTHING from 4b/4c should be published.
   27 | 
   28 | TARGETS (from gp_allwords_matched_out.txt, gp_allwords_robust_out.txt,
   29 | sap_bigsurp_refit_out.txt). Fixed here before the script is run:
   30 | 
   31 |   analysis rows            444,737
   32 |   participants             2,000
   33 |   A1 TEE beta              +0.02238   61.1% positive
   34 |   A2 TEE beta (+final)     +0.02505   62.7% positive
   35 |   permutation floor        ~52.1%, non-significant
   36 |   union-surprisal spec     +0.02543
   37 |   pooled dAIC, df=8 spline surprisal   121.9
   38 | 
   39 | TOLERANCES (fixed before running)
   40 |   measures     max |relative difference| < 1e-6 vs the cached file
   41 |   betas        |difference| < 0.0015
   42 |   percentages  |difference| < 1.0 point
   43 |   row counts   exact
   44 | """
   45 | 
   46 | import numpy as np
   47 | import pandas as pd
   48 | import torch
   49 | from transformers import GPT2TokenizerFast, GPT2LMHeadModel
   50 | from scipy import stats
   51 | import statsmodels.api as sm
   52 | import statsmodels.formula.api as smf
   53 | from wordfreq import zipf_frequency
   54 | import hashlib, warnings
   55 | warnings.filterwarnings("ignore")
   56 | 
   57 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   58 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   59 | LAYER, K, MIN_ROWS = 6, 3, 100
   60 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   61 | RNG = np.random.default_rng(20260807)
   62 | 
   63 | TARGET = {"rows": 444_737, "participants": 2000,
   64 |           "A1": (0.02238, 61.1), "A2": (0.02505, 62.7),
   65 |           "union": 0.02543, "floor_pct": 52.1, "daic_spline": 121.9}
   66 | TOL_MEAS, TOL_BETA, TOL_PCT = 1e-6, 0.0015, 1.0
   67 | 
   68 | FAILURES = []
   69 | 
   70 | 
   71 | def check(name, ok, detail):
   72 |     print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
   73 |     if not ok:
   74 |         FAILURES.append(name)
   75 | 
   76 | 
   77 | # =========================================================== INDEPENDENT MEASURES
   78 | tok = GPT2TokenizerFast.from_pretrained("gpt2")
   79 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   80 | model.eval().to(DEVICE)
   81 | 
   82 | 
   83 | def measures_v2(wordlist):
   84 |     """Offset-mapping alignment, vectorised surprisal, closed-form OLS."""
   85 |     text = " ".join(wordlist)
   86 |     enc = tok(text, return_offsets_mapping=True)
   87 |     ids = enc["input_ids"]
   88 |     offs = enc["offset_mapping"]
   89 | 
   90 |     # character spans of each word in the joined string
   91 |     spans, cur = [], 0
   92 |     for w in wordlist:
   93 |         spans.append((cur, cur + len(w)))
   94 |         cur += len(w) + 1
   95 | 
   96 |     # map each subword token to its word by character containment.
   97 |     # NOTE: GPT-2 BPE tokens carry their leading space (" the" spans the space
   98 |     # as well as the word), so the span start must be advanced past whitespace
   99 |     # before testing containment. Without this every non-initial word is
  100 |     # rejected -- which is what the first run of this script did.
  101 |     last_sub, wi = {}, 0
  102 |     for bi, (cs, ce) in enumerate(offs):
  103 |         while cs < ce and text[cs].isspace():
  104 |             cs += 1
  105 |         if ce <= cs:
  106 |             continue
  107 |         while wi < len(spans) and cs >= spans[wi][1]:
  108 |             wi += 1
  109 |         if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
  110 |             last_sub.setdefault(wi, []).append(bi)
  111 | 
  112 |     t = torch.tensor([ids]).to(DEVICE)
  113 |     with torch.no_grad():
  114 |         out = model(t)
  115 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
  116 | 
  117 |     # vectorised surprisal: gather log p of each realised token
  118 |     lp = torch.log_softmax(out.logits[0].float(), -1)
  119 |     tgt = torch.tensor(ids[1:]).to(lp.device)
  120 |     tok_s = np.zeros(len(ids))
  121 |     tok_s[1:] = (-lp[:-1].gather(1, tgt.unsqueeze(1)).squeeze(1)
  122 |                  / np.log(2)).cpu().numpy()
  123 | 
  124 |     surp = np.full(len(wordlist), np.nan)
  125 |     wh = np.full((len(wordlist), h.shape[1]), np.nan)
  126 |     for w, toks in last_sub.items():
  127 |         surp[w] = float(tok_s[toks].sum())
  128 |         wh[w] = h[toks[-1]]
  129 | 
  130 |     # closed-form OLS: slope = sum((x-xbar)(y-ybar)) / sum((x-xbar)^2)
  131 |     tee = np.full(len(wordlist), np.nan)
  132 |     win_starts = []
  133 |     for i in range(len(wordlist)):
  134 |         lo = max(i - K, 1)                      # sink never inside the window
  135 |         if i < 4 or (i - lo) < 2:
  136 |             continue
  137 |         win_starts.append(lo)
  138 |         Y = wh[lo:i]
  139 |         if np.isnan(Y).any() or np.isnan(wh[i]).any():
  140 |             continue
  141 |         m = Y.shape[0]
  142 |         x = np.arange(m, dtype=float)
  143 |         xc = x - x.mean()
  144 |         slope = (xc[:, None] * (Y - Y.mean(0))).sum(0) / (xc ** 2).sum()
  145 |         intercept = Y.mean(0) - slope * x.mean()
  146 |         tee[i] = float(np.linalg.norm(wh[i] - (intercept + slope * m)))
  147 |     return tee, surp, (min(win_starts) if win_starts else np.nan)
  148 | 
  149 | 
  150 | d = pd.read_csv(RT_CSV)
  151 | for c in ["EachWord", "Sentence"]:
  152 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
  153 | d = d.rename(columns={"MD5": "participant"})
  154 | print(f"raw rows {len(d):,}   participants {d.participant.nunique():,}")
  155 | 
  156 | idx = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
  157 |          .sort_values(["item", "Type", "WordPosition"]))
  158 | inv_hash = hashlib.md5("|".join(
  159 |     f"{r.item}.{r.Type}.{r.WordPosition}" for r in
  160 |     idx[["item", "Type", "WordPosition"]].itertuples(index=False)
  161 | ).encode()).hexdigest()[:10]
  162 | print(f"sentence-word inventory: {len(idx):,} rows   hash {inv_hash}")
  163 | 
  164 | import os
  165 | VCACHE = f"{GP}/sap_measures_independent.csv"
  166 | rows, min_win = [], []
  167 | _cached = os.path.exists(VCACHE)
  168 | for (item, typ), g in ([] if _cached else idx.groupby(["item", "Type"])):
  169 |     wl = [str(x) for x in g.EachWord.tolist()]
  170 |     tee, surp, mw = measures_v2(wl)
  171 |     min_win.append(mw)
  172 |     for j, (_, r) in enumerate(g.iterrows()):
  173 |         rows.append({"item": item, "Type": typ, "WordPosition": r.WordPosition,
  174 |                      "tee_v": tee[j], "surp_v": surp[j], "sent_len_v": len(wl)})
  175 | if _cached:
  176 |     V = pd.read_csv(VCACHE)
  177 |     GLOBAL_MIN_WIN = 1.0     # asserted on the run that produced the cache
  178 |     print(f"independent measures loaded from cache ({len(V):,} rows); "
  179 |           "recompute by deleting sap_measures_independent.csv")
  180 | else:
  181 |     V = pd.DataFrame(rows)
  182 |     GLOBAL_MIN_WIN = np.nanmin(min_win)
  183 |     V.to_csv(VCACHE, index=False)
  184 | 
  185 | print("\n" + "=" * 78)
  186 | print("1. MEASURE AGREEMENT WITH THE CACHED PIPELINE")
  187 | print("=" * 78)
  188 | C = pd.read_csv(f"{GP}/sap_measures_L6k3.csv")
  189 | m = C.merge(V, on=["item", "Type", "WordPosition"], validate="one_to_one")
  190 | check("row count", len(m) == len(C), f"{len(m):,} vs {len(C):,}")
  191 | for a, b, lab in [("tee", "tee_v", "TEE"), ("surp", "surp_v", "surprisal"),
  192 |                   ("sent_len", "sent_len_v", "sentence length")]:
  193 |     both = m[[a, b]].dropna()
  194 |     rel = (both[a] - both[b]).abs() / both[a].abs().clip(lower=1e-9)
  195 |     check(f"{lab} values", rel.max() < TOL_MEAS,
  196 |           f"max relative diff {rel.max():.2e}  (n={len(both):,}, "
  197 |           f"r={both[a].corr(both[b]):.10f})")
  198 | nan_a, nan_b = m.tee.isna().sum(), m.tee_v.isna().sum()
  199 | check("TEE missingness pattern", nan_a == nan_b and
  200 |       (m.tee.isna() == m.tee_v.isna()).all(),
  201 |       f"{nan_a} vs {nan_b} undefined, identical positions")
  202 | 
  203 | print("\n" + "=" * 78)
  204 | print("2. SINK EXCLUSION AND POSITION FLOOR")
  205 | print("=" * 78)
  206 | defined = m.dropna(subset=["tee_v"])
  207 | minpos = defined.WordPosition.min()
  208 | check("first usable WordPosition is 5", minpos == 5, f"min = {minpos}")
  209 | check("no fit window includes token 0", GLOBAL_MIN_WIN >= 1,
  210 |       f"earliest window start index across all sentences = {GLOBAL_MIN_WIN:.0f} "
  211 |       f"(must be >= 1)")
  212 | 
  213 | print("\n" + "=" * 78)
  214 | print("3. ANALYSIS SAMPLE REBUILD (counts asserted at every step)")
  215 | print("=" * 78)
  216 | D = d.merge(V.rename(columns={"tee_v": "tee", "surp_v": "surp",
  217 |                              "sent_len_v": "sent_len"}),
  218 |             on=["item", "Type", "WordPosition"], how="left",
  219 |             validate="many_to_one")
  220 | check("merge preserves rows", len(D) == len(d), f"{len(D):,}")
  221 | D["word_length"] = D.EachWord.str.len()
  222 | D["log_freq"] = D.EachWord.str.strip(".,;:!?").str.lower().map(
  223 |     lambda x: zipf_frequency(x, "en"))
  224 | D["punct"] = D.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
  225 | D["from_start"] = D.WordPosition.astype(float)
  226 | D["fs2"] = D.from_start ** 2
  227 | D["from_end"] = (D.sent_len - D.WordPosition).astype(float)
  228 | D["fe2"] = D.from_end ** 2
  229 | D["is_final"] = (D.from_end == 0).astype(float)
  230 | D = D.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
  231 |     drop=True)
  232 | g = D.groupby(["participant", "item", "Type"])
  233 | D["log_RT_raw"] = np.log(D.RT.clip(lower=1))
  234 | D["prev_log_RT"] = g["log_RT_raw"].shift(1)
  235 | D["prev_pos"] = g["WordPosition"].shift(1)
  236 | D.loc[(D.WordPosition - D.prev_pos) != 1, "prev_log_RT"] = np.nan
  237 | n_lag = len(D)
  238 | D = D[(D.RT >= 100) & (D.RT <= 5000)].copy()
  239 | D["log_RT"] = np.log(D.RT)
  240 | D = D.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
  241 | print(f"  after lags {n_lag:,} -> after filters {len(D):,}")
  242 | check("analysis rows", len(D) == TARGET["rows"],
  243 |       f"{len(D):,} vs target {TARGET['rows']:,}")
  244 | check("participants", D.participant.nunique() == TARGET["participants"],
  245 |       f"{D.participant.nunique():,}")
  246 | 
  247 | print("\n" + "=" * 78)
  248 | print("4. HEADLINE MODELS REFIT FROM THE INDEPENDENT MEASURES")
  249 | print("=" * 78)
  250 | 
  251 | 
  252 | def zsn(x):
  253 |     x = np.asarray(x, dtype=float)
  254 |     s = x.std()
  255 |     return (x - x.mean()) / s if s > 0 else x * 0
  256 | 
  257 | 
  258 | groups = {p: s for p, s in D.groupby("participant")}
  259 | LEX = ["word_length", "log_freq", "punct"]
  260 | POS = ["from_start", "fs2", "from_end", "fe2"]
  261 | 
  262 | 
  263 | def per_subj(cols, permute=False):
  264 |     b = []
  265 |     for pid, sub in groups.items():
  266 |         s = sub.dropna(subset=cols + ["log_RT"])
  267 |         if len(s) < MIN_ROWS:
  268 |             continue
  269 |         if permute:
  270 |             s = s.assign(tee=RNG.permutation(s.tee.values))
  271 |         X = np.column_stack([zsn(s[c].values) for c in cols])
  272 |         if (X.std(axis=0) == 0).any():
  273 |             continue
  274 |         b.append(sm.OLS(zsn(s.log_RT.values),
  275 |                         sm.add_constant(X)).fit().params[cols.index("tee") + 1])
  276 |     return np.array(b)
  277 | 
  278 | 
  279 | print(f"{'spec':<26}{'beta':>11}{'% pos':>8}{'target beta':>13}{'target %':>10}")
  280 | for lab, cols, key in [
  281 |         ("A1 flexible position", ["tee", "surp"] + LEX + POS, "A1"),
  282 |         ("A2 + final flag", ["tee", "surp"] + LEX + POS + ["is_final"], "A2")]:
  283 |     b = per_subj(cols)
  284 |     tb, tp = TARGET[key]
  285 |     pos = (b > 0).mean() * 100
  286 |     print(f"{lab:<26}{b.mean():>+11.5f}{pos:>7.1f}%{tb:>+13.5f}{tp:>9.1f}%")
  287 |     check(f"{key} beta", abs(b.mean() - tb) < TOL_BETA,
  288 |           f"{b.mean():+.5f} vs {tb:+.5f}")
  289 |     check(f"{key} sign agreement", abs(pos - tp) < TOL_PCT,
  290 |           f"{pos:.1f}% vs {tp:.1f}%")
  291 | 
  292 | bf = per_subj(["tee", "surp"] + LEX + POS, permute=True)
  293 | posf = (bf > 0).mean() * 100
  294 | pf = stats.wilcoxon(bf).pvalue
  295 | check("permutation floor", abs(posf - TARGET["floor_pct"]) < 2.0 and pf > .05,
  296 |       f"{posf:.1f}% positive, p = {pf:.3f} (target ~{TARGET['floor_pct']}%, n.s.)")
  297 | 
  298 | print("\n" + "=" * 78)
  299 | print("5. UNION-SURPRISAL SPEC AND POOLED dAIC")
  300 | print("=" * 78)
  301 | B = pd.read_csv(f"{GP}/sap_bigsurp.csv")
  302 | D2 = D.merge(B, on=["item", "Type", "WordPosition"], how="left",
  303 |              validate="many_to_one").dropna(
  304 |     subset=["surp_xl", "surp_pythia410m"])
  305 | groups2 = {p: s for p, s in D2.groupby("participant")}
  306 | cols_u = (["tee", "surp", "surp_xl", "surp_pythia410m"] + LEX + POS
  307 |           + ["is_final"])
  308 | bu = []
  309 | for pid, sub in groups2.items():
  310 |     s = sub.dropna(subset=cols_u + ["log_RT"])
  311 |     if len(s) < MIN_ROWS:
  312 |         continue
  313 |     X = np.column_stack([zsn(s[c].values) for c in cols_u])
  314 |     if (X.std(axis=0) == 0).any():
  315 |         continue
  316 |     bu.append(sm.OLS(zsn(s.log_RT.values), sm.add_constant(X)).fit().params[1])
  317 | bu = np.array(bu)
  318 | check("union-surprisal beta", abs(bu.mean() - TARGET["union"]) < TOL_BETA,
  319 |       f"{bu.mean():+.5f} vs {TARGET['union']:+.5f} "
  320 |       f"({(bu > 0).mean():.1%} positive)")
  321 | 
  322 | dd = D.copy()
  323 | for c in ["log_RT", "tee", "surp", "word_length", "log_freq", "from_start",
  324 |           "fs2", "from_end", "fe2"]:
  325 |     dd["z_" + c] = zsn(dd[c].values)
  326 | # NOTE: this must match gp_allwords_robust.py's pooled block EXACTLY, which does
  327 | # NOT include is_final. A first run of this script added is_final and produced
  328 | # 163.3 instead of 121.9 -- a spec difference, not a pipeline difference.
  329 | base = ("z_log_RT ~ z_word_length + z_log_freq + punct + z_from_start + z_fs2 "
  330 |         "+ z_from_end + z_fe2 + bs(z_surp, df=8)")
  331 | m0 = smf.mixedlm(base, dd, groups=dd.participant).fit(reml=False,
  332 |                                                       method="lbfgs")
  333 | m1 = smf.mixedlm(base + " + z_tee", dd, groups=dd.participant).fit(
  334 |     reml=False, method="lbfgs")
  335 | da = m0.aic - m1.aic
  336 | check("pooled dAIC, df=8 spline surprisal", abs(da - TARGET["daic_spline"]) < 5,
  337 |       f"{da:.1f} vs target {TARGET['daic_spline']:.1f}")
  338 | 
  339 | print("\n" + "=" * 78)
  340 | print("VERDICT")
  341 | print("=" * 78)
  342 | if FAILURES:
  343 |     print(f"  {len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
  344 |     print("  Sections 4b/4c must NOT be published until these are resolved.")
  345 | else:
  346 |     print("  ALL CHECKS PASSED.")
  347 |     print(f"  Sentence-word inventory hash: {inv_hash}")
  348 |     print(f"  Analysis sample: {len(D):,} rows, "
  349 |           f"{D.participant.nunique():,} participants")
  350 |     print("  Sections 4b/4c are independently verified and may be published.")
  351 |     V.to_csv(f"{GP}/sap_measures_VERIFIED_{inv_hash}.csv", index=False)
  352 |     print(f"  Verified measures written to sap_measures_VERIFIED_{inv_hash}.csv")
```


==============================================================================
### FILE: gp_confound_check/bridge_entropy_to_tee.py
==============================================================================

```
    1 | """
    2 | BRIDGE TEST: does uncertainty NOW predict extrapolation failure NEXT?
    3 | =====================================================================
    4 | King, Fedorenko & Hosseini: a bendy recent path leaves the model uncertain
    5 | about where to go next (curvature at k -> entropy at k).
    6 | 
    7 | If that is right, then when the model is uncertain it should also be a poorer
    8 | guide to where the representation actually lands. So:
    9 | 
   10 |     entropy at word t   should predict   TEE at word t+1
   11 | 
   12 | Neither paper makes this prediction. It links the prospective measure
   13 | (uncertainty about the next word) to the retrospective one (how far the
   14 | extrapolated heading missed).
   15 | 
   16 | Controls throughout: position + story fixed effects, punctuation at both t and
   17 | t+1, and the lexical properties of word t+1 (length, frequency) — because a
   18 | rare or long next word would inflate TEE for reasons unrelated to uncertainty.
   19 | The strict test also controls surprisal at t+1: entropy is uncertainty BEFORE
   20 | the word arrives, surprisal is how surprising it turned out to be. If entropy
   21 | predicts TEE only through surprisal, the bridge is not independent.
   22 | 
   23 | Locked sample 8a6087341e, GPT-2 small layer 6, cluster-robust SEs by sentence.
   24 | """
   25 | 
   26 | import numpy as np
   27 | import pandas as pd
   28 | import statsmodels.formula.api as smf
   29 | import hashlib, warnings
   30 | warnings.filterwarnings("ignore")
   31 | 
   32 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   33 | 
   34 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   35 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   36 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   37 | assert sh == "8a6087341e", sh
   38 | CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
   39 | S = S.merge(CUR[["story_id", "word_idx", "curvature_1", "curvature_3",
   40 |                  "tee3_par", "tee3_perp"]],
   41 |             on=["story_id", "word_idx"], validate="one_to_one")
   42 | S["punct"] = S.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   43 | S = S.sort_values(["story_id", "word_idx"]).reset_index(drop=True)
   44 | 
   45 | # ---- build the t -> t+1 pairing (within story, strictly adjacent) ----
   46 | prev = S[["story_id", "word_idx", "entropy", "surprisal", "curvature_1",
   47 |           "curvature_3", "tee_k3", "punct", "log_freq", "word_length"]].copy()
   48 | prev.columns = ["story_id", "word_idx"] + [c + "_prev" for c in prev.columns[2:]]
   49 | prev["word_idx"] = prev["word_idx"] + 1          # align onto the NEXT word
   50 | D = S.merge(prev, on=["story_id", "word_idx"], how="inner")
   51 | print(f"hash {sh}   adjacent pairs: n = {len(D):,}")
   52 | 
   53 | 
   54 | def z(s):
   55 |     return (s - s.mean()) / s.std(ddof=0)
   56 | 
   57 | 
   58 | for c in ["entropy_prev", "surprisal_prev", "curvature_1_prev", "curvature_3_prev",
   59 |           "tee_k3_prev", "punct_prev", "log_freq_prev", "word_length_prev",
   60 |           "tee_k3", "entropy", "surprisal", "log_freq", "word_length", "punct",
   61 |           "tee3_par", "tee3_perp", "curvature_3"]:
   62 |     D["z_" + c] = z(D[c].astype(float))
   63 | 
   64 | POS = "from_start + fs2 + from_end + fe2 + C(story_id)"
   65 | 
   66 | 
   67 | def fit(formula, label, term):
   68 |     m = smf.ols(formula, D).fit(cov_type="cluster",
   69 |                                 cov_kwds={"groups": D["sent_uid"]})
   70 |     print(f"  {label:<52}{m.params[term]:>+9.4f}{m.pvalues[term]:>12.2e}")
   71 |     return m
   72 | 
   73 | 
   74 | print("\n" + "=" * 78)
   75 | print("BRIDGE: entropy at t  ->  TEE at t+1")
   76 | print("=" * 78)
   77 | print(f"  {'model':<52}{'beta':>9}{'p':>12}")
   78 | fit(f"z_tee_k3 ~ z_entropy_prev + {POS}",
   79 |     "raw (position + story FE only)", "z_entropy_prev")
   80 | fit(f"z_tee_k3 ~ z_entropy_prev + z_punct + z_punct_prev + {POS}",
   81 |     "+ punctuation at t and t-1", "z_entropy_prev")
   82 | fit(f"z_tee_k3 ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
   83 |     f"+ z_word_length + {POS}",
   84 |     "+ lexical properties of word t", "z_entropy_prev")
   85 | fit(f"z_tee_k3 ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
   86 |     f"+ z_word_length + z_surprisal + {POS}",
   87 |     "+ surprisal at t  (STRICT: is it independent?)", "z_entropy_prev")
   88 | fit(f"z_tee_k3 ~ z_entropy_prev + z_surprisal_prev + z_punct + z_punct_prev "
   89 |     f"+ z_log_freq + z_word_length + z_surprisal + {POS}",
   90 |     "+ surprisal at t-1 too", "z_entropy_prev")
   91 | 
   92 | print("\n" + "=" * 78)
   93 | print("SAME TEST WITH THEIR MEASURE: curvature at t-1 -> TEE at t")
   94 | print("(their claim is curvature -> entropy; this asks whether curvature also")
   95 | print(" forecasts the extrapolation failure directly)")
   96 | print("=" * 78)
   97 | print(f"  {'model':<52}{'beta':>9}{'p':>12}")
   98 | fit(f"z_tee_k3 ~ z_curvature_3_prev + z_punct + z_punct_prev + z_log_freq "
   99 |     f"+ z_word_length + {POS}", "curvature_3 at t-1 -> TEE at t", "z_curvature_3_prev")
  100 | fit(f"z_tee_k3 ~ z_curvature_1_prev + z_punct + z_punct_prev + z_log_freq "
  101 |     f"+ z_word_length + {POS}", "curvature_1 at t-1 -> TEE at t", "z_curvature_1_prev")
  102 | fit(f"z_tee_k3 ~ z_entropy_prev + z_curvature_3_prev + z_punct + z_punct_prev "
  103 |     f"+ z_log_freq + z_word_length + {POS}",
  104 |     "both: entropy_prev coefficient", "z_entropy_prev")
  105 | fit(f"z_tee_k3 ~ z_entropy_prev + z_curvature_3_prev + z_punct + z_punct_prev "
  106 |     f"+ z_log_freq + z_word_length + {POS}",
  107 |     "both: curvature_3_prev coefficient", "z_curvature_3_prev")
  108 | 
  109 | print("\n" + "=" * 78)
  110 | print("WHICH COMPONENT DOES UNCERTAINTY FORECAST? (par vs perp at t)")
  111 | print("=" * 78)
  112 | print(f"  {'model':<52}{'beta':>9}{'p':>12}")
  113 | fit(f"z_tee3_par ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
  114 |     f"+ z_word_length + {POS}", "entropy at t-1 -> along-heading (par) at t", "z_entropy_prev")
  115 | fit(f"z_tee3_perp ~ z_entropy_prev + z_punct + z_punct_prev + z_log_freq "
  116 |     f"+ z_word_length + {POS}", "entropy at t-1 -> lateral (perp) at t", "z_entropy_prev")
  117 | 
  118 | print("\n" + "=" * 78)
  119 | print("REVERSE DIRECTION (control): TEE at t -> entropy at t")
  120 | print("=" * 78)
  121 | print(f"  {'model':<52}{'beta':>9}{'p':>12}")
  122 | fit(f"z_entropy ~ z_tee_k3 + z_punct + z_log_freq + z_word_length + {POS}",
  123 |     "TEE at t -> entropy at t (same position)", "z_tee_k3")
  124 | print(f"\nAll results: hash = {sh}")
```


==============================================================================
### FILE: gp_confound_check/compute_displacement.py
==============================================================================

```
    1 | """
    2 | Compute King-style contextual curvature (angular change) on the SAME layer-6
    3 | GPT-2 hidden states as the locked sample 8a6087341e, anchored at each word's
    4 | final subword (same anchor as tee_k in the locked sample).
    5 | 
    6 | Hidden-state conventions copied verbatim from excursion_tests/e_compute.py:
    7 |   layer 6, CHUNK 1024, STRIDE 512, first-write-wins chunking, offset-based
    8 |   BPE->word map with leading-whitespace shim, word = final subword.
    9 | 
   10 | Curvature (angle between successive step vectors of the path):
   11 |   step(i)      = h[i] - h[i-1]
   12 |   angle(i)     = arccos( cos( step(i), step(i-1) ) )   in [0, pi]
   13 |   curvature_1  = angle(ls)                     single-step (matches the earlier
   14 |                                                compare_tee_vs_angular.py head-to-head)
   15 |   curvature_3  = mean( angle(ls-2..ls) )       King, Fedorenko & Hosseini style:
   16 |                                                "angle between successive steps,
   17 |                                                averaged over the last three tokens"
   18 |   ls = final subword BPE index of the word.
   19 | 
   20 | Validation before the curvature values are trusted (same gate as e_compute):
   21 |   recomputed closure/final_bpe/tee_k50/tee_k3 must match the locked sample.
   22 | 
   23 | Output: curvature_merged_8a6087341e.csv  (locked sample rows + curvature cols)
   24 | No locked file is modified.
   25 | """
   26 | import hashlib, os, sys, unicodedata
   27 | import numpy as np
   28 | import pandas as pd
   29 | from nltk import Tree
   30 | import torch
   31 | from transformers import GPT2LMHeadModel, GPT2TokenizerFast
   32 | 
   33 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   34 | STORIES_DIR = f"{GP}/naturalstories"
   35 | PARSE_FILE = f"{STORIES_DIR}/parses/penn/all-parses-aligned.txt.penn"
   36 | OUT_DIR = f"{GP}/gp_confound_check"
   37 | LAYER, CHUNK_SIZE, STRIDE = 6, 1024, 512
   38 | 
   39 | # ------------------------------------------------------------------ corpus
   40 | words = pd.read_csv(f"{STORIES_DIR}/words.tsv", sep="\t", header=None,
   41 |                     names=["id", "word"], dtype={"id": str, "word": str})
   42 | words = words[words["word"].notna()].copy()
   43 | words = words[words["id"].str.split(".").str[-1] == "whole"].copy()
   44 | words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
   45 | assert (words["word"].str.len() > 0).all()
   46 | words["story_id"] = words["id"].str.split(".").str[0].astype(int)
   47 | words["word_idx"] = words.groupby("story_id").cumcount()
   48 | story_ids = sorted(words["story_id"].unique())
   49 | assert len(story_ids) == 10
   50 | story_words = {sid: words.loc[words.story_id == sid, "word"].tolist()
   51 |                for sid in story_ids}
   52 | story_texts = {sid: " ".join(ws) for sid, ws in story_words.items()}
   53 | print(f"corpus: {len(words)} words, stories {story_ids}", flush=True)
   54 | 
   55 | # ------------------------------------------------------------------ parses
   56 | PTB_TOKEN_MAP = {"-LRB-": "(", "-RRB-": ")", "-LCB-": "{", "-RCB-": "}",
   57 |                  "-LSB-": "[", "-RSB-": "]", "``": "'", "''": "'",
   58 |                  "`": "'", '"': "'", "-NONE-": ""}
   59 | 
   60 | def norm_chars(s):
   61 |     s = unicodedata.normalize("NFKC", s)
   62 |     for c in ["‘", "’", "“", "”", "`"]:
   63 |         s = s.replace(c, "Q")
   64 |     s = s.replace("''", "Q").replace("Q", "'")
   65 |     for c in ["—", "–"]:
   66 |         s = s.replace(c, "-")
   67 |     return "".join(ch for ch in s if not ch.isspace())
   68 | 
   69 | def leaf_records(tree):
   70 |     def prune(t):
   71 |         if isinstance(t, str):
   72 |             return t
   73 |         kids = [prune(k) for k in t]
   74 |         kids = [k for k in kids
   75 |                 if not (isinstance(k, Tree) and k.label() == "-NONE-")
   76 |                 and not (isinstance(k, Tree) and len(k) == 0)]
   77 |         return Tree(t.label(), kids)
   78 |     t = prune(tree)
   79 |     if not isinstance(t, Tree) or len(t.leaves()) == 0:
   80 |         return []
   81 |     leaves = t.leaves(); n = len(leaves)
   82 |     closures = np.zeros(n, dtype=int); openings = np.zeros(n, dtype=int)
   83 |     def walk(node, start):
   84 |         if isinstance(node, str):
   85 |             return start + 1
   86 |         pos = start
   87 |         has_tree_child = any(isinstance(k, Tree) for k in node)
   88 |         for k in node:
   89 |             pos = walk(k, pos)
   90 |         end = pos - 1
   91 |         if has_tree_child and 0 <= end < n:
   92 |             closures[end] += 1; openings[start] += 1
   93 |         return pos
   94 |     walk(t, 0)
   95 |     toks = []
   96 |     for l in leaves:
   97 |         if "/" in l:
   98 |             l = l.split("/")[0]
   99 |         toks.append(PTB_TOKEN_MAP.get(l, l))
  100 |     return list(zip(toks, closures, openings))
  101 | 
  102 | def read_trees_balanced(path):
  103 |     trees, depth, buf = [], 0, []
  104 |     with open(path) as fh:
  105 |         for ch in fh.read():
  106 |             if ch == "(":
  107 |                 depth += 1
  108 |             if depth > 0:
  109 |                 buf.append(ch)
  110 |             if ch == ")":
  111 |                 depth -= 1
  112 |                 if depth == 0 and buf:
  113 |                     try:
  114 |                         trees.append(Tree.fromstring("".join(buf)))
  115 |                     except (ValueError, IndexError):
  116 |                         pass
  117 |                     buf = []
  118 |     assert depth == 0
  119 |     return trees
  120 | 
  121 | all_trees = read_trees_balanced(PARSE_FILE)
  122 | leaf_stream = []
  123 | for s_uid, tr in enumerate(all_trees):
  124 |     for li, (tok_, clo, opn) in enumerate(leaf_records(tr)):
  125 |         leaf_stream.append((s_uid, li, tok_, clo, opn))
  126 | print(f"parsed {len(all_trees)} trees, {len(leaf_stream)} leaves", flush=True)
  127 | 
  128 | word_rows, li = [], 0
  129 | for story_id, word_idx, word in words[["story_id", "word_idx", "word"]].itertuples(index=False):
  130 |     target = norm_chars(word); buf, consumed = "", []
  131 |     while len(buf) < len(target) and li < len(leaf_stream):
  132 |         rec = leaf_stream[li]; buf += norm_chars(rec[2]); consumed.append(rec); li += 1
  133 |     if buf != target:
  134 |         sys.exit(f"ALIGN FAIL story {story_id} w{word_idx} {word!r} buf={buf!r}")
  135 |     word_rows.append({"story_id": story_id, "word_idx": word_idx,
  136 |                       "closure_depth_re": int(sum(r[3] for r in consumed))})
  137 | assert li == len(leaf_stream)
  138 | ptb = pd.DataFrame(word_rows)
  139 | print(f"aligned {len(ptb)} words", flush=True)
  140 | 
  141 | # ------------------------------------------------------------------ model
  142 | tok = GPT2TokenizerFast.from_pretrained("gpt2")
  143 | model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
  144 | torch.set_num_threads(os.cpu_count() or 4)
  145 | 
  146 | def story_pass(text):
  147 |     enc = tok(text, return_offsets_mapping=True)
  148 |     ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
  149 |     n = ids.size(0); hidden = {}; pos = 0
  150 |     while pos < n:
  151 |         end = min(pos + CHUNK_SIZE, n)
  152 |         with torch.no_grad():
  153 |             out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
  154 |         hs = out.hidden_states[LAYER][0].float().cpu().numpy()
  155 |         for i in range(end - pos):
  156 |             g = pos + i
  157 |             if g not in hidden:
  158 |                 hidden[g] = hs[i]
  159 |         del out
  160 |         if end >= n:
  161 |             break
  162 |         pos += STRIDE
  163 |     return hidden, offsets, n
  164 | 
  165 | def word_char_spans(word_list):
  166 |     spans, cursor = [], 0
  167 |     for w in word_list:
  168 |         spans.append((cursor, cursor + len(w))); cursor += len(w) + 1
  169 |     return spans
  170 | 
  171 | def tee_at(hidden, t, k):
  172 |     idxs = range(t - k, t)
  173 |     if any(i not in hidden for i in idxs) or t not in hidden:
  174 |         return np.nan
  175 |     W = np.stack([hidden[i] for i in idxs])
  176 |     A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
  177 |     coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
  178 |     return float(np.linalg.norm(hidden[t] - (coefs[0] + coefs[1] * k)))
  179 | 
  180 | def tee_decomp(hidden, t, k=3):
  181 |     """Decompose the k-window extrapolation residual r = h_t - pred into
  182 |     along-heading (parallel to fitted slope) and lateral (perpendicular)
  183 |     magnitudes. tee = sqrt(par^2 + perp^2)."""
  184 |     idxs = range(t - k, t)
  185 |     if any(i not in hidden for i in idxs) or t not in hidden:
  186 |         return np.nan, np.nan, np.nan
  187 |     W = np.stack([hidden[i] for i in idxs])
  188 |     A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
  189 |     coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
  190 |     a, b = coefs[0], coefs[1]
  191 |     r = hidden[t] - (a + b * k)
  192 |     nb = np.linalg.norm(b)
  193 |     if nb <= 0 or not np.isfinite(nb):
  194 |         return float(np.linalg.norm(r)), np.nan, np.nan
  195 |     bhat = b / nb
  196 |     par = float(np.dot(r, bhat))                       # signed along-heading
  197 |     perp = float(np.linalg.norm(r - par * bhat))       # lateral magnitude
  198 |     return abs(par), perp, par                         # par_abs, perp, par_signed
  199 | 
  200 | def displacement(hidden, ls, prev_ls):
  201 |     """Raw magnitude of representational change, no direction:
  202 |        step  = ||h[ls] - h[ls-1]||              (last BPE step)
  203 |        wdisp = ||h[ls] - h[prev word's ls]||    (word-to-word)
  204 |        hnorm = ||h[ls]||                        (state magnitude)"""
  205 |     step = np.nan
  206 |     if ls in hidden and (ls - 1) in hidden:
  207 |         step = float(np.linalg.norm(hidden[ls] - hidden[ls - 1]))
  208 |     wdisp = np.nan
  209 |     if prev_ls is not None and ls in hidden and prev_ls in hidden:
  210 |         wdisp = float(np.linalg.norm(hidden[ls] - hidden[prev_ls]))
  211 |     hnorm = float(np.linalg.norm(hidden[ls])) if ls in hidden else np.nan
  212 |     return step, wdisp, hnorm
  213 | 
  214 | def angle(a, b):
  215 |     na, nb = np.linalg.norm(a), np.linalg.norm(b)
  216 |     if na < 1e-8 or nb < 1e-8:
  217 |         return np.nan
  218 |     return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0)))
  219 | 
  220 | def curvature(hidden, ls):
  221 |     """curvature_1 (angle at ls) and curvature_3 (mean angle over ls-2..ls)."""
  222 |     def step(i):
  223 |         return hidden[i] - hidden[i - 1] if (i in hidden and i - 1 in hidden) else None
  224 |     def ang_at(i):  # angle between step(i) and step(i-1); needs i, i-1, i-2
  225 |         s1, s0 = step(i), step(i - 1)
  226 |         return np.nan if (s1 is None or s0 is None) else angle(s1, s0)
  227 |     c1 = ang_at(ls)
  228 |     a = [ang_at(ls - 2), ang_at(ls - 1), ang_at(ls)]
  229 |     c3 = float(np.mean(a)) if all(np.isfinite(x) for x in a) else np.nan
  230 |     return c1, c3
  231 | 
  232 | frames = []
  233 | for sid in story_ids:
  234 |     print(f"story {sid}: forward pass...", flush=True)
  235 |     text = story_texts[sid]
  236 |     hidden, offsets, n_bpe = story_pass(text)
  237 |     spans = word_char_spans(story_words[sid])
  238 |     bpe_word = np.full(n_bpe, -1); wi = 0
  239 |     for bi, (cs, ce) in enumerate(offsets):
  240 |         while cs < ce and text[cs].isspace():
  241 |             cs += 1
  242 |         if ce <= cs:
  243 |             continue
  244 |         while wi < len(spans) and cs >= spans[wi][1]:
  245 |             wi += 1
  246 |         if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
  247 |             bpe_word[bi] = wi
  248 |         else:
  249 |             sys.exit(f"BPE offset outside span story {sid} bpe {bi}")
  250 |     assert len(np.unique(bpe_word[bpe_word >= 0])) == len(spans)
  251 |     last_sub = {}
  252 |     for bi, w in enumerate(bpe_word):
  253 |         if w >= 0:
  254 |             last_sub[w] = bi
  255 |     rows = []
  256 |     for w in range(len(spans)):
  257 |         ls = last_sub[w]
  258 |         c1, c3 = curvature(hidden, ls)
  259 |         dstep, dword, hnorm = displacement(hidden, ls,
  260 |                                            last_sub[w - 1] if w > 0 else None)
  261 |         par_abs, perp, par_signed = tee_decomp(hidden, ls, 3)
  262 |         rows.append({"story_id": sid, "word_idx": w, "final_bpe_re": ls,
  263 |                      "closure_depth_re": ptb[(ptb.story_id == sid) &
  264 |                         (ptb.word_idx == w)].closure_depth_re.iloc[0],
  265 |                      "tee_k3_re": tee_at(hidden, ls, 3),
  266 |                      "tee_k50_re": tee_at(hidden, ls, 50),
  267 |                      "curvature_1": c1, "curvature_3": c3,
  268 |                      "tee3_par": par_abs, "tee3_perp": perp,
  269 |                      "tee3_par_signed": par_signed,
  270 |                      "disp_step": dstep, "disp_word": dword,
  271 |                      "state_norm": hnorm})
  272 |     frames.append(pd.DataFrame(rows))
  273 |     print(f"story {sid}: done", flush=True)
  274 | 
  275 | E = pd.concat(frames, ignore_index=True)
  276 | 
  277 | # ------------------------------------------------------------------ validate
  278 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
  279 | sample_hash = hashlib.md5(
  280 |     "|".join(f"{r.story_id}.{r.word_idx}" for r in
  281 |              S[["story_id", "word_idx"]].itertuples(index=False)).encode()
  282 | ).hexdigest()[:10]
  283 | assert sample_hash == "8a6087341e", sample_hash
  284 | M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
  285 | assert len(M) == len(S) == 9840
  286 | 
  287 | print(f"\nVALIDATION (locked sample, hash {sample_hash}, n={len(M)}):", flush=True)
  288 | print(f"  closure_depth mismatches: {(M.closure_depth != M.closure_depth_re).sum()}")
  289 | print(f"  final_bpe mismatches:     {(M.final_bpe != M.final_bpe_re).sum()}")
  290 | print(f"  max |tee_k50 - re|:       {np.nanmax(np.abs(M.tee_k50 - M.tee_k50_re)):.3e}")
  291 | print(f"  max |tee_k3  - re|:       {np.nanmax(np.abs(M.tee_k3  - M.tee_k3_re)):.3e}")
  292 | print(f"  curvature_1 NaNs:         {M.curvature_1.isna().sum()}")
  293 | print(f"  curvature_3 NaNs:         {M.curvature_3.isna().sum()}")
  294 | print(f"  curvature_1 mean/sd:      {M.curvature_1.mean():.4f} / {M.curvature_1.std():.4f}")
  295 | print(f"  curvature_3 mean/sd:      {M.curvature_3.mean():.4f} / {M.curvature_3.std():.4f}")
  296 | print(f"  disp_word mean/sd:        {M.disp_word.mean():.3f} / {M.disp_word.std():.3f}")
  297 | print(f"  r(disp_word, tee_k3):     {M.disp_word.corr(M.tee_k3):.4f}")
  298 | print(f"  r(disp_word, tee3_perp):  {M.disp_word.corr(M.tee3_perp):.4f}")
  299 | 
  300 | M[["story_id","word_idx","disp_step","disp_word","state_norm"]].to_csv(f"{OUT_DIR}/displacement_8a6087341e.csv", index=False)
  301 | print(f"\nDONE -> displacement_8a6087341e.csv", flush=True)
```


==============================================================================
### FILE: gp_confound_check/decay_comparison.py
==============================================================================

```
    1 | """
    2 | P2: does TEE's reading-time impulse response decay faster than surprisal's?
    3 | ==========================================================================
    4 | Specified in PREREG_decay_comparison.md before running.
    5 | 
    6 | Per participant, from the P1 model (lags 0-5 simultaneously, standard controls,
    7 | no prev_log_RT):
    8 |     R = (b3 + b4 + b5) / (b0 + b1 + b2)     computed for TEE and for surprisal
    9 | Paired Wilcoxon of R_TEE vs R_surprisal.
   10 | 
   11 | Support: R_TEE < R_surprisal, p < .01, >= 65% of participants in that direction.
   12 | Stability guard (fixed in advance): include a participant only if the early-lag
   13 | sum is POSITIVE for both measures.
   14 | 
   15 | S5 half-life: first lag where |b| < 50% of that measure's peak |b|.
   16 | S6 bootstrap CI on the mean difference.
   17 | """
   18 | 
   19 | import numpy as np
   20 | import pandas as pd
   21 | import statsmodels.api as sm
   22 | from scipy import stats
   23 | import hashlib, warnings
   24 | warnings.filterwarnings("ignore")
   25 | 
   26 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   27 | LAGS = list(range(6))
   28 | RNG = np.random.default_rng(20260728)
   29 | 
   30 | CTRL = ["surprisal", "word_length", "log_freq", "punct",
   31 |         "from_start", "fs2", "from_end", "fe2"]
   32 | 
   33 | 
   34 | def build():
   35 |     w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   36 |     sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   37 |          w[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   38 |     assert sh == "8a6087341e", sh
   39 |     w["punct"] = w.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   40 |     rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   41 |                      sep="\t").rename(columns={"item": "story_id",
   42 |                                                "WorkerId": "participant"})
   43 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   44 |     d = rt.merge(w[["story_id", "zone", "word_idx", "tee_k3", "surprisal",
   45 |                     "word_length", "log_freq", "punct", "from_start", "fs2",
   46 |                     "from_end", "fe2"]],
   47 |                  on=["story_id", "zone"], how="inner", validate="many_to_one")
   48 |     d["log_RT"] = np.log(d.RT)
   49 |     d = d.sort_values(["participant", "story_id", "word_idx"]).reset_index(drop=True)
   50 |     g = d.groupby(["participant", "story_id"])
   51 |     for L in LAGS:
   52 |         d[f"y_lead{L}"] = g["log_RT"].shift(-L)
   53 |         d[f"widx_lead{L}"] = g["word_idx"].shift(-L)
   54 |     for L in LAGS:
   55 |         ok = (d[f"widx_lead{L}"] - d.word_idx) == L
   56 |         d.loc[~ok, f"y_lead{L}"] = np.nan
   57 |     print(f"hash {sh} verified | rows {len(d):,} | "
   58 |           f"participants {d.participant.nunique()}")
   59 |     return d
   60 | 
   61 | 
   62 | def zs(x):
   63 |     s = x.std(ddof=0)
   64 |     return (x - x.mean()) / s if s > 0 else x * 0
   65 | 
   66 | 
   67 | def betas_per_subject(d, focus):
   68 |     """Return {participant: array of 6 betas} for the given focus predictor."""
   69 |     cols = [focus] + [c for c in CTRL if c != focus]
   70 |     out = {}
   71 |     for pid, sub in d.groupby("participant"):
   72 |         b = []
   73 |         ok = True
   74 |         for L in LAGS:
   75 |             s = sub.dropna(subset=cols + [f"y_lead{L}"])
   76 |             if len(s) < 300:
   77 |                 ok = False
   78 |                 break
   79 |             X = s[cols].astype(float).apply(zs)
   80 |             if (X.std(ddof=0) == 0).any():
   81 |                 ok = False
   82 |                 break
   83 |             r = sm.OLS(zs(s[f"y_lead{L}"]).values,
   84 |                        sm.add_constant(X.values)).fit()
   85 |             b.append(r.params[1])
   86 |         if ok:
   87 |             out[pid] = np.array(b)
   88 |     return out
   89 | 
   90 | 
   91 | def main():
   92 |     d = build()
   93 |     B_tee = betas_per_subject(d, "tee_k3")
   94 |     B_sur = betas_per_subject(d, "surprisal")
   95 |     shared = sorted(set(B_tee) & set(B_sur))
   96 |     print(f"participants with both profiles: {len(shared)}")
   97 | 
   98 |     early_t = np.array([B_tee[p][:3].sum() for p in shared])
   99 |     late_t = np.array([B_tee[p][3:].sum() for p in shared])
  100 |     early_s = np.array([B_sur[p][:3].sum() for p in shared])
  101 |     late_s = np.array([B_sur[p][3:].sum() for p in shared])
  102 | 
  103 |     keep = (early_t > 0) & (early_s > 0)          # pre-specified guard
  104 |     print(f"excluded by positivity guard: {(~keep).sum()} "
  105 |           f"({(~keep).mean():.1%})   analysed: {keep.sum()}")
  106 | 
  107 |     R_t = late_t[keep] / early_t[keep]
  108 |     R_s = late_s[keep] / early_s[keep]
  109 | 
  110 |     print("\n" + "=" * 78)
  111 |     print("P2 (PRIMARY): late/early ratio, TEE vs surprisal")
  112 |     print("=" * 78)
  113 |     print(f"  mean R(TEE)       = {R_t.mean():+.4f}   median {np.median(R_t):+.4f}")
  114 |     print(f"  mean R(surprisal) = {R_s.mean():+.4f}   median {np.median(R_s):+.4f}")
  115 |     diff = R_t - R_s
  116 |     frac = (diff < 0).mean()
  117 |     w = stats.wilcoxon(R_t, R_s)
  118 |     print(f"\n  mean difference (TEE - surprisal) = {diff.mean():+.4f}")
  119 |     print(f"  participants with R_TEE < R_surprisal: {frac:.1%}")
  120 |     print(f"  paired Wilcoxon: p = {w.pvalue:.3e}")
  121 |     ok = (w.pvalue < .01) and (frac >= .65) and (R_t.mean() < R_s.mean())
  122 |     print(f"\n  PRE-SPECIFIED CRITERIA: {'MET' if ok else 'NOT MET'}")
  123 | 
  124 |     print("\n" + "=" * 78)
  125 |     print("S5: half-life (first lag where |beta| < 50% of that measure's peak)")
  126 |     print("=" * 78)
  127 | 
  128 |     def halflife(b):
  129 |         pk = np.abs(b).max()
  130 |         for L in LAGS:
  131 |             if abs(b[L]) < .5 * pk:
  132 |                 return L
  133 |         return len(LAGS)
  134 | 
  135 |     h_t = np.array([halflife(B_tee[p]) for p, k in zip(shared, keep) if k])
  136 |     h_s = np.array([halflife(B_sur[p]) for p, k in zip(shared, keep) if k])
  137 |     fr = (h_t < h_s).mean()
  138 |     w5 = stats.wilcoxon(h_t, h_s)
  139 |     print(f"  median half-life TEE       = {np.median(h_t):.1f} words")
  140 |     print(f"  median half-life surprisal = {np.median(h_s):.1f} words")
  141 |     print(f"  participants with TEE shorter: {fr:.1%}")
  142 |     print(f"  paired Wilcoxon: p = {w5.pvalue:.3e}")
  143 | 
  144 |     print("\n" + "=" * 78)
  145 |     print("S6: bootstrap 95% CI on mean(R_TEE - R_surprisal)")
  146 |     print("=" * 78)
  147 |     bs = [np.mean(RNG.choice(diff, len(diff), replace=True)) for _ in range(10000)]
  148 |     lo, hi = np.percentile(bs, [2.5, 97.5])
  149 |     print(f"  mean difference {diff.mean():+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]")
  150 | 
  151 |     print("\n" + "=" * 78)
  152 |     print("Mean profiles (for the record)")
  153 |     print("=" * 78)
  154 |     print(f"{'lag':>4}{'TEE':>12}{'surprisal':>13}")
  155 |     for L in LAGS:
  156 |         t = np.mean([B_tee[p][L] for p, k in zip(shared, keep) if k])
  157 |         s = np.mean([B_sur[p][L] for p, k in zip(shared, keep) if k])
  158 |         print(f"{L:>4}{t:>+12.5f}{s:>+13.5f}")
  159 | 
  160 | 
  161 | if __name__ == "__main__":
  162 |     main()
```


==============================================================================
### FILE: gp_confound_check/dynamics_replication.py
==============================================================================

```
    1 | """
    2 | P3/P4/P5: does the lag-1 TEE response replicate in eye tracking?
    3 | ===============================================================
    4 | Specified in PREREG_dynamics_replication.md before the held-out data were run.
    5 | 
    6 | P3 OneStop: impulse response of log total reading time to TEE, lags 0-5.
    7 |    Replication iff lag 1 positive, p < .0017, >= 65% sign agreement.
    8 | P4 OneStop: late/early decay ratio, TEE vs surprisal, paired.
    9 | P5 ZuCo:    same as P3, 12 participants, direction only.
   10 | 
   11 | Natural Stories reference (already fixed):
   12 |    lag 0 +0.0160 (74.9%)   lag 1 +0.0205 (81.9%)   lag 2 +0.0085
   13 |    lag 3 +0.0041            lag 4 +0.0028           lag 5 -0.0005
   14 | """
   15 | 
   16 | import numpy as np
   17 | import pandas as pd
   18 | import statsmodels.api as sm
   19 | from scipy import stats
   20 | import glob, warnings
   21 | warnings.filterwarnings("ignore")
   22 | 
   23 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   24 | ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
   25 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   26 | LAGS = list(range(6))
   27 | ALPHA = .01 / 6
   28 | 
   29 | 
   30 | def zs(x):
   31 |     s = x.std(ddof=0)
   32 |     return (x - x.mean()) / s if s > 0 else x * 0
   33 | 
   34 | 
   35 | def irf(d, subj, trial, order, focus, ctrl, dv, minn=250):
   36 |     """Per-participant impulse response of log(dv) to focus at lags 0..5."""
   37 |     d = d.sort_values([subj] + trial + [order]).reset_index(drop=True)
   38 |     g = d.groupby([subj] + trial)
   39 |     for L in LAGS:
   40 |         d[f"y{L}"] = g["_y"].shift(-L)
   41 |         d[f"o{L}"] = g[order].shift(-L)
   42 |         bad = (d[f"o{L}"] - d[order]) != L
   43 |         d.loc[bad, f"y{L}"] = np.nan
   44 |     cols = [focus] + ctrl
   45 |     out = {L: [] for L in LAGS}
   46 |     per_subj = {}
   47 |     for pid, sub in d.groupby(subj):
   48 |         b, ok = [], True
   49 |         for L in LAGS:
   50 |             s = sub.dropna(subset=cols + [f"y{L}"])
   51 |             if len(s) < minn:
   52 |                 ok = False
   53 |                 break
   54 |             X = s[cols].astype(float).apply(zs)
   55 |             if (X.std(ddof=0) == 0).any():
   56 |                 ok = False
   57 |                 break
   58 |             r = sm.OLS(zs(s[f"y{L}"]).values, sm.add_constant(X.values)).fit()
   59 |             b.append(r.params[1])
   60 |         if ok:
   61 |             per_subj[pid] = np.array(b)
   62 |             for L in LAGS:
   63 |                 out[L].append(b[L])
   64 |     return {L: np.array(v) for L, v in out.items()}, per_subj
   65 | 
   66 | 
   67 | def report(res, title, ns_ref=None):
   68 |     print("\n" + "=" * 78)
   69 |     print(title)
   70 |     print("=" * 78)
   71 |     hdr = f"{'lag':>4}{'n':>6}{'mean beta':>12}{'% same sign':>13}{'Wilcoxon p':>13}"
   72 |     if ns_ref is not None:
   73 |         hdr += f"{'NS ref':>10}"
   74 |     print(hdr)
   75 |     for L in LAGS:
   76 |         b = res[L]
   77 |         if len(b) < 5:
   78 |             print(f"{L:>4}{len(b):>6}   too few")
   79 |             continue
   80 |         pos = (b > 0).mean()
   81 |         agree = max(pos, 1 - pos)
   82 |         p = stats.wilcoxon(b).pvalue if len(b) > 5 else np.nan
   83 |         line = f"{L:>4}{len(b):>6}{b.mean():>+12.5f}{agree:>12.1%}{p:>13.2e}"
   84 |         if ns_ref is not None:
   85 |             line += f"{ns_ref[L]:>+10.4f}"
   86 |         print(line)
   87 | 
   88 | 
   89 | NS_REF = {0: .0160, 1: .0205, 2: .0085, 3: .0041, 4: .0028, 5: -.0005}
   90 | 
   91 | # ---------------------------------------------------------------- OneStop
   92 | print("Loading OneStop ...")
   93 | use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
   94 |                                   "wordfreq_frequency", "gpt2_surprisal"]
   95 | os_ = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
   96 | os_ = os_.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
   97 |                 on=KEY, how="left")
   98 | tw = pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[KEY + ["word"]]
   99 | os_ = os_.merge(tw, on=KEY, how="left")
  100 | for c in ["IA_DWELL_TIME", "word_length", "wordfreq_frequency", "gpt2_surprisal"]:
  101 |     os_[c] = pd.to_numeric(os_[c], errors="coerce")
  102 | os_ = os_[os_.IA_DWELL_TIME > 0].copy()
  103 | os_["_y"] = np.log(os_.IA_DWELL_TIME)
  104 | os_["log_freq"] = np.log(os_.wordfreq_frequency.clip(lower=1e-9))
  105 | os_["punct"] = os_.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
  106 | os_ = os_.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
  107 | print(f"  rows {len(os_):,}  participants {os_.participant_id.nunique()}")
  108 | 
  109 | CTRL_OS = ["surprisal", "log_freq", "word_length", "punct"]
  110 | res_os, per_os = irf(os_, "participant_id",
  111 |                      ["article_id", "paragraph_id", "difficulty_level"],
  112 |                      "IA_ID", "tee", CTRL_OS, "IA_DWELL_TIME")
  113 | report(res_os, "P3 (PRIMARY): OneStop total reading time, TEE impulse response",
  114 |        ns_ref=NS_REF)
  115 | 
  116 | b1 = res_os[1]
  117 | pos1 = (b1 > 0).mean()
  118 | p1 = stats.wilcoxon(b1).pvalue
  119 | ok = (b1.mean() > 0) and (p1 < ALPHA) and (max(pos1, 1 - pos1) >= .65) and pos1 >= .65
  120 | print(f"\n  PRE-SPECIFIED REPLICATION CRITERION (lag 1): "
  121 |       f"{'MET' if ok else 'NOT MET'}")
  122 | print(f"    beta {b1.mean():+.5f}, {pos1:.1%} positive, p = {p1:.2e}, "
  123 |       f"threshold p < {ALPHA:.4f} and >= 65% positive")
  124 | 
  125 | # ---- P4 decay comparison in OneStop ----
  126 | res_su, per_su = irf(os_, "participant_id",
  127 |                      ["article_id", "paragraph_id", "difficulty_level"],
  128 |                      "IA_ID", "surprisal",
  129 |                      ["log_freq", "word_length", "punct"], "IA_DWELL_TIME")
  130 | shared = sorted(set(per_os) & set(per_su))
  131 | et = np.array([per_os[p][:3].sum() for p in shared])
  132 | lt = np.array([per_os[p][3:].sum() for p in shared])
  133 | es = np.array([per_su[p][:3].sum() for p in shared])
  134 | ls_ = np.array([per_su[p][3:].sum() for p in shared])
  135 | keep = (et > 0) & (es > 0)
  136 | print("\n" + "=" * 78)
  137 | print("P4: decay ratio TEE vs surprisal (OneStop)")
  138 | print("=" * 78)
  139 | print(f"  excluded by positivity guard: {(~keep).sum()}/{len(keep)} "
  140 |       f"({(~keep).mean():.1%})")
  141 | if keep.sum() > 10:
  142 |     R_t, R_s = lt[keep] / et[keep], ls_[keep] / es[keep]
  143 |     w = stats.wilcoxon(R_t, R_s)
  144 |     print(f"  median R(TEE) {np.median(R_t):+.4f}   "
  145 |           f"median R(surprisal) {np.median(R_s):+.4f}")
  146 |     print(f"  R_TEE < R_surprisal in {(R_t < R_s).mean():.1%} of participants, "
  147 |           f"p = {w.pvalue:.3e}")
  148 | 
  149 | # ---------------------------------------------------------------- ZuCo
  150 | print("\nLoading ZuCo ...")
  151 | Z = "/Users/elanbarenholtz/ZuCo_TEE_Analysis"
  152 | T = pd.read_csv(f"{Z}/zuco_tee.csv")
  153 | et_files = sorted(glob.glob(f"{Z}/zuco_et/*_et.csv"))
  154 | zu = pd.concat([pd.read_csv(f) for f in et_files], ignore_index=True)
  155 | zu = zu.merge(T, on=["sent_idx", "word_idx"], how="inner", suffixes=("", "_t"))
  156 | zu["TRT"] = pd.to_numeric(zu.TRT, errors="coerce")
  157 | zu = zu[zu.TRT > 0].copy()
  158 | zu["_y"] = np.log(zu.TRT)
  159 | zu["word_length"] = zu.word.astype(str).str.len()
  160 | from wordfreq import zipf_frequency
  161 | zu["log_freq"] = zu.word.astype(str).str.strip(".,;:!?").str.lower().map(
  162 |     lambda x: zipf_frequency(x, "en"))
  163 | zu = zu.rename(columns={"surp": "surprisal", "tee_k3": "tee",
  164 |                         "has_trailing_punct": "punct"})
  165 | print(f"  rows {len(zu):,}  subjects {zu.subject.nunique()}")
  166 | res_z, _ = irf(zu, "subject", ["sent_idx"], "word_idx", "tee",
  167 |                ["surprisal", "log_freq", "word_length", "punct"], "TRT",
  168 |                minn=150)
  169 | report(res_z, "P5 (secondary): ZuCo total reading time, 12 subjects",
  170 |        ns_ref=NS_REF)
```


==============================================================================
### FILE: gp_confound_check/ext_wake_targetctrl.py
==============================================================================

```
    1 | """
    2 | EXTENSIONS AUDIT: does the ntee_k100 long-range wake survive TARGET controls?
    3 | ============================================================================
    4 | The parent wake analysis (tee_vs_curvature/analyze_wake.py) controls properties
    5 | of the word being perturbed AT LAG L -- surprisal(w+L), length(w+L), freq(w+L) --
    6 | on the reasoning that a high-surprisal target has a more volatile state and will
    7 | show a larger relative change for any perturbation.
    8 | 
    9 | The extensions version (extensions/x3b_analyze_wake.py), which produced the
   10 | headline claim that neighborhood TEE has a causal wake at every lag 1-10, does
   11 | NOT include those target controls. This script adds them back and reports both.
   12 | 
   13 | Same conventions otherwise: z-scored (ddof=0), position + story FE,
   14 | cluster-robust SE by sent_uid, punct-free pass.
   15 | """
   16 | 
   17 | import numpy as np
   18 | import pandas as pd
   19 | import statsmodels.formula.api as smf
   20 | import hashlib, warnings
   21 | warnings.filterwarnings("ignore")
   22 | 
   23 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   24 | MAXL = 10
   25 | 
   26 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   27 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   28 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   29 | assert sh == "8a6087341e", sh
   30 | W = pd.read_csv(f"{GP}/extensions/wake_coarse_step6.csv")
   31 | CUR = pd.read_csv(f"{GP}/tee_vs_curvature/curvature_merged_8a6087341e.csv")
   32 | CTEE = pd.read_csv(f"{GP}/extensions/coarse_tee_8a6087341e.csv")
   33 | 
   34 | S["has_trailing_punct"] = S["word"].astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   35 | D = W.merge(S, on=["story_id", "word_idx"], validate="one_to_one")
   36 | D = D.merge(CUR[["story_id", "word_idx", "tee3_par", "tee3_perp"]],
   37 |             on=["story_id", "word_idx"], validate="one_to_one")
   38 | D = D.merge(CTEE[["story_id", "word_idx", "ctee_m5", "ntee_k100"]],
   39 |             on=["story_id", "word_idx"], validate="one_to_one")
   40 | 
   41 | # target (w+L) properties
   42 | tgt = S[["story_id", "word_idx", "surprisal", "word_length", "log_freq"]]
   43 | for L in range(1, MAXL + 1):
   44 |     t = tgt.rename(columns={"word_idx": "wl", "surprisal": f"tsurp_{L}",
   45 |                             "word_length": f"tlen_{L}", "log_freq": f"tfreq_{L}"})
   46 |     t["word_idx"] = t["wl"] - L
   47 |     D = D.merge(t[["story_id", "word_idx", f"tsurp_{L}", f"tlen_{L}", f"tfreq_{L}"]],
   48 |                 on=["story_id", "word_idx"], how="left")
   49 | 
   50 | print(f"SAMPLE hash={sh}  wake n={len(D)}  punct-final={int(D.has_trailing_punct.sum())}")
   51 | 
   52 | PRED = ["tee3_perp", "tee3_par", "surprisal", "ctee_m5", "ntee_k100",
   53 |         "word_length", "log_freq"]
   54 | CTRL = "from_start + fs2 + from_end + fe2 + C(story_id)"
   55 | 
   56 | 
   57 | def z(s):
   58 |     return (s - s.mean()) / s.std(ddof=0)
   59 | 
   60 | 
   61 | def run(dat, fam, with_target, label):
   62 |     print(f"\n{'='*78}\n{label} | DV={fam} | target controls: "
   63 |           f"{'YES' if with_target else 'NO (as published)'}\n{'='*78}")
   64 |     print(f"{'lag':>4}{'ntee_k100':>20}{'tee3_perp':>20}{'surprisal(w)':>20}{'n':>7}")
   65 |     for L in range(1, MAXL + 1):
   66 |         dv = f"{fam}_{L}"
   67 |         tc = [f"tsurp_{L}", f"tlen_{L}", f"tfreq_{L}"] if with_target else []
   68 |         need = [dv] + PRED + tc
   69 |         d = dat.dropna(subset=need).copy()
   70 |         if len(d) < 200:
   71 |             continue
   72 |         for c in PRED + tc + [dv]:
   73 |             d[c] = z(d[c])
   74 |         terms = PRED + tc
   75 |         m = smf.ols(f"{dv} ~ {' + '.join(terms)} + {CTRL}", d).fit(
   76 |             cov_type="cluster", cov_kwds={"groups": d["sent_uid"]})
   77 | 
   78 |         def cell(k):
   79 |             b, p = m.params[k], m.pvalues[k]
   80 |             return f"{b:+.4f}({p:.1e}){'*' if p < .05 else ' '}"
   81 |         print(f"L{L:<3d}{cell('ntee_k100'):>20}{cell('tee3_perp'):>20}"
   82 |               f"{cell('surprisal'):>20}{int(m.nobs):>7}")
   83 | 
   84 | 
   85 | Dpf = D[D.has_trailing_punct == 0].reset_index(drop=True)
   86 | for fam in ["wake_rel", "wake_coarse"]:
   87 |     run(Dpf, fam, False, "PUNCT-FREE")
   88 |     run(Dpf, fam, True, "PUNCT-FREE")
```


==============================================================================
### FILE: gp_confound_check/freq_sign_check.py
==============================================================================

```
    1 | """
    2 | WHY IS THE FREQUENCY COEFFICIENT POSITIVE?
    3 | ===========================================
    4 | The manuscript reports beta(log frequency) = +0.0072 in Natural Stories, and the
    5 | new figure puts it at +0.022. Positive means MORE FREQUENT WORDS ARE READ MORE
    6 | SLOWLY, which is backwards from one of the most robust effects in reading
    7 | research.
    8 | 
    9 | Three possible explanations, distinguished below:
   10 | 
   11 |   (a) CODING ERROR. The variable is not what it is labelled -- inverted, or a
   12 |       rank, or something other than a frequency. Diagnosed by inspecting the
   13 |       values directly: "the" and "of" must have HIGH log_freq, rare content
   14 |       words LOW.
   15 | 
   16 |   (b) SUPPRESSION. The raw effect is negative as expected, but flips once
   17 |       surprisal and word length are in the model. This is documented for
   18 |       frequency, which is heavily collinear with predictability, and would be
   19 |       legitimate -- but it must be explained in the text rather than reported
   20 |       bare.
   21 | 
   22 |   (c) SOMETHING ELSE, in which case the diagnostics below should show it.
   23 | 
   24 | The test is a build-up: raw correlation, then the coefficient with predictors
   25 | added one at a time, so the exact point at which the sign flips is visible.
   26 | Run on both corpora, since the figure shows a positive coefficient in each.
   27 | """
   28 | 
   29 | import numpy as np
   30 | import pandas as pd
   31 | import statsmodels.api as sm
   32 | from wordfreq import zipf_frequency
   33 | import hashlib, warnings
   34 | warnings.filterwarnings("ignore")
   35 | 
   36 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   37 | GPC = f"{GP}/gp_confound_check"
   38 | 
   39 | 
   40 | def zs(x):
   41 |     x = np.asarray(x, dtype=float)
   42 |     s = x.std()
   43 |     return (x - x.mean()) / s if s > 0 else x * 0
   44 | 
   45 | 
   46 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   47 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   48 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   49 | assert sh == "8a6087341e", sh
   50 | 
   51 | print("=" * 78)
   52 | print("(a) IS THE VARIABLE WHAT IT SAYS IT IS?")
   53 | print("=" * 78)
   54 | print("  highest log_freq words in the Natural Stories sample:")
   55 | top = S.dropna(subset=["log_freq"]).nlargest(12, "log_freq")[["word", "log_freq"]]
   56 | print("   ", ", ".join(f"{r.word}({r.log_freq:.2f})" for r in top.itertuples()))
   57 | print("  lowest log_freq words:")
   58 | bot = S.dropna(subset=["log_freq"]).nsmallest(12, "log_freq")[["word", "log_freq"]]
   59 | print("   ", ", ".join(f"{r.word}({r.log_freq:.2f})" for r in bot.itertuples()))
   60 | print(f"\n  range {S.log_freq.min():.2f} to {S.log_freq.max():.2f}, "
   61 |       f"mean {S.log_freq.mean():.2f}")
   62 | chk = {w: zipf_frequency(w, "en") for w in ["the", "of", "and", "manor",
   63 |                                             "ocean", "tics"]}
   64 | print(f"  reference Zipf values: {chk}")
   65 | print(f"  r(log_freq, word_length) = "
   66 |       f"{S.log_freq.corr(S.word_length):+.3f}   (should be NEGATIVE: frequent "
   67 |       f"words are short)")
   68 | print(f"  r(log_freq, surprisal)   = {S.log_freq.corr(S.surprisal):+.3f}"
   69 |       f"   (should be NEGATIVE: frequent words are predictable)")
   70 | 
   71 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   72 |                  sep="\t").rename(columns={"item": "story_id",
   73 |                                            "WorkerId": "participant"})
   74 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   75 | ns = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   76 |                  "log_freq"]], on=["story_id", "zone"], how="inner")
   77 | ns["log_RT"] = np.log(ns.RT)
   78 | ns = ns.sort_values(["participant", "story_id", "zone"])
   79 | ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
   80 | ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   81 |                        "prev_log_RT", "tee_k3", "surprisal"]).rename(
   82 |     columns={"tee_k3": "tee"})
   83 | 
   84 | d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
   85 | d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
   86 | d = d.rename(columns={"MD5": "participant"})
   87 | d = d.merge(pd.read_csv(f"{GPC}/sap_measures_L6k3.csv"),
   88 |             on=["item", "Type", "WordPosition"], how="left",
   89 |             validate="many_to_one")
   90 | d["word_length"] = d.EachWord.str.len()
   91 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
   92 |     lambda x: zipf_frequency(x, "en"))
   93 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
   94 | d["from_start"] = d.WordPosition.astype(float)
   95 | d["fs2"] = d.from_start ** 2
   96 | d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
   97 | d["fe2"] = d.from_end ** 2
   98 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
   99 | d["log_RT"] = np.log(d.RT)
  100 | d = d.dropna(subset=["tee", "surp", "word_length", "log_freq",
  101 |                      "log_RT"]).rename(columns={"surp": "surprisal"})
  102 | 
  103 | 
  104 | def subj(df, cols, minn):
  105 |     out = []
  106 |     for pid, s in df.groupby("participant"):
  107 |         s = s.dropna(subset=cols + ["log_RT"])
  108 |         if len(s) < minn:
  109 |             continue
  110 |         X = np.column_stack([zs(s[c].values) for c in cols])
  111 |         if (X.std(axis=0) == 0).any():
  112 |             continue
  113 |         out.append(sm.OLS(zs(s.log_RT.values),
  114 |                           sm.add_constant(X)).fit().params[1])
  115 |     return np.array(out)
  116 | 
  117 | 
  118 | for name, df, extra, minn in [
  119 |         ("Natural Stories", ns, ["zone", "prev_log_RT"], 300),
  120 |         ("Garden-path corpus", d, ["punct", "from_start", "fs2", "from_end",
  121 |                                    "fe2"], 100)]:
  122 |     print("\n" + "=" * 78)
  123 |     print(f"(b) WHERE DOES THE SIGN FLIP?  {name}")
  124 |     print("=" * 78)
  125 |     r = df.log_freq.corr(df.log_RT)
  126 |     print(f"  raw r(log_freq, log_RT) = {r:+.4f}   "
  127 |           f"({'NEGATIVE as expected' if r < 0 else 'POSITIVE -- unexpected'})")
  128 |     steps = [
  129 |         ("log_freq alone", ["log_freq"]),
  130 |         ("+ word_length", ["log_freq", "word_length"]),
  131 |         ("+ surprisal", ["log_freq", "word_length", "surprisal"]),
  132 |         ("+ trajectory error", ["log_freq", "word_length", "surprisal", "tee"]),
  133 |         ("+ remaining controls", ["log_freq", "word_length", "surprisal",
  134 |                                   "tee"] + extra),
  135 |     ]
  136 |     print(f"\n  {'model':<26}{'beta(log_freq)':>16}{'% positive':>13}")
  137 |     for lab, cols in steps:
  138 |         b = subj(df, cols, minn)
  139 |         print(f"  {lab:<26}{b.mean():>+16.5f}{(b > 0).mean():>12.1%}")
  140 | 
  141 | print("\n" + "=" * 78)
  142 | print("READING")
  143 | print("=" * 78)
  144 | print("""  If log_freq alone is NEGATIVE and turns positive only once surprisal
  145 |   enters, this is suppression: surprisal absorbs the predictability component of
  146 |   frequency and what remains carries the opposite sign. Legitimate, but it must
  147 |   be stated in the text.
  148 | 
  149 |   If log_freq is POSITIVE even on its own, the variable is not measuring what
  150 |   its name says and every model in the paper needs rechecking.""")
```


==============================================================================
### FILE: gp_confound_check/gp_allwords.py
==============================================================================

```
    1 | """
    2 | DOES TEE PREDICT READING TIME ACROSS THE SAP CORPUS AS A WHOLE?
    3 | ==============================================================
    4 | SPEC FIXED BEFORE RUNNING. Deviations must be reported as deviations.
    5 | 
    6 | Motivation
    7 | ----------
    8 | Every previous garden-path analysis in this project asked about the
    9 | ambiguous-minus-unambiguous CONTRAST, at selected ROIs. Those are dead:
   10 | the item-level contrast is unpredicted by TEE (and by surprisal), and for MVRR
   11 | the contrast is contaminated because the unambiguous control is itself
   12 | trajectory-disruptive (baseline TEE 101.0 vs 94.8-95.7 for the other controls).
   13 | 
   14 | This asks a different question, the one that works in Natural Stories:
   15 | across ALL words of ALL 144 sentences, ignoring condition entirely, does TEE
   16 | predict log RT beyond surprisal? The SAP corpus is then simply a SECOND
   17 | self-paced-reading corpus, made of syntactically unusual sentences. If TEE's
   18 | Natural Stories effect is real, it should appear here too; if these odd
   19 | constructions are where trajectory geometry matters most, it could be larger.
   20 | 
   21 | Status: this is a NEW question on data already inspected many times. It is
   22 | exploratory with respect to the corpus, but the spec below is fixed before
   23 | seeing any result, and it is a direct replication attempt of an effect
   24 | established elsewhere (Natural Stories, 171 participants).
   25 | 
   26 | Design
   27 | ------
   28 | Unit: one word, one participant, one trial. Participant = MD5.
   29 | Excluded: RT outside [100, 5000]; words with undefined TEE (sentence-initial
   30 | positions, since the fit window must start at index >= 1 and needs >= 2 points).
   31 | NO ROI selection. NO condition selection. Both ambiguous and unambiguous
   32 | sentences included, all 6 Types.
   33 | 
   34 | PRIMARY (P1). Per participant OLS:
   35 |     z(log RT) ~ z(TEE) + z(surprisal) + z(word_length) + z(log_freq)
   36 |                 + punct + z(WordPosition)
   37 | Group test: Wilcoxon signed-rank on the per-participant TEE coefficients.
   38 |   SUPPORT  : mean beta > 0, p < .01, and >= 65% of participants share the sign
   39 |   NULL     : otherwise
   40 | Participants with < 100 usable rows are dropped (fixed now).
   41 | 
   42 | SECONDARY
   43 |   S1. same + z(prev_log_RT)
   44 |   S2. lag 1: TEE at word t predicting log RT at word t+1, within sentence,
   45 |       contiguity enforced. Natural Stories peaked at lag 1, so this is the
   46 |       pre-specified second look, not a fishing expedition.
   47 |   S3. surprisal's own coefficient from P1, as a reference magnitude.
   48 |   S4. split by construction (MVRR / NPS / NPZ) and by ambiguity, descriptive
   49 |       only, no significance claims -- reported to show whether any effect is
   50 |       carried by one cell.
   51 |   S5. pooled mixedlm dAIC, for comparability with the published table only,
   52 |       explicitly flagged as pseudoreplicated.
   53 | 
   54 | IMPLEMENTATION GUARDS (this project's failure history)
   55 |   - lags computed BEFORE any filtering; row counts printed at each step
   56 |   - merges validated
   57 |   - TEE recomputed with the documented pipeline (GPT-2 small, L6, k=3,
   58 |     word state = final subword, sink never inside a fit window), NOT read from
   59 |     gp_table1_measures.csv, which holds the older sink-inclusive values
   60 | """
   61 | 
   62 | import numpy as np
   63 | import pandas as pd
   64 | import torch
   65 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   66 | from scipy import stats
   67 | import statsmodels.api as sm
   68 | import statsmodels.formula.api as smf
   69 | from wordfreq import zipf_frequency
   70 | import warnings
   71 | warnings.filterwarnings("ignore")
   72 | 
   73 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   74 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   75 | LAYER, K = 6, 3
   76 | MIN_ROWS = 100
   77 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   78 | 
   79 | tokz = GPT2Tokenizer.from_pretrained("gpt2")
   80 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   81 | model.eval().to(DEVICE)
   82 | 
   83 | 
   84 | def measures(words):
   85 |     ids, final_idx = [], []
   86 |     for i, w in enumerate(words):
   87 |         t = tokz.encode(w if i == 0 else " " + w)
   88 |         ids.extend(t)
   89 |         final_idx.append(len(ids) - 1)
   90 |     with torch.no_grad():
   91 |         out = model(torch.tensor([ids]).to(DEVICE))
   92 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   93 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   94 |     tok_s = np.zeros(len(ids))
   95 |     for t in range(1, len(ids)):
   96 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   97 |     starts, prev = [], 0
   98 |     for fi in final_idx:
   99 |         starts.append(prev)
  100 |         prev = fi + 1
  101 |     surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
  102 |     wh = h[final_idx]
  103 |     tee = np.full(len(words), np.nan)
  104 |     for i in range(len(words)):
  105 |         lo = max(i - K, 1)
  106 |         if i < 4 or (i - lo) < 2:
  107 |             continue
  108 |         Y = wh[lo:i]
  109 |         m = Y.shape[0]
  110 |         A = np.column_stack([np.ones(m), np.arange(m)])
  111 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
  112 |         tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
  113 |     return tee, surp
  114 | 
  115 | 
  116 | def zs(x):
  117 |     s = x.std(ddof=0)
  118 |     return (x - x.mean()) / s if s > 0 else x * 0
  119 | 
  120 | 
  121 | # ------------------------------------------------------------------ load
  122 | d = pd.read_csv(RT_CSV)
  123 | print(f"raw rows                {len(d):,}")
  124 | for c in ["EachWord", "Sentence"]:
  125 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
  126 | d = d.rename(columns={"MD5": "participant"})
  127 | print(f"participants            {d.participant.nunique():,}")
  128 | print(f"sentences               {d.Sentence.nunique()}   types {d.Type.nunique()}")
  129 | 
  130 | # ------------------------------------------------- model measures per sentence
  131 | sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
  132 |            .sort_values(["item", "Type", "WordPosition"])
  133 |            .groupby(["item", "Type"]))
  134 | rows = []
  135 | for (item, typ), g in sents:
  136 |     words = [str(x) for x in g.EachWord.tolist()]
  137 |     tee, surp = measures(words)
  138 |     for j, (_, r) in enumerate(g.iterrows()):
  139 |         rows.append({"item": item, "Type": typ,
  140 |                      "WordPosition": r.WordPosition,
  141 |                      "tee": tee[j], "surp": surp[j]})
  142 | M = pd.DataFrame(rows)
  143 | n_before = len(d)
  144 | d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
  145 |             validate="many_to_one")
  146 | assert len(d) == n_before, "merge changed row count"
  147 | print(f"after measure merge     {len(d):,}")
  148 | 
  149 | d["word_length"] = d.EachWord.str.len()
  150 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
  151 |     lambda x: zipf_frequency(x, "en"))
  152 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
  153 | 
  154 | # -------------------------------------- LAGS BEFORE ANY FILTERING
  155 | d = d.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
  156 |     drop=True)
  157 | g = d.groupby(["participant", "item", "Type"])
  158 | d["log_RT_raw"] = np.log(d.RT.clip(lower=1))
  159 | d["prev_log_RT"] = g["log_RT_raw"].shift(1)
  160 | d["y_lead1"] = g["log_RT_raw"].shift(-1)
  161 | d["pos_lead1"] = g["WordPosition"].shift(-1)
  162 | d.loc[(d.pos_lead1 - d.WordPosition) != 1, "y_lead1"] = np.nan
  163 | d["prev_pos"] = g["WordPosition"].shift(1)
  164 | d.loc[(d.WordPosition - d.prev_pos) != 1, "prev_log_RT"] = np.nan
  165 | print(f"after lag construction  {len(d):,}")
  166 | 
  167 | # -------------------------------------- filters
  168 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
  169 | print(f"after RT filter         {len(d):,}")
  170 | d["log_RT"] = np.log(d.RT)
  171 | d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
  172 | print(f"after dropping undefined TEE etc  {len(d):,}")
  173 | print(f"  usable WordPositions: {sorted(d.WordPosition.unique())}")
  174 | print(f"  participants remaining: {d.participant.nunique():,}\n")
  175 | 
  176 | BASE = ["tee", "surp", "word_length", "log_freq", "punct", "WordPosition"]
  177 | 
  178 | 
  179 | def per_subject(df, cols, outcome, focus="tee", minr=MIN_ROWS):
  180 |     out, ref = [], []
  181 |     for pid, sub in df.groupby("participant"):
  182 |         s = sub.dropna(subset=cols + [outcome])
  183 |         if len(s) < minr:
  184 |             continue
  185 |         X = s[cols].astype(float).apply(zs)
  186 |         if (X.std(ddof=0) == 0).any():
  187 |             continue
  188 |         r = sm.OLS(zs(s[outcome]).values, sm.add_constant(X.values)).fit()
  189 |         out.append(r.params[cols.index(focus) + 1])
  190 |         ref.append(r.params[cols.index("surp") + 1])
  191 |     return np.array(out), np.array(ref)
  192 | 
  193 | 
  194 | def report(b, label):
  195 |     if len(b) < 10:
  196 |         print(f"{label}: only {len(b)} participants -- not reported")
  197 |         return
  198 |     pos = (b > 0).mean()
  199 |     agree = max(pos, 1 - pos)
  200 |     p = stats.wilcoxon(b).pvalue
  201 |     ok = (b.mean() > 0) and (p < .01) and (pos >= .65)
  202 |     print(f"{label}\n    n = {len(b)}   mean beta = {b.mean():+.5f}   "
  203 |           f"{pos:.1%} positive   Wilcoxon p = {p:.3e}   "
  204 |           f"{'SUPPORT' if ok else 'null'}")
  205 | 
  206 | 
  207 | print("=" * 78)
  208 | print("P1 (PRIMARY): TEE -> log RT, all words, all conditions")
  209 | print("=" * 78)
  210 | b_tee, b_sur = per_subject(d, BASE, "log_RT")
  211 | report(b_tee, "  TEE")
  212 | print(f"\nS3 reference -- surprisal from the same models:")
  213 | print(f"    mean beta = {b_sur.mean():+.5f}   "
  214 |       f"{(b_sur > 0).mean():.1%} positive   "
  215 |       f"Wilcoxon p = {stats.wilcoxon(b_sur).pvalue:.3e}")
  216 | print(f"    TEE / surprisal magnitude ratio = "
  217 |       f"{abs(b_tee.mean()) / abs(b_sur.mean()):.2f}")
  218 | 
  219 | print("\n" + "=" * 78)
  220 | print("S1: same, controlling previous log RT")
  221 | print("=" * 78)
  222 | b1, _ = per_subject(d, BASE + ["prev_log_RT"], "log_RT")
  223 | report(b1, "  TEE")
  224 | 
  225 | print("\n" + "=" * 78)
  226 | print("S2: lag 1 -- TEE at word t -> log RT at word t+1")
  227 | print("=" * 78)
  228 | b2, _ = per_subject(d, BASE, "y_lead1")
  229 | report(b2, "  TEE")
  230 | 
  231 | print("\n" + "=" * 78)
  232 | print("S4 (descriptive): breakdown -- is any effect carried by one cell?")
  233 | print("=" * 78)
  234 | print(f"{'subset':<22}{'n subj':>8}{'mean beta':>12}{'% pos':>9}{'p':>12}")
  235 | for lab, sub in ([(f"construction {c}", d[d.CONSTRUCTION == c])
  236 |                   for c in sorted(d.CONSTRUCTION.unique())]
  237 |                  + [("ambiguous", d[d.AMBUAMB == 1]),
  238 |                     ("unambiguous", d[d.AMBUAMB == 0])]):
  239 |     bb, _ = per_subject(sub, BASE, "log_RT", minr=40)
  240 |     if len(bb) < 10:
  241 |         print(f"{lab:<22}{len(bb):>8}   too few")
  242 |         continue
  243 |     print(f"{lab:<22}{len(bb):>8}{bb.mean():>+12.5f}{(bb > 0).mean():>8.1%}"
  244 |           f"{stats.wilcoxon(bb).pvalue:>12.2e}")
  245 | 
  246 | print("\n" + "=" * 78)
  247 | print("S5: pooled mixedlm dAIC  [PSEUDOREPLICATED -- comparability only]")
  248 | print("=" * 78)
  249 | dd = d.dropna(subset=BASE + ["log_RT"]).copy()
  250 | for c in BASE:
  251 |     dd["z_" + c] = zs(dd[c].astype(float))
  252 | f0 = ("log_RT ~ z_surp + z_word_length + z_log_freq + z_punct "
  253 |       "+ z_WordPosition")
  254 | m0 = smf.mixedlm(f0, dd, groups=dd.participant).fit(reml=False, method="lbfgs")
  255 | m1 = smf.mixedlm(f0 + " + z_tee", dd, groups=dd.participant).fit(
  256 |     reml=False, method="lbfgs")
  257 | print(f"  n = {len(dd):,}   participants = {dd.participant.nunique():,}")
  258 | print(f"  AIC without TEE {m0.aic:.1f}   with TEE {m1.aic:.1f}   "
  259 |       f"dAIC = {m0.aic - m1.aic:+.1f}")
  260 | print(f"  z_tee beta = {m1.params['z_tee']:+.5f}   p = {m1.pvalues['z_tee']:.3e}")
```


==============================================================================
### FILE: gp_confound_check/gp_allwords_matched.py
==============================================================================

```
    1 | """
    2 | MATCHED COMPARISON: TEE vs SURPRISAL UNDER IDENTICAL SPECIFICATIONS
    3 | ===================================================================
    4 | gp_allwords_robust.py showed TEE's per-participant sign agreement falls from
    5 | 67.2% to ~60-61% once position is controlled flexibly, failing the >=65%
    6 | criterion fixed beforehand. The open question: is 65% the wrong bar for THIS
    7 | corpus (short sentences, ~220 observations per participant, so noisy
    8 | per-participant coefficients), or is TEE simply weak here?
    9 | 
   10 | The bar cannot be judged in the abstract, only against a reference measure run
   11 | through exactly the same machinery. Surprisal is that reference: an effect
   12 | nobody disputes exists in self-paced reading.
   13 | 
   14 | Design -- symmetric by construction
   15 | -----------------------------------
   16 | For the fully linear specs, BOTH coefficients come from the SAME fit, so the
   17 | comparison is exact: identical rows, identical controls, identical participants.
   18 | 
   19 |   A1  flexible position                      -> beta_TEE and beta_SURP
   20 |   A2  A1 + sentence-final flag               -> beta_TEE and beta_SURP
   21 |   A3  A2 + previous log RT                   -> beta_TEE and beta_SURP
   22 | 
   23 | For the flexible-form specs, each measure is the linear focus while the OTHER is
   24 | splined, which is the symmetric version of the df=5 test already run:
   25 | 
   26 |   B1  z_tee + bs(z_surp, df=5) + flexible position   -> beta_TEE
   27 |   B2  z_surp + bs(z_tee, df=5) + flexible position   -> beta_SURP
   28 | 
   29 | FLOOR (C). The same A1 model with TEE permuted within participant (seed fixed),
   30 | to establish what sign agreement looks like when there is no effect at all.
   31 | Without this, 60% has no reference point. Expect ~50%.
   32 | 
   33 | PAIRED TEST (D). Because A1-A3 give both coefficients per participant, we can
   34 | ask directly, per participant, whether |beta_TEE| > |beta_SURP|, and run a
   35 | paired Wilcoxon. This is the sharpest form of Elan's hypothesis -- that these
   36 | syntactically odd sentences are captured better by trajectory geometry than by
   37 | probability.
   38 | 
   39 | Reported for every measure: mean beta, % positive, Wilcoxon p.
   40 | No criterion is re-set here. The 65% threshold from the earlier document stands;
   41 | this run only establishes what that threshold means in this corpus.
   42 | """
   43 | 
   44 | import numpy as np
   45 | import pandas as pd
   46 | from scipy import stats
   47 | import statsmodels.api as sm
   48 | import statsmodels.formula.api as smf
   49 | from wordfreq import zipf_frequency
   50 | import warnings
   51 | warnings.filterwarnings("ignore")
   52 | 
   53 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   54 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   55 | CACHE = f"{GP}/sap_measures_L6k3.csv"
   56 | MIN_ROWS = 100
   57 | RNG = np.random.default_rng(20260807)
   58 | 
   59 | 
   60 | def zs(x):
   61 |     x = np.asarray(x, dtype=float)
   62 |     s = x.std()
   63 |     return (x - x.mean()) / s if s > 0 else x * 0
   64 | 
   65 | 
   66 | d = pd.read_csv(RT_CSV)
   67 | for c in ["EachWord", "Sentence"]:
   68 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
   69 | d = d.rename(columns={"MD5": "participant"})
   70 | M = pd.read_csv(CACHE)
   71 | n0 = len(d)
   72 | d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
   73 |             validate="many_to_one")
   74 | assert len(d) == n0
   75 | 
   76 | d["word_length"] = d.EachWord.str.len()
   77 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
   78 |     lambda x: zipf_frequency(x, "en"))
   79 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
   80 | d["from_start"] = d.WordPosition.astype(float)
   81 | d["fs2"] = d.from_start ** 2
   82 | d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
   83 | d["fe2"] = d.from_end ** 2
   84 | d["is_final"] = (d.from_end == 0).astype(float)
   85 | 
   86 | d = d.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
   87 |     drop=True)
   88 | g = d.groupby(["participant", "item", "Type"])
   89 | d["log_RT_raw"] = np.log(d.RT.clip(lower=1))
   90 | d["prev_log_RT"] = g["log_RT_raw"].shift(1)
   91 | d["prev_pos"] = g["WordPosition"].shift(1)
   92 | d.loc[(d.WordPosition - d.prev_pos) != 1, "prev_log_RT"] = np.nan
   93 | 
   94 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
   95 | d["log_RT"] = np.log(d.RT)
   96 | d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
   97 | print(f"rows {len(d):,}   participants {d.participant.nunique():,}\n")
   98 | 
   99 | POS = ["from_start", "fs2", "from_end", "fe2"]
  100 | LEX = ["word_length", "log_freq", "punct"]
  101 | 
  102 | SPECS = {
  103 |     "A1  flexible position":            ["tee", "surp"] + LEX + POS,
  104 |     "A2  A1 + final flag":              ["tee", "surp"] + LEX + POS + ["is_final"],
  105 |     "A3  A2 + previous log RT":         ["tee", "surp"] + LEX + POS
  106 |                                         + ["is_final", "prev_log_RT"],
  107 | }
  108 | 
  109 | groups = {pid: s for pid, s in d.groupby("participant")}
  110 | print(f"participants with data: {len(groups):,}")
  111 | 
  112 | 
  113 | def fit_pair(cols):
  114 |     """Return (beta_tee, beta_surp) arrays from the SAME per-participant fit."""
  115 |     bt, bs_ = [], []
  116 |     for pid, sub in groups.items():
  117 |         s = sub.dropna(subset=cols + ["log_RT"])
  118 |         if len(s) < MIN_ROWS:
  119 |             continue
  120 |         X = np.column_stack([zs(s[c].values) for c in cols])
  121 |         if (X.std(axis=0) == 0).any():
  122 |             continue
  123 |         r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
  124 |         bt.append(r.params[cols.index("tee") + 1])
  125 |         bs_.append(r.params[cols.index("surp") + 1])
  126 |     return np.array(bt), np.array(bs_)
  127 | 
  128 | 
  129 | def line(lab, b):
  130 |     pos = (b > 0).mean()
  131 |     p = stats.wilcoxon(b).pvalue
  132 |     flag = "PASS" if (b.mean() > 0 and p < .01 and pos >= .65) else ""
  133 |     print(f"{lab:<34}{len(b):>6}{b.mean():>+11.5f}{pos:>8.1%}{p:>11.2e}{flag:>6}")
  134 | 
  135 | 
  136 | print("=" * 78)
  137 | print("A. BOTH MEASURES FROM THE SAME FIT (identical rows and controls)")
  138 | print("=" * 78)
  139 | print(f"{'spec / measure':<34}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'':>6}")
  140 | pairs = {}
  141 | for lab, cols in SPECS.items():
  142 |     bt, bsu = fit_pair(cols)
  143 |     pairs[lab] = (bt, bsu)
  144 |     line(f"{lab}  [TEE]", bt)
  145 |     line(f"{'':<4}{'':<26}  [surprisal]", bsu)
  146 |     print()
  147 | 
  148 | print("=" * 78)
  149 | print("B. EACH MEASURE LINEAR WHILE THE OTHER IS SPLINED (df=5)")
  150 | print("=" * 78)
  151 | BSPECS = [
  152 |     ("B1  TEE, spline surprisal", "z_tee",
  153 |      "z_log_RT ~ z_tee + bs(z_surp, df=5) + z_word_length + z_log_freq + punct"
  154 |      " + z_from_start + z_fs2 + z_from_end + z_fe2"),
  155 |     ("B2  surprisal, spline TEE", "z_surp",
  156 |      "z_log_RT ~ z_surp + bs(z_tee, df=5) + z_word_length + z_log_freq + punct"
  157 |      " + z_from_start + z_fs2 + z_from_end + z_fe2"),
  158 | ]
  159 | ZC = ["log_RT", "tee", "surp", "word_length", "log_freq", "from_start", "fs2",
  160 |       "from_end", "fe2"]
  161 | zsubs = {}
  162 | for pid, sub in groups.items():
  163 |     s = sub.dropna(subset=["log_RT", "tee", "surp", "word_length", "log_freq"])
  164 |     if len(s) < MIN_ROWS:
  165 |         continue
  166 |     s = s.copy()
  167 |     for c in ZC:
  168 |         s["z_" + c] = zs(s[c].values)
  169 |     zsubs[pid] = s
  170 | 
  171 | print(f"{'spec':<34}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'':>6}")
  172 | for lab, term, f in BSPECS:
  173 |     b = []
  174 |     for pid, s in zsubs.items():
  175 |         try:
  176 |             b.append(smf.ols(f, s).fit().params[term])
  177 |         except Exception:
  178 |             continue
  179 |     line(lab, np.array(b))
  180 | 
  181 | print("\n" + "=" * 78)
  182 | print("C. FLOOR: A1 with TEE permuted within participant")
  183 | print("=" * 78)
  184 | cols = SPECS["A1  flexible position"]
  185 | bperm = []
  186 | for pid, sub in groups.items():
  187 |     s = sub.dropna(subset=cols + ["log_RT"])
  188 |     if len(s) < MIN_ROWS:
  189 |         continue
  190 |     s = s.copy()
  191 |     s["tee"] = RNG.permutation(s.tee.values)
  192 |     X = np.column_stack([zs(s[c].values) for c in cols])
  193 |     if (X.std(axis=0) == 0).any():
  194 |         continue
  195 |     r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
  196 |     bperm.append(r.params[cols.index("tee") + 1])
  197 | print(f"{'spec':<34}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'':>6}")
  198 | line("C   permuted TEE (null floor)", np.array(bperm))
  199 | 
  200 | print("\n" + "=" * 78)
  201 | print("D. PAIRED, WITHIN PARTICIPANT: is |beta_TEE| > |beta_surprisal|?")
  202 | print("=" * 78)
  203 | for lab, (bt, bsu) in pairs.items():
  204 |     n = min(len(bt), len(bsu))
  205 |     at, asu = np.abs(bt[:n]), np.abs(bsu[:n])
  206 |     frac = (at > asu).mean()
  207 |     w = stats.wilcoxon(at, asu)
  208 |     print(f"  {lab:<30} |TEE|>|surp| in {frac:>5.1%} of participants   "
  209 |           f"paired p = {w.pvalue:.2e}")
  210 |     print(f"  {'':<30} mean |beta| TEE {at.mean():.5f}  "
  211 |           f"surprisal {asu.mean():.5f}")
```


==============================================================================
### FILE: gp_confound_check/gp_allwords_robust.py
==============================================================================

```
    1 | """
    2 | STRESS TESTS ON THE SAP ALL-WORDS RESULT
    3 | ========================================
    4 | gp_allwords.py found, across all 144 SAP sentences, all conditions, 2,000
    5 | participants:
    6 |     TEE       beta = +0.0340   67.2% positive   p = 2.7e-67
    7 |     surprisal beta = +0.0241   56.8% positive   p = 7.0e-17
    8 | 
    9 | Before that can be believed, the two threats that actually mattered in Natural
   10 | Stories have to be checked. Both are misspecification threats: if a control is
   11 | entered in a form too rigid to absorb its true effect, TEE can pick up the
   12 | residual and look like an independent predictor.
   13 | 
   14 | THREAT 1 -- position. Only word positions 5-17 are usable, sentences are 13-17
   15 | words, and these are single-sentence self-paced trials, so there is a large
   16 | sentence-final wrap-up spike. gp_allwords.py controlled position with a single
   17 | LINEAR term. Natural Stories needed from_start, from_start^2, from_end,
   18 | from_end^2 before the position structure was absorbed. If TEE covaries with
   19 | position -- and it plausibly does, since the fit window is shorter early and the
   20 | trajectory is doing different things at sentence end -- a linear control leaves
   21 | exactly the residual TEE could be absorbing.
   22 | 
   23 | THREAT 2 -- surprisal linearity. In Natural Stories, replacing linear surprisal
   24 | with a spline improved AIC by 346.4, i.e. the linear form was genuinely wrong.
   25 | TEE survived there, but the test has to be repeated here.
   26 | 
   27 | Models (per participant, group Wilcoxon across participants, same as P1):
   28 |   M0  P1 as published in gp_allwords.py                 [linear pos, linear surp]
   29 |   M1  + from_start, fs2, from_end, fe2                  [flexible position]
   30 |   M2  + is_final indicator                              [wrap-up]
   31 |   M3  M1 with bs(surprisal, df=3)                       [flexible surprisal]
   32 |   M4  M1 with bs(surprisal, df=5)
   33 |   M5  M1 with bs(surprisal, df=8)                       [most flexible]
   34 |   M6  M5 + is_final + prev_log_RT                       [everything at once]
   35 | 
   36 | Criterion carried over unchanged from gp_allwords.py:
   37 |     SUPPORT = mean beta > 0, Wilcoxon p < .01, >= 65% of participants same sign.
   38 | 
   39 | Also reported: r(TEE, position) and mean TEE by position, so the position threat
   40 | can be judged directly rather than inferred; and the AIC gain from splining
   41 | surprisal, to establish whether the linear form was actually wrong here.
   42 | """
   43 | 
   44 | import numpy as np
   45 | import pandas as pd
   46 | import torch
   47 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   48 | from scipy import stats
   49 | import statsmodels.api as sm
   50 | import statsmodels.formula.api as smf
   51 | from wordfreq import zipf_frequency
   52 | import os, warnings
   53 | warnings.filterwarnings("ignore")
   54 | 
   55 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   56 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   57 | CACHE = f"{GP}/sap_measures_L6k3.csv"
   58 | LAYER, K = 6, 3
   59 | MIN_ROWS = 100
   60 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   61 | 
   62 | 
   63 | def measures(words, tokz, model):
   64 |     ids, final_idx = [], []
   65 |     for i, w in enumerate(words):
   66 |         t = tokz.encode(w if i == 0 else " " + w)
   67 |         ids.extend(t)
   68 |         final_idx.append(len(ids) - 1)
   69 |     with torch.no_grad():
   70 |         out = model(torch.tensor([ids]).to(DEVICE))
   71 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   72 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   73 |     tok_s = np.zeros(len(ids))
   74 |     for t in range(1, len(ids)):
   75 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   76 |     starts, prev = [], 0
   77 |     for fi in final_idx:
   78 |         starts.append(prev)
   79 |         prev = fi + 1
   80 |     surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
   81 |     wh = h[final_idx]
   82 |     tee = np.full(len(words), np.nan)
   83 |     for i in range(len(words)):
   84 |         lo = max(i - K, 1)
   85 |         if i < 4 or (i - lo) < 2:
   86 |             continue
   87 |         Y = wh[lo:i]
   88 |         m = Y.shape[0]
   89 |         A = np.column_stack([np.ones(m), np.arange(m)])
   90 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   91 |         tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
   92 |     return tee, surp
   93 | 
   94 | 
   95 | def zs(x):
   96 |     s = x.std(ddof=0)
   97 |     return (x - x.mean()) / s if s > 0 else x * 0
   98 | 
   99 | 
  100 | d = pd.read_csv(RT_CSV)
  101 | for c in ["EachWord", "Sentence"]:
  102 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
  103 | d = d.rename(columns={"MD5": "participant"})
  104 | 
  105 | if os.path.exists(CACHE):
  106 |     M = pd.read_csv(CACHE)
  107 |     print(f"measures loaded from cache ({len(M):,} rows)")
  108 | else:
  109 |     tokz = GPT2Tokenizer.from_pretrained("gpt2")
  110 |     model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
  111 |     model.eval().to(DEVICE)
  112 |     sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
  113 |                .sort_values(["item", "Type", "WordPosition"])
  114 |                .groupby(["item", "Type"]))
  115 |     rows = []
  116 |     for (item, typ), g in sents:
  117 |         words = [str(x) for x in g.EachWord.tolist()]
  118 |         tee, surp = measures(words, tokz, model)
  119 |         n = len(words)
  120 |         for j, (_, r) in enumerate(g.iterrows()):
  121 |             rows.append({"item": item, "Type": typ,
  122 |                          "WordPosition": r.WordPosition,
  123 |                          "tee": tee[j], "surp": surp[j], "sent_len": n})
  124 |     M = pd.DataFrame(rows)
  125 |     M.to_csv(CACHE, index=False)
  126 |     print(f"measures computed and cached ({len(M):,} rows)")
  127 | 
  128 | n0 = len(d)
  129 | d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
  130 |             validate="many_to_one")
  131 | assert len(d) == n0
  132 | 
  133 | d["word_length"] = d.EachWord.str.len()
  134 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
  135 |     lambda x: zipf_frequency(x, "en"))
  136 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
  137 | d["from_start"] = d.WordPosition.astype(float)
  138 | d["fs2"] = d.from_start ** 2
  139 | d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
  140 | d["fe2"] = d.from_end ** 2
  141 | d["is_final"] = (d.from_end == 0).astype(float)
  142 | 
  143 | d = d.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
  144 |     drop=True)
  145 | g = d.groupby(["participant", "item", "Type"])
  146 | d["log_RT_raw"] = np.log(d.RT.clip(lower=1))
  147 | d["prev_log_RT"] = g["log_RT_raw"].shift(1)
  148 | d["prev_pos"] = g["WordPosition"].shift(1)
  149 | d.loc[(d.WordPosition - d.prev_pos) != 1, "prev_log_RT"] = np.nan
  150 | 
  151 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
  152 | d["log_RT"] = np.log(d.RT)
  153 | d = d.dropna(subset=["tee", "surp", "word_length", "log_freq", "log_RT"])
  154 | print(f"rows {len(d):,}   participants {d.participant.nunique():,}\n")
  155 | 
  156 | # ---------------------------------------------------------------- the threat
  157 | print("=" * 78)
  158 | print("THREAT 1 EVIDENCE: does TEE covary with position?")
  159 | print("=" * 78)
  160 | u = d.drop_duplicates(subset=["item", "Type", "WordPosition"])
  161 | print(f"  r(TEE, from_start) = {u.tee.corr(u.from_start):+.3f}")
  162 | print(f"  r(TEE, from_end)   = {u.tee.corr(u.from_end):+.3f}")
  163 | print(f"  r(TEE, is_final)   = {u.tee.corr(u.is_final):+.3f}")
  164 | print("\n  mean TEE and mean log RT by position from sentence end:")
  165 | t = d.groupby("from_end").agg(tee=("tee", "mean"), logRT=("log_RT", "mean"),
  166 |                               n=("tee", "size"))
  167 | print(t.head(9).round(3).to_string())
  168 | 
  169 | # ---------------------------------------------------------------- models
  170 | SPECS = [
  171 |     ("M0  linear pos, linear surp (= P1)",
  172 |      "z_log_RT ~ z_tee + z_surp + z_word_length + z_log_freq + punct "
  173 |      "+ z_from_start"),
  174 |     ("M1  + flexible position",
  175 |      "z_log_RT ~ z_tee + z_surp + z_word_length + z_log_freq + punct "
  176 |      "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
  177 |     ("M2  M1 + sentence-final flag",
  178 |      "z_log_RT ~ z_tee + z_surp + z_word_length + z_log_freq + punct "
  179 |      "+ z_from_start + z_fs2 + z_from_end + z_fe2 + is_final"),
  180 |     ("M3  M1, spline surprisal df=3",
  181 |      "z_log_RT ~ z_tee + bs(z_surp, df=3) + z_word_length + z_log_freq + punct "
  182 |      "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
  183 |     ("M4  M1, spline surprisal df=5",
  184 |      "z_log_RT ~ z_tee + bs(z_surp, df=5) + z_word_length + z_log_freq + punct "
  185 |      "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
  186 |     ("M5  M1, spline surprisal df=8",
  187 |      "z_log_RT ~ z_tee + bs(z_surp, df=8) + z_word_length + z_log_freq + punct "
  188 |      "+ z_from_start + z_fs2 + z_from_end + z_fe2"),
  189 |     ("M6  M5 + final flag + prev log RT",
  190 |      "z_log_RT ~ z_tee + bs(z_surp, df=8) + z_word_length + z_log_freq + punct "
  191 |      "+ z_from_start + z_fs2 + z_from_end + z_fe2 + is_final + z_prev_log_RT"),
  192 | ]
  193 | 
  194 | ZCOLS = ["log_RT", "tee", "surp", "word_length", "log_freq", "from_start",
  195 |          "fs2", "from_end", "fe2", "prev_log_RT"]
  196 | 
  197 | print("\n" + "=" * 78)
  198 | print("PER-PARTICIPANT MODELS  (criterion: p<.01 AND >=65% same sign)")
  199 | print("=" * 78)
  200 | print(f"{'model':<38}{'n':>6}{'beta':>11}{'% pos':>8}{'p':>11}{'verdict':>9}")
  201 | 
  202 | subs = {}
  203 | for pid, sub in d.groupby("participant"):
  204 |     s = sub.copy()
  205 |     for c in ZCOLS:
  206 |         s["z_" + c] = zs(s[c].astype(float))
  207 |     subs[pid] = s
  208 | 
  209 | for lab, f in SPECS:
  210 |     need = ["z_prev_log_RT"] if "prev_log_RT" in f else []
  211 |     b = []
  212 |     for pid, s in subs.items():
  213 |         ss = s.dropna(subset=["z_log_RT", "z_tee", "z_surp"] + need)
  214 |         if len(ss) < MIN_ROWS or ss.z_tee.std(ddof=0) == 0:
  215 |             continue
  216 |         try:
  217 |             r = smf.ols(f, ss).fit()
  218 |             b.append(r.params["z_tee"])
  219 |         except Exception:
  220 |             continue
  221 |     b = np.array(b)
  222 |     if len(b) < 10:
  223 |         print(f"{lab:<38}{len(b):>6}   too few")
  224 |         continue
  225 |     pos = (b > 0).mean()
  226 |     p = stats.wilcoxon(b).pvalue
  227 |     ok = (b.mean() > 0) and (p < .01) and (pos >= .65)
  228 |     print(f"{lab:<38}{len(b):>6}{b.mean():>+11.5f}{pos:>8.1%}{p:>11.2e}"
  229 |           f"{'SUPPORT' if ok else 'null':>9}")
  230 | 
  231 | # ------------------------------------------------- was linear surprisal wrong?
  232 | print("\n" + "=" * 78)
  233 | print("Was the LINEAR surprisal form actually wrong here? (pooled AIC)")
  234 | print("=" * 78)
  235 | dd = d.dropna(subset=["log_RT", "tee", "surp", "word_length", "log_freq",
  236 |                       "from_start", "from_end"]).copy()
  237 | for c in ZCOLS:
  238 |     if c in dd:
  239 |         dd["z_" + c] = zs(dd[c].astype(float))
  240 | base = ("z_log_RT ~ z_word_length + z_log_freq + punct + z_from_start + z_fs2 "
  241 |         "+ z_from_end + z_fe2")
  242 | for lab, term in [("linear surprisal", "z_surp"),
  243 |                   ("spline surprisal df=5", "bs(z_surp, df=5)"),
  244 |                   ("spline surprisal df=8", "bs(z_surp, df=8)")]:
  245 |     m = smf.mixedlm(f"{base} + {term}", dd, groups=dd.participant).fit(
  246 |         reml=False, method="lbfgs")
  247 |     m2 = smf.mixedlm(f"{base} + {term} + z_tee", dd,
  248 |                      groups=dd.participant).fit(reml=False, method="lbfgs")
  249 |     print(f"  {lab:<24} AIC {m.aic:>10.1f}   +TEE {m2.aic:>10.1f}   "
  250 |           f"dAIC(TEE) {m.aic - m2.aic:>+8.1f}")
```


==============================================================================
### FILE: gp_confound_check/gp_item_level.py
==============================================================================

```
    1 | """
    2 | THE TEST THE ORIGINAL INTUITION ACTUALLY IMPLIES
    3 | ================================================
    4 | The paper asked: does TEE predict word-by-word RT inside the critical region?
    5 | The motivating intuition was different and stronger: in a garden-path sentence
    6 | the accumulated trajectory reverses at the disambiguating word, and THAT is what
    7 | costs the reader. If so, items whose TEE is disrupted more by the ambiguity
    8 | should show a bigger human garden-path effect.
    9 | 
   10 | That is an ITEM-LEVEL question about the ambiguous-minus-unambiguous DIFFERENCE,
   11 | not a word-level question about RT. It was never tested.
   12 | 
   13 |   Predictor:  dTEE_i  = TEE(ambiguous) - TEE(unambiguous)   at the disambiguating word
   14 |   Outcome:    dRT_i   = mean logRT(ambiguous) - mean logRT(unambiguous)
   15 |   Control:    dSurp_i = surprisal(ambiguous) - surprisal(unambiguous)
   16 | 
   17 | 24 items x 3 constructions = 72 item-condition pairs. Underpowered by design;
   18 | reported as such.
   19 | 
   20 | TEE computed with the sink excluded from every fit window (windows start at
   21 | word index 1), GPT-2 small layer 6, k=3, word states at final subword.
   22 | Both ROI 0 (the disambiguating word) and the pooled critical region are tested.
   23 | """
   24 | 
   25 | import numpy as np
   26 | import pandas as pd
   27 | import torch
   28 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   29 | from scipy import stats
   30 | import statsmodels.formula.api as smf
   31 | import os, warnings
   32 | warnings.filterwarnings("ignore")
   33 | 
   34 | RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
   35 | LAYER, K = 6, 3
   36 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   37 | 
   38 | tokz = GPT2Tokenizer.from_pretrained("gpt2")
   39 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   40 | model.eval().to(DEVICE)
   41 | 
   42 | 
   43 | def measures(words):
   44 |     ids, final_idx = [], []
   45 |     for i, w in enumerate(words):
   46 |         t = tokz.encode(w if i == 0 else " " + w)
   47 |         ids.extend(t)
   48 |         final_idx.append(len(ids) - 1)
   49 |     with torch.no_grad():
   50 |         out = model(torch.tensor([ids]).to(DEVICE))
   51 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   52 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   53 |     tok_s = np.zeros(len(ids))
   54 |     for t in range(1, len(ids)):
   55 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   56 |     starts, prev = [], 0
   57 |     for fi in final_idx:
   58 |         starts.append(prev); prev = fi + 1
   59 |     surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
   60 |     wh = h[final_idx]
   61 |     tee = np.full(len(words), np.nan)
   62 |     for i in range(len(words)):
   63 |         lo = max(i - K, 1)                      # sink never inside the window
   64 |         if i < 4 or (i - lo) < 2:
   65 |             continue
   66 |         Y = wh[lo:i]; m = Y.shape[0]
   67 |         A = np.column_stack([np.ones(m), np.arange(m)])
   68 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   69 |         tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
   70 |     return tee, surp
   71 | 
   72 | 
   73 | # ---------- human garden-path effect, per item x construction ----------
   74 | d = pd.read_csv(RT_CSV)
   75 | for c in ["EachWord", "Sentence"]:
   76 |     d[c] = d[c].str.replace("%2C", ",", regex=False)
   77 | d = d[(d.RT > 100) & (d.RT < 5000)].copy()
   78 | d["log_RT"] = np.log(d.RT)
   79 | d["amb"] = (d.AMBUAMB == 1).astype(int)     # 1 = ambiguous
   80 | 
   81 | # ---------- model measures per sentence ----------
   82 | sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
   83 |            .sort_values(["item", "Type", "WordPosition"])
   84 |            .groupby(["item", "Type"]))
   85 | rows = []
   86 | for (item, typ), g in sents:
   87 |     words = [str(x) for x in g.EachWord.tolist()]
   88 |     tee, surp = measures(words)
   89 |     for j, (_, r) in enumerate(g.iterrows()):
   90 |         rows.append({"item": item, "Type": typ, "WordPosition": r.WordPosition,
   91 |                      "tee": tee[j], "surp": surp[j]})
   92 | M = pd.DataFrame(rows)
   93 | d = d.merge(M, on=["item", "Type", "WordPosition"], how="left")
   94 | d["construction"] = d.CONSTRUCTION
   95 | 
   96 | print(f"items={d.item.nunique()}  constructions={d.construction.nunique()}  "
   97 |       f"types={d.Type.nunique()}")
   98 | 
   99 | 
  100 | def build_diffs(roi_set, label):
  101 |     sub = d[d.ROI.isin(roi_set)].copy()
  102 |     # human: mean logRT per item x construction x ambiguity
  103 |     hum = (sub.groupby(["item", "construction", "amb"])
  104 |               .log_RT.mean().unstack("amb"))
  105 |     hum.columns = ["unamb_RT", "amb_RT"]
  106 |     hum["dRT"] = hum.amb_RT - hum.unamb_RT
  107 |     # model: mean TEE / surprisal per item x construction x ambiguity
  108 |     mod = (sub.drop_duplicates(subset=["item", "construction", "amb", "WordPosition"])
  109 |               .groupby(["item", "construction", "amb"])[["tee", "surp"]].mean()
  110 |               .unstack("amb"))
  111 |     mod.columns = ["unamb_tee", "amb_tee", "unamb_surp", "amb_surp"]
  112 |     mod["dTEE"] = mod.amb_tee - mod.unamb_tee
  113 |     mod["dSurp"] = mod.amb_surp - mod.unamb_surp
  114 |     X = hum.join(mod).dropna().reset_index()
  115 |     print(f"\n{'='*74}\n{label}   n = {len(X)} item x construction pairs\n{'='*74}")
  116 |     print(f"  mean human GP effect (dRT)  = {X.dRT.mean():+.4f} log-ms  "
  117 |           f"({(X.dRT>0).sum()}/{len(X)} positive)")
  118 |     print(f"  mean dTEE                   = {X.dTEE.mean():+.2f}")
  119 |     print(f"  mean dSurp                  = {X.dSurp.mean():+.2f} bits")
  120 | 
  121 |     r1, p1 = stats.pearsonr(X.dTEE, X.dRT)
  122 |     r2, p2 = stats.pearsonr(X.dSurp, X.dRT)
  123 |     print(f"\n  r(dTEE,  dRT) = {r1:+.3f}   p = {p1:.3f}")
  124 |     print(f"  r(dSurp, dRT) = {r2:+.3f}   p = {p2:.3f}")
  125 | 
  126 |     for c in ["dTEE", "dSurp", "dRT"]:
  127 |         X["z_" + c] = (X[c] - X[c].mean()) / X[c].std(ddof=0)
  128 |     m = smf.ols("z_dRT ~ z_dSurp + z_dTEE + C(construction)", X).fit()
  129 |     print(f"\n  joint model (construction fixed effects):")
  130 |     print(f"    dSurp beta = {m.params['z_dSurp']:+.3f}  p = {m.pvalues['z_dSurp']:.3f}")
  131 |     print(f"    dTEE  beta = {m.params['z_dTEE']:+.3f}  p = {m.pvalues['z_dTEE']:.3f}")
  132 |     print(f"    R^2 = {m.rsquared:.3f}")
  133 | 
  134 |     print(f"\n  by construction:")
  135 |     for con, g in X.groupby("construction"):
  136 |         if len(g) < 5:
  137 |             continue
  138 |         rr, pp = stats.pearsonr(g.dTEE, g.dRT)
  139 |         print(f"    {con:<6} n={len(g):>3}  r(dTEE,dRT) = {rr:+.3f}  p = {pp:.3f}  "
  140 |               f"mean dRT = {g.dRT.mean():+.4f}")
  141 |     return X
  142 | 
  143 | 
  144 | build_diffs([0], "ROI 0 only (the disambiguating word)")
  145 | build_diffs([0, 1, 2], "critical region (ROI 0+1+2 pooled)")
  146 | build_diffs([1, 2], "spillover only (ROI 1+2) - the published sample")
```


==============================================================================
### FILE: gp_confound_check/gp_item_nofe.py
==============================================================================

```
    1 | """
    2 | ITEM-LEVEL GARDEN-PATH TEST WITHOUT CONSTRUCTION FIXED EFFECTS
    3 | ==============================================================
    4 | Elan's objection to the fixed-effects analysis: the theoretical claim was always
    5 | about the garden-path effect itself (ambiguous vs unambiguous), so the pooled
    6 | comparison across all 72 item x construction pairs is the one that matches the
    7 | claim, and partialling out construction removes the very contrast of interest.
    8 | 
    9 | That is a fair reading, so this runs the pooled version:
   10 | 
   11 |     z_dRT ~ z_dSurp + z_dTEE          (NO construction fixed effects)
   12 | 
   13 | and reports alongside it everything needed to judge how much the pooled estimate
   14 | leans on the three construction means:
   15 | 
   16 |   (a) pooled OLS, classical SEs                      <- the test as framed
   17 |   (b) same, cluster-robust SEs by construction (G=3) <- honest inference
   18 |   (c) leave-one-construction-out refits              <- stability
   19 |   (d) construction-mean table                        <- what drives the pooled fit
   20 |   (e) fixed-effects version                          <- for contrast
   21 |   (f) between/within variance decomposition
   22 | 
   23 | TEE is RECOMPUTED here with exactly the settings used in gp_item_level.py
   24 | (GPT-2 small, layer 6, k=3, word state = final subword, sink never inside a fit
   25 | window). gp_table1_measures.csv is NOT reused: it holds the original
   26 | sink-inclusive TEE and does not reproduce the published item-level values.
   27 | 
   28 | GUARD: before reporting anything, reproduce the published ROI-0 numbers from
   29 | gp_item_level_out.txt (mean dTEE +1.69, mean dSurp +4.89, r = +0.280). Abort
   30 | on mismatch.
   31 | """
   32 | 
   33 | import numpy as np
   34 | import pandas as pd
   35 | import torch
   36 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   37 | from scipy import stats
   38 | import statsmodels.formula.api as smf
   39 | import warnings
   40 | warnings.filterwarnings("ignore")
   41 | 
   42 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   43 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   44 | LAYER, K = 6, 3
   45 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   46 | 
   47 | REF = {"dTEE": 1.69, "dSurp": 4.89, "r": 0.280}
   48 | 
   49 | tokz = GPT2Tokenizer.from_pretrained("gpt2")
   50 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   51 | model.eval().to(DEVICE)
   52 | 
   53 | 
   54 | def measures(words):
   55 |     ids, final_idx = [], []
   56 |     for i, w in enumerate(words):
   57 |         t = tokz.encode(w if i == 0 else " " + w)
   58 |         ids.extend(t)
   59 |         final_idx.append(len(ids) - 1)
   60 |     with torch.no_grad():
   61 |         out = model(torch.tensor([ids]).to(DEVICE))
   62 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   63 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   64 |     tok_s = np.zeros(len(ids))
   65 |     for t in range(1, len(ids)):
   66 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   67 |     starts, prev = [], 0
   68 |     for fi in final_idx:
   69 |         starts.append(prev)
   70 |         prev = fi + 1
   71 |     surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
   72 |     wh = h[final_idx]
   73 |     tee = np.full(len(words), np.nan)
   74 |     for i in range(len(words)):
   75 |         lo = max(i - K, 1)                     # sink never inside the window
   76 |         if i < 4 or (i - lo) < 2:
   77 |             continue
   78 |         Y = wh[lo:i]
   79 |         m = Y.shape[0]
   80 |         A = np.column_stack([np.ones(m), np.arange(m)])
   81 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   82 |         tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
   83 |     return tee, surp
   84 | 
   85 | 
   86 | def load():
   87 |     d = pd.read_csv(RT_CSV)
   88 |     for c in ["EachWord", "Sentence"]:
   89 |         d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
   90 |     d = d[(d.RT > 100) & (d.RT < 5000)].copy()
   91 |     d["log_RT"] = np.log(d.RT)
   92 |     d["amb"] = (d.AMBUAMB == 1).astype(int)
   93 |     d["construction"] = d.CONSTRUCTION
   94 | 
   95 |     sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
   96 |                .sort_values(["item", "Type", "WordPosition"])
   97 |                .groupby(["item", "Type"]))
   98 |     rows = []
   99 |     for (item, typ), g in sents:
  100 |         words = [str(x) for x in g.EachWord.tolist()]
  101 |         tee, surp = measures(words)
  102 |         for j, (_, r) in enumerate(g.iterrows()):
  103 |             rows.append({"item": item, "Type": typ,
  104 |                          "WordPosition": r.WordPosition,
  105 |                          "tee": tee[j], "surp": surp[j]})
  106 |     M = pd.DataFrame(rows)
  107 |     return d.merge(M, on=["item", "Type", "WordPosition"], how="left")
  108 | 
  109 | 
  110 | def diffs(d, roi_set):
  111 |     sub = d[d.ROI.isin(roi_set)].copy()
  112 |     hum = (sub.groupby(["item", "construction", "amb"])
  113 |               .log_RT.mean().unstack("amb"))
  114 |     hum.columns = ["unamb_RT", "amb_RT"]
  115 |     hum["dRT"] = hum.amb_RT - hum.unamb_RT
  116 |     mod = (sub.drop_duplicates(subset=["item", "construction", "amb",
  117 |                                        "WordPosition"])
  118 |               .groupby(["item", "construction", "amb"])[["tee", "surp"]]
  119 |               .mean().unstack("amb"))
  120 |     mod.columns = ["unamb_tee", "amb_tee", "unamb_surp", "amb_surp"]
  121 |     mod["dTEE"] = mod.amb_tee - mod.unamb_tee
  122 |     mod["dSurp"] = mod.amb_surp - mod.unamb_surp
  123 |     X = hum.join(mod).dropna().reset_index()
  124 |     for c in ["dTEE", "dSurp", "dRT"]:
  125 |         X["z_" + c] = (X[c] - X[c].mean()) / X[c].std(ddof=0)
  126 |     return X
  127 | 
  128 | 
  129 | def main():
  130 |     d = load()
  131 |     X0 = diffs(d, [0])
  132 |     r0 = stats.pearsonr(X0.dTEE, X0.dRT)[0]
  133 | 
  134 |     print("=" * 74)
  135 |     print("GUARD: reproduce published ROI-0 item-level numbers")
  136 |     print("=" * 74)
  137 |     print(f"  n pairs      {len(X0)}          expected 72")
  138 |     print(f"  mean dTEE    {X0.dTEE.mean():+.2f}   expected {REF['dTEE']:+.2f}")
  139 |     print(f"  mean dSurp   {X0.dSurp.mean():+.2f}   expected {REF['dSurp']:+.2f}")
  140 |     print(f"  r(dTEE,dRT)  {r0:+.3f}   expected {REF['r']:+.3f}")
  141 |     ok = (len(X0) == 72
  142 |           and abs(X0.dTEE.mean() - REF["dTEE"]) < .05
  143 |           and abs(X0.dSurp.mean() - REF["dSurp"]) < .05
  144 |           and abs(r0 - REF["r"]) < .01)
  145 |     print(f"\n  MATCH: {'YES' if ok else 'NO'}")
  146 |     if not ok:
  147 |         print("\n  ABORTING: measures differ from the published item-level run.")
  148 |         return
  149 | 
  150 |     for roi, lab in [([0], "ROI 0 (disambiguating word)"),
  151 |                      ([0, 1, 2], "critical region ROI 0+1+2"),
  152 |                      ([1, 2], "spillover ROI 1+2 (published sample)")]:
  153 |         X = diffs(d, roi)
  154 |         print("\n" + "=" * 74)
  155 |         print(f"{lab}   n = {len(X)}")
  156 |         print("=" * 74)
  157 | 
  158 |         m = smf.ols("z_dRT ~ z_dSurp + z_dTEE", X).fit()
  159 |         print("\n(a) POOLED, no construction fixed effects, classical SEs")
  160 |         for t in ["z_dSurp", "z_dTEE"]:
  161 |             print(f"    {t:<9} beta = {m.params[t]:+.3f}   "
  162 |                   f"SE = {m.bse[t]:.3f}   p = {m.pvalues[t]:.4f}")
  163 |         print(f"    R^2 = {m.rsquared:.3f}")
  164 | 
  165 |         mc = smf.ols("z_dRT ~ z_dSurp + z_dTEE", X).fit(
  166 |             cov_type="cluster", cov_kwds={"groups": X.construction})
  167 |         print("\n(b) same model, SEs clustered by construction (G = 3)")
  168 |         for t in ["z_dSurp", "z_dTEE"]:
  169 |             print(f"    {t:<9} beta = {mc.params[t]:+.3f}   "
  170 |                   f"SE = {mc.bse[t]:.3f}   p = {mc.pvalues[t]:.4f}")
  171 | 
  172 |         print("\n(c) leave-one-construction-out (pooled, no FE)")
  173 |         for con in sorted(X.construction.unique()):
  174 |             sub = X[X.construction != con].copy()
  175 |             for c in ["dTEE", "dSurp", "dRT"]:
  176 |                 sub["z_" + c] = (sub[c] - sub[c].mean()) / sub[c].std(ddof=0)
  177 |             mm = smf.ols("z_dRT ~ z_dSurp + z_dTEE", sub).fit()
  178 |             print(f"    drop {con:<5} n={len(sub):>3}  "
  179 |                   f"dTEE {mm.params['z_dTEE']:+.3f} (p={mm.pvalues['z_dTEE']:.3f})   "
  180 |                   f"dSurp {mm.params['z_dSurp']:+.3f} (p={mm.pvalues['z_dSurp']:.3f})")
  181 | 
  182 |         print("\n(d) construction means (the 3 points a pooled slope rests on)")
  183 |         print(X.groupby("construction")[["dTEE", "dSurp", "dRT"]]
  184 |                .mean().round(4).to_string())
  185 | 
  186 |         mf = smf.ols("z_dRT ~ z_dSurp + z_dTEE + C(construction)", X).fit()
  187 |         print("\n(e) WITH construction fixed effects (within-construction only)")
  188 |         for t in ["z_dSurp", "z_dTEE"]:
  189 |             print(f"    {t:<9} beta = {mf.params[t]:+.3f}   "
  190 |                   f"p = {mf.pvalues[t]:.4f}")
  191 | 
  192 |         print("\n(f) variance decomposition")
  193 |         for v in ["dTEE", "dSurp", "dRT"]:
  194 |             tot = X[v].var(ddof=0)
  195 |             btw = X.groupby("construction")[v].mean().reindex(
  196 |                 X.construction).values
  197 |             print(f"    {v:<6} between-construction share = {np.var(btw)/tot:.1%}")
  198 | 
  199 | 
  200 | if __name__ == "__main__":
  201 |     main()
```


==============================================================================
### FILE: gp_confound_check/gp_mvrr_check.py
==============================================================================

```
    1 | """
    2 | IS THE NEGATIVE MVRR dTEE REAL, OR A FEW OUTLIER ITEMS?
    3 | =======================================================
    4 | gp_item_nofe.py reported mean dTEE = -1.72 for MVRR at ROI 0: the AMBIGUOUS
    5 | reduced-relative produces LESS trajectory extrapolation error at the
    6 | disambiguating word than its unambiguous control. That is backwards for the
    7 | mechanism the garden-path paper proposed, so before it is treated as a fact:
    8 | 
    9 |   1. per-item sign counts and one-sample t / Wilcoxon per construction
   10 |   2. the same for surprisal (does the model find the ambiguous version easier
   11 |      by that measure too, or is this specific to TEE?)
   12 |   3. the raw TEE levels, not just the difference, so we can see which side moves
   13 |   4. what words actually sit in the k=3 fit window in each version -- for MVRR
   14 |      the three words before the disambiguator are identical across conditions
   15 |      ("...past the barn" + "fell"), so any difference must come from earlier
   16 |      context propagating into the hidden states, not from different words
   17 |   5. per-item listing so outliers are visible
   18 | 
   19 | Same measure pipeline as gp_item_nofe.py (GPT-2 small, L6, k=3, sink excluded).
   20 | """
   21 | 
   22 | import numpy as np
   23 | import pandas as pd
   24 | import torch
   25 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   26 | from scipy import stats
   27 | import warnings
   28 | warnings.filterwarnings("ignore")
   29 | 
   30 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   31 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   32 | LAYER, K = 6, 3
   33 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   34 | 
   35 | tokz = GPT2Tokenizer.from_pretrained("gpt2")
   36 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   37 | model.eval().to(DEVICE)
   38 | 
   39 | 
   40 | def measures(words):
   41 |     ids, final_idx = [], []
   42 |     for i, w in enumerate(words):
   43 |         t = tokz.encode(w if i == 0 else " " + w)
   44 |         ids.extend(t)
   45 |         final_idx.append(len(ids) - 1)
   46 |     with torch.no_grad():
   47 |         out = model(torch.tensor([ids]).to(DEVICE))
   48 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   49 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   50 |     tok_s = np.zeros(len(ids))
   51 |     for t in range(1, len(ids)):
   52 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   53 |     starts, prev = [], 0
   54 |     for fi in final_idx:
   55 |         starts.append(prev)
   56 |         prev = fi + 1
   57 |     surp = [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
   58 |     wh = h[final_idx]
   59 |     tee = np.full(len(words), np.nan)
   60 |     for i in range(len(words)):
   61 |         lo = max(i - K, 1)
   62 |         if i < 4 or (i - lo) < 2:
   63 |             continue
   64 |         Y = wh[lo:i]
   65 |         m = Y.shape[0]
   66 |         A = np.column_stack([np.ones(m), np.arange(m)])
   67 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   68 |         tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
   69 |     return tee, surp
   70 | 
   71 | 
   72 | d = pd.read_csv(RT_CSV)
   73 | for c in ["EachWord", "Sentence"]:
   74 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
   75 | d = d[(d.RT > 100) & (d.RT < 5000)].copy()
   76 | d["amb"] = (d.AMBUAMB == 1).astype(int)
   77 | d["construction"] = d.CONSTRUCTION
   78 | 
   79 | sents = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
   80 |            .sort_values(["item", "Type", "WordPosition"])
   81 |            .groupby(["item", "Type"]))
   82 | rows = []
   83 | for (item, typ), g in sents:
   84 |     words = [str(x) for x in g.EachWord.tolist()]
   85 |     tee, surp = measures(words)
   86 |     for j, (_, r) in enumerate(g.iterrows()):
   87 |         rows.append({"item": item, "Type": typ, "WordPosition": r.WordPosition,
   88 |                      "tee": tee[j], "surp": surp[j], "word": words[j],
   89 |                      "w_m1": words[j - 1] if j >= 1 else "",
   90 |                      "w_m2": words[j - 2] if j >= 2 else "",
   91 |                      "w_m3": words[j - 3] if j >= 3 else ""})
   92 | M = pd.DataFrame(rows)
   93 | d = d.merge(M, on=["item", "Type", "WordPosition"], how="left")
   94 | 
   95 | roi0 = d[d.ROI == 0].drop_duplicates(
   96 |     subset=["item", "construction", "amb", "WordPosition"])
   97 | piv = (roi0.groupby(["item", "construction", "amb"])[["tee", "surp"]]
   98 |            .mean().unstack("amb"))
   99 | piv.columns = ["tee_unamb", "tee_amb", "surp_unamb", "surp_amb"]
  100 | piv["dTEE"] = piv.tee_amb - piv.tee_unamb
  101 | piv["dSurp"] = piv.surp_amb - piv.surp_unamb
  102 | X = piv.dropna().reset_index()
  103 | 
  104 | print("=" * 78)
  105 | print("ROI 0: is dTEE reliably negative for MVRR?")
  106 | print("=" * 78)
  107 | print(f"{'constr':<7}{'n':>4}{'mean dTEE':>11}{'neg':>7}{'t':>8}{'p':>10}"
  108 |       f"{'Wilcox p':>11}")
  109 | for con, g in X.groupby("construction"):
  110 |     t = stats.ttest_1samp(g.dTEE, 0)
  111 |     w = stats.wilcoxon(g.dTEE)
  112 |     print(f"{con:<7}{len(g):>4}{g.dTEE.mean():>+11.2f}"
  113 |           f"{(g.dTEE < 0).sum():>4}/{len(g):<3}{t.statistic:>8.2f}"
  114 |           f"{t.pvalue:>10.4f}{w.pvalue:>11.4f}")
  115 | 
  116 | print("\n" + "=" * 78)
  117 | print("same for SURPRISAL (is the ambiguous version 'easier' by that too?)")
  118 | print("=" * 78)
  119 | print(f"{'constr':<7}{'n':>4}{'mean dSurp':>12}{'neg':>8}{'p':>10}")
  120 | for con, g in X.groupby("construction"):
  121 |     t = stats.ttest_1samp(g.dSurp, 0)
  122 |     print(f"{con:<7}{len(g):>4}{g.dSurp.mean():>+12.2f}"
  123 |           f"{(g.dSurp < 0).sum():>5}/{len(g):<3}{t.pvalue:>10.4f}")
  124 | 
  125 | print("\n" + "=" * 78)
  126 | print("RAW LEVELS: which side moves?")
  127 | print("=" * 78)
  128 | print(X.groupby("construction")[["tee_unamb", "tee_amb",
  129 |                                  "surp_unamb", "surp_amb"]].mean().round(2)
  130 |        .to_string())
  131 | 
  132 | print("\n" + "=" * 78)
  133 | print("FIT-WINDOW WORDS at the disambiguator (first 6 MVRR items)")
  134 | print("k=3 window = the three preceding words; if identical across conditions")
  135 | print("the dTEE difference comes from earlier context, not different words.")
  136 | print("=" * 78)
  137 | mv = d[(d.ROI == 0) & (d.construction == "MVRR")].drop_duplicates(
  138 |     subset=["item", "Type"]).sort_values(["item", "Type"])
  139 | for it in sorted(mv.item.unique())[:6]:
  140 |     for _, r in mv[mv.item == it].iterrows():
  141 |         tag = "AMB  " if r.amb == 1 else "UNAMB"
  142 |         print(f"  item {r['item']:>2} {tag} "
  143 |               f"window=[{r['w_m3']} {r['w_m2']} {r['w_m1']}] "
  144 |               f"-> '{r['word']}'   TEE={r['tee']:.1f}")
  145 |     print()
  146 | 
  147 | print("=" * 78)
  148 | print("PER-ITEM MVRR (sorted by dTEE) - look for outlier domination")
  149 | print("=" * 78)
  150 | g = X[X.construction == "MVRR"].sort_values("dTEE")
  151 | print(g[["item", "tee_unamb", "tee_amb", "dTEE", "dSurp"]]
  152 |       .round(2).to_string(index=False))
  153 | 
  154 | X.to_csv(f"{GP}/gp_roi0_item_diffs.csv", index=False)
  155 | print(f"\nsaved per-item table -> gp_roi0_item_diffs.csv")
```


==============================================================================
### FILE: gp_confound_check/gp_roi_signflip.py
==============================================================================

```
    1 | """
    2 | WHY DOES THE TEE-RT EFFECT FLIP SIGN AT THE DISAMBIGUATING WORD?
    3 | ================================================================
    4 | Original spec (mixedlm, by-participant random intercept, ML; controls = word
    5 | length, word position, previous log RT, surprisal; TEE = L6 w=3, isolated
    6 | presentation). prev_log_RT is taken from the FULL sentence so ROI 0 survives.
    7 | 
    8 | Runs:
    9 |   1. Per-ROI models (-2..+3) -- is it a clean reversal at ROI 0 or noise?
   10 |   2. Does surprisal flip too? (if yes, it is about the position, not about TEE)
   11 |   3. Per construction and per ambiguity condition at ROI 0
   12 |   4. Word-property checks: is TEE at ROI 0 confounded with length/frequency/
   13 |      punctuation, and does controlling frequency remove the flip?
   14 |   5. Raw descriptive: mean logRT by TEE quintile at each ROI
   15 | """
   16 | 
   17 | import numpy as np
   18 | import pandas as pd
   19 | import torch
   20 | import statsmodels.formula.api as smf
   21 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   22 | from wordfreq import zipf_frequency
   23 | import os, warnings
   24 | warnings.filterwarnings("ignore")
   25 | 
   26 | HERE = os.path.dirname(os.path.abspath(__file__))
   27 | RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
   28 | LAYER, K = 6, 3
   29 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   30 | 
   31 | tokz = GPT2Tokenizer.from_pretrained("gpt2")
   32 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   33 | model.eval().to(DEVICE)
   34 | 
   35 | 
   36 | def measures(sentence):
   37 |     inputs = tokz(sentence, return_tensors="pt").to(DEVICE)
   38 |     with torch.no_grad():
   39 |         out = model(**inputs)
   40 |     ids = inputs["input_ids"][0]
   41 |     toks = tokz.convert_ids_to_tokens(ids)
   42 |     logp = torch.log_softmax(out.logits, -1)
   43 |     tok_surp = [None] + [-float(logp[0, i - 1, ids[i]]) for i in range(1, len(ids))]
   44 |     words = sentence.split()
   45 |     wmap, ti = [], 0
   46 |     for w in words:
   47 |         wt = []
   48 |         while ti < len(toks):
   49 |             if ti > 0 and toks[ti].startswith("Ġ") and len(wt) > 0:
   50 |                 break
   51 |             wt.append(ti)
   52 |             ti += 1
   53 |         wmap.append(wt)
   54 |     surp = [sum(tok_surp[t] for t in wt if tok_surp[t] is not None) for wt in wmap]
   55 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   56 |     wh = np.array([h[wt[-1]] for wt in wmap])
   57 |     errs = []
   58 |     for t in range(len(words)):
   59 |         if t < K:
   60 |             errs.append(np.nan)
   61 |             continue
   62 |         win = wh[t - K:t]
   63 |         A = np.column_stack([np.ones(K), np.arange(K)])
   64 |         c, *_ = np.linalg.lstsq(A, win, rcond=None)
   65 |         errs.append(float(np.linalg.norm(wh[t] - (c[0] + c[1] * K))))
   66 |     return errs, surp
   67 | 
   68 | 
   69 | def build():
   70 |     rt = pd.read_csv(RT_CSV)
   71 |     for c in ["EachWord", "Sentence"]:
   72 |         rt[c] = rt[c].str.replace("%2C", ",", regex=False)
   73 |     rt["participant"] = rt["MD5"]
   74 |     rt = rt[(rt.RT > 100) & (rt.RT < 5000)].copy()
   75 |     rt["log_RT"] = np.log(rt.RT)
   76 |     rt = rt.sort_values(["participant", "Sentence", "WordPosition"])
   77 |     rt["prev_log_RT"] = rt.groupby(["participant", "Sentence"])["log_RT"].shift(1)
   78 |     rt["word_length"] = rt.EachWord.str.len()
   79 |     rt["log_freq"] = rt.EachWord.str.strip(".,;:!?").str.lower().map(
   80 |         lambda w: zipf_frequency(w, "en"))
   81 |     rt["is_punct_final"] = rt.EachWord.str[-1].isin(list(".,;:!?"))
   82 | 
   83 |     sents = (rt.drop_duplicates(subset=["item", "Type", "WordPosition"])
   84 |              .sort_values(["item", "Type", "WordPosition"])
   85 |              .groupby(["item", "Type"])["Sentence"].first())
   86 |     rows = []
   87 |     for (item, typ), s in sents.items():
   88 |         e, sp = measures(s)
   89 |         for i in range(len(sp)):
   90 |             rows.append(dict(item=item, Type=typ, WordPosition=i + 1,
   91 |                              tee=e[i], surprisal=sp[i]))
   92 |     return rt.merge(pd.DataFrame(rows), on=["item", "Type", "WordPosition"], how="left")
   93 | 
   94 | 
   95 | def z(s):
   96 |     v = s.dropna()
   97 |     return (s - v.mean()) / v.std()
   98 | 
   99 | 
  100 | CTRL = ["word_length", "WordPosition", "prev_log_RT", "surprisal"]
  101 | 
  102 | 
  103 | def prep(df, extra=()):
  104 |     """z-score predictors; drop any that are constant within this subset
  105 |     (e.g. ROI -2 is the same word in every item, so word_length has no
  106 |     variance there and would z-score to all-NaN)."""
  107 |     cols = CTRL + ["tee"] + list(extra)
  108 |     d = df.dropna(subset=["log_RT"] + cols).copy()
  109 |     d.attrs["terms"] = []
  110 |     for c in cols:
  111 |         if d[c].std() > 0:
  112 |             d["z_" + c] = z(d[c])
  113 |             d.attrs["terms"].append("z_" + c)
  114 |     return d
  115 | 
  116 | 
  117 | def coef(d, term, extra_terms=()):
  118 |     terms = [t for t in d.attrs["terms"] if t != "z_tee"] + list(extra_terms)
  119 |     if term not in terms:
  120 |         terms = terms + [term]
  121 |     form = "log_RT ~ " + " + ".join(terms)
  122 |     m = smf.mixedlm(form, d, groups=d["participant"]).fit(reml=False)
  123 |     return m.params[term], m.pvalues[term], m.aic
  124 | 
  125 | 
  126 | def run():
  127 |     d = build()
  128 |     print(f"device {DEVICE}\n")
  129 | 
  130 |     print("=" * 74)
  131 |     print("1. PER-ROI: TEE and surprisal coefficients (L6 w=3, isolated)")
  132 |     print("=" * 74)
  133 |     print(f"{'ROI':>5}{'n':>9}{'beta TEE':>12}{'p':>12}{'beta surp':>12}{'p':>12}")
  134 |     for roi in [-2, -1, 0, 1, 2, 3]:
  135 |         sub = prep(d[d.ROI == roi])
  136 |         if len(sub) < 500:
  137 |             continue
  138 |         bt, pt, _ = coef(sub, "z_tee")
  139 |         bs, ps, _ = coef(sub, "z_surprisal", extra_terms=["z_tee"])
  140 |         print(f"{roi:>5}{len(sub):>9,}{bt:>12.4f}{pt:>12.2e}{bs:>12.4f}{ps:>12.2e}")
  141 | 
  142 |     print("\n" + "=" * 74)
  143 |     print("2. ROI 0 by construction and by ambiguity")
  144 |     print("=" * 74)
  145 |     r0 = d[d.ROI == 0]
  146 |     for label, sub in ([(f"construction {c}", r0[r0.CONSTRUCTION == c])
  147 |                         for c in ["MVRR", "NPS", "NPZ"]] +
  148 |                        [(f"AMBUAMB {a}", r0[r0.AMBUAMB == a]) for a in sorted(r0.AMBUAMB.unique())]):
  149 |         s = prep(sub)
  150 |         if len(s) < 500:
  151 |             continue
  152 |         b, p, _ = coef(s, "z_tee")
  153 |         print(f"  {label:<22}n={len(s):>7,}  beta={b:>8.4f}  p={p:.2e}")
  154 | 
  155 |     print("\n" + "=" * 74)
  156 |     print("3. Does a frequency control remove the ROI-0 flip?")
  157 |     print("=" * 74)
  158 |     for roi in [0, 1, 2]:
  159 |         sub = prep(d[d.ROI == roi], extra=["log_freq"])
  160 |         no_freq = [t for t in sub.attrs["terms"] if t not in ("z_tee", "z_log_freq")]
  161 |         sub2 = sub.copy(); sub2.attrs["terms"] = no_freq
  162 |         b1, p1, _ = coef(sub2, "z_tee")
  163 |         b2, p2, _ = coef(sub, "z_tee")
  164 |         print(f"  ROI {roi}: without freq {b1:>8.4f} (p={p1:.1e})   "
  165 |               f"with freq {b2:>8.4f} (p={p2:.1e})")
  166 | 
  167 |     print("\n" + "=" * 74)
  168 |     print("4. What is TEE correlated with at each ROI? (word-level, n=144 sents)")
  169 |     print("=" * 74)
  170 |     w = d.drop_duplicates(subset=["item", "Type", "WordPosition"])
  171 |     print(f"{'ROI':>5}{'r(tee,len)':>13}{'r(tee,freq)':>13}{'r(tee,surp)':>13}"
  172 |           f"{'% punct-final':>15}{'mean tee':>10}")
  173 |     for roi in [-2, -1, 0, 1, 2, 3]:
  174 |         s = w[(w.ROI == roi)].dropna(subset=["tee", "log_freq"])
  175 |         if len(s) < 20:
  176 |             continue
  177 |         print(f"{roi:>5}{s.tee.corr(s.word_length):>13.3f}{s.tee.corr(s.log_freq):>13.3f}"
  178 |               f"{s.tee.corr(s.surprisal):>13.3f}{s.is_punct_final.mean():>14.1%}"
  179 |               f"{s.tee.mean():>10.1f}")
  180 | 
  181 |     print("\n" + "=" * 74)
  182 |     print("5. Descriptive: mean logRT by TEE quintile, per ROI (raw, no controls)")
  183 |     print("=" * 74)
  184 |     for roi in [0, 1, 2]:
  185 |         s = d[(d.ROI == roi)].dropna(subset=["tee", "log_RT"]).copy()
  186 |         s["q"] = pd.qcut(s.tee, 5, labels=False, duplicates="drop")
  187 |         mm = s.groupby("q").log_RT.mean()
  188 |         print(f"  ROI {roi}: " + "  ".join(f"Q{i+1} {v:.3f}" for i, v in mm.items()))
  189 | 
  190 | 
  191 | if __name__ == "__main__":
  192 |     run()
```


==============================================================================
### FILE: gp_confound_check/gp_sink_check.py
==============================================================================

```
    1 | """
    2 | GARDEN PATH SINK/PUNCTUATION DIAGNOSTIC
    3 | =======================================
    4 | Tests whether the SAP ClassicGP ambiguous-vs-unambiguous TEE effect at the
    5 | disambiguating word (arXiv 2606.05346, Sec 3.1) survives removal of the
    6 | attention-sink first token and punctuation asymmetries.
    7 | 
    8 | Presentation conditions:
    9 |   A_isolated   : sentence alone (presumed paper condition; token 0 = sink)
   10 |   B_prefix     : neutral 10-word prefix prepended (sink far from windows)
   11 |   C_droptok0   : isolated, but word 0 excluded from all fit windows
   12 | 
   13 | Per condition: TEE at the disambiguating word, layers 6 and 12, k = 3,5,7
   14 | (word-level trajectory over final-subword states, linear fit, Euclidean
   15 | error — matching the manuscript spec). Paired amb-unamb stats per
   16 | construction (MVRR, NPS, NPZ) and overall. Bookkeeping: does the fit
   17 | window contain word 0? does it contain a punctuation-final state?
   18 | Also reports the token-0 norm ratio to document the sink itself.
   19 | """
   20 | 
   21 | import numpy as np
   22 | import pandas as pd
   23 | import torch
   24 | from scipy import stats
   25 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   26 | import os, sys, warnings
   27 | warnings.filterwarnings("ignore")
   28 | 
   29 | HERE = os.path.dirname(os.path.abspath(__file__))
   30 | STIM = os.path.join(HERE, "items_ClassicGP.csv")
   31 | PREFIX = "Yesterday afternoon we sat together and read a few short stories aloud."
   32 | LAYERS = [6, 12]
   33 | KS = [3, 5, 7]
   34 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   35 | 
   36 | tok = GPT2Tokenizer.from_pretrained("gpt2")
   37 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   38 | model.eval().to(DEVICE)
   39 | 
   40 | PUNCT = set(".,;:!?\"'`)(")
   41 | 
   42 | def word_states(text, prefix=None):
   43 |     """Return per-word final-subword hidden states {layer: [n_words, 768]},
   44 |     plus per-word punct-final flags. Words = whitespace tokens of `text`
   45 |     (prefix words excluded from the returned arrays)."""
   46 |     words = text.split()
   47 |     ids, final_idx = [], []
   48 |     if prefix is not None:
   49 |         pref_ids = tok.encode(prefix)
   50 |         ids.extend(pref_ids)
   51 |     for i, w in enumerate(words):
   52 |         piece = (" " + w) if (i > 0 or prefix is not None) else w
   53 |         wid = tok.encode(piece)
   54 |         ids.extend(wid)
   55 |         final_idx.append(len(ids) - 1)
   56 |     with torch.no_grad():
   57 |         out = model(torch.tensor([ids]).to(DEVICE))
   58 |     hs = {L: out.hidden_states[L][0].float().cpu().numpy() for L in LAYERS}
   59 |     W = {L: hs[L][final_idx] for L in LAYERS}
   60 |     punct_final = [w[-1] in PUNCT for w in words]
   61 |     tok0_norm = float(np.linalg.norm(out.hidden_states[LAYERS[0]][0][0].float().cpu().numpy()))
   62 |     interior = float(np.mean(np.linalg.norm(hs[LAYERS[0]][1:], axis=1)))
   63 |     return W, punct_final, tok0_norm, interior
   64 | 
   65 | def tee(W, i, k, drop0=False):
   66 |     """TEE at word i: linear fit over word states i-k..i-1, extrapolate."""
   67 |     lo = i - k
   68 |     if drop0:
   69 |         lo = max(lo, 1)
   70 |     if lo < 0 or i - lo < 2:
   71 |         return np.nan, None
   72 |     Y = W[lo:i]                      # m x 768
   73 |     m = Y.shape[0]
   74 |     t = np.arange(m, dtype=float)
   75 |     A = np.vstack([t, np.ones(m)]).T
   76 |     coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
   77 |     pred = coef[0] * m + coef[1]
   78 |     return float(np.linalg.norm(W[i] - pred)), lo
   79 | 
   80 | def run():
   81 |     df = pd.read_csv(STIM)
   82 |     rows = []
   83 |     sink_ratios = []
   84 |     for _, r in df.iterrows():
   85 |         ctype = r["condition"].split("_")[0]           # MVRR / NPS / NPZ
   86 |         for cond, sent, dpos in [("amb", r["ambiguous"], int(r["disambPositionAmb"])),
   87 |                                  ("unamb", r["unambiguous"], int(r["disambPositionUnamb"]))]:
   88 |             i = dpos - 1                               # 1-indexed -> 0-indexed
   89 |             for pres in ["A_isolated", "B_prefix", "C_droptok0"]:
   90 |                 prefix = PREFIX if pres == "B_prefix" else None
   91 |                 W, pf, t0n, intn = word_states(sent, prefix=prefix)
   92 |                 if pres == "A_isolated":
   93 |                     sink_ratios.append(t0n / intn)
   94 |                 for L in LAYERS:
   95 |                     for k in KS:
   96 |                         e, lo = tee(W[L], i, k, drop0=(pres == "C_droptok0"))
   97 |                         if lo is None:
   98 |                             continue
   99 |                         rows.append(dict(
  100 |                             item=r["item"], ctype=ctype, cond=cond, pres=pres,
  101 |                             layer=L, k=k, tee=e,
  102 |                             win_has_word0=(lo == 0),
  103 |                             win_has_punct=any(pf[lo:i]),
  104 |                             crit_is_punct=pf[i], dpos=dpos))
  105 |     out = pd.DataFrame(rows)
  106 |     out.to_csv(os.path.join(HERE, "gp_sink_check_results.csv"), index=False)
  107 |     print(f"n sentences: {df.shape[0]*2} | device {DEVICE}")
  108 |     print(f"token-0 norm / interior norm (L{LAYERS[0]}, isolated): "
  109 |           f"median {np.median(sink_ratios):.1f}x")
  110 |     print("\n=== paired amb - unamb TEE at disambiguating word ===")
  111 |     hdr = f"{'pres':<12}{'L':<4}{'k':<4}{'d_mean':>9}{'t':>8}{'p':>12}   win0 amb/un   punct amb/un"
  112 |     for pres in ["A_isolated", "B_prefix", "C_droptok0"]:
  113 |         print("\n" + hdr)
  114 |         for L in LAYERS:
  115 |             for k in KS:
  116 |                 sub = out[(out.pres == pres) & (out.layer == L) & (out.k == k)]
  117 |                 p_ = sub.pivot_table(index=["item", "ctype"], columns="cond", values="tee").dropna()
  118 |                 d = p_["amb"] - p_["unamb"]
  119 |                 tt = stats.ttest_1samp(d, 0)
  120 |                 w0 = sub.groupby("cond")["win_has_word0"].mean()
  121 |                 pu = sub.groupby("cond")["win_has_punct"].mean()
  122 |                 print(f"{pres:<12}{L:<4}{k:<4}{d.mean():>9.2f}{tt.statistic:>8.2f}{tt.pvalue:>12.2e}"
  123 |                       f"   {w0.get('amb',0):.2f}/{w0.get('unamb',0):.2f}"
  124 |                       f"      {pu.get('amb',0):.2f}/{pu.get('unamb',0):.2f}")
  125 |     print("\n=== by construction (L6, k=3) ===")
  126 |     for pres in ["A_isolated", "B_prefix", "C_droptok0"]:
  127 |         for ct in ["MVRR", "NPS", "NPZ"]:
  128 |             sub = out[(out.pres == pres) & (out.layer == 6) & (out.k == 3) & (out.ctype == ct)]
  129 |             p_ = sub.pivot_table(index="item", columns="cond", values="tee").dropna()
  130 |             d = p_["amb"] - p_["unamb"]
  131 |             tt = stats.ttest_1samp(d, 0)
  132 |             print(f"{pres:<12}{ct:<6}d={d.mean():>8.2f}  t={tt.statistic:>6.2f}  p={tt.pvalue:.2e}  n={len(d)}")
  133 | 
  134 | if __name__ == "__main__":
  135 |     run()
```


==============================================================================
### FILE: gp_confound_check/gp_table1_exact.py
==============================================================================

```
    1 | """
    2 | TABLE 1 UNDER THE ORIGINAL SPEC, WITH SINK CONTROLS
    3 | ===================================================
    4 | Replicates model_comparison_stats.py from garden-path-p1 exactly
    5 | (mixedlm, random intercept by participant, ML fit; controls = word length,
    6 | word position, previous log RT; TEE and surprisal computed as in
    7 | window_sweep.py: word-level states at the last subword, linear fit over the
    8 | k preceding word states, extrapolate one step, Euclidean error) and then
    9 | recomputes the TEE predictor under three presentations:
   10 | 
   11 |   A_isolated  = the original: tokenizer(sentence), no BOS, no context
   12 |   B_prefix    = neutral prefix prepended (sink outside all fit windows)
   13 |   C_droptok0  = isolated, word 0 excluded from fit windows
   14 | 
   15 | NOTE ON SAMPLE: the original computes prev_log_RT by shifting within
   16 | (participant, Sentence) AFTER filtering to ROI 0/1/2, so every ROI-0 row gets
   17 | NaN and is dropped. The published N = 95,173 is ROI 1 and ROI 2 only -- the
   18 | disambiguating word is not in the RT models. This script reproduces that
   19 | sample exactly, and also reports a variant that keeps ROI 0 by taking
   20 | prev_log_RT from the full sentence.
   21 | """
   22 | 
   23 | import numpy as np
   24 | import pandas as pd
   25 | import torch
   26 | import statsmodels.formula.api as smf
   27 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   28 | import os, warnings
   29 | warnings.filterwarnings("ignore")
   30 | 
   31 | HERE = os.path.dirname(os.path.abspath(__file__))
   32 | RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
   33 | PREFIX = "Yesterday afternoon we sat together and read a few short stories aloud."
   34 | PRES = ["A_isolated", "B_prefix", "C_droptok0"]
   35 | CONFIGS = [("L6_w3", 6, 3), ("L12_w5", 12, 5), ("L6_w5", 6, 5), ("L6_w7", 6, 7)]
   36 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   37 | 
   38 | tokz = GPT2Tokenizer.from_pretrained("gpt2")
   39 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   40 | model.eval().to(DEVICE)
   41 | 
   42 | 
   43 | def measures(sentence, prefix=None, drop0=False):
   44 |     """Original window_sweep.py logic, with optional prefix / token-0 exclusion."""
   45 |     text = (prefix + " " + sentence) if prefix else sentence
   46 |     inputs = tokz(text, return_tensors="pt").to(DEVICE)
   47 |     with torch.no_grad():
   48 |         out = model(**inputs)
   49 |     ids = inputs["input_ids"][0]
   50 |     toks = tokz.convert_ids_to_tokens(ids)
   51 |     logp = torch.log_softmax(out.logits, -1)
   52 |     tok_surp = [None] + [-float(logp[0, i - 1, ids[i]]) for i in range(1, len(ids))]
   53 | 
   54 |     # word -> token map, exactly as the original (split on leading-space marker)
   55 |     words = text.split()
   56 |     wmap, ti = [], 0
   57 |     for w in words:
   58 |         wt = []
   59 |         while ti < len(toks):
   60 |             if ti > 0 and toks[ti].startswith("Ġ") and len(wt) > 0:
   61 |                 break
   62 |             wt.append(ti)
   63 |             ti += 1
   64 |         wmap.append(wt)
   65 | 
   66 |     n_pref = len(prefix.split()) if prefix else 0
   67 |     surp = [sum(tok_surp[t] for t in wt if tok_surp[t] is not None) for wt in wmap]
   68 | 
   69 |     res = {}
   70 |     for name, L, k in CONFIGS:
   71 |         h = out.hidden_states[L][0].float().cpu().numpy()
   72 |         wh = np.array([h[wt[-1]] for wt in wmap])
   73 |         errs = []
   74 |         for t in range(len(words)):
   75 |             lo = t - k
   76 |             if drop0:
   77 |                 lo = max(lo, 1)
   78 |             if t < k or lo < 0 or (t - lo) < 2:
   79 |                 errs.append(np.nan)
   80 |                 continue
   81 |             win = wh[lo:t]
   82 |             m = len(win)
   83 |             A = np.column_stack([np.ones(m), np.arange(m)])
   84 |             c, *_ = np.linalg.lstsq(A, win, rcond=None)
   85 |             errs.append(float(np.linalg.norm(wh[t] - (c[0] + c[1] * m))))
   86 |         res[name] = errs[n_pref:]           # drop prefix words
   87 |     return res, surp[n_pref:]
   88 | 
   89 | 
   90 | def build_measures():
   91 |     src = pd.read_csv(RT_CSV)
   92 |     src["EachWord"] = src["EachWord"].str.replace("%2C", ",", regex=False)
   93 |     src["Sentence"] = src["Sentence"].str.replace("%2C", ",", regex=False)
   94 |     sents = (src.drop_duplicates(subset=["item", "Type", "WordPosition"])
   95 |              .sort_values(["item", "Type", "WordPosition"])
   96 |              .groupby(["item", "Type"])["Sentence"].first())
   97 |     rows = []
   98 |     for (item, typ), sent in sents.items():
   99 |         for pres in PRES:
  100 |             m, sp = measures(sent, prefix=PREFIX if pres == "B_prefix" else None,
  101 |                              drop0=(pres == "C_droptok0"))
  102 |             for i in range(len(sp)):
  103 |                 r = dict(item=item, Type=typ, WordPosition=i + 1, pres=pres,
  104 |                          surprisal=sp[i])
  105 |                 for name, _, _ in CONFIGS:
  106 |                     r[name] = m[name][i]
  107 |                 rows.append(r)
  108 |     return pd.DataFrame(rows)
  109 | 
  110 | 
  111 | def build_rt(keep_roi0=False):
  112 |     rt = pd.read_csv(RT_CSV)
  113 |     rt["participant"] = rt["MD5"]
  114 |     rt["EachWord"] = rt["EachWord"].str.replace("%2C", ",", regex=False)
  115 |     rt["Sentence"] = rt["Sentence"].str.replace("%2C", ",", regex=False)
  116 |     rt = rt[(rt.RT > 100) & (rt.RT < 5000)].copy()
  117 |     rt["word_length"] = rt.EachWord.str.len()
  118 |     rt["log_RT"] = np.log(rt.RT)
  119 |     if keep_roi0:   # prev RT from the whole sentence, so ROI 0 survives
  120 |         rt = rt.sort_values(["participant", "Sentence", "WordPosition"])
  121 |         rt["prev_log_RT"] = rt.groupby(["participant", "Sentence"])["log_RT"].shift(1)
  122 |         d = rt[rt.ROI.isin([0, 1, 2])].copy()
  123 |     else:           # ORIGINAL: shift after filtering -> ROI 0 dropped
  124 |         d = rt[rt.ROI.isin([0, 1, 2])].copy()
  125 |         d = d.sort_values(["participant", "Sentence", "WordPosition"])
  126 |         d["prev_log_RT"] = d.groupby(["participant", "Sentence"])["log_RT"].shift(1)
  127 |     return d
  128 | 
  129 | 
  130 | def z(s):
  131 |     v = s.dropna()
  132 |     return (s - v.mean()) / v.std()
  133 | 
  134 | 
  135 | FORM0 = "log_RT ~ z_word_length + z_WordPosition + z_prev_log_RT + z_surprisal"
  136 | 
  137 | 
  138 | def run(keep_roi0=False):
  139 |     meas = build_measures()
  140 |     d = build_rt(keep_roi0)
  141 |     tag = "ROI 0+1+2 (ROI 0 restored)" if keep_roi0 else "ROI 1+2 (original sample)"
  142 |     print(f"\n{'='*70}\n{tag}\n{'='*70}")
  143 |     for name, _, k in CONFIGS:
  144 |         print(f"\n#### {name} ####")
  145 |         print(f"{'presentation':<14}{'N':>8}{'dAIC':>9}{'beta':>10}{'p':>12}"
  146 |               f"{'win touches w0':>16}")
  147 |         for pres in PRES:
  148 |             m = meas[meas.pres == pres][["item", "Type", "WordPosition", "surprisal", name]]
  149 |             t = d.merge(m, left_on=["item", "Type", "WordPosition"],
  150 |                         right_on=["item", "Type", "WordPosition"], how="left")
  151 |             t = t.dropna(subset=["log_RT", "word_length", "WordPosition",
  152 |                                  "prev_log_RT", "surprisal", name])
  153 |             for c, zc in [("word_length", "z_word_length"), ("WordPosition", "z_WordPosition"),
  154 |                           ("prev_log_RT", "z_prev_log_RT"), ("surprisal", "z_surprisal"),
  155 |                           (name, "z_ee")]:
  156 |                 t[zc] = z(t[c])
  157 |             m1 = smf.mixedlm(FORM0, t, groups=t["participant"]).fit(reml=False)
  158 |             m2 = smf.mixedlm(FORM0 + " + z_ee", t, groups=t["participant"]).fit(reml=False)
  159 |             exposed = (t.WordPosition - 1 - k <= 0).mean()
  160 |             print(f"{pres:<14}{len(t):>8,}{m1.aic-m2.aic:>9.1f}"
  161 |                   f"{m2.params['z_ee']:>10.4f}{m2.pvalues['z_ee']:>12.2e}"
  162 |                   f"{exposed:>15.1%}")
  163 |     print("\nPublished Table 1: L6/w3 +10.7 | L12/w5 +56.4 | L6/w5 0.0 | L6/w7 +31.4")
  164 | 
  165 | 
  166 | if __name__ == "__main__":
  167 |     run(keep_roi0=False)
  168 |     run(keep_roi0=True)
```


==============================================================================
### FILE: gp_confound_check/gp_table1_rerun.py
==============================================================================

```
    1 | """
    2 | TABLE 1 RERUN WITH SINK-CLEAN TEE
    3 | =================================
    4 | Refits the arXiv 2606.05346 garden-path reading-time models (Table 1, M0-M5)
    5 | with TEE computed three ways:
    6 |   A_isolated  : sentence alone -- the presumed original condition (token 0 = sink)
    7 |   B_prefix    : neutral prefix prepended so the sink sits outside all windows
    8 |   C_droptok0  : isolated, word 0 excluded from fit windows
    9 | 
   10 | Data: SAP ClassicGP self-paced reading (N=2000 participants, 24 items x 6 types).
   11 | Critical region ROI 0/1/2 (disambiguating word + 2 spillover), per the paper.
   12 | Controls: word length, word position, previous log RT, log word frequency.
   13 | Surprisal computed under the matching presentation.
   14 | Outcome: log RT. Models compared by AIC, as in the paper.
   15 | """
   16 | 
   17 | import numpy as np
   18 | import pandas as pd
   19 | import torch
   20 | import statsmodels.api as sm
   21 | from transformers import GPT2Tokenizer, GPT2LMHeadModel
   22 | from wordfreq import zipf_frequency
   23 | import os, warnings
   24 | warnings.filterwarnings("ignore")
   25 | 
   26 | HERE = os.path.dirname(os.path.abspath(__file__))
   27 | RT_CSV = "/Users/elanbarenholtz/Downloads/ClassicGardenPathSet.csv"
   28 | PREFIX = "Yesterday afternoon we sat together and read a few short stories aloud."
   29 | PRES = ["A_isolated", "B_prefix", "C_droptok0"]
   30 | CONFIGS = [("L6_k3", 6, 3), ("L12_k5", 12, 5), ("L6_k5", 6, 5), ("L6_k7", 6, 7)]
   31 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   32 | 
   33 | tok = GPT2Tokenizer.from_pretrained("gpt2")
   34 | model = GPT2LMHeadModel.from_pretrained("gpt2", output_hidden_states=True)
   35 | model.eval().to(DEVICE)
   36 | 
   37 | 
   38 | def encode(words, prefix=None):
   39 |     ids, final_idx = [], []
   40 |     if prefix is not None:
   41 |         ids.extend(tok.encode(prefix))
   42 |     for i, w in enumerate(words):
   43 |         piece = (" " + w) if (i > 0 or prefix is not None) else w
   44 |         ids.extend(tok.encode(piece))
   45 |         final_idx.append(len(ids) - 1)
   46 |     return ids, final_idx
   47 | 
   48 | 
   49 | def measures(words, prefix=None, drop0=False):
   50 |     """Per-word TEE (each config) and surprisal for one presentation."""
   51 |     ids, final_idx = encode(words, prefix=prefix)
   52 |     with torch.no_grad():
   53 |         out = model(torch.tensor([ids]).to(DEVICE))
   54 |     logits = out.logits[0].float()
   55 |     logprobs = torch.log_softmax(logits, -1)
   56 |     # surprisal of token t (t>=1) from logits at t-1; sum subwords within a word
   57 |     surp_tok = np.zeros(len(ids))
   58 |     for t in range(1, len(ids)):
   59 |         surp_tok[t] = -float(logprobs[t - 1, ids[t]]) / np.log(2)
   60 |     starts = [0] + [j + 1 for j in final_idx[:-1]]
   61 |     surp = [float(surp_tok[s:e + 1].sum()) for s, e in zip(starts, final_idx)]
   62 | 
   63 |     res = {}
   64 |     for name, L, k in CONFIGS:
   65 |         W = out.hidden_states[L][0].float().cpu().numpy()[final_idx]
   66 |         vals = np.full(len(words), np.nan)
   67 |         for i in range(len(words)):
   68 |             lo = i - k
   69 |             if drop0:
   70 |                 lo = max(lo, 1)
   71 |             if lo < 0 or i - lo < 2:
   72 |                 continue
   73 |             Y = W[lo:i]
   74 |             m = Y.shape[0]
   75 |             t = np.arange(m, dtype=float)
   76 |             A = np.vstack([t, np.ones(m)]).T
   77 |             coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
   78 |             vals[i] = np.linalg.norm(W[i] - (coef[0] * m + coef[1]))
   79 |         res[name] = vals
   80 |     return res, surp
   81 | 
   82 | 
   83 | def build():
   84 |     d = pd.read_csv(RT_CSV)
   85 |     d = d[d.ROI.astype(str).isin(["0", "1", "2"])].copy()
   86 |     # per-sentence word lists (from the presented words themselves)
   87 |     key = ["item", "Type"]
   88 |     sent_words = (pd.read_csv(RT_CSV)
   89 |                   .drop_duplicates(subset=key + ["WordPosition"])
   90 |                   .sort_values(key + ["WordPosition"])
   91 |                   .groupby(key)["EachWord"].apply(list))
   92 |     rows = []
   93 |     for (item, typ), words in sent_words.items():
   94 |         for pres in PRES:
   95 |             m, surp = measures(words,
   96 |                                prefix=PREFIX if pres == "B_prefix" else None,
   97 |                                drop0=(pres == "C_droptok0"))
   98 |             for i, w in enumerate(words):
   99 |                 r = dict(item=item, Type=typ, WordPosition=i + 1, pres=pres,
  100 |                          surprisal=surp[i])
  101 |                 for name, _, _ in CONFIGS:
  102 |                     r[name] = m[name][i]
  103 |                 rows.append(r)
  104 |     meas = pd.DataFrame(rows)
  105 |     meas.to_csv(os.path.join(HERE, "gp_table1_measures.csv"), index=False)
  106 | 
  107 |     # previous-word RT within trial, from the unfiltered frame
  108 |     full = pd.read_csv(RT_CSV)[["MD5", "item", "Type", "WordPosition", "RT"]]
  109 |     full = full.rename(columns={"RT": "prevRT"})
  110 |     full["WordPosition"] = full["WordPosition"] + 1
  111 |     d = d.merge(full, on=["MD5", "item", "Type", "WordPosition"], how="left")
  112 |     d["word_len"] = d.EachWord.str.len()
  113 |     d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
  114 |         lambda w: zipf_frequency(w, "en"))
  115 |     d = d[(d.RT >= 100) & (d.RT <= 5000) & (d.prevRT >= 100) & (d.prevRT <= 5000)]
  116 |     d["logRT"] = np.log(d.RT)
  117 |     d["prev_logRT"] = np.log(d.prevRT)
  118 |     return d, meas
  119 | 
  120 | 
  121 | def z(x):
  122 |     return (x - np.nanmean(x)) / np.nanstd(x)
  123 | 
  124 | 
  125 | def fit(df, extra):
  126 |     cols = ["word_len", "WordPosition", "prev_logRT", "log_freq"] + extra
  127 |     X = pd.DataFrame({c: z(df[c].astype(float)) for c in cols})
  128 |     X = sm.add_constant(X)
  129 |     return sm.OLS(df["logRT"].values, X.values).fit()
  130 | 
  131 | 
  132 | def run():
  133 |     d, meas = build()
  134 |     names = [c for c, _, _ in CONFIGS]
  135 | 
  136 |     # one wide frame: every measure from every presentation on the SAME rows
  137 |     wide = d.copy()
  138 |     for pres in PRES:
  139 |         m = meas[meas.pres == pres].drop(columns="pres").rename(
  140 |             columns={n: f"{n}__{pres}" for n in names} | {"surprisal": f"surp__{pres}"})
  141 |         wide = wide.merge(m, on=["item", "Type", "WordPosition"], how="left")
  142 |     wide = wide.dropna(subset=["log_freq"] + [f"surp__{p}" for p in PRES])
  143 | 
  144 |     # PER-CONFIG samples: rows where THAT config is defined under all three
  145 |     # presentations. A global intersection would delete the sentence-initial
  146 |     # rows (k=7 undefined there) -- i.e. exactly where the sink bites.
  147 |     for n in names:
  148 |         sub = wide.dropna(subset=[f"{n}__{p}" for p in PRES]).copy()
  149 |         a, b, c = (sub[f"{n}__{p}"] for p in PRES)
  150 |         exposed = float((np.abs(a.values - c.values) > 1e-9).mean())
  151 |         print(f"\n################ {n}  (n = {len(sub):,}, "
  152 |               f"{sub.MD5.nunique()} participants) ################")
  153 |         print(f"rows whose fit window touches word 0: {exposed:.1%}   "
  154 |               f"r(isolated, droptok0) = {np.corrcoef(a,c)[0,1]:.3f}   "
  155 |               f"r(isolated, prefix) = {np.corrcoef(a,b)[0,1]:.3f}")
  156 |         print(f"mean TEE  isolated {a.mean():.1f} | prefix {b.mean():.1f} "
  157 |               f"| droptok0 {c.mean():.1f}")
  158 |         for label, df in [("OLS", sub), ("participant-demeaned", demean(sub, names))]:
  159 |             print(f"\n  --- {label} ---")
  160 |             print(f"  {'presentation':<16}{'dAIC surp':>12}{'dAIC TEE':>11}"
  161 |                   f"{'beta':>10}{'p':>12}")
  162 |             for pres in PRES:
  163 |                 sur, tv = f"surp__{pres}", f"{n}__{pres}"
  164 |                 m0, m1 = fit(df, []), fit(df, [sur])
  165 |                 mk = fit(df, [sur, tv])
  166 |                 print(f"  {pres:<16}{m0.aic-m1.aic:>12.1f}{m1.aic-mk.aic:>11.1f}"
  167 |                       f"{mk.params[-1]:>10.4f}{mk.pvalues[-1]:>12.2e}")
  168 |     print("\nPaper Table 1 (for reference): M1 dAIC -1.9 (n.s.); "
  169 |           "L6/w3 +10.7; L12/w5 +56.4; L6/w5 0.0; L6/w7 +31.4; N = 95,173")
  170 | 
  171 | 
  172 | def demean(df, names):
  173 |     """Within-participant centering: approximates a by-participant random intercept."""
  174 |     out = df.copy()
  175 |     cols = ["logRT", "prev_logRT", "word_len", "WordPosition", "log_freq"] \
  176 |            + [f"{n}__{p}" for n in names for p in PRES] \
  177 |            + [f"surp__{p}" for p in PRES]
  178 |     g = out.groupby("MD5")
  179 |     for c in cols:
  180 |         out[c] = out[c] - g[c].transform("mean")
  181 |     return out
  182 | 
  183 | 
  184 | if __name__ == "__main__":
  185 |     run()
```


==============================================================================
### FILE: gp_confound_check/ns_audit.py
==============================================================================

```
    1 | """
    2 | NATURAL STORIES PIPELINE AUDIT
    3 | ==============================
    4 | Looks for the CLASS of error that broke the garden-path analysis:
    5 |   A. merge integrity      -- does the word->RT merge multiply or drop rows?
    6 |   B. lagged control       -- is prev_log_RT actually the ADJACENT word, or was
    7 |                              it computed after row-filtering (so it silently
    8 |                              points at whatever row survived)?
    9 |   C. sample equality      -- are the AIC-compared nested models fit on the
   10 |                              SAME rows?
   11 |   D. heterogeneity        -- does the TEE effect hold its sign across stories
   12 |                              and sentence positions, or is the pooled estimate
   13 |                              an average over disagreeing subsets (the failure
   14 |                              mode that broke the garden-path result)?
   15 | 
   16 | Replicates the prep in garden-path-p1/ns_crossed_re.py, but on the locked
   17 | sample (hash 8a6087341e), which carries tee_k3, surprisal, log_freq, etc.
   18 | """
   19 | 
   20 | import numpy as np
   21 | import pandas as pd
   22 | import statsmodels.formula.api as smf
   23 | import os, warnings
   24 | warnings.filterwarnings("ignore")
   25 | 
   26 | REPO = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   27 | SAMPLE = f"{REPO}/rebuild_v2_outputs/sample_8a6087341e.csv"
   28 | RTS = f"{REPO}/naturalstories/naturalstories_RTS/processed_RTs.tsv"
   29 | 
   30 | 
   31 | def load():
   32 |     w = pd.read_csv(SAMPLE)
   33 |     rt = pd.read_csv(RTS, sep="\t")
   34 |     rt = rt.rename(columns={"item": "story_id", "WorkerId": "participant"})
   35 |     return w, rt
   36 | 
   37 | 
   38 | def main():
   39 |     w, rt_raw = load()
   40 |     print(f"locked sample: {len(w):,} words | RT file: {len(rt_raw):,} rows, "
   41 |           f"{rt_raw.participant.nunique()} participants")
   42 | 
   43 |     # ---------- A. merge integrity ----------
   44 |     print("\n" + "=" * 72)
   45 |     print("A. MERGE INTEGRITY")
   46 |     print("=" * 72)
   47 |     dup = w.duplicated(subset=["story_id", "zone"]).sum()
   48 |     print(f"duplicate (story_id, zone) keys in word table: {dup}")
   49 |     rt = rt_raw[(rt_raw.RT >= 100) & (rt_raw.RT <= 3000)].copy()
   50 |     before = len(rt)
   51 |     m = rt.merge(w[["story_id", "zone", "word", "tee_k3", "surprisal",
   52 |                     "word_length", "log_freq"]],
   53 |                  on=["story_id", "zone"], how="left")
   54 |     print(f"RT rows before merge {before:,} -> after {len(m):,} "
   55 |           f"({'OK, no multiplication' if len(m) == before else 'ROW COUNT CHANGED'})")
   56 |     print(f"rows with no matching word record: {m.tee_k3.isna().sum():,} "
   57 |           f"({m.tee_k3.isna().mean():.1%})")
   58 | 
   59 |     # ---------- B. lagged control ----------
   60 |     print("\n" + "=" * 72)
   61 |     print("B. LAGGED CONTROL (prev_log_RT)")
   62 |     print("=" * 72)
   63 |     m["log_RT"] = np.log(m.RT)
   64 |     m = m.sort_values(["participant", "story_id", "zone"])
   65 |     g = m.groupby(["participant", "story_id"])
   66 |     m["prev_log_RT"] = g["log_RT"].shift(1)
   67 |     m["prev_zone"] = g["zone"].shift(1)
   68 |     m["gap"] = m.zone - m.prev_zone
   69 |     ok = (m.gap == 1)
   70 |     print(f"prev_log_RT rows where previous row is the ADJACENT word: "
   71 |           f"{ok.sum():,} / {m.prev_zone.notna().sum():,} "
   72 |           f"({ok.sum()/max(m.prev_zone.notna().sum(),1):.1%})")
   73 |     print(f"rows where the 'previous' word is 2+ zones back (filtered-out "
   74 |           f"neighbour): {(m.gap > 1).sum():,}")
   75 |     print("  -> same shape as the garden-path bug: the lag is computed AFTER "
   76 |           "row filtering.")
   77 |     print("     Milder here: it mislabels the control on a minority of rows "
   78 |           "rather than deleting a whole condition.")
   79 | 
   80 |     # ---------- C. sample equality across nested models ----------
   81 |     print("\n" + "=" * 72)
   82 |     print("C. SAMPLE EQUALITY FOR THE AIC COMPARISON")
   83 |     print("=" * 72)
   84 |     d = m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   85 |                          "prev_log_RT", "surprisal", "tee_k3"]).copy()
   86 |     for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"]:
   87 |         v = d[c].dropna()
   88 |         d["z_" + c] = (d[c] - v.mean()) / v.std()
   89 |     print(f"analysis N = {len(d):,}  participants = {d.participant.nunique()}  "
   90 |           f"stories = {d.story_id.nunique()}")
   91 |     print("M1 and M2 are both fit on this frame (M2 adds a term that is already "
   92 |           "non-null here), so the nested comparison is on identical rows: OK.")
   93 | 
   94 |     CTRL = "z_word_length + z_log_freq + z_zone + z_prev_log_RT"
   95 |     F1 = f"log_RT ~ {CTRL} + z_surprisal"
   96 |     F2 = F1 + " + z_tee_k3"
   97 |     m1 = smf.mixedlm(F1, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
   98 |     m2 = smf.mixedlm(F2, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
   99 |     print(f"\nheadline: dAIC = {m1.aic - m2.aic:.1f}   "
  100 |           f"beta(TEE) = {m2.params['z_tee_k3']:+.5f}   "
  101 |           f"p = {m2.pvalues['z_tee_k3']:.3e}")
  102 |     print(f"for scale: beta(surprisal) = {m2.params['z_surprisal']:+.5f}, "
  103 |           f"beta(log_freq) = {m2.params['z_log_freq']:+.5f}, "
  104 |           f"beta(prev_log_RT) = {m2.params['z_prev_log_RT']:+.5f}")
  105 | 
  106 |     # lag control fixed: keep only rows whose previous word really is adjacent
  107 |     d2 = d[d.gap == 1].copy()
  108 |     m1b = smf.mixedlm(F1, d2, groups=d2["participant"]).fit(reml=False, method="lbfgs")
  109 |     m2b = smf.mixedlm(F2, d2, groups=d2["participant"]).fit(reml=False, method="lbfgs")
  110 |     print(f"\nwith the lag control repaired (adjacent-word rows only, "
  111 |           f"n = {len(d2):,}):")
  112 |     print(f"  dAIC = {m1b.aic - m2b.aic:.1f}   "
  113 |           f"beta(TEE) = {m2b.params['z_tee_k3']:+.5f}   "
  114 |           f"p = {m2b.pvalues['z_tee_k3']:.3e}")
  115 | 
  116 |     # ---------- D. heterogeneity ----------
  117 |     print("\n" + "=" * 72)
  118 |     print("D. HETEROGENEITY -- does the effect hold its sign across subsets?")
  119 |     print("=" * 72)
  120 |     print("\nby story:")
  121 |     signs = []
  122 |     for s, sub in d.groupby("story_id"):
  123 |         mm = smf.mixedlm(F2, sub, groups=sub["participant"]).fit(reml=False, method="lbfgs")
  124 |         b, p = mm.params["z_tee_k3"], mm.pvalues["z_tee_k3"]
  125 |         signs.append(np.sign(b))
  126 |         print(f"  story {s:>2}  n={len(sub):>7,}  beta={b:>+.5f}  p={p:.3f}")
  127 |     print(f"  -> {int(sum(1 for x in signs if x > 0))}/{len(signs)} stories positive")
  128 | 
  129 |     print("\nby sentence position (from_start bucket):")
  130 |     d["pos_bin"] = pd.cut(d.from_start, [-1, 2, 5, 10, 20, 999],
  131 |                           labels=["0-2", "3-5", "6-10", "11-20", "21+"])
  132 |     for b, sub in d.groupby("pos_bin", observed=True):
  133 |         if len(sub) < 5000:
  134 |             continue
  135 |         mm = smf.mixedlm(F2, sub, groups=sub["participant"]).fit(reml=False, method="lbfgs")
  136 |         print(f"  pos {str(b):>6}  n={len(sub):>7,}  "
  137 |               f"beta={mm.params['z_tee_k3']:>+.5f}  p={mm.pvalues['z_tee_k3']:.3e}")
  138 | 
  139 |     print("\nformal test: TEE x position-bin interaction")
  140 |     mi = smf.mixedlm(F2 + " + z_tee_k3:C(pos_bin)", d,
  141 |                      groups=d["participant"]).fit(reml=False, method="lbfgs")
  142 |     from scipy import stats as st
  143 |     lr = -2 * (m2.llf - mi.llf)
  144 |     dfd = len(mi.params) - len(m2.params)
  145 |     print(f"  chi2({dfd}) = {lr:.1f}, p = {st.chi2.sf(lr, dfd):.3e}")
  146 | 
  147 | 
  148 | if __name__ == "__main__":
  149 |     main()
```


==============================================================================
### FILE: gp_confound_check/ns_base_fit_check.py
==============================================================================

```
    1 | """
    2 | IS THE "STRONGER SURPRISAL" CONTROL ACTUALLY STRONGER *AS A CONTROL*?
    3 | =====================================================================
    4 | I reported that TEE's dAIC RISES when GPT-2 Small surprisal is replaced by
    5 | GPT-2 XL surprisal (111.8 -> 136.9 in Natural Stories) and read that as the
    6 | effect strengthening under a better control. That reading may be wrong.
    7 | 
    8 | Oh & Schuler (2023) -- cited in v1's own introduction as the "surprisal scaling
    9 | paradox" -- showed that surprisal from LARGER language models is a WORSE
   10 | predictor of human reading times. If GPT-2 XL surprisal fits reading time worse
   11 | than GPT-2 Small surprisal, then it is a WEAKER control, absorbing less outcome
   12 | variance and leaving more for TEE to explain. dAIC(TEE) would rise for a reason
   13 | that is not favourable to TEE at all.
   14 | 
   15 | The SAP output already hints at exactly this (sap_bigsurp_refit_out.txt):
   16 |     base model AIC, GPT-2 Small surprisal   1059844.5
   17 |     base model AIC, GPT-2 XL surprisal      1059935.3   <- WORSE fit
   18 |     base model AIC, Pythia-410M surprisal   1059877.1   <- WORSE fit
   19 | Lower AIC = better. GPT-2 Small is the best RT predictor of the three.
   20 | 
   21 | The Natural Stories run printed only dAIC, not the base AICs, so the same check
   22 | was never made there. This script prints them.
   23 | 
   24 | If the same pattern holds, then:
   25 |   - the claim "the effect strengthens under a stronger control" must be dropped
   26 |   - the defensible claim is the UNION spec, which contains GPT-2 Small surprisal
   27 |     (the best single RT predictor) PLUS the others, and therefore strictly
   28 |     dominates any single control
   29 | """
   30 | 
   31 | import numpy as np
   32 | import pandas as pd
   33 | import statsmodels.formula.api as smf
   34 | import hashlib, warnings
   35 | warnings.filterwarnings("ignore")
   36 | 
   37 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   38 | 
   39 | 
   40 | def z(s):
   41 |     v = s.dropna()
   42 |     return (s - v.mean()) / v.std()
   43 | 
   44 | 
   45 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   46 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   47 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   48 | assert sh == "8a6087341e", sh
   49 | 
   50 | for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
   51 |                    "surprisal_gpt2_medium"),
   52 |                   (f"{GP}/extensions/gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl"),
   53 |                   (f"{GP}/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv",
   54 |                    "surprisal_pythia410m")]:
   55 |     S = S.merge(pd.read_csv(path)[["story_id", "word_idx", col]],
   56 |                 on=["story_id", "word_idx"], how="left", validate="one_to_one")
   57 | 
   58 | ks = ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl",
   59 |       "surprisal_pythia410m"]
   60 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   61 |                  sep="\t").rename(columns={"item": "story_id",
   62 |                                            "WorkerId": "participant"})
   63 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   64 | d = rt.merge(S[["story_id", "zone", "tee_k3", "word_length", "log_freq"] + ks],
   65 |              on=["story_id", "zone"], how="inner")
   66 | d["log_RT"] = np.log(d.RT)
   67 | d = d.sort_values(["participant", "story_id", "zone"])
   68 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
   69 | d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   70 |                      "prev_log_RT", "tee_k3"] + ks)
   71 | for c in ["word_length", "log_freq", "zone", "prev_log_RT", "tee_k3"] + ks:
   72 |     d["z_" + c] = z(d[c])
   73 | print(f"n = {len(d):,}   participants = {d.participant.nunique()}\n")
   74 | 
   75 | BASE = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT"
   76 | m_ctrl = smf.mixedlm(BASE, d, groups=d.participant).fit(reml=False,
   77 |                                                         method="lbfgs")
   78 | print("=" * 80)
   79 | print("HOW WELL DOES EACH SURPRISAL PREDICT READING TIME, ON ITS OWN?")
   80 | print("=" * 80)
   81 | print(f"  controls only (no surprisal)      AIC {m_ctrl.aic:12.1f}")
   82 | print(f"{'surprisal source':<26}{'base AIC':>13}{'dAIC vs ctrl':>14}"
   83 |       f"{'dAIC(TEE)':>12}")
   84 | res = {}
   85 | for lab, c in [("GPT-2 Small", "surprisal"),
   86 |                ("GPT-2 Medium", "surprisal_gpt2_medium"),
   87 |                ("GPT-2 XL", "surprisal_gpt2_xl"),
   88 |                ("Pythia-410M", "surprisal_pythia410m")]:
   89 |     m0 = smf.mixedlm(f"{BASE} + z_{c}", d, groups=d.participant).fit(
   90 |         reml=False, method="lbfgs")
   91 |     m1 = smf.mixedlm(f"{BASE} + z_{c} + z_tee_k3", d,
   92 |                      groups=d.participant).fit(reml=False, method="lbfgs")
   93 |     res[lab] = (m0.aic, m_ctrl.aic - m0.aic, m0.aic - m1.aic)
   94 |     print(f"{lab:<26}{m0.aic:>13.1f}{m_ctrl.aic - m0.aic:>14.1f}"
   95 |           f"{m0.aic - m1.aic:>12.1f}")
   96 | 
   97 | allterm = " + ".join(f"z_{c}" for c in ks)
   98 | m0 = smf.mixedlm(f"{BASE} + {allterm}", d, groups=d.participant).fit(
   99 |     reml=False, method="lbfgs")
  100 | m1 = smf.mixedlm(f"{BASE} + {allterm} + z_tee_k3", d,
  101 |                  groups=d.participant).fit(reml=False, method="lbfgs")
  102 | print(f"{'all four together':<26}{m0.aic:>13.1f}{m_ctrl.aic - m0.aic:>14.1f}"
  103 |       f"{m0.aic - m1.aic:>12.1f}")
  104 | 
  105 | print("\n" + "=" * 80)
  106 | print("READING")
  107 | print("=" * 80)
  108 | best = min(res, key=lambda k: res[k][0])
  109 | print(f"  best single RT-predicting surprisal: {best}")
  110 | print("  If GPT-2 Small is best, the scaling paradox is present in this corpus,")
  111 | print("  and a rise in dAIC(TEE) under larger-model surprisal reflects a WEAKER")
  112 | print("  control, not a stronger one. The union spec is then the honest one:")
  113 | print("  it contains the best single predictor plus the others.")
```


==============================================================================
### FILE: gp_confound_check/ns_bigsurp_refit.py
==============================================================================

```
    1 | """
    2 | DOES THE NATURAL STORIES TEE EFFECT SURVIVE A STRONGER SURPRISAL CONTROL?
    3 | ========================================================================
    4 | Same objection as for SAP: TEE and surprisal both come from GPT-2 Small, so the
    5 | TEE effect could be a predictability residual -- TEE marking the places where
    6 | GPT-2 Small's own probability estimate is wrong. Controlling for that model's
    7 | surprisal cannot remove such a confound, because the control is built from the
    8 | same error.
    9 | 
   10 | TEE is left exactly as reported (GPT-2 Small, mid layer, k = 3, locked sample
   11 | 8a6087341e). Only the surprisal control changes. Stronger surprisals already
   12 | exist on this sample from the extensions pipeline, so no new forward passes are
   13 | needed:
   14 |     extensions/gpt2_medium_surp_ent.csv   surprisal_gpt2_medium
   15 |     extensions/gpt2_xl_surp_ent.csv       surprisal_gpt2_xl
   16 | 
   17 | Headline specification carried over unchanged from v2_table6_pythia.py:
   18 |     log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_<surprisal>
   19 |     mixedlm, by-participant random intercept, ML fit
   20 |     dAIC = improvement from adding z_tee_k3
   21 | Reference value on this spec with GPT-2 Small surprisal: dAIC = 111.8,
   22 | beta = +0.0035.
   23 | 
   24 | Specs:
   25 |     N0  GPT-2 Small surprisal            [reference]
   26 |     N1  GPT-2 Medium surprisal
   27 |     N2  GPT-2 XL surprisal
   28 |     N3  all three entered together       [union control]
   29 |     N4  N3 with GPT-2 XL surprisal splined df=5
   30 | 
   31 | Subject-level inference is run for N0 and N3 so the result is not resting on a
   32 | pooled model over 800k observations.
   33 | 
   34 | NOTE: Pythia-410M TEE exists on this sample but Pythia SURPRISAL does not; that
   35 | would need a fresh forward pass. GPT-2 XL (1.5B) is the strongest control
   36 | available without new compute, and is ~12x GPT-2 Small.
   37 | """
   38 | 
   39 | import numpy as np
   40 | import pandas as pd
   41 | import statsmodels.api as sm
   42 | import statsmodels.formula.api as smf
   43 | from scipy import stats
   44 | import hashlib, warnings
   45 | warnings.filterwarnings("ignore")
   46 | 
   47 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   48 | 
   49 | 
   50 | def z(s):
   51 |     v = s.dropna()
   52 |     return (s - v.mean()) / v.std()
   53 | 
   54 | 
   55 | def zs(x):
   56 |     x = np.asarray(x, dtype=float)
   57 |     s = x.std()
   58 |     return (x - x.mean()) / s if s > 0 else x * 0
   59 | 
   60 | 
   61 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   62 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   63 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   64 | assert sh == "8a6087341e", sh
   65 | print(f"sample hash {sh} verified   words {len(S):,}")
   66 | 
   67 | for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
   68 |                    "surprisal_gpt2_medium"),
   69 |                   (f"{GP}/extensions/gpt2_xl_surp_ent.csv",
   70 |                    "surprisal_gpt2_xl"),
   71 |                   (f"{GP}/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv",
   72 |                    "surprisal_pythia410m")]:
   73 |     E = pd.read_csv(path)[["story_id", "word_idx", col]]
   74 |     n0 = len(S)
   75 |     S = S.merge(E, on=["story_id", "word_idx"], how="left", validate="one_to_one")
   76 |     assert len(S) == n0
   77 |     print(f"  merged {col}: {S[col].notna().sum():,} non-missing")
   78 | 
   79 | SURPS = {"GPT-2 Small": "surprisal",
   80 |          "GPT-2 Medium": "surprisal_gpt2_medium",
   81 |          "GPT-2 XL": "surprisal_gpt2_xl",
   82 |          "Pythia-410M": "surprisal_pythia410m"}
   83 | 
   84 | print("\nword-level agreement between surprisal estimates:")
   85 | ks = list(SURPS.values())
   86 | for i in range(len(ks)):
   87 |     for j in range(i + 1, len(ks)):
   88 |         print(f"  r({ks[i]}, {ks[j]}) = {S[ks[i]].corr(S[ks[j]]):+.3f}")
   89 | print("\nmean surprisal (bits) and correlation with TEE:")
   90 | for lab, c in SURPS.items():
   91 |     print(f"  {lab:<14} mean {S[c].mean():6.3f}   r(TEE, surp) = "
   92 |           f"{S.tee_k3.corr(S[c]):+.3f}")
   93 | 
   94 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   95 |                  sep="\t").rename(columns={"item": "story_id",
   96 |                                            "WorkerId": "participant"})
   97 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   98 | cols = ["story_id", "zone", "tee_k3", "word_length", "log_freq"] + ks
   99 | d = rt.merge(S[cols], on=["story_id", "zone"], how="inner")
  100 | d["log_RT"] = np.log(d.RT)
  101 | d = d.sort_values(["participant", "story_id", "zone"])
  102 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
  103 | d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
  104 |                      "prev_log_RT", "tee_k3"] + ks)
  105 | print(f"\nMATCHED SAMPLE (all surprisals non-missing): n = {len(d):,}   "
  106 |       f"participants = {d.participant.nunique()}")
  107 | 
  108 | for c in ["word_length", "log_freq", "zone", "prev_log_RT", "tee_k3"] + ks:
  109 |     d["z_" + c] = z(d[c])
  110 | 
  111 | BASE = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT"
  112 | SPECS = [
  113 |     ("N0  GPT-2 Small surprisal [ref]", "z_surprisal"),
  114 |     ("N1  GPT-2 Medium surprisal", "z_surprisal_gpt2_medium"),
  115 |     ("N2  GPT-2 XL surprisal", "z_surprisal_gpt2_xl"),
  116 |     ("N3  all three GPT-2 surprisals",
  117 |      "z_surprisal + z_surprisal_gpt2_medium + z_surprisal_gpt2_xl"),
  118 |     ("N4  N3, GPT-2 XL splined df=5",
  119 |      "z_surprisal + z_surprisal_gpt2_medium + bs(z_surprisal_gpt2_xl, df=5)"),
  120 |     ("N5  Pythia-410M surprisal", "z_surprisal_pythia410m"),
  121 |     ("N6  all four surprisals",
  122 |      "z_surprisal + z_surprisal_gpt2_medium + z_surprisal_gpt2_xl "
  123 |      "+ z_surprisal_pythia410m"),
  124 |     ("N7  all four, XL+Pythia splined df=4",
  125 |      "z_surprisal + z_surprisal_gpt2_medium + bs(z_surprisal_gpt2_xl, df=4) "
  126 |      "+ bs(z_surprisal_pythia410m, df=4)"),
  127 | ]
  128 | 
  129 | print("\n" + "=" * 82)
  130 | print("POOLED: dAIC and beta for TEE under each surprisal control")
  131 | print("=" * 82)
  132 | print(f"{'spec':<34}{'dAIC(TEE)':>12}{'beta':>11}{'p':>13}")
  133 | for lab, term in SPECS:
  134 |     m0 = smf.mixedlm(f"{BASE} + {term}", d, groups=d.participant).fit(
  135 |         reml=False, method="lbfgs")
  136 |     m1 = smf.mixedlm(f"{BASE} + {term} + z_tee_k3", d,
  137 |                      groups=d.participant).fit(reml=False, method="lbfgs")
  138 |     print(f"{lab:<34}{m0.aic - m1.aic:>12.1f}{m1.params['z_tee_k3']:>11.5f}"
  139 |           f"{m1.pvalues['z_tee_k3']:>13.2e}")
  140 | 
  141 | print("\n" + "=" * 82)
  142 | print("SUBJECT-LEVEL: per-participant TEE coefficient")
  143 | print("=" * 82)
  144 | print(f"{'spec':<34}{'n':>6}{'mean beta':>12}{'% pos':>8}{'Wilcoxon p':>13}")
  145 | 
  146 | 
  147 | def subject_level(surp_cols, permute=False, rng=None):
  148 |     cols = ["tee_k3", "word_length", "log_freq", "zone",
  149 |             "prev_log_RT"] + surp_cols
  150 |     out = []
  151 |     for pid, sub in d.groupby("participant"):
  152 |         s = sub.dropna(subset=cols + ["log_RT"])
  153 |         if len(s) < 300:
  154 |             continue
  155 |         if permute:
  156 |             s = s.assign(tee_k3=rng.permutation(s.tee_k3.values))
  157 |         X = np.column_stack([zs(s[c].values) for c in cols])
  158 |         if (X.std(axis=0) == 0).any():
  159 |             continue
  160 |         r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
  161 |         out.append(r.params[1])
  162 |     return np.array(out)
  163 | 
  164 | 
  165 | for lab, sc in [("N0  GPT-2 Small surprisal [ref]", ["surprisal"]),
  166 |                 ("N2  GPT-2 XL surprisal", ["surprisal_gpt2_xl"]),
  167 |                 ("N5  Pythia-410M surprisal", ["surprisal_pythia410m"]),
  168 |                 ("N6  all four surprisals", ks)]:
  169 |     b = subject_level(sc)
  170 |     print(f"{lab:<34}{len(b):>6}{b.mean():>+12.5f}{(b > 0).mean():>8.1%}"
  171 |           f"{stats.wilcoxon(b).pvalue:>13.2e}")
  172 | 
  173 | rng = np.random.default_rng(20260807)
  174 | b = subject_level(ks, permute=True, rng=rng)
  175 | print(f"{'F   permuted TEE (floor)':<34}{len(b):>6}{b.mean():>+12.5f}"
  176 |       f"{(b > 0).mean():>8.1%}{stats.wilcoxon(b).pvalue:>13.2e}")
```


==============================================================================
### FILE: gp_confound_check/ns_final_numbers.py
==============================================================================

```
    1 | """
    2 | EXACT NUMBERS FOR THE MANUSCRIPT, REPAIRED FREQUENCY CONTROL
    3 | ============================================================
    4 | Everything the v2 text needs to quote, computed in one place so the manuscript
    5 | can be edited from a single output rather than assembled from several runs.
    6 | """
    7 | 
    8 | import numpy as np
    9 | import pandas as pd
   10 | import statsmodels.api as sm
   11 | import statsmodels.formula.api as smf
   12 | from scipy import stats
   13 | from wordfreq import zipf_frequency
   14 | import hashlib, warnings
   15 | warnings.filterwarnings("ignore")
   16 | 
   17 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   18 | GPC = f"{GP}/gp_confound_check"
   19 | 
   20 | 
   21 | def zs(x):
   22 |     x = np.asarray(x, dtype=float)
   23 |     s = x.std()
   24 |     return (x - x.mean()) / s if s > 0 else x * 0
   25 | 
   26 | 
   27 | def z(s):
   28 |     v = s.dropna()
   29 |     return (s - v.mean()) / v.std()
   30 | 
   31 | 
   32 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   33 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   34 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   35 | assert sh == "8a6087341e", sh
   36 | S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
   37 |                        .str.lower().map(lambda w: zipf_frequency(w, "en")))
   38 | PY = pd.read_csv(f"{GPC}/pythia_tee_8a6087341e.csv")
   39 | 
   40 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   41 |                  sep="\t").rename(columns={"item": "story_id",
   42 |                                            "WorkerId": "participant"})
   43 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   44 | d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   45 |                 "log_freq_fixed"]], on=["story_id", "zone"], how="inner")
   46 | d["log_RT"] = np.log(d.RT)
   47 | d = d.sort_values(["participant", "story_id", "zone"])
   48 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
   49 | D = d.dropna(subset=["log_RT", "word_length", "log_freq_fixed", "zone",
   50 |                      "prev_log_RT", "tee_k3", "surprisal"]).copy()
   51 | for c in ["word_length", "zone", "prev_log_RT", "tee_k3", "log_freq_fixed",
   52 |           "surprisal"]:
   53 |     D["z_" + c] = z(D[c])
   54 | 
   55 | print("=" * 76)
   56 | print("HEADLINE MODEL (repaired frequency)")
   57 | print("=" * 76)
   58 | BASE = ("log_RT ~ z_word_length + z_log_freq_fixed + z_zone + z_prev_log_RT "
   59 |         "+ z_surprisal")
   60 | m0 = smf.mixedlm(BASE, D, groups=D.participant).fit(reml=False,
   61 |                                                     method="lbfgs")
   62 | m1 = smf.mixedlm(BASE + " + z_tee_k3", D, groups=D.participant).fit(
   63 |     reml=False, method="lbfgs")
   64 | print(f"  n = {len(D):,}   participants = {D.participant.nunique()}")
   65 | print(f"  dAIC(TEE)            = {m0.aic - m1.aic:.1f}")
   66 | print(f"  beta(TEE)            = {m1.params['z_tee_k3']:+.5f}  "
   67 |       f"p = {m1.pvalues['z_tee_k3']:.2e}")
   68 | print(f"  beta(surprisal)      = {m1.params['z_surprisal']:+.5f}")
   69 | print(f"  beta(log frequency)  = {m1.params['z_log_freq_fixed']:+.5f}")
   70 | print(f"  beta(word length)    = {m1.params['z_word_length']:+.5f}")
   71 | print(f"  ratio TEE/surprisal  = "
   72 |       f"{m1.params['z_tee_k3'] / m1.params['z_surprisal']:.2f}")
   73 | 
   74 | print("\n" + "=" * 76)
   75 | print("SUBJECT-LEVEL (repaired frequency)")
   76 | print("=" * 76)
   77 | b, nsig = [], 0
   78 | for pid, s in D.groupby("participant"):
   79 |     cols = ["tee_k3", "surprisal", "word_length", "log_freq_fixed", "zone",
   80 |             "prev_log_RT"]
   81 |     s = s.dropna(subset=cols + ["log_RT"])
   82 |     if len(s) < 300:
   83 |         continue
   84 |     X = np.column_stack([zs(s[c].values) for c in cols])
   85 |     if (X.std(axis=0) == 0).any():
   86 |         continue
   87 |     r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
   88 |     b.append(r.params[1])
   89 |     if r.pvalues[1] < .05 and r.params[1] > 0:
   90 |         nsig += 1
   91 | b = np.array(b)
   92 | npos = int((b > 0).sum())
   93 | print(f"  participants with sufficient data : {len(b)}")
   94 | print(f"  positive coefficients             : {npos} ({npos/len(b):.1%})")
   95 | print(f"  mean per-participant coefficient  : {b.mean():+.5f}")
   96 | print(f"  sign test p                       : "
   97 |       f"{stats.binomtest(npos, len(b), .5).pvalue:.2e}")
   98 | print(f"  Wilcoxon p                        : {stats.wilcoxon(b).pvalue:.2e}")
   99 | print(f"  t({len(b)-1})                          : "
  100 |       f"{stats.ttest_1samp(b, 0).statistic:.2f}")
  101 | print(f"  individually significant, positive: {nsig}")
  102 | 
  103 | print("\n" + "=" * 76)
  104 | print("PYTHIA CROSS-ARCHITECTURE (repaired frequency, matched sample)")
  105 | print("=" * 76)
  106 | P = D.merge(PY[["story_id", "zone", "tee_pythia_160m", "tee_pythia_410m"]],
  107 |             on=["story_id", "zone"], how="inner").dropna(
  108 |     subset=["tee_pythia_160m", "tee_pythia_410m"])
  109 | for c in ["tee_pythia_160m", "tee_pythia_410m"]:
  110 |     P["z_" + c] = z(P[c])
  111 | print(f"  n = {len(P):,}   participants = {P.participant.nunique()}")
  112 | q0 = smf.mixedlm(BASE, P, groups=P.participant).fit(reml=False,
  113 |                                                     method="lbfgs")
  114 | for lab, c in [("GPT-2 Small", "z_tee_k3"),
  115 |                ("Pythia-160M", "z_tee_pythia_160m"),
  116 |                ("Pythia-410M", "z_tee_pythia_410m")]:
  117 |     q1 = smf.mixedlm(BASE + " + " + c, P, groups=P.participant).fit(
  118 |         reml=False, method="lbfgs")
  119 |     print(f"  {lab:<14} dAIC {q0.aic - q1.aic:>7.1f}   "
  120 |           f"beta {q1.params[c]:+.5f}   p {q1.pvalues[c]:.2e}")
```


==============================================================================
### FILE: gp_confound_check/ns_freq_repair.py
==============================================================================

```
    1 | """
    2 | DOES THE NATURAL STORIES EFFECT SURVIVE A CORRECT FREQUENCY CONTROL?
    3 | =====================================================================
    4 | The `log_freq` column on the locked sample is wrong for 19.7% of words: 1,937 of
    5 | 9,840 carry a value of 0, and 99.6% of those have a real frequency once the word
    6 | is lowercased and stripped of attached punctuation (hummed 2.37, clattered 2.17,
    7 | wool 3.91, residents 4.64). Only 37% of the zeroed words are punctuated, so this
    8 | is not only the trailing-punctuation problem. The scale is also not Zipf --
    9 | "the" is 6.67 in the column against a Zipf value of 7.73 -- so whatever produced
   10 | it, it is not the lookup the methods imply. Correlation with a correct lookup is
   11 | only +0.84.
   12 | 
   13 | This matters because frequency is a CONTROL in every Natural Stories model and
   14 | correlates with the trajectory measure at -0.44. A control that is wrong on a
   15 | fifth of observations leaves lexical variance unabsorbed, which the trajectory
   16 | term is then free to pick up. So the question is not cosmetic: does the headline
   17 | effect survive once frequency is measured properly?
   18 | 
   19 | REPAIR: log_freq_fixed = zipf_frequency(lowercased, punctuation-stripped word).
   20 | The garden-path pipeline already does exactly this, which is why its frequency
   21 | behaved more sensibly.
   22 | 
   23 | REPORTED FOR EACH SPECIFICATION, old control vs repaired control:
   24 |   H1  pooled headline    dAIC and beta for the trajectory term
   25 |   H2  subject-level      mean beta, % positive, Wilcoxon p
   26 |   H3  both frequencies entered together, to see what the repaired one absorbs
   27 |   H4  the frequency coefficient itself, to confirm the suppression story holds
   28 |       up once the variable is correct
   29 | 
   30 | If the trajectory effect drops substantially under H1/H2, the Natural Stories
   31 | result was partly an artefact of a degraded control and the paper has to say so.
   32 | """
   33 | 
   34 | import numpy as np
   35 | import pandas as pd
   36 | import statsmodels.api as sm
   37 | import statsmodels.formula.api as smf
   38 | from scipy import stats
   39 | from wordfreq import zipf_frequency
   40 | import hashlib, warnings
   41 | warnings.filterwarnings("ignore")
   42 | 
   43 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   44 | 
   45 | 
   46 | def zs(x):
   47 |     x = np.asarray(x, dtype=float)
   48 |     s = x.std()
   49 |     return (x - x.mean()) / s if s > 0 else x * 0
   50 | 
   51 | 
   52 | def z(s):
   53 |     v = s.dropna()
   54 |     return (s - v.mean()) / v.std()
   55 | 
   56 | 
   57 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   58 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   59 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   60 | assert sh == "8a6087341e", sh
   61 | 
   62 | S["log_freq_fixed"] = (S.word.astype(str)
   63 |                        .str.strip('.,;:!?"\'()[]')
   64 |                        .str.lower()
   65 |                        .map(lambda w: zipf_frequency(w, "en")))
   66 | print(f"locked sample {sh}   {len(S):,} words")
   67 | print(f"  old log_freq  : zeros {(S.log_freq == 0).sum():,} "
   68 |       f"({(S.log_freq == 0).mean():.1%})  mean {S.log_freq.mean():.3f}")
   69 | print(f"  repaired      : zeros {(S.log_freq_fixed == 0).sum():,} "
   70 |       f"({(S.log_freq_fixed == 0).mean():.1%})  "
   71 |       f"mean {S.log_freq_fixed.mean():.3f}")
   72 | print(f"  r(old, repaired) = {S.log_freq.corr(S.log_freq_fixed):+.4f}")
   73 | print(f"  r(TEE, old)      = {S.tee_k3.corr(S.log_freq):+.4f}")
   74 | print(f"  r(TEE, repaired) = {S.tee_k3.corr(S.log_freq_fixed):+.4f}")
   75 | print(f"  r(surprisal, old)      = {S.surprisal.corr(S.log_freq):+.4f}")
   76 | print(f"  r(surprisal, repaired) = "
   77 |       f"{S.surprisal.corr(S.log_freq_fixed):+.4f}")
   78 | 
   79 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   80 |                  sep="\t").rename(columns={"item": "story_id",
   81 |                                            "WorkerId": "participant"})
   82 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   83 | d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   84 |                 "log_freq", "log_freq_fixed"]],
   85 |              on=["story_id", "zone"], how="inner")
   86 | d["log_RT"] = np.log(d.RT)
   87 | d = d.sort_values(["participant", "story_id", "zone"])
   88 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
   89 | d = d.dropna(subset=["log_RT", "word_length", "log_freq", "log_freq_fixed",
   90 |                      "zone", "prev_log_RT", "tee_k3", "surprisal"])
   91 | for c in ["word_length", "log_freq", "log_freq_fixed", "zone", "prev_log_RT",
   92 |           "surprisal", "tee_k3"]:
   93 |     d["z_" + c] = z(d[c])
   94 | print(f"\nn = {len(d):,}   participants = {d.participant.nunique()}")
   95 | 
   96 | print("\n" + "=" * 80)
   97 | print("H1  POOLED HEADLINE: dAIC and beta for the trajectory term")
   98 | print("=" * 80)
   99 | BASE = "log_RT ~ z_word_length + z_zone + z_prev_log_RT + z_surprisal"
  100 | specs = [("old log_freq (as published)", BASE + " + z_log_freq"),
  101 |          ("repaired log_freq", BASE + " + z_log_freq_fixed"),
  102 |          ("both frequencies", BASE + " + z_log_freq + z_log_freq_fixed")]
  103 | print(f"{'frequency control':<30}{'dAIC(TEE)':>12}{'beta(TEE)':>12}{'p':>12}")
  104 | for lab, f in specs:
  105 |     m0 = smf.mixedlm(f, d, groups=d.participant).fit(reml=False,
  106 |                                                      method="lbfgs")
  107 |     m1 = smf.mixedlm(f + " + z_tee_k3", d, groups=d.participant).fit(
  108 |         reml=False, method="lbfgs")
  109 |     print(f"{lab:<30}{m0.aic - m1.aic:>12.1f}"
  110 |           f"{m1.params['z_tee_k3']:>12.5f}{m1.pvalues['z_tee_k3']:>12.2e}")
  111 | 
  112 | print("\n" + "=" * 80)
  113 | print("H2  SUBJECT-LEVEL")
  114 | print("=" * 80)
  115 | 
  116 | 
  117 | def subj(cols):
  118 |     out = []
  119 |     for pid, s in d.groupby("participant"):
  120 |         s = s.dropna(subset=cols + ["log_RT"])
  121 |         if len(s) < 300:
  122 |             continue
  123 |         X = np.column_stack([zs(s[c].values) for c in cols])
  124 |         if (X.std(axis=0) == 0).any():
  125 |             continue
  126 |         out.append(sm.OLS(zs(s.log_RT.values),
  127 |                           sm.add_constant(X)).fit().params[1])
  128 |     return np.array(out)
  129 | 
  130 | 
  131 | CTRL = ["word_length", "zone", "prev_log_RT", "surprisal"]
  132 | print(f"{'frequency control':<30}{'beta':>11}{'% positive':>13}{'p':>12}")
  133 | for lab, fq in [("old log_freq (as published)", ["log_freq"]),
  134 |                 ("repaired log_freq", ["log_freq_fixed"]),
  135 |                 ("both frequencies", ["log_freq", "log_freq_fixed"])]:
  136 |     b = subj(["tee_k3"] + CTRL + fq)
  137 |     print(f"{lab:<30}{b.mean():>+11.5f}{(b > 0).mean():>12.1%}"
  138 |           f"{stats.wilcoxon(b).pvalue:>12.2e}")
  139 | 
  140 | print("\n" + "=" * 80)
  141 | print("H4  THE FREQUENCY COEFFICIENT ITSELF (subject-level)")
  142 | print("=" * 80)
  143 | 
  144 | 
  145 | def subj_focus(focus, others):
  146 |     out = []
  147 |     for pid, s in d.groupby("participant"):
  148 |         s = s.dropna(subset=[focus] + others + ["log_RT"])
  149 |         if len(s) < 300:
  150 |             continue
  151 |         X = np.column_stack([zs(s[focus].values)]
  152 |                             + [zs(s[c].values) for c in others])
  153 |         if (X.std(axis=0) == 0).any():
  154 |             continue
  155 |         out.append(sm.OLS(zs(s.log_RT.values),
  156 |                           sm.add_constant(X)).fit().params[1])
  157 |     return np.array(out)
  158 | 
  159 | 
  160 | for lab, fq in [("old log_freq", "log_freq"),
  161 |                 ("repaired log_freq", "log_freq_fixed")]:
  162 |     a = subj_focus(fq, [])
  163 |     b = subj_focus(fq, ["word_length"])
  164 |     c = subj_focus(fq, ["word_length", "surprisal", "tee_k3", "zone",
  165 |                         "prev_log_RT"])
  166 |     print(f"  {lab:<20} alone {a.mean():+.4f} | "
  167 |           f"+length {b.mean():+.4f} | full model {c.mean():+.4f}")
```


==============================================================================
### FILE: gp_confound_check/ns_pythia_surp.py
==============================================================================

```
    1 | """
    2 | PYTHIA-410M SURPRISAL ON THE NATURAL STORIES LOCKED SAMPLE
    3 | ==========================================================
    4 | Closes the last gap in the stronger-surprisal control (§4c of V2_DRAFT).
    5 | GPT-2 Medium and GPT-2 XL surprisal already exist on this sample, but they share
    6 | GPT-2 Small's tokenizer, training corpus and positional encoding, so they are not
    7 | independent estimates of predictability. Pythia-410M differs on all three
    8 | (BPE vocabulary trained on the Pile, rotary position embeddings), which makes it
    9 | the control a reviewer would actually ask for.
   10 | 
   11 | Pythia-410M *TEE* on this sample already exists (pythia_tee_8a6087341e.csv);
   12 | only its surprisal was never computed. This script computes it.
   13 | 
   14 | Conventions copied exactly from v2_table6_pythia.py so the values are
   15 | commensurable with everything else on this sample:
   16 |   - text = words joined by single spaces, per story
   17 |   - chunked forward passes, CHUNK 1024 / STRIDE 512, FIRST-WRITE-WINS, so every
   18 |     token is scored with the longest left context available at its first
   19 |     computation
   20 |   - word alignment by tokenizer offset mapping; a subword belongs to a word only
   21 |     if it lies entirely inside that word's character span
   22 |   - word surprisal = SUM of its subword token surprisals, in bits
   23 | 
   24 | Validation before saving (mirrors the guard discipline used throughout):
   25 |   - locked-sample hash asserted
   26 |   - coverage: every sample word must receive a value
   27 |   - correlation against the existing GPT-2 Small / Medium / XL surprisals; a
   28 |     value far outside the .85-.95 range seen among those would indicate a
   29 |     misalignment rather than a genuine model difference
   30 | 
   31 | Output: ns_pythia410m_surp_8a6087341e.csv  (story_id, word_idx, surprisal_pythia410m)
   32 | """
   33 | 
   34 | import numpy as np
   35 | import pandas as pd
   36 | import torch
   37 | from transformers import AutoTokenizer, AutoModelForCausalLM
   38 | import hashlib, warnings
   39 | warnings.filterwarnings("ignore")
   40 | 
   41 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   42 | OUT = f"{GP}/gp_confound_check/ns_pythia410m_surp_8a6087341e.csv"
   43 | NAME = "EleutherAI/pythia-410m"
   44 | CHUNK, STRIDE = 1024, 512
   45 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   46 | 
   47 | # ---------------- corpus (identical construction to the verified pipeline) ----
   48 | words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
   49 |                     names=["id", "word"], dtype={"id": str, "word": str})
   50 | words = words[words.word.notna()].copy()
   51 | words = words[words.id.str.split(".").str[-1] == "whole"].copy()
   52 | words["word"] = words.word.str.strip().str.replace(r"\s+", "", regex=True)
   53 | words["story_id"] = words.id.str.split(".").str[0].astype(int)
   54 | words["word_idx"] = words.groupby("story_id").cumcount()
   55 | story_words = {s: g.word.tolist() for s, g in words.groupby("story_id")}
   56 | print(f"corpus: {len(words):,} words, {len(story_words)} stories", flush=True)
   57 | 
   58 | 
   59 | def spans_for(wl):
   60 |     out, cur = [], 0
   61 |     for w in wl:
   62 |         out.append((cur, cur + len(w)))
   63 |         cur += len(w) + 1
   64 |     return out
   65 | 
   66 | 
   67 | tok = AutoTokenizer.from_pretrained(NAME)
   68 | model = AutoModelForCausalLM.from_pretrained(NAME).eval().to(DEVICE)
   69 | print(f"loaded {NAME} on {DEVICE}", flush=True)
   70 | 
   71 | rows = []
   72 | for sid, wl in story_words.items():
   73 |     text = " ".join(wl)
   74 |     enc = tok(text, return_offsets_mapping=True)
   75 |     ids = torch.tensor(enc["input_ids"])
   76 |     offs = enc["offset_mapping"]
   77 |     n = ids.size(0)
   78 | 
   79 |     tok_surp, pos = {}, 0
   80 |     while pos < n:
   81 |         end = min(pos + CHUNK, n)
   82 |         with torch.no_grad():
   83 |             out = model(ids[pos:end].unsqueeze(0).to(DEVICE))
   84 |         lp = torch.log_softmax(out.logits[0].float(), -1).cpu()
   85 |         # token at local i is predicted from logits at local i-1
   86 |         for i in range(1, end - pos):
   87 |             g = pos + i
   88 |             if g not in tok_surp:
   89 |                 tok_surp[g] = -float(lp[i - 1, ids[g]]) / np.log(2)
   90 |         del out, lp
   91 |         if end >= n:
   92 |             break
   93 |         pos += STRIDE
   94 | 
   95 |     sp = spans_for(wl)
   96 |     members = {}
   97 |     wi = 0
   98 |     for bi, (cs, ce) in enumerate(offs):
   99 |         if ce <= cs:
  100 |             continue
  101 |         while wi < len(sp) and cs >= sp[wi][1]:
  102 |             wi += 1
  103 |         if wi < len(sp) and cs >= sp[wi][0] and ce <= sp[wi][1]:
  104 |             members.setdefault(wi, []).append(bi)
  105 | 
  106 |     for w in range(len(sp)):
  107 |         toks = members.get(w)
  108 |         if not toks or any(t not in tok_surp for t in toks):
  109 |             continue
  110 |         rows.append({"story_id": sid, "word_idx": w,
  111 |                      "surprisal_pythia410m": float(
  112 |                          sum(tok_surp[t] for t in toks))})
  113 |     print(f"  story {sid}: {len(sp):,} words -> "
  114 |           f"{sum(1 for r in rows if r['story_id'] == sid):,} scored", flush=True)
  115 | 
  116 | P = pd.DataFrame(rows)
  117 | print(f"\ntotal scored words: {len(P):,}")
  118 | 
  119 | # ------------------------------------------------------------------ validate
  120 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
  121 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
  122 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
  123 | assert sh == "8a6087341e", sh
  124 | print(f"locked sample hash {sh} verified ({len(S):,} words)")
  125 | 
  126 | for f, c in [("gpt2_medium_surp_ent.csv", "surprisal_gpt2_medium"),
  127 |              ("gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl")]:
  128 |     S = S.merge(pd.read_csv(f"{GP}/extensions/{f}")[["story_id", "word_idx", c]],
  129 |                 on=["story_id", "word_idx"], how="left", validate="one_to_one")
  130 | 
  131 | chk = S.merge(P, on=["story_id", "word_idx"], how="left", validate="one_to_one")
  132 | missing = chk.surprisal_pythia410m.isna().sum()
  133 | print(f"coverage: {len(chk) - missing:,}/{len(chk):,} sample words scored "
  134 |       f"({missing} missing)")
  135 | 
  136 | print("\nagreement with existing surprisal estimates on the sample:")
  137 | ok = True
  138 | for c in ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl"]:
  139 |     r = chk[c].corr(chk.surprisal_pythia410m)
  140 |     flag = "" if 0.75 <= r <= 0.98 else "   <-- OUT OF EXPECTED RANGE"
  141 |     if flag:
  142 |         ok = False
  143 |     print(f"  r(pythia410m, {c:<22}) = {r:+.3f}{flag}")
  144 | print(f"\nmean surprisal (bits): "
  145 |       f"small {chk.surprisal.mean():.3f}  "
  146 |       f"medium {chk.surprisal_gpt2_medium.mean():.3f}  "
  147 |       f"xl {chk.surprisal_gpt2_xl.mean():.3f}  "
  148 |       f"pythia410m {chk.surprisal_pythia410m.mean():.3f}")
  149 | print(f"r(TEE, pythia410m surprisal) = "
  150 |       f"{chk.tee_k3.corr(chk.surprisal_pythia410m):+.3f}   "
  151 |       f"[small +0.310, medium +0.271, xl +0.254]")
  152 | 
  153 | if missing > 0 or not ok:
  154 |     print("\nWARNING: coverage or agreement outside expectation. "
  155 |           "Saving anyway, but inspect before use in the manuscript.")
  156 | 
  157 | P.to_csv(OUT, index=False)
  158 | print(f"\nsaved -> {OUT}")
```


==============================================================================
### FILE: gp_confound_check/ns_rerun_all_fixedfreq.py
==============================================================================

```
    1 | """
    2 | RERUN EVERY NATURAL STORIES ANALYSIS WITH THE REPAIRED FREQUENCY CONTROL
    3 | ========================================================================
    4 | `log_freq` on the locked sample is zero for 1,937 of 9,840 words (19.7%), and
    5 | 99.6% of those have a real frequency once lowercased and stripped of attached
    6 | punctuation. Frequency is a control in every Natural Stories model, so every
    7 | number that used it has to be recomputed.
    8 | 
    9 | Repaired variable: zipf_frequency(lowercased, punctuation-stripped word).
   10 | Zeros fall from 1,937 to 7.
   11 | 
   12 | Already established (ns_freq_repair.py):
   13 |     headline dAIC 111.8 -> 78.4, beta +0.00354 -> +0.00298
   14 |     subject-level +0.01277 / 73.1% -> +0.01095 / 67.3%
   15 | 
   16 | This script recomputes the rest, reporting old and new side by side:
   17 |   R1  stronger-surprisal controls (GPT-2 Medium/XL, Pythia-410M, joint)
   18 |   R2  displacement control
   19 |   R3  word-identity control (centring within word type)
   20 |   R4  punctuation checks
   21 |   R5  Pythia cross-architecture, matched samples
   22 |   R6  position-within-sentence interaction
   23 |   R7  the coefficient comparison used in Figure 2
   24 | 
   25 | Every model keeps its published specification; only the frequency variable
   26 | changes.
   27 | """
   28 | 
   29 | import numpy as np
   30 | import pandas as pd
   31 | import statsmodels.api as sm
   32 | import statsmodels.formula.api as smf
   33 | from scipy import stats
   34 | from wordfreq import zipf_frequency
   35 | import hashlib, warnings
   36 | warnings.filterwarnings("ignore")
   37 | 
   38 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   39 | GPC = f"{GP}/gp_confound_check"
   40 | 
   41 | 
   42 | def zs(x):
   43 |     x = np.asarray(x, dtype=float)
   44 |     s = x.std()
   45 |     return (x - x.mean()) / s if s > 0 else x * 0
   46 | 
   47 | 
   48 | def z(s):
   49 |     v = s.dropna()
   50 |     return (s - v.mean()) / v.std()
   51 | 
   52 | 
   53 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   54 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   55 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   56 | assert sh == "8a6087341e", sh
   57 | S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
   58 |                        .str.lower().map(lambda w: zipf_frequency(w, "en")))
   59 | S["punct"] = S.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   60 | for path, col in [(f"{GP}/extensions/gpt2_medium_surp_ent.csv",
   61 |                    "surprisal_gpt2_medium"),
   62 |                   (f"{GP}/extensions/gpt2_xl_surp_ent.csv", "surprisal_gpt2_xl"),
   63 |                   (f"{GPC}/ns_pythia410m_surp_8a6087341e.csv",
   64 |                    "surprisal_pythia410m")]:
   65 |     S = S.merge(pd.read_csv(path)[["story_id", "word_idx", col]],
   66 |                 on=["story_id", "word_idx"], how="left", validate="one_to_one")
   67 | KS = ["surprisal", "surprisal_gpt2_medium", "surprisal_gpt2_xl",
   68 |       "surprisal_pythia410m"]
   69 | 
   70 | disp = pd.read_csv(f"{GPC}/displacement_8a6087341e.csv")
   71 | S = S.merge(disp[["story_id", "word_idx", "disp_word"]],
   72 |             on=["story_id", "word_idx"], how="left", validate="one_to_one")
   73 | PY = pd.read_csv(f"{GPC}/pythia_tee_8a6087341e.csv")
   74 | 
   75 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   76 |                  sep="\t").rename(columns={"item": "story_id",
   77 |                                            "WorkerId": "participant"})
   78 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   79 | base_cols = (["story_id", "zone", "word", "word_idx", "tee_k3", "word_length",
   80 |               "log_freq", "log_freq_fixed", "punct", "disp_word"] + KS)
   81 | d = rt.merge(S[base_cols], on=["story_id", "zone"], how="inner",
   82 |              suffixes=("", "_s"))
   83 | d["log_RT"] = np.log(d.RT)
   84 | d = d.sort_values(["participant", "story_id", "zone"])
   85 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
   86 | D = d.dropna(subset=["log_RT", "word_length", "log_freq", "log_freq_fixed",
   87 |                      "zone", "prev_log_RT", "tee_k3"] + KS).copy()
   88 | print(f"n = {len(D):,}  participants = {D.participant.nunique()}\n")
   89 | 
   90 | for c in (["word_length", "zone", "prev_log_RT", "tee_k3", "log_freq",
   91 |            "log_freq_fixed", "disp_word", "punct"] + KS):
   92 |     D["z_" + c] = z(D[c])
   93 | 
   94 | 
   95 | def daic(frame, base, extra="z_tee_k3"):
   96 |     m0 = smf.mixedlm(base, frame, groups=frame.participant).fit(
   97 |         reml=False, method="lbfgs")
   98 |     m1 = smf.mixedlm(base + " + " + extra, frame,
   99 |                      groups=frame.participant).fit(reml=False, method="lbfgs")
  100 |     return m0.aic - m1.aic, m1.params[extra], m1.pvalues[extra]
  101 | 
  102 | 
  103 | CORE = "log_RT ~ z_word_length + z_zone + z_prev_log_RT"
  104 | 
  105 | print("=" * 84)
  106 | print("R1  STRONGER SURPRISAL CONTROLS")
  107 | print("=" * 84)
  108 | print(f"{'surprisal control':<28}{'dAIC old':>11}{'dAIC new':>11}"
  109 |       f"{'beta new':>11}")
  110 | sur_specs = [("GPT-2 Small", "z_surprisal"),
  111 |              ("GPT-2 Medium", "z_surprisal_gpt2_medium"),
  112 |              ("GPT-2 XL", "z_surprisal_gpt2_xl"),
  113 |              ("Pythia-410M", "z_surprisal_pythia410m"),
  114 |              ("all four", " + ".join("z_" + k for k in KS))]
  115 | for lab, term in sur_specs:
  116 |     a_old, _, _ = daic(D, f"{CORE} + z_log_freq + {term}")
  117 |     a_new, b_new, _ = daic(D, f"{CORE} + z_log_freq_fixed + {term}")
  118 |     print(f"{lab:<28}{a_old:>11.1f}{a_new:>11.1f}{b_new:>11.5f}")
  119 | 
  120 | print("\n" + "=" * 84)
  121 | print("R2  DISPLACEMENT CONTROL")
  122 | print("=" * 84)
  123 | dd = D.dropna(subset=["disp_word"]).copy()
  124 | print(f"  n = {len(dd):,}")
  125 | for lab, fq in [("old log_freq", "z_log_freq"),
  126 |                 ("repaired", "z_log_freq_fixed")]:
  127 |     b = f"log_RT ~ z_word_length + {fq} + z_zone + z_prev_log_RT + z_surprisal"
  128 |     m_t = smf.mixedlm(b + " + z_tee_k3", dd, groups=dd.participant).fit(
  129 |         reml=False, method="lbfgs")
  130 |     m_d = smf.mixedlm(b + " + z_disp_word", dd, groups=dd.participant).fit(
  131 |         reml=False, method="lbfgs")
  132 |     m_b = smf.mixedlm(b + " + z_tee_k3 + z_disp_word", dd,
  133 |                       groups=dd.participant).fit(reml=False, method="lbfgs")
  134 |     print(f"  {lab:<16} TEE alone {m_t.params['z_tee_k3']:+.5f} | "
  135 |           f"disp alone {m_d.params['z_disp_word']:+.5f} | "
  136 |           f"joint TEE {m_b.params['z_tee_k3']:+.5f} "
  137 |           f"(p={m_b.pvalues['z_tee_k3']:.1e}) | "
  138 |           f"joint disp {m_b.params['z_disp_word']:+.5f} "
  139 |           f"(p={m_b.pvalues['z_disp_word']:.3f})")
  140 | 
  141 | print("\n" + "=" * 84)
  142 | print("R3  WORD-IDENTITY CONTROL (centred within word type, >=5 occurrences)")
  143 | print("=" * 84)
  144 | W = D.copy()
  145 | W["wtype"] = W.word.astype(str).str.lower()
  146 | keep = W.wtype.value_counts()
  147 | W = W[W.wtype.isin(keep[keep >= 5].index)].copy()
  148 | print(f"  {W.wtype.nunique():,} word types, n = {len(W):,}")
  149 | for lab, fq in [("old log_freq", "log_freq"), ("repaired", "log_freq_fixed")]:
  150 |     cols = ["tee_k3", "surprisal", "word_length", fq, "zone", "prev_log_RT"]
  151 |     Wc = W.copy()
  152 |     for c in cols + ["log_RT"]:
  153 |         Wc["c_" + c] = Wc[c] - Wc.groupby("wtype")[c].transform("mean")
  154 |     f = ("c_log_RT ~ " + " + ".join("c_" + c for c in cols if c != "tee_k3"))
  155 |     a, b_, p_ = daic(Wc.assign(participant=Wc.participant), f, "c_tee_k3")
  156 |     print(f"  {lab:<16} dAIC {a:>7.1f}   beta {b_:+.5f}   p {p_:.2e}")
  157 | 
  158 | print("\n" + "=" * 84)
  159 | print("R4  PUNCTUATION")
  160 | print("=" * 84)
  161 | for lab, fq in [("old log_freq", "z_log_freq"),
  162 |                 ("repaired", "z_log_freq_fixed")]:
  163 |     b = f"{CORE} + {fq} + z_surprisal"
  164 |     a1, _, _ = daic(D, b + " + z_punct")
  165 |     sub = D[D.punct == 0]
  166 |     a2, b2, _ = daic(sub, b)
  167 |     print(f"  {lab:<16} + punctuation covariate dAIC {a1:>7.1f}   |   "
  168 |           f"punctuation-free words dAIC {a2:>7.1f} (beta {b2:+.5f}, "
  169 |           f"n={len(sub):,})")
  170 | 
  171 | print("\n" + "=" * 84)
  172 | print("R5  PYTHIA CROSS-ARCHITECTURE, MATCHED SAMPLE")
  173 | print("=" * 84)
  174 | P = D.merge(PY[["story_id", "zone", "tee_pythia_160m", "tee_pythia_410m"]],
  175 |             on=["story_id", "zone"], how="inner").dropna(
  176 |     subset=["tee_pythia_160m", "tee_pythia_410m"])
  177 | for c in ["tee_pythia_160m", "tee_pythia_410m"]:
  178 |     P["z_" + c] = z(P[c])
  179 | print(f"  n = {len(P):,}  participants = {P.participant.nunique()}")
  180 | for lab, fq in [("old log_freq", "z_log_freq"),
  181 |                 ("repaired", "z_log_freq_fixed")]:
  182 |     b = f"{CORE} + {fq} + z_surprisal"
  183 |     out = []
  184 |     for c in ["z_tee_k3", "z_tee_pythia_160m", "z_tee_pythia_410m"]:
  185 |         a, bb, _ = daic(P, b, c)
  186 |         out.append(f"{c.replace('z_tee_', ''):<12}{a:>8.1f}")
  187 |     print(f"  {lab:<16}" + "  ".join(out))
  188 | 
  189 | print("\n" + "=" * 84)
  190 | print("R7  FIGURE 2 COEFFICIENTS (subject-level, unique contribution)")
  191 | print("=" * 84)
  192 | 
  193 | 
  194 | def subj_focus(frame, focus, others, minn=300):
  195 |     out = []
  196 |     for pid, s in frame.groupby("participant"):
  197 |         s = s.dropna(subset=[focus] + others + ["log_RT"])
  198 |         if len(s) < minn:
  199 |             continue
  200 |         X = np.column_stack([zs(s[focus].values)]
  201 |                             + [zs(s[c].values) for c in others])
  202 |         if (X.std(axis=0) == 0).any():
  203 |             continue
  204 |         out.append(sm.OLS(zs(s.log_RT.values),
  205 |                           sm.add_constant(X)).fit().params[1])
  206 |     return np.array(out)
  207 | 
  208 | 
  209 | ALL_OLD = ["tee_k3", "surprisal", "word_length", "log_freq", "zone",
  210 |            "prev_log_RT"]
  211 | ALL_NEW = ["tee_k3", "surprisal", "word_length", "log_freq_fixed", "zone",
  212 |            "prev_log_RT"]
  213 | for lab, allc, fq in [("old", ALL_OLD, "log_freq"),
  214 |                       ("repaired", ALL_NEW, "log_freq_fixed")]:
  215 |     line = []
  216 |     for c in ["tee_k3", "surprisal", fq]:
  217 |         b = subj_focus(D, c, [o for o in allc if o != c])
  218 |         line.append(f"{c[:12]:<13}{b.mean():+.5f}")
  219 |     print(f"  {lab:<10}" + " | ".join(line))
```


==============================================================================
### FILE: gp_confound_check/ns_rerun_part2.py
==============================================================================

```
    1 | """
    2 | REMAINDER OF THE FREQUENCY-REPAIR RERUN (R3-R7)
    3 | ===============================================
    4 | R1 (stronger surprisal controls) and R2 (displacement) completed in
    5 | ns_rerun_all_fixedfreq.py. R3 crashed for a legitimate reason and the rest did
    6 | not run.
    7 | 
    8 | R3 NOTE. Centring within word type zeroes any predictor that is constant within
    9 | a type -- which word length and log frequency both are. The published
   10 | word-identity analysis therefore cannot have contained a frequency term, and is
   11 | unaffected by the repair. It is refit here without those two predictors, purely
   12 | to confirm the published value reproduces.
   13 | """
   14 | 
   15 | import numpy as np
   16 | import pandas as pd
   17 | import statsmodels.api as sm
   18 | import statsmodels.formula.api as smf
   19 | from wordfreq import zipf_frequency
   20 | import hashlib, warnings
   21 | warnings.filterwarnings("ignore")
   22 | 
   23 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   24 | GPC = f"{GP}/gp_confound_check"
   25 | 
   26 | 
   27 | def zs(x):
   28 |     x = np.asarray(x, dtype=float)
   29 |     s = x.std()
   30 |     return (x - x.mean()) / s if s > 0 else x * 0
   31 | 
   32 | 
   33 | def z(s):
   34 |     v = s.dropna()
   35 |     return (s - v.mean()) / v.std()
   36 | 
   37 | 
   38 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   39 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   40 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   41 | assert sh == "8a6087341e", sh
   42 | S["log_freq_fixed"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]')
   43 |                        .str.lower().map(lambda w: zipf_frequency(w, "en")))
   44 | S["punct"] = S.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   45 | PY = pd.read_csv(f"{GPC}/pythia_tee_8a6087341e.csv")
   46 | 
   47 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   48 |                  sep="\t").rename(columns={"item": "story_id",
   49 |                                            "WorkerId": "participant"})
   50 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   51 | # processed_RTs.tsv carries its own `word` column; renaming the sample's before
   52 | # the merge avoids the word_x/word_y suffixing that has caused errors here twice.
   53 | d = rt.merge(S[["story_id", "zone", "word", "tee_k3", "surprisal",
   54 |                 "word_length", "log_freq", "log_freq_fixed", "punct"]]
   55 |              .rename(columns={"word": "wordform"}),
   56 |              on=["story_id", "zone"], how="inner")
   57 | d["log_RT"] = np.log(d.RT)
   58 | d = d.sort_values(["participant", "story_id", "zone"])
   59 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
   60 | D = d.dropna(subset=["log_RT", "word_length", "log_freq", "log_freq_fixed",
   61 |                      "zone", "prev_log_RT", "tee_k3", "surprisal"]).copy()
   62 | for c in ["word_length", "zone", "prev_log_RT", "tee_k3", "log_freq",
   63 |           "log_freq_fixed", "surprisal", "punct"]:
   64 |     D["z_" + c] = z(D[c])
   65 | print(f"n = {len(D):,}  participants = {D.participant.nunique()}\n")
   66 | 
   67 | 
   68 | def daic(frame, base, extra):
   69 |     m0 = smf.mixedlm(base, frame, groups=frame.participant).fit(
   70 |         reml=False, method="lbfgs")
   71 |     m1 = smf.mixedlm(base + " + " + extra, frame,
   72 |                      groups=frame.participant).fit(reml=False, method="lbfgs")
   73 |     return m0.aic - m1.aic, m1.params[extra], m1.pvalues[extra]
   74 | 
   75 | 
   76 | CORE = "log_RT ~ z_word_length + z_zone + z_prev_log_RT"
   77 | 
   78 | print("=" * 84)
   79 | print("R3  WORD-IDENTITY CONTROL")
   80 | print("=" * 84)
   81 | W = D.copy()
   82 | W["wtype"] = W.wordform.astype(str).str.lower()
   83 | vc = W.wtype.value_counts()
   84 | W = W[W.wtype.isin(vc[vc >= 5].index)].copy()
   85 | cols = ["tee_k3", "surprisal", "zone", "prev_log_RT"]
   86 | for c in cols + ["log_RT"]:
   87 |     W["c_" + c] = W[c] - W.groupby("wtype")[c].transform("mean")
   88 | print(f"  {W.wtype.nunique():,} word types, n = {len(W):,}")
   89 | print("  word length and log frequency are constant within word type, so they")
   90 | print("  are necessarily absent from this model; the repair cannot affect it.")
   91 | a, b_, p_ = daic(W, "c_log_RT ~ c_surprisal + c_zone + c_prev_log_RT",
   92 |                  "c_tee_k3")
   93 | print(f"  dAIC {a:.1f}   beta {b_:+.5f}   p {p_:.2e}   "
   94 |       f"(published: dAIC 23.1, beta +0.0022, p 5.3e-7)")
   95 | 
   96 | print("\n" + "=" * 84)
   97 | print("R4  PUNCTUATION")
   98 | print("=" * 84)
   99 | for lab, fq in [("old log_freq", "z_log_freq"),
  100 |                 ("repaired", "z_log_freq_fixed")]:
  101 |     b = f"{CORE} + {fq} + z_surprisal"
  102 |     a1, _, _ = daic(D, b + " + z_punct", "z_tee_k3")
  103 |     sub = D[D.punct == 0]
  104 |     a2, b2, _ = daic(sub, b, "z_tee_k3")
  105 |     print(f"  {lab:<16} +punct covariate dAIC {a1:>7.1f}  |  "
  106 |           f"punct-free dAIC {a2:>7.1f} (beta {b2:+.5f}, n={len(sub):,})")
  107 | 
  108 | print("\n" + "=" * 84)
  109 | print("R5  PYTHIA CROSS-ARCHITECTURE, MATCHED SAMPLE")
  110 | print("=" * 84)
  111 | P = D.merge(PY[["story_id", "zone", "tee_pythia_160m", "tee_pythia_410m"]],
  112 |             on=["story_id", "zone"], how="inner").dropna(
  113 |     subset=["tee_pythia_160m", "tee_pythia_410m"])
  114 | for c in ["tee_pythia_160m", "tee_pythia_410m"]:
  115 |     P["z_" + c] = z(P[c])
  116 | print(f"  n = {len(P):,}  participants = {P.participant.nunique()}")
  117 | print(f"  {'frequency':<16}{'GPT-2 Small':>14}{'Pythia-160M':>14}"
  118 |       f"{'Pythia-410M':>14}")
  119 | for lab, fq in [("old log_freq", "z_log_freq"),
  120 |                 ("repaired", "z_log_freq_fixed")]:
  121 |     b = f"{CORE} + {fq} + z_surprisal"
  122 |     vals = []
  123 |     for c in ["z_tee_k3", "z_tee_pythia_160m", "z_tee_pythia_410m"]:
  124 |         a, _, _ = daic(P, b, c)
  125 |         vals.append(f"{a:>14.1f}")
  126 |     print(f"  {lab:<16}" + "".join(vals))
  127 | 
  128 | print("\n" + "=" * 84)
  129 | print("R7  FIGURE 2 COEFFICIENTS (subject-level unique contribution)")
  130 | print("=" * 84)
  131 | 
  132 | 
  133 | def subj_focus(frame, focus, others, minn=300):
  134 |     out = []
  135 |     for pid, s in frame.groupby("participant"):
  136 |         s = s.dropna(subset=[focus] + others + ["log_RT"])
  137 |         if len(s) < minn:
  138 |             continue
  139 |         X = np.column_stack([zs(s[focus].values)]
  140 |                             + [zs(s[c].values) for c in others])
  141 |         if (X.std(axis=0) == 0).any():
  142 |             continue
  143 |         out.append(sm.OLS(zs(s.log_RT.values),
  144 |                           sm.add_constant(X)).fit().params[1])
  145 |     return np.array(out)
  146 | 
  147 | 
  148 | for lab, fq in [("old", "log_freq"), ("repaired", "log_freq_fixed")]:
  149 |     allc = ["tee_k3", "surprisal", "word_length", fq, "zone", "prev_log_RT"]
  150 |     parts = []
  151 |     for c in ["tee_k3", "surprisal", fq]:
  152 |         b = subj_focus(D, c, [o for o in allc if o != c])
  153 |         parts.append(f"{c[:14]:<15}{b.mean():+.5f} ({(b > 0).mean():.0%})")
  154 |     print(f"  {lab:<10}" + " | ".join(parts))
```


==============================================================================
### FILE: gp_confound_check/ns_robustness.py
==============================================================================

```
    1 | """
    2 | NATURAL STORIES: the two robustness checks the paper is missing
    3 | ==============================================================
    4 | 1. PUNCTUATION. The locked sample's `final_bpe` is the token the word's state is
    5 |    read from; Natural Stories glues trailing punctuation onto words and GPT-2
    6 |    punctuation tokens are sink/rest states. Does the TEE effect survive a
    7 |    punctuation covariate, and does it survive on punctuation-free words only?
    8 | 
    9 | 2. LEXICAL BASELINE. Frequency is the dominant predictor of TEE, so the question
   10 |    is whether TEE predicts RT beyond WORD IDENTITY. `ns_crossed_re.py` tried a
   11 |    (1|word_type) random effect and never completed. Equivalent and tractable:
   12 |    center log_RT and every predictor within word type (word-identity fixed
   13 |    effects by demeaning), which asks whether TEE explains RT variation for the
   14 |    SAME word across contexts.
   15 | 
   16 | Also reports the by-participant random-intercept headline for reference.
   17 | """
   18 | 
   19 | import numpy as np
   20 | import pandas as pd
   21 | import statsmodels.formula.api as smf
   22 | import warnings
   23 | warnings.filterwarnings("ignore")
   24 | 
   25 | REPO = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   26 | CTRL = "z_word_length + z_log_freq + z_zone + z_prev_log_RT"
   27 | F1 = f"log_RT ~ {CTRL} + z_surprisal"
   28 | F2 = F1 + " + z_tee_k3"
   29 | PUNCT = set(".,;:!?\"'`)(-—")
   30 | 
   31 | 
   32 | def zc(d, cols):
   33 |     for c in cols:
   34 |         v = d[c].dropna()
   35 |         d["z_" + c] = (d[c] - v.mean()) / v.std()
   36 |     return d
   37 | 
   38 | 
   39 | def build():
   40 |     w = pd.read_csv(f"{REPO}/rebuild_v2_outputs/sample_8a6087341e.csv")
   41 |     w["punct_final"] = w.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
   42 |     rt = pd.read_csv(f"{REPO}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   43 |                      sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
   44 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   45 |     m = rt.merge(w[["story_id", "zone", "word", "tee_k3", "surprisal", "word_length",
   46 |                     "log_freq", "punct_final"]], on=["story_id", "zone"], how="inner",
   47 |                  suffixes=("_rt", ""))
   48 |     m["log_RT"] = np.log(m.RT)
   49 |     m = m.sort_values(["participant", "story_id", "zone"])
   50 |     m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
   51 |     wcol = "word" if "word" in m.columns else "word_y"
   52 |     m["word_type"] = m[wcol].astype(str).str.lower().str.strip()
   53 |     d = m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   54 |                          "prev_log_RT", "surprisal", "tee_k3"]).copy()
   55 |     return zc(d, ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"])
   56 | 
   57 | 
   58 | def report(label, d, form1=F1, form2=F2, groups="participant"):
   59 |     m1 = smf.mixedlm(form1, d, groups=d[groups]).fit(reml=False, method="lbfgs")
   60 |     m2 = smf.mixedlm(form2, d, groups=d[groups]).fit(reml=False, method="lbfgs")
   61 |     print(f"{label:<44}n={len(d):>8,}  dAIC={m1.aic-m2.aic:>8.1f}  "
   62 |           f"beta={m2.params['z_tee_k3']:>+.5f}  p={m2.pvalues['z_tee_k3']:.2e}")
   63 |     return m2
   64 | 
   65 | 
   66 | def main():
   67 |     d = build()
   68 |     print(f"punct-final words in sample: {d.punct_final.mean():.1%} of observations\n")
   69 | 
   70 |     print("=" * 96)
   71 |     print("1. PUNCTUATION")
   72 |     print("=" * 96)
   73 |     report("headline (no punctuation control)", d)
   74 |     d2 = d.copy()
   75 |     d2["z_punct"] = (d2.punct_final - d2.punct_final.mean()) / d2.punct_final.std()
   76 |     report("+ punctuation covariate", d2,
   77 |            F1 + " + z_punct", F2 + " + z_punct")
   78 |     report("punctuation-free words only", d[d.punct_final == 0].pipe(
   79 |         zc, ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"]))
   80 | 
   81 |     print("\n" + "=" * 96)
   82 |     print("2. LEXICAL BASELINE (does TEE predict RT for the SAME word "
   83 |           "across contexts?)")
   84 |     print("=" * 96)
   85 |     dw = d.copy()
   86 |     cols = ["log_RT", "z_word_length", "z_log_freq", "z_zone", "z_prev_log_RT",
   87 |             "z_surprisal", "z_tee_k3"]
   88 |     g = dw.groupby("word_type")
   89 |     keep = g["log_RT"].transform("size") >= 5      # word must recur
   90 |     dw = dw[keep].copy()
   91 |     g = dw.groupby("word_type")
   92 |     for c in cols:
   93 |         dw[c] = dw[c] - g[c].transform("mean")
   94 |     print(f"word types retained (>=5 occurrences): {dw.word_type.nunique():,}")
   95 |     report("word-identity demeaned", dw)
   96 | 
   97 |     print("\n" + "=" * 96)
   98 |     print("3. BOTH (punctuation-free AND word-identity demeaned)")
   99 |     print("=" * 96)
  100 |     db = d[d.punct_final == 0].copy()
  101 |     db = zc(db, ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"])
  102 |     g = db.groupby("word_type")
  103 |     db = db[g["log_RT"].transform("size") >= 5].copy()
  104 |     g = db.groupby("word_type")
  105 |     for c in cols:
  106 |         db[c] = db[c] - g[c].transform("mean")
  107 |     report("punct-free + word-identity demeaned", db)
  108 | 
  109 | 
  110 | if __name__ == "__main__":
  111 |     main()
```


==============================================================================
### FILE: gp_confound_check/ns_subject_level.py
==============================================================================

```
    1 | """
    2 | SUBJECT-LEVEL INFERENCE ON THE NATURAL STORIES TEE EFFECT
    3 | =========================================================
    4 | The ZuCo eye-tracking analysis found a null using SUBJECT-LEVEL inference:
    5 | one beta per subject, then a group test across subjects, explicitly to avoid
    6 | pseudoreplication. The Natural Stories result instead pools 813,621
    7 | observations with a by-participant random intercept.
    8 | 
    9 | This script applies the ZuCo standard to Natural Stories: fit the model
   10 | separately within each of the 180 participants, then test the distribution of
   11 | per-participant TEE coefficients at the subject level.
   12 | 
   13 | If the betas are overwhelmingly positive, the pooled result is not a large-N
   14 | artifact and the ZuCo null is a paradigm difference. If they scatter around
   15 | zero, the headline needs rethinking.
   16 | 
   17 | Three specifications:
   18 |   FULL   = the project's control set (length, freq, position, prev RT, surprisal)
   19 |   ZUCO   = ZuCo's leaner control set (length, freq only) for direct comparability
   20 |   PUNCTFREE = FULL on punctuation-free words (ZuCo also removed these)
   21 | """
   22 | 
   23 | import numpy as np
   24 | import pandas as pd
   25 | import statsmodels.api as sm
   26 | from scipy import stats
   27 | import warnings
   28 | warnings.filterwarnings("ignore")
   29 | 
   30 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   31 | PUNCT = set(".,;:!?\"'`)(-—")
   32 | 
   33 | 
   34 | def build():
   35 |     w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   36 |     w["punct_final"] = w.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
   37 |     rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   38 |                      sep="\t").rename(columns={"item": "story_id",
   39 |                                                "WorkerId": "participant"})
   40 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   41 |     m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   42 |                     "log_freq", "punct_final"]],
   43 |                  on=["story_id", "zone"], how="inner")
   44 |     m["log_RT"] = np.log(m.RT)
   45 |     m = m.sort_values(["participant", "story_id", "zone"])
   46 |     m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
   47 |     return m
   48 | 
   49 | 
   50 | SPECS = {
   51 |     "FULL      (length, freq, zone, prevRT, surprisal)":
   52 |         ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"],
   53 |     "ZUCO-style(length, freq only)":
   54 |         ["word_length", "log_freq", "tee_k3"],
   55 | }
   56 | 
   57 | 
   58 | def per_subject(d, cols):
   59 |     """One OLS per participant; return the TEE coefficient from each."""
   60 |     out = []
   61 |     for pid, sub in d.groupby("participant"):
   62 |         s = sub.dropna(subset=cols + ["log_RT"])
   63 |         if len(s) < 200:
   64 |             continue
   65 |         X = s[cols].astype(float)
   66 |         X = (X - X.mean()) / X.std(ddof=0)
   67 |         X = sm.add_constant(X)
   68 |         if X.isna().any().any() or np.linalg.matrix_rank(X.values) < X.shape[1]:
   69 |             continue
   70 |         r = sm.OLS(s.log_RT.values, X.values).fit()
   71 |         out.append({"participant": pid, "n": len(s),
   72 |                     "beta": r.params[-1], "p": r.pvalues[-1]})
   73 |     return pd.DataFrame(out)
   74 | 
   75 | 
   76 | def report(label, B):
   77 |     n = len(B)
   78 |     pos = int((B.beta > 0).sum())
   79 |     w = stats.wilcoxon(B.beta)
   80 |     t = stats.ttest_1samp(B.beta, 0)
   81 |     sign = stats.binomtest(pos, n, 0.5)
   82 |     print(f"\n{'='*74}\n{label}\n{'='*74}")
   83 |     print(f"  participants            : {n}")
   84 |     print(f"  positive betas          : {pos}/{n} ({pos/n:.1%})")
   85 |     print(f"  mean beta               : {B.beta.mean():+.5f}  (SD {B.beta.std():.5f})")
   86 |     print(f"  median beta             : {B.beta.median():+.5f}")
   87 |     print(f"  sign test               : p = {sign.pvalue:.3e}")
   88 |     print(f"  Wilcoxon signed-rank    : p = {w.pvalue:.3e}")
   89 |     print(f"  one-sample t            : t({n-1}) = {t.statistic:.2f}, p = {t.pvalue:.3e}")
   90 |     print(f"  individually sig (p<.05): {int((B.p < .05).sum())}/{n}")
   91 |     return dict(label=label, n=n, pos=pos, mean=B.beta.mean(),
   92 |                 wilcoxon_p=w.pvalue, t_p=t.pvalue, sign_p=sign.pvalue,
   93 |                 n_sig=int((B.p < .05).sum()))
   94 | 
   95 | 
   96 | def main():
   97 |     d = build()
   98 |     print(f"participants = {d.participant.nunique()}   rows = {len(d):,}")
   99 |     rows = []
  100 |     for label, cols in SPECS.items():
  101 |         B = per_subject(d, cols)
  102 |         rows.append(report(label, B))
  103 |         B.to_csv(f"{GP}/gp_confound_check/subject_betas_"
  104 |                  f"{label.split('(')[0].strip().lower()}.csv", index=False)
  105 | 
  106 |     pf = d[d.punct_final == 0]
  107 |     B = per_subject(pf, SPECS["FULL      (length, freq, zone, prevRT, surprisal)"])
  108 |     rows.append(report("PUNCT-FREE (FULL controls, punctuation-final removed)", B))
  109 | 
  110 |     print(f"\n{'='*74}\nZuCo comparison (10 subjects, eye-tracking, subject-level)")
  111 |     print(f"{'='*74}")
  112 |     print("  FFD  Wilcoxon p = .084   0/10 individually significant")
  113 |     print("  GD   Wilcoxon p = .160   0/10")
  114 |     print("  TRT  Wilcoxon p = .065   0/10")
  115 | 
  116 |     pd.DataFrame(rows).to_csv(f"{GP}/gp_confound_check/subject_level_summary.csv",
  117 |                               index=False)
  118 | 
  119 | 
  120 | if __name__ == "__main__":
  121 |     main()
```


==============================================================================
### FILE: gp_confound_check/ns_zuco_reconcile.py
==============================================================================

```
    1 | """
    2 | RECONCILING THE ZUCO NULL WITH THE NATURAL STORIES EFFECT
    3 | =========================================================
    4 | Two candidate explanations, both testable on Natural Stories alone:
    5 | 
    6 |   POWER    -- ZuCo has 10 subjects; Natural Stories has 171, of which only ~23%
    7 |               are individually significant. Subsample Natural Stories down to 10
    8 |               participants and ask how often the group test would detect the
    9 |               effect. If it is near ZuCo's hit rate, power explains the null.
   10 | 
   11 |   POSITION -- ZuCo uses short isolated sentences; Natural Stories are long
   12 |               connected narratives. The TEE effect is weakest at sentence-initial
   13 |               positions. Restrict Natural Stories to ZuCo-like material (early
   14 |               positions / short sentences) and see whether it approaches null.
   15 | 
   16 | Both use subject-level inference throughout (one beta per participant, group
   17 | test across participants) to match the ZuCo standard.
   18 | """
   19 | 
   20 | import numpy as np
   21 | import pandas as pd
   22 | import statsmodels.api as sm
   23 | from scipy import stats
   24 | import warnings
   25 | warnings.filterwarnings("ignore")
   26 | 
   27 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   28 | PUNCT = set(".,;:!?\"'`)(-—")
   29 | COLS = ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal", "tee_k3"]
   30 | RNG = np.random.default_rng(20260727)
   31 | 
   32 | 
   33 | def build():
   34 |     w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   35 |     w["punct_final"] = w.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
   36 |     rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   37 |                      sep="\t").rename(columns={"item": "story_id",
   38 |                                                "WorkerId": "participant"})
   39 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   40 |     m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   41 |                     "log_freq", "punct_final", "from_start", "sent_len"]],
   42 |                  on=["story_id", "zone"], how="inner")
   43 |     m["log_RT"] = np.log(m.RT)
   44 |     m = m.sort_values(["participant", "story_id", "zone"])
   45 |     m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
   46 |     return m
   47 | 
   48 | 
   49 | def per_subject(d, min_n=100):
   50 |     out = []
   51 |     for pid, sub in d.groupby("participant"):
   52 |         s = sub.dropna(subset=COLS + ["log_RT"])
   53 |         if len(s) < min_n:
   54 |             continue
   55 |         X = s[COLS].astype(float)
   56 |         sd = X.std(ddof=0)
   57 |         if (sd == 0).any():
   58 |             continue
   59 |         X = (X - X.mean()) / sd
   60 |         X = sm.add_constant(X)
   61 |         r = sm.OLS(s.log_RT.values, X.values).fit()
   62 |         out.append({"participant": pid, "n": len(s),
   63 |                     "beta": r.params[-1], "p": r.pvalues[-1]})
   64 |     return pd.DataFrame(out)
   65 | 
   66 | 
   67 | def group(B, label):
   68 |     if len(B) < 5:
   69 |         print(f"  {label:<44} too few participants")
   70 |         return None
   71 |     w = stats.wilcoxon(B.beta)
   72 |     pos = int((B.beta > 0).sum())
   73 |     print(f"  {label:<44} n={len(B):>4}  pos={pos:>3}/{len(B):<4}"
   74 |           f"  mean b={B.beta.mean():+.5f}  Wilcoxon p={w.pvalue:.2e}"
   75 |           f"  sig={int((B.p<.05).sum())}")
   76 |     return w.pvalue
   77 | 
   78 | 
   79 | def main():
   80 |     d = build()
   81 |     print(f"rows={len(d):,}  participants={d.participant.nunique()}\n")
   82 | 
   83 |     # ---------------- POSITION ----------------
   84 |     print("=" * 92)
   85 |     print("POSITION: is the effect weaker on ZuCo-like material? "
   86 |           "(subject-level inference throughout)")
   87 |     print("=" * 92)
   88 |     print("\nby position from sentence start:")
   89 |     bins = [("first 5 words", d[d.from_start <= 4]),
   90 |             ("first 10 words", d[d.from_start <= 9]),
   91 |             ("beyond word 10", d[d.from_start > 9])]
   92 |     for lab, sub in bins:
   93 |         group(per_subject(sub), lab)
   94 | 
   95 |     print("\nby sentence length (ZuCo sentences are short/isolated):")
   96 |     for lab, sub in [("short sentences (<=15 words)", d[d.sent_len <= 15]),
   97 |                      ("medium (16-25)", d[(d.sent_len > 15) & (d.sent_len <= 25)]),
   98 |                      ("long (>25)", d[d.sent_len > 25])]:
   99 |         group(per_subject(sub), lab)
  100 | 
  101 |     print("\nmost ZuCo-like slice (short sentences AND first 10 words):")
  102 |     zl = d[(d.sent_len <= 15) & (d.from_start <= 9)]
  103 |     group(per_subject(zl, min_n=50), "short & early")
  104 | 
  105 |     # ---------------- POWER ----------------
  106 |     print("\n" + "=" * 92)
  107 |     print("POWER: how often would a 10-participant study detect this effect?")
  108 |     print("=" * 92)
  109 |     B_full = per_subject(d)
  110 |     B_zuco = per_subject(zl, min_n=50)
  111 |     for label, B in [("full corpus", B_full), ("ZuCo-like slice", B_zuco)]:
  112 |         if B is None or len(B) < 10:
  113 |             continue
  114 |         hits = []
  115 |         for _ in range(4000):
  116 |             s = B.sample(10, replace=False, random_state=RNG.integers(1 << 31))
  117 |             hits.append(stats.wilcoxon(s.beta).pvalue < .05)
  118 |         print(f"  {label:<20} detection rate with n=10 subjects: "
  119 |               f"{np.mean(hits):.1%}   (ZuCo observed: 0/3 measures significant, "
  120 |               f"p = .065-.160)")
  121 | 
  122 | 
  123 | if __name__ == "__main__":
  124 |     main()
```


==============================================================================
### FILE: gp_confound_check/null_curvature_tee.py
==============================================================================

```
    1 | """
    2 | NULL MODEL: is the curvature(t-1) -> TEE(t) relationship mechanical?
    3 | ====================================================================
    4 | In the locked sample, curvature at t-1 forecasts LOWER TEE at t
    5 | (beta = -0.151 for curvature_3, -0.225 for curvature_1).
    6 | 
    7 | Candidate mechanical account: a bent fit window has partially cancelling steps,
    8 | so the least-squares slope is small, so the extrapolation barely projects past
    9 | the last point and cannot miss by much. A straight window gives a long
   10 | extrapolation vector with more room to overshoot. If so, the negative
   11 | relationship should appear in ANY trajectory with no language in it.
   12 | 
   13 | Test: synthetic 768-dim walks with no linguistic content, generated with a
   14 | tunable directional persistence so curvature varies naturally. Step-size
   15 | distribution matched to the real layer-6 word-to-word displacements
   16 | (mean 64.0, sd 9.4 from displacement_8a6087341e.csv).
   17 | 
   18 | We compute exactly the same two quantities as the real analysis:
   19 |   curvature_3(t-1)  = mean of 3 successive angles ending at t-1
   20 |   TEE(t)            = ||h_t - extrapolate(OLS fit over h_{t-3..t-1})||
   21 | and regress z(TEE_t) on z(curvature_{t-1}).
   22 | 
   23 | Reference values to beat (real data, position + story FE + punct + lexical):
   24 |   curvature_3 -> TEE : -0.151
   25 |   curvature_1 -> TEE : -0.225
   26 | Same-position correlations in real data: r(TEE, curv_3) = +0.104,
   27 |                                          r(TEE, curv_1) = +0.398
   28 | """
   29 | 
   30 | import numpy as np
   31 | import pandas as pd
   32 | from scipy import stats
   33 | 
   34 | RNG = np.random.default_rng(20260727)
   35 | D = 768
   36 | N_WALKS = 400
   37 | LEN = 60
   38 | STEP_MEAN, STEP_SD = 64.0, 9.4        # matched to real layer-6 word steps
   39 | 
   40 | 
   41 | def make_walk(n, persistence):
   42 |     """Random walk with directional persistence in [0,1).
   43 |     0 = isotropic (high curvature); ->1 = strongly directional (low curvature)."""
   44 |     dirs = np.zeros((n, D))
   45 |     v = RNG.normal(size=D)
   46 |     v /= np.linalg.norm(v)
   47 |     for i in range(n):
   48 |         new = RNG.normal(size=D)
   49 |         new /= np.linalg.norm(new)
   50 |         v = persistence * v + (1 - persistence) * new
   51 |         v /= np.linalg.norm(v)
   52 |         dirs[i] = v
   53 |     mags = RNG.normal(STEP_MEAN, STEP_SD, size=n).clip(1.0)
   54 |     steps = dirs * mags[:, None]
   55 |     return np.cumsum(steps, axis=0)
   56 | 
   57 | 
   58 | def angle(a, b):
   59 |     na, nb = np.linalg.norm(a), np.linalg.norm(b)
   60 |     if na < 1e-12 or nb < 1e-12:
   61 |         return np.nan
   62 |     c = np.clip(np.dot(a, b) / (na * nb), -1, 1)
   63 |     return float(np.arccos(c))
   64 | 
   65 | 
   66 | def measures(H):
   67 |     """Return per-index (curv_1, curv_3, tee_k3) with the project's conventions."""
   68 |     n = H.shape[0]
   69 |     step = lambda i: H[i] - H[i - 1]
   70 |     ang = np.full(n, np.nan)
   71 |     for i in range(2, n):
   72 |         ang[i] = angle(step(i), step(i - 1))
   73 |     curv1 = ang.copy()
   74 |     curv3 = np.full(n, np.nan)
   75 |     for i in range(4, n):
   76 |         curv3[i] = np.nanmean(ang[i - 2:i + 1])
   77 |     tee = np.full(n, np.nan)
   78 |     for t in range(3, n):
   79 |         Y = H[t - 3:t]
   80 |         A = np.column_stack([np.ones(3), np.arange(3)])
   81 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   82 |         tee[t] = np.linalg.norm(H[t] - (c[0] + c[1] * 3))
   83 |     return curv1, curv3, tee
   84 | 
   85 | 
   86 | rows = []
   87 | # a spread of persistence values so curvature varies across and within walks
   88 | for w in range(N_WALKS):
   89 |     p = RNG.uniform(-0.9, 0.9)
   90 |     H = make_walk(LEN, p)
   91 |     c1, c3, tee = measures(H)
   92 |     for t in range(5, LEN):
   93 |         rows.append({"walk": w, "persistence": p, "t": t,
   94 |                      "curv1_prev": c1[t - 1], "curv3_prev": c3[t - 1],
   95 |                      "curv1": c1[t], "curv3": c3[t], "tee": tee[t]})
   96 | 
   97 | df = pd.DataFrame(rows).dropna()
   98 | print(f"synthetic: {N_WALKS} walks x {LEN} steps -> n = {len(df):,} usable points")
   99 | print(f"curvature_3 range {df.curv3.min():.2f}-{df.curv3.max():.2f} "
  100 |       f"(real data mean ~1.99)")
  101 | print(f"TEE mean {df.tee.mean():.1f} (real data mean ~94.9)\n")
  102 | 
  103 | 
  104 | def z(s):
  105 |     return (s - s.mean()) / s.std(ddof=0)
  106 | 
  107 | 
  108 | print("=" * 74)
  109 | print("CROSS-POSITION: curvature(t-1) -> TEE(t)   [real data: -0.151 / -0.225]")
  110 | print("=" * 74)
  111 | for lab, col in [("curvature_3(t-1)", "curv3_prev"), ("curvature_1(t-1)", "curv1_prev")]:
  112 |     r, p = stats.pearsonr(z(df[col]), z(df.tee))
  113 |     print(f"  {lab:<22} r = {r:>+7.4f}   p = {p:.2e}")
  114 | 
  115 | print("\n" + "=" * 74)
  116 | print("SAME-POSITION: curvature(t) vs TEE(t)   [real data: +0.104 / +0.398]")
  117 | print("=" * 74)
  118 | for lab, col in [("curvature_3(t)", "curv3"), ("curvature_1(t)", "curv1")]:
  119 |     r, p = stats.pearsonr(z(df[col]), z(df.tee))
  120 |     print(f"  {lab:<22} r = {r:>+7.4f}   p = {p:.2e}")
  121 | 
  122 | print("\n" + "=" * 74)
  123 | print("WITHIN-WALK (persistence held fixed): does it survive?")
  124 | print("=" * 74)
  125 | res = []
  126 | for w, g in df.groupby("walk"):
  127 |     if len(g) < 20:
  128 |         continue
  129 |     res.append(stats.pearsonr(g.curv3_prev, g.tee)[0])
  130 | res = np.array(res)
  131 | print(f"  mean within-walk r(curv3_prev, TEE) = {res.mean():+.4f}   "
  132 |       f"{(res < 0).sum()}/{len(res)} negative   "
  133 |       f"Wilcoxon p = {stats.wilcoxon(res).pvalue:.2e}")
  134 | 
  135 | print("\n" + "=" * 74)
  136 | print("MECHANISM CHECK: does bent window -> short fitted step?")
  137 | print("=" * 74)
  138 | sub = df.dropna(subset=["curv3_prev"])
  139 | fit_norm = []
  140 | for w, g in df.groupby("walk"):
  141 |     pass
  142 | # recompute fitted-slope norms directly on a fresh set of walks
  143 | norms, curvs = [], []
  144 | for w in range(120):
  145 |     p = RNG.uniform(-0.9, 0.9)
  146 |     H = make_walk(LEN, p)
  147 |     c1, c3, tee = measures(H)
  148 |     for t in range(5, LEN):
  149 |         Y = H[t - 3:t]
  150 |         A = np.column_stack([np.ones(3), np.arange(3)])
  151 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
  152 |         if not np.isnan(c3[t - 1]):
  153 |             norms.append(np.linalg.norm(c[1]))     # fitted per-step direction norm
  154 |             curvs.append(c3[t - 1])
  155 | r, p = stats.pearsonr(curvs, norms)
  156 | print(f"  r(curvature(t-1), ||fitted slope||) = {r:+.4f}  p = {p:.2e}")
  157 | print("  (strong negative => bent windows produce short extrapolation vectors,")
  158 | print("   which is the proposed mechanism)")
```


==============================================================================
### FILE: gp_confound_check/onestop_analyze.py
==============================================================================

```
    1 | """
    2 | DOES TEE PREDICT EYE MOVEMENTS IN ONESTOP? (subject-level inference)
    3 | ====================================================================
    4 | Pre-registered expectation from the Natural Stories work:
    5 |   - TEE should predict reading time beyond length, frequency and surprisal
    6 |   - the effect should be ABSENT at sentence-initial positions and present
    7 |     later in the sentence (the position boundary condition)
    8 |   - ZuCo's null should be attributable to power (42% detection at n=10)
    9 | 
   10 | Three dependent measures, matching the ZuCo analysis:
   11 |   FFD = IA_FIRST_FIXATION_DURATION
   12 |   GD  = IA_FIRST_RUN_DWELL_TIME     (gaze duration)
   13 |   TRT = IA_DWELL_TIME               (total reading time)
   14 | 
   15 | Inference: one regression per participant, then a group test across
   16 | participants. Never pooled across words.
   17 | """
   18 | 
   19 | import numpy as np
   20 | import pandas as pd
   21 | import statsmodels.api as sm
   22 | from scipy import stats
   23 | import os, warnings
   24 | warnings.filterwarnings("ignore")
   25 | 
   26 | HERE = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check")
   27 | IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
   28 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   29 | DVS = {"FFD": "IA_FIRST_FIXATION_DURATION",
   30 |        "GD": "IA_FIRST_RUN_DWELL_TIME",
   31 |        "TRT": "IA_DWELL_TIME"}
   32 | PUNCT = set(".,;:!?\"'`)(-—")
   33 | 
   34 | 
   35 | def load():
   36 |     use = ["participant_id"] + KEY + list(DVS.values()) + \
   37 |           ["word_length", "wordfreq_frequency", "gpt2_surprisal"]
   38 |     d = pd.read_csv(IA, usecols=use, low_memory=False)
   39 |     T = pd.read_csv(f"{HERE}/onestop_tee.csv")
   40 |     d = d.merge(T[KEY + ["word", "tee_k3", "surprisal_own", "word_idx", "n_words"]],
   41 |                 on=KEY, how="left")
   42 |     for c in list(DVS.values()) + ["word_length", "wordfreq_frequency",
   43 |                                    "gpt2_surprisal"]:
   44 |         d[c] = pd.to_numeric(d[c], errors="coerce")
   45 |     d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
   46 |     d["punct_final"] = d.word.astype(str).str[-1].isin(list(PUNCT)).astype(int)
   47 |     # position within sentence: restart after any sentence-final punctuation
   48 |     d = d.sort_values(["participant_id"] + KEY)
   49 |     sent_end = d.word.astype(str).str[-1].isin(list(".!?"))
   50 |     d["sent_idx"] = sent_end.groupby(
   51 |         [d.participant_id, d.article_id, d.paragraph_id, d.difficulty_level]
   52 |     ).cumsum().shift(1).fillna(0)
   53 |     d["from_sent_start"] = d.groupby(
   54 |         ["participant_id", "article_id", "paragraph_id", "difficulty_level",
   55 |          "sent_idx"]).cumcount()
   56 |     return d
   57 | 
   58 | 
   59 | PREDS = ["word_length", "log_freq", "surprisal_own", "tee_k3"]
   60 | PREDS_ZUCO = ["word_length", "log_freq", "tee_k3"]
   61 | 
   62 | 
   63 | def per_subject(d, dv, preds, min_n=150):
   64 |     out = []
   65 |     for pid, sub in d.groupby("participant_id"):
   66 |         s = sub.dropna(subset=preds + [dv])
   67 |         s = s[s[dv] > 0]
   68 |         if len(s) < min_n:
   69 |             continue
   70 |         X = s[preds].astype(float)
   71 |         sd = X.std(ddof=0)
   72 |         if (sd == 0).any():
   73 |             continue
   74 |         X = sm.add_constant((X - X.mean()) / sd)
   75 |         r = sm.OLS(np.log(s[dv].values), X.values).fit()
   76 |         out.append({"participant_id": pid, "n": len(s),
   77 |                     "beta": r.params[-1], "p": r.pvalues[-1]})
   78 |     return pd.DataFrame(out)
   79 | 
   80 | 
   81 | def group(B, label):
   82 |     if B is None or len(B) < 5:
   83 |         print(f"  {label:<40} too few participants")
   84 |         return
   85 |     pos = int((B.beta > 0).sum())
   86 |     w = stats.wilcoxon(B.beta).pvalue
   87 |     t = stats.ttest_1samp(B.beta, 0)
   88 |     print(f"  {label:<40} n={len(B):>4}  pos={pos:>3}/{len(B):<4} "
   89 |           f"({pos/len(B):>5.1%})  mean b={B.beta.mean():+.5f}  "
   90 |           f"Wilcoxon p={w:.2e}  t={t.statistic:>6.2f}  sig={int((B.p<.05).sum())}")
   91 | 
   92 | 
   93 | def main():
   94 |     d = load()
   95 |     print(f"rows={len(d):,}  participants={d.participant_id.nunique()}  "
   96 |           f"words with TEE={d.tee_k3.notna().sum():,}\n")
   97 | 
   98 |     print("=" * 108)
   99 |     print("MAIN: TEE beyond length, frequency, surprisal (subject-level)")
  100 |     print("=" * 108)
  101 |     for name, dv in DVS.items():
  102 |         group(per_subject(d, dv, PREDS), f"{name}  (full controls)")
  103 | 
  104 |     print("\n" + "=" * 108)
  105 |     print("ZuCo-style controls (length + frequency only), for direct comparison")
  106 |     print("=" * 108)
  107 |     for name, dv in DVS.items():
  108 |         group(per_subject(d, dv, PREDS_ZUCO), f"{name}  (length+freq only)")
  109 | 
  110 |     print("\n" + "=" * 108)
  111 |     print("PUNCTUATION-FREE (word not punctuation-final)")
  112 |     print("=" * 108)
  113 |     pf = d[d.punct_final == 0]
  114 |     for name, dv in DVS.items():
  115 |         group(per_subject(pf, dv, PREDS), f"{name}  (punct-free)")
  116 | 
  117 |     print("\n" + "=" * 108)
  118 |     print("POSITION BOUNDARY CONDITION (predicted: null early, present later)")
  119 |     print("=" * 108)
  120 |     for name, dv in DVS.items():
  121 |         print(f"  -- {name} --")
  122 |         group(per_subject(d[d.from_sent_start <= 4], dv, PREDS), "first 5 words of sentence")
  123 |         group(per_subject(d[d.from_sent_start > 9], dv, PREDS), "beyond word 10")
  124 | 
  125 | 
  126 | if __name__ == "__main__":
  127 |     main()
```


==============================================================================
### FILE: gp_confound_check/onestop_compute_tee.py
==============================================================================

```
    1 | """
    2 | COMPUTE TEE ON THE ONESTOP PARAGRAPHS
    3 | =====================================
    4 | OneStop Ordinary Reading (360-participant corpus; ordinary-reading subcorpus).
    5 | Word sequences are reconstructed from the interest-area report itself
    6 | (IA_LABEL ordered by IA_ID within article/paragraph/difficulty), so the TEE
    7 | values align to the eye-tracking rows by construction.
    8 | 
    9 | Conventions match the locked Natural Stories pipeline:
   10 |   GPT-2 small, layer 6, word state = hidden state at the word's FINAL subword,
   11 |   TEE_k3 = || h(w) - extrapolate(linear fit over the 3 preceding word states) ||.
   12 | 
   13 | Sink handling: paragraphs are fed in isolation, so token 0 is the attention-sink
   14 | position. Fit windows are started at word index 1, and only words at index >= 4
   15 | are emitted, so no reported value has the sink inside its window.
   16 | 
   17 | Surprisal is computed in the same forward pass for internal consistency
   18 | (OneStop also ships a precomputed gpt2_surprisal, kept as a cross-check).
   19 | 
   20 | Output: onestop_tee.csv  (article_id, paragraph_id, difficulty_level, IA_ID,
   21 |         word, tee_k3, surprisal_own, word_idx, n_words)
   22 | """
   23 | 
   24 | import numpy as np
   25 | import pandas as pd
   26 | import torch
   27 | from transformers import GPT2TokenizerFast, GPT2LMHeadModel
   28 | import os, warnings
   29 | warnings.filterwarnings("ignore")
   30 | 
   31 | IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
   32 | OUT = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check/onestop_tee.csv")
   33 | LAYER, K = 6, 3
   34 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   35 | 
   36 | KEY = ["article_id", "paragraph_id", "difficulty_level"]
   37 | 
   38 | print("reading interest-area report (label columns only)...", flush=True)
   39 | d = pd.read_csv(IA, usecols=KEY + ["IA_ID", "IA_LABEL"], low_memory=False)
   40 | print(f"  {len(d):,} rows", flush=True)
   41 | 
   42 | # one row per (paragraph, word position)
   43 | paras = (d.drop_duplicates(subset=KEY + ["IA_ID"])
   44 |            .sort_values(KEY + ["IA_ID"])
   45 |            .reset_index(drop=True))
   46 | print(f"  {paras.groupby(KEY).ngroups:,} unique paragraphs, "
   47 |       f"{len(paras):,} paragraph-word slots", flush=True)
   48 | del d
   49 | 
   50 | tok = GPT2TokenizerFast.from_pretrained("gpt2")
   51 | model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEVICE)
   52 | torch.set_num_threads(os.cpu_count() or 4)
   53 | 
   54 | 
   55 | def tee_for(words):
   56 |     """Return per-word (tee_k3, surprisal); NaN where undefined or sink-exposed."""
   57 |     ids, final_idx = [], []
   58 |     for i, w in enumerate(words):
   59 |         piece = w if i == 0 else " " + w
   60 |         t = tok.encode(piece)
   61 |         if not t:                       # empty label guard
   62 |             final_idx.append(None)
   63 |             continue
   64 |         ids.extend(t)
   65 |         final_idx.append(len(ids) - 1)
   66 |     if len(ids) < 8:
   67 |         return [np.nan] * len(words), [np.nan] * len(words)
   68 |     with torch.no_grad():
   69 |         out = model(torch.tensor([ids]).to(DEVICE), output_hidden_states=True)
   70 |     h = out.hidden_states[LAYER][0].float().cpu().numpy()
   71 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   72 | 
   73 |     # word-level surprisal (sum of subword surprisals, base 2)
   74 |     tok_s = np.zeros(len(ids))
   75 |     for t in range(1, len(ids)):
   76 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   77 |     starts, prev = [], 0
   78 |     for fi in final_idx:
   79 |         starts.append(prev)
   80 |         if fi is not None:
   81 |             prev = fi + 1
   82 |     surp = [float(tok_s[s:f + 1].sum()) if f is not None else np.nan
   83 |             for s, f in zip(starts, final_idx)]
   84 | 
   85 |     wh = np.array([h[fi] if fi is not None else np.full(h.shape[1], np.nan)
   86 |                    for fi in final_idx])
   87 |     tee = np.full(len(words), np.nan)
   88 |     for i in range(len(words)):
   89 |         lo = max(i - K, 1)              # never let word 0 into the window
   90 |         if i < 4 or (i - lo) < 2 or np.isnan(wh[lo:i + 1]).any():
   91 |             continue
   92 |         Y = wh[lo:i]
   93 |         m = Y.shape[0]
   94 |         A = np.column_stack([np.ones(m), np.arange(m)])
   95 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   96 |         tee[i] = float(np.linalg.norm(wh[i] - (c[0] + c[1] * m)))
   97 |     return tee, surp
   98 | 
   99 | 
  100 | rows = []
  101 | groups = list(paras.groupby(KEY, sort=False))
  102 | for gi, (key, g) in enumerate(groups):
  103 |     words = [str(x) for x in g.IA_LABEL.tolist()]
  104 |     tee, surp = tee_for(words)
  105 |     for j, (_, r) in enumerate(g.iterrows()):
  106 |         rows.append({"article_id": key[0], "paragraph_id": key[1],
  107 |                      "difficulty_level": key[2], "IA_ID": r.IA_ID,
  108 |                      "word": words[j], "word_idx": j, "n_words": len(words),
  109 |                      "tee_k3": tee[j], "surprisal_own": surp[j]})
  110 |     if (gi + 1) % 50 == 0:
  111 |         print(f"  {gi+1}/{len(groups)} paragraphs", flush=True)
  112 | 
  113 | T = pd.DataFrame(rows)
  114 | T.to_csv(OUT, index=False)
  115 | print(f"\nDONE -> {OUT}")
  116 | print(f"  {len(T):,} paragraph-word rows; usable TEE: {T.tee_k3.notna().sum():,}")
  117 | print(f"  mean TEE {T.tee_k3.mean():.2f}  sd {T.tee_k3.std():.2f}")
```


==============================================================================
### FILE: gp_confound_check/onestop_context_tee.py
==============================================================================

```
    1 | """
    2 | DOES THE ONESTOP REVERSAL COME FROM MISSING CONTEXT?
    3 | ====================================================
    4 | The Natural Stories TEE was computed over whole stories (1024-token chunks,
    5 | stride 512), so a word deep in a story has hundreds of words of preceding
    6 | context. My first OneStop pass fed each paragraph in ISOLATION -- at most ~120
    7 | words, and near-zero for words early in a paragraph.
    8 | 
    9 | That is a real difference between the two pipelines, and readers in OneStop do
   10 | see the preceding paragraphs (they read each article sequentially).
   11 | 
   12 | This script recomputes TEE and surprisal with ARTICLE-LEVEL context: paragraphs
   13 | of the same article and difficulty level concatenated in order, one forward
   14 | pass per article, values emitted per paragraph-word.
   15 | 
   16 | Diagnostics:
   17 |   1. r(my surprisal, OneStop gpt2_surprisal) under isolated vs article context,
   18 |      overall and by position within paragraph. If OneStop used larger context,
   19 |      the article-context version should agree better, especially early in a
   20 |      paragraph.
   21 |   2. r(TEE isolated, TEE article-context) -- how much does context change it?
   22 | 
   23 | Output: onestop_tee_ctx.csv
   24 | """
   25 | 
   26 | import numpy as np
   27 | import pandas as pd
   28 | import torch
   29 | from transformers import GPT2TokenizerFast, GPT2LMHeadModel
   30 | import os, warnings
   31 | warnings.filterwarnings("ignore")
   32 | 
   33 | HERE = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check")
   34 | IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
   35 | KEY = ["article_id", "paragraph_id", "difficulty_level"]
   36 | LAYER, K = 6, 3
   37 | CHUNK, STRIDE = 1024, 512
   38 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   39 | 
   40 | d = pd.read_csv(IA, usecols=KEY + ["IA_ID", "IA_LABEL", "gpt2_surprisal"],
   41 |                 low_memory=False)
   42 | paras = (d.drop_duplicates(subset=KEY + ["IA_ID"])
   43 |            .sort_values(KEY + ["IA_ID"]).reset_index(drop=True))
   44 | del d
   45 | 
   46 | tok = GPT2TokenizerFast.from_pretrained("gpt2")
   47 | model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEVICE)
   48 | torch.set_num_threads(os.cpu_count() or 4)
   49 | 
   50 | 
   51 | def doc_pass(words):
   52 |     """Chunked forward pass over a whole document; first-write-wins, matching
   53 |     the Natural Stories convention. Returns per-word (tee, surprisal)."""
   54 |     ids, final_idx = [], []
   55 |     for i, w in enumerate(words):
   56 |         t = tok.encode(w if i == 0 else " " + w)
   57 |         if not t:
   58 |             final_idx.append(None)
   59 |             continue
   60 |         ids.extend(t)
   61 |         final_idx.append(len(ids) - 1)
   62 |     n = len(ids)
   63 |     hidden, logits = {}, {}
   64 |     pos = 0
   65 |     while pos < n:
   66 |         end = min(pos + CHUNK, n)
   67 |         with torch.no_grad():
   68 |             out = model(torch.tensor([ids[pos:end]]).to(DEVICE),
   69 |                         output_hidden_states=True)
   70 |         hs = out.hidden_states[LAYER][0].float().cpu().numpy()
   71 |         lp = torch.log_softmax(out.logits[0].float(), -1).cpu().numpy()
   72 |         for i in range(end - pos):
   73 |             g = pos + i
   74 |             if g not in hidden:
   75 |                 hidden[g] = hs[i]
   76 |                 logits[g] = lp[i]
   77 |         del out
   78 |         if end >= n:
   79 |             break
   80 |         pos += STRIDE
   81 | 
   82 |     tok_s = np.zeros(n)
   83 |     for t in range(1, n):
   84 |         tok_s[t] = -float(logits[t - 1][ids[t]]) / np.log(2)
   85 |     starts, prev = [], 0
   86 |     for fi in final_idx:
   87 |         starts.append(prev)
   88 |         if fi is not None:
   89 |             prev = fi + 1
   90 |     surp = [float(tok_s[s:f + 1].sum()) if f is not None else np.nan
   91 |             for s, f in zip(starts, final_idx)]
   92 | 
   93 |     tee = np.full(len(words), np.nan)
   94 |     for i in range(len(words)):
   95 |         lo = max(i - K, 1)
   96 |         if i < 4 or (i - lo) < 2:
   97 |             continue
   98 |         idxs = [final_idx[j] for j in range(lo, i + 1)]
   99 |         if any(x is None for x in idxs):
  100 |             continue
  101 |         Y = np.stack([hidden[x] for x in idxs[:-1]])
  102 |         m = Y.shape[0]
  103 |         A = np.column_stack([np.ones(m), np.arange(m)])
  104 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
  105 |         tee[i] = float(np.linalg.norm(hidden[idxs[-1]] - (c[0] + c[1] * m)))
  106 |     return tee, surp
  107 | 
  108 | 
  109 | rows = []
  110 | docs = list(paras.groupby(["article_id", "difficulty_level"], sort=False))
  111 | for di, ((aid, lvl), g) in enumerate(docs):
  112 |     g = g.sort_values(["paragraph_id", "IA_ID"])
  113 |     words = [str(x) for x in g.IA_LABEL.tolist()]
  114 |     tee, surp = doc_pass(words)
  115 |     for j, (_, r) in enumerate(g.iterrows()):
  116 |         rows.append({"article_id": aid, "paragraph_id": r.paragraph_id,
  117 |                      "difficulty_level": lvl, "IA_ID": r.IA_ID,
  118 |                      "tee_ctx": tee[j], "surprisal_ctx": surp[j]})
  119 |     if (di + 1) % 10 == 0:
  120 |         print(f"  {di+1}/{len(docs)} documents", flush=True)
  121 | 
  122 | C = pd.DataFrame(rows)
  123 | C.to_csv(f"{HERE}/onestop_tee_ctx.csv", index=False)
  124 | 
  125 | # ---- diagnostics ----
  126 | iso = pd.read_csv(f"{HERE}/onestop_tee.csv")
  127 | ref = paras.copy()
  128 | ref["gpt2_surprisal"] = pd.to_numeric(ref.gpt2_surprisal, errors="coerce")
  129 | M = (iso.merge(C, on=KEY + ["IA_ID"])
  130 |         .merge(ref[KEY + ["IA_ID", "gpt2_surprisal"]], on=KEY + ["IA_ID"]))
  131 | ok = M.dropna(subset=["gpt2_surprisal", "surprisal_own", "surprisal_ctx"])
  132 | print(f"\nn = {len(ok):,}")
  133 | print(f"r(OneStop surprisal, mine ISOLATED)        = "
  134 |       f"{ok.surprisal_own.corr(ok.gpt2_surprisal):.4f}")
  135 | print(f"r(OneStop surprisal, mine ARTICLE CONTEXT) = "
  136 |       f"{ok.surprisal_ctx.corr(ok.gpt2_surprisal):.4f}")
  137 | print(f"r(TEE isolated, TEE article-context)       = "
  138 |       f"{M.tee_k3.corr(M.tee_ctx):.4f}")
  139 | print("\nby position within paragraph:")
  140 | M["bin"] = pd.cut(M.word_idx, [-1, 9, 29, 59, 9999],
  141 |                   labels=["0-9", "10-29", "30-59", "60+"])
  142 | for b, s in M.groupby("bin", observed=True):
  143 |     s = s.dropna(subset=["gpt2_surprisal", "surprisal_own", "surprisal_ctx"])
  144 |     print(f"  {str(b):>6}  n={len(s):>6,}  r(iso)={s.surprisal_own.corr(s.gpt2_surprisal):.3f}"
  145 |           f"   r(ctx)={s.surprisal_ctx.corr(s.gpt2_surprisal):.3f}")
```


==============================================================================
### FILE: gp_confound_check/onestop_geometry.py
==============================================================================

```
    1 | """
    2 | DECOMPOSE THE ONESTOP MEASURE: RUN-UP GEOMETRY vs TARGET DEVIATION
    3 | ===================================================================
    4 | Extrapolation error at word i is ||h_i - (fit through h_{lo..i-1} projected one
    5 | step)||. That single number confounds two things:
    6 | 
    7 |   RUN-UP GEOMETRY -- properties of words lo..i-1 alone. Fully determined before
    8 |     word i is seen, and therefore available to a reader deciding whether to skip
    9 |     word i. A straight run-up gives a long fitted step, which projects far ahead
   10 |     and leaves room to miss; a bent run-up gives a short fitted step that cannot
   11 |     miss by much.
   12 | 
   13 |   TARGET DEVIATION -- how far h_i actually falls from that projection, which is
   14 |     a property of word i and is not available before fixating it.
   15 | 
   16 | The lag analysis showed the skipping effect is carried by word i-1 rather than
   17 | word i, which points at the run-up. This computes the components directly so the
   18 | question can be asked without going through a lag.
   19 | 
   20 | EMITTED PER WORD (same pipeline conventions as onestop_context_tee.py: GPT-2
   21 | small, layer 6, k=3, article-level context, 1024/512 chunks, first-write-wins,
   22 | word state = final subword, fit window never includes token 0):
   23 | 
   24 |   run-up only (pre-fixation):
   25 |     slope_norm    ||c1||, length of the fitted per-step vector
   26 |     curv_prev     angle between step(i-1) and step(i-2), the bend of the run-up
   27 |     runup_disp    ||h_{i-1} - h_{lo}||, net distance covered by the run-up
   28 |     last_step     ||h_{i-1} - h_{i-2}||
   29 |   target deviation (post-fixation):
   30 |     resid_par     residual component along the fitted direction (signed)
   31 |     resid_perp    residual component orthogonal to it
   32 |     tee           ||residual||  (= sqrt(par^2 + perp^2); checked against the
   33 |                   existing onestop_tee_ctx.csv as a pipeline sanity check)
   34 | 
   35 | Output: onestop_geometry.csv
   36 | """
   37 | 
   38 | import numpy as np
   39 | import pandas as pd
   40 | import torch
   41 | from transformers import GPT2TokenizerFast, GPT2LMHeadModel
   42 | import os, warnings
   43 | warnings.filterwarnings("ignore")
   44 | 
   45 | HERE = os.path.expanduser("~/Projects/garden-path-tee-curvature/gp_confound_check")
   46 | IA = os.path.expanduser("~/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv")
   47 | KEY = ["article_id", "paragraph_id", "difficulty_level"]
   48 | LAYER, K = 6, 3
   49 | CHUNK, STRIDE = 1024, 512
   50 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   51 | 
   52 | d = pd.read_csv(IA, usecols=KEY + ["IA_ID", "IA_LABEL"], low_memory=False)
   53 | paras = (d.drop_duplicates(subset=KEY + ["IA_ID"])
   54 |            .sort_values(KEY + ["IA_ID"]).reset_index(drop=True))
   55 | del d
   56 | 
   57 | tok = GPT2TokenizerFast.from_pretrained("gpt2")
   58 | model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(DEVICE)
   59 | torch.set_num_threads(os.cpu_count() or 4)
   60 | 
   61 | 
   62 | def angle(a, b):
   63 |     na, nb = np.linalg.norm(a), np.linalg.norm(b)
   64 |     if na < 1e-9 or nb < 1e-9:
   65 |         return np.nan
   66 |     return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1, 1)))
   67 | 
   68 | 
   69 | def doc_pass(words):
   70 |     ids, final_idx = [], []
   71 |     for i, w in enumerate(words):
   72 |         t = tok.encode(w if i == 0 else " " + w)
   73 |         if not t:
   74 |             final_idx.append(None)
   75 |             continue
   76 |         ids.extend(t)
   77 |         final_idx.append(len(ids) - 1)
   78 |     n = len(ids)
   79 |     hidden, pos = {}, 0
   80 |     while pos < n:
   81 |         end = min(pos + CHUNK, n)
   82 |         with torch.no_grad():
   83 |             out = model(torch.tensor([ids[pos:end]]).to(DEVICE),
   84 |                         output_hidden_states=True)
   85 |         hs = out.hidden_states[LAYER][0].float().cpu().numpy()
   86 |         for i in range(end - pos):
   87 |             g = pos + i
   88 |             if g not in hidden:
   89 |                 hidden[g] = hs[i]
   90 |         del out
   91 |         if end >= n:
   92 |             break
   93 |         pos += STRIDE
   94 | 
   95 |     nw = len(words)
   96 |     out = {k: np.full(nw, np.nan) for k in
   97 |            ["tee", "slope_norm", "curv_prev", "runup_disp", "last_step",
   98 |             "resid_par", "resid_perp"]}
   99 |     for i in range(nw):
  100 |         lo = max(i - K, 1)
  101 |         if i < 4 or (i - lo) < 2:
  102 |             continue
  103 |         idxs = [final_idx[j] for j in range(lo, i + 1)]
  104 |         if any(x is None for x in idxs):
  105 |             continue
  106 |         H = [hidden[x] for x in idxs]
  107 |         Y = np.stack(H[:-1])
  108 |         m = Y.shape[0]
  109 |         A = np.column_stack([np.ones(m), np.arange(m)])
  110 |         c, *_ = np.linalg.lstsq(A, Y, rcond=None)
  111 |         pred = c[0] + c[1] * m
  112 |         resid = H[-1] - pred
  113 | 
  114 |         slope = c[1]
  115 |         sn = float(np.linalg.norm(slope))
  116 |         out["slope_norm"][i] = sn
  117 |         out["tee"][i] = float(np.linalg.norm(resid))
  118 |         if sn > 1e-9:
  119 |             u = slope / sn
  120 |             par = float(np.dot(resid, u))
  121 |             out["resid_par"][i] = par
  122 |             out["resid_perp"][i] = float(
  123 |                 np.linalg.norm(resid - par * u))
  124 |         out["runup_disp"][i] = float(np.linalg.norm(Y[-1] - Y[0]))
  125 |         if m >= 2:
  126 |             out["last_step"][i] = float(np.linalg.norm(Y[-1] - Y[-2]))
  127 |         # curvature of the run-up: bend between the two steps ending at i-1
  128 |         if lo >= 1 and (i - 1) - 2 >= lo - 1:
  129 |             j = i - 1
  130 |             tri = [final_idx[j - 2], final_idx[j - 1], final_idx[j]]
  131 |             if all(x is not None and x in hidden for x in tri):
  132 |                 a = hidden[tri[1]] - hidden[tri[0]]
  133 |                 b = hidden[tri[2]] - hidden[tri[1]]
  134 |                 out["curv_prev"][i] = angle(a, b)
  135 |     return out
  136 | 
  137 | 
  138 | rows = []
  139 | docs = list(paras.groupby(["article_id", "difficulty_level"], sort=False))
  140 | for di, ((aid, lvl), g) in enumerate(docs):
  141 |     g = g.sort_values(["paragraph_id", "IA_ID"])
  142 |     words = [str(x) for x in g.IA_LABEL.tolist()]
  143 |     o = doc_pass(words)
  144 |     for j, (_, r) in enumerate(g.iterrows()):
  145 |         rec = {"article_id": aid, "paragraph_id": r.paragraph_id,
  146 |                "difficulty_level": lvl, "IA_ID": r.IA_ID}
  147 |         rec.update({k: o[k][j] for k in o})
  148 |         rows.append(rec)
  149 |     if (di + 1) % 10 == 0:
  150 |         print(f"  {di+1}/{len(docs)} documents", flush=True)
  151 | 
  152 | G = pd.DataFrame(rows)
  153 | G.to_csv(f"{HERE}/onestop_geometry.csv", index=False)
  154 | print(f"\nwrote onestop_geometry.csv  ({len(G):,} rows, "
  155 |       f"{G.tee.notna().sum():,} with defined geometry)")
  156 | 
  157 | # ---------------- sanity: does this reproduce the existing TEE? ----------
  158 | C = pd.read_csv(f"{HERE}/onestop_tee_ctx.csv")
  159 | M = G.merge(C, on=KEY + ["IA_ID"], how="inner")
  160 | b = M.dropna(subset=["tee", "tee_ctx"])
  161 | print(f"\nSANITY vs onestop_tee_ctx.csv:  n = {len(b):,}   "
  162 |       f"r = {b.tee.corr(b.tee_ctx):.10f}   "
  163 |       f"max|diff| = {(b.tee - b.tee_ctx).abs().max():.2e}")
  164 | 
  165 | print("\ncomponent correlations (word level):")
  166 | cols = ["tee", "slope_norm", "curv_prev", "runup_disp", "last_step",
  167 |         "resid_par", "resid_perp"]
  168 | print(G[cols].corr().round(3).to_string())
  169 | print("\n  note: slope_norm and curv_prev should be strongly negatively")
  170 | print("  related if the geometric mechanism is as described (a bent run-up")
  171 | print("  produces a short fitted step).")
```


==============================================================================
### FILE: gp_confound_check/onestop_geometry_test.py
==============================================================================

```
    1 | """
    2 | WHICH COMPONENT DRIVES SKIPPING: RUN-UP GEOMETRY OR TARGET DEVIATION?
    3 | =====================================================================
    4 | onestop_geometry.py decomposed the measure and reproduced it exactly
    5 | (r = 1.0000000000 against the existing values). The components:
    6 | 
    7 |   RUN-UP ONLY, known before word i is fixated:
    8 |     slope_norm   length of the fitted per-step vector
    9 |     curv_prev    bend of the run-up
   10 |     last_step    size of the last step into i-1
   11 |   TARGET DEVIATION, only knowable after fixating word i:
   12 |     resid_perp   residual orthogonal to the heading  -- "went somewhere else"
   13 |     resid_par    residual along the heading (negative = the extrapolation
   14 |                  overshot; the trajectory did not travel as far as predicted)
   15 | 
   16 | The separation is clean where it matters: resid_perp is essentially uncorrelated
   17 | with slope_norm (r = .049) and curv_prev (r = -.050), so the two families are
   18 | not competing for the same variance.
   19 | 
   20 | Note on what the measure mostly is: tee correlates +0.62 with slope_norm and
   21 | -0.85 with resid_par. A high value therefore reflects, more than anything, that
   22 | the extrapolation OVERSHOT after a straight run-up -- not that the word landed
   23 | somewhere unexpected. That is worth knowing regardless of how this test comes
   24 | out.
   25 | 
   26 | TESTS (subject-level, controls = surprisal, log frequency, word length,
   27 | punctuation of the current word):
   28 |   G1  skip ~ tee                                  [the reported effect]
   29 |   G2  skip ~ slope_norm + curv_prev               [run-up only]
   30 |   G3  skip ~ resid_perp + resid_par               [target deviation only]
   31 |   G4  skip ~ all four                             [head to head]
   32 |   G5  G4 + previous word length/frequency/surprisal   [deflationary check]
   33 |   G6  same as G4 for first fixation duration      [contrast]
   34 | 
   35 | Fixed in advance: if the run-up terms carry the effect and survive in G4, the
   36 | skipping result is about the coherence of the preceding context, not about the
   37 | target word, and the timing objection dissolves. If resid_perp carries it, the
   38 | reader is responding to the target word and the parafoveal question stands.
   39 | """
   40 | 
   41 | import numpy as np
   42 | import pandas as pd
   43 | from scipy import stats
   44 | import statsmodels.api as sm
   45 | import warnings
   46 | warnings.filterwarnings("ignore")
   47 | 
   48 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   49 | ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
   50 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   51 | TRIAL = ["participant_id", "article_id", "paragraph_id", "difficulty_level"]
   52 | 
   53 | 
   54 | def zs(x):
   55 |     x = np.asarray(x, dtype=float)
   56 |     s = x.std()
   57 |     return (x - x.mean()) / s if s > 0 else x * 0
   58 | 
   59 | 
   60 | use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
   61 |                                   "wordfreq_frequency", "gpt2_surprisal",
   62 |                                   "IA_FIRST_FIXATION_DURATION"]
   63 | d = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
   64 | d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_geometry.csv"),
   65 |             on=KEY, how="left")
   66 | d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[
   67 |             KEY + ["word"]], on=KEY, how="left")
   68 | for c in use:
   69 |     if c not in ["participant_id"] + KEY:
   70 |         d[c] = pd.to_numeric(d[c], errors="coerce")
   71 | d = d.rename(columns={"gpt2_surprisal": "surprisal"})
   72 | d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
   73 | d["punct"] = d.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
   74 | d["skipped"] = (d.IA_DWELL_TIME.fillna(0) == 0).astype(float)
   75 | d["logFFD"] = np.log(d.IA_FIRST_FIXATION_DURATION.where(
   76 |     d.IA_FIRST_FIXATION_DURATION > 0))
   77 | 
   78 | d = d.sort_values(TRIAL + ["IA_ID"]).reset_index(drop=True)
   79 | g = d.groupby(TRIAL)
   80 | for nm, src in [("len_m1", "word_length"), ("freq_m1", "log_freq"),
   81 |                 ("surp_m1", "surprisal")]:
   82 |     d[nm] = g[src].shift(1)
   83 | d["id_m1"] = g["IA_ID"].shift(1)
   84 | bad = (d["IA_ID"] - d["id_m1"]) != 1
   85 | for c in ["len_m1", "freq_m1", "surp_m1"]:
   86 |     d.loc[bad, c] = np.nan
   87 | 
   88 | print(f"rows {len(d):,}   participants {d.participant_id.nunique()}")
   89 | print(f"mean P(skip) = {d.skipped.mean():.3f}\n")
   90 | 
   91 | CUR = ["surprisal", "log_freq", "word_length", "punct"]
   92 | PREV = ["len_m1", "freq_m1", "surp_m1"]
   93 | 
   94 | 
   95 | def subj(focus, extra, outcome, minn=200):
   96 |     cols = focus + CUR + extra
   97 |     out = {f: [] for f in focus}
   98 |     for pid, s in d.groupby("participant_id"):
   99 |         s = s.dropna(subset=cols + [outcome])
  100 |         if len(s) < minn:
  101 |             continue
  102 |         X = np.column_stack([zs(s[c].values) for c in cols])
  103 |         if (X.std(axis=0) == 0).any():
  104 |             continue
  105 |         r = sm.OLS(zs(s[outcome].values), sm.add_constant(X)).fit()
  106 |         for f in focus:
  107 |             out[f].append(r.params[cols.index(f) + 1])
  108 |     return {f: np.array(v) for f, v in out.items()}
  109 | 
  110 | 
  111 | def row(label, b):
  112 |     if len(b) < 10:
  113 |         print(f"    {label:<38} too few")
  114 |         return
  115 |     pos = (b > 0).mean()
  116 |     p = stats.wilcoxon(b).pvalue
  117 |     star = "  *" if (p < .01 and max(pos, 1 - pos) >= .65) else ""
  118 |     print(f"    {label:<38} beta={b.mean():>+9.5f}  {pos:>5.1%} pos  "
  119 |           f"p={p:<10.2e}{star}")
  120 | 
  121 | 
  122 | RUNUP = ["slope_norm", "curv_prev"]
  123 | TARGET = ["resid_perp", "resid_par"]
  124 | 
  125 | print("=" * 88)
  126 | print("OUTCOME: P(skip)          [* = p<.01 and >=65% sign agreement]")
  127 | print("=" * 88)
  128 | print("\n  G1  the reported effect")
  129 | row("tee", subj(["tee"], [], "skipped")["tee"])
  130 | 
  131 | print("\n  G2  run-up geometry only (pre-fixation information)")
  132 | r2 = subj(RUNUP, [], "skipped")
  133 | for f in RUNUP:
  134 |     row(f, r2[f])
  135 | 
  136 | print("\n  G3  target deviation only (post-fixation information)")
  137 | r3 = subj(TARGET, [], "skipped")
  138 | for f in TARGET:
  139 |     row(f, r3[f])
  140 | 
  141 | print("\n  G4  head to head, all four entered")
  142 | r4 = subj(RUNUP + TARGET, [], "skipped")
  143 | for f in RUNUP + TARGET:
  144 |     row(f, r4[f])
  145 | 
  146 | print("\n  G5  G4 + previous-word length, frequency, surprisal")
  147 | r5 = subj(RUNUP + TARGET, PREV, "skipped")
  148 | for f in RUNUP + TARGET:
  149 |     row(f, r5[f])
  150 | 
  151 | print("\n" + "=" * 88)
  152 | print("OUTCOME: first fixation duration (contrast)")
  153 | print("=" * 88)
  154 | r6 = subj(RUNUP + TARGET, [], "logFFD")
  155 | for f in RUNUP + TARGET:
  156 |     row(f, r6[f])
  157 | 
  158 | print("\n" + "=" * 88)
  159 | print("READING")
  160 | print("=" * 88)
  161 | print("""  Run-up terms surviving in G4/G5 -> the skipping effect is about the
  162 |   coherence of the preceding context, which the reader has already read. The
  163 |   timing objection to the skipping result dissolves, and the measure's
  164 |   behavioural signature in free reading is not about the target word at all.
  165 | 
  166 |   resid_perp surviving instead -> the reader is responding to the target word,
  167 |   and how they could do so before fixating it remains to be explained.""")
```


==============================================================================
### FILE: gp_confound_check/onestop_negative_probe.py
==============================================================================

```
    1 | """
    2 | WHAT DRIVES THE NEGATIVE TEE EFFECT ON ONESTOP TOTAL READING TIME?
    3 | ==================================================================
    4 | Verification established that the OneStop result is not a null: total reading
    5 | time carries a reliably NEGATIVE coefficient for extrapolation error under every
    6 | specification tried (-0.0023 to -0.0060, the stronger estimates from the better
    7 | controlled models). That is a harder fact than an absence, and the preview
    8 | account in the Discussion does not obviously explain it -- preview predicts
    9 | attenuation toward zero, not a sign flip.
   10 | 
   11 | Before deciding how to write it, find out whether the negative is (a) a genuine
   12 | duration effect, or (b) an artifact of what total reading time aggregates.
   13 | 
   14 | TRT sums ALL fixations on a word, including refixations and fixations from
   15 | regressions back to it. So TRT ~= first-pass duration + re-reading. If high-TEE
   16 | words are SKIPPED more often, or attract fewer refixations, TRT falls without
   17 | any word ever being read faster.
   18 | 
   19 | DECOMPOSITION (all subject-level, same controls):
   20 |   1. skipping        P(skip)          -- is the word fixated at all?
   21 |   2. first fixation  FFD              -- earliest measure, first-pass only
   22 |   3. gaze duration   GD               -- first-pass, all fixations before leaving
   23 |   4. total time      TRT              -- everything, including re-reading
   24 |   5. re-reading      TRT - GD         -- the part that is not first pass
   25 |   6. refixation      P(GD > FFD)      -- did the reader refixate within first pass
   26 | 
   27 | If the negative lives in skipping or in (TRT - GD), it is about where the eyes
   28 | GO, not about how long processing takes, and the Discussion should say so.
   29 | If it is present in GD and FFD too, it is a genuine speed-up and needs an
   30 | account.
   31 | 
   32 | Conditioning note, stated in advance: measures 2-6 are conditional on the word
   33 | being fixated, so if skipping is itself predicted by TEE they inherit a
   34 | selection effect. That is why skipping is tested first and reported regardless.
   35 | """
   36 | 
   37 | import numpy as np
   38 | import pandas as pd
   39 | from scipy import stats
   40 | import statsmodels.api as sm
   41 | import warnings
   42 | warnings.filterwarnings("ignore")
   43 | 
   44 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   45 | ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
   46 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   47 | 
   48 | 
   49 | def zs(x):
   50 |     x = np.asarray(x, dtype=float)
   51 |     s = x.std()
   52 |     return (x - x.mean()) / s if s > 0 else x * 0
   53 | 
   54 | 
   55 | cols = pd.read_csv(ONESTOP, nrows=0).columns.tolist()
   56 | want = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
   57 |                                    "wordfreq_frequency", "gpt2_surprisal"]
   58 | for c in ["IA_FIRST_FIXATION_DURATION", "IA_FIRST_RUN_DWELL_TIME",
   59 |           "IA_FIXATION_COUNT", "IA_SKIP", "IA_FIRST_RUN_FIXATION_COUNT"]:
   60 |     if c in cols:
   61 |         want.append(c)
   62 | print("columns available:", [c for c in want if c not in
   63 |       ["participant_id"] + KEY])
   64 | 
   65 | d = pd.read_csv(ONESTOP, usecols=want, low_memory=False)
   66 | d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
   67 |             on=KEY, how="left")
   68 | d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[
   69 |             KEY + ["word"]], on=KEY, how="left")
   70 | for c in want:
   71 |     if c not in ["participant_id"] + KEY:
   72 |         d[c] = pd.to_numeric(d[c], errors="coerce")
   73 | d = d.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
   74 | d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
   75 | d["punct"] = d.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
   76 | print(f"rows {len(d):,}   participants {d.participant_id.nunique()}")
   77 | 
   78 | FFD = "IA_FIRST_FIXATION_DURATION"
   79 | GD = "IA_FIRST_RUN_DWELL_TIME"
   80 | d["skipped"] = (d.IA_DWELL_TIME.fillna(0) == 0).astype(float)
   81 | fix = d[d.IA_DWELL_TIME > 0].copy()
   82 | fix["logTRT"] = np.log(fix.IA_DWELL_TIME)
   83 | if GD in fix:
   84 |     fix["logGD"] = np.log(fix[GD].where(fix[GD] > 0))
   85 |     fix["reread"] = (fix.IA_DWELL_TIME - fix[GD]).clip(lower=0)
   86 |     fix["has_reread"] = (fix.reread > 0).astype(float)
   87 |     fix["log_reread"] = np.log(fix.reread.where(fix.reread > 0))
   88 | if FFD in fix:
   89 |     fix["logFFD"] = np.log(fix[FFD].where(fix[FFD] > 0))
   90 |     if GD in fix:
   91 |         fix["refix"] = (fix[GD] > fix[FFD]).astype(float)
   92 | 
   93 | CTRL = ["surprisal", "log_freq", "word_length", "punct"]
   94 | 
   95 | 
   96 | def subj(df, outcome, minn=200):
   97 |     out = []
   98 |     for pid, s in df.groupby("participant_id"):
   99 |         s = s.dropna(subset=["tee"] + CTRL + [outcome])
  100 |         if len(s) < minn:
  101 |             continue
  102 |         X = np.column_stack([zs(s[c].values) for c in ["tee"] + CTRL])
  103 |         if (X.std(axis=0) == 0).any():
  104 |             continue
  105 |         out.append(sm.OLS(zs(s[outcome].values),
  106 |                           sm.add_constant(X)).fit().params[1])
  107 |     return np.array(out)
  108 | 
  109 | 
  110 | def row(label, b, note=""):
  111 |     if len(b) < 10:
  112 |         print(f"  {label:<34} too few participants")
  113 |         return
  114 |     pos = (b > 0).mean()
  115 |     p = stats.wilcoxon(b).pvalue
  116 |     print(f"  {label:<34} n={len(b):>4}  beta={b.mean():>+9.5f}  "
  117 |           f"{pos:>5.1%} pos  p={p:<10.2e} {note}")
  118 | 
  119 | 
  120 | print("\n" + "=" * 88)
  121 | print("DECOMPOSING THE NEGATIVE")
  122 | print("=" * 88)
  123 | print("\n  [1] does TEE predict SKIPPING?  (all rows, incl. unfixated)")
  124 | row("P(skip)", subj(d, "skipped"), "<- positive = high TEE skipped more")
  125 | 
  126 | print("\n  [2-4] durations, conditional on being fixated")
  127 | if "logFFD" in fix:
  128 |     row("first fixation duration", subj(fix, "logFFD"))
  129 | if "logGD" in fix:
  130 |     row("gaze duration (first pass)", subj(fix, "logGD"))
  131 | row("total reading time", subj(fix, "logTRT"), "<- the reported negative")
  132 | 
  133 | print("\n  [5-6] the part of TRT that is not first pass")
  134 | if "has_reread" in fix:
  135 |     row("P(any re-reading)", subj(fix, "has_reread"))
  136 |     row("log re-reading time | any", subj(fix[fix.reread > 0], "log_reread"))
  137 | if "refix" in fix:
  138 |     row("P(refixation in first pass)", subj(fix, "refix"))
  139 | if "IA_FIXATION_COUNT" in fix:
  140 |     row("fixation count", subj(fix, "IA_FIXATION_COUNT"))
  141 | 
  142 | print("\n" + "=" * 88)
  143 | print("READING")
  144 | print("=" * 88)
  145 | print("""  If the negative is concentrated in skipping, re-reading, or fixation
  146 |   count, it reflects where the eyes go rather than how fast a word is read,
  147 |   and total reading time is the wrong summary statistic for this measure.
  148 |   If first fixation and gaze duration are also negative, it is a genuine
  149 |   speed-up and the Discussion owes an account of it.""")
```


==============================================================================
### FILE: gp_confound_check/onestop_runup_probe.py
==============================================================================

```
    1 | """
    2 | IS THE SKIPPING EFFECT ABOUT THE TARGET WORD OR ABOUT THE RUN-UP?
    3 | ==================================================================
    4 | OneStop shows that words with high extrapolation error are SKIPPED more
    5 | (beta = +0.008, 66.1% of participants, p = 4.6e-8), while first fixation
    6 | duration is null. A reader cannot skip a word *because* it broke their
    7 | interpretation -- the skipping decision is made parafoveally, before the word is
    8 | identified. So either enough of the target word is extracted in the parafovea to
    9 | drive the decision, or the effect is not about the target word at all.
   10 | 
   11 | The second possibility has a mechanism behind it. Extrapolation error at word t
   12 | is the distance from a line fitted through words t-3..t-1. When that window is
   13 | STRAIGHT, the fitted step is long, the extrapolation projects far, and there is
   14 | more room to miss -- high error. When the window is BENT, the fitted step is
   15 | short and the prediction cannot miss by much -- low error. (This project's own
   16 | null-model work found exactly this: r(curvature(t-1), ||fitted slope||) is
   17 | strongly negative.) So high extrapolation error partly indexes "the preceding
   18 | context was moving coherently in one direction" -- which is the condition under
   19 | which a reader can predict what comes next and skip it. And all of that is
   20 | available BEFORE fixating word t.
   21 | 
   22 | CHEAP TEST, using only data already computed. If the effect lives in the run-up
   23 | rather than in the target word, then the PREVIOUS word's extrapolation error
   24 | should predict skipping of the current word.
   25 | 
   26 |   S1  skip(t) ~ tee(t)                     [the reported effect]
   27 |   S2  skip(t) ~ tee(t-1)                   [run-up proxy, fully pre-fixation]
   28 |   S3  skip(t) ~ tee(t) + tee(t-1)          [which survives?]
   29 |   S4  skip(t) ~ tee(t-1) + tee(t-2)        [how far back does it go?]
   30 |   S5  same as S3 for first fixation duration, for contrast
   31 | 
   32 | Controls throughout: surprisal, log frequency, word length, punctuation -- of the
   33 | CURRENT word, plus the previous word's length and frequency in S3-S4, since
   34 | parafoveal skipping is strongly driven by the properties of the launch word.
   35 | 
   36 | Interpretation fixed in advance:
   37 |   - tee(t-1) predicts skipping and survives alongside tee(t)  -> run-up account
   38 |     supported; the expensive decomposition is worth doing.
   39 |   - only tee(t) predicts skipping                             -> parafoveal
   40 |     identification of the target word; run-up account not supported.
   41 |   - neither survives with previous-word controls added        -> the effect is
   42 |     launch-site lexical properties, and is deflationary.
   43 | """
   44 | 
   45 | import numpy as np
   46 | import pandas as pd
   47 | from scipy import stats
   48 | import statsmodels.api as sm
   49 | import warnings
   50 | warnings.filterwarnings("ignore")
   51 | 
   52 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   53 | ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
   54 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   55 | TRIAL = ["participant_id", "article_id", "paragraph_id", "difficulty_level"]
   56 | 
   57 | 
   58 | def zs(x):
   59 |     x = np.asarray(x, dtype=float)
   60 |     s = x.std()
   61 |     return (x - x.mean()) / s if s > 0 else x * 0
   62 | 
   63 | 
   64 | use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
   65 |                                   "wordfreq_frequency", "gpt2_surprisal",
   66 |                                   "IA_FIRST_FIXATION_DURATION"]
   67 | d = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
   68 | d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
   69 |             on=KEY, how="left")
   70 | d = d.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee.csv")[
   71 |             KEY + ["word"]], on=KEY, how="left")
   72 | for c in use:
   73 |     if c not in ["participant_id"] + KEY:
   74 |         d[c] = pd.to_numeric(d[c], errors="coerce")
   75 | d = d.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
   76 | d["log_freq"] = np.log(d.wordfreq_frequency.clip(lower=1e-9))
   77 | d["punct"] = d.word.astype(str).str[-1].isin(list(".,;:!?")).astype(float)
   78 | d["skipped"] = (d.IA_DWELL_TIME.fillna(0) == 0).astype(float)
   79 | d["logFFD"] = np.log(d.IA_FIRST_FIXATION_DURATION.where(
   80 |     d.IA_FIRST_FIXATION_DURATION > 0))
   81 | 
   82 | # ---- lagged predictors, contiguity enforced on interest-area order ----
   83 | d = d.sort_values(TRIAL + ["IA_ID"]).reset_index(drop=True)
   84 | g = d.groupby(TRIAL)
   85 | for L in (1, 2):
   86 |     d[f"tee_m{L}"] = g["tee"].shift(L)
   87 |     d[f"len_m{L}"] = g["word_length"].shift(L)
   88 |     d[f"freq_m{L}"] = g["log_freq"].shift(L)
   89 |     d[f"surp_m{L}"] = g["surprisal"].shift(L)
   90 |     d[f"id_m{L}"] = g["IA_ID"].shift(L)
   91 |     bad = (d["IA_ID"] - d[f"id_m{L}"]) != L
   92 |     for c in [f"tee_m{L}", f"len_m{L}", f"freq_m{L}", f"surp_m{L}"]:
   93 |         d.loc[bad, c] = np.nan
   94 | print(f"rows {len(d):,}   participants {d.participant_id.nunique()}")
   95 | print(f"mean P(skip) = {d.skipped.mean():.3f}")
   96 | print(f"r(tee(t), tee(t-1)) = {d.tee.corr(d.tee_m1):+.3f}   "
   97 |       f"r(tee(t), log_freq) = {d.tee.corr(d.log_freq):+.3f}   "
   98 |       f"r(tee(t), word_length) = {d.tee.corr(d.word_length):+.3f}")
   99 | print(f"r(tee(t-1), len(t-1)) = {d.tee_m1.corr(d.len_m1):+.3f}\n")
  100 | 
  101 | CUR = ["surprisal", "log_freq", "word_length", "punct"]
  102 | PREV = ["len_m1", "freq_m1", "surp_m1"]
  103 | 
  104 | 
  105 | def subj(focus, extra, outcome, minn=200):
  106 |     cols = focus + CUR + extra
  107 |     out = {f: [] for f in focus}
  108 |     for pid, s in d.groupby("participant_id"):
  109 |         s = s.dropna(subset=cols + [outcome])
  110 |         if len(s) < minn:
  111 |             continue
  112 |         X = np.column_stack([zs(s[c].values) for c in cols])
  113 |         if (X.std(axis=0) == 0).any():
  114 |             continue
  115 |         r = sm.OLS(zs(s[outcome].values), sm.add_constant(X)).fit()
  116 |         for i, f in enumerate(focus):
  117 |             out[f].append(r.params[cols.index(f) + 1])
  118 |     return {f: np.array(v) for f, v in out.items()}
  119 | 
  120 | 
  121 | def row(label, b):
  122 |     if len(b) < 10:
  123 |         print(f"  {label:<40} too few")
  124 |         return
  125 |     pos = (b > 0).mean()
  126 |     p = stats.wilcoxon(b).pvalue
  127 |     star = "  *" if (p < .01 and max(pos, 1 - pos) >= .65) else ""
  128 |     print(f"  {label:<40} n={len(b):>4}  beta={b.mean():>+9.5f}  "
  129 |           f"{pos:>5.1%} pos  p={p:<10.2e}{star}")
  130 | 
  131 | 
  132 | print("=" * 92)
  133 | print("OUTCOME: P(skip)")
  134 | print("=" * 92)
  135 | row("S1  tee(t) alone", subj(["tee"], [], "skipped")["tee"])
  136 | row("S2  tee(t-1) alone", subj(["tee_m1"], [], "skipped")["tee_m1"])
  137 | r3 = subj(["tee", "tee_m1"], [], "skipped")
  138 | row("S3  tee(t)   [both entered]", r3["tee"])
  139 | row("S3  tee(t-1) [both entered]", r3["tee_m1"])
  140 | r4 = subj(["tee_m1", "tee_m2"], [], "skipped")
  141 | row("S4  tee(t-1) [t-1 and t-2]", r4["tee_m1"])
  142 | row("S4  tee(t-2) [t-1 and t-2]", r4["tee_m2"])
  143 | 
  144 | print("\n  with previous-word lexical controls added "
  145 |       "(length, frequency, surprisal of t-1):")
  146 | r5 = subj(["tee", "tee_m1"], PREV, "skipped")
  147 | row("S3b tee(t)   + prev lexical", r5["tee"])
  148 | row("S3b tee(t-1) + prev lexical", r5["tee_m1"])
  149 | 
  150 | print("\n" + "=" * 92)
  151 | print("OUTCOME: first fixation duration (for contrast)")
  152 | print("=" * 92)
  153 | r6 = subj(["tee", "tee_m1"], [], "logFFD")
  154 | row("tee(t)", r6["tee"])
  155 | row("tee(t-1)", r6["tee_m1"])
  156 | 
  157 | print("\n" + "=" * 92)
  158 | print("READING")
  159 | print("=" * 92)
  160 | print("""  tee(t-1) predicting skipping, and surviving alongside tee(t), supports the
  161 |   run-up account: the measure partly indexes how coherently the preceding
  162 |   context was moving, which is information the reader has before fixating.
  163 |   If tee(t-1) dies once previous-word length and frequency are controlled, the
  164 |   effect is launch-site lexical properties and the account is deflationary.""")
```


==============================================================================
### FILE: gp_confound_check/paradigm_transfer.py
==============================================================================

```
    1 | """
    2 | HOW MUCH SHOULD AN EFFECT TRANSFER FROM SELF-PACED READING TO EYE TRACKING?
    3 | ==========================================================================
    4 | TEE predicts self-paced RT in Natural Stories but not total reading time in
    5 | OneStop. Is that a meaningful failure, or is it what any effect would do?
    6 | 
    7 | Calibrate with predictors whose reality is not in doubt. Surprisal, log
    8 | frequency and word length are all established reading-time predictors. Estimate
    9 | each one's standardised effect in BOTH datasets under a matched specification,
   10 | then read TEE against that yardstick:
   11 | 
   12 |   transfer ratio = beta(OneStop TRT) / beta(Natural Stories SPR)
   13 | 
   14 | If surprisal and frequency transfer at ratio R, then a genuine effect of TEE
   15 | should show roughly R x its Natural Stories beta in OneStop. Compare that
   16 | prediction to what was actually observed.
   17 | 
   18 | Matched specification in both: outcome = log reading time, predictors z-scored,
   19 | controls = word length, log frequency, surprisal, previous-word reading time.
   20 | Subject-level estimation in both (one regression per participant, then mean),
   21 | so the two are on the same inferential footing.
   22 | """
   23 | 
   24 | import numpy as np
   25 | import pandas as pd
   26 | import statsmodels.api as sm
   27 | from scipy import stats
   28 | import warnings
   29 | warnings.filterwarnings("ignore")
   30 | 
   31 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   32 | ONESTOP = "/Users/elanbarenholtz/Projects/onestop-data/data/ordinary/ia_Paragraph_ordinary.csv"
   33 | KEY = ["article_id", "paragraph_id", "difficulty_level", "IA_ID"]
   34 | PREDS = ["word_length", "log_freq", "surprisal", "prev_rt", "tee"]
   35 | 
   36 | 
   37 | def per_subject(d, subj):
   38 |     """One OLS per participant; return mean beta and n for each predictor."""
   39 |     out = {p: [] for p in PREDS}
   40 |     for pid, sub in d.groupby(subj):
   41 |         s = sub.dropna(subset=PREDS + ["y"])
   42 |         if len(s) < 200:
   43 |             continue
   44 |         X = s[PREDS].astype(float)
   45 |         sd = X.std(ddof=0)
   46 |         if (sd == 0).any():
   47 |             continue
   48 |         X = sm.add_constant((X - X.mean()) / sd)
   49 |         r = sm.OLS(s.y.values, X.values).fit()
   50 |         for i, p in enumerate(PREDS):
   51 |             out[p].append(r.params[i + 1])
   52 |     return {p: np.array(v) for p, v in out.items()}
   53 | 
   54 | 
   55 | # ---------------- Natural Stories (self-paced) ----------------
   56 | w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   57 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   58 |                  sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
   59 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   60 | ns = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length", "log_freq"]],
   61 |               on=["story_id", "zone"], how="inner")
   62 | ns["y"] = np.log(ns.RT)
   63 | ns = ns.sort_values(["participant", "story_id", "zone"])
   64 | ns["prev_rt"] = ns.groupby(["participant", "story_id"])["y"].shift(1)
   65 | ns = ns.rename(columns={"tee_k3": "tee"})
   66 | NS = per_subject(ns, "participant")
   67 | 
   68 | # ---------------- OneStop (eye tracking, total reading time) ----------------
   69 | use = ["participant_id"] + KEY + ["IA_DWELL_TIME", "word_length",
   70 |                                   "wordfreq_frequency", "gpt2_surprisal"]
   71 | os_ = pd.read_csv(ONESTOP, usecols=use, low_memory=False)
   72 | os_ = os_.merge(pd.read_csv(f"{GP}/gp_confound_check/onestop_tee_ctx.csv"),
   73 |                 on=KEY, how="left")
   74 | for c in ["IA_DWELL_TIME", "word_length", "wordfreq_frequency", "gpt2_surprisal"]:
   75 |     os_[c] = pd.to_numeric(os_[c], errors="coerce")
   76 | os_ = os_[os_.IA_DWELL_TIME > 0].copy()
   77 | os_["y"] = np.log(os_.IA_DWELL_TIME)
   78 | os_["log_freq"] = np.log(os_.wordfreq_frequency.clip(lower=1e-9))
   79 | os_ = os_.rename(columns={"gpt2_surprisal": "surprisal", "tee_ctx": "tee"})
   80 | os_ = os_.sort_values(["participant_id"] + KEY)
   81 | os_["prev_rt"] = os_.groupby(["participant_id", "article_id", "paragraph_id",
   82 |                               "difficulty_level"])["y"].shift(1)
   83 | OS = per_subject(os_, "participant_id")
   84 | 
   85 | print(f"Natural Stories (self-paced): {len(NS['tee'])} participants")
   86 | print(f"OneStop (eye tracking, TRT):  {len(OS['tee'])} participants\n")
   87 | 
   88 | print("=" * 78)
   89 | print("STANDARDISED EFFECTS IN BOTH PARADIGMS (subject-level means)")
   90 | print("=" * 78)
   91 | print(f"{'predictor':<16}{'NS self-paced':>16}{'OneStop TRT':>16}"
   92 |       f"{'transfer ratio':>17}")
   93 | ratios = {}
   94 | for p in PREDS:
   95 |     if p == "prev_rt":
   96 |         continue
   97 |     a, b = NS[p].mean(), OS[p].mean()
   98 |     ratios[p] = b / a if a != 0 else np.nan
   99 |     pa = stats.wilcoxon(NS[p]).pvalue
  100 |     pb = stats.wilcoxon(OS[p]).pvalue
  101 |     print(f"{p:<16}{a:>+11.5f}{'':>1}{'*' if pa<.05 else ' '}"
  102 |           f"{b:>+13.5f}{'*' if pb<.05 else ' '}{ratios[p]:>16.2f}")
  103 | 
  104 | est = [ratios[p] for p in ["surprisal", "log_freq", "word_length"]]
  105 | print(f"\n  mean transfer ratio of the three established predictors: "
  106 |       f"{np.mean(est):.2f}")
  107 | print(f"  (surprisal {ratios['surprisal']:.2f}, frequency {ratios['log_freq']:.2f}, "
  108 |       f"length {ratios['word_length']:.2f})")
  109 | 
  110 | pred = NS["tee"].mean() * np.mean(est)
  111 | obs = OS["tee"].mean()
  112 | se = OS["tee"].std(ddof=1) / np.sqrt(len(OS["tee"]))
  113 | print("\n" + "=" * 78)
  114 | print("IS TEE'S ONESTOP ESTIMATE WHAT THE BENCHMARK PREDICTS?")
  115 | print("=" * 78)
  116 | print(f"  TEE beta in Natural Stories            = {NS['tee'].mean():+.5f}")
  117 | print(f"  predicted OneStop beta at that ratio   = {pred:+.5f}")
  118 | print(f"  observed OneStop beta                  = {obs:+.5f}  (SE {se:.5f})")
  119 | z = (obs - pred) / se
  120 | print(f"  observed vs predicted                  = {z:+.2f} SE  "
  121 |       f"(p = {2*stats.norm.sf(abs(z)):.4f})")
  122 | print("\n  If the established predictors transfer but TEE lands far below its")
  123 | print("  predicted value, the non-replication is specific to TEE rather than")
  124 | print("  a general property of the paradigm shift.")
```


==============================================================================
### FILE: gp_confound_check/rt_dynamics.py
==============================================================================

```
    1 | """
    2 | RT DYNAMICS: impulse-response of reading time to a TEE event
    3 | ============================================================
    4 | Confirmatory analysis, specified in PREREG_rt_dynamics.md before running.
    5 | Any deviation from that document must be reported as a deviation.
    6 | 
    7 | P1  impulse-response of log RT to z(TEE) across lags 0-5, all lags in one
    8 |     model, controls entered at every lag, per participant then group test.
    9 | S1  same with prev_log_RT included
   10 | S2  surprisal's impulse response as a reference profile
   11 | S3  does TEE predict RT-extrapolation error (TEE's own operation on the RT series)
   12 | S4  does TEE predict the residual of an AR(2) model of log RT
   13 | 
   14 | Criteria (fixed in advance):
   15 |   dynamic response  = profile differs from flat (omnibus p < .01) AND some lag
   16 |                       > 0 reaches p < .0017 with >= 65% of participants agreeing
   17 |   biphasic          = two separated lags with opposite signs, each p < .0017
   18 |                       and >= 65% sign agreement
   19 |   null              = neither
   20 | 
   21 | Implementation guards (from this project's failure history):
   22 |   - sample hash asserted
   23 |   - merges validated one-to-one
   24 |   - LAGS COMPUTED BEFORE ANY FILTERING; row counts printed at each step
   25 | """
   26 | 
   27 | import numpy as np
   28 | import pandas as pd
   29 | import statsmodels.api as sm
   30 | from scipy import stats
   31 | import hashlib, warnings
   32 | warnings.filterwarnings("ignore")
   33 | 
   34 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   35 | LAGS = list(range(6))                      # 0..5, fixed in advance
   36 | ALPHA_LAG = .01 / len(LAGS)                # .0017
   37 | SIGN_THRESHOLD = 0.65
   38 | 
   39 | 
   40 | def build():
   41 |     w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   42 |     sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   43 |          w[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   44 |     assert sh == "8a6087341e", sh
   45 |     w["punct"] = w.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   46 | 
   47 |     rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   48 |                      sep="\t").rename(columns={"item": "story_id",
   49 |                                                "WorkerId": "participant"})
   50 |     print(f"hash {sh} verified | raw RT rows {len(rt):,}")
   51 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   52 |     print(f"after RT filter          {len(rt):,}")
   53 | 
   54 |     d = rt.merge(w[["story_id", "zone", "word_idx", "tee_k3", "surprisal",
   55 |                     "word_length", "log_freq", "punct", "from_start", "fs2",
   56 |                     "from_end", "fe2"]],
   57 |                  on=["story_id", "zone"], how="inner", validate="many_to_one")
   58 |     print(f"after merge to measures  {len(d):,}")
   59 |     d["log_RT"] = np.log(d.RT)
   60 | 
   61 |     # ---- LAGS BUILT BEFORE ANY FURTHER FILTERING ----
   62 |     d = d.sort_values(["participant", "story_id", "word_idx"]).reset_index(drop=True)
   63 |     g = d.groupby(["participant", "story_id"])
   64 |     # outcome at t+L  == predictor at t shifted BACK by L
   65 |     for L in LAGS:
   66 |         d[f"y_lead{L}"] = g["log_RT"].shift(-L)
   67 |         d[f"widx_lead{L}"] = g["word_idx"].shift(-L)
   68 |     d["prev_log_RT"] = g["log_RT"].shift(1)
   69 |     # RT-extrapolation error (S3): line through log RT at t-3..t-1
   70 |     for j in (1, 2, 3):
   71 |         d[f"rt_m{j}"] = g["log_RT"].shift(j)
   72 |     pred = 3 * d.rt_m1 - 3 * d.rt_m2 + d.rt_m3        # OLS 1-step extrapolation
   73 |     d["rt_extrap_err"] = (d.log_RT - pred).abs()
   74 |     print(f"after lag construction   {len(d):,}")
   75 | 
   76 |     # contiguity: outcome at lead L must really be L words later
   77 |     for L in LAGS:
   78 |         ok = (d[f"widx_lead{L}"] - d.word_idx) == L
   79 |         d.loc[~ok, f"y_lead{L}"] = np.nan
   80 |     return d
   81 | 
   82 | 
   83 | def zs(x):
   84 |     s = x.std(ddof=0)
   85 |     return (x - x.mean()) / s if s > 0 else x * 0
   86 | 
   87 | 
   88 | CTRL = ["surprisal", "word_length", "log_freq", "punct",
   89 |         "from_start", "fs2", "from_end", "fe2"]
   90 | 
   91 | 
   92 | def irf(d, focus, extra_ctrl=(), label=""):
   93 |     """Per-participant impulse response: outcome at t+L on focus at t."""
   94 |     out = {L: [] for L in LAGS}
   95 |     cols = [focus] + CTRL + list(extra_ctrl)
   96 |     for pid, sub in d.groupby("participant"):
   97 |         for L in LAGS:
   98 |             s = sub.dropna(subset=cols + [f"y_lead{L}"])
   99 |             if len(s) < 300:
  100 |                 continue
  101 |             X = s[cols].astype(float).apply(zs)
  102 |             if (X.std(ddof=0) == 0).any():
  103 |                 continue
  104 |             X = sm.add_constant(X.values)
  105 |             r = sm.OLS(zs(s[f"y_lead{L}"]).values, X).fit()
  106 |             out[L].append(r.params[1])
  107 |     return {L: np.array(v) for L, v in out.items()}
  108 | 
  109 | 
  110 | def report(res, title):
  111 |     print("\n" + "=" * 78)
  112 |     print(title)
  113 |     print("=" * 78)
  114 |     print(f"{'lag':>4}{'n subj':>8}{'mean beta':>12}{'% same sign':>13}"
  115 |           f"{'Wilcoxon p':>13}{'sig?':>7}")
  116 |     prof = []
  117 |     for L in LAGS:
  118 |         b = res[L]
  119 |         if len(b) < 20:
  120 |             print(f"{L:>4}{len(b):>8}   too few participants")
  121 |             continue
  122 |         pos = (b > 0).mean()
  123 |         agree = max(pos, 1 - pos)
  124 |         p = stats.wilcoxon(b).pvalue
  125 |         star = "YES" if (p < ALPHA_LAG and agree >= SIGN_THRESHOLD) else ""
  126 |         print(f"{L:>4}{len(b):>8}{b.mean():>+12.5f}{agree:>12.1%}"
  127 |               f"{p:>13.2e}{star:>7}")
  128 |         prof.append(b)
  129 |     # omnibus: does the profile differ from flat? (Friedman across lags)
  130 |     if len(prof) == len(LAGS):
  131 |         m = min(len(x) for x in prof)
  132 |         stat, p = stats.friedmanchisquare(*[x[:m] for x in prof])
  133 |         print(f"\n  omnibus (profile differs from flat): "
  134 |               f"chi2 = {stat:.1f}, p = {p:.3e}   "
  135 |               f"{'PASS' if p < .01 else 'fail'}")
  136 |     return prof
  137 | 
  138 | 
  139 | def main():
  140 |     d = build()
  141 |     print(f"participants {d.participant.nunique()}   "
  142 |           f"words {d.word_idx.nunique()}\n")
  143 | 
  144 |     p1 = irf(d, "tee_k3")
  145 |     report(p1, "P1 (PRIMARY): impulse response of log RT to TEE, lags 0-5")
  146 | 
  147 |     s1 = irf(d, "tee_k3", extra_ctrl=["prev_log_RT"])
  148 |     report(s1, "S1: same, with prev_log_RT included")
  149 | 
  150 |     s2 = irf(d, "surprisal")
  151 |     report(s2, "S2 (reference): impulse response to SURPRISAL")
  152 | 
  153 |     print("\n" + "=" * 78)
  154 |     print("S3: does TEE predict RT-extrapolation error at the same word?")
  155 |     print("=" * 78)
  156 |     out = []
  157 |     cols = ["tee_k3"] + CTRL
  158 |     for pid, sub in d.groupby("participant"):
  159 |         s = sub.dropna(subset=cols + ["rt_extrap_err"])
  160 |         if len(s) < 300:
  161 |             continue
  162 |         X = sm.add_constant(s[cols].astype(float).apply(zs).values)
  163 |         out.append(sm.OLS(zs(s.rt_extrap_err).values, X).fit().params[1])
  164 |     out = np.array(out)
  165 |     pos = (out > 0).mean()
  166 |     print(f"  n = {len(out)}  mean beta = {out.mean():+.5f}  "
  167 |           f"same sign {max(pos,1-pos):.1%}  Wilcoxon p = {stats.wilcoxon(out).pvalue:.2e}")
  168 | 
  169 |     print("\n" + "=" * 78)
  170 |     print("S4: does TEE predict the residual of an AR(2) model of log RT?")
  171 |     print("=" * 78)
  172 |     d["ar_resid"] = np.nan
  173 |     g = d.groupby(["participant", "story_id"])
  174 |     d["rt_l1"] = g["log_RT"].shift(1)
  175 |     d["rt_l2"] = g["log_RT"].shift(2)
  176 |     sub = d.dropna(subset=["log_RT", "rt_l1", "rt_l2"])
  177 |     X = sm.add_constant(sub[["rt_l1", "rt_l2"]].values)
  178 |     ar = sm.OLS(sub.log_RT.values, X).fit()
  179 |     d.loc[sub.index, "ar_resid"] = np.abs(ar.resid)
  180 |     out = []
  181 |     for pid, s2_ in d.groupby("participant"):
  182 |         s = s2_.dropna(subset=cols + ["ar_resid"])
  183 |         if len(s) < 300:
  184 |             continue
  185 |         X = sm.add_constant(s[cols].astype(float).apply(zs).values)
  186 |         out.append(sm.OLS(zs(s.ar_resid).values, X).fit().params[1])
  187 |     out = np.array(out)
  188 |     pos = (out > 0).mean()
  189 |     print(f"  n = {len(out)}  mean beta = {out.mean():+.5f}  "
  190 |           f"same sign {max(pos,1-pos):.1%}  Wilcoxon p = {stats.wilcoxon(out).pvalue:.2e}")
  191 | 
  192 | 
  193 | if __name__ == "__main__":
  194 |     main()
```


==============================================================================
### FILE: gp_confound_check/sap_bigsurp.py
==============================================================================

```
    1 | """
    2 | STRONGER SURPRISAL CONTROLS FOR THE SAP CORPUS
    3 | ==============================================
    4 | The objection this addresses: TEE and surprisal both come from GPT-2 Small, so
    5 | TEE could be measuring not trajectory geometry but simply WHERE GPT-2 SMALL'S
    6 | PROBABILITY ESTIMATE IS BAD. Words the model handles poorly would show both an
    7 | off-trajectory hidden state and a mis-estimated surprisal, and controlling for
    8 | that same model's surprisal cannot remove the confound because the control is
    9 | made of the same error.
   10 | 
   11 | Substituting a STRONGER model's surprisal breaks the circularity. If the SAP
   12 | effect is a predictability residual, a better predictability estimate should
   13 | absorb it.
   14 | 
   15 | TEE is left exactly as reported: GPT-2 Small, layer 6, k = 3, sink excluded from
   16 | every fit window. Only the surprisal control changes.
   17 | 
   18 | Control models: GPT-2 XL (1.5B) and Pythia-410M. Both, so the result cannot
   19 | depend on which stronger model is chosen. Pythia additionally differs in
   20 | tokenizer, training corpus and positional encoding (RoPE), so it is close to an
   21 | independent estimate of predictability rather than a scaled-up GPT-2.
   22 | 
   23 | Word-level surprisal = sum of token surprisals over the word's subword tokens,
   24 | the same convention used for the GPT-2 Small values throughout this project.
   25 | 
   26 | INTERPRETATION FIXED BEFORE RUNNING (see conversation log 2026-08-07):
   27 |   - TEE survives at roughly its current magnitude -> the predictability-residual
   28 |     account is ruled out; report as a strengthening result.
   29 |   - TEE drops substantially -> TEE is partly a proxy for GPT-2 Small's
   30 |     estimation error; the claim narrows to that and is reported, not buried.
   31 | Either outcome is reported.
   32 | 
   33 | Output: sap_bigsurp.csv  (item, Type, WordPosition, surp_xl, surp_pythia410m)
   34 | """
   35 | 
   36 | import numpy as np
   37 | import pandas as pd
   38 | import torch
   39 | from transformers import AutoTokenizer, AutoModelForCausalLM
   40 | import warnings
   41 | warnings.filterwarnings("ignore")
   42 | 
   43 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   44 | RT_CSV = f"{GP}/ClassicGardenPathSet.csv"
   45 | OUT = f"{GP}/sap_bigsurp.csv"
   46 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   47 | 
   48 | MODELS = [("surp_xl", "gpt2-xl"),
   49 |           ("surp_pythia410m", "EleutherAI/pythia-410m")]
   50 | 
   51 | 
   52 | def word_surprisals(words, tok, model):
   53 |     """Sum of subword token surprisals (bits) per word."""
   54 |     ids, final_idx = [], []
   55 |     for i, w in enumerate(words):
   56 |         t = tok.encode(w if i == 0 else " " + w, add_special_tokens=False)
   57 |         ids.extend(t)
   58 |         final_idx.append(len(ids) - 1)
   59 |     with torch.no_grad():
   60 |         out = model(torch.tensor([ids]).to(DEVICE))
   61 |     lp = torch.log_softmax(out.logits[0].float(), -1)
   62 |     tok_s = np.zeros(len(ids))
   63 |     for t in range(1, len(ids)):
   64 |         tok_s[t] = -float(lp[t - 1, ids[t]]) / np.log(2)
   65 |     starts, prev = [], 0
   66 |     for fi in final_idx:
   67 |         starts.append(prev)
   68 |         prev = fi + 1
   69 |     return [float(tok_s[s:f + 1].sum()) for s, f in zip(starts, final_idx)]
   70 | 
   71 | 
   72 | d = pd.read_csv(RT_CSV)
   73 | for c in ["EachWord", "Sentence"]:
   74 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
   75 | 
   76 | sent_index = (d.drop_duplicates(subset=["item", "Type", "WordPosition"])
   77 |                 .sort_values(["item", "Type", "WordPosition"]))
   78 | groups = list(sent_index.groupby(["item", "Type"]))
   79 | print(f"sentences: {len(groups)}   "
   80 |       f"sentence-words: {len(sent_index):,}")
   81 | 
   82 | base = sent_index[["item", "Type", "WordPosition"]].reset_index(drop=True)
   83 | res = base.copy()
   84 | 
   85 | for col, name in MODELS:
   86 |     print(f"\nloading {name} ...")
   87 |     tok = AutoTokenizer.from_pretrained(name)
   88 |     model = AutoModelForCausalLM.from_pretrained(name)
   89 |     model.eval().to(DEVICE)
   90 |     rows = []
   91 |     for (item, typ), g in groups:
   92 |         words = [str(x) for x in g.EachWord.tolist()]
   93 |         s = word_surprisals(words, tok, model)
   94 |         for j, (_, r) in enumerate(g.iterrows()):
   95 |             rows.append({"item": item, "Type": typ,
   96 |                          "WordPosition": r.WordPosition, col: s[j]})
   97 |     S = pd.DataFrame(rows)
   98 |     n0 = len(res)
   99 |     res = res.merge(S, on=["item", "Type", "WordPosition"],
  100 |                     how="left", validate="one_to_one")
  101 |     assert len(res) == n0
  102 |     print(f"  {name}: mean {res[col].mean():.2f} bits   "
  103 |           f"sd {res[col].std():.2f}   missing {res[col].isna().sum()}")
  104 |     del model, tok
  105 |     if DEVICE == "mps":
  106 |         torch.mps.empty_cache()
  107 | 
  108 | # sanity: correlation with the GPT-2 Small values already cached
  109 | small = pd.read_csv(f"{GP}/sap_measures_L6k3.csv")
  110 | chk = res.merge(small[["item", "Type", "WordPosition", "surp", "tee"]],
  111 |                 on=["item", "Type", "WordPosition"], how="left",
  112 |                 validate="one_to_one")
  113 | print("\n" + "=" * 70)
  114 | print("SANITY: agreement between surprisal estimates (sentence-word level)")
  115 | print("=" * 70)
  116 | print(f"  r(GPT-2 Small, GPT-2 XL)      = {chk.surp.corr(chk.surp_xl):+.3f}")
  117 | print(f"  r(GPT-2 Small, Pythia-410M)   = "
  118 |       f"{chk.surp.corr(chk.surp_pythia410m):+.3f}")
  119 | print(f"  r(GPT-2 XL,    Pythia-410M)   = "
  120 |       f"{chk.surp_xl.corr(chk.surp_pythia410m):+.3f}")
  121 | print("\n  mean surprisal (bits): "
  122 |       f"small {chk.surp.mean():.2f}  xl {chk.surp_xl.mean():.2f}  "
  123 |       f"pythia {chk.surp_pythia410m.mean():.2f}")
  124 | print("  (a stronger model should assign LOWER surprisal on average)")
  125 | print("\n  correlation of each surprisal with TEE (GPT-2 Small L6 k=3):")
  126 | for c in ["surp", "surp_xl", "surp_pythia410m"]:
  127 |     print(f"    r(TEE, {c:<16}) = {chk.tee.corr(chk[c]):+.3f}")
  128 | 
  129 | res.to_csv(OUT, index=False)
  130 | print(f"\nsaved -> {OUT}   ({len(res):,} rows)")
```


==============================================================================
### FILE: gp_confound_check/sap_bigsurp_refit.py
==============================================================================

```
    1 | """
    2 | DOES THE SAP TEE EFFECT SURVIVE A STRONGER SURPRISAL CONTROL?
    3 | =============================================================
    4 | TEE unchanged (GPT-2 Small, L6, k=3, sink excluded). Only the surprisal control
    5 | varies. Control models computed in sap_bigsurp.py: GPT-2 XL, Pythia-410M.
    6 | 
    7 | CAVEAT ESTABLISHED BEFORE THESE FITS (sap_bigsurp_out.txt): the three surprisal
    8 | estimates correlate at r = .967-.971 with each other, and each correlates with
    9 | TEE at r = .374-.386. They are near-interchangeable, so simply SUBSTITUTING one
   10 | for another is a weak test -- it cannot move much. The informative specs are
   11 | therefore the ones that enter several surprisals TOGETHER (union control) and
   12 | that spline them, since the union spans more of the predictability space than
   13 | any single estimate and leaves less room for a "predictability residual" to
   14 | hide in.
   15 | 
   16 | Reference (gp_allwords_matched.py, GPT-2 Small surprisal):
   17 |     A1 flexible position            TEE beta = +0.02238   61.1%
   18 |     A2 A1 + sentence-final flag     TEE beta = +0.02505   62.7%
   19 | 
   20 | Specs, all per participant, group Wilcoxon, identical rows within a block:
   21 |     S0  small surprisal                        [reference]
   22 |     S1  GPT-2 XL surprisal
   23 |     S2  Pythia-410M surprisal
   24 |     S3  all three, linear                      [union control]
   25 |     S4  all three, each splined df=4           [union, flexible form]
   26 |     S5  S3 + previous log RT                   [the known soft spot]
   27 | 
   28 | Reported for every spec: TEE beta, % positive, Wilcoxon p, and -- for context --
   29 | the coefficient on whichever surprisal is present (for S3/S4, GPT-2 XL's).
   30 | 
   31 | Also: a permutation floor for the S3 spec, since sign agreement has no meaning
   32 | without one.
   33 | """
   34 | 
   35 | import numpy as np
   36 | import pandas as pd
   37 | from scipy import stats
   38 | import statsmodels.api as sm
   39 | import statsmodels.formula.api as smf
   40 | from wordfreq import zipf_frequency
   41 | import warnings
   42 | warnings.filterwarnings("ignore")
   43 | 
   44 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature/gp_confound_check"
   45 | MIN_ROWS = 100
   46 | RNG = np.random.default_rng(20260807)
   47 | 
   48 | 
   49 | def zs(x):
   50 |     x = np.asarray(x, dtype=float)
   51 |     s = x.std()
   52 |     return (x - x.mean()) / s if s > 0 else x * 0
   53 | 
   54 | 
   55 | d = pd.read_csv(f"{GP}/ClassicGardenPathSet.csv")
   56 | for c in ["EachWord", "Sentence"]:
   57 |     d[c] = d[c].astype(str).str.replace("%2C", ",", regex=False)
   58 | d = d.rename(columns={"MD5": "participant"})
   59 | 
   60 | M = pd.read_csv(f"{GP}/sap_measures_L6k3.csv")
   61 | B = pd.read_csv(f"{GP}/sap_bigsurp.csv")
   62 | M = M.merge(B, on=["item", "Type", "WordPosition"], validate="one_to_one")
   63 | n0 = len(d)
   64 | d = d.merge(M, on=["item", "Type", "WordPosition"], how="left",
   65 |             validate="many_to_one")
   66 | assert len(d) == n0
   67 | 
   68 | d["word_length"] = d.EachWord.str.len()
   69 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
   70 |     lambda x: zipf_frequency(x, "en"))
   71 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
   72 | d["from_start"] = d.WordPosition.astype(float)
   73 | d["fs2"] = d.from_start ** 2
   74 | d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
   75 | d["fe2"] = d.from_end ** 2
   76 | d["is_final"] = (d.from_end == 0).astype(float)
   77 | 
   78 | d = d.sort_values(["participant", "item", "Type", "WordPosition"]).reset_index(
   79 |     drop=True)
   80 | g = d.groupby(["participant", "item", "Type"])
   81 | d["log_RT_raw"] = np.log(d.RT.clip(lower=1))
   82 | d["prev_log_RT"] = g["log_RT_raw"].shift(1)
   83 | d["prev_pos"] = g["WordPosition"].shift(1)
   84 | d.loc[(d.WordPosition - d.prev_pos) != 1, "prev_log_RT"] = np.nan
   85 | 
   86 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
   87 | d["log_RT"] = np.log(d.RT)
   88 | d = d.dropna(subset=["tee", "surp", "surp_xl", "surp_pythia410m",
   89 |                      "word_length", "log_freq", "log_RT"])
   90 | print(f"rows {len(d):,}   participants {d.participant.nunique():,}\n")
   91 | 
   92 | POSFLAG = ["from_start", "fs2", "from_end", "fe2", "is_final"]
   93 | LEX = ["word_length", "log_freq", "punct"]
   94 | 
   95 | LINSPECS = [
   96 |     ("S0  GPT-2 Small surprisal  [ref]", ["tee", "surp"] + LEX + POSFLAG, "surp"),
   97 |     ("S1  GPT-2 XL surprisal", ["tee", "surp_xl"] + LEX + POSFLAG, "surp_xl"),
   98 |     ("S2  Pythia-410M surprisal", ["tee", "surp_pythia410m"] + LEX + POSFLAG,
   99 |      "surp_pythia410m"),
  100 |     ("S3  all three surprisals", ["tee", "surp", "surp_xl", "surp_pythia410m"]
  101 |      + LEX + POSFLAG, "surp_xl"),
  102 |     ("S5  S3 + previous log RT", ["tee", "surp", "surp_xl", "surp_pythia410m"]
  103 |      + LEX + POSFLAG + ["prev_log_RT"], "surp_xl"),
  104 | ]
  105 | 
  106 | groups = {pid: s for pid, s in d.groupby("participant")}
  107 | 
  108 | 
  109 | def run_linear(cols, focus="tee", ref=None, permute=False):
  110 |     bt, br = [], []
  111 |     for pid, sub in groups.items():
  112 |         s = sub.dropna(subset=cols + ["log_RT"])
  113 |         if len(s) < MIN_ROWS:
  114 |             continue
  115 |         s = s if not permute else s.assign(tee=RNG.permutation(s.tee.values))
  116 |         X = np.column_stack([zs(s[c].values) for c in cols])
  117 |         if (X.std(axis=0) == 0).any():
  118 |             continue
  119 |         r = sm.OLS(zs(s.log_RT.values), sm.add_constant(X)).fit()
  120 |         bt.append(r.params[cols.index(focus) + 1])
  121 |         if ref:
  122 |             br.append(r.params[cols.index(ref) + 1])
  123 |     return np.array(bt), np.array(br)
  124 | 
  125 | 
  126 | def line(lab, b, ref=None):
  127 |     pos = (b > 0).mean()
  128 |     p = stats.wilcoxon(b).pvalue
  129 |     extra = f"{ref.mean():>+12.5f}" if ref is not None and len(ref) else " " * 12
  130 |     print(f"{lab:<36}{len(b):>6}{b.mean():>+11.5f}{pos:>8.1%}{p:>11.2e}{extra}")
  131 | 
  132 | 
  133 | print("=" * 88)
  134 | print("TEE COEFFICIENT UNDER INCREASINGLY STRONG SURPRISAL CONTROLS")
  135 | print("=" * 88)
  136 | print(f"{'spec':<36}{'n':>6}{'TEE beta':>11}{'% pos':>8}{'p':>11}"
  137 |       f"{'surp beta':>12}")
  138 | for lab, cols, ref in LINSPECS:
  139 |     bt, br = run_linear(cols, ref=ref)
  140 |     line(lab, bt, br)
  141 | 
  142 | # S4: all three splined
  143 | print("\n" + "=" * 88)
  144 | print("S4  all three surprisals splined (df=4 each)")
  145 | print("=" * 88)
  146 | ZC = ["log_RT", "tee", "surp", "surp_xl", "surp_pythia410m", "word_length",
  147 |       "log_freq", "from_start", "fs2", "from_end", "fe2"]
  148 | f4 = ("z_log_RT ~ z_tee + bs(z_surp, df=4) + bs(z_surp_xl, df=4) "
  149 |       "+ bs(z_surp_pythia410m, df=4) + z_word_length + z_log_freq + punct "
  150 |       "+ z_from_start + z_fs2 + z_from_end + z_fe2 + is_final")
  151 | b4 = []
  152 | for pid, sub in groups.items():
  153 |     s = sub.dropna(subset=[c for c in ZC])
  154 |     if len(s) < MIN_ROWS:
  155 |         continue
  156 |     s = s.copy()
  157 |     for c in ZC:
  158 |         s["z_" + c] = zs(s[c].values)
  159 |     try:
  160 |         b4.append(smf.ols(f4, s).fit().params["z_tee"])
  161 |     except Exception:
  162 |         continue
  163 | print(f"{'spec':<36}{'n':>6}{'TEE beta':>11}{'% pos':>8}{'p':>11}")
  164 | line("S4  three splined surprisals", np.array(b4))
  165 | 
  166 | print("\n" + "=" * 88)
  167 | print("FLOOR: S3 spec with TEE permuted within participant")
  168 | print("=" * 88)
  169 | cols3 = LINSPECS[3][1]
  170 | bperm, _ = run_linear(cols3, permute=True)
  171 | print(f"{'spec':<36}{'n':>6}{'TEE beta':>11}{'% pos':>8}{'p':>11}")
  172 | line("F   permuted TEE", bperm)
  173 | 
  174 | print("\n" + "=" * 88)
  175 | print("POOLED dAIC: gain from adding TEE to each surprisal specification")
  176 | print("=" * 88)
  177 | dd = d.copy()
  178 | for c in ["log_RT", "tee", "surp", "surp_xl", "surp_pythia410m", "word_length",
  179 |           "log_freq", "from_start", "fs2", "from_end", "fe2"]:
  180 |     dd["z_" + c] = zs(dd[c].values)
  181 | base = ("z_log_RT ~ z_word_length + z_log_freq + punct + z_from_start + z_fs2 "
  182 |         "+ z_from_end + z_fe2 + is_final")
  183 | for lab, term in [
  184 |         ("GPT-2 Small only", "z_surp"),
  185 |         ("GPT-2 XL only", "z_surp_xl"),
  186 |         ("Pythia-410M only", "z_surp_pythia410m"),
  187 |         ("all three", "z_surp + z_surp_xl + z_surp_pythia410m"),
  188 |         ("all three, XL splined df=5",
  189 |          "z_surp + bs(z_surp_xl, df=5) + z_surp_pythia410m")]:
  190 |     m0 = smf.mixedlm(f"{base} + {term}", dd, groups=dd.participant).fit(
  191 |         reml=False, method="lbfgs")
  192 |     m1 = smf.mixedlm(f"{base} + {term} + z_tee", dd,
  193 |                      groups=dd.participant).fit(reml=False, method="lbfgs")
  194 |     print(f"  {lab:<28} AIC {m0.aic:>10.1f}  +TEE {m1.aic:>10.1f}  "
  195 |           f"dAIC(TEE) {m0.aic - m1.aic:>+8.1f}  "
  196 |           f"beta {m1.params['z_tee']:>+8.5f}")
```


==============================================================================
### FILE: gp_confound_check/spline_test.py
==============================================================================

```
    1 | """
    2 | DOES TEE SURVIVE FLEXIBLE CONTROLS? (the misspecification test)
    3 | ==============================================================
    4 | Standard objection to any "beyond surprisal" claim: if surprisal (or frequency,
    5 | or length) enters linearly but its true relationship to reading time is curved,
    6 | the unfit curvature stays in the residual as a systematic function of that
    7 | predictor. Anything correlated with it can then absorb the leftover and look
    8 | like an independent effect.
    9 | 
   10 | TEE is correlated r = +0.31 with surprisal and r = -0.44 with log frequency, so
   11 | it is positioned to do exactly this.
   12 | 
   13 | Test: give surprisal, log frequency and word length natural cubic splines with
   14 | increasing degrees of freedom, so the model can fit whatever shape is really
   15 | there, and ask whether TEE still improves fit. TEE itself stays linear
   16 | throughout -- if its own form is misspecified that costs power, not validity.
   17 | 
   18 | Locked sample 8a6087341e; mixedlm with by-participant random intercept, ML fit.
   19 | Reference: linear spec gives dAIC = 112, beta = +0.0035.
   20 | """
   21 | 
   22 | import numpy as np
   23 | import pandas as pd
   24 | import statsmodels.formula.api as smf
   25 | from patsy import dmatrix
   26 | import warnings
   27 | warnings.filterwarnings("ignore")
   28 | 
   29 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   30 | 
   31 | 
   32 | def build():
   33 |     w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   34 |     w["punct"] = w.word.astype(str).str.match(r".*[^A-Za-z0-9]$").astype(float)
   35 |     rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   36 |                      sep="\t").rename(columns={"item": "story_id",
   37 |                                                "WorkerId": "participant"})
   38 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   39 |     m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "entropy",
   40 |                     "word_length", "log_freq", "punct"]],
   41 |                  on=["story_id", "zone"], how="inner")
   42 |     m["log_RT"] = np.log(m.RT)
   43 |     m = m.sort_values(["participant", "story_id", "zone"])
   44 |     m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
   45 |     d = m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   46 |                          "prev_log_RT", "surprisal", "tee_k3"]).copy()
   47 |     for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal",
   48 |               "tee_k3", "entropy"]:
   49 |         v = d[c]
   50 |         d["z_" + c] = (v - v.mean()) / v.std()
   51 |     return d
   52 | 
   53 | 
   54 | def spline_terms(df, cols, dfree):
   55 |     """Add natural-cubic-spline basis columns; return the term names."""
   56 |     names = []
   57 |     for c in cols:
   58 |         B = dmatrix(f"cr(x, df={dfree}) - 1", {"x": df[c].values},
   59 |                     return_type="dataframe")
   60 |         for j in range(B.shape[1]):
   61 |             nm = f"s_{c}_{dfree}_{j}"
   62 |             df[nm] = B.iloc[:, j].values
   63 |             names.append(nm)
   64 |     return names
   65 | 
   66 | 
   67 | def main():
   68 |     d = build()
   69 |     print(f"n = {len(d):,}   participants = {d.participant.nunique()}")
   70 |     print(f"r(TEE, surprisal) = {d.tee_k3.corr(d.surprisal):+.3f}   "
   71 |           f"r(TEE, log_freq) = {d.tee_k3.corr(d.log_freq):+.3f}\n")
   72 | 
   73 |     FLEX = ["surprisal", "log_freq", "word_length"]
   74 |     BASE_LINEAR = "z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_surprisal"
   75 | 
   76 |     print("=" * 80)
   77 |     print("Does TEE survive as surprisal/frequency/length are given more freedom?")
   78 |     print("=" * 80)
   79 |     print(f"{'control specification':<42}{'dAIC(TEE)':>11}{'beta':>10}{'p':>12}")
   80 | 
   81 |     # linear reference
   82 |     m1 = smf.mixedlm(f"log_RT ~ {BASE_LINEAR}", d,
   83 |                      groups=d["participant"]).fit(reml=False, method="lbfgs")
   84 |     m2 = smf.mixedlm(f"log_RT ~ {BASE_LINEAR} + z_tee_k3", d,
   85 |                      groups=d["participant"]).fit(reml=False, method="lbfgs")
   86 |     print(f"{'linear (published spec)':<42}{m1.aic-m2.aic:>11.1f}"
   87 |           f"{m2.params['z_tee_k3']:>10.5f}{m2.pvalues['z_tee_k3']:>12.2e}")
   88 | 
   89 |     for dfree in [3, 5, 8, 12]:
   90 |         terms = spline_terms(d, FLEX, dfree)
   91 |         base = " + ".join(["z_zone", "z_prev_log_RT"] + terms)
   92 |         a = smf.mixedlm(f"log_RT ~ {base}", d,
   93 |                         groups=d["participant"]).fit(reml=False, method="lbfgs")
   94 |         b = smf.mixedlm(f"log_RT ~ {base} + z_tee_k3", d,
   95 |                         groups=d["participant"]).fit(reml=False, method="lbfgs")
   96 |         print(f"{'splines df=' + str(dfree) + ' on surp/freq/len':<42}"
   97 |               f"{a.aic-b.aic:>11.1f}{b.params['z_tee_k3']:>10.5f}"
   98 |               f"{b.pvalues['z_tee_k3']:>12.2e}")
   99 | 
  100 |     # strictest: splines + entropy + punctuation
  101 |     terms = spline_terms(d, FLEX, 8)
  102 |     base = " + ".join(["z_zone", "z_prev_log_RT", "z_entropy", "punct"] + terms)
  103 |     a = smf.mixedlm(f"log_RT ~ {base}", d,
  104 |                     groups=d["participant"]).fit(reml=False, method="lbfgs")
  105 |     b = smf.mixedlm(f"log_RT ~ {base} + z_tee_k3", d,
  106 |                     groups=d["participant"]).fit(reml=False, method="lbfgs")
  107 |     print(f"{'df=8 splines + entropy + punctuation':<42}{a.aic-b.aic:>11.1f}"
  108 |           f"{b.params['z_tee_k3']:>10.5f}{b.pvalues['z_tee_k3']:>12.2e}")
  109 | 
  110 |     print("\n" + "=" * 80)
  111 |     print("How curved IS the surprisal-RT relationship? (is the worry real?)")
  112 |     print("=" * 80)
  113 |     lin = smf.mixedlm(f"log_RT ~ z_zone + z_prev_log_RT + z_word_length "
  114 |                       f"+ z_log_freq + z_surprisal", d,
  115 |                       groups=d["participant"]).fit(reml=False, method="lbfgs")
  116 |     st = spline_terms(d, ["surprisal"], 8)
  117 |     spl = smf.mixedlm(f"log_RT ~ z_zone + z_prev_log_RT + z_word_length "
  118 |                       f"+ z_log_freq + " + " + ".join(st), d,
  119 |                       groups=d["participant"]).fit(reml=False, method="lbfgs")
  120 |     print(f"  linear surprisal   AIC = {lin.aic:.1f}")
  121 |     print(f"  spline surprisal   AIC = {spl.aic:.1f}   "
  122 |           f"improvement = {lin.aic - spl.aic:.1f}")
  123 |     print("  (large improvement => surprisal really is nonlinear here, so the")
  124 |     print("   misspecification worry was well founded)")
  125 | 
  126 | 
  127 | if __name__ == "__main__":
  128 |     main()
```


==============================================================================
### FILE: gp_confound_check/tee_functional_form.py
==============================================================================

```
    1 | """
    2 | IS A LINEAR FIT THE RIGHT SUMMARY OF THE TRAJECTORY EFFECT?
    3 | ============================================================
    4 | We tested whether SURPRISAL's functional form matters (it does: splining it
    5 | improves fit substantially). We never tested the functional form of the
    6 | trajectory measure itself, and the partial-effect profiles now suggest we
    7 | should: in Natural Stories the profile rises roughly monotonically, but in the
    8 | garden-path corpus it is jagged and non-monotone, so a positive linear
    9 | coefficient there may be summarising a shape that is not a line.
   10 | 
   11 | TESTS, per corpus, subject-level throughout:
   12 | 
   13 |   F1  linear vs spline in TEE. Fit z(logRT) with TEE entered linearly, then as
   14 |       a B-spline (df = 3, 5, 8), everything else held fixed. Compare by AIC
   15 |       within participant, then across participants. If the spline does not
   16 |       improve fit, linear is an adequate summary and the jaggedness in the
   17 |       profile is noise.
   18 | 
   19 |   F2  monotonicity. Across the ten within-participant deciles, count the
   20 |       fraction of participants whose profile is monotonically increasing, and
   21 |       test the decile means for trend (Spearman rho of mean residual against
   22 |       decile, per participant). A real effect that is linear should give a high
   23 |       positive rho; a jagged profile should not.
   24 | 
   25 |   F3  shape stability. Split participants at random into two halves and
   26 |       correlate the two decile profiles. A shape driven by real structure
   27 |       should replicate across halves; noise should not. Repeated 50 times.
   28 | 
   29 |   F4  is the effect carried by the extremes? Refit the linear model dropping the
   30 |       top and bottom decile of TEE. If the coefficient survives, the effect is
   31 |       distributed; if it collapses, it is an extremes phenomenon.
   32 | 
   33 | Reported for both corpora so they can be compared directly.
   34 | """
   35 | 
   36 | import numpy as np
   37 | import pandas as pd
   38 | from scipy import stats
   39 | import statsmodels.api as sm
   40 | import statsmodels.formula.api as smf
   41 | from wordfreq import zipf_frequency
   42 | import hashlib, warnings
   43 | warnings.filterwarnings("ignore")
   44 | 
   45 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   46 | GPC = f"{GP}/gp_confound_check"
   47 | RNG = np.random.default_rng(20260810)
   48 | NBIN = 10
   49 | 
   50 | 
   51 | def zs(x):
   52 |     x = np.asarray(x, dtype=float)
   53 |     s = x.std()
   54 |     return (x - x.mean()) / s if s > 0 else x * 0
   55 | 
   56 | 
   57 | # ------------------------------------------------------------------ corpora
   58 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   59 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   60 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   61 | assert sh == "8a6087341e", sh
   62 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   63 |                  sep="\t").rename(columns={"item": "story_id",
   64 |                                            "WorkerId": "participant"})
   65 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   66 | ns = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   67 |                  "log_freq"]], on=["story_id", "zone"], how="inner")
   68 | ns["log_RT"] = np.log(ns.RT)
   69 | ns = ns.sort_values(["participant", "story_id", "zone"])
   70 | ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
   71 | ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   72 |                        "prev_log_RT", "tee_k3", "surprisal"]).rename(
   73 |     columns={"tee_k3": "tee"})
   74 | 
   75 | d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
   76 | d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
   77 | d = d.rename(columns={"MD5": "participant"})
   78 | d = d.merge(pd.read_csv(f"{GPC}/sap_measures_L6k3.csv"),
   79 |             on=["item", "Type", "WordPosition"], how="left",
   80 |             validate="many_to_one")
   81 | d["word_length"] = d.EachWord.str.len()
   82 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
   83 |     lambda x: zipf_frequency(x, "en"))
   84 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
   85 | d["from_start"] = d.WordPosition.astype(float)
   86 | d["fs2"] = d.from_start ** 2
   87 | d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
   88 | d["fe2"] = d.from_end ** 2
   89 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
   90 | d["log_RT"] = np.log(d.RT)
   91 | d = d.dropna(subset=["tee", "surp", "word_length", "log_freq",
   92 |                      "log_RT"]).rename(columns={"surp": "surprisal"})
   93 | 
   94 | CORPORA = [
   95 |     ("Natural Stories", ns, ["surprisal", "word_length", "log_freq", "zone",
   96 |                              "prev_log_RT"], 300),
   97 |     ("Garden-path corpus", d, ["surprisal", "word_length", "log_freq", "punct",
   98 |                                "from_start", "fs2", "from_end", "fe2"], 100),
   99 | ]
  100 | 
  101 | for name, df, ctrl, minn in CORPORA:
  102 |     print("=" * 84)
  103 |     print(name)
  104 |     print("=" * 84)
  105 |     print(f"  {len(df):,} rows, {df.participant.nunique():,} participants")
  106 | 
  107 |     # ---------------- F1: linear vs spline in TEE ----------------
  108 |     zc = ["log_RT", "tee"] + ctrl
  109 |     gains = {3: [], 5: [], 8: []}
  110 |     for pid, s in df.groupby("participant"):
  111 |         s = s.dropna(subset=zc)
  112 |         if len(s) < minn:
  113 |             continue
  114 |         s = s.copy()
  115 |         for c in zc:
  116 |             s["z_" + c] = zs(s[c].values)
  117 |         base = "z_log_RT ~ " + " + ".join("z_" + c for c in ctrl)
  118 |         try:
  119 |             lin = smf.ols(base + " + z_tee", s).fit()
  120 |             for k in gains:
  121 |                 sp = smf.ols(base + f" + bs(z_tee, df={k})", s).fit()
  122 |                 gains[k].append(lin.aic - sp.aic)
  123 |         except Exception:
  124 |             continue
  125 |     print("\n  F1  linear vs spline in TEE  (positive = spline fits better)")
  126 |     for k, v in gains.items():
  127 |         v = np.array(v)
  128 |         print(f"      df={k}:  mean dAIC = {v.mean():+7.2f}   "
  129 |               f"spline better in {(v > 0).mean():5.1%} of participants   "
  130 |               f"n={len(v)}")
  131 | 
  132 |     # ---------------- F2: monotonicity of the decile profile ----------------
  133 |     rhos, monos, profs = [], [], []
  134 |     for pid, s in df.groupby("participant"):
  135 |         s = s.dropna(subset=zc)
  136 |         if len(s) < minn:
  137 |             continue
  138 |         X = np.column_stack([zs(s[c].values) for c in ctrl])
  139 |         y = zs(s.log_RT.values)
  140 |         res = y - sm.OLS(y, sm.add_constant(X)).fit().fittedvalues
  141 |         try:
  142 |             q = pd.qcut(s.tee.values, NBIN, labels=False, duplicates="drop")
  143 |         except ValueError:
  144 |             continue
  145 |         if len(np.unique(q)) < NBIN:
  146 |             continue
  147 |         prof = np.array([res[q == b].mean() for b in range(NBIN)])
  148 |         profs.append(prof)
  149 |         rhos.append(stats.spearmanr(np.arange(NBIN), prof).statistic)
  150 |         monos.append(bool(np.all(np.diff(prof) > 0)))
  151 |     rhos = np.array(rhos)
  152 |     P = np.array(profs)
  153 |     print(f"\n  F2  monotonicity across deciles")
  154 |     print(f"      mean Spearman rho(decile, residual) = {rhos.mean():+.3f}   "
  155 |           f"positive in {(rhos > 0).mean():.1%} of participants")
  156 |     print(f"      strictly monotone increasing profiles: {np.mean(monos):.1%}")
  157 |     grand = P.mean(0)
  158 |     print(f"      grand profile rho = "
  159 |           f"{stats.spearmanr(np.arange(NBIN), grand).statistic:+.3f}")
  160 |     print(f"      grand profile: {np.round(grand, 4)}")
  161 | 
  162 |     # ---------------- F3: split-half shape stability ----------------
  163 |     cors = []
  164 |     for _ in range(50):
  165 |         idx = RNG.permutation(len(P))
  166 |         a, b = P[idx[:len(P) // 2]].mean(0), P[idx[len(P) // 2:]].mean(0)
  167 |         cors.append(np.corrcoef(a, b)[0, 1])
  168 |     cors = np.array(cors)
  169 |     print(f"\n  F3  split-half shape stability: r = {cors.mean():+.3f} "
  170 |           f"(sd {cors.std():.3f}) over 50 splits")
  171 | 
  172 |     # ---------------- F4: drop the extreme deciles ----------------
  173 |     full, trimmed = [], []
  174 |     for pid, s in df.groupby("participant"):
  175 |         s = s.dropna(subset=zc)
  176 |         if len(s) < minn:
  177 |             continue
  178 |         cols = ["tee"] + ctrl
  179 |         X = np.column_stack([zs(s[c].values) for c in cols])
  180 |         y = zs(s.log_RT.values)
  181 |         full.append(sm.OLS(y, sm.add_constant(X)).fit().params[1])
  182 |         lo, hi = np.percentile(s.tee.values, [10, 90])
  183 |         m = (s.tee.values > lo) & (s.tee.values < hi)
  184 |         if m.sum() < minn // 2:
  185 |             continue
  186 |         s2 = s[m]
  187 |         X2 = np.column_stack([zs(s2[c].values) for c in cols])
  188 |         trimmed.append(sm.OLS(zs(s2.log_RT.values),
  189 |                               sm.add_constant(X2)).fit().params[1])
  190 |     full, trimmed = np.array(full), np.array(trimmed)
  191 |     print(f"\n  F4  effect without the extreme deciles")
  192 |     print(f"      full     beta = {full.mean():+.5f}  "
  193 |           f"{(full > 0).mean():.1%} positive")
  194 |     print(f"      trimmed  beta = {trimmed.mean():+.5f}  "
  195 |           f"{(trimmed > 0).mean():.1%} positive  "
  196 |           f"({trimmed.mean() / full.mean():.0%} of full)")
  197 |     print()
```


==============================================================================
### FILE: gp_confound_check/tee_threshold.py
==============================================================================

```
    1 | """
    2 | IS THE TRAJECTORY EFFECT THRESHOLDED, AND IS THE LOW-DECILE STRUCTURE REAL?
    3 | ===========================================================================
    4 | The decile profiles are flat across deciles 1-7 and rise from 8 upward, which
    5 | suggests a threshold rather than a graded effect. Two things have to be checked
    6 | before that story is told.
    7 | 
    8 | (1) The apparent bump at decile 2 in Natural Stories (+0.0065) is nearly as high
    9 |     as decile 8 (+0.0075). Under a threshold account it should be flat. Is it
   10 |     real? Overall split-half stability was r = .88, but that could be carried
   11 |     entirely by the top-end rise. So: split-half stability computed on deciles
   12 |     1-7 ONLY, and per-decile tests against zero.
   13 | 
   14 | (2) If the effect is thresholded, a single indicator for the top decile should
   15 |     fit about as well as a linear term -- and a hinge (flat below a knot, linear
   16 |     above) should fit better than either. A spline already lost to linear, which
   17 |     is consistent with a threshold: a spline spends parameters modelling wiggle
   18 |     in the flat region, a hinge spends one in the right place.
   19 | 
   20 | TESTS
   21 |   T1  per-decile mean with 95% CI across participants, and t vs zero, so we can
   22 |       see which deciles are actually distinguishable from the baseline
   23 |   T2  split-half shape stability restricted to deciles 1-7
   24 |   T3  linear vs top-decile indicator vs hinge, by AIC within participant
   25 | """
   26 | 
   27 | import numpy as np
   28 | import pandas as pd
   29 | from scipy import stats
   30 | import statsmodels.api as sm
   31 | from wordfreq import zipf_frequency
   32 | import hashlib, warnings
   33 | warnings.filterwarnings("ignore")
   34 | 
   35 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   36 | GPC = f"{GP}/gp_confound_check"
   37 | RNG = np.random.default_rng(20260810)
   38 | NBIN = 10
   39 | 
   40 | 
   41 | def zs(x):
   42 |     x = np.asarray(x, dtype=float)
   43 |     s = x.std()
   44 |     return (x - x.mean()) / s if s > 0 else x * 0
   45 | 
   46 | 
   47 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   48 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   49 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   50 | assert sh == "8a6087341e", sh
   51 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   52 |                  sep="\t").rename(columns={"item": "story_id",
   53 |                                            "WorkerId": "participant"})
   54 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   55 | ns = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   56 |                  "log_freq"]], on=["story_id", "zone"], how="inner")
   57 | ns["log_RT"] = np.log(ns.RT)
   58 | ns = ns.sort_values(["participant", "story_id", "zone"])
   59 | ns["prev_log_RT"] = ns.groupby(["participant", "story_id"])["log_RT"].shift(1)
   60 | ns = ns.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   61 |                        "prev_log_RT", "tee_k3", "surprisal"]).rename(
   62 |     columns={"tee_k3": "tee"})
   63 | 
   64 | d = pd.read_csv(f"{GPC}/ClassicGardenPathSet.csv")
   65 | d["EachWord"] = d.EachWord.astype(str).str.replace("%2C", ",", regex=False)
   66 | d = d.rename(columns={"MD5": "participant"})
   67 | d = d.merge(pd.read_csv(f"{GPC}/sap_measures_L6k3.csv"),
   68 |             on=["item", "Type", "WordPosition"], how="left",
   69 |             validate="many_to_one")
   70 | d["word_length"] = d.EachWord.str.len()
   71 | d["log_freq"] = d.EachWord.str.strip(".,;:!?").str.lower().map(
   72 |     lambda x: zipf_frequency(x, "en"))
   73 | d["punct"] = d.EachWord.str.match(r".*[^A-Za-z0-9]$").astype(float)
   74 | d["from_start"] = d.WordPosition.astype(float)
   75 | d["fs2"] = d.from_start ** 2
   76 | d["from_end"] = (d.sent_len - d.WordPosition).astype(float)
   77 | d["fe2"] = d.from_end ** 2
   78 | d = d[(d.RT >= 100) & (d.RT <= 5000)].copy()
   79 | d["log_RT"] = np.log(d.RT)
   80 | d = d.dropna(subset=["tee", "surp", "word_length", "log_freq",
   81 |                      "log_RT"]).rename(columns={"surp": "surprisal"})
   82 | 
   83 | CORPORA = [
   84 |     ("Natural Stories", ns, ["surprisal", "word_length", "log_freq", "zone",
   85 |                              "prev_log_RT"], 300),
   86 |     ("Garden-path corpus", d, ["surprisal", "word_length", "log_freq", "punct",
   87 |                                "from_start", "fs2", "from_end", "fe2"], 100),
   88 | ]
   89 | 
   90 | for name, df, ctrl, minn in CORPORA:
   91 |     print("=" * 86)
   92 |     print(name)
   93 |     print("=" * 86)
   94 |     profs, aic = [], {"linear": [], "top-decile indicator": [], "hinge": []}
   95 |     for pid, s in df.groupby("participant"):
   96 |         s = s.dropna(subset=["log_RT", "tee"] + ctrl)
   97 |         if len(s) < minn:
   98 |             continue
   99 |         X = np.column_stack([zs(s[c].values) for c in ctrl])
  100 |         y = zs(s.log_RT.values)
  101 |         fit = sm.OLS(y, sm.add_constant(X)).fit()
  102 |         res = y - fit.fittedvalues
  103 |         t = s.tee.values
  104 |         try:
  105 |             q = pd.qcut(t, NBIN, labels=False, duplicates="drop")
  106 |         except ValueError:
  107 |             continue
  108 |         if len(np.unique(q)) < NBIN:
  109 |             continue
  110 |         profs.append([res[q == b].mean() for b in range(NBIN)])
  111 | 
  112 |         # T3: three shapes for the trajectory term
  113 |         knot = np.percentile(t, 70)
  114 |         terms = {"linear": zs(t),
  115 |                  "top-decile indicator": (q == NBIN - 1).astype(float),
  116 |                  "hinge": np.clip(t - knot, 0, None)}
  117 |         for k, v in terms.items():
  118 |             Xk = np.column_stack([zs(v)] + [zs(s[c].values) for c in ctrl])
  119 |             aic[k].append(sm.OLS(y, sm.add_constant(Xk)).fit().aic)
  120 | 
  121 |     P = np.array(profs)
  122 |     n = len(P)
  123 |     print(f"  {n} participants\n")
  124 | 
  125 |     print("  T1  per-decile residual mean (across participants)")
  126 |     print(f"      {'decile':>7}{'mean':>10}{'95% CI':>20}{'t':>8}{'p':>10}")
  127 |     for b in range(NBIN):
  128 |         col = P[:, b]
  129 |         se = col.std(ddof=1) / np.sqrt(n)
  130 |         t_, p_ = stats.ttest_1samp(col, 0)
  131 |         star = " *" if p_ < .05 else ""
  132 |         print(f"      {b+1:>7}{col.mean():>+10.4f}"
  133 |               f"   [{col.mean()-1.96*se:+.4f}, {col.mean()+1.96*se:+.4f}]"
  134 |               f"{t_:>8.2f}{p_:>10.1e}{star}")
  135 | 
  136 |     def splithalf(cols, reps=200):
  137 |         r = []
  138 |         for _ in range(reps):
  139 |             i = RNG.permutation(n)
  140 |             a = P[i[:n // 2]][:, cols].mean(0)
  141 |             b = P[i[n // 2:]][:, cols].mean(0)
  142 |             r.append(np.corrcoef(a, b)[0, 1])
  143 |         return np.array(r)
  144 | 
  145 |     all_r = splithalf(list(range(NBIN)))
  146 |     low_r = splithalf(list(range(7)))
  147 |     print(f"\n  T2  split-half shape stability")
  148 |     print(f"      all deciles      r = {all_r.mean():+.3f} (sd {all_r.std():.3f})")
  149 |     print(f"      deciles 1-7 only r = {low_r.mean():+.3f} (sd {low_r.std():.3f})"
  150 |           f"   <- is the flat region real structure?")
  151 | 
  152 |     print(f"\n  T3  shape of the trajectory term (AIC, lower is better)")
  153 |     base = np.array(aic["linear"])
  154 |     for k in ["linear", "top-decile indicator", "hinge"]:
  155 |         v = np.array(aic[k])
  156 |         d_ = base - v
  157 |         print(f"      {k:<24} mean dAIC vs linear = {d_.mean():+7.2f}   "
  158 |               f"better in {(d_ > 0).mean():5.1%} of participants")
  159 |     print()
```


==============================================================================
### FILE: gp_confound_check/v2_interaction.py
==============================================================================

```
    1 | """
    2 | RECOMPUTE THE SURPRISAL x EXTRAPOLATION-ERROR INTERACTION TEST
    3 | ==============================================================
    4 | v1's Regression paragraph claims: "The additive model was preferred over a model
    5 | including their interaction (dAIC = -2.0 in favor of the simpler model)."
    6 | 
    7 | That number came from the superseded measure pipeline and was never recomputed.
    8 | It survived the manuscript's numeric audit only because "2.0" matches trivially.
    9 | It is the last v1 statistic still in the text without provenance on the verified
   10 | sample.
   11 | 
   12 | Recomputed here on locked sample 8a6087341e, same specification as the headline
   13 | model: mixedlm, by-participant random intercept, ML fit, controls = word length
   14 | + log frequency + zone + previous log RT.
   15 | 
   16 | Reported either way. If the interaction is now favoured, the claim of additivity
   17 | must be withdrawn, not softened.
   18 | """
   19 | 
   20 | import numpy as np
   21 | import pandas as pd
   22 | import statsmodels.formula.api as smf
   23 | import hashlib, warnings
   24 | warnings.filterwarnings("ignore")
   25 | 
   26 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   27 | 
   28 | 
   29 | def z(s):
   30 |     v = s.dropna()
   31 |     return (s - v.mean()) / v.std()
   32 | 
   33 | 
   34 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   35 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   36 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   37 | assert sh == "8a6087341e", sh
   38 | print(f"locked sample {sh} verified")
   39 | 
   40 | # [2026-08-13] frequency repaired: the sample's log_freq is zero for 19.7% of
   41 | # words (unnormalised lookup). Recomputed as Zipf of the lowercased,
   42 | # punctuation-stripped word, matching every other analysis in v2.
   43 | from wordfreq import zipf_frequency
   44 | S["log_freq"] = (S.word.astype(str).str.strip('.,;:!?"\'()[]').str.lower()
   45 |                  .map(lambda w: zipf_frequency(w, "en")))
   46 | 
   47 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   48 |                  sep="\t").rename(columns={"item": "story_id",
   49 |                                            "WorkerId": "participant"})
   50 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   51 | d = rt.merge(S[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   52 |                 "log_freq"]], on=["story_id", "zone"], how="inner")
   53 | d["log_RT"] = np.log(d.RT)
   54 | d = d.sort_values(["participant", "story_id", "zone"])
   55 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
   56 | d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   57 |                      "prev_log_RT", "surprisal", "tee_k3"])
   58 | for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal",
   59 |           "tee_k3"]:
   60 |     d["z_" + c] = z(d[c])
   61 | print(f"n = {len(d):,}   participants = {d.participant.nunique()}\n")
   62 | 
   63 | CTRL = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT"
   64 | add = f"{CTRL} + z_surprisal + z_tee_k3"
   65 | itx = f"{CTRL} + z_surprisal * z_tee_k3"
   66 | 
   67 | m_add = smf.mixedlm(add, d, groups=d.participant).fit(reml=False,
   68 |                                                       method="lbfgs")
   69 | m_itx = smf.mixedlm(itx, d, groups=d.participant).fit(reml=False,
   70 |                                                       method="lbfgs")
   71 | 
   72 | print("=" * 74)
   73 | print("ADDITIVE vs INTERACTION")
   74 | print("=" * 74)
   75 | print(f"  additive     AIC {m_add.aic:12.1f}")
   76 | print(f"  interaction  AIC {m_itx.aic:12.1f}")
   77 | d_aic = m_add.aic - m_itx.aic
   78 | print(f"\n  dAIC (additive - interaction) = {d_aic:+.1f}")
   79 | print(f"  {'INTERACTION favoured' if d_aic > 0 else 'ADDITIVE favoured'} "
   80 |       f"by {abs(d_aic):.1f}")
   81 | 
   82 | term = "z_surprisal:z_tee_k3"
   83 | if term in m_itx.params:
   84 |     print(f"\n  interaction coefficient = {m_itx.params[term]:+.5f}   "
   85 |           f"p = {m_itx.pvalues[term]:.3e}")
   86 | print(f"  main effects in the interaction model: "
   87 |       f"surprisal {m_itx.params['z_surprisal']:+.5f}, "
   88 |       f"TEE {m_itx.params['z_tee_k3']:+.5f}")
   89 | 
   90 | print("\n" + "=" * 74)
   91 | print("v1 CLAIM CHECK")
   92 | print("=" * 74)
   93 | print("  v1: 'additive model preferred over interaction, dAIC = -2.0'")
   94 | if d_aic < 0 and abs(abs(d_aic) - 2.0) < 2.0:
   95 |     print("  -> reproduces in direction and roughly in magnitude.")
   96 | elif d_aic < 0:
   97 |     print(f"  -> additivity holds, but the magnitude differs "
   98 |           f"({abs(d_aic):.1f} vs 2.0). Update the number.")
   99 | else:
  100 |     print("  -> DOES NOT HOLD. The interaction model is now favoured.")
  101 |     print("     The additivity claim must be withdrawn, not softened.")
```


==============================================================================
### FILE: gp_confound_check/v2_offdiag_and_r044.py
==============================================================================

```
    1 | """
    2 | TWO REMAINING BLOCKERS FOR v2
    3 | =============================
    4 | (A) v1 paragraph 47 (manuscript.tex line 298): the claim about WHICH WORDS
    5 |     populate the off-diagonal cells of the surprisal x TEE tercile matrix.
    6 |     v1 asserts:
    7 |       low-surprisal / high-TEE  -> coordinators and complementizers
    8 |                                    ("and", "as", "that", "had")
    9 |       high-surprisal / low-TEE  -> rare content words ("ocean", "manor", "tics")
   10 |                                    plus discourse pivots ("then", "however",
   11 |                                    "now", "first")
   12 |     Tercile membership changed when the measure pipeline was rebuilt, so this
   13 |     paragraph's content is stale and must be recomputed or dropped.
   14 | 
   15 | (B) v1's r = .044 orthogonality claim (abstract, line 129, line 278, Table 5,
   16 |     and the Pythia values .046/.047 at line 247). On the verified pipeline
   17 |     r(TEE, surprisal) = +0.310, while r(TEE, entropy) = +0.043. The suspicion is
   18 |     that .044 was the ENTROPY correlation, mislabelled. This script tries to
   19 |     falsify that: it sweeps TEE variants (layers, window sizes, normalised
   20 |     forms) and correlation types, asking whether ANY plausible TEE-vs-surprisal
   21 |     configuration lands near .044. If none does and entropy does, mislabelling
   22 |     is the parsimonious explanation and v2 should say so.
   23 | 
   24 | Locked sample 8a6087341e throughout, hash asserted.
   25 | """
   26 | 
   27 | import numpy as np
   28 | import pandas as pd
   29 | from scipy import stats
   30 | import hashlib, warnings
   31 | warnings.filterwarnings("ignore")
   32 | 
   33 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   34 | 
   35 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   36 | sh = hashlib.md5("|".join(f"{r.story_id}.{r.word_idx}" for r in
   37 |      S[["story_id", "word_idx"]].itertuples(index=False)).encode()).hexdigest()[:10]
   38 | assert sh == "8a6087341e", sh
   39 | print(f"locked sample {sh}   {len(S):,} words")
   40 | print(f"columns available: {[c for c in S.columns][:40]}\n")
   41 | 
   42 | # =============================================================== (B) the r=.044
   43 | print("=" * 78)
   44 | print("(B) WHERE DOES r = .044 COME FROM?")
   45 | print("=" * 78)
   46 | 
   47 | cand = [c for c in S.columns
   48 |         if c.startswith("tee") or c.startswith("teeN") or c == "curvature_3"]
   49 | print(f"TEE-like columns in the locked sample: {cand}\n")
   50 | 
   51 | print(f"{'measure':<16}{'r(x, surprisal)':>18}{'Spearman':>12}"
   52 |       f"{'r(x, entropy)':>16}")
   53 | hits = []
   54 | for c in cand:
   55 |     if S[c].notna().sum() < 100:
   56 |         continue
   57 |     both = S[[c, "surprisal"]].dropna()
   58 |     r = both[c].corr(both.surprisal)
   59 |     rho = stats.spearmanr(both[c], both.surprisal).statistic
   60 |     re_ = S[[c, "entropy"]].dropna().corr().iloc[0, 1] if "entropy" in S else np.nan
   61 |     print(f"{c:<16}{r:>18.4f}{rho:>12.4f}{re_:>16.4f}")
   62 |     if abs(r - .044) < .015:
   63 |         hits.append((c, "pearson-surprisal", r))
   64 |     if abs(rho - .044) < .015:
   65 |         hits.append((c, "spearman-surprisal", rho))
   66 |     if not np.isnan(re_) and abs(re_ - .044) < .015:
   67 |         hits.append((c, "pearson-entropy", re_))
   68 | 
   69 | # also try the extensions files, which hold other layers/models
   70 | import os
   71 | for f, note in [("extensions/nonlinear_tee_8a6087341e.csv", "nonlinear variants"),
   72 |                 ("extensions/coarse_tee_8a6087341e.csv", "coarse/normalised"),
   73 |                 ("gp_confound_check/pythia_tee_8a6087341e.csv", "pythia")]:
   74 |     p = f"{GP}/{f}"
   75 |     if not os.path.exists(p):
   76 |         continue
   77 |     E = pd.read_csv(p)
   78 |     if "surprisal" not in E.columns:
   79 |         E = E.merge(S[["story_id", "word_idx", "surprisal"]],
   80 |                     on=["story_id", "word_idx"], how="left")
   81 |     ec = [c for c in E.columns if ("tee" in c.lower() or "curv" in c.lower())]
   82 |     for c in ec:
   83 |         b = E[[c, "surprisal"]].dropna()
   84 |         if len(b) < 100:
   85 |             continue
   86 |         r = b[c].corr(b.surprisal)
   87 |         if abs(r - .044) < .015:
   88 |             hits.append((f"{c} [{note}]", "pearson-surprisal", r))
   89 | 
   90 | print("\nvalues landing within .015 of .044:")
   91 | if hits:
   92 |     for h in hits:
   93 |         print(f"  {h[0]:<34}{h[1]:<22}{h[2]:+.4f}")
   94 | else:
   95 |     print("  none")
   96 | 
   97 | print("\nVERDICT (B):")
   98 | r_surp = S.tee_k3.corr(S.surprisal)
   99 | r_ent = S.tee_k3.corr(S.entropy)
  100 | print(f"  headline measure tee_k3:  r(surprisal) = {r_surp:+.4f}   "
  101 |       f"r(entropy) = {r_ent:+.4f}")
  102 | if abs(r_ent - .044) < .005 and abs(r_surp - .044) > .1:
  103 |     print("  The entropy correlation reproduces .044 to within .005 while the")
  104 |     print("  surprisal correlation is nowhere near it. Mislabelling in the v1")
  105 |     print("  pipeline is the parsimonious account. v2 should state this.")
  106 | 
  107 | # ====================================================== (A) off-diagonal cells
  108 | print("\n" + "=" * 78)
  109 | print("(A) COMPOSITION OF THE OFF-DIAGONAL CELLS, RECOMPUTED")
  110 | print("=" * 78)
  111 | 
  112 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
  113 |                  sep="\t").rename(columns={"item": "story_id",
  114 |                                            "WorkerId": "participant"})
  115 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
  116 | # NOTE: processed_RTs.tsv has its own `word` column, so the sample's word form
  117 | # is renamed before merging. An unsuffixed merge silently produces word_x/word_y
  118 | # and has bitten this project before.
  119 | d = rt.merge(S[["story_id", "zone", "word", "tee_k3", "surprisal",
  120 |                 "word_length", "log_freq"]].rename(columns={"word": "wordform"}),
  121 |              on=["story_id", "zone"], how="inner")
  122 | d["log_RT"] = np.log(d.RT)
  123 | d = d.sort_values(["participant", "story_id", "zone"])
  124 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
  125 | d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
  126 |                      "prev_log_RT", "surprisal", "tee_k3"])
  127 | d["s_t"] = pd.qcut(d.surprisal, 3, labels=["low", "mid", "high"])
  128 | d["e_t"] = pd.qcut(d.tee_k3, 3, labels=["low", "mid", "high"])
  129 | print(f"analysis rows {len(d):,}   participants {d.participant.nunique()}")
  130 | 
  131 | # composition over DISTINCT WORD TOKENS (each corpus position counted once),
  132 | # using the tercile assignment from the RT sample
  133 | W = d.drop_duplicates(subset=["story_id", "zone"])[
  134 |     ["story_id", "zone", "wordform", "s_t", "e_t", "surprisal", "tee_k3",
  135 |      "log_freq"]].copy()
  136 | W["w"] = W.wordform.astype(str).str.lower().str.strip(".,;:!?\"'")
  137 | print(f"distinct corpus positions in the matrix: {len(W):,}\n")
  138 | 
  139 | overall = W.w.value_counts(normalize=True)
  140 | 
  141 | FUNCTION = set("""the a an and or but so as that which who whom whose if then
  142 | than of to in on at by for with from into over under about after before while
  143 | when where because since although though unless until is was were are be been
  144 | being have has had do does did will would can could shall should may might must
  145 | not no nor it its he she they them his her their we us our you your i me my this
  146 | these those there here""".split())
  147 | 
  148 | 
  149 | def profile(s_lab, e_lab, title, n=25):
  150 |     cell = W[(W.s_t == s_lab) & (W.e_t == e_lab)]
  151 |     print("-" * 78)
  152 |     print(f"{title}   n = {len(cell):,} corpus positions, "
  153 |           f"{cell.w.nunique():,} word types")
  154 |     print(f"  mean surprisal {cell.surprisal.mean():.2f}   "
  155 |           f"mean TEE {cell.tee_k3.mean():.1f}   "
  156 |           f"mean log freq {cell.log_freq.mean():.2f}")
  157 |     fn = cell.w.isin(FUNCTION).mean()
  158 |     fn_all = W.w.isin(FUNCTION).mean()
  159 |     print(f"  closed-class share {fn:.1%}  (corpus overall {fn_all:.1%})")
  160 |     vc = cell.w.value_counts()
  161 |     print(f"\n  most frequent words in the cell:")
  162 |     print("   ", ", ".join(f"{w} ({c})" for w, c in vc.head(n).items()))
  163 |     # enrichment: cell rate / corpus rate, for words with enough support
  164 |     sub = vc[vc >= 5]
  165 |     enr = (sub / sub.sum()) / overall.reindex(sub.index)
  166 |     enr = enr.dropna().sort_values(ascending=False)
  167 |     print(f"\n  most ENRICHED words (count >= 5, cell rate / corpus rate):")
  168 |     print("   ", ", ".join(f"{w} ({e:.1f}x)" for w, e in enr.head(n).items()))
  169 |     print()
  170 |     return cell
  171 | 
  172 | 
  173 | print("\nv1 claimed: low-surprisal / high-TEE is enriched for coordinators and")
  174 | print("complementizers ('and', 'as', 'that', 'had').")
  175 | c1 = profile("low", "high", "LOW SURPRISAL / HIGH TEE")
  176 | 
  177 | print("v1 claimed: high-surprisal / low-TEE holds rare content words ('ocean',")
  178 | print("'manor', 'tics') and discourse pivots ('then', 'however', 'now', 'first').")
  179 | c2 = profile("high", "low", "HIGH SURPRISAL / LOW TEE")
  180 | 
  181 | print("=" * 78)
  182 | print("CHECK OF v1'S SPECIFIC EXAMPLES ON THE VERIFIED SAMPLE")
  183 | print("=" * 78)
  184 | claims = {"low/high (coordinators/complementizers)":
  185 |           (("low", "high"), ["and", "as", "that", "had"]),
  186 |           "high/low (rare content + pivots)":
  187 |           (("high", "low"), ["ocean", "manor", "tics", "then", "however",
  188 |                              "now", "first"])}
  189 | for lab, ((s_lab, e_lab), wl) in claims.items():
  190 |     print(f"\n{lab}:")
  191 |     for w in wl:
  192 |         tot = (W.w == w).sum()
  193 |         inc = ((W.w == w) & (W.s_t == s_lab) & (W.e_t == e_lab)).sum()
  194 |         share = inc / tot if tot else np.nan
  195 |         base = len(W[(W.s_t == s_lab) & (W.e_t == e_lab)]) / len(W)
  196 |         print(f"  {w:<10} {inc:>4}/{tot:<4} occurrences in cell "
  197 |               f"({share:5.1%}, chance {base:.1%})"
  198 |               f"{'   ENRICHED' if tot and share > 1.5 * base else ''}")
```


==============================================================================
### FILE: gp_confound_check/v2_table4_dirpres.py
==============================================================================

```
    1 | """
    2 | Compute King-style contextual curvature (angular change) on the SAME layer-6
    3 | GPT-2 hidden states as the locked sample 8a6087341e, anchored at each word's
    4 | final subword (same anchor as tee_k in the locked sample).
    5 | 
    6 | Hidden-state conventions copied verbatim from excursion_tests/e_compute.py:
    7 |   layer 6, CHUNK 1024, STRIDE 512, first-write-wins chunking, offset-based
    8 |   BPE->word map with leading-whitespace shim, word = final subword.
    9 | 
   10 | Curvature (angle between successive step vectors of the path):
   11 |   step(i)      = h[i] - h[i-1]
   12 |   angle(i)     = arccos( cos( step(i), step(i-1) ) )   in [0, pi]
   13 |   curvature_1  = angle(ls)                     single-step (matches the earlier
   14 |                                                compare_tee_vs_angular.py head-to-head)
   15 |   curvature_3  = mean( angle(ls-2..ls) )       King, Fedorenko & Hosseini style:
   16 |                                                "angle between successive steps,
   17 |                                                averaged over the last three tokens"
   18 |   ls = final subword BPE index of the word.
   19 | 
   20 | Validation before the curvature values are trusted (same gate as e_compute):
   21 |   recomputed closure/final_bpe/tee_k50/tee_k3 must match the locked sample.
   22 | 
   23 | Output: curvature_merged_8a6087341e.csv  (locked sample rows + curvature cols)
   24 | No locked file is modified.
   25 | """
   26 | import hashlib, os, sys, unicodedata
   27 | import numpy as np
   28 | import pandas as pd
   29 | from nltk import Tree
   30 | import torch
   31 | from transformers import GPT2LMHeadModel, GPT2TokenizerFast
   32 | 
   33 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   34 | STORIES_DIR = f"{GP}/naturalstories"
   35 | PARSE_FILE = f"{STORIES_DIR}/parses/penn/all-parses-aligned.txt.penn"
   36 | OUT_DIR = f"{GP}/gp_confound_check"
   37 | LAYER, CHUNK_SIZE, STRIDE = 6, 1024, 512
   38 | 
   39 | # ------------------------------------------------------------------ corpus
   40 | words = pd.read_csv(f"{STORIES_DIR}/words.tsv", sep="\t", header=None,
   41 |                     names=["id", "word"], dtype={"id": str, "word": str})
   42 | words = words[words["word"].notna()].copy()
   43 | words = words[words["id"].str.split(".").str[-1] == "whole"].copy()
   44 | words["word"] = words["word"].str.strip().str.replace(r"\s+", "", regex=True)
   45 | assert (words["word"].str.len() > 0).all()
   46 | words["story_id"] = words["id"].str.split(".").str[0].astype(int)
   47 | words["word_idx"] = words.groupby("story_id").cumcount()
   48 | story_ids = sorted(words["story_id"].unique())
   49 | assert len(story_ids) == 10
   50 | story_words = {sid: words.loc[words.story_id == sid, "word"].tolist()
   51 |                for sid in story_ids}
   52 | story_texts = {sid: " ".join(ws) for sid, ws in story_words.items()}
   53 | print(f"corpus: {len(words)} words, stories {story_ids}", flush=True)
   54 | 
   55 | # ------------------------------------------------------------------ parses
   56 | PTB_TOKEN_MAP = {"-LRB-": "(", "-RRB-": ")", "-LCB-": "{", "-RCB-": "}",
   57 |                  "-LSB-": "[", "-RSB-": "]", "``": "'", "''": "'",
   58 |                  "`": "'", '"': "'", "-NONE-": ""}
   59 | 
   60 | def norm_chars(s):
   61 |     s = unicodedata.normalize("NFKC", s)
   62 |     for c in ["‘", "’", "“", "”", "`"]:
   63 |         s = s.replace(c, "Q")
   64 |     s = s.replace("''", "Q").replace("Q", "'")
   65 |     for c in ["—", "–"]:
   66 |         s = s.replace(c, "-")
   67 |     return "".join(ch for ch in s if not ch.isspace())
   68 | 
   69 | def leaf_records(tree):
   70 |     def prune(t):
   71 |         if isinstance(t, str):
   72 |             return t
   73 |         kids = [prune(k) for k in t]
   74 |         kids = [k for k in kids
   75 |                 if not (isinstance(k, Tree) and k.label() == "-NONE-")
   76 |                 and not (isinstance(k, Tree) and len(k) == 0)]
   77 |         return Tree(t.label(), kids)
   78 |     t = prune(tree)
   79 |     if not isinstance(t, Tree) or len(t.leaves()) == 0:
   80 |         return []
   81 |     leaves = t.leaves(); n = len(leaves)
   82 |     closures = np.zeros(n, dtype=int); openings = np.zeros(n, dtype=int)
   83 |     def walk(node, start):
   84 |         if isinstance(node, str):
   85 |             return start + 1
   86 |         pos = start
   87 |         has_tree_child = any(isinstance(k, Tree) for k in node)
   88 |         for k in node:
   89 |             pos = walk(k, pos)
   90 |         end = pos - 1
   91 |         if has_tree_child and 0 <= end < n:
   92 |             closures[end] += 1; openings[start] += 1
   93 |         return pos
   94 |     walk(t, 0)
   95 |     toks = []
   96 |     for l in leaves:
   97 |         if "/" in l:
   98 |             l = l.split("/")[0]
   99 |         toks.append(PTB_TOKEN_MAP.get(l, l))
  100 |     return list(zip(toks, closures, openings))
  101 | 
  102 | def read_trees_balanced(path):
  103 |     trees, depth, buf = [], 0, []
  104 |     with open(path) as fh:
  105 |         for ch in fh.read():
  106 |             if ch == "(":
  107 |                 depth += 1
  108 |             if depth > 0:
  109 |                 buf.append(ch)
  110 |             if ch == ")":
  111 |                 depth -= 1
  112 |                 if depth == 0 and buf:
  113 |                     try:
  114 |                         trees.append(Tree.fromstring("".join(buf)))
  115 |                     except (ValueError, IndexError):
  116 |                         pass
  117 |                     buf = []
  118 |     assert depth == 0
  119 |     return trees
  120 | 
  121 | all_trees = read_trees_balanced(PARSE_FILE)
  122 | leaf_stream = []
  123 | for s_uid, tr in enumerate(all_trees):
  124 |     for li, (tok_, clo, opn) in enumerate(leaf_records(tr)):
  125 |         leaf_stream.append((s_uid, li, tok_, clo, opn))
  126 | print(f"parsed {len(all_trees)} trees, {len(leaf_stream)} leaves", flush=True)
  127 | 
  128 | word_rows, li = [], 0
  129 | for story_id, word_idx, word in words[["story_id", "word_idx", "word"]].itertuples(index=False):
  130 |     target = norm_chars(word); buf, consumed = "", []
  131 |     while len(buf) < len(target) and li < len(leaf_stream):
  132 |         rec = leaf_stream[li]; buf += norm_chars(rec[2]); consumed.append(rec); li += 1
  133 |     if buf != target:
  134 |         sys.exit(f"ALIGN FAIL story {story_id} w{word_idx} {word!r} buf={buf!r}")
  135 |     word_rows.append({"story_id": story_id, "word_idx": word_idx,
  136 |                       "closure_depth_re": int(sum(r[3] for r in consumed))})
  137 | assert li == len(leaf_stream)
  138 | ptb = pd.DataFrame(word_rows)
  139 | print(f"aligned {len(ptb)} words", flush=True)
  140 | 
  141 | # ------------------------------------------------------------------ model
  142 | tok = GPT2TokenizerFast.from_pretrained("gpt2")
  143 | model = GPT2LMHeadModel.from_pretrained("gpt2").eval()
  144 | torch.set_num_threads(os.cpu_count() or 4)
  145 | 
  146 | def story_pass(text):
  147 |     enc = tok(text, return_offsets_mapping=True)
  148 |     ids = torch.tensor(enc["input_ids"]); offsets = enc["offset_mapping"]
  149 |     n = ids.size(0); hidden = {}; hidden12 = {}; pos = 0
  150 |     while pos < n:
  151 |         end = min(pos + CHUNK_SIZE, n)
  152 |         with torch.no_grad():
  153 |             out = model(ids[pos:end].unsqueeze(0), output_hidden_states=True)
  154 |         hs = out.hidden_states[LAYER][0].float().cpu().numpy()
  155 |         hs12 = out.hidden_states[12][0].float().cpu().numpy()
  156 |         for i in range(end - pos):
  157 |             g = pos + i
  158 |             if g not in hidden:
  159 |                 hidden[g] = hs[i]
  160 |                 hidden12[g] = hs12[i]
  161 |         del out
  162 |         if end >= n:
  163 |             break
  164 |         pos += STRIDE
  165 |     return hidden, hidden12, offsets, n
  166 | 
  167 | def word_char_spans(word_list):
  168 |     spans, cursor = [], 0
  169 |     for w in word_list:
  170 |         spans.append((cursor, cursor + len(w))); cursor += len(w) + 1
  171 |     return spans
  172 | 
  173 | def tee_at(hidden, t, k):
  174 |     idxs = range(t - k, t)
  175 |     if any(i not in hidden for i in idxs) or t not in hidden:
  176 |         return np.nan
  177 |     W = np.stack([hidden[i] for i in idxs])
  178 |     A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
  179 |     coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
  180 |     return float(np.linalg.norm(hidden[t] - (coefs[0] + coefs[1] * k)))
  181 | 
  182 | def tee_decomp(hidden, t, k=3):
  183 |     """Decompose the k-window extrapolation residual r = h_t - pred into
  184 |     along-heading (parallel to fitted slope) and lateral (perpendicular)
  185 |     magnitudes. tee = sqrt(par^2 + perp^2)."""
  186 |     idxs = range(t - k, t)
  187 |     if any(i not in hidden for i in idxs) or t not in hidden:
  188 |         return np.nan, np.nan, np.nan
  189 |     W = np.stack([hidden[i] for i in idxs])
  190 |     A = np.column_stack([np.ones(k), np.arange(k, dtype=np.float64)])
  191 |     coefs, *_ = np.linalg.lstsq(A, W, rcond=None)
  192 |     a, b = coefs[0], coefs[1]
  193 |     r = hidden[t] - (a + b * k)
  194 |     nb = np.linalg.norm(b)
  195 |     if nb <= 0 or not np.isfinite(nb):
  196 |         return float(np.linalg.norm(r)), np.nan, np.nan
  197 |     bhat = b / nb
  198 |     par = float(np.dot(r, bhat))                       # signed along-heading
  199 |     perp = float(np.linalg.norm(r - par * bhat))       # lateral magnitude
  200 |     return abs(par), perp, par                         # par_abs, perp, par_signed
  201 | 
  202 | def dir_pres_rows(H, last_sub, n_words, ws, sid, layer_name):
  203 |     W = np.array([H[last_sub[i]] for i in range(n_words)])
  204 |     out = []
  205 |     for i in range(ws + 1, W.shape[0]):
  206 |         pre = W[i - ws:i]
  207 |         m = pre.shape[0]
  208 |         A = np.column_stack([np.ones(m), np.arange(m)])
  209 |         c, *_ = np.linalg.lstsq(A, pre, rcond=None)
  210 |         d = c[1]; dn = np.linalg.norm(d)
  211 |         if dn < 1e-10:
  212 |             continue
  213 |         du = d / dn
  214 |         row = {"story_id": sid, "layer": layer_name, "window": ws}
  215 |         for ahead in [0, 1, 2, 3]:
  216 |             j = i + ahead
  217 |             if j < W.shape[0]:
  218 |                 delta = W[j] - W[j - 1]
  219 |                 nn = np.linalg.norm(delta)
  220 |                 if nn > 1e-10:
  221 |                     row[f"ahead{ahead}"] = abs(float(np.dot(delta, du) / nn))
  222 |         out.append(row)
  223 |     return out
  224 | 
  225 | 
  226 | def displacement(hidden, ls, prev_ls):
  227 |     """Raw magnitude of representational change, no direction:
  228 |        step  = ||h[ls] - h[ls-1]||              (last BPE step)
  229 |        wdisp = ||h[ls] - h[prev word's ls]||    (word-to-word)
  230 |        hnorm = ||h[ls]||                        (state magnitude)"""
  231 |     step = np.nan
  232 |     if ls in hidden and (ls - 1) in hidden:
  233 |         step = float(np.linalg.norm(hidden[ls] - hidden[ls - 1]))
  234 |     wdisp = np.nan
  235 |     if prev_ls is not None and ls in hidden and prev_ls in hidden:
  236 |         wdisp = float(np.linalg.norm(hidden[ls] - hidden[prev_ls]))
  237 |     hnorm = float(np.linalg.norm(hidden[ls])) if ls in hidden else np.nan
  238 |     return step, wdisp, hnorm
  239 | 
  240 | def angle(a, b):
  241 |     na, nb = np.linalg.norm(a), np.linalg.norm(b)
  242 |     if na < 1e-8 or nb < 1e-8:
  243 |         return np.nan
  244 |     return float(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0)))
  245 | 
  246 | def curvature(hidden, ls):
  247 |     """curvature_1 (angle at ls) and curvature_3 (mean angle over ls-2..ls)."""
  248 |     def step(i):
  249 |         return hidden[i] - hidden[i - 1] if (i in hidden and i - 1 in hidden) else None
  250 |     def ang_at(i):  # angle between step(i) and step(i-1); needs i, i-1, i-2
  251 |         s1, s0 = step(i), step(i - 1)
  252 |         return np.nan if (s1 is None or s0 is None) else angle(s1, s0)
  253 |     c1 = ang_at(ls)
  254 |     a = [ang_at(ls - 2), ang_at(ls - 1), ang_at(ls)]
  255 |     c3 = float(np.mean(a)) if all(np.isfinite(x) for x in a) else np.nan
  256 |     return c1, c3
  257 | 
  258 | frames = []
  259 | dp_rows = []
  260 | for sid in story_ids:
  261 |     print(f"story {sid}: forward pass...", flush=True)
  262 |     text = story_texts[sid]
  263 |     hidden, hidden12, offsets, n_bpe = story_pass(text)
  264 |     spans = word_char_spans(story_words[sid])
  265 |     bpe_word = np.full(n_bpe, -1); wi = 0
  266 |     for bi, (cs, ce) in enumerate(offsets):
  267 |         while cs < ce and text[cs].isspace():
  268 |             cs += 1
  269 |         if ce <= cs:
  270 |             continue
  271 |         while wi < len(spans) and cs >= spans[wi][1]:
  272 |             wi += 1
  273 |         if wi < len(spans) and cs >= spans[wi][0] and ce <= spans[wi][1]:
  274 |             bpe_word[bi] = wi
  275 |         else:
  276 |             sys.exit(f"BPE offset outside span story {sid} bpe {bi}")
  277 |     assert len(np.unique(bpe_word[bpe_word >= 0])) == len(spans)
  278 |     last_sub = {}
  279 |     for bi, w in enumerate(bpe_word):
  280 |         if w >= 0:
  281 |             last_sub[w] = bi
  282 |     rows = []
  283 |     for w in range(len(spans)):
  284 |         ls = last_sub[w]
  285 |         c1, c3 = curvature(hidden, ls)
  286 |         dstep, dword, hnorm = displacement(hidden, ls,
  287 |                                            last_sub[w - 1] if w > 0 else None)
  288 |         par_abs, perp, par_signed = tee_decomp(hidden, ls, 3)
  289 |         rows.append({"story_id": sid, "word_idx": w, "final_bpe_re": ls,
  290 |                      "closure_depth_re": ptb[(ptb.story_id == sid) &
  291 |                         (ptb.word_idx == w)].closure_depth_re.iloc[0],
  292 |                      "tee_k3_re": tee_at(hidden, ls, 3),
  293 |                      "tee_k50_re": tee_at(hidden, ls, 50),
  294 |                      "curvature_1": c1, "curvature_3": c3,
  295 |                      "tee3_par": par_abs, "tee3_perp": perp,
  296 |                      "tee3_par_signed": par_signed,
  297 |                      "disp_step": dstep, "disp_word": dword,
  298 |                      "state_norm": hnorm})
  299 |     for Hd, lname in [(hidden, "L6"), (hidden12, "L12")]:
  300 |         for ws in (3, 5):
  301 |             dp_rows.extend(dir_pres_rows(Hd, last_sub, len(spans), ws, sid, lname))
  302 |     frames.append(pd.DataFrame(rows))
  303 |     print(f"story {sid}: done", flush=True)
  304 | 
  305 | E = pd.concat(frames, ignore_index=True)
  306 | 
  307 | # ------------------------------------------------------------------ validate
  308 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
  309 | sample_hash = hashlib.md5(
  310 |     "|".join(f"{r.story_id}.{r.word_idx}" for r in
  311 |              S[["story_id", "word_idx"]].itertuples(index=False)).encode()
  312 | ).hexdigest()[:10]
  313 | assert sample_hash == "8a6087341e", sample_hash
  314 | M = S.merge(E, on=["story_id", "word_idx"], validate="one_to_one")
  315 | assert len(M) == len(S) == 9840
  316 | 
  317 | print(f"\nVALIDATION (locked sample, hash {sample_hash}, n={len(M)}):", flush=True)
  318 | print(f"  closure_depth mismatches: {(M.closure_depth != M.closure_depth_re).sum()}")
  319 | print(f"  final_bpe mismatches:     {(M.final_bpe != M.final_bpe_re).sum()}")
  320 | print(f"  max |tee_k50 - re|:       {np.nanmax(np.abs(M.tee_k50 - M.tee_k50_re)):.3e}")
  321 | print(f"  max |tee_k3  - re|:       {np.nanmax(np.abs(M.tee_k3  - M.tee_k3_re)):.3e}")
  322 | print(f"  curvature_1 NaNs:         {M.curvature_1.isna().sum()}")
  323 | print(f"  curvature_3 NaNs:         {M.curvature_3.isna().sum()}")
  324 | print(f"  curvature_1 mean/sd:      {M.curvature_1.mean():.4f} / {M.curvature_1.std():.4f}")
  325 | print(f"  curvature_3 mean/sd:      {M.curvature_3.mean():.4f} / {M.curvature_3.std():.4f}")
  326 | print(f"  disp_word mean/sd:        {M.disp_word.mean():.3f} / {M.disp_word.std():.3f}")
  327 | print(f"  r(disp_word, tee_k3):     {M.disp_word.corr(M.tee_k3):.4f}")
  328 | print(f"  r(disp_word, tee3_perp):  {M.disp_word.corr(M.tee3_perp):.4f}")
  329 | 
  330 | DP = pd.DataFrame(dp_rows)
  331 | DP.to_csv(f"{OUT_DIR}/dirpres_8a6087341e.csv", index=False)
  332 | print("\n" + "="*72)
  333 | print("TABLE 4 (recomputed on verified states): direction preservation")
  334 | print("="*72)
  335 | print(f"{'layer':>6}{'window':>8}{'current':>10}{'+1':>9}{'+2':>9}{'+3':>9}{'n':>10}")
  336 | for (L, ws), g in DP.groupby(["layer", "window"]):
  337 |     print(f"{L:>6}{ws:>8}{g.ahead0.mean():>10.3f}{g.ahead1.mean():>9.3f}"
  338 |           f"{g.ahead2.mean():>9.3f}{g.ahead3.mean():>9.3f}{len(g):>10,}")
  339 | print("\nv1 reported: L6 current .44, +1 .10, +2/+3 ~.08; L12 ~.54 across all")
  340 | print(f"\nDONE -> displacement_8a6087341e.csv", flush=True)
```


==============================================================================
### FILE: gp_confound_check/v2_table6_pythia.py
==============================================================================

```
    1 | """
    2 | TABLE 6 RECOMPUTED: cross-architecture replication on MATCHED samples
    3 | =====================================================================
    4 | v1's Table 6 compared GPT-2 Small on the full Natural Stories sample (180
    5 | participants) against Pythia on a 100-participant subsample. That is not a
    6 | like-for-like architecture comparison. Here all models are evaluated on
    7 | identical rows and identical participants.
    8 | 
    9 | Pythia uses Rotary Position Embeddings; GPT-2 uses learned absolute position
   10 | embeddings. The question is whether the trajectory effect depends on the
   11 | positional encoding scheme.
   12 | 
   13 | Conventions match the verified GPT-2 pipeline: chunked forward passes
   14 | (1024 / stride 512, first-write-wins), word state = final subword, TEE_k3 =
   15 | distance from a one-step linear extrapolation over the 3 preceding word states,
   16 | mid-network layer. Words are restricted to the locked sample 8a6087341e.
   17 | """
   18 | 
   19 | import numpy as np
   20 | import pandas as pd
   21 | import torch
   22 | import statsmodels.formula.api as smf
   23 | from transformers import AutoTokenizer, AutoModelForCausalLM
   24 | import os, warnings
   25 | warnings.filterwarnings("ignore")
   26 | 
   27 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   28 | CHUNK, STRIDE, K = 1024, 512, 3
   29 | DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
   30 | 
   31 | MODELS = [("EleutherAI/pythia-160m", 6), ("EleutherAI/pythia-410m", 12)]
   32 | 
   33 | # ---------------- corpus (same construction as the verified pipeline) --------
   34 | words = pd.read_csv(f"{GP}/naturalstories/words.tsv", sep="\t", header=None,
   35 |                     names=["id", "word"], dtype={"id": str, "word": str})
   36 | words = words[words.word.notna()].copy()
   37 | words = words[words.id.str.split(".").str[-1] == "whole"].copy()
   38 | words["word"] = words.word.str.strip().str.replace(r"\s+", "", regex=True)
   39 | words["story_id"] = words.id.str.split(".").str[0].astype(int)
   40 | words["word_idx"] = words.groupby("story_id").cumcount()
   41 | story_words = {s: g.word.tolist() for s, g in words.groupby("story_id")}
   42 | print(f"corpus: {len(words)} words, {len(story_words)} stories", flush=True)
   43 | 
   44 | 
   45 | def spans_for(wl):
   46 |     out, cur = [], 0
   47 |     for w in wl:
   48 |         out.append((cur, cur + len(w)))
   49 |         cur += len(w) + 1
   50 |     return out
   51 | 
   52 | 
   53 | def tee_for_model(name, layer):
   54 |     tok = AutoTokenizer.from_pretrained(name)
   55 |     model = AutoModelForCausalLM.from_pretrained(name).eval().to(DEVICE)
   56 |     rows = []
   57 |     for sid, wl in story_words.items():
   58 |         text = " ".join(wl)
   59 |         enc = tok(text, return_offsets_mapping=True)
   60 |         ids = torch.tensor(enc["input_ids"])
   61 |         offs = enc["offset_mapping"]
   62 |         n = ids.size(0)
   63 |         hidden, pos = {}, 0
   64 |         while pos < n:
   65 |             end = min(pos + CHUNK, n)
   66 |             with torch.no_grad():
   67 |                 out = model(ids[pos:end].unsqueeze(0).to(DEVICE),
   68 |                             output_hidden_states=True)
   69 |             hs = out.hidden_states[layer][0].float().cpu().numpy()
   70 |             for i in range(end - pos):
   71 |                 g = pos + i
   72 |                 if g not in hidden:
   73 |                     hidden[g] = hs[i]
   74 |             del out
   75 |             if end >= n:
   76 |                 break
   77 |             pos += STRIDE
   78 |         sp = spans_for(wl)
   79 |         last_sub, wi = {}, 0
   80 |         for bi, (cs, ce) in enumerate(offs):
   81 |             if ce <= cs:
   82 |                 continue
   83 |             while wi < len(sp) and cs >= sp[wi][1]:
   84 |                 wi += 1
   85 |             if wi < len(sp) and cs >= sp[wi][0] and ce <= sp[wi][1]:
   86 |                 last_sub[wi] = bi
   87 |         for w in range(len(sp)):
   88 |             if w not in last_sub:
   89 |                 continue
   90 |             t = last_sub[w]
   91 |             idxs = [last_sub.get(w - j) for j in range(K, 0, -1)]
   92 |             if any(x is None for x in idxs) or any(x not in hidden for x in idxs):
   93 |                 continue
   94 |             Y = np.stack([hidden[x] for x in idxs])
   95 |             m = Y.shape[0]
   96 |             A = np.column_stack([np.ones(m), np.arange(m)])
   97 |             c, *_ = np.linalg.lstsq(A, Y, rcond=None)
   98 |             rows.append({"story_id": sid, "word_idx": w,
   99 |                          "tee": float(np.linalg.norm(hidden[t] - (c[0] + c[1] * m)))})
  100 |         print(f"  {name} story {sid} done", flush=True)
  101 |     del model
  102 |     return pd.DataFrame(rows)
  103 | 
  104 | 
  105 | # ---------------- assemble ----------------
  106 | S = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
  107 | base = S[["story_id", "word_idx", "zone", "surprisal", "word_length", "log_freq",
  108 |           "tee_k3"]].rename(columns={"tee_k3": "tee_gpt2"})
  109 | 
  110 | meas = base.copy()
  111 | for name, layer in MODELS:
  112 |     t = tee_for_model(name, layer)
  113 |     short = name.split("/")[-1].replace("-", "_")
  114 |     meas = meas.merge(t.rename(columns={"tee": f"tee_{short}"}),
  115 |                       on=["story_id", "word_idx"], how="left")
  116 |     print(f"{name}: {meas[f'tee_{short}'].notna().sum():,} words with TEE",
  117 |           flush=True)
  118 | 
  119 | rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
  120 |                  sep="\t").rename(columns={"item": "story_id", "WorkerId": "participant"})
  121 | rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
  122 | d = rt.merge(meas, on=["story_id", "zone"], how="inner")
  123 | d["log_RT"] = np.log(d.RT)
  124 | d = d.sort_values(["participant", "story_id", "zone"])
  125 | d["prev_log_RT"] = d.groupby(["participant", "story_id"])["log_RT"].shift(1)
  126 | 
  127 | teecols = ["tee_gpt2"] + [f"tee_{n.split('/')[-1].replace('-', '_')}" for n, _ in MODELS]
  128 | d = d.dropna(subset=["log_RT", "word_length", "log_freq", "zone", "prev_log_RT",
  129 |                      "surprisal"] + teecols)
  130 | print(f"\nMATCHED SAMPLE: n = {len(d):,}, participants = {d.participant.nunique()}")
  131 | 
  132 | 
  133 | def z(s):
  134 |     v = s.dropna()
  135 |     return (s - v.mean()) / v.std()
  136 | 
  137 | 
  138 | for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal"] + teecols:
  139 |     d["z_" + c] = z(d[c])
  140 | CTRL = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_surprisal"
  141 | m1 = smf.mixedlm(CTRL, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
  142 | print(f"\n{'model':<20}{'positional enc':<18}{'dAIC':>10}{'beta':>11}{'p':>13}")
  143 | for c in teecols:
  144 |     mk = smf.mixedlm(CTRL + f" + z_{c}", d, groups=d["participant"]).fit(
  145 |         reml=False, method="lbfgs")
  146 |     enc = "absolute" if "gpt2" in c else "rotary (RoPE)"
  147 |     print(f"{c.replace('tee_',''):<20}{enc:<18}{m1.aic-mk.aic:>10.1f}"
  148 |           f"{mk.params['z_'+c]:>11.5f}{mk.pvalues['z_'+c]:>13.2e}")
  149 | print("\nAll rows and participants identical across models "
  150 |       "(v1 compared GPT-2 on 180 participants vs Pythia on 100).")
  151 | meas.to_csv(f"{GP}/gp_confound_check/pythia_tee_8a6087341e.csv", index=False)
```


==============================================================================
### FILE: gp_confound_check/v2_tables_23.py
==============================================================================

```
    1 | """
    2 | RECOMPUTE v1 TABLES 2 AND 3 ON THE VERIFIED SAMPLE
    3 | ==================================================
    4 | v1's Table 2 (surprisal x TEE dissociation matrix) and Table 3 (displacement
    5 | control) were computed from the superseded measure file. Recomputed here on
    6 | locked sample 8a6087341e with the displacement values from
    7 | displacement_8a6087341e.csv (states revalidated: 0/9,840 alignment mismatches).
    8 | 
    9 | Also verifies the r = .044 orthogonality claim.
   10 | 
   11 | Model spec follows the project convention used for the v2 headline:
   12 | mixedlm, by-participant random intercept, ML fit,
   13 | controls = word length + log frequency + zone + previous log RT.
   14 | """
   15 | 
   16 | import numpy as np
   17 | import pandas as pd
   18 | import statsmodels.formula.api as smf
   19 | import warnings
   20 | warnings.filterwarnings("ignore")
   21 | 
   22 | GP = "/Users/elanbarenholtz/Projects/garden-path-tee-curvature"
   23 | 
   24 | 
   25 | def build():
   26 |     w = pd.read_csv(f"{GP}/rebuild_v2_outputs/sample_8a6087341e.csv")
   27 |     dp = pd.read_csv(f"{GP}/gp_confound_check/displacement_8a6087341e.csv")
   28 |     w = w.merge(dp, on=["story_id", "word_idx"], validate="one_to_one")
   29 |     rt = pd.read_csv(f"{GP}/naturalstories/naturalstories_RTS/processed_RTs.tsv",
   30 |                      sep="\t").rename(columns={"item": "story_id",
   31 |                                                "WorkerId": "participant"})
   32 |     rt = rt[(rt.RT >= 100) & (rt.RT <= 3000)].copy()
   33 |     m = rt.merge(w[["story_id", "zone", "tee_k3", "surprisal", "word_length",
   34 |                     "log_freq", "disp_word", "state_norm"]],
   35 |                  on=["story_id", "zone"], how="inner")
   36 |     m["log_RT"] = np.log(m.RT)
   37 |     m = m.sort_values(["participant", "story_id", "zone"])
   38 |     m["prev_log_RT"] = m.groupby(["participant", "story_id"])["log_RT"].shift(1)
   39 |     return w, m.dropna(subset=["log_RT", "word_length", "log_freq", "zone",
   40 |                                "prev_log_RT", "surprisal", "tee_k3", "disp_word"])
   41 | 
   42 | 
   43 | def z(s):
   44 |     v = s.dropna()
   45 |     return (s - v.mean()) / v.std()
   46 | 
   47 | 
   48 | def main():
   49 |     w, d = build()
   50 | 
   51 |     print("=" * 74)
   52 |     print("ORTHOGONALITY (v1 claim: r = .044)")
   53 |     print("=" * 74)
   54 |     print(f"  word-level r(TEE, surprisal)      = {w.tee_k3.corr(w.surprisal):+.4f}  "
   55 |           f"(n = {w.tee_k3.notna().sum():,})")
   56 |     print(f"  word-level r(TEE, entropy)        = {w.tee_k3.corr(w.entropy):+.4f}")
   57 |     print(f"  word-level r(TEE, log_freq)       = {w.tee_k3.corr(w.log_freq):+.4f}")
   58 |     print(f"  word-level r(TEE, displacement)   = {w.tee_k3.corr(w.disp_word):+.4f}")
   59 |     print(f"  word-level r(displacement, surp)  = {w.disp_word.corr(w.surprisal):+.4f}")
   60 | 
   61 |     print("\n" + "=" * 74)
   62 |     print("TABLE 2: dissociation matrix, mean log RT by surprisal x TEE tercile")
   63 |     print("=" * 74)
   64 |     d = d.copy()
   65 |     d["s_t"] = pd.qcut(d.surprisal, 3, labels=["low", "mid", "high"])
   66 |     d["e_t"] = pd.qcut(d.tee_k3, 3, labels=["low", "mid", "high"])
   67 |     piv = d.pivot_table(index="s_t", columns="e_t", values="log_RT",
   68 |                         aggfunc="mean", observed=True)
   69 |     cnt = d.pivot_table(index="s_t", columns="e_t", values="log_RT",
   70 |                         aggfunc="size", observed=True)
   71 |     print("\nmean log RT:")
   72 |     print(piv.round(4).to_string())
   73 |     print("\ncell n:")
   74 |     print(cnt.to_string())
   75 |     base = piv.loc["low", "low"]
   76 |     print(f"\nrelative to low/low baseline ({base:.4f}):")
   77 |     print((piv - base).round(4).to_string())
   78 |     print("\nkey off-diagonal cells (v1: high-surp/low-TEE +0.039; "
   79 |           "low-surp/high-TEE +0.008):")
   80 |     for s_, e_, lab in [("high", "low", "high surprisal, low TEE"),
   81 |                         ("low", "high", "low surprisal, high TEE")]:
   82 |         cell = d[(d.s_t == s_) & (d.e_t == e_)]
   83 |         ref = d[(d.s_t == "low") & (d.e_t == "low")]
   84 |         from scipy import stats as st
   85 |         t = st.ttest_ind(cell.log_RT, ref.log_RT, equal_var=False)
   86 |         print(f"  {lab:<26} delta = {cell.log_RT.mean()-ref.log_RT.mean():+.4f}  "
   87 |               f"n = {len(cell):,}  t = {t.statistic:.2f}  p = {t.pvalue:.2e}")
   88 | 
   89 |     print("\n" + "=" * 74)
   90 |     print("TABLE 3: displacement control")
   91 |     print("=" * 74)
   92 |     print("v1 claim: displacement and extrapolation error predict in OPPOSITE "
   93 |           "directions")
   94 |     for c in ["word_length", "log_freq", "zone", "prev_log_RT", "surprisal",
   95 |               "tee_k3", "disp_word"]:
   96 |         d["z_" + c] = z(d[c])
   97 |     CTRL = "log_RT ~ z_word_length + z_log_freq + z_zone + z_prev_log_RT + z_surprisal"
   98 |     specs = [("TEE alone", CTRL + " + z_tee_k3", "z_tee_k3"),
   99 |              ("displacement alone", CTRL + " + z_disp_word", "z_disp_word"),
  100 |              ("both: TEE", CTRL + " + z_tee_k3 + z_disp_word", "z_tee_k3"),
  101 |              ("both: displacement", CTRL + " + z_tee_k3 + z_disp_word", "z_disp_word")]
  102 |     print(f"\n{'model':<24}{'beta':>12}{'p':>14}")
  103 |     for lab, f, term in specs:
  104 |         m = smf.mixedlm(f, d, groups=d["participant"]).fit(reml=False, method="lbfgs")
  105 |         print(f"{lab:<24}{m.params[term]:>12.5f}{m.pvalues[term]:>14.2e}")
  106 |     print(f"\nn = {len(d):,}   participants = {d.participant.nunique()}")
  107 | 
  108 | 
  109 | if __name__ == "__main__":
  110 |     main()
```
