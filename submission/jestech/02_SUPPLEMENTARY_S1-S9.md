# RUHSAT-Bench — Supplementary material

Companion to *"Measuring abstention, not accuracy alone: a re-qualification benchmark
for language-model decision support on Turkish construction and
occupational-safety regulation."*

This document carries the material the main text refers to as S1–S9: the full
model-by-model listings, the pre-registration compliance record, the family-size
and corpus sensitivity analyses, the probe-subtype breakdowns and the complete
expert-audit report. Section numbers in the form §4.2 refer to the main text.

Every figure here is regenerated from committed script outputs; the number sheet
mapping each figure to its producing script is in the released archive. No figure
appears here that does not appear there.

---


## S1 — Terms and definitions in full

> The main text §3.1 carries an abridged version of this glossary.

The study sits between legal engineering practice and language-model evaluation, so the measurement vocabulary is fixed first. Two of these terms — response rate and commitment count — are kept apart deliberately, because the gates of §3.4 apply to one of them and not to the other.

| Term | Meaning as used here |
|---|---|
| Closed-book | The model is asked about a regulation without being shown its text, and must answer from what is stored in its parameters. |
| Abstention | An explicit "not sure" response, offered as a third option in one of the two conditions. |
| Response rate | The share of the 473 claims for which the model emitted a label of any usable kind — true, false, or "not sure". Its complement is unparsable output. This is a compliance measure, not a performance measure. |
| Coverage | The share of the claim set on which a model commits to a verdict, that is, answers true or false rather than abstaining or emitting an unparsable output. |
| Commitment count | The same quantity expressed as a count of claims rather than a fraction. It is read from the run record for each cell, not recomputed from the rounded coverage figure, and it governs which cells carry an accuracy figure (§3.4). |
| Balanced accuracy (BAcc) | The mean of accuracy on the true claims and accuracy on the false claims. 0.5 is the level reached by any strategy that ignores content — always answering "true", always "false", or answering at random. |
| Calibration / ECE | Whether a stated confidence matches observed correctness, in the sense in which a measuring instrument is calibrated: a gauge marked 95 must be right on about 95 of every 100 readings. Expected calibration error (ECE) is the average gap between the stated figure and the observed rate; 0 is a perfectly calibrated instrument, and a large ECE means an individual reading cannot be relied on even when the average happens to be correct. |
| Bootstrap | An uncertainty interval obtained by repeatedly resampling the data. We resample clusters, not single claims: a cluster is one (law, article) pair, so that claims drawn from the same article are kept together. Resample counts and interval levels are given in §3.7. |
| BM25 | A classical keyword-scoring retrieval function that ranks text units against a query (Robertson and Zaragoza, 2009). One untuned retriever, used at k = 3. |
| Token | The unit in which model input and output are counted; the output budgets named below (32, 128) are token budgets. |


## S2 — Scoring gates and the pre-registration compliance record

> The main text §3.4 states the deviation, the 7-scored/13-removed outcome and the three systems it removes; the full argument for the redefinition, the two gates in their original wording and the four named cells that fall under the minimum-n rule are here. The commitment rate of every cell, from which the original gate's outcome can be read off for all twenty, is in the table in S3.

Every claim is asked twice. **E1** allows abstention (true / false / not sure); **E2** forces a binary choice. Two system-prompt variants (A and B) were written for each condition; A is primary and B is a controlled re-wording. Annex EK-2, written after both variants had run but before any cross-variant comparison was computed, records that B's declared role changed at that point. The main pre-registration had called B a *consistency check*, wording that presumes B would confirm A. It does not: re-wording the system prompt alone moves abstention rates by tens of points on the same claims and the same model. EK-2 therefore reframes B as a controlled manipulation of the measurement's stability, and the instability is reported as a finding rather than as a deviation (§4.4). The reframing was declared before the comparison was computed, and we note it here because a role change of this kind is otherwise indistinguishable from choosing an interpretation after seeing the result. Output budget is part of the run label (A@32, A@128, B@128). For the hosted models, extended thinking was disabled so that the task matched the local arm, and this was verified per response rather than assumed.

**Repeat runs.** Each archived hosted configuration and each local grounded arm was executed three times and scored by majority vote. The one exception is the repeat run of §4.4, `frontCA32_bugun`, which is a single run compared against single runs, because annex EK-7 fixed that comparison at equal granularity and forbids comparing one run against a majority vote; §4.4 states the consequence for what that run can support. The policy was adopted because one local model, llama3.2:3b, reproduced only 17 of 20 identical calls; the same model also departed from the output-format instruction, so the two defects recorded for local inference belong to a single model rather than to local inference as such. Repetition is not required everywhere: for qwen2.5:32b-instruct the within-arm agreement across the three grounded runs was 1.0000 in both R1 and R2 (three pairwise comparisons, 1,524 calls per run), which is exact reproduction, so for that model the vote changes no record and a single run would have sufficed. We therefore state the repeat requirement per model, on measured agreement, rather than as a blanket rule for grounded or local execution. Where a majority-voted cell has no majority on a claim — the three runs disagree without a plurality — the claim carries no label in that cell, and §3.7 states how such claims are handled.

**Two gates, and one quantity that is deliberately not a gate.**

1. *Response-rate gate (pre-registered, as corrected in EK-1 §1).* A model × condition cell whose parsable-response rate — any usable label, of any kind, divided by 473 — falls below 0.80 is reported as non-compliant in form and is not scored. The rate is recorded for every cell and is reported for all eighteen E1 / variant A cells in Table S1; no cell lacks the figure, and no cell is retained on the ground that the figure was unavailable. Two cells fall below the gate: llama3.2:3b-instruct-q4_K_M, response rate 0.674, and llama3.2:1b, response rate 0.545. Both write the claim text back instead of emitting a label, so the failure is one of output format rather than of knowledge. Their rows are marked *gate failed* in Table S1 and carry no accuracy figure.
2. *Commitment rate (coverage) is not a gate.* It is the dependent variable of this study. A model that abstains often is producing the measurement, not failing the protocol, and no cell is excluded, downgraded, or described as non-compliant on account of low coverage anywhere in this paper.
3. *Minimum-n reporting rule (EK-1 §2, post hoc).* Accuracy-type metrics — balanced accuracy, Youden's J, d′, ECE — are reported only for cells with at least 30 committed answers. Below that the count is given and the metric is left blank. The rule exists because a balanced accuracy computed on a handful of items is not interpretable, not because the underlying behaviour is uninteresting.

Applying rule 3 to the eighteen E1 / variant A cells, using the commitment count recorded for each cell, four cells fall below the threshold, all of them variants of the same 7B model: qwen2.5:7b-instruct-q4_K_M (6 committed answers), qwen2.5:7b-instruct-fp16 (24), qwen2.5:7b-instruct-q8_0 (18) and qwen2.5:7b-instruct-q5_K_M (16). Those four rows are **kept** in Table S1, because their coverage is itself a result and removing them would hide four of the eighteen systems, but their balanced accuracies and intervals are marked *not scored*, are printed in no comparison, and support no statement in Sections 4 and 5. The accounting is therefore: eighteen cells exist, two fail the response-rate gate, four fall under the minimum-n rule, and **twelve** carry a scored accuracy figure. Separately, ECE and Brier are suppressed in 8 of 56 cells that carry fewer than 50 confidence-bearing records.

One cell sits close to the boundary and is worth naming here rather than in the results. qwen2.5:32b-instruct answers every claim in a parsable form (response rate 1.000) while committing on 82 of them (coverage 0.173). It clears the response-rate gate outright and clears the minimum-n rule by 52 items, so it is scored. Describing it as falling below a pre-registered minimum-coverage threshold would be incorrect: EK-1 §1 removed coverage from the gate, and no such threshold exists in the protocol.

**Pre-registration, and one deviation from it.** The main pre-registration (`sonuclar/F4_on_kayit.txt`) was frozen before the runs. Its item 3 applied the 0.80 gate to whether a cell "answers" the claims, and that phrase covers two distinct quantities: whether the model emitted a parsable label at all, and whether that label was a commitment rather than an abstention. Addendum EK-1 (`sonuclar/F4_on_kayit_ek.txt`, 28 July 2026) re-defined the gate onto the first of the two. The addendum was written after the closed-book calls had completed — 18 models × 2 conditions × 473 claims = 17,028 calls — but before any accuracy metric had been computed; only response and abstention counts had been inspected at that point, and the addendum records that state. The reason for the change is a definition rather than an observation: applying an 0.80 floor to the commitment rate would classify the study's dependent variable as protocol non-compliance, so that a model producing fully parsable output while abstaining on 467 of 473 claims would be scored as non-compliant when it is in fact following the instruction exactly. The correct definition does not depend on what the data turned out to show. It is nonetheless a deviation from the frozen document, EK-1 itself states that it must be declared in the paper, and we declare it here. Both rules are reported, and the sensitivity arm the addendum requires is given here rather than deferred, because its result is not a formality. Applying the original 0.80 gate to the *commitment* rate, over the twenty E1 / variant A cells excluding the rule baseline, leaves **7 cells scored and removes 13**. The 13 removed include three of the four systems this paper's findings rest on: `claude-sonnet-5` at a commitment rate of 0.615, `claude-haiku-4.5` at 0.710, and `qwen2.5:32b-instruct` at 0.173, the model that carries the entire grounded ladder of §4.6. The fourth, `gemma3:27b`, commits on 0.970 and survives the original gate; it is also the marginal cell of §4.2. The seven survivors are the high-commitment configurations, which on this claim set are the near-chance ones. **This deviation is therefore load-bearing in a way the corpus deviation of §4.6.5 is not**, and a reader who rejects the redefinition should read this paper as reporting only those seven cells. We think the redefinition is correct — a 0.80 floor on the commitment rate classifies the study's dependent variable as non-compliance, so a system that emits perfectly parsable output while declining 467 of 473 claims would be recorded as protocol-violating when it is following the instruction exactly — and the argument for it does not depend on which systems it happens to retain. But the fact that it retains precisely the systems we go on to discuss is a reason for the reader to weigh the argument rather than the outcome. The minimum-n rule above is likewise post hoc, is a reporting convention only, and is used in no hypothesis test.


## S3 — The open-weight arm in full

> The main text §4.2 reports the twelve scored cells and the two survivors; the complete listing of all eighteen open-weight cells, with response rates, commitment counts and gate outcomes, is here. The two hosted cells are in the main text's Table 1.

Eighteen open-weight models have a complete E1 cell under prompt variant A. The
two rules declared in Section 3.4 are applied to Table S1 rather than merely
stated, and they are applied in the order in which they are defined.

First, the **response-rate gate** (pre-registered, as corrected in EK-1 §1). A
cell whose parsable-response rate — any usable label, of any kind, divided by
473 — falls below 0.80 is non-compliant in form and is not scored. The per-model
response rates are part of the frozen number set and are printed in Table S1. Two
cells fail: llama3.2:3b-instruct-q4_K_M, which returned no parsable label on 154
of 473 items (response rate 0.674), and llama3.2:1b, which failed on 215
(response rate 0.545). Both write the claim text back instead of emitting a
label, so the failure is one of output format rather than of judgement. Their
balanced accuracies are withheld and enter no comparison. Of the remaining
sixteen cells, eleven returned a parsable label on every item and five on
between 0.886 and 0.998 of them.

Second, the **minimum-n reporting rule** (EK-1 §2, post hoc). Accuracy-type
metrics are reported only where the model committed to at least 30 claims; the
committed count is the count recorded for the cell, which coverage reports as a
proportion of 473 rounded to three places; the counts below are the recorded
integers, not that product. Four cells fall below that floor — 6, 24, 18
and 16 committed answers, all four qwen2.5:7b variants — and are printed as
*not scored* rather than removed, so that the reader can see that the
configurations were run and why they carry no number.

The arithmetic of the two rules is therefore 18 = 12 + 2 + 4: **twelve cells
carry a scored accuracy figure**, two are excluded by the response-rate gate,
and four fall under the minimum-n rule. Commitment rate itself is not a gate at
any point; it is the dependent variable of this study, and no cell is excluded
or described as non-compliant on account of low coverage.

**Table S1. Open-weight models, E1 / variant A.** Response rate is the share of
the 473 items returning a parsable label of any kind; committed *n* is
the recorded committed count for the cell, of which coverage is the rounded
proportion. The gate outcome column records which of the two rules of
Section 3.4 the cell meets. The interval is the **uncorrected** 95% interval;
the pre-registered correction is applied in Table S2.

| model | response rate | committed n | coverage | BAcc | 95% CI | excludes 0.5 (uncorr.) | gate outcome |
|---|---|---|---|---|---|---|---|
| qwen2.5:32b-instruct | 1.000 | 82 | 0.173 | 0.6769 | [0.5833, 0.7618] | **yes** | scored |
| gemma3:27b | 1.000 | 459 | 0.970 | 0.5674 | [0.5230, 0.6115] | **yes** | scored |
| llama3.2:3b-instruct-q8_0 | 0.886 | 418 | 0.884 | 0.5509 | [0.5073, 0.5963] | **yes** | scored |
| qwen2.5:14b-instruct | 1.000 | 97 | 0.205 | 0.5509 | [0.4839, 0.6159] | no | scored |
| gemma3:12b | 1.000 | 467 | 0.987 | 0.5493 | [0.5139, 0.5836] | **yes** | scored |
| llama3.2:3b-instruct-fp16 | 0.888 | 419 | 0.886 | 0.5434 | [0.4999, 0.5879] | no | scored |
| llama3.2:3b-instruct-q5_K_M | 0.943 | 446 | 0.943 | 0.5318 | [0.4963, 0.5676] | no | scored |
| qwen2.5:3b-instruct-q8_0 | 1.000 | 311 | 0.657 | 0.5176 | [0.4915, 0.5436] | no | scored |
| qwen2.5:3b-instruct-fp16 | 1.000 | 344 | 0.727 | 0.5126 | [0.4922, 0.5336] | no | scored |
| qwen2.5:3b-instruct-q5_K_M | 0.998 | 244 | 0.516 | 0.5124 | [0.4898, 0.5350] | no | scored |
| gemma3:4b | 1.000 | 424 | 0.896 | 0.5114 | [0.4766, 0.5456] | no | scored |
| qwen2.5:3b-instruct-q4_K_M | 0.992 | 458 | 0.968 | 0.5029 | [0.4886, 0.5183] | no | scored |
| llama3.2:3b-instruct-q4_K_M | 0.674 | 316 | 0.668 | not scored | not scored | — | **excluded: response rate < 0.80** |
| llama3.2:1b | 0.545 | 110 | 0.233 | not scored | not scored | — | **excluded: response rate < 0.80** |
| qwen2.5:7b-instruct-fp16 | 1.000 | 24 | 0.051 | not scored | not scored | — | not scored: committed n < 30 |
| qwen2.5:7b-instruct-q8_0 | 1.000 | 18 | 0.038 | not scored | not scored | — | not scored: committed n < 30 |
| qwen2.5:7b-instruct-q5_K_M | 1.000 | 16 | 0.034 | not scored | not scored | — | not scored: committed n < 30 |
| qwen2.5:7b-instruct-q4_K_M | 1.000 | 6 | 0.013 | not scored | not scored | — | not scored: committed n < 30 |

Rows are ordered by balanced accuracy among the scored cells; the six unscored
cells follow, grouped by the rule that removed them and ordered by committed n.
No statement in Sections 4 and 5 rests on a cell printed as *not scored*.

**The correction changes the count from four to two.** Eighteen configurations
are compared against the same 0.5 line, and the main pre-registration (§1)
requires a Bonferroni correction over the number of models. With 18 models and
α = 0.05, the per-cell level is 0.00278, that is, a 99.72% interval. The
correction is taken over all eighteen cells that were run, not over the twelve
that survive the gates, which is the more conservative of the two choices. Four
models exclude 0.5 at the uncorrected 95% level; two of them survive the
correction.

**Table S2. The four uncorrected candidates, before and after the
pre-registered correction.**

| model | BAcc | 95% lower | Bonferroni (99.72%) lower | coverage | excludes 0.5 after correction |
|---|---|---|---|---|---|
| qwen2.5:32b-instruct | 0.6769 | 0.5820 | 0.5349 | 0.173 | **yes** |
| gemma3:27b | 0.5674 | 0.5235 | 0.5017 | 0.970 | **yes, by 0.0017** |
| llama3.2:3b-instruct-q8_0 | 0.5509 | 0.5077 | 0.4878 | 0.884 | no |
| gemma3:12b | 0.5493 | 0.5136 | 0.4915 | 0.987 | no |

The lower bounds in Table S2 come from a separate bootstrap of 4,000 resamples
(same clustering, seed 42) run for the correction, which is why its 95% lower
bounds differ from Table S1 in the third decimal — 0.5820 against 0.5833 for the
32B model, 0.5235 against 0.5230 for gemma3:27b. The difference is resampling
noise, not a different estimator, and it does not move any verdict. The headline
should be stated with both numbers: **four models clear chance on uncorrected
intervals, two after the pre-registered correction, and the second of those two
clears it by a margin of 0.0017.** gemma3:27b is therefore a marginal case and
we describe it as one; a reader who prefers a more conservative correction, or a
different resample count, could plausibly lose it.

The two surviving models clear the line in two different ways, and the
difference is the finding.

The first way is to answer rarely. qwen2.5:32b-instruct reaches 0.6769
[0.5833, 0.7618], an interval that overlaps the hosted claude-sonnet-5 value of
0.6920 [0.633, 0.750] — but it commits on 0.173 of the claim set, 82 of 473
items, under a fifth. Its response rate is 1.000, so it passes the form gate
outright, and 82 committed answers is above the floor of 30 at which accuracy is
reported; the figure is therefore scored, and low coverage is not a
disqualification, since the pre-registration sets no minimum coverage. What the
low coverage does mean is that the score describes a small self-selected slice
and says little about the remaining 391 items. The scoring floor and the
response-rate gate it replaced are two different rules; the deviation between
the main pre-registration and its addendum on this point is recorded in
Section 3.

The second way is to answer nearly everything and clear chance by a small
margin. Uncorrected, three models did this: gemma3:27b (0.5674 at coverage
0.970), llama3.2:3b-instruct-q8_0 (0.5509 at 0.884) and gemma3:12b (0.5493 at
0.987), all five to seven points above the 0.5 line at close to complete
coverage. After the correction only gemma3:27b remains, and only just. Its point
estimate is above the smaller hosted model's 0.5298 at higher coverage, but the
intervals overlap ([0.5230, 0.6115] against [0.489, 0.570]), so we do not claim
a separation between them.

This is a coverage–accuracy trade-off, not a uniform failure. The two ways of
exceeding chance answer different operational questions: one system is more
often right on a small selected slice, the other is slightly better than a coin
across almost the whole set. Neither result is large.

**What would count as acceptable.** Deciding whether either mode is usable in a
building-inspection workflow requires a threshold, and this study does not
supply one. A threshold would have to state the cost of a false acceptance (a
non-compliant claim passed) against a false rejection (a compliant claim
escalated), and the residual error rate the reviewing authority is willing to
carry, neither of which follows from the measurements here. Two observations
bear on such a decision without settling it. A system operating at coverage
0.173 leaves the large majority of items to a human reviewer, so its value
depends on whether the routing itself is cheap. A system at coverage near 0.97
and balanced accuracy near 0.57 returns a verdict on almost every item while
being wrong on nearly as many items as it is right, so its output would have to
be treated as a prompt for review rather than as a check. We therefore report
the measurements and refrain from a general verdict on usability.


## S4 — The confirmatory contrast and its family-size sensitivity

> The main text §4.3.1 gives its own Table 3 and the verdict; the family-size sensitivity table (Table S4 below) is here.

**Which correction family this contrast belongs to.** This study carries two
distinct confirmatory families and they must not be merged. The contrast
BAcc(E1) − BAcc(E2) is item 1.2 of the main pre-registration, whose stated
correction is "Bonferroni over the number of models". Twenty models were run —
the eighteen open-weight configurations of Table S1 and the two hosted ones — so
the per-comparison level is 0.05/20 = 0.0025 and the corresponding interval is a
99.75% interval. Correcting over the models that were run, rather than over the
subset that survived the reporting gates, is the conservative choice and does
not require the family to be defined by an outcome.

Two different denominators therefore appear in this paper and the difference is
deliberate. Section 4.2 corrects the open-weight comparison against chance over
the **eighteen** open-weight configurations that produced a cell in it; this
section corrects the condition contrast over the **twenty** models that were run
at all, since both hosted models are in its scope. Each family is the set of
models eligible for the comparison it governs, and each is larger than the
number of comparisons actually made in it — twelve and two respectively — so
both are conservative. Nothing turns on the choice: Table S4 reports this
contrast at every denominator from two to twenty-one and the verdict is the same
throughout. The family of two, at 97.5%,
belongs to annex EK-4 §4 and covers the grounded-arm hypotheses H1 and H2 of
Section 4.6.3, not this contrast. An earlier draft of this paper applied the
family of two here, which understates the correction, and a later one asserted a
family of seventeen, which cannot be derived from any counting rule used in this
paper; the figures below use twenty, the number of models run, as the main text
§4.3.1 explains. Eighteen, which §4.2 uses for the open-weight comparison, is a
different and equally derivable count — the eighteen open-weight configurations
eligible for *that* comparison. Neither number is arbitrary and neither is
interchangeable with the other; what was arbitrary was seventeen.

**Table S3. Confirmatory contrast BAcc(E1) − BAcc(E2), hosted arm.** Paired
cluster bootstrap, 4,000 resamples, clusters = law + article, seed 42, v7a gold.
Correction: Bonferroni over 20 models (main pre-registration §1.2).

| system | BAcc(E1) − BAcc(E2) | 95% CI | Bonferroni-20 (99.75%) CI | excludes 0 after correction |
|---|---|---|---|---|
| claude-sonnet-5 | +0.0678 | [+0.0243, +0.1106] | [+0.0018, +0.1359] | **yes, narrowly** |
| claude-haiku-4.5 | −0.0260 | [−0.0612, +0.0130] | [−0.0765, +0.0377] | no |

**Table S4. The same contrast across a range of family sizes.** The denominator
is a judgement call, so its effect is reported rather than argued. The range
spans every count that could be defended from the run record — two (the wrong
family, retained here only because an earlier draft used it), seventeen and
eighteen (counts an earlier draft asserted but which no rule in this paper
produces), twenty (the number of models run, used above) and twenty-one (every
scored model × variant pair). Same bootstrap; only the interval level changes.

| family | level | claude-sonnet-5 | excludes 0 | claude-haiku-4.5 | excludes 0 |
|---|---|---|---|---|---|
| none | 95 % | [+0.0243, +0.1106] | yes | [−0.0612, +0.0130] | no |
| 2 | 97.5 % | [+0.0190, +0.1170] | yes | [−0.0659, +0.0183] | no |
| 17 | 99.71 % | [+0.0018, +0.1343] | yes | [−0.0765, +0.0347] | no |
| 18 | 99.72 % | [+0.0018, +0.1343] | yes | [−0.0765, +0.0347] | no |
| **20** | **99.75 %** | **[+0.0018, +0.1359]** | **yes** | **[−0.0765, +0.0377]** | **no** |
| 21 | 99.76 % | [+0.0009, +0.1359] | yes | [−0.0783, +0.0377] | no |

Neither verdict changes anywhere in that range, so the choice of denominator does
not carry either conclusion. The sonnet lower bound does shrink towards zero as
the family grows, reaching +0.0009 at twenty-one, and no claim about the *size*
of the effect should be made on this basis.

For claude-sonnet-5 the corrected interval lies above zero: permitting
abstention raises balanced accuracy, and the effect survives the pre-registered
correction. It survives it by a small margin — the corrected lower bound is
+0.0018, under two thousandths of a point of balanced accuracy — and should be
read as an effect that is established rather than an effect that is large or
robustly separated from zero. For
claude-haiku-4.5 the point estimate is negative and the corrected interval spans
zero, so no measurable benefit of abstention is established for that system;
the sign of the point estimate should not be read as a finding, because the
interval does not exclude the opposite sign. The two systems therefore differ
not only in accuracy but in whether their abstention is worth anything at all
on this measure.


## S5 — The exploratory selectivity measure in full

> The main text §4.3.2 gives the hosted figures; the complete run table, the denominator note and the declared departures from EK-1 §3 are here.

Δ is an **exploratory measure, added in Annex EK-1 §3 after the main
pre-registration**; the addendum labels it exploratory in those terms and states
that no multiple-comparison correction is applied to it. Two departures from that
addendum's text are declared here. First, the addendum describes the second arm
as the abstained items; we compute it as the complement of the committed set,
which additionally contains unparsable and no-majority records, and §3.7 gives
the reason. Second, the addendum specifies no interval for Δ and this paper
reports one, because §3.7 undertook to report differences with intervals; the
intervals are descriptive and carry no correction, consistent with the
addendum's instruction. It is not part of the
confirmatory analysis and is reported as a descriptive quantity.

**Table S5. Δ (exploratory measure, EK-1 §3).** Intervals are paired cluster
bootstraps (4,000 resamples, clusters = law + article, seed 42, v7a gold). They
are given because Section 3.7 undertook to give them; they carry no
multiple-comparison correction, in accordance with the addendum that introduced
the measure.

| run | A_com | n | A_nc | n | Δ | 95% CI |
|---|---|---|---|---|---|---|
| archive A@32 run 1 | 0.6644 | 292 | 0.5470 | 181 | 0.1174 | [+0.0344, +0.1974] |
| archive A@32 run 2 | 0.6609 | 289 | 0.5326 | 184 | 0.1283 | [+0.0385, +0.2147] |
| archive A@32 run 3 | 0.7010 | 291 | 0.5220 | 182 | 0.1791 | [+0.0914, +0.2638] |
| A@128 (earlier day) | 0.6540 | 289 | 0.5870 | 184 | 0.0670 | [−0.0180, +0.1494] |
| A@32 today | 0.6576 | 295 | 0.5562 | 178 | 0.1014 | [+0.0212, +0.1833] |
| claude-haiku-4.5, majority | 0.5672 | 335 | 0.5255 | 137 | 0.0416 | [−0.0448, +0.1380] |
| claude-sonnet-5, majority | 0.6942 | 291 | 0.5385 | 182 | 0.1557 | [+0.0724, +0.2374] |

Five of the seven intervals exclude zero. Two do not: the earlier A@128 run
([−0.0180, +0.1494]) and claude-haiku-4.5 ([−0.0448, +0.1380]). For those two
configurations non-commitment is not shown to carry information, and the
positive point estimates should not be read as though it did.

*Denominator note.* Both A_com and A_nc are E2 accuracies, so the denominator of
Δ is the set of items for which the system produced an E2 verdict, not the full
473. For a majority-voted configuration that means an item on which an E2
majority formed. The haiku row therefore sums to 472 rather than 473
(335 + 137 = 472): claim id 211 was answered under E1 but split three ways
across the three E2 runs — false, true, and one response carrying no parsable
label — so no E2 majority formed and the item leaves both arms. It is dropped
once, from one row, and is counted nowhere else. Every other row sums to 473.
The E1 partition into committed and non-committed items is unaffected by this;
only the E2 accuracy computed on each part is.

Across the hosted arm, Δ is 0.1557 [+0.0724, +0.2374] for the larger model and
0.0416 [−0.0448, +0.1380] for the smaller: non-commitment is informative in the
first case, and in the second the interval spans zero, so it is not shown to be
informative at all. That is the same ordering the confirmatory contrast of
Section 4.3.1 gives.


## S6 — Probe and subtype breakdowns in full

> The main text §4.3.3 carries the P6 result; the P5 subtype comparison, which is a null, is here with the rest.

Items 2 and 6 of the main pre-registration require the probe families and their
subtypes to be broken out and reported descriptively, with intervals and not as
hypothesis tests; item 2 fixes the minimum detectable differences in advance and
they are large — 27.6 points for the P5 contrast, 33.4 for the P6 cells — so the
pre-registration anticipated that these comparisons would be underpowered. They
are reported here because one of them is not a null.

Intervals in this subsection are Wilson intervals on the claim-level proportion
rather than the cluster bootstrap used elsewhere. These cells are small and each
draws on many articles, so a cluster bootstrap would be resampling a handful of
clusters; the pre-registration asks for intervals on these breakdowns and this is
the interval the data support. They are descriptive and carry no correction.

**P5, cross-reference claims, claude-sonnet-5 under E2.** Every P5 claim is
false, so there is no balanced accuracy to report and the quantity below is the
rate at which the system selects the gold class — the term §3.1 uses for
single-class strata, and the term the pre-registration requires here in place of
"accuracy". That rate is 0.812 [0.647, 0.911] on the 32 law-shuffle items and
0.674 [0.571, 0.763] on the 89 article-shift items, a difference of 13.8 points
against a minimum detectable difference of 27.6. The intervals overlap across
most of their range. The direction is plausible — swapping the statute is a
coarser error than moving to a neighbouring article — but the comparison has no
power to establish it and is reported as descriptive only.

**P6, currency of amendment, claude-sonnet-5 under E2.** This breakdown is not a
null, and it changes how the aggregate should be read.

Each cell is single-class, so these are gold-class selection rates, with Wilson
intervals.

| cell | n | what the claim asserts | gold | model's answers | gold-class rate | 95 % CI |
|---|---|---|---|---|---|---|
| P6_degismedi | 30 | "never amended" | false | false ×30 | 1.000 | [0.886, 1.000] |
| P6_degismedi_dogru | 30 | "never amended" | true | false ×29, true ×1 | 0.033 | [0.006, 0.167] |
| P6_yil | 30 | "amended in year N" | true | false ×30 | 0.000 | [0.000, 0.114] |
| P6_yil_yanlis | 30 | "amended in year N" | false | false ×30 | 1.000 | [0.886, 1.000] |

The model answers **false to 119 of 120 P6 claims**. Its aggregate P6 accuracy of
0.508 is not chance-level performance; it is the arithmetic of a design balanced
60 true against 60 false meeting a constant response. Read without the
breakdown, that 0.508 would be described as coin-flipping on questions of
amendment currency, and the description would be wrong in a way that matters.

The constant answer is a constant answer *to the claim*, not a constant belief
about amendment, and the two halves of the design make that explicit. Where the
claim asserts that a provision has never been amended, "false" asserts that it
was; where the claim asserts an amendment in a named year, "false" denies that
amendment. The single description that fits all four cells is that the system
rejects whatever currency proposition it is shown. That fails differently from
guessing, and it fails predictably: on this evidence it would reject a correct
statement about a provision's amendment history as readily as an incorrect one. `claude-haiku-4.5` shows the same
constancy on the two *degismedi* cells (false ×30 and false ×30) and behaves
close to randomly on the two *yil* cells (15/15 and 18/12), so the pattern is
model-specific rather than a property of the probe.

This is the same phenomenon as R3-BM25 shows in §5.4 and it is why this paper
reports λ alongside accuracy: an aggregate near 0.5 can be produced either by a
system that is guessing or by one that is answering constantly into a balanced
design, and only a bias-corrected index or a subtype breakdown separates them.


## S7 — Corpus sensitivity and the seventeen flagged claims

> The main text §4.6.5 summarises both mandatory checks; the full tables are here.

The refined corpus was made primary by annex EK-6, which also made a sensitivity
arm over the raw 1,366-unit corpus **mandatory** rather than optional, on the
ground that the refinement was a deviation from what EK-4 had named. The same
model, gold labels, output budget and seed were used; only the corpus differs.

Two properties of the comparison should be stated before the numbers. First, the
primary arm is a majority of three runs and the sensitivity arm is a single run,
so the two are comparable only if the three primary runs agree exactly; they do,
at 1,524 of 1,524 records for both k1–k2 and k1–k3, so the majority vote and any
single run are the same object here. Second, the sensitivity run satisfies the
invalidation conditions of EK-4 §10: no response was truncated (0 of 1,524) and
the retrieval recall is reported below.

**Table S6. Corpus sensitivity (EK-6 §3), qwen2.5:32b-instruct, v7a gold.**
Intervals are 95% cluster bootstraps (4,000 resamples, seed 42); the difference
column is a **paired** cluster bootstrap over the same clusters, since both
corpora are evaluated on the identical claims.

| arm | cond. | n | BAcc (1,755) | 95% CI | BAcc (1,366) | 95% CI | paired difference | 95% CI |
|---|---|---|---|---|---|---|---|---|
| R1 | E1 | 289 | 0.9164 | [0.8804, 0.9494] | 0.8976 | [0.8541, 0.9386] | +0.0188 | [−0.0040, +0.0475] |
| R1 | E2 | 289 | 0.8615 | [0.8207, 0.8987] | 0.8486 | [0.8039, 0.8910] | +0.0128 | [+0.0000, +0.0343] |
| R2 | E1 | 473 | 0.8229 | [0.7866, 0.8579] | 0.8159 | [0.7698, 0.8559] | +0.0070 | [−0.0203, +0.0354] |
| R2 | E2 | 473 | 0.8100 | [0.7763, 0.8415] | 0.8027 | [0.7633, 0.8383] | +0.0073 | [−0.0151, +0.0296] |
| R3-BM25 | — | 473 | 0.5938 | [0.5598, 0.6261] | 0.5938 | [0.5598, 0.6261] | +0.0000 | — |

**No arm shows a corpus effect that excludes zero.** Each of the four
model-bearing point estimates favours the refined corpus, by between 0.007 and
0.019 in balanced accuracy; the fifth, R3-BM25, is exactly zero. Every paired
interval contains zero. The R1 / E2 interval is the one to look at
twice: its lower bound is exactly zero, and that is not a rounding artefact. Of
its 4,000 cluster resamples, none produced a negative difference and 534
produced a difference of exactly zero — the two corpora disagree on only 4 of
289 claims in that cell, so a resample that omits those clusters returns an
identical score for both. The 2.5th percentile is therefore exactly zero, the
interval touches zero, and the difference is read here as not established. Decision agreement between the two corpora is
high but not total — 421 of 473 for R2 under E1, 447 of 473 under E2, 280 of 289
and 285 of 289 for R1 — so the corpora do produce different individual decisions,
and the null result is a statement about the aggregate rather than about the
runs being identical. The conclusion is that **the results of Sections 4.6.2 and
4.6.3 do not depend on the corpus deviation declared in EK-6**, which is what
the mandatory sensitivity arm was there to establish.

**The raw corpus retrieves better and scores slightly worse.** BM25 recall of the
cited unit is 87 of 289 (0.3010) over the raw corpus against 79 of 289 (0.2734)
over the refined one: splitting fused units into finer ones makes the top-3 less
likely to contain the cited unit, which is expected. What is not expected on a
retrieval-bound account is that the arm with the *higher* recall has the
*lower* balanced accuracy in all four grounded cells. This is a second and
independent instance of the dissociation reported in Section 4.6.4, obtained by
varying the corpus rather than by comparing recall against accuracy within one
configuration.

**The rule baseline is unchanged to four decimals.** R3-BM25 returns identical
decisions on all 473 claims under both corpora, despite receiving a different set
of retrieved passages for 271 of the 473 claims and a different recall figure.
This was checked rather than assumed: the two runs carry different corpus
checksums and different retrieved-unit lists. A containment rule is evidently
sensitive to whether the matching string is present somewhere in the three
supplied passages and largely indifferent to which unit boundaries produced them.

Building the refined corpus surfaced 32 anomalies: 31 claims whose quoted text
was located in a unit other than the one the claim record names, plus one whose
quoted text could not be located anywhere in its document. That last one is a
different kind of problem — a quotation with no source rather than a
misattributed one — and it is carried in the defect log rather than in this
count; the seventeen discussed here come from the 31. Measurement resolved 14 of them
as artefacts of the splitting procedure or as cases the expert reconciliation had
already corrected. The remaining **17 were declared `needs_human_review`** under
annex EK-6 §4, which forbids resolving borderline cases automatically, keeps them
in the run — removing them would change the selectivity being measured — and
requires that they appear as a separate row and enter the primary comparisons as
a sensitivity check. The claim identifiers are 25, 38, 60, 70, 123, 159, 189,
203, 211, 278, 310, 323, 351, 426, 444, 455 and 476. **No gold label
changed**, and the v7a labels used throughout this paper are the labels those
claims already carried — but the route to that outcome has to be stated, because
it is not the route the rest of the audit took.

An adjudication pass over the seventeen was produced by a language model rather
than by the two human coders whose agreement Section 4.7 measures. Thirteen of
its rows confirmed the existing label; four proposed decisions, of which three
were label changes. We did not adopt them. The three (claims 278, 426 and 444)
rest on reading the `madde` field of the claim record as the provision the claim
cites, whereas annex EK-4 §2 defines that field as the provision the claim's text
was drawn *from*; all three cite at document level ("under TBDY 2018"), their
content is present in that document, and EK-4 §9(d) resolves document-level
citations against the whole document. The deterministic baseline detected the
same thing independently: R3-rule scores 473/473 against the unaltered labels and
drops to 470/473 against the altered ones, disagreeing on exactly those three
claims.

The seventeen therefore remain `needs_human_review`. We report them this way
rather than as resolved because a study measuring whether language models can
judge Turkish regulation cannot let a language model set the labels it is scored
against without saying so; on those items the measurement would be partly
circular. Nothing in this paper depends on the outcome either way, as the
sensitivity check below shows.

**Table S7. The seventeen flagged claims, scored separately.**

| arm | condition | n | committed | accuracy |
|---|---|---|---|---|
| R1 | E1 | 8 | 7 | 1.0000 |
| R1 | E2 | 8 | 8 | 1.0000 |
| R2 | E1 | 17 | 16 | 0.8125 |
| R2 | E2 | 17 | 17 | 0.8824 |
| R3-BM25 | — | 17 | 17 | 0.5294 |

Removing them from the headline contrast moves it by less than the width of its
interval: R2 − R3-BM25 is +0.2292 [+0.1939, +0.2635] on all 473 claims and
+0.2312 [+0.1943, +0.2672] on the 456 that remain under E1, and +0.2162
[+0.1818, +0.2493] against +0.2154 [+0.1798, +0.2504] under E2. The flagged
claims are not driving the result.


## S8 — The expert audit: design and both passes

> The main text §4.7 reports the outcome of both passes; the sampling design, stratum weights and the reconciliation of the 158 / 150 / 138 counts are here.

Five deterministic layers (source identity, accidental truth, sentence cleaning, rendering-artefact repair, design-leak audit) were applied first, each with a positive control that had to fire. Two specialists in civil engineering and occupational safety then audited the labels in two passes with gold, probe family, template and stratum hidden, and row order randomised per rater. The two raters worked from separate workbooks and each was required to enter a free-text rationale; rationale-text identity between raters was checked as an independence control.

| | First pass | Second pass |
|---|---|---|
| Question put to the rater | is the claim consistent with the quoted sentence? | is the claim true of the whole article, read in the source? |
| Sample | 150 items (158 codes with controls) | 60 items: 58 scored + 2 seeded controls |
| Strata | unflagged / consensus-flagged | N: all 33 items either rater called less than clean; T: 25 drawn from the 105 both called clean; K: 2 seeded known-bad controls |
| κ, verdict axis | 1.000, 95 % CI [1.000, 1.000] | **0.722**, approximate 95 % CI [0.513, 0.933] (p_o = 0.897, p_e = 0.628, n = 58) — analysed in §4.7 |
| κ, verdict excluding "not sure" | 1.000, 95 % CI [1.000, 1.000] | — |
| κ, item-quality axis | 0.860, 95 % CI [0.759, 0.961] | — |

The first-pass κ of 1.000 is a property of the instrument rather than evidence that the labels are sound: the workbook shows the rater the quoted sentence and the recorded article, which is the same evidence the label was derived from, so the pass re-derives the generator's reasoning instead of testing it against the legislation. Contextual defect counts from the first pass are zero in each of the five probe families the pass sampled (P1 0/22, P2 0/17, P3 0/15, P4 0/12, P5 0/16); the sixth family, currency of amendment (P6), was not sampled by this pass and is instead checked against official sources in §4.7, so the phrase "every family" would misdescribe the coverage. With these sample sizes the 95 % upper bounds run from 14.9 % to 24.3 %, so the pass bounds the rate loosely rather than establishing it. It bounds it more loosely still once the second pass is read, for the reason given below.

**Design of the second pass.** The second pass was built to reach the class the first cannot: a sentence that, lifted from its article, no longer says what the article says. Raters opened the source and read the whole article. Its sampling frame is 138 items, and the step from 150 to 138 is worth stating because both numbers appear in this paper: the first-pass workbook holds 158 codes, of which 8 are seeded traps, leaving the 150 real claims on which the first-pass κ is computed; 12 of those 150 were removed from the claim set during the repair that produced the version this pass samples from, and an item no longer in the set cannot be sampled. The frame is therefore the 138 that survive, split 33 N + 105 T; the N stratum was taken whole, the T stratum was sampled at 25 of 105, and 2 items with known gold errors were seeded as a positive control. Analysis was specified as follows.

1. *Two decision rules, declared in advance of interpretation.* An item counts as a contextual defect under the **lenient** rule if at least one rater's verdict differs from gold, and under the **strict** rule if both do. The two rules bracket the quantity from opposite sides and both are reported.
2. *Which rule is primary is decided by the seeded control, not by preference.* The rule that recovers the known-bad items is the primary measure; the other is reported as a bound. The control result is given in §4.7, and it selects the lenient rule. One consequence must be carried back to the paragraph above: the strict rule is the rule under which the first pass returned zero defects in each of the five families it sampled, and the strict rule failed the seeded control here. The first-pass zeros are therefore a lower bound on the contextual defect rate, not an estimate of it, and are read that way throughout.
3. *Stratum weighting.* Rates are computed per stratum and combined with the design weights implied by the sampling: 33/33 for N and 105/25 for T. A frame estimate for the 138 first-pass items is reported, and separately a compound-weighted figure projecting to the whole claim set; the two are distinct quantities and are labelled as such.
4. *Zero-event strata.* Where a stratum records no events, a one-sided 95 % upper bound is reported. The form "0.0 % [0.0 %, 0.0 %]" is not used.
5. *Direction of disagreement.* Rater disagreements are cross-tabulated by direction and tested with a sign test, because a disagreement that runs one way is evidence of two rules being applied rather than of noise around one rule, and the two call for different remedies — the first cannot be closed by averaging.
6. *Predictive validity of the first-pass flag.* Whether the first-pass quality flag predicts contextual defects is tested by comparing the N and T defect rates with a Fisher exact test. The N/T contrast is a two-stage sampling artefact by construction, so it is reported as a single test with its p-value attached and no claim of validity is made on the strength of the point ratio alone.

The κ of 0.722 in the table is a substantial fall from the first pass, its disagreement structure is not symmetric, and the seeded control was not recovered under the strict rule. These outcomes are reported with their numbers in §4.7 and carried into the limitations of Section 6, because they qualify the gold-label quality claim that Sections 4 and 5 rest on. They are not averaged away here.

One further consequence must be stated plainly, because it bears on how the R3-rule result above may be read. The 7 gold corrections were proposed after a corpus observation — the clause-merging defect — and the same observation motivated the refined corpus; the expert step confirmed the mis-attribution on those items but did not generate the labels independently, and R3-rule failed on those same 7 items rather than identifying them from scratch. The agreement between corpus repair, gold repair and R3-rule therefore contains a circular component, and the three are not independent confirmations of each other.

---

### First pass

The first pass put one question: is the claim consistent with the sentence
quoted in the record? On 150 items (158 codes including controls), agreement was
exact on the verdict axis, Cohen's κ = 1.000, 95% CI [1.000, 1.000], and
unchanged when "not sure" responses were excluded. On the item-quality axis
κ = 0.860, 95% CI [0.759, 0.961]. Contextual defect counts were zero in each of the
five families this pass sampled: P1 0/22, P2 0/17, P3 0/15, P4 0/12, P5 0/16.
P6, currency of amendment, carries no first-pass count; it was verified against
mevzuat.gov.tr instead (20 of 20 agreeing), and that check covers three of the
six documents.

Neither figure should be read as evidence that the labels are sound. A κ of
1.000 is a property of the instrument: the workbook shows the rater the quoted
sentence and the recorded article, which is the same evidence the label was
derived from, so the pass re-derives the generator's reasoning rather than
testing it against the legislation. And the zero defect counts bound the rate
only loosely — at these sample sizes the 95% upper bounds run from 14.9% to
24.3%, so "zero observed" is consistent with a defect rate approaching one item
in five within a family.

---

### Second pass

The second pass was designed to reach the class the first cannot — a sentence
that, lifted from its article, no longer says what the article says. Raters
opened the source and read the whole article. Sixty items were drawn from a
frame of 138 first-pass items in three strata: all 33 items that at least one
rater had not called clean (stratum N), 25 of the 105 both raters had called
clean (stratum T), and 2 seeded items with known-bad gold labels as a positive
control (stratum K).

**Agreement fell.** On the 58 non-control items, Cohen's κ = 0.722, with an approximate 95 % confidence interval of [0.513, 0.933] from the Fleiss standard-error formula. The interval is wide and the normal approximation is rough at n = 58, so it is labelled approximate; it is given because the first-pass κ is reported with an interval and reporting only the favourable one with its uncertainty would be asymmetric. The first-pass interval [1.000, 1.000] and this one do not overlap. κ = 0.722
(observed agreement 0.897, chance agreement 0.628). Six items were scored
differently by the two raters, and all six ran the same way: the rater who
disagreed always moved in one direction rather than the other. A sign test on
that direction gives p = 0.0312, so the disagreement is systematic and not
sampling noise. The audit report's own conclusion is that the two raters are
applying different rules, that this is a definitional problem rather than a
measurement error, and that it cannot be closed by averaging the two ratings —
it requires an adjudication session between the raters, which had not been held
at the time of writing. We report the second-pass figures on that basis and do
not treat the first-pass κ of 1.000 as the audit's summary.

**The positive control did not fire cleanly.** Two items with known-bad gold
labels were seeded into the second-pass sample. Under the strict rule — an item
counts as caught only when both raters flag it — 0 of 2 were caught. Under the
lenient rule — at least one rater flags it — 1 of 2 was caught. The audit report
draws the consequence: the lenient rule must be the primary measure and the
strict rule gives a lower bound only, and the first pass's 0-of-150 clean result
has to be read in the same light, since an instrument that misses seeded bad
labels cannot certify their absence.

**Contextual error rate.** Under the lenient rule, the observed contextual error
rate is 5 of 33 in stratum N (15.2%, 95% CI [6.7%, 30.9%]) and 1 of 25 in
stratum T (4.0%, 95% CI [0.7%, 19.5%]). Weighting the strata back to the
138-item frame gives an estimated 6.7%, 95% CI [1.6%, 11.8%]; a composite
weighting projected onto the whole claim set gives 8.8%. Under the strict rule
no event was observed in 58 items, giving a one-sided 95% upper bound of 6.2%.
The lenient figures are the ones to use, for the reason the positive control
gives.

**The first-pass quality flag is a trend, not a predictor.** The design assumed
that items the first pass flagged would be enriched for contextual errors, and
directionally they were: 15.2% in stratum N against 4.0% in stratum T, a lift of
3.8×. That difference is not statistically significant (Fisher exact
p = 0.2216), so we report it as a trend and make no claim of predictive validity
for the first-pass flag. A screening pass that cannot be shown to concentrate
errors cannot be used to argue that the unscreened remainder is clean.


## S9 — Every result under both label sets

> The main text §4.7 states the one verdict that changes and the summary statistics; this section gives the comparison in prose rather than as a 56-row table. The full 56-cell table under all three gold versions is in the released archive (`sonuclar/f4_analiz_raporu.txt`, section 5); it is not reproduced here because every row but the ones discussed differs in the third decimal or less.

Annex EK-5 §8 requires that results be reported under the pre-revision gold (v6)
alongside the post-reconciliation gold (v7a), on the ground that a large
difference would itself be a finding. All 56 model × condition cells were scored
under three label sets — v7a as primary, v6 and v7b as sensitivity — and the
comparison is summarised here rather than tabulated in full, since the
differences are small and uniform.

Across the model cells the mean absolute difference between v7a and v6 balanced
accuracy is 0.0039. The largest is 0.0346, at `qwen2.5:32b-instruct` under E1
(0.6769 against 0.6423) — the low-coverage cell where 82 commitments make each
relabelled claim weigh more — followed by 0.0208 at `llama3.2:1b` under E2. **One verdict does change under v6, and it is reported rather than smoothed.**
Recomputing the corrected intervals of Section 4.2 against v6 leaves
`qwen2.5:32b-instruct` and `gemma3:27b` excluding chance as before, but
`gemma3:12b` also excludes it, with a corrected lower bound of 0.5013 against
0.4915 under v7a. Three cells survive correction under v6 where two survive
under v7a. The additional cell clears chance by 0.0013 of balanced accuracy —
narrower still than the 0.0017 by which `gemma3:27b` clears it under v7a — so
what the comparison exposes is the fragility of cells sitting on the threshold
rather than a difference in what the models can do. A reader should take from
this that no engineering decision belongs on either marginal cell, which is what
Section 4.2 already says about the first of them.

λ is the measure EK-5 predicted would be most exposed, since the P1 label
distribution changes, and the prediction holds: in three of the four hosted
cells λ moves further between label sets than balanced accuracy does (0.0088
against 0.0045, 0.0072 against 0.0029, 0.0061 against 0.0017), the exception
being `claude-sonnet-5` under E2 (0.0061 against 0.0072). The absolute
movements are small, but the ordering is the one the annex anticipated and it is
reported here as such rather than the other way round.

The one cell where the label set matters qualitatively is the deterministic
baseline R3-rule. Two different quantities are involved and they must not be run
together. Its exact-match count against the **refined** corpus is 473/473 with
v7a. The figure in the gold-comparison table, 0.9860 under v7a against 1.0000
under v6, is a balanced accuracy on the **raw** corpus cell, where the exact-match
count is 466/473. That gap is not noise but the EK-5 correction itself: seven gold
labels were revised, and the baseline had been agreeing with the pre-revision
versions. Section 4.5 is about exactly that.
