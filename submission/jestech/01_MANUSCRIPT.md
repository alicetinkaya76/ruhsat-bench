# RUHSAT-Bench — JESTECH ana metin

**Title.** Measuring abstention, not accuracy: a re-qualification benchmark for
language-model decision support on Turkish construction and occupational-safety
regulation

**Author.** Ali Çetinkaya <sup>a,\*</sup>

<sup>a</sup> Department of Computer Engineering, Faculty of Technology,
Selçuk University, Konya, Türkiye
ORCID: 0000-0002-7747-6854

<sup>\*</sup> Corresponding author. E-mail: ali.cetinkaya@selcuk.edu.tr

> **Note on structure.** Nine supplementary sections, referred to below as S1–S9,
> carry the full model-by-model listings, the pre-registration compliance record,
> the family-size and corpus sensitivity analyses, the probe-subtype breakdowns
> and the complete expert-audit report. The number sheet mapping each figure to
> the script that produced it is in the released archive rather than in either
> document. This paper contains tables and no plotted figures: every quantity it
> reports is a point estimate with an interval, and we found no chart that carried
> more than the table it would have been drawn from.

---

## Abstract

Decision-support software used in regulatory compliance checking is qualified
before it is trusted, and a qualification asks not only how often a tool is right
but whether it declines the cases it cannot handle. We report RUHSAT-Bench, a
benchmark of 473 true/false claims over six frozen Turkish regulatory documents —
the Development Law, the Building Inspection Law and its implementing regulation,
the Occupational Health and Safety Law and its risk-assessment regulation, and
the Turkish Building Earthquake Code TBDY 2018 — scored under two conditions: one
permitting an explicit "not sure" (E1) and one forcing a binary verdict (E2).
Gold labels were audited by two domain specialists in two blinded passes and the
audit is reported in full, including its negative result.

Three findings are reported. First, closed book, the systems tested sit at a
coverage–accuracy trade-off rather than at a uniform failure: of eighteen
open-weight configurations, twelve carry a scored accuracy figure and, after the
pre-registered Bonferroni correction, **one** excludes chance robustly. A second
sits on the threshold, clearing it by 0.0017 under the reported seed and failing
to under three of five, and we report it as undecided rather than as a
survivor. Second, supplying the governing text changes the
operating point decisively. On the pre-registered primary family, a 32B
open-weight model gains +0.2607 in balanced accuracy under forced choice when
three retrieved passages are supplied (95% CI [+0.2218, +0.2964]) and +0.3552
when the cited article is supplied (95% CI [+0.3112, +0.3984]); both survive
correction. Against a string-matching rule applied to the *same* retrieved
passages, the model adds +0.2292 under E1 (95% CI [+0.1939, +0.2635]), so the
judgement step is separable from the presence of evidence. Third, and this is the
qualification result: a hosted model re-run about four weeks later on the same
frozen claim set, at the same budget and with byte-identical prompts, kept its
forced-choice accuracy inside its archived range while its abstention-permitted
accuracy fell outside it, and the condition contrast moved from an archive mean
of 0.0762 to 0.0332 while the number of abstentions barely changed. That drop is
a point estimate: a paired interval on the change is −0.0434 [−0.0986, +0.0118]
and contains zero, so the *size* of the change is not separable from resampling
noise, and we report it as an observation on a frozen test set rather than as an
established effect. What the observation does show is that the two conditions
moved differently — which is the property a forced-choice benchmark cannot
register at all.

We draw a conclusion about measurement rather than a verdict on the technology.
On this claim set and these six documents, closed-book operation of the systems
we tested does not support a compliance decision; retrieval-grounded operation
reaches a materially different operating point; and neither observation
establishes an acceptance threshold, which we argue is not a quantity a benchmark
can supply. What the paper does claim is that an acceptance criterion has to be
stated over abstention behaviour and re-checked over time, because forced-choice
accuracy did not detect a change we could measure by other means.

**Keywords.** compliance checking; decision-support software qualification;
abstention; selective prediction; large language models; building regulation

---

# 1. Introduction

Turkish building inspection runs on documents. A project is checked against the
Development Law No. 3194, the Building Inspection Law No. 4708 and its
implementing regulation, the Occupational Health and Safety Law No. 6331 and its
risk-assessment regulation, and, for structural design, the Turkish Building
Earthquake Code TBDY 2018. The work is textual — locating the governing
provision, reading it against a design or a site condition, and recording a
verdict — and it is exactly the shape of work that language-model assistants are
now offered for. What is at stake in getting it right is not abstract: post-event
surveys of the February 2023 Kahramanmaraş earthquakes attribute a large share of
reinforced-concrete building damage to design and construction deficiencies of
the kind code compliance is meant to prevent (Turan et al., 2024).

Before such an assistant is used in an inspection workflow it has to be
qualified, in the ordinary engineering sense: someone has to state what evidence
would justify relying on it, gather that evidence, and define what would trigger
re-checking. This paper is about the measurement that a qualification of this
kind requires. It is not about which model is best.

Automating this kind of check is not a new goal. Rule-based checking of building
designs has a long line of work behind it (Eastman et al., 2009; Solihin and
Eastman, 2015), and the bottleneck it repeatedly meets is getting the rules out of
the prose: extracting checkable structure from regulatory text has been pursued
with semantic NLP (Zhang and El-Gohary, 2016) and with ontology-based extraction
from energy codes (Zhou and El-Gohary, 2017); the same ontological move has been
applied to standard measurement rules so that BIM tools can act on them
(Abanda et al., 2017). Language models change the shape of
that bottleneck rather than removing it, and recent work has begun to combine them
with rule checking for BIM compliance (Chen et al., 2024). What has also become
clear, from the adjacent legal domain, is that fluent output is a poor guide to
correctness: hallucination rates in legal question answering are substantial
(Dahl et al., 2024), and even retrieval-grounded commercial legal research tools
do not eliminate them (Magesh et al., 2025). That is the pairing this paper takes
as its starting point — a task where the text is the ground truth, and a tool
class whose errors do not announce themselves.

Our claim is that for this class of tool the qualification criterion cannot be
accuracy alone. A compliance check has two failure modes and they are not
equivalent. A tool that says "I cannot resolve this" hands the case to a person;
a tool that answers wrongly with the same fluency it uses when right does not.
The first is a fail-safe failure and the second is fail-silent, and functional
safety practice has treated the distinction as fundamental for decades
(IEC 61508). Meeting the verification obligations such standards impose is itself
an engineering problem rather than a formality — the cost of demonstrating
compliance is what usually decides whether a method is adopted (Makartetskiy et
al., 2020) — and the argument of this paper is that for a language-model
assistant the demonstration has to be about abstention. A benchmark that forces a binary answer measures the second mode and
is blind to the first. So we measure both, under two conditions on the same
claims: one that permits an explicit "not sure", and one that forbids it.

The instrument is RUHSAT-Bench: 473 true/false claims over the six documents
above, generated from frozen source text by a sealed script, labelled by that
script and then audited by two domain specialists in two blinded passes. Claims
fall into six probe families that separate distinct failure modes — direct
assertion, numeric alteration, cross-reference (real text attributed to the wrong
provision), currency of amendment, anachronism, and fabricated provision — so
that an aggregate score can be decomposed rather than trusted whole.

**Contributions.**

1. *A regulatory benchmark for Turkish construction law with auditable
   provenance.* Every reported figure is regenerated from committed script
   outputs. The claim set, the three gold-label versions, the pre-registration
   with its eight annexes and the expert-audit record — including its negative
   result — are released with the code. Deviations from the pre-registration are
   declared in §3 and their consequences are measured, not asserted (S2).

2. *A measured coverage–accuracy trade-off among open-weight models rather than a
   blanket failure.* Eighteen open-weight configurations produced an E1 cell
   under prompt variant A; twelve are scored, after two are removed by the
   pre-registered response-rate gate and four are withheld for committing on
   fewer than 30 items. With uncorrected intervals four of the twelve exclude
   chance; after the pre-registered Bonferroni correction, **one** does so
   robustly — `qwen2.5:32b-instruct` (balanced accuracy 0.6769, corrected lower
   bound 0.5349 under the reported seed and above 0.5 under all five seeds
   tested, at coverage 0.173). `gemma3:27b` (0.5674, corrected lower bound
   0.5017, coverage 0.970) clears chance by 0.0017 under the reported seed and
   fails to under three of five, so its verdict is seed-dependent and it is
   reported as undecided. The two operating points are opposite: one answers a sixth of the
   claims well, the other nearly all of them barely above chance (§4.2, S3).

3. *Abstention as a measured quantity rather than an assumed safety feature.* The
   confirmatory contrast BAcc(E1) − BAcc(E2) is item 1.2 of the main
   pre-registration, corrected by Bonferroni over the number of models run
   (twenty, giving 99.75% intervals): for `claude-sonnet-5` it is +0.0678
   [+0.0018, +0.1359], excluding zero though by less than two thousandths of a
   point; for `claude-haiku-4.5` it is −0.0260 [−0.0765, +0.0377], which does
   not. The verdict is unchanged for every family size from two to twenty-one
   (S4). Abstention is worth something for one hosted model and nothing
   measurable for the other.

4. *A re-qualification result.* Re-running one hosted configuration on the frozen
   claim set about four weeks later, at the same budget and with prompts verified
   byte-identical, leaves forced-choice accuracy inside its archived range and
   moves the abstention-permitted figure outside it. Abstention frequency held
   (182.33 archived mean against 178) while the confirmatory contrast fell from an
   archive mean of 0.0762 to 0.0332. A paired interval on that change is
   −0.0434 [−0.0986, +0.0118] and contains zero, so the size of the drop is not
   established; what the run shows is that the two conditions moved differently
   on a frozen claim set (§4.4).

5. *A grounded-arm measurement showing that the closed-book figures describe a
   mode of use, not a ceiling on the task.* For `qwen2.5:32b-instruct`, supplying
   the cited article raises balanced accuracy to 0.9164 [0.8804, 0.9494] under E1
   and 0.8615 [0.8207, 0.8987] under E2; supplying three BM25-retrieved passages
   gives 0.8229 [0.7866, 0.8579] and 0.8100 [0.7763, 0.8415]. A containment rule
   over the *same* passages reaches 0.5938 [0.5598, 0.6261], and the paired
   difference is +0.2292 [+0.1939, +0.2635] under E1 (§4.6).

The predecessor of this work was rejected in part for an unsupported claim of
comprehensiveness. This paper makes no coverage claim: the corpus is six
documents, the retrieval configuration is one untuned BM25 at k = 3, the grounded
ladder is one model, and §6 states what each of those bounds.

# 2. Motivation

## 2.1 Fail-safe and fail-silent behaviour

Functional safety distinguishes a component that fails into a state the
surrounding system can handle from one that fails while continuing to present
normal output. An inspection assistant that declines a case is the first kind:
the case reaches a human, and the cost is throughput. One that produces a
confident wrong verdict on a provision it has never seen is the second: the error
enters the record with the same appearance as a correct one. The two failure
modes have different consequences and a qualification argument has to address
them separately. Accuracy on a forced-choice benchmark collapses them into one
number.

Treating the option to decline as part of what a classifier is for is old: the
error–reject trade-off was formalised by Chow (1970) and developed as **selective
prediction**, in which a system is evaluated jointly on the fraction of inputs it
answers and its accuracy on them (El-Yaniv and Wiener, 2010; Geifman and
El-Yaniv, 2017). That framing is what this paper's two conditions implement. A
neighbouring literature asks whether a model's stated confidence can be trusted
as the basis for declining — modern networks are typically miscalibrated (Guo et
al., 2017), calibration error is estimated over confidence buckets (Naeini et
al., 2015), and language models specifically have been examined for whether their
confidence tracks their accuracy in question answering (Jiang et al., 2021), for
whether they can be said to know what they know (Kadavath et al., 2022), and for
whether confidence expressed in words carries usable information (Lin et al.,
2022; Xiong et al., 2024). We report calibration error alongside the abstention
measures for this reason, but the paper's criterion is behavioural rather than
introspective: what is measured is whether the system declines the items it would
have got wrong, not whether it says it is uncertain.

## 2.2 An acceptance criterion has to be about abstention

Suppose an organisation sets a threshold — say, the tool must be right on 90% of
claims. Two systems meet it in different ways: one answers everything at 90%, the
other answers half the claims at 99% and declines the rest. In a workflow where
declined cases are cheap to route and wrong verdicts are expensive to discover,
the second is preferable, and the threshold cannot express that. The criterion
has to be stated jointly over the answering rate and the accuracy on answered
items, and it has to say what the system should do when it does not know. This
paper does not supply the threshold — that depends on the cost of a missed defect
in a given workflow, which is not a quantity a benchmark can measure — but it
supplies the measurement the threshold would be stated over.

## 2.3 Benchmarks expire, so systems have to be re-qualified

A qualification is a statement about a component at a time. It is widely assumed
among practitioners that hosted models change behind a stable name without an
announcement a downstream user can audit; we cite no source for that assumption
because we found no verifiable publication establishing it, and §4.4 reports an
observation consistent with it rather than a confirmation of it. If the only measure in the qualification file is
forced-choice accuracy, a change that leaves accuracy intact while degrading the
system's ability to recognise its own limits will not appear. §4.4 reports such a
case, on a frozen claim set, with prompts verified identical.

# 3. Materials and Methods

## 3.1 Terms

**Coverage** is the share of claims on which a system commits to true or false.
**Balanced accuracy (BAcc)** is the mean of sensitivity and specificity on
committed items. **λ** is a bias-corrected index, defined exactly as the scoring
code computes it: accuracy on the direct-citation family P1 plus accuracy on the
cross-reference family P5, minus one. P1 holds 163 claims of which 156 are true
and P5 holds 121, all false, so λ's neutral point is not zero: a system answering
"true" throughout scores −0.0429 and one answering "false" throughout scores
+0.0429. Those two values, not 0, are the reference points (§4.6.2 shows a
measured system sitting on one of them exactly). **Intervals** are cluster
bootstraps; the resampled unit is the (law, article) pair, of which the 473 claims
form 183, because several claims come from one article and resampling claims
individually would narrow every interval artificially. A **probe family** is a
claim-generation template targeting one failure mode. Where a family is
single-class, balanced accuracy is undefined and we report the **gold-class
selection rate** instead. Full glossary: S1.

## 3.2 Corpus

Six documents, frozen as PDFs and identified by SHA-256 of their extracted text:
Law No. 3194 (49 articles), Law No. 4708 (15) and its implementing regulation
(36 units), Law No. 6331 (39) and the risk-assessment regulation (19 units), and
TBDY 2018 (1,208 units in the raw parse). The raw corpus holds 1,366 units.

The raw segmentation was later found to merge adjacent TBDY clauses, so a refined
corpus was built and made primary by annex EK-6: TBDY 1,208 → 1,523 units and the
five remaining documents 158 → 232, the latter recovering 16 annex and 58
provisional articles the first parser had dropped. The refined corpus holds 1,755
units. Because this deviates from what the pre-registration named, EK-6 §3 makes a
sensitivity arm over the raw corpus mandatory; it was run and no result depends on
the choice (§4.6.5, S7).

## 3.3 Claim set

473 claims, 223 true and 250 false, in six probe families: direct assertion
(P1, 163), numeric value (P2, 37), cross-reference (P5, 121), currency of
amendment (P6, 120), anachronism (P3, 19), fabricated provision (P4, 13). The
codes are used throughout; their numbering follows the order in which the
families were written, not the order above. By citation form, 289 cite a
specific article and 184 cite only a document. Claims were generated by a sealed
script from the frozen text; that script was not modified after the runs began.

## 3.4 Conditions, runs and scoring gates

Every claim is asked twice. **E1** permits abstention (true / false / not sure);
**E2** forces a binary choice. Two system-prompt variants were written for each
condition; A is primary and B is a controlled re-wording. Annex EK-2, written
after both variants ran but before any cross-variant comparison was computed,
records that B's declared role changed at that point: the main pre-registration
had called it a consistency check, wording that presumes B would confirm A. It
does not — re-wording the system prompt alone moves abstention rates by tens of
points on the same claims and the same model — so EK-2 reframes B as a controlled
manipulation of measurement stability, and the instability is a finding rather
than a deviation (§4.4). For hosted models, extended thinking was disabled so the
task matched the local arm, and this was verified per response.

Each archived hosted configuration and each local grounded arm was run three
times and scored by majority vote. The one exception is the repeat run of §4.4,
which is a single run compared against single runs, because EK-7 fixed that
comparison at equal granularity.

**Two scoring gates.** A cell whose parsable-response rate falls below 0.80 is
not scored. Accuracy-type metrics are withheld for cells committing on fewer than
30 items; those cells are still shown, because coverage is itself a result.

**One deviation, and it is load-bearing.** The main pre-registration applied the
0.80 gate to whether a cell "answers" the claims, a phrase covering two distinct
quantities: whether a parsable label was emitted at all, and whether that label
was a commitment rather than an abstention. Addendum EK-1 re-defined the gate onto
the first. The reason is definitional and independent of the data: an 0.80 floor
on the commitment rate would classify this study's dependent variable as protocol
non-compliance, so that a system emitting perfectly parsable output while
declining 467 of 473 claims would be recorded as violating a protocol it is in
fact following exactly. It is nonetheless a deviation, and the sensitivity arm the
addendum requires is not a formality: applying the original gate to the commitment
rate leaves **7 cells scored and removes 13**, and the 13 include three of the
four systems this paper's findings rest on — `claude-sonnet-5` (0.615),
`claude-haiku-4.5` (0.710) and `qwen2.5:32b-instruct` (0.173). The fourth,
`gemma3:27b` (0.970), survives. A reader who rejects the redefinition should read
this paper as reporting seven cells. We think the redefinition is right and its
argument does not depend on which systems it retains — but the fact that it
retains precisely the systems we discuss is a reason to weigh the argument rather
than the outcome. Full listing: S2.

## 3.5 Grounded arms

Four arms differ in the evidence supplied and in nothing else. **R0** is closed
book. **R1** supplies the full text of the cited article, defined only on the 289
article-attributing claims; it is a ceiling, not a deployable configuration.
**R2** supplies the top three passages returned by an untuned BM25 retriever
(Robertson and Zaragoza, 2009) over the 1,755 refined units. **R3-BM25** supplies those same three passages to a
literal string-containment rule with no model, isolating what the model
contributes to identical evidence. A separate deterministic control that performs
no retrieval, **R3-rule**, resolves claims against the whole corpus; it checks the
scoring path and is a different object from R3-BM25 throughout.

The ladder was run with `qwen2.5:32b-instruct` on the refined corpus against the
v7a gold labels, three runs plus majority vote, 128-token budget, seed 42, with 0
of 1,524 responses truncated per run, satisfying the 1% ceiling EK-4 §10 sets as
an invalidation condition. The whole ladder was re-run over the raw 1,366-unit
corpus as the sensitivity arm EK-6 §3 requires (§4.6.5).

## 3.6 Gold-label quality assurance

Two specialists in civil engineering and occupational safety audited the labels in
two blinded passes, with gold, probe family, template and stratum hidden and row
order randomised per rater. The first pass asks whether a claim, read against the
quoted sentence, is correctly labelled. The second asks a harder question: whether
the claim still says what its source article says once the whole article is read.

The two passes do not give the same answer, and §4.7 reports both. The first-pass
κ is a property of the instrument as much as of the labels: the workbook shows the
rater the same evidence the label was derived from, so it re-derives the
generator's reasoning rather than testing it against the legislation. Design,
sampling frames and stratum weights: S8.

## 3.7 Outcome measures

Two measures of what abstention buys are reported together, and they have
different evidential status.

**The main pre-registration names four confirmatory quantities, not one, and all
four are reported.** Item 1.1 is the coverage difference, 1.2 the difference in
accuracy on committed items, 1.3 balanced accuracy and Youden's J, and 1.4 λ. For
the hosted arm the four are: coverage difference −0.3848 (`claude-sonnet-5`) and
−0.2875 (`claude-haiku-4.5`); BAcc difference +0.0678 and −0.0260; λ difference
+0.0318 and −0.0866. Item 1.1 is negative by construction — E1 permits declining
and E2 does not — so it is a descriptive quantity rather than a test, and we do
not correct or test it. Item 1.3 pairs balanced accuracy with Youden's J, and
since J = 2·BAcc − 1 on this design the two are a monotone transformation of each
other; testing both would be testing one quantity twice, so we report the
balanced-accuracy form. Item 1.4 agrees in sign with 1.2 for both systems.

The measure carried through the rest of this paper is therefore **1.2**, the
difference in accuracy on committed items, and the reason is that it is the only
one of the four that is both a test and not redundant with another. Its
prescribed correction is Bonferroni over the number of models. Twenty models were run — eighteen open-weight configurations and two
hosted ones — so the per-comparison level is 0.05/20 = 0.0025 and the interval is
a 99.75% interval.

The **exploratory** measure is Δ = A_com − A_nc, where A_com is E2 accuracy on the
items a system committed to under E1 and A_nc is E2 accuracy on the items it did
not. Annex EK-1 §3 introduced it after the main pre-registration under the heading
"added analysis (exploratory, not in the pre-registration)" and applies no
multiplicity correction. Two departures from that addendum are declared: it
describes the second arm as the abstained items, whereas we compute the complement
of the committed set, which additionally holds unparsable and no-majority records;
and it specifies no interval whereas we report one, descriptively.

Three interval levels govern the analyses here — 95%, 97.5% (EK-4 §4's family of
two, covering H1 and H2) and 99.75% (the family above) — and each is named where
it is used. S4 additionally reports family-size sensitivity levels.

Two denominators therefore appear and the difference is deliberate: §4.2 corrects
the open-weight comparison against chance over the eighteen open-weight
configurations eligible for it, and §4.3.1 corrects the condition contrast over
the twenty models run, since both hosted models are in its scope. Each family is
larger than the number of comparisons actually made in it, so both are
conservative, and S4 shows the verdict is invariant across the whole range.

## 3.8 Comparison baselines, and the limit of the provenance chain

The replication run held everything constant except date: same model name, same
variant A prompt, same 32-token budget as the archived runs, thinking disabled,
temperature not sent. Annex EK-7 fixed the decision rule before the run (§4.4).

We do not claim nothing on our side changed. The archived runs used `f4_api.py`
and the replication used `f4_api_v2.py`; the variant A prompts are byte-identical
across that change, but the identity was re-derived from archived source code
because the archived run records carry no script or prompt hash at all. Six
archived hosted runs and two repeat probes are retained but reported nowhere as
results: annex EK-3, written before the replacement runs, records that they were
executed with extended thinking enabled, and on many claims the whole budget went
to thinking, leaving no text block. Items lost that way are not lost at random —
they are the ones the model spent longest on — so every metric from those runs is
biased upward by an unknown amount. All hosted figures here come from runs with
thinking disabled and verified per response.

## 3.9 What would count as acceptable

We state no threshold. What a qualification would need is a joint statement over
coverage and accuracy on committed items, a demonstration that abstention carries
information rather than being noise, and a re-check interval justified against the
observed rate of change. §5.6 returns to this.

# 4 Results

All figures are scored against the v7a gold labels. Intervals are cluster
bootstraps over (law, article) pairs, seed 42.

## 4.1 The evaluated systems

Twenty models were run: eighteen open-weight configurations served locally
(qwen2.5, llama3.2 and gemma3 families at 1B–32B, in fp16 and three quantisations: q4_K_M, q5_K_M and q8_0)
and two hosted (`claude-sonnet-5`, `claude-haiku-4.5`). Quantisation variants of
one model are counted separately because they are separate deployments and, as
§4.2 shows, they do not behave identically. Full listing with per-cell response
rates: S3.

The hosted arm is summarised in Table 1; the open-weight arm follows in §4.2 and
Table 2.

**Table 1. Hosted arm, majority of three runs, closed book.**

| system | condition | BAcc | 95% CI | coverage | λ | ECE |
|---|---|---|---|---|---|---|
| claude-sonnet-5 | E1 | 0.6920 | [0.633, 0.750] | 0.615 | 0.325 | 0.0373 |
| claude-sonnet-5 | E2 | 0.6242 | — | 1.000 | 0.294 | 0.0634 |
| claude-haiku-4.5 | E1 | 0.5298 | [0.489, 0.570] | 0.710 | −0.026 | 0.2263 |
| claude-haiku-4.5 | E2 | 0.5558 | — | 0.998 | 0.061 | 0.2070 |

**ECE** is expected calibration error, the average gap between the confidence a
system states and the accuracy it achieves at that confidence, computed over
buckets of stated confidence and weighted by bucket size; a well-calibrated system
approaches 0. The estimator was positive-controlled against the deterministic
baseline, which states 100 on every claim it answers and answers almost all of
them correctly: it returns 0.0000, where an earlier mid-point formula returned
0.0500 on the same records.

**Table 1 is uncorrected, and its E2 rows carry no interval.** Corrected
intervals were computed for the open-weight comparison of §4.2 and for the
condition contrast of §4.3.1; they were not computed for the hosted cells in this
form, and the E2 cells have no interval in the frozen number set at all. The
haiku E1 interval contains 0.5, so on this claim set that system is not shown to
be above chance under E1. No statement is made here about haiku under E2, because
the figure to support one was not produced.

## 4.2 The coverage–accuracy trade-off

Eighteen open-weight configurations produced an E1 cell under variant A. Two fail
the response-rate gate — `llama3.2:3b-instruct-q4_K_M` at 0.674 and
`llama3.2:1b` at 0.545, both writing the claim text back instead of emitting a
label, which is a format failure rather than a knowledge one. Four
`qwen2.5:7b-instruct` quantisations commit on 6, 24, 18 and 16 items, below the
30-item floor, so their accuracy figures are withheld and support no statement
anywhere in this paper; their rows remain in S3 because coverage is itself a
result. Twelve cells carry a scored accuracy figure.

Read one cell at a time with uncorrected 95% intervals, four exclude 0.5. The
pre-registration requires Bonferroni over the number of models; taken over all
eighteen open-weight configurations rather than the twelve that survive the gates
— the conservative direction — the per-cell level is 0.00278, a 99.72% interval,
and, under the reported seed, two cells clear it — but only one of those two
verdicts survives a change of seed, as the paragraph after the table shows:

**Table 2. The four uncorrected candidates, before and after correction.**

| model | BAcc | 95% lower | corrected lower | coverage | excludes 0.5 after correction |
|---|---|---|---|---|---|
| qwen2.5:32b-instruct | 0.6769 | 0.5820 | 0.5349 | 0.173 | **yes** |
| gemma3:27b | 0.5674 | 0.5235 | 0.5017 | 0.970 | **yes, by 0.0017** |
| llama3.2:3b-instruct-q8_0 | 0.5509 | 0.5077 | 0.4878 | 0.884 | no |
| gemma3:12b | 0.5493 | 0.5136 | 0.4915 | 0.987 | no |

*On two figures for one cell.* The uncorrected lower bound for
`qwen2.5:32b-instruct` is 0.5820 here and 0.5833 in Table 4, because the
correction table is computed with 4,000 resamples and the main per-cell table
with 10,000. The difference is in the third decimal and is resampling noise, not
two measurements; nothing in this paper turns on it.

**Only one of those two verdicts is stable.** The 0.0017 by which `gemma3:27b`
clears chance is inside the noise of the bootstrap itself: repeating the
correction with five different resampling seeds gives corrected lower bounds of
0.5017, 0.4987, 0.4979, 0.5016 and 0.4981, so the cell excludes chance under two
seeds of five and does not under three. `qwen2.5:32b-instruct` excludes chance
under all five (0.5349, 0.5438, 0.5448, 0.5315, 0.5290). We therefore report
**one** open-weight configuration as exceeding chance after the pre-registered
correction, and `gemma3:27b` as sitting on the threshold with a verdict that
depends on the seed. Reporting it as a survivor, as an earlier version of this
paper did, would be reporting an artefact of one arbitrary choice.

The two cells sit at opposite operating points and that contrast is the result of
this section, independently of which side of the threshold the second one falls.
`qwen2.5:32b-instruct` reaches an interval overlapping the hosted
`claude-sonnet-5` (0.6920 [0.633, 0.750] at coverage 0.615) while committing on
82 of 473 claims — roughly one in six — so its accuracy and its coverage have to
be read as one figure. `gemma3:27b` answers 459 of 473 and sits about seven
points above chance on nearly the whole set. One is accurate on a small
self-selected fraction; the other is barely better than chance on almost
everything. Neither is a usable closed-book compliance checker, and they are
unusable for different reasons. Which operating point is preferable depends on
the workflow, and §2.2 argues the choice cannot be made by accuracy alone.

## 4.3 What abstention buys

### 4.3.1 The confirmatory contrast

The contrast is given in Table 3.

**Table 3. BAcc(E1) − BAcc(E2), hosted arm.** Paired cluster bootstrap, 4,000
resamples, seed 42. Correction: Bonferroni over 20 models (§3.7).

| system | difference | 95% CI | Bonferroni-20 (99.75%) CI | excludes 0 after correction |
|---|---|---|---|---|
| claude-sonnet-5 | +0.0678 | [+0.0243, +0.1106] | [+0.0018, +0.1359] | **yes, narrowly** |
| claude-haiku-4.5 | −0.0260 | [−0.0612, +0.0130] | [−0.0765, +0.0377] | no |

For `claude-sonnet-5` permitting abstention raises balanced accuracy and the
effect survives the pre-registered correction, by a corrected lower bound of
+0.0018 — established rather than large. For `claude-haiku-4.5` the point
estimate is negative and the corrected interval spans zero, so no measurable
benefit is established; the sign of the point estimate should not be read as a
finding. The verdict is identical at every family size from two to twenty-one
(S4), so the choice of denominator carries neither conclusion.

### 4.3.2 The exploratory selectivity measure

Δ is exploratory (§3.7). For the hosted arm it is 0.1557 [+0.0724, +0.2374] for
`claude-sonnet-5` and 0.0416 [−0.0448, +0.1380] for `claude-haiku-4.5`:
informative in the first case, and in the second the interval spans zero, so not
shown to be informative at all. That is the same ordering the confirmatory
contrast gives. Full table with all runs and denominator notes: S5.

### 4.3.3 A breakdown the pre-registration required, and what it exposes

Items 2 and 6 of the main pre-registration require probe families and their
subtypes to be broken out descriptively with intervals, and item 2 fixes the
minimum detectable differences in advance — 27.6 points for the P5 contrast, 33.4
for the P6 cells — so it anticipated that these comparisons would be underpowered.
Intervals here are Wilson intervals on the claim-level proportion; these cells are
small and draw on many articles, so a cluster bootstrap would be resampling a
handful of clusters. One of the breakdowns is not a null.

**P6, currency of amendment, `claude-sonnet-5` under E2.** Every cell is
single-class, so these are gold-class selection rates.

| cell | n | what the claim asserts | gold | model's answers | rate | 95% CI |
|---|---|---|---|---|---|---|
| P6_degismedi | 30 | "never amended" | false | false ×30 | 1.000 | [0.886, 1.000] |
| P6_degismedi_dogru | 30 | "never amended" | true | false ×29, true ×1 | 0.033 | [0.006, 0.167] |
| P6_yil | 30 | "amended in year N" | true | false ×30 | 0.000 | [0.000, 0.114] |
| P6_yil_yanlis | 30 | "amended in year N" | false | false ×30 | 1.000 | [0.886, 1.000] |

The model answers **false to 119 of 120 P6 claims**. Its aggregate P6 accuracy of
0.508 is not chance-level performance; it is the arithmetic of a design balanced
60 true against 60 false meeting a constant response. Read without the breakdown
it would be described as coin-flipping on questions of amendment currency, and
the description would be wrong in a way that matters.

The constant answer is a constant answer *to the claim*, not a constant belief
about amendment, and the two halves of the design make that explicit: where the
claim asserts a provision was never amended, "false" asserts that it was; where
the claim asserts an amendment in a named year, "false" denies it. The single
description fitting all four cells is that the system rejects whatever currency
proposition it is shown — which fails differently from guessing, and predictably.
`claude-haiku-4.5` is constant on the two *degismedi* cells and close to random on
the two *yil* cells, so the pattern is model-specific rather than a property of
the probe. The P5 subtype breakdown, which is a null, is in S6.

This is the same phenomenon R3-BM25 shows in §4.6, and it is why λ is reported
alongside accuracy: an aggregate near 0.5 can come from a system that is guessing
or from one answering constantly into a balanced design, and only a bias-corrected
index or a subtype breakdown separates them.

## 4.4 Change over time

The same configuration (`claude-sonnet-5`, variant A, 32-token budget) was re-run
on the frozen claim set about four weeks after the archived runs, under a rule
fixed beforehand in annex EK-7. **The interval is approximate and inferred, not
recorded.** The archived run records carry no timestamp; four weeks is the gap
between the dates written on the surrounding pre-registration documents, 2 August
and 28 August 2026. An earlier draft of this work said "months", which the record
does not support, and nothing in this section rests on the precise length of the
gap. That rule set three outcomes against the archived
A@32 range [0.6796, 0.6986]: a value inside it would be read as a **budget
effect**; a value at or below **0.66** as **version drift**; a value between as
**indeterminate**, reported and not forced. The 0.66 threshold is approximately
the midpoint between the archived lower bound and an earlier 128-token result of
0.6395; EK-7 states in terms that it is stipulated rather than externally
justified, and it was not altered after the run.

| | E1 | E2 |
|---|---|---|
| archive A@32, three runs | [0.6796, 0.6986] | [0.6012, 0.6220] |
| A@32 today | 0.6422 (outside) | 0.6090 (inside) |
| BAcc(E1) − BAcc(E2), archive | 0.0735 · 0.0784 · 0.0767, mean 0.0762 | |
| BAcc(E1) − BAcc(E2), today | 0.0332 | |
| abstentions, archive | 181 · 184 · 182 | |
| abstentions, today | 178 | |

The observed 0.6422 is at or below 0.66, so branch (b) applies: **version drift**.
Under forced choice the run sits inside the archived range; the divergence appears
only where abstention is permitted.

The confirmatory contrast falls from a mean of 0.0762 to 0.0332, a 56% relative
drop, outside the archive range of point estimates [0.0735, 0.0784] — but see the
interval on that change below, which contains zero. The number of abstentions moved
little: against the archive mean of 182.33 the drop to 178 is 2.4%. Frequency was
roughly preserved while the difference the abstentions made declined — the change
is in which items were declined, not how many.

The exploratory Δ falls from an archive mean of 0.1416 to 0.1014, a 28% drop
against the range of archived point estimates — but that comparison does not
survive being given intervals. Today's Δ is 0.1014 [+0.0212, +0.1833] and the
archived runs give [+0.0344, +0.1974], [+0.0385, +0.2147] and [+0.0914, +0.2638];
today's interval overlaps all three. **On the Δ axis, today's run and the archived
runs are not distinguishable.** The drift finding rests on the confirmatory
contrast, whose archived spread is narrow. Δ points the same way and adds no
discrimination; what it does still establish is that abstention on today's run
remains informative in absolute terms, since its interval excludes zero.

**Why the run range is the comparison base, and one asymmetry.** The clustered
bootstrap interval for the archived E1 runs is [0.633, 0.750] and today's 0.6422
falls inside it; that interval treats the claims as a sample and asks whether a
result generalises to other claims. The run-to-run range holds the 473 items fixed
and asks whether the system changed on this set. The claim set is frozen, so the
run range is the appropriate base for the version question, and we report the
bootstrap interval as well: a reader interested in generalisation to other claims
should use it and would not find the change established.

**An interval on the change is available, and it does not exclude zero.** An
earlier version of this section held the two measures to different standards: Δ
was set aside because its intervals overlapped, while the condition contrast was
retained on a three-run range, on the stated ground that no interval on the
*change* could be computed. That ground was wrong, and the correction matters
enough to state plainly. All four runs are scored on the same 473 claims, so the
same clusters can be resampled once and all four contrasts recomputed inside each
resample. The difference between today's contrast and the archive mean is then
**−0.0434, 95 % interval [−0.0986, +0.0118]**, which contains zero.

The consequence is specific. The *direction* is consistent across every
comparison in this section. The *magnitude* — the 56 % relative drop — is a point
estimate whose interval spans no change at all, so Δ and the condition contrast
end up in the same position and neither separates the two dates by an interval
excluding zero. What does not depend on an interval is that the two conditions
moved differently: forced-choice balanced accuracy stayed inside the range the
archived runs occupied and abstention-permitted balanced accuracy did not. That
is an observation on a frozen test set from a single repeat run, and §6 records
it as such.

**Prompt wording moves outputs more than run-to-run noise does.** Within the A@32
arm, run-to-run agreement is [0.9017, 0.9133]; within B@128 it is [0.9165,
0.9228]; agreement between A@128 and B@128 is 0.8302, below both bands. This is
why the byte-identity of the prompts across the harness change matters, and it is
the instability EK-2 reframed variant B to measure.

## 4.5 The rule-based baseline

**R3-rule** is deterministic, uses no language model, performs no retrieval, and
resolves each claim against the corpus by literal matching. Two properties of it
are conditions of reporting it at all, fixed in annex EK-4 §6, and are asserted at
start-up by the script itself: it never reads the gold label, and it resolves a
claim using the claim text and identifier only. Without both, a baseline scoring
473/473 would be measuring its own access to the answer key rather than the
scoring path. A note required by
annex EK-4 §8 comes first: its verdict on the anachronism family P3 is derived not
from corpus text but from the enactment-year field of the generator's own metadata
table. That is the same circularity the paper flags for P6 and it is worse,
because the corpus offers no independent channel. P3 is therefore reported
separately and labelled metadata-derived: R3-rule scores 1.000 on the 19 P3 claims
under both conditions, and that figure certifies the scoring path, not a
capability.

Against the raw corpus R3-rule scored 473/473 with the pre-revision gold (v6) and
466/473 with the audited gold (v7a); against the refined corpus it scores 473/473
with v7a. The earlier perfect score was therefore partly an artefact: **7 of 473**
came from the corpus and the gold being wrong in the same direction, and those
seven are exactly the seven labels the expert reconciliation later corrected. A
negative control with shuffled claim–unit pairings over five seeds averages
0.5315, inside a 0.50–0.56 acceptance band. That band was fixed in the task
specification before the control was run, not in a pre-registration annex, and we
label it that way rather than as pre-registered.

## 4.6 Grounded arms: supplying the text

### 4.6.1 The retriever on its own

BM25 at k = 3 over the 1,755 refined units places the cited unit in the supplied
context for 79 of the 289 article-attributing claims, a recall of 0.2734.

### 4.6.2 End-to-end results

Table 4 gives the four arms on the same claim set.

**Table 4. Grounded arms, `qwen2.5:32b-instruct`, refined corpus + v7a gold,
majority of three runs.** Cluster bootstrap, 4,000 resamples, seed 42.

| arm | evidence supplied | cond. | n | coverage | BAcc | 95% CI | λ |
|---|---|---|---|---|---|---|---|
| R0 | none (closed book) | E1 | 473 | 0.173 | 0.6769 | [0.5833, 0.7618] | — |
| R0 | none (closed book) | E2 | 473 | 1.000 | 0.5493 | — | — |
| R1 | cited article, full text | E1 | 289 | 0.830 | 0.9164 | [0.8804, 0.9494] | 0.987 |
| R1 | cited article, full text | E2 | 289 | 1.000 | 0.8615 | [0.8207, 0.8987] | 0.988 |
| R2 | BM25 top-3 | E1 | 473 | 0.899 | 0.8229 | [0.7866, 0.8579] | 0.804 |
| R2 | BM25 top-3 | E2 | 473 | 1.000 | 0.8100 | [0.7763, 0.8415] | 0.829 |
| R3-BM25 | BM25 top-3, no model | — | 473 | 1.000 | 0.5938 | [0.5598, 0.6261] | −0.043 |

**The model adds about 22 points to the same retrieved passages.** R2 minus
R3-BM25 is +0.2292 under E1 with a paired 95% interval of [+0.1939, +0.2635] and
+0.2162 under E2 with [+0.1818, +0.2493]. The intervals are paired — the same
clusters are resampled for both arms, which decide the same claims from the same
retrieved passages — and both exclude zero. EK-4 §4 lists this contrast as
secondary and exploratory; the pre-registered primary family is §4.6.3.

**The lexical baseline extracts nothing from the passages.** R3-BM25's λ of −0.043
is not merely near the neutral point: it is exactly the value of a system
answering "true" to every P1 and every P5 claim, and that is what the rule does.
Its decisions are constant within every probe family — true on all 163
direct-citation and all 121 cross-reference claims, false on all 37 numeric, 19
anachronism, 13 fabricated and 120 currency claims — so the set it calls true is
exactly P1 ∪ P5, 284 of 473. Its balanced accuracy of 0.5938 is produced by probe
base rates. This is what the design anticipated: P5 claims quote real regulatory
text and attribute it to the wrong provision, so a containment rule finds the
string and cannot see the mis-attribution.

**A perfect citation is worth about 5 to 9 points over BM25, but the arms are not
scored on the same items.** R1 exceeds R2 by 0.0935 under E1 and 0.0515 under E2.
R1 is defined on 289 claims and R2 on 473, so this contrast is not paired: it
confounds evidence quality with item composition and is indicative only. Under E2
the intervals overlap; under E1 they are disjoint, R1's lower bound of 0.8804
lying above R2's upper bound of 0.8579.

### 4.6.3 The pre-registered primary hypotheses

Annex EK-4 §4 names two comparisons as the primary confirmatory family for the
grounded arms, with Bonferroni over two (97.5% intervals). **H1 is R2 − R0** and
**H2 is R1 − R0**, both fixed before the grounded runs. H2 is computed on the 289
article-attributing claims against an R0 baseline restricted to those same claims,
which is not the same number as R0 on the full set: R0 scores 0.6226 under E1 and
0.5062 under E2 on the subset, against 0.6769 and 0.5493 on all 473.

Table 5 reports both hypotheses in both conditions.

**Table 5. Pre-registered primary family (EK-4 §4), `qwen2.5:32b-instruct`.**

| hypothesis | cond. | contrast | n | difference | 95% CI | Bonferroni-2 CI | excludes 0 |
|---|---|---|---|---|---|---|---|
| H1 | E1 | R2 − R0 | 473 | **+0.1460** | [+0.0503, +0.2455] | [+0.0367, +0.2575] | **yes** |
| H1 | E2 | R2 − R0 | 473 | **+0.2607** | [+0.2218, +0.2964] | [+0.2170, +0.3014] | **yes** |
| H2 | E1 | R1 − R0 | 289 | **+0.2938** | [+0.1361, +0.4479] | [+0.1118, +0.4717] | yes, *see note* |
| H2 | E2 | R1 − R0 | 289 | **+0.3552** | [+0.3112, +0.3984] | [+0.3051, +0.4036] | **yes** |

*Note on H2 / E1.* Restricting the closed-book arm to 289 claims also restricts
its commitments: R0 commits on only **29** of them under E1, below the 30-item
floor this paper applies elsewhere. The row is shown rather than deleted —
deleting it would hide a pre-registered hypothesis, and the floor is a reporting
convention rather than a test — but **no conclusion here rests on H2 under E1**.
H2 / E2 is computed on all 289 committed items and both forms of H1 use the
full-set R0 cell with 82 commitments.

All four corrected intervals exclude zero. The E1 intervals are much wider than
the E2 intervals because R0 under E1 commits on few items; the E2 comparison,
where both arms answer everything, is the better-conditioned one. There is a
further reason to prefer it. Under E1 the two arms of each contrast are scored on
*different subsets of claims* — each arm's own committed set — because balanced
accuracy is defined on committed items only. The E1 differences therefore
confound the effect of supplying evidence with a change in which items are being
scored, and the same caution applies to the E1 column of Table 3 and to the E1
row of every grounded comparison. Under E2 both arms answer every claim and the
confound does not arise. We report the E1 figures because coverage is itself a
result, and we rest the conclusions on the E2 forms.

### 4.6.4 What the retrieval figure does and does not bound

R2 reached 0.8229 while the retriever placed the cited unit in context for only
0.2734 of the article-attributing claims. Retrieval recall is therefore **not** a
ceiling on grounded accuracy, and an earlier statement in this work that a
grounded arm inherits the retriever's ceiling is withdrawn: it was a prediction and
the measurement contradicts it. At least two mechanisms could produce this — the
retrieved passages are often sufficient even when they are not the cited unit, or
the model completes from parametric knowledge — and this experiment does not
separate them. Attributing R2's accuracy to retrieval alone would be unsupported.

Three runs were executed per arm as a precaution and were not needed for this
model: within-arm agreement is 1.0000 for both R1 and R2 across 1,524 calls per
run. An earlier observation of non-determinism under grounded prompting belongs to
`llama3.2:3b`, which is also the model that dropped the output-format
instruction; both are properties of that one model.

### 4.6.5 Two mandatory sensitivity checks, neither of which moves the result

Annex EK-6 makes a sensitivity arm over the raw 1,366-unit corpus **mandatory**
because the refined corpus was a deviation from what the pre-registration named.
The whole ladder was re-run over it with the same model, gold, budget and seed,
with 0 of 1,524 responses truncated. The primary arm is a majority of three runs
and the sensitivity arm a single run, which is comparable only because the three
primary runs agree exactly, at 1,524 of 1,524 records.

**No arm shows a corpus effect that excludes zero.** Paired differences
BAcc(refined) − BAcc(raw) are +0.0188 [−0.0040, +0.0475] (R1/E1), +0.0128
[+0.0000, +0.0343] (R1/E2), +0.0070 [−0.0203, +0.0354] (R2/E1), +0.0073 [−0.0151,
+0.0296] (R2/E2) and exactly 0.0000 for R3-BM25. Decision agreement between the
corpora is high but not total — 421 of 473 for R2 under E1 — so the corpora do
produce different individual decisions and the null is a statement about the
aggregate. The R1/E2 lower bound is exactly zero and not by rounding: of 4,000
resamples none produced a negative difference and 534 produced exactly zero,
because the two corpora disagree on only 4 of 289 claims in that cell. Full table
and the R3-BM25 identity result: S7.

The raw corpus **retrieves better and scores slightly worse**: BM25 recall is 87
of 289 (0.3010) against 79 of 289 (0.2734), yet all four grounded cells score
lower. This is a second, independent instance of the dissociation in §4.6.4,
obtained by varying the corpus rather than by comparing recall against accuracy
within one configuration.

The second check concerns **seventeen claims flagged `needs_human_review`** under
EK-6 §4, whose quoted text was located in a unit other than the one the claim
record names. No gold label changed, but the route matters: an adjudication pass
over the seventeen was produced by a language model rather than by the two human
coders whose agreement §4.7 measures. It proposed three label changes and we did
not adopt them — they read the claim record's `madde` field as the provision the
claim cites, whereas EK-4 §2 defines it as the provision the text was drawn
*from*, and all three cite at document level, which EK-4 §9(d) resolves against the
whole document. R3-rule detected the same thing independently, dropping from
473/473 to 470/473 on exactly those three claims. The seventeen therefore remain
`needs_human_review`: a study measuring whether language models can judge Turkish
regulation cannot let a language model set the labels it is scored against without
saying so. Removing them moves the headline contrast by less than its interval
width (S7).

## 4.7 The expert audit of the gold labels

**First pass.** On the decision axis agreement was complete (Cohen's κ = 1.000,
95% CI [1.000, 1.000], n = 150) and on the quality axis high (κ = 0.860 [0.759,
0.961]). Contextual defect counts were zero in each of the five families the pass
sampled (P1 0/22, P2 0/17, P3 0/15, P4 0/12, P5 0/16); with these sample sizes the
95% upper bounds run from 14.9% to 24.3%, so the pass bounds the rate loosely.
P6 carries no first-pass count and was checked against official HTML on
mevzuat.gov.tr instead, where 20 of 20 sampled claims agreed. That check is
framed to three of the six documents — Laws 3194, 4708 and 6331 — so the
implementing regulation is outside it and **43 P6 claims drawn from that
regulation were not independently verified by any route**.

**Second pass, and it is negative.** On the 58 non-control items agreement fell to
κ = 0.722, approximate 95% CI [0.513, 0.933]; the interval is wide and the normal
approximation rough at this n, and it is given because the first-pass κ is
reported with one and reporting only the favourable interval would be asymmetric.
The two intervals do not overlap. All six disagreements ran in the same direction
(sign test p = 0.0312), so the pattern is systematic: the two coders are applying
different rules, which is a definitional problem rather than measurement error and
cannot be closed by averaging. The seeded positive control was caught 1 of 2 by
the looser adjudication rule and 0 of 2 by the strict one, so the strict rule is a
lower bound and the first pass's zero counts must be read in that light. The
stratum-weighted contextual error rate under the looser rule is 5/33 = 15.2%
[6.7%, 30.9%] in the flagged stratum and 1/25 = 4.0% [0.7%, 19.5%] in the clean
one, giving a frame estimate of 6.7% [1.6%, 11.8%] and a composite projection of
8.8% over the whole set. Full design, weights and the reconciliation of the 158 /
150 / 138 sample counts: S8.

**Every result under both label sets.** Annex EK-5 §8 requires reporting under the
pre-revision gold (v6) alongside v7a. Across model cells the mean absolute
difference in balanced accuracy is 0.0039 and the largest is 0.0346, at
`qwen2.5:32b-instruct` under E1 (0.6769 against 0.6423). **One verdict does change
and is reported rather than smoothed:** under v6, `gemma3:12b` also excludes
chance after correction, with a corrected lower bound of 0.5013 against 0.4915
under v7a, so three cells survive correction under v6 where two survive under v7a.
The additional cell clears chance by 0.0013 — narrower still than the 0.0017 by
which `gemma3:27b` clears it under v7a — so what this exposes is the fragility of
threshold cells, not a difference in what the models can do. λ is the measure
EK-5 predicted would be most exposed, and it is: in three of four hosted cells λ
moves further between label sets than balanced accuracy does. S9 gives the comparison in full, and the complete 56-cell table under all
three gold versions is in the released archive.

**What the audit does and does not license.** It establishes that the labels are
internally consistent on the evidence the first pass shows a rater, and that a
contextual error rate of roughly 7% over the audited frame — with an interval
running to about 12% — cannot be excluded. It does not establish a label-quality
figure small relative to the accuracy differences this paper reports, and in
particular it is not small relative to `gemma3:27b` clearing chance by 0.0017.
Differences of that size should be read as within the label noise the audit
failed to exclude.

# 5 Discussion

## 5.1 A trade-off, not a uniform failure

The open-weight arm does not fail uniformly. Twelve of eighteen cells are scored;
four exceed chance with uncorrected intervals; after the pre-registered
correction one does so robustly and a second is seed-dependent. The two sit at
opposite operating points, and that contrast is the finding rather than the count. `qwen2.5:32b-instruct` answers one claim
in six and is accurate on those; `gemma3:27b` answers nearly all of them barely
above chance. Neither is usable as a closed-book compliance checker, but they are
unusable for different reasons, and only the second would be caught by an accuracy
threshold. The first would pass a 0.65-accuracy gate while declining five items in
six, which is why §2.2 argues the criterion has to be joint.

## 5.2 Abstention frequency held; abstention selectivity fell

The repeated hosted run is the paper's qualification result. Forced-choice
accuracy stayed inside its archived range. The abstention count barely moved:
181, 184 and 182 in the archive against 178 today, a relative decrease of 2.4%
against the archive mean of 182.33. What changed is what the abstentions were
worth. The confirmatory contrast fell from 0.0762 to 0.0332, a 56% relative drop
against the archive range of point estimates — a difference whose own interval,
−0.0434 [−0.0986, +0.0118], contains zero, so the magnitude is not established
and only the pattern is.

For a building-inspection workflow this pattern matters more than either number
alone. A tool whose abstention rate is stable but whose abstentions have become
less informative looks unchanged on a dashboard that monitors abstention rate: the
"send this one to a human" signal remains visually intact while carrying less of
the meaning it was accepted for. What would detect it is the condition contrast
recomputed against a retained gold subset — the measure whose archived spread is
narrow enough for the change to fall outside it. Δ is not the right instrument
even though it moves the same way, because its intervals on the repeated run
overlap the archived ones throughout (§4.4); a monitor built on Δ alone would have
registered a drop it could not distinguish from resampling.

Across the two hosted models the value of abstention is model-specific: +0.0678
[+0.0018, +0.1359] for one and −0.0260 [−0.0765, +0.0377] for the other. It is a
property of the system, not of the prompt or the task, and it has to be measured
per system rather than assumed.

## 5.3 Re-qualification: a fixed test set, a changed component

The claim set was frozen, the prompts were byte-identical, the budget was the
same, and thinking was disabled in both. Within the limits §3.8 and §6 state, the
component behaved differently underneath a fixed measurement. We do not know what
changed on the provider's side, and §6 says so; what an inspection organisation
would face is the same either way — a tool whose qualification evidence was
gathered on one date and whose behaviour on the same test set is no longer the
same. The practical consequence is that a qualification file for a hosted model
needs a date, a re-check interval, and a retained gold subset the re-check can be
run against. We do not claim to know how
often such changes occur; one observation does not establish a rate.

## 5.4 Supplying the governing provision changes the operating point

Four quantities set the scale for `qwen2.5:32b-instruct`. Closed book, 0.6769 at
coverage 0.173 under E1 and 0.5493 at full coverage under E2. Given three
retrieved passages, 0.8229 [0.7866, 0.8579] and 0.8100 [0.7763, 0.8415]. Given the
cited article, 0.9164 [0.8804, 0.9494] and 0.8615 [0.8207, 0.8987]. Given the same
retrieved passages with no model, 0.5938 [0.5598, 0.6261].

The pre-registered primary comparisons (§4.6.3) put the gain from supplying text
at +0.2607 [+0.2218, +0.2964] for retrieved passages and +0.3552 [+0.3112,
+0.3984] for the cited article, under forced choice, both surviving correction.
The engineering reading is direct: on this material the deficit measured closed
book is a deficit of the deployment architecture, not of the task. Effort spent
on supplying the governing provision buys more than effort spent choosing between
closed-book models.

The judgement step is separable from the evidence. R2 and R3-BM25 see identical
passages; the paired difference is +0.2292 [+0.1939, +0.2635]. And the lexical
baseline is not a weak reader but a non-reader: its decisions are constant within
every probe family and the set it calls true is exactly P1 ∪ P5 (§4.6.2). Whatever
is in those passages, a containment rule cannot use it.

Two cautions. R1 is a ceiling, not an operating point: a deployed system does not
know in advance which article a claim should be checked against. And the retrieval
component is the least examined part of the pipeline — one untuned retriever, one
k — which §6 records.

## 5.5 The rule baseline, and one circularity we cannot remove

R3-rule scores 473/473 on the refined corpus with the audited gold. That is not
evidence about regulation-checking; it is evidence that the scoring path is intact,
and it is partly circular, because the same generator metadata that produced some
claims also supplies the baseline's answer on P3 and P6. §4.5 labels those
families metadata-derived. The informative result from this baseline is historical:
its earlier perfect score against the raw corpus was 7/473 dependent on the corpus
and the gold being wrong together, and those seven are exactly the labels the
experts corrected.

## 5.6 What would count as acceptable

We decline to state a threshold, because the cost of a missed defect relative to
the cost of a routed case is a property of a workflow and not of a benchmark. Recent work on machine-learning
decision support in construction pairs predictions with confidence intervals and
with post-hoc explanations of what drove them (Chen et al., 2025); what this paper adds is that for a system that may decline, the
interval and the explanation are not enough on their own — the decision to
decline is itself a measured quantity. What a qualification argument would need,
and what this paper supplies the instruments for, is: a joint statement over coverage and accuracy on committed items rather
than an accuracy figure alone; evidence that abstention carries information for
the specific system, since it does for one hosted model here and not for the
other; a decision about grounding, since the operating point moves by more than
any closed-book model choice does; and a re-check interval with a retained gold
subset, since a change large enough to halve the value of abstention was invisible
to forced-choice accuracy.

# 6 Limitations

**One claim set, one jurisdiction, six documents.** No coverage claim is made. The
claims are generated from frozen text by templates, so they test recognition of
provisions rather than the open-ended reasoning an inspection involves.

**Gold-label quality is bounded loosely, not tightly.** The second pass could not
exclude a contextual error rate of roughly 7% over the audited frame, with an
interval to about 12% and a composite projection of 8.8%, and its own positive
control was missed under the strict rule. Differences of a few thousandths — such
as `gemma3:27b` clearing chance by 0.0017 — sit inside that uncertainty.

**The drift result is one run against three, and its magnitude is not
established.** A paired interval on the change *is* computable and is
−0.0434 [−0.0986, +0.0118] (§4.4); it contains zero, so the size of the drop in
the value of abstention is not separable from resampling noise. What the run
shows is a difference in *which* condition moved, on a frozen claim set, from a
single repeat whose own within-arm band was not measured. Any reading that treats
the 56 % figure as an established effect size is stronger than the data support,
and we have withdrawn that reading from this paper.

**"Version drift" is our label for a behavioural difference, not a claim about the
provider.** We did not observe, and were not told, any vendor release, weight
change or serving change, and no vendor version identifier was recorded or could
be read from the API. What we measured is that a fixed claim set produced
different behaviour on two dates under prompts we verified identical.

**Mechanism unmeasured.** Whether the shift in abstention selectivity reflects
decoding, serving, prompt handling on the provider's side, or something else, is
outside what these runs can determine. We report the difference and its
consequence for qualification practice, not its cause.

**The provenance chain has a boundary.** Archived run records carry no script or
prompt hash; prompt identity was re-derived from archived source code. The
development repository's version history was lost and the repository was
reconstructed from dated hand-over packages, so the claim that a pre-registration
preceded its run rests on document dates rather than commit timestamps.

**One deviation is load-bearing.** Under the original reading of the coverage
gate, three of the four systems discussed here would not be scored (§3.4). We
argue the redefinition is correct on definitional grounds, but a reader who
rejects it is left with seven cells.

**One untuned retriever.** BM25 at k = 3 is the only retrieval configuration
tested. Its recall of 0.2734 does not cap grounded accuracy (§4.6.4), and across
corpora it does not order it either: the raw corpus retrieves better and scores
slightly worse (§4.6.5). Neither observation says retrieval is unimportant; both
say this recall number is not the quantity that predicts accuracy here, and we did
not measure what is.

**The grounded ladder is one model.** R1 and R2 were run on
`qwen2.5:32b-instruct` only. Whether the +0.2607 gain generalises across model
families was not tested.

**Seventeen claims remain unresolved.** They are flagged `needs_human_review` and
were not adjudicated by the human coders (§4.6.5). Removing them does not move the
headline, but they are open.

# 7 Conclusions

We built a 473-claim benchmark over six frozen Turkish regulatory documents to
ask what a qualification argument for language-model decision support in
compliance checking would have to measure, and we conclude that forced-choice
accuracy is not sufficient for it.

Closed book, the systems tested sit at a coverage–accuracy trade-off. Twelve of
eighteen open-weight cells are scored and, after the pre-registered correction,
one excludes chance robustly. A second clears it by 0.0017 under the reported
seed and not under three of five others — a margin inside both the bootstrap's own
noise and the label noise the expert audit could not exclude, so we report it as
undecided. Neither operating point supports a compliance
decision on this material.

Abstention has to be measured per system rather than assumed. It is worth +0.0678
[+0.0018, +0.1359] in balanced accuracy for one hosted model and nothing
measurable for the other, and the aggregate scores that look like chance can
conceal a constant response: one hosted model answers "false" to 119 of 120
currency-of-amendment claims, and a lexical baseline that appears to score 0.5938
turns out to answer "true" to exactly the two probe families whose text is present
in the corpus.

The closed-book deficit is a deficit of the deployment architecture, not of the
task. Supplying three retrieved passages raises forced-choice balanced accuracy by
+0.2607 [+0.2218, +0.2964] and supplying the cited article by +0.3552 [+0.3112,
+0.3984]; a string-matching rule over the same retrieved passages gains nothing,
so roughly 22 points of the grounded result come from the model's judgement of the
evidence rather than from the evidence being present. The practical implication is
to put engineering effort into supplying the governing provision rather than into
selecting a closed-book model — with the cautions that this was measured on one
model and that the retrieval component is the least examined part of the pipeline.

Finally, a qualified component changed. Re-running one hosted configuration about four
weeks later on the frozen claim set left forced-choice accuracy inside its
archived range while abstention-permitted accuracy fell outside it, with the
number of abstentions barely moving. The size of the drop in what abstention was
worth is not established — its interval, −0.0434 [−0.0986, +0.0118], contains
zero — and we make no claim about it. What the run does show is that the two
conditions moved differently, and an acceptance criterion that looked only at
accuracy, or only at abstention rate, would have registered nothing at all. A
qualification file for this class of tool needs a date, a retained gold subset,
and a measure stated over abstention behaviour.

# Acknowledgements

The author thanks the two domain specialists — one in civil engineering, one in
occupational health and safety — who carried out the blinded gold-label audit
reported in §4.7. They worked without sight of the gold labels, the probe
families or the sampling strata, and the negative result of the second pass is
theirs as much as the positive result of the first. The audit is what allows this
paper to treat its labels as a measured object rather than an assumption.

# Declarations

**Funding.** This research received no specific grant from any funding agency in
the public, commercial, or not-for-profit sectors.

**Conflict of interest.** The author declares no conflict of interest.

**Data and code.** See below.

# Data and code availability

The frozen source documents with their SHA-256 checksums, the 473-claim set with
all three gold label versions, the pre-registration and its eight annexes, the
expert-audit workbooks including the negative second-pass result, the run records
and the analysis code are released as a single archive, together with the
supplementary material S1–S9.

Repository: **https://github.com/alicetinkaya76/ruhsat-bench**

Archive: **https://doi.org/10.5281/zenodo.22168590** — this identifier resolves to
the most recent archived version and is the one to cite for the benchmark itself.
The exact state from which every figure in this paper was produced is release
v1.0.2, **https://doi.org/10.5281/zenodo.22180708**; readers checking a specific
number should use that one. One consequence of depositing the manuscript inside
its own archive should be stated: the copy of this text held in any given release
was written before that release had an identifier, so the DOI printed above was
inserted in the working repository after v1.0.2 was minted and appears in full
only from the next deposit onward. The data, code and run records are identical
across that boundary.

The repository is where the work continues and the archive is what does not
change; a repository can be moved, rewritten or deleted, so the reproducibility
claim in §1 rests on the archive rather than on the repository.

*One limit on the provenance of the archive itself.* The version-control history
of the development repository was lost before submission and the repository was
reconstructed from dated hand-over packages, whose checksums are recorded in the
archive.

# References

*Every entry below was resolved against its Crossref record on 30.08.2026, and
the year given is the issue year from the `published-print` field rather than the
online-first date; two entries carried the wrong year in an earlier draft for
exactly that reason and are corrected here. Entries without a registered DOI say
so. No source that failed verification is cited. The verification record is
released with the archive.*

Abanda, Kamsu-Foguem and Tah, 2017. BIM — new rules of measurement ontology for construction cost estimation. *Engineering Science and Technology, an International Journal* 20(2), 443–459. doi:10.1016/j.jestch.2017.01.007

Chen, et al., 2024. Automated building information modeling compliance check through a large language model combined with deep learning. *Buildings* 14(7). doi:10.3390/buildings14071983

Chen, Xu, Lim, Sharma and Tiang, 2025. Transparent and reliable construction cost prediction using advanced machine learning and explainable AI. *Engineering Science and Technology, an International Journal* 70, 102159. doi:10.1016/j.jestch.2025.102159

Chow, 1970. On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory*. doi:10.1109/tit.1970.1054406

Dahl, et al., 2024. Large legal fictions: profiling legal hallucinations in large language models. *Journal of Legal Analysis*. doi:10.1093/jla/laae003

Eastman, et al., 2009. Automatic rule-based checking of building designs. *Automation in Construction*. doi:10.1016/j.autcon.2009.07.002

El-Yaniv and Wiener, 2010. On the foundations of noise-free selective classification. *Journal of Machine Learning Research* 11, 1605–1641. — *no registered DOI; the identifier 10.5555/1756006.1859904 that appears in some indexes is an ACM placeholder and does not resolve.*

Geifman and El-Yaniv, 2017. Selective classification for deep neural networks. arXiv:1705.08500

Guo, et al., 2017. On calibration of modern neural networks. *ICML*. arXiv:1706.04599

Jiang, et al., 2021. How can we know when language models know? On the calibration of language models for question answering. *TACL*. doi:10.1162/tacl_a_00407

Kadavath, et al., 2022. Language models (mostly) know what they know. arXiv:2207.05221

Lin, et al., 2022. Teaching models to express their uncertainty in words. arXiv:2205.14334

Makartetskiy, Marchetto, Sisto, Valenza and Virgilio, 2020. (User-friendly) formal requirements verification in the context of ISO26262. *Engineering Science and Technology, an International Journal* 23(3), 494–506. doi:10.1016/j.jestch.2019.09.005 — *online October 2019, June 2020 issue; cited by issue year.*

Magesh, et al., 2025. Hallucination-free? Assessing the reliability of leading AI legal research tools. *Journal of Empirical Legal Studies*. doi:10.1111/jels.12413

Naeini, et al., 2015. Obtaining well calibrated probabilities using Bayesian binning. *AAAI*. doi:10.1609/aaai.v29i1.9602

Robertson and Zaragoza, 2009. The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*. doi:10.1561/1500000019

Solihin and Eastman, 2015. Classification of rules for automated BIM rule checking development. *Automation in Construction*. doi:10.1016/j.autcon.2015.03.003

Turan, Çelik, Kumbasaroğlu and Yalçıner, 2024. Assessment of reinforced concrete building damages following the Kahramanmaraş earthquakes in Malatya, Turkey (February 6, 2023). *Engineering Science and Technology, an International Journal* 54, 101718. doi:10.1016/j.jestch.2024.101718

Xiong, et al., 2024. Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. *International Conference on Learning Representations (ICLR) 2024*. arXiv:2306.13063 — *the preprint is dated 2023 and the conference version 2024; this paper cites the conference version throughout.*

Zhang and El-Gohary, 2016. Semantic NLP-based information extraction from construction regulatory documents for automated compliance checking. *Journal of Computing in Civil Engineering* 30(2). doi:10.1061/(ASCE)CP.1943-5487.0000346 — *the article carries a 2013 online-first date and a March 2016 issue date; it is cited by its issue year.*

Zhou and El-Gohary, 2017. Ontology-based automated information extraction from building energy conservation codes. *Automation in Construction* 74, 103–117. doi:10.1016/j.autcon.2016.09.004 — *online December 2016, February 2017 issue; cited by issue year.*

## Standard

IEC 61508. *Functional safety of electrical/electronic/programmable electronic safety-related systems.* International Electrotechnical Commission, Geneva. — *A standard rather than a journal article; outside OpenAlex coverage, and its edition and part number should be completed from the IEC catalogue before submission.*

## Primary legal sources

The six documents constituting the corpus were frozen as PDF files and are distributed with the benchmark under SHA-256 checksums (§3.2): Law No. 3194 on Development (49 articles); Law No. 4708 on Building Inspection (15 articles) and its implementing regulation (36 units); Law No. 6331 on Occupational Health and Safety (39 articles) and the risk-assessment regulation issued under it (19 units); and the Turkish Building Earthquake Code, TBDY 2018 (1,208 units in the raw parse, 1,523 in the refined corpus).
