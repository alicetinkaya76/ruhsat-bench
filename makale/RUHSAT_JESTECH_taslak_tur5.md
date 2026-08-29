# RUHSAT-Bench — JESTECH taslağı (5. tur)

<!-- YAZAR BLOGU — gonderim oncesi Ali tarafindan doldurulur. Iceriden
     uydurulmus hicbir alan yoktur; bos birakilan her alan bilerek bostur. -->

**Title.** Measuring abstention, not accuracy: a re-qualification benchmark for
language-model decision support on Turkish construction and occupational-safety
regulation

**Authors.** [AUTHOR 1], [AUTHOR 2] — *affiliations, ORCIDs and the corresponding
author to be supplied at submission.*

**Corresponding author.** [e-mail]

---

## Abstract

Decision-support software used in regulatory compliance checking is qualified
before it is trusted, and a qualification asks not only how often a tool is
right but whether it declines the cases it cannot handle. We report RUHSAT-Bench,
a benchmark of 473 true/false claims over six frozen Turkish regulatory
documents — the Development Law, the Building Inspection Law and its implementing
regulation, the Occupational Health and Safety Law and its risk-assessment
regulation, and the Turkish Building Earthquake Code TBDY 2018 — scored under
two conditions: one permitting an explicit "not sure" (E1) and one forcing a
binary verdict (E2). Gold labels were audited by two domain specialists in two
blinded passes and the audit is reported in full, including its negative result.

Three findings are reported. First, closed book, the systems tested sit at a
coverage–accuracy trade-off rather than at a uniform failure: of eighteen
open-weight configurations, twelve carry a scored accuracy figure and, after the
pre-registered Bonferroni correction over models, two exclude chance — one of
them by less than two thousandths of a point. Second, supplying the governing
text changes the operating point decisively. On the pre-registered primary
family, a 32B open-weight model gains +0.2607 in balanced accuracy under forced
choice when three retrieved passages are supplied (95% CI [+0.2218, +0.2964])
and +0.3552 when the cited article is supplied (95% CI [+0.3112, +0.3984]); both
survive correction. Against a string-matching rule applied to the *same*
retrieved passages, the model adds +0.2292 under E1 (95% CI [+0.1939, +0.2635]),
so the judgement step is separable from the presence of evidence. Third, and
this is the qualification result: a hosted model re-run months later on the same
frozen claim set, at the same budget and with byte-identical prompts, kept its
forced-choice accuracy but lost roughly half of what abstention had been buying
it (BAcc(E1) − BAcc(E2) falling from 0.0762 to 0.0332) while the number of
abstentions barely moved. A qualified component changed in a way that
forced-choice accuracy, the measure most benchmarks report, does not see.

We draw an engineering conclusion rather than a claim about language models:
closed-book use of these tools on this material is not defensible, retrieval-
grounded use reaches a materially different operating point, and any acceptance
criterion has to be stated over abstention behaviour and re-checked over time.
The benchmark, the frozen documents, the pre-registrations and the analysis code
are released so that the re-qualification can be repeated.

**Keywords.** compliance checking; decision-support software qualification;
abstention; selective prediction; large language models; building regulation

---

# 1. Introduction

Building permitting and inspection in Türkiye rest on a compact stack of binding instruments: the Development Law (No. 3194), the Building Inspection Law (No. 4708) together with its implementing regulation (YDUY), the Occupational Health and Safety Law (No. 6331) with the risk-assessment regulation, and the Turkish Building Earthquake Code (TBDY 2018). Much of the daily work in an inspection office is documentary rather than analytical: does an obligation sit in Law 4708 or in its regulation, is the article a file cites the article that actually carries the rule, was that article amended in the year an applicant states. Each such question has a checkable answer in a published text.

Automating these checks is a long-standing goal in construction informatics. Rule-based model checking encodes provisions as machine-verifiable constraints (Eastman et al., 2009; Solihin and Eastman, 2015), while NLP-driven extraction attempts to recover those constraints from the regulatory text itself (Zhang and El-Gohary, 2013; Zhou and El-Gohary, 2016), and more recent work places a language model inside the compliance-checking loop (Chen et al., 2024). Those lines assume the governing text is in hand. Large language models (LLMs) also support a different proposition: an answer produced from model parameters with no document supplied. We refer to this as the **closed-book** setting — the system is asked about a provision without being shown it, the way a person answers from memory. It is also one of the ways these systems are in fact consulted, when an engineer types a regulatory question into a chat window and acts on what comes back (Dahl et al., 2024; Magesh et al., 2025).

**Terminology.** A model *abstains* when it returns "I am not sure" instead of a verdict; *coverage* is the fraction of claims on which it commits to a verdict, so coverage 1.000 means it always answers. *Balanced accuracy* averages accuracy on true claims with accuracy on false claims, so a system that answers "false" to everything scores 0.5 regardless of how many false claims the set happens to contain. *Calibration* is the correspondence between stated confidence and observed correctness, in the sense in which a pressure gauge is calibrated against a reference: a gauge that reads 6 bar should mean 6 bar, and a model that reports 90 % confidence should be right on about 90 % of such items (Guo et al., 2017; Jiang et al., 2021). *Expected calibration error* (ECE) is the average gap between the two, so smaller is better (Naeini et al., 2015). Confidence intervals are obtained by *bootstrap* — repeatedly resampling the evaluated claims and reading the spread of the resulting scores — clustered by statute and article, so that claims from the same article are resampled together.

**RUHSAT-Bench.** We assemble 473 claims over the six documents above, indexed against a corpus of 1,755 regulatory units, with a gold label distribution of 223 true and 250 false. Claims are organised in six probe families: direct assertion (163), numeric value (37), cross-reference (121), currency of amendment (120), anachronism (19), and fabricated provision (13). Each system is run under two conditions: abstention-permitted (E1) and forced binary choice (E2). Closed-book operation is one arm of the design, not the whole of it: a grounded ladder run on the same claims differs from the closed-book arm only in the evidence supplied and in who judges it — the cited article verbatim (R1), passages returned by an untuned BM25 retriever (R2), and those same retrieved passages judged by a lexical containment rule with no model at all (R3-BM25) — so that the study measures a mode of use rather than pronouncing on a technology. A separate deterministic control that performs no retrieval, R3-rule, is used to check the scoring path rather than to compete with the models; the two are kept apart throughout, and Section 3.5 states why.

**Gold labels and what the audit does and does not certify.** Two coders audited the claim set. On the first pass — is the claim, read on its own, correctly labelled — agreement was complete on the decision axis (Cohen's κ = 1.000, n = 150) and high on the quality axis (κ = 0.860). A second pass asked a harder question: whether a claim still says what its source article says once the whole article is read. There agreement fell to κ = 0.722 (n = 58), all six disagreements ran in the same direction (sign test p = 0.0312), and the two known gold errors planted as a positive control were caught 1 of 2 by the looser adjudication rule and 0 of 2 by the strict one. The pattern is systematic rather than random: the two coders are applying different rules, which is a definitional problem and not a measurement error, and it cannot be closed by averaging. We report the first-pass figures and the second-pass figures together throughout, because the first on its own would overstate what the audit establishes. Section 4 gives the full second-pass result and Section 6 treats it as a limitation on gold-label quality. Independently of the coders, the currency-of-amendment family was checked against official HTML on mevzuat.gov.tr, where 20 of 20 sampled claims agreed.

**What would count as usable?** A benchmark number is not a verdict on its own; declaring a system unusable requires a threshold, and we could not locate a defensible one. Turkish building-inspection practice sets no accuracy requirement for advisory software, and the compliance-checking literature reports system performance without stating an acceptance level. We therefore do not issue an absolute verdict. Section 2.2 sets out the shape such a criterion would need to have — which is, we argue, a criterion on the abstention behaviour rather than on accuracy alone — and our results are reported so that a reader who does have a threshold in mind can apply it.

**Contributions.**

1. A regulatory benchmark for Turkish construction law with auditable provenance: every reported figure is regenerated from committed script outputs, and the claim set, gold labels and expert-audit record — including the negative second-pass result — are released with the code. One deviation between the main pre-registration and its first appendix is declared in Section 3, together with its date and its reason.

2. A measured **coverage–accuracy trade-off** among open-weight models rather than a blanket failure. Eighteen open-weight configurations were run to an E1 cell under prompt variant A; twelve of those cells are scored. Two are removed by the pre-registered gate on the parsable-response rate, which requires a parsable answer on at least 80 % of items: llama3.2:3b-instruct-q4_K_M (0.674) and llama3.2:1b (0.545). Four qwen2.5:7b variants are left unscored because they commit on fewer than 30 items — 6 (q4_K_M), 24 (fp16), 18 (q8_0) and 16 (q5_K_M) committed items — which is the floor below which accuracy-type metrics are not reported; their balanced-accuracy values accordingly support no statement anywhere in this paper. Read with uncorrected 95 % cluster-bootstrap intervals, four of the twelve scored cells exclude 0.5. The pre-registration requires a Bonferroni correction over the number of models — 18 models, a per-cell level of 0.00278, that is 99.72 % intervals — and after that correction two survive: qwen2.5:32b-instruct, balanced accuracy 0.6769, lower bound 0.5820 uncorrected and 0.5349 corrected, at coverage 0.173; and gemma3:27b, balanced accuracy 0.5674, lower bound 0.5235 uncorrected and 0.5017 corrected, at coverage 0.970. The second clears chance by less than two thousandths of a point and should be read as marginal. The two that do not survive the correction are llama3.2:3b-instruct-q8_0 (0.5509, corrected lower bound 0.4878) and gemma3:12b (0.5493, corrected lower bound 0.4915). The 32B model's uncorrected interval overlaps that of the hosted claude-sonnet-5 (0.6920 [0.633, 0.750], coverage 0.615), but it reaches its score while committing on roughly one claim in six — 82 committed items, above the floor of 30, so the cell is scored, and its accuracy and its coverage have to be read as one figure rather than two. Which operating point is preferable depends on the workflow, and Section 2.2 argues the choice cannot be made by accuracy alone.

3. An account of abstention as a measured quantity rather than an assumed safety feature. Two summaries are reported side by side. The confirmatory contrast BAcc(E1) − BAcc(E2) belongs to the main pre-registration and, because that confirmatory family contains two contrasts, is read at a Bonferroni-2 level (97.5 % intervals): for claude-sonnet-5 it is +0.0678 [+0.0190, +0.1170], which excludes zero, so permitting abstention raises accuracy; for claude-haiku-4.5 it is −0.0260 [−0.0659, +0.0183], which does not, so abstention buys that model no measurable accuracy. The second summary is Δ, the difference in forced-choice accuracy between the items a model committed to and the items it did not commit to. Δ is exploratory, added in EK-1 after the main pre-registration; it is not part of the confirmatory set and carries no multiple-comparison correction. Both are given because they do not agree in magnitude, and reporting only one would let an author choose the larger effect.

4. A re-qualification result: on a frozen claim set and prompts we verified to be byte-identical, a re-run of one hosted configuration falls outside the archived run-to-run range while remaining inside the archived clustered bootstrap interval. We report both baselines and justify which one answers the version question (Section 5).

5. **A grounded-arm measurement showing that the closed-book figures describe a mode of use, not a ceiling on the task.** For qwen2.5:32b-instruct — the same open-weight model that scores balanced accuracy 0.6769 at coverage 0.173 closed-book, and 0.5493 under forced choice — supplying the governing text changes the operating point. All intervals below are 95 % cluster bootstrap, 4,000 resamples, clustered by statute and article, seed 42. Given the cited article verbatim (R1), balanced accuracy is 0.9164 [0.8804, 0.9494] (n = 289, coverage 0.830) with abstention permitted and 0.8615 [0.8207, 0.8987] at full coverage under forced choice. Given instead whatever one untuned BM25 retriever returns at k = 3 (R2), it is 0.8229 [0.7866, 0.8579] (n = 473, coverage 0.899) and 0.8100 [0.7763, 0.8415] at full coverage. R3-BM25 — the same retrieved passages with no model, the verdict coming from lexical match alone — reaches 0.5938 [0.5598, 0.6261]. The paired difference R2 − R3-BM25, computed on the same clusters, is therefore +0.2292 [+0.1939, +0.2635] with abstention permitted and +0.2162 [+0.1818, +0.2493] under forced choice; both exclude zero, so the language model's contribution over string matching on identical evidence is separable from sampling noise. The cost of using retrieval rather than a perfect citation is 0.0935 (E1) and 0.0515 (E2) points, reported as point differences because no interval was computed for that contrast. Each grounded arm was run three times and scored by majority vote, with 0 of 1,524 responses truncated per run. What this does not establish is *why* the grounded arms succeed: the retriever's own recall is only 0.2734, so the model is evidently completing from parametric knowledge on many items, and the two contributions were not separated here.

6. A retrieval measurement bounded to what was tested: one untuned BM25 retriever — BM25 being a standard ranking function that scores a passage by how many of the query's *tokens* (word-like units) it contains, weighted by their rarity (Robertson and Zaragoza, 2009) — placed the cited unit among the top three for 79 of 289 article-level citations (recall 0.2734) on this corpus. That figure characterises this retriever at this setting on this corpus. It is not a bound on the accuracy of a system built on it, and should not be read as one: the R2 arm, using exactly these retrieved passages, scored 0.8229. It is likewise not a claim about retrieval-augmented systems in general.

# 2. Motivation

## 2.1 Fail-safe and fail-silent behaviour

Safety engineering distinguishes a component that fails into a defined safe state from one that fails while continuing to emit plausible output. A load cell that saturates and reads zero announces its own failure; one that drifts by 15 % does not. Functional-safety practice treats the second class as the harder problem, because the downstream process has no signal that anything is wrong (IEC 61508).

An LLM asked a closed-book regulatory question is a candidate fail-silent component. It returns a fluent verdict with a confidence figure attached, in the same register whether the provision is one it can reproduce or one it has never encountered. If the confidence figure tracked correctness, the component would be fail-safe by construction: an inspector could route low-confidence items to manual review. This is precisely the promise of selective prediction, where a classifier is permitted to reject inputs it cannot handle (Chow, 1970; El-Yaniv and Wiener, 2010; Geifman and El-Yaniv, 2017), and of work asking whether language models know what they know (Kadavath et al., 2022; Lin et al., 2022; Xiong et al., 2024).

Whether that promise holds for regulatory text is an empirical question, and it is the question this benchmark is built to answer. It cannot be answered by accuracy, because accuracy conditions on the items a model chose to answer. A system that abstains on 83 % of claims and a system that answers all of them are not comparable on accuracy alone; both numbers are reported here alongside coverage for that reason. The closed-book arm isolates the failure mode; it is not the recommended architecture, and the grounded arms of Section 3.5 are run precisely so that a poor closed-book figure is not mistaken for a limit on what the same model can do when the governing article is placed in front of it.

## 2.2 An acceptance criterion has to be about abstention

Consider a building-inspection workflow in which a model pre-screens claims in a permit file and flags the doubtful ones for an engineer. The quantity that governs whether this saves work is not overall accuracy: it is whether the flagged set is enriched for errors. If abstention is uninformative — if the model declines items it would have got right at the same rate as items it would have got wrong — then the flags carry no triage value and the engineer must check everything regardless, at which point the screening step costs time without removing any.

This gives the shape of a usable acceptance criterion: a stated coverage level, an accuracy on the covered items, and evidence that accuracy on the abstained items is materially lower. Calibration enters the same criterion, because a confidence figure is only actionable if it means what it says; a model whose ECE is large is reporting a gauge reading that has not been calibrated against anything. We do not fix numeric values for these three quantities, because we have no principled basis on which to fix them for Turkish inspection practice, and we avoid statements of the form "this system cannot be used". We report the three quantities so that an organisation with its own tolerance can evaluate them. We are not aware of an established risk-based acceptance threshold for decision-support software in construction that could be adopted here, which is itself part of the reason the criterion is left open.

## 2.3 Benchmarks expire, so systems have to be re-qualified

A calibration certificate for a torque wrench carries an expiry date; the instrument is re-qualified on a schedule because its behaviour drifts. Hosted LLMs are updated behind a stable model identifier, and Section 4.4 reports one case in which behaviour on a fixed task changed between two dates without any announced version change. We attach no citation to the general phenomenon: we found no published account of it whose bibliographic record we could verify, and the evidence offered here for it is our own measurement. A benchmark score for such a system is therefore a measurement at a date, not a property of the name.

We treat this as part of the study design rather than as a limitation note. One hosted configuration was re-run on the frozen 473-claim set months after the archived runs, under prompts whose identity we verified. Section 4.4 reports what changed and Section 5.3 sets out which baseline the comparison should use and what the provenance of the archived runs does and does not allow us to assert. The result is reported not because the direction of the change is itself of interest, but because it establishes that a score of this kind needs a date attached and a re-qualification procedure defined — which is a requirement any deployment in a regulated inspection workflow would have to meet.

---

# 3. Materials and Methods

## 3.1 Terms used in this paper

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

## 3.2 Corpus

Six frozen Turkish regulatory documents cover permitting, building inspection, occupational health and safety, and seismic design. Each was segmented into units by the same parsers that generate the claims, so that a retrieved unit and the unit a claim was written from are the same object.

| Code | Document | Units (raw) | Characters |
|---|---|---|---|
| 3194 | İmar Kanunu | 49 | 158,417 |
| 6331 | İş Sağlığı ve Güvenliği Kanunu | 39 | 71,025 |
| YDUY | Yapı Denetimi Uygulama Yönetmeliği | 36 | 94,556 |
| ISGRISK | İSG Risk Değerlendirmesi Yönetmeliği | 19 | 16,703 |
| 4708 | Yapı Denetimi Hakkında Kanun | 15 | 55,563 |
| TBDY | Türkiye Bina Deprem Yönetmeliği 2018 (technical annex) | 1,208 | 870,747 |
| | **Total (raw corpus)** | **1,366** | |

Each document is identified in the release by a SHA-256 of its extracted text. The raw segmentation was later found to merge adjacent TBDY clauses, so a refined corpus was built and made primary (EK-6): TBDY 1,208 → 1,523 units, the five remaining documents 158 → 232 units, the latter recovering annex and provisional articles that the first parser had dropped (16 annex and 58 provisional articles). The refined corpus holds 1,755 units. The raw 1,366-unit corpus is retained as a **mandatory sensitivity arm**, because it, not the refined one, is what the pre-registration named: EK-6 §3 requires the same grounded arms to be run over it and reported side by side with the primary corpus.
 The arm was run and is reported side by side in Section 4.6.5; no result in this paper depends on which of the two corpora is used.

## 3.3 Claim set

A sealed deterministic generator produced 473 claims from the corpus; the generator was never re-executed, so claim identifiers are stable across the whole study. The gold distribution is 223 true / 250 false. Six probe families are represented: P1 verbatim or article-cited provision (163), P5 provision attributed to the wrong article or document (121), P6 amendment-history statement (120), P2 altered quantity (37), P3 enactment-year statement (19), P4 invented document or clause (13). Surface form is held constant within contrasting pairs, so P1, P2 and P5 items are lexically alike and separable only through knowledge of the source.

Citations are resolved from the claim text alone, never from the generator's bookkeeping columns, because in P5 the cited location and the true source deliberately differ: 289 claims cite an article, 184 cite only a document. This is the same operation an engineer performs — look at the provision the claim points to.

## 3.4 Conditions, prompt variants, runs and scoring gates

Every claim is asked twice. **E1** allows abstention (true / false / not sure); **E2** forces a binary choice. Two system-prompt variants (A and B) were written for each condition; A is primary and B is a controlled re-wording. Output budget is part of the run label (A@32, A@128, B@128). For the hosted models, extended thinking was disabled so that the task matched the local arm, and this was verified per response rather than assumed.

**Repeat runs.** Each hosted configuration and each local grounded arm was executed three times and scored by majority vote. The policy was adopted because one local model, llama3.2:3b, reproduced only 17 of 20 identical calls; the same model also departed from the output-format instruction, so the two defects recorded for local inference belong to a single model rather than to local inference as such. Repetition is not required everywhere: for qwen2.5:32b-instruct the within-arm agreement across the three grounded runs was 1.0000 in both R1 and R2 (three pairwise comparisons, 1,524 calls per run), which is exact reproduction, so for that model the vote changes no record and a single run would have sufficed. We therefore state the repeat requirement per model, on measured agreement, rather than as a blanket rule for grounded or local execution. Where a majority-voted cell has no majority on a claim — the three runs disagree without a plurality — the claim carries no label in that cell, and §3.7 states how such claims are handled.

**Two gates, and one quantity that is deliberately not a gate.**

1. *Response-rate gate (pre-registered, as corrected in EK-1 §1).* A model × condition cell whose parsable-response rate — any usable label, of any kind, divided by 473 — falls below 0.80 is reported as non-compliant in form and is not scored. The rate is recorded for every cell and is reported for all eighteen E1 / variant A cells in Table 2; no cell lacks the figure, and no cell is retained on the ground that the figure was unavailable. Two cells fall below the gate: llama3.2:3b-instruct-q4_K_M, response rate 0.674, and llama3.2:1b, response rate 0.545. Both write the claim text back instead of emitting a label, so the failure is one of output format rather than of knowledge. Their rows are marked *gate failed* in Table 2 and carry no accuracy figure.
2. *Commitment rate (coverage) is not a gate.* It is the dependent variable of this study. A model that abstains often is producing the measurement, not failing the protocol, and no cell is excluded, downgraded, or described as non-compliant on account of low coverage anywhere in this paper.
3. *Minimum-n reporting rule (EK-1 §2, post hoc).* Accuracy-type metrics — balanced accuracy, Youden's J, d′, ECE — are reported only for cells with at least 30 committed answers. Below that the count is given and the metric is left blank. The rule exists because a balanced accuracy computed on a handful of items is not interpretable, not because the underlying behaviour is uninteresting.

Applying rule 3 to the eighteen E1 / variant A cells, using the commitment count recorded for each cell, four cells fall below the threshold, all of them variants of the same 7B model: qwen2.5:7b-instruct-q4_K_M (6 committed answers), qwen2.5:7b-instruct-fp16 (24), qwen2.5:7b-instruct-q8_0 (18) and qwen2.5:7b-instruct-q5_K_M (16). Those four rows are **kept** in Table 2, because their coverage is itself a result and removing them would hide four of the eighteen systems, but their balanced accuracies and intervals are marked *not scored*, are printed in no comparison, and support no statement in Sections 4 and 5. The accounting is therefore: eighteen cells exist, two fail the response-rate gate, four fall under the minimum-n rule, and **twelve** carry a scored accuracy figure. Separately, ECE and Brier are suppressed in 8 of 56 cells that carry fewer than 50 confidence-bearing records.

One cell sits close to the boundary and is worth naming here rather than in the results. qwen2.5:32b-instruct answers every claim in a parsable form (response rate 1.000) while committing on 82 of them (coverage 0.173). It clears the response-rate gate outright and clears the minimum-n rule by 52 items, so it is scored. Describing it as falling below a pre-registered minimum-coverage threshold would be incorrect: EK-1 §1 removed coverage from the gate, and no such threshold exists in the protocol.

**Pre-registration, and one deviation from it.** The main pre-registration (`sonuclar/F4_on_kayit.txt`) was frozen before the runs. Its item 3 applied the 0.80 gate to whether a cell "answers" the claims, and that phrase covers two distinct quantities: whether the model emitted a parsable label at all, and whether that label was a commitment rather than an abstention. Addendum EK-1 (`sonuclar/F4_on_kayit_ek.txt`, 28 July 2026) re-defined the gate onto the first of the two. The addendum was written after the closed-book calls had completed — 18 models × 2 conditions × 473 claims = 17,028 calls — but before any accuracy metric had been computed; only response and abstention counts had been inspected at that point, and the addendum records that state. The reason for the change is a definition rather than an observation: applying an 0.80 floor to the commitment rate would classify the study's dependent variable as protocol non-compliance, so that a model producing fully parsable output while abstaining on 467 of 473 claims would be scored as non-compliant when it is in fact following the instruction exactly. The correct definition does not depend on what the data turned out to show. It is nonetheless a deviation from the frozen document, EK-1 itself states that it must be declared in the paper, and we declare it here. Both rules are reported: the corrected gate is primary, and the original gate is carried as a sensitivity arm. The minimum-n rule above is likewise post hoc, is a reporting convention only, and is used in no hypothesis test.

## 3.5 Grounded arms

Closed-book performance bounds an architecture rather than the task, so a grounded ladder was pre-registered (EK-4) against the closed-book arm R0. That ladder has now been executed.

| Arm | n | Evidence supplied | Role |
|---|---|---|---|
| R0 | 473 | none (closed-book) | baseline |
| R1 | 289 | full text of the cited article | upper reference point, not a deployable configuration: it presupposes that the citation in the claim has already been resolved correctly |
| R2 | 473 | BM25 top-k (k = 3) over the 1,755 refined units | retrieval plus judgement |
| R3-BM25 | 473 | the same retrieved passages, with no model: verdict from lexical match alone | retrieval-only control |

**Naming convention.** Two different objects in this study were recorded during the runs under the label "R3", and they are not the same control. Throughout this paper — Sections 3 to 7, all tables and all figures — they are named **R3-BM25** and **R3-rule**, and no other spelling of either is used.

- **R3-BM25** (run record `r3_bm25`) is the no-model control inside the grounded ladder: 473 decisions, no E1/E2 split, verdict from lexical containment over the three passages BM25 returned.
- **R3-rule** (run record `kural_taban_r3`) is a separate deterministic string-rule baseline, reported in Section 4.5. It performs no retrieval.

The distinction matters because their scores differ by a wide margin, and a reader who merges them will misread both.

**Execution.** The grounded ladder was run with a single model, qwen2.5:32b-instruct, on the refined corpus (corpus_v2, made primary by EK-6; EK-4 §1 had named the 1,366-unit raw corpus) against the v7a gold labels, three runs plus majority vote, 128-token output budget, seed 42. No response was truncated in any run (0 of 1,524 per run), which satisfies the invalidation condition of EK-4 §10 that set a 1 % ceiling on truncation. R0 for the same model is its closed-book cell, so R0, R1, R2 and R3-BM25 differ in the evidence supplied and in nothing else.

R1 is restricted to 289 claims by the data, not by choice: the remaining 184 cite only a document, and document texts run from roughly 17k to 871k characters.

**Retrieval is reported separately from judgement**, as EK-4 §10 requires. BM25 at k = 3 places the cited unit in the retrieved set for 79 of the 289 article-level claims (recall 0.2734) and misses 210. That figure characterises one untuned lexical retriever at one value of k on this corpus. It is reported as a property of the retriever and **not** as a bound on the accuracy of an arm built on that retriever: the two contributions to a grounded verdict — evidence actually supplied by retrieval, and knowledge the model brings to a passage that does not contain the cited provision — are not separated by this design, and Section 4.6 reports an R2 balanced accuracy far above what the recall figure on its own would imply. Any reading in which the recall number caps the grounded arm is contradicted by the measurement.

**R3-rule is blind by construction.** `kural_taban.py` reads only two columns of the claim file, `id` and `iddia` (the claim text). It does not read `probe`, `kanun`, `madde`, `gold`, `uretim_sablonu`, `degisiklik_notu` or `kaynak_alinti`, and it asserts this at start-up; EK-4 §6 makes the assertion a condition of reporting the arm at all. In particular it does not read the generator's article mapping — the citation it acts on is resolved from the claim text, exactly as in the model arms. It has no abstention option, so it is excluded from the calibration comparisons, and its matching rules were fixed before the run. Its behaviour is corpus-dependent in an informative way: with the refined corpus and the audited gold labels it decides 473/473 claims correctly, while the raw corpus paired with the same labels gives 466/473, and the 7 claims that separate the two (1.48 % of the set) are exactly the 7 whose gold labels the expert audit had frozen. A shuffled-pairing negative control over five seeds returns 0.5349, 0.5349, 0.5159, 0.5370 and 0.5349 (mean 0.5315), establishing that the rule set is exploiting the pairing rather than a surface regularity.

Two of R3-rule's channels are reconstructed from the same annotations the claims were generated from, and both are labelled accordingly. Its amendment-history (P6) channel derives from the same regular expression applied to the same PDFs as the generator's, so the check is circular in the sense that it verifies channel presence rather than legal correctness. A sample of 20 P6 claims was therefore checked against official consolidated HTML text: 20 agreed, 0 disagreed, and our parser reproduced the official article counts exactly (3194: 49, 4708: 15, 6331: 39). The verification frame covers only 3194, 4708 and 6331; YDUY was outside it, so 43 P6 claims remain unverified against an independent source. The enactment-year (P3) channel is weaker still: it derives from a metadata field of the generator rather than from the corpus text, and the corpus offers no independent channel against which to check it. Per EK-4 §8, R3-rule's P3 results are reported separately and marked *metadata-derived*.

## 3.6 Gold-label quality assurance and expert audit

Five deterministic layers (source identity, accidental truth, sentence cleaning, rendering-artefact repair, design-leak audit) were applied first, each with a positive control that had to fire. Two specialists in civil engineering and occupational safety then audited the labels in two passes with gold, probe family, template and stratum hidden, and row order randomised per rater. The two raters worked from separate workbooks and each was required to enter a free-text rationale; rationale-text identity between raters was checked as an independence control.

| | First pass | Second pass |
|---|---|---|
| Question put to the rater | is the claim consistent with the quoted sentence? | is the claim true of the whole article, read in the source? |
| Sample | 150 items (158 codes with controls) | 60 items: 58 scored + 2 seeded controls |
| Strata | unflagged / consensus-flagged | N: all 33 items either rater called less than clean; T: 25 drawn from the 105 both called clean; K: 2 seeded known-bad controls |
| κ, verdict axis | 1.000, 95 % CI [1.000, 1.000] | **0.722** (p_o = 0.897, p_e = 0.628, n = 58) — analysed in §4.7 |
| κ, verdict excluding "not sure" | 1.000, 95 % CI [1.000, 1.000] | — |
| κ, item-quality axis | 0.860, 95 % CI [0.759, 0.961] | — |

The first-pass κ of 1.000 is a property of the instrument rather than evidence that the labels are sound: the workbook shows the rater the quoted sentence and the recorded article, which is the same evidence the label was derived from, so the pass re-derives the generator's reasoning instead of testing it against the legislation. Contextual defect counts from the first pass are zero in every probe family sampled (P1 0/22, P2 0/17, P3 0/15, P4 0/12, P5 0/16), but with these sample sizes the 95 % upper bounds run from 14.9 % to 24.3 %, so the pass bounds the rate loosely rather than establishing it. It bounds it more loosely still once the second pass is read, for the reason given below.

**Design of the second pass.** The second pass was built to reach the class the first cannot: a sentence that, lifted from its article, no longer says what the article says. Raters opened the source and read the whole article. Its sampling frame is the 138 non-control items of the first pass (33 N + 105 T); the N stratum was taken whole, the T stratum was sampled at 25 of 105, and 2 items with known gold errors were seeded as a positive control. Analysis was specified as follows.

1. *Two decision rules, declared in advance of interpretation.* An item counts as a contextual defect under the **lenient** rule if at least one rater's verdict differs from gold, and under the **strict** rule if both do. The two rules bracket the quantity from opposite sides and both are reported.
2. *Which rule is primary is decided by the seeded control, not by preference.* The rule that recovers the known-bad items is the primary measure; the other is reported as a bound. The control result is given in §4.7, and it selects the lenient rule. One consequence must be carried back to the paragraph above: the strict rule is the rule under which the first pass returned zero defects in every family, and the strict rule failed the seeded control here. The first-pass zeros are therefore a lower bound on the contextual defect rate, not an estimate of it, and are read that way throughout.
3. *Stratum weighting.* Rates are computed per stratum and combined with the design weights implied by the sampling: 33/33 for N and 105/25 for T. A frame estimate for the 138 first-pass items is reported, and separately a compound-weighted figure projecting to the whole claim set; the two are distinct quantities and are labelled as such.
4. *Zero-event strata.* Where a stratum records no events, a one-sided 95 % upper bound is reported. The form "0.0 % [0.0 %, 0.0 %]" is not used.
5. *Direction of disagreement.* Rater disagreements are cross-tabulated by direction and tested with a sign test, because a disagreement that runs one way is evidence of two rules being applied rather than of noise around one rule, and the two call for different remedies — the first cannot be closed by averaging.
6. *Predictive validity of the first-pass flag.* Whether the first-pass quality flag predicts contextual defects is tested by comparing the N and T defect rates with a Fisher exact test. The N/T contrast is a two-stage sampling artefact by construction, so it is reported as a single test with its p-value attached and no claim of validity is made on the strength of the point ratio alone.

The κ of 0.722 in the table is a substantial fall from the first pass, its disagreement structure is not symmetric, and the seeded control was not recovered under the strict rule. These outcomes are reported with their numbers in §4.7 and carried into the limitations of Section 6, because they qualify the gold-label quality claim that Sections 4 and 5 rest on. They are not averaged away here.

One further consequence must be stated plainly, because it bears on how the R3-rule result above may be read. The 7 gold corrections were proposed after a corpus observation — the clause-merging defect — and the same observation motivated the refined corpus; the expert step confirmed the mis-attribution on those items but did not generate the labels independently, and R3-rule failed on those same 7 items rather than identifying them from scratch. The agreement between corpus repair, gold repair and R3-rule therefore contains a circular component, and the three are not independent confirmations of each other.

## 3.7 Outcome measures: two of them, reported together

Abstention is the dependent variable of this study, and it can be summarised in two ways that answer different questions. Both are reported everywhere, because they do not agree in magnitude.

| Measure | Definition | Status | Question it answers |
|---|---|---|---|
| BAcc(E1) − BAcc(E2) | Difference in balanced accuracy between the abstention-permitted and forced conditions, over the full claim set | Confirmatory: named in the main pre-registration, items 1.2–1.3, and carrying the multiple-comparison correction declared there | How much does the score improve when the model is allowed to stay silent? |
| Δ = A_com − A_nc | A_com is E2 accuracy on the items the model committed to in E1; A_nc is E2 accuracy on the items it did **not** commit to in E1 | **Exploratory.** Introduced in addendum EK-1 §3, after the main pre-registration, under the heading "added analysis (exploratory, not in the pre-registration)". No multiple-comparison correction is applied to it, as that addendum specifies | Does the silence carry information — is the model worse on precisely the items it declined? |

The status column is not a formality. Δ is the measure closest to the study's central question, and it is nonetheless the one with the weaker evidential standing: it was written down after the main pre-registration was frozen, so it is reported descriptively, with intervals and without a hypothesis test, and it is never described in this paper as pre-registered. The confirmatory analyses of the main pre-registration are a separate set, and the two must not be read as one.

The first quantity mixes two effects, since removing low-accuracy items from the denominator raises the score even if the choice of items is arbitrary. Δ isolates the second effect: Δ > 0 means abstention is selective, Δ ≈ 0 means the model is merely reticent. Reporting only one of them would let an author choose the larger effect; we therefore give both, together with coverage, since a balanced accuracy obtained on a small fraction of the claim set is not the same object as one obtained on nearly all of it, and the two must be read side by side.

**The two arms of Δ, and its denominator.** The split between the arms is taken from the E1 record. The committed arm is the set of claims on which the model answered true or false in E1. The other arm is its complement within the 473 claims, and it is **not** the abstentions alone: it is every claim the model did not commit to in E1 — explicit abstentions together with claims carrying no usable E1 label, whether because the output was unparsable or, in a majority-voted configuration, because the three runs produced no majority. We write it A_nc, "not committed", rather than A_abs, because "abstained" would name only part of the set.

Both arms are then scored on E2, so the denominator of each is the number of claims in that arm **for which an E2 verdict exists**. A claim with no E2 verdict is scored in neither arm, and the two arms can therefore sum to fewer than 473. In Table 4 the row for claude-haiku-4.5 sums to 472 (335 committed, 137 not committed). Claim 211 accounts for the difference: it was committed under E1 (majority "false"), but its three E2 runs split three ways — false, true, and one response with no parsable label — so no E2 majority formed. Having no E2 verdict, it drops out of the committed arm and cannot enter the other one either; it is absent from Δ entirely rather than moved between arms. This is the only such case in the hosted arm: the claude-sonnet-5 row sums to 473 (291 committed, 182 not committed).

**Statistical treatment.** Uncertainty on any single configuration is a cluster bootstrap, clusters being (law, article) pairs, seed 42, gold v7a. Contrasts between two arms measured on the same claims — the E1-versus-E2 difference for one model, and the differences between grounded arms — are computed as **paired** cluster bootstraps over the same clusters, so that the interval is an interval on the difference rather than an overlap judgement between two separate intervals. Differences are reported with those intervals and not as bare point values.

Three interval levels appear in this paper and each is labelled wherever it is used.

- *Nominal 95 %*, 10,000 resamples for the closed-book cells and 4,000 for the grounded arms and the paired contrasts, describing one configuration or one difference on its own.
- *99.72 %*, from the main pre-registration item 1, which requires a Bonferroni correction over the number of models: 18 models at α = 0.05 gives a per-cell level of 0.00278. Computed with 4,000 resamples. This level governs the open-weight closed-book comparison of §4.2. The correction is taken over all 18 models that produced an E1 / variant A cell, which is the more conservative choice, since only 12 of those cells survive the gates of §3.4 and carry a scored accuracy figure.
- *97.5 %*, from EK-4 §4, which declares a confirmatory family of two contrasts and prescribes Bonferroni-2. Computed with 4,000 resamples. This level governs the confirmatory two-contrast family, and both the uncorrected 95 % and the Bonferroni-2 interval are printed for each member of it.

Both the corrected and the uncorrected intervals are reported for every confirmatory comparison, because they lead to different counts of configurations separated from the null and a reader is entitled to see which threshold produced which count. Δ, being exploratory, carries no correction and is reported with 95 % intervals only.

## 3.8 Comparison baselines for the replication run

Judging whether a model has changed requires a baseline, and two are available. They answer different questions and we report both.

| Baseline | Construction | Question |
|---|---|---|
| Cluster bootstrap CI | Resample claims (clusters) within one archived run | Would this result generalise to other claims about these laws? Items vary. |
| Across-run range | The spread of the three archived runs of the same configuration | Did the model change on *these* 473 claims? Items are fixed. |

For a version-drift question the across-run range is the appropriate reference, because the claim set is frozen and identical between the archived runs and the replication; the bootstrap interval deliberately varies the item sample and so answers a different question. We adopt the across-run range as primary for that comparison and state the reason, and we report the bootstrap interval alongside, since it is wider and a reader is entitled to see that the two baselines lead to different verdicts on the same replication.

## 3.9 Replication protocol and the limit of its provenance

The replication run held everything constant except date: same model family, same variant A prompt, same output budget as the archived A@32 runs, thinking disabled, temperature not sent (the hosted endpoint rejects it), 473 claims × 2 conditions.

We do not claim that nothing on our side changed. The archived runs were executed with `f4_api.py`; the replication used `f4_api_v2.py` (script hash 002df510703fb0a7; the earlier v2 run frontCA128_k1 carries 11a5d5a3b7b7af20). The archived runs carry **no script hash at all** — the hashing was added after them. The variant A prompts are byte-identical across the change (E1 8a8ef386b0b2b619, E2 64dedda000ce465e), but that identity was re-derived from the archived source code, not read from the archived run records. This is the boundary of the provenance chain and any drift interpretation inherits it.

## 3.10 What would count as acceptable

We did not pre-specify a threshold at which a model would be declared fit or unfit for building-inspection use, and we do not assert one after the fact. Setting such a threshold requires facts this study does not supply: the cost ratio between a missed non-conformity and a false alarm in a given inspection workflow, whether the model's output is the decision or an input to a human decision, and what coverage the workflow needs before the tool saves any time at all. What the design does provide is the raw material for such a threshold — accuracy, coverage and selectivity reported separately rather than folded into a single headline number — and Section 5 discusses which of these an inspection workflow would have to fix first.

---

# 4 Results

Every figure below is regenerated from a committed script output. Where a
quantity was not produced by that pipeline, it is not reported. Terms are
defined at first use, since the intended reader is an engineer rather than a
natural-language-processing specialist. Sections 4.1 to 4.5 report closed-book
runs, Section 4.6 the arms in which the regulatory text is supplied, and
Section 4.7 the expert audit of the gold labels themselves, including the
second pass promised in Section 3.6. Section 4.7 qualifies every figure that
precedes it, since all of them are scored against those labels.

## 4.1 The evaluated systems

The claim set is frozen at 473 items (223 labelled true, 250 false) drawn from
six Turkish regulatory documents, distributed over six probe families: 163
verbatim-attribution items (P1), 37 numeric-alteration (P2), 19 enactment-year
(P3), 13 fabricated-source (P4), 121 misattribution (P5) and 120
amendment-history (P6). Of these, 289 cite a specific article and 184 cite only
a document.

Each claim is put to each system under two conditions. Under **E1** the system
may answer "not sure" — this is **abstention**, declining to commit. Under **E2**
it must choose true or false. **Coverage** is the fraction of the 473 claims on
which a system commits instead of abstaining or emitting an unparsable output.
**Balanced accuracy** (BAcc) is the mean of accuracy on true claims and accuracy
on false claims, so 0.5 is the value of a coin flip regardless of the class mix.
Intervals are clustered **bootstrap** intervals (10,000 resamples, clusters =
statute + article): the claim set is resampled repeatedly to estimate how far a
figure would move had a different sample of claims been drawn. **Calibration**
is reported as expected calibration error (ECE), the average gap between stated
confidence and observed accuracy — the same idea as checking a pressure gauge
against a reference instrument: a gauge reading 95 should be right about 95
times in 100. λ is a bias-corrected index, defined
throughout this paper exactly as the scoring code computes it: λ = accuracy on
the direct-citation family P1 (163 claims, of which 156 are true) plus accuracy
on the cross-reference family P5 (121 claims, all false), minus one. P1 is
predominantly rather than uniformly true, and it is named that way here; an
earlier draft described it as an always-true family, which the label
distribution does not support. The index is zero for a system answering from a
fixed response preference, because a constant answer scores one family at the
cost of the other. The runs of Sections 4.1 to 4.5 are
**closed-book**: the system answers from what it already contains, with no
document text supplied, the equivalent of an examination taken with the code
book shut.

**Table 1. Hosted arm, majority vote, closed book.**

| system | condition | BAcc | 95% CI | coverage | λ | ECE |
|---|---|---|---|---|---|---|
| claude-sonnet-5 | E1 | 0.6920 | [0.633, 0.750] | 0.615 | 0.325 | 0.0373 |
| claude-sonnet-5 | E2 | 0.6242 | — | 1.000 | 0.294 | 0.0634 |
| claude-haiku-4.5 | E1 | 0.5298 | [0.489, 0.570] | 0.710 | −0.026 | 0.2263 |
| claude-haiku-4.5 | E2 | 0.5558 | — | 0.998 | 0.061 | 0.2070 |

The uncorrected 95% interval for the smaller hosted model contains 0.5; the
uncorrected interval for the larger one does not. The multiple-comparison
correction fixed in the main pre-registration is applied in Section 4.2 over the
open-weight family, where the comparison is one model against the 0.5 line;
corrected intervals of that form were not computed for these two hosted
configurations [figure not in the frozen number set], so Table 1 should be read
as uncorrected. The separate correction that does apply to the hosted arm is the
one governing the confirmatory E1-versus-E2 contrast, and it is reported in
Section 4.3. The calibration figures differ by roughly a factor of six between
the two systems. The calibration estimator was checked against a positive
control: applied to the deterministic rule baseline of Section 4.5 it returns
0.0000, where the earlier mid-point formula returned 0.0500. In 8 of 56 cells
fewer than 50 committed answers carried a confidence value, and ECE is
suppressed for those cells rather than reported.

## 4.2 The coverage–accuracy trade-off

Eighteen open-weight models have a complete E1 cell under prompt variant A. The
two rules declared in Section 3.4 are applied to Table 2 rather than merely
stated, and they are applied in the order in which they are defined.

First, the **response-rate gate** (pre-registered, as corrected in EK-1 §1). A
cell whose parsable-response rate — any usable label, of any kind, divided by
473 — falls below 0.80 is non-compliant in form and is not scored. The per-model
response rates are part of the frozen number set and are printed in Table 2. Two
cells fail: llama3.2:3b-instruct-q4_K_M, which returned no parsable label on 154
of 473 items (response rate 0.674), and llama3.2:1b, which failed on 215
(response rate 0.545). Both write the claim text back instead of emitting a
label, so the failure is one of output format rather than of judgement. Their
balanced accuracies are withheld and enter no comparison. Of the remaining
sixteen cells, eleven returned a parsable label on every item and five on
between 0.886 and 0.998 of them.

Second, the **minimum-n reporting rule** (EK-1 §2, post hoc). Accuracy-type
metrics are reported only where the model committed to at least 30 claims; the
committed count is coverage × 473. Four cells fall below that floor — 6, 24, 18
and 16 committed answers, all four qwen2.5:7b variants — and are printed as
*not scored* rather than removed, so that the reader can see that the
configurations were run and why they carry no number.

The arithmetic of the two rules is therefore 18 = 12 + 2 + 4: **twelve cells
carry a scored accuracy figure**, two are excluded by the response-rate gate,
and four fall under the minimum-n rule. Commitment rate itself is not a gate at
any point; it is the dependent variable of this study, and no cell is excluded
or described as non-compliant on account of low coverage.

**Table 2. Open-weight models, E1 / variant A.** Response rate is the share of
the 473 items returning a parsable label of any kind; committed *n* is
coverage × 473. The gate outcome column records which of the two rules of
Section 3.4 the cell meets. The interval is the **uncorrected** 95% interval;
the pre-registered correction is applied in Table 2b.

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

**Table 2b. The four uncorrected candidates, before and after the
pre-registered correction.**

| model | BAcc | 95% lower | Bonferroni (99.72%) lower | coverage | excludes 0.5 after correction |
|---|---|---|---|---|---|
| qwen2.5:32b-instruct | 0.6769 | 0.5820 | 0.5349 | 0.173 | **yes** |
| gemma3:27b | 0.5674 | 0.5235 | 0.5017 | 0.970 | **yes, by 0.0017** |
| llama3.2:3b-instruct-q8_0 | 0.5509 | 0.5077 | 0.4878 | 0.884 | no |
| gemma3:12b | 0.5493 | 0.5136 | 0.4915 | 0.987 | no |

The lower bounds in Table 2b come from a separate bootstrap of 4,000 resamples
(same clustering, seed 42) run for the correction, which is why its 95% lower
bounds differ from Table 2 in the third decimal — 0.5820 against 0.5833 for the
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

## 4.3 What abstention buys: two measures

Abstention was priced two ways, and the two have different evidential status.
The first is the difference BAcc(E1) − BAcc(E2): what permitting "not sure" adds
to committed accuracy. This is the confirmatory measure of the main
pre-registration (§1.2–1.3). The second is Δ = A_com − A_nc, where A_com is E2
accuracy on the items the system committed to under E1 and A_nc is E2 accuracy
on the items it did **not** commit to under E1. The notation follows §3.7 and is
used in that form everywhere in this paper: the second set is the complement of
the committed set within the claim set, so it holds explicit abstentions
together with any output from which no label could be parsed, and writing it
A_abs would name only part of it. It is not the explicit abstentions alone, and describing it that way
would understate what the measure conditions on. Δ > 0 means non-commitment
carried information about which items the system would get wrong.

### 4.3.1 The confirmatory contrast, with the correction it carries

**Which correction family this contrast belongs to.** This study carries two
distinct confirmatory families and they must not be merged. The contrast
BAcc(E1) − BAcc(E2) is item 1.2 of the main pre-registration, whose stated
correction is "Bonferroni over the number of models"; seventeen configurations
have both an E1 and an E2 scored cell, so the per-comparison level is
0.05/17 = 0.00294 and the corresponding interval is a 99.71% interval. The
family of two, at 97.5%, belongs to annex EK-4 §4 and covers the grounded-arm
hypotheses H1 and H2 of Section 4.6.3, not this contrast. An earlier draft of
this paper applied the family of two here, which understates the correction;
the figures below use the family of seventeen and the conclusion changes in
strength though not in sign.

**Table 3. Confirmatory contrast BAcc(E1) − BAcc(E2), hosted arm.** Paired
cluster bootstrap, 4,000 resamples, clusters = law + article, seed 42, v7a gold.
Correction: Bonferroni over 17 models (main pre-registration §1.2).

| system | BAcc(E1) − BAcc(E2) | 95% CI | Bonferroni-17 (99.71%) CI | excludes 0 after correction |
|---|---|---|---|---|
| claude-sonnet-5 | +0.0678 | [+0.0243, +0.1106] | [+0.0018, +0.1343] | **yes, narrowly** |
| claude-haiku-4.5 | −0.0260 | [−0.0612, +0.0130] | [−0.0765, +0.0347] | no |

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

### 4.3.2 The exploratory selectivity measure

Δ is an **exploratory measure, added in Annex EK-1 §3 after the main
pre-registration**; the addendum labels it exploratory in those terms and states
that no multiple-comparison correction is applied to it. It is not part of the
confirmatory analysis and is reported as a descriptive quantity.

**Table 4. Δ (exploratory measure, EK-1 §3).** Intervals are paired cluster
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

## 4.4 Change over time

The same configuration (claude-sonnet-5, variant A, 32-token response budget; a
token is a sub-word unit of model output) was re-run on the frozen claim set
after the archived runs, under a decision rule fixed before the run (Annex EK-7).

**The decision rule, stated.** EK-7 was written and committed before any API
call of this run was issued, and it fixed three outcomes in advance against the
archived A@32 balanced-accuracy range [0.6796, 0.6986]: a value inside that
range would be read as a **budget effect**, meaning today's model behaves as the
archived one did at the archived budget; a value at or below **0.66** would be
read as **version drift**; and a value between 0.66 and 0.6796 would be declared
**indeterminate**, reported as such, with a further run recommended and not
required. The 0.66 threshold is approximately the midpoint between the archived
lower bound and the earlier A@128 result of 0.6395. It is a stipulated
threshold, not an externally justified one, and EK-7 says so in those terms; it
was not altered after the run. The comparison is made at equal granularity —
one run against one run — and EK-7 forbids comparing this single run against a
majority-voted configuration. The observed value is 0.6422, which is at or below
0.66, so branch (b) applies and the outcome is **version drift**.

| | E1 | E2 |
|---|---|---|
| archive A@32, three runs | [0.6796, 0.6986] | [0.6012, 0.6220] |
| A@32 today | 0.6422 (outside) | 0.6090 (inside) |
| BAcc(E1) − BAcc(E2), archive | 0.0735 · 0.0784 · 0.0767, mean 0.0762 | |
| BAcc(E1) − BAcc(E2), today | 0.0332 | |
| abstentions, archive | 181 · 184 · 182 | |
| abstentions, today | 178 | |

Under forced choice the current run sits inside the archive range. The
divergence appears only where abstention is permitted.

The two abstention measures agree in direction and disagree in size, and both
are reported. The confirmatory contrast BAcc(E1) − BAcc(E2) falls from a mean of
0.0762 to 0.0332, a 56% relative drop and 44% of the archive mean, outside the
archive range [0.0735, 0.0784]. The exploratory Δ falls from an archive mean of
0.1416 to 0.1014, a 28% relative drop, below the archive range of point
estimates [0.1174, 0.1791]. "Halved" is accurate for the confirmatory measure
only.

That second comparison, however, is between point estimates, and it does not
survive being given intervals. Today's Δ is 0.1014 with a 95% paired interval of
[+0.0212, +0.1833], and the three archived runs give [+0.0344, +0.1974],
[+0.0385, +0.2147] and [+0.0914, +0.2638]. Today's interval overlaps all three
substantially. **On the Δ axis, today's run and the archived runs are not
distinguishable**, and any statement that Δ fell outside the archive range must
be qualified accordingly: it is outside the range of the point estimates and
inside the uncertainty of every one of them. The version-drift finding of this
section therefore rests on the confirmatory contrast BAcc(E1) − BAcc(E2), which
falls outside the archive range on a measure whose archive spread is narrow
([0.0735, 0.0784]). Δ points the same way and adds no discrimination of its own.
What Δ does still establish is that abstention on today's run remains
informative in absolute terms: its interval excludes zero.

The number of abstentions moved little: 181/184/182 in the archive against 178
today, a 2.2% relative drop from the archive mean and just outside the archive
range. Frequency was roughly preserved while the difference the abstentions made
declined — the change is in which items were declined, not how many.

**Why the run range is the comparison base.** Two baselines are available and
they answer different questions. The clustered bootstrap interval for the
archive E1 runs is [0.633, 0.750], and today's 0.6422 falls inside it; that
interval treats the claims as a sample and asks whether a result would
generalise to other claims. The run-to-run range [0.6796, 0.6986] holds the 473
items fixed and asks whether the system changed on this set. Because the claim
set is frozen and identical across all runs compared here, the run range is the
appropriate base for the version question, and it excludes today's value. We
report the bootstrap interval as well, and note that a reader interested in
generalisation to other claims should use it and would not find the change
established.

**Provenance limits.** The comparison is between runs produced by different
harness code: the archived runs used `f4_api.py`, today's used the regenerated
`f4_api_v2.py` (script hash 002df510703fb0a7; the original v2 run carries
11a5d5a3b7b7af20). The variant A prompts are byte-identical before and after the
patch (E1 8a8ef386b0b2b619, E2 64dedda000ce465e), but that identity was
re-derived from the archived source code, because the archived runs record no
script or prompt hash at all. Prompt wording is measurable as a factor: within
the A@32 arm, run-to-run agreement is [0.9017, 0.9133], within B@128 it is
[0.9165, 0.9228], while agreement between A@128 and B@128 is [0.8266, 0.8319]
(mean 0.8302), below both within-arm bands; B@128 E1 balanced accuracy is
0.6992 · 0.7027 · 0.7172. Wording therefore moves outputs more than run-to-run
noise does, which is why the prompt identity above matters. Finally, "version
drift" here refers to what the provider served behind the model name changing
over time; the served version could not be read from the API, and today's figure
rests on a single run whose own within-arm band was not measured.

## 4.5 The rule-based baseline (R3-rule)

**R3-rule** is a deterministic string-matching baseline with no language model:
it reads the claim identifier and the claim text only, asserts that restriction
at start-up, and resolves each claim against the corpus by literal matching. It
performs no retrieval, and it is a different object from R3-BM25 of
Section 4.6, which decides over three retrieved passages; the two share a letter
in the run labels and not a method. Against the raw corpus R3-rule scored
473/473 with the earlier gold labels (v6) and 466/473 with the revised gold
labels (v7a); against the refined corpus (corpus_v2) it scored 473/473 with
v7a. The refinement splits fused units, raising the corpus from 1,366 to 1,755
units (TBDY 1,208 → 1,523; remaining articles 158 → 232, which recovers 16
annex and 58 provisional provisions).

The 7 items in the gap (1.48% of the set) are claims 246, 257, 304, 360, 364,
382 and 393 — the same seven the experts returned during gold revision. This
should not be read as independent corroboration. R3-rule did not produce the
expert judgement; it failed on those seven items, that is, it flagged the same
seven, and the gold correction itself rested on the same corpus observation
about fused parsing. The agreement is therefore circular and is reported as a
consistency check on the parser, not as validation of the labels.

A negative control bounds what the matching rule can achieve on its own. With
the claim-to-unit mapping shuffled across five seeds, accuracy is 0.5349,
0.5349, 0.5159, 0.5370 and 0.5349 (mean 0.5315), near chance: the baseline's
ceiling comes from the mapping, not from the matching rule.

Twenty P6 claims were checked against the official HTML text at mevzuat.gov.tr:
20 matched, 0 did not, and our parser reproduced the official article counts
exactly (3194: 49, 4708: 15, 6331: 39). The check is restricted to those three
statutes; YDUY lies outside its frame, leaving 43 P6 claims not independently
verified.

## 4.6 Grounded arms: supplying the text

Sections 4.1 to 4.5 measure closed-book behaviour, which bounds an architecture
and not the task. This section reports the arms in which the regulatory text is
placed in front of the model. All figures here are from one model,
qwen2.5:32b-instruct, over the refined corpus (corpus_v2, 1,755 units) with the
audited gold labels (v7a), at a 128-token output budget, three runs scored by
majority vote. No response was truncated: 0 of 1,524 calls in each run.

### 4.6.1 The retriever on its own

BM25 is a standard lexical ranking function that scores passages by weighted
word overlap with the query. Over corpus_v2 with the top three passages
retrieved per claim, it placed the cited unit among the retrieved passages for
79 of the 289 article-attributing claims, a recall of 0.2734; 210 were missed.
This bounds the configuration measured, not retrieval in general: one lexical
retriever, untuned, at a single value of k, against a corpus in which many units
share near-identical legal phrasing.

### 4.6.2 End-to-end results

Four arms are compared on the same claim set. R0 is the closed-book baseline.
R1 supplies the full text of the article the claim cites — a ceiling, not a
deployable configuration, and restricted to the 289 article-attributing claims
because the remaining 184 cite only a document. R2 supplies the BM25 top-3
passages. **R3-BM25** supplies nothing to a model at all: it takes the **same
three retrieved passages** and decides by literal string containment, no model
involved. It is the ablation that isolates what the model contributes to the
retrieved evidence, and it is distinct from R3-rule of Section 4.5, which
matches against the whole corpus rather than the retrieved passages.

**Table 5. Grounded arms, qwen2.5:32b-instruct, corpus_v2 + v7a, majority of
three runs.** Intervals are clustered bootstrap (4,000 resamples, clusters =
law + article, seed 42).

| arm | evidence supplied | condition | n | coverage | BAcc | 95% CI | accuracy | λ |
|---|---|---|---|---|---|---|---|---|
| R0 | none (closed book) | E1 | 473 | 0.173 | 0.6769 | [0.5833, 0.7618] | — | — |
| R0 | none (closed book) | E2 | 473 | 1.000 | 0.5493 | — | — | — |
| R1 | cited article, full text | E1 | 289 | 0.830 | 0.9164 | [0.8804, 0.9494] | 0.9208 | 0.987 |
| R1 | cited article, full text | E2 | 289 | 1.000 | 0.8615 | [0.8207, 0.8987] | 0.8720 | 0.988 |
| R2 | BM25 top-3 | E1 | 473 | 0.899 | 0.8229 | [0.7866, 0.8579] | 0.8235 | 0.804 |
| R2 | BM25 top-3 | E2 | 473 | 1.000 | 0.8100 | [0.7763, 0.8415] | 0.8161 | 0.829 |
| R3-BM25 | BM25 top-3, no model | — | 473 | 1.000 | 0.5938 | [0.5598, 0.6261] | 0.5877 | −0.043 |

The R0 / E1 interval is the closed-book interval of Table 2, repeated here for
comparison; no interval was produced for the R0 / E2 cell
[figure not in the frozen number set].

**The model adds about 22 points to the same retrieved passages.** R2 minus
R3-BM25 is +0.2292 under E1 with a paired 95% interval of [+0.1939, +0.2635],
and +0.2162 under E2 with [+0.1818, +0.2493]. The intervals are paired — the
same clusters are resampled for both arms, since both arms decide the same
claims from the same retrieved passages — and both exclude zero. Both arms see
identical evidence, so the difference is attributable to the judgement step
rather than to what was retrieved. This contrast is listed in EK-4 §4 as a
secondary, exploratory comparison; the pre-registered primary family for the
grounded arms is H1 and H2, reported in Section 4.6.3.

**Perfect citation is worth about 5 to 9 points over BM25.** R1 minus R2 is
+0.0935 under E1 and +0.0515 under E2: the cost of replacing an oracle pointer
to the cited article with an untuned lexical retriever. These two differences
are point differences between arms scored on different item sets — R1 on the 289
article-attributing claims, R2 on all 473 — so no paired interval is available
for them and they are stated as indicative. R1 is a ceiling and not an operating
point, since a deployed system does not know in advance which article a claim
ought to be checked against.

**The same model moves from 0.6769 at coverage 0.173 to 0.8229 at coverage
0.899 when the text is supplied.** The closed-book and grounded figures come
from one model on one claim set, so the comparison is within-system: the
closed-book arm commits to 82 of 473 items, the BM25-grounded arm to 425, and it
is more accurate on the larger set than the closed-book arm was on the smaller
one. Under forced choice the same contrast is 0.5493 against 0.8100.

### 4.6.3 The pre-registered primary hypotheses

Annex EK-4 §4 names two comparisons as the primary confirmatory family for the
grounded arms, and applies a Bonferroni correction over two, that is a 97.5%
interval. **H1 is R2 − R0**: does supplying three retrieved passages improve on
closed book? **H2 is R1 − R0**: does supplying the cited article improve on
closed book? Both were fixed before the grounded runs were executed. They are
reported here for the first time; earlier drafts of this paper reported only the
secondary contrast of Section 4.6.2, which is an omission of the pre-registered
analysis rather than a difference of emphasis.

Both hypotheses are evaluated as paired cluster bootstraps on the item set each
is defined over. H1 is computed on all 473 claims. H2 is computed on the 289
article-attributing claims, because R1 exists only there; the R0 baseline for H2
is therefore R0 restricted to those same 289 items and re-scored on them, which
is not the same number as R0 on the full set. R0 scores 0.6226 under E1 and
0.5062 under E2 on the 289-item subset, against 0.6769 and 0.5493 on all 473.
Reporting H2 against the full-set R0 figure would compare across different item
sets and is not done.

**Table 6. Pre-registered primary family for the grounded arms (EK-4 §4),
qwen2.5:32b-instruct.** Paired cluster bootstrap, 4,000 resamples, clusters =
law + article, seed 42, v7a gold; Bonferroni-2 intervals are 97.5% intervals.

| hypothesis | condition | contrast | n | difference | 95% CI | Bonferroni-2 CI | excludes 0 |
|---|---|---|---|---|---|---|---|
| H1 | E1 | R2 − R0 | 473 | 0.8229 − 0.6769 = **+0.1460** | [+0.0503, +0.2455] | [+0.0367, +0.2575] | **yes** |
| H1 | E2 | R2 − R0 | 473 | 0.8100 − 0.5493 = **+0.2607** | [+0.2218, +0.2964] | [+0.2170, +0.3014] | **yes** |
| H2 | E1 | R1 − R0 | 289 | 0.9164 − 0.6226 = **+0.2938** | [+0.1361, +0.4479] | [+0.1118, +0.4717] | **yes** |
| H2 | E2 | R1 − R0 | 289 | 0.8615 − 0.5062 = **+0.3552** | [+0.3112, +0.3984] | [+0.3051, +0.4036] | **yes** |

All four corrected intervals exclude zero. The pre-registered conclusion is
therefore supported in both conditions and for both kinds of supplied evidence:
on this claim set, giving the model regulation text raises balanced accuracy by
an amount that does not plausibly arise from resampling the claims, and the
oracle-citation arm raises it further than the retrieved-passage arm does.

Two cautions attach to the size of these differences rather than to their sign.
First, the E1 intervals are much wider than the E2 intervals — [+0.0503,
+0.2455] against [+0.2218, +0.2964] for H1 — because R0 under E1 commits to only
82 of 473 items, so its balanced accuracy is estimated on a small and
self-selected subset. The E2 comparison, where both arms answer everything, is
the better-conditioned one. Second, H1 and H2 compare a grounded arm against a
closed-book arm, which differ in what evidence is supplied *and* in nothing
else; the isolation of the model's judgement step from the evidence itself is
the separate question that Section 4.6.2 addresses.

### 4.6.4 What the retrieval figure does and does not bound

R2's balanced accuracy of 0.8229 [0.7866, 0.8579] was obtained while the
retriever placed the cited unit in the context for only 0.2734 of the
article-attributing claims. The retrieval recall is therefore **not** a ceiling
on the grounded arm's accuracy, and an earlier statement in this work that a
grounded arm inherits the retriever's ceiling is withdrawn: it was a prediction,
and the measurement contradicts it. At least two mechanisms could produce the
observed result — the retrieved passages are often sufficient to judge a claim
even when they are not the cited unit, or the model completes the judgement from
parametric knowledge — and this experiment does not separate them. Attributing
R2's accuracy to retrieval alone would be unsupported. Whether a tuned
retriever, a larger k, or a dense or hybrid retriever changes the picture was
not measured.

**Run-to-run behaviour.** Three runs were executed per arm as a precaution, and
they were not needed for this model: within-arm agreement is 1.0000 for both R1
and R2 (three pairwise comparisons, 1,524 calls per run), that is, fully
deterministic output. An earlier observation of non-determinism under grounded
prompting (defect log #29, 17/20 agreement) belongs to llama3.2:3b, which is
also the model that dropped the output-format instruction (defect log #28). Both
findings are properties of that one model, not of grounded prompting, and the
claim that local grounded arms require three runs is narrowed accordingly: for
qwen2.5:32b-instruct a single run reproduces the result exactly, as measured.

### 4.6.5 Sensitivity to the corpus choice

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

**Table 7. Corpus sensitivity (EK-6 §3), qwen2.5:32b-instruct, v7a gold.**
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

**No arm shows a corpus effect that excludes zero.** Every point estimate favours
the refined corpus, by between 0.007 and 0.019 in balanced accuracy, and every
paired interval contains zero. The R1 / E2 interval is the one to look at
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

## 4.7 The expert audit of the gold labels: both passes

Every figure above is scored against the v7a gold labels, so the labels
themselves are a measured object and not an assumption. Two specialists in civil
engineering and occupational safety audited them in two passes, with gold, probe
family, template and stratum hidden and row order randomised per rater. The two
passes ask different questions, and — this is the result of this section — they
do not give the same answer.

### 4.7.1 First pass: consistency with the quoted sentence

The first pass put one question: is the claim consistent with the sentence
quoted in the record? On 150 items (158 codes including controls), agreement was
exact on the verdict axis, Cohen's κ = 1.000, 95% CI [1.000, 1.000], and
unchanged when "not sure" responses were excluded. On the item-quality axis
κ = 0.860, 95% CI [0.759, 0.961]. Contextual defect counts were zero in every
probe family sampled: P1 0/22, P2 0/17, P3 0/15, P4 0/12, P5 0/16.

Neither figure should be read as evidence that the labels are sound. A κ of
1.000 is a property of the instrument: the workbook shows the rater the quoted
sentence and the recorded article, which is the same evidence the label was
derived from, so the pass re-derives the generator's reasoning rather than
testing it against the legislation. And the zero defect counts bound the rate
only loosely — at these sample sizes the 95% upper bounds run from 14.9% to
24.3%, so "zero observed" is consistent with a defect rate approaching one item
in five within a family.

### 4.7.2 Second pass: reading the whole article

The second pass was designed to reach the class the first cannot — a sentence
that, lifted from its article, no longer says what the article says. Raters
opened the source and read the whole article. Sixty items were drawn from a
frame of 138 first-pass items in three strata: all 33 items that at least one
rater had not called clean (stratum N), 25 of the 105 both raters had called
clean (stratum T), and 2 seeded items with known-bad gold labels as a positive
control (stratum K).

**Agreement fell.** On the 58 non-control items, Cohen's κ = 0.722
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

### 4.7.3 What this does and does not license

The audit establishes that the gold labels are internally consistent on the
evidence the first pass shows a rater, and that a contextual error rate of
roughly 7% over the audited frame — with an interval running to about 12%, and
a composite projection of 8.8% over the whole set — cannot be excluded. It does
not establish a label quality figure that the accuracy differences reported
above can be compared against, because the two raters were not applying the same
rule in the second pass and the disagreement between them is systematic. The
differences that carry the paper's conclusions are large relative to that rate
— the R2-minus-R3-BM25 gap is 0.2292 [0.1939, 0.2635] — and the differences that
are small relative to it, in particular gemma3:27b clearing chance by 0.0017
after correction, should be read as sensitive to it. This limitation is carried
into Section 6 rather than resolved here.

One consequence must be stated plainly, because it bears on Section 4.5. The 7
gold corrections were proposed after a corpus observation — the clause-merging
defect — and the same observation motivated the refined corpus; the expert step
confirmed the mis-attribution on those items but did not generate the labels
independently, and R3-rule failed on those same 7 items rather than identifying
them from scratch. Corpus repair, gold repair and the R3-rule result are three
views of one observation, not three independent confirmations.

---

# 5 Discussion

## 5.1 The open-weight arm is a coverage–accuracy trade-off, not a uniform failure

Eighteen locally hosted configurations produced an E1 cell under prompt variant A. The gates of §3.4 leave twelve of them carrying a scored accuracy figure. Two cells fail the response-rate gate — `llama3.2:3b-instruct-q4_K_M` at a parsable-response rate of 0.674 and `llama3.2:1b` at 0.545, both because they write the claim text back instead of emitting a label — and four commit to fewer than 30 claims and are therefore reported without an accuracy figure under the minimum-n rule of EK-1 §2: the four `qwen2.5:7b-instruct` quantisations, at 6, 24, 18 and 16 committed answers. Those four cells appear in Table 2 because their coverage is itself a result, and no statement in Sections 4 to 7 rests on their scores. The pre-registered Bonferroni correction is nonetheless taken over all eighteen cells rather than over the twelve scored ones, which is the conservative direction.

How many of the twelve scored cells can be separated from chance depends on whether that correction is applied, and we report both counts because the difference is material.

Read one cell at a time with an uncorrected 95% cluster-bootstrap interval, four models lie entirely above 0.5: `qwen2.5:32b-instruct` at 0.6769 [0.5833, 0.7618] with coverage 0.173, `gemma3:27b` at 0.5674 [0.5230, 0.6115] with coverage 0.970, `llama3.2:3b-instruct-q8_0` at 0.5509 [0.5073, 0.5963] with coverage 0.884, and `gemma3:12b` at 0.5493 [0.5139, 0.5836] with coverage 0.987. But the main pre-registration (§1) fixes Bonferroni correction over the number of models, and eighteen models at α = 0.05 give 0.00278 per cell, that is a 99.72% interval. Under that correction two models remain: `qwen2.5:32b-instruct`, lower bound 0.5349, and `gemma3:27b`, lower bound 0.5017 (4,000 resamples, clusters = law + article, seed 42). `llama3.2:3b-instruct-q8_0` (0.4878) and `gemma3:12b` (0.4915) no longer exclude chance. The second surviving model clears 0.5 by 0.0017 of balanced accuracy, which is a margin no engineering decision should rest on; we report it as surviving the stated test, not as a demonstrated capability.

The two survivors sit at opposite operating points. `qwen2.5:32b-instruct` reaches an interval that overlaps the hosted `claude-sonnet-5` value of 0.6920 [0.633, 0.750], but it commits on 0.173 of the claims — 82 of 473 — declining roughly five items in six, and its accuracy is measured only on the sixth. That cell is scored rather than withheld: the reporting rule adopted in the pre-registration addendum (EK-1 §2) requires at least 30 committed items, and 82 is above it. The 80% gate in the pre-registration applies to the parsable-response rate, not to the commitment rate, and commitment rate is the dependent variable of this study, so a low-coverage cell is a result and not a protocol violation. `gemma3:27b`, by contrast, answers 0.970 of the claims — 459 of 473 — and sits about seven points above chance on nearly the whole set.

The engineering reading is a trade-off between how much of the workload a system will take on and how well it does on that share. It is not an absence of signal, and it is not a demonstration of usable performance either. The correction matters for the same reason the minimum-n rule does: eighteen cells were examined, so the largest uncorrected value in the table is also the value most exposed to sampling, and a balanced accuracy computed over a small committed set is not a capability claim. Those two rules are what separate the twelve scored cells from the six that carry no comparison in this paper.

## 5.2 Abstention frequency held; abstention selectivity fell

Comparing the three archived hosted runs (variant A, 32-token budget) with the run repeated on 28.08.2026 under the same settings, the number of abstentions is close to unchanged: 181, 184 and 182 in the archive against 178 today, a relative decrease of 2.2%. What changed is what those abstentions were worth, and the two available measures of that disagree in size.

The condition contrast BAcc(E1) − BAcc(E2) — how much the option to say "not sure" buys in balanced accuracy — is a confirmatory measure of the main pre-registration, and it falls from an archive mean of 0.0762 (range [0.0735, 0.0784]) to 0.0332, a relative drop of 56%. The selectivity measure Δ = A_com − A_nc, where A_com is E2 accuracy on the items the model committed to under E1 and A_nc is E2 accuracy on the items it did **not** commit to under E1 — abstentions together with unparsable outputs — asks whether the items a model declined are ones it would have got wrong anyway. Its point estimate falls from an archive mean of 0.1416 to 0.1014, a relative drop of 28%, but its intervals overlap the archived intervals throughout (Section 4.4), so Δ agrees in direction and discriminates nothing. The claim of this section rests on the confirmatory contrast alone.

**The confirmatory contrast across the two hosted models, corrected.** The abstention question was pre-registered as a family of two contrasts (EK-4 §4), one per hosted model, so a Bonferroni-2 correction applies and the corrected intervals are at the 97.5% level (paired cluster bootstrap, 4,000 resamples, clusters = law + article, seed 42, v7a gold). For `claude-sonnet-5` the contrast is +0.0678, 95% [+0.0243, +0.1106], Bonferroni-2 [+0.0190, +0.1170]: the corrected interval excludes zero, so permitting abstention raises balanced accuracy for that model by an amount that survives the correction. For `claude-haiku-4.5` the contrast is −0.0260, 95% [−0.0612, +0.0130], Bonferroni-2 [−0.0659, +0.0183]: the interval spans zero in both directions and the point estimate is negative, so abstention has no measurable benefit for that model on this claim set. The abstention mechanism is therefore model-specific rather than a property of the prompt or of the task, which is the same conclusion the Δ figures reach from the other side (0.1557 against 0.0416, §4.3).

**Status of Δ.** Δ is an *exploratory* measure, added in the pre-registration addendum (EK-1 §3) after the main pre-registration and after the run had completed, though before any accuracy metric was computed. The addendum marks it exploratory and applies no multiple-comparison correction to it, and we follow that. It is not one of the confirmatory analyses of the main pre-registration, and it should not be read as a pre-specified test. We report it because it isolates a quantity the confirmatory contrast cannot — whether the items not committed to are the ones the model would have failed — and because reporting only the confirmatory contrast would leave that question unanswered.

Both measures are positive today and both moved in the same direction; the description "halved" applies only to the first. The archive Δ range is wide, [0.1174, 0.1791], with the third run at 0.1791, so the width of the reference band limits how firmly the size of the decrease can be stated. We report both because reporting only the larger one would overstate the effect.

For a building-inspection workflow this pattern matters more than either number alone. A tool whose abstention rate is stable but whose abstentions have become less informative looks unchanged on a dashboard that monitors abstention rate. The "send this one to a human" signal remains visually intact while carrying less of the meaning it was accepted for. An operator monitoring only the abstention count would not see this change; an operator recomputing Δ against a retained gold subset would.

## 5.3 Re-qualification: a fixed test set, a changed component

One result bears directly on procurement and maintenance practice: a system qualified once against a frozen test set may not stay qualified. The same 473 claims, the same gold labels, the same variant A prompt, the same 32-token budget and the same hosted model name yield archive balanced accuracies of 0.6832, 0.6796 and 0.6986 — a run-to-run range of [0.6796, 0.6986] — against 0.6422 today, outside that range. Under the forced-choice condition the archive range is [0.6012, 0.6220] and today's value 0.6090 falls inside it. The movement is concentrated in the condition where the model is allowed to abstain, which is consistent with §5.2.

**Choice of comparison baseline.** Two baselines are available and they answer different questions. The cluster bootstrap over claims, [0.633, 0.750], asks whether a measured value would generalise to other claims drawn from a comparable population; the claim set is treated as variable, and today's 0.6422 falls inside it. The run-to-run range, [0.6796, 0.6986], asks whether behaviour changed on *this* set of 473 items; the claim set is held fixed. The version question fixes the item set by construction, so the run-to-run range is the matching baseline. We nonetheless report the bootstrap interval, because a reader who prefers the generalisation framing should be able to read the result in those terms: behaviour on the frozen set moved beyond previously observed run-to-run variation, while remaining inside the interval one would expect across resamples of comparable claim sets.

**What we can and cannot say about our own side.** The archived runs were produced with `f4_api.py`; the repeated run was produced with the regenerated `f4_api_v2.py`. The variant A prompt strings are byte-identical across the two (E1 `8a8ef386b0b2b619`, E2 `64dedda000ce465e`), but that identity was re-derived from the archived source code: the archived run records carry no script hash at all. The two v2 runs do carry hashes (`11a5d5a3b7b7af20` for the 128-token run, `002df510703fb0a7` for today's), and they differ, because the file was regenerated from patches. The statement "the harness is the same" therefore rests on source inspection rather than on recorded provenance, and we cannot rule out a difference that reading the source did not surface. This is a real limit on the inference, and it is the reason the finding is framed as a re-qualification requirement rather than as a measurement of a vendor release.

The practical recommendation follows from the weaker reading as well as the stronger one. Qualification of an LLM-assisted checking aid is a dated statement about a component that can change outside the operator's control. Building inspection already has vocabulary for this — periodic re-verification of measuring instruments, re-qualification of a procedure after a change to any element of it. The corresponding practice here is to retain a frozen item set, re-run it on a schedule, and report a run-to-run range rather than a single figure.

## 5.4 Supplying the governing provision changes the operating point

The closed-book results above are a property of one deployment choice, not of the task. To separate the two, the grounded arms specified in EK-4 were run on `qwen2.5:32b-instruct` — the local model with the widest margin over chance after correction — over the refined corpus (corpus_v2, 1,755 units) with the audited v7a gold, three runs scored by majority vote, a 128-token output budget, and 0 of 1,524 responses truncated in each run. The figures are in §4.6; the readings below refer to them. Intervals for these arms are 95% cluster bootstraps on the same construction used elsewhere in the paper (4,000 resamples, clusters = law + article, seed 42), and the headline contrast is computed as a **paired** bootstrap over the same clusters, since R2 and R3-BM25 decide the identical claim set from the identical retrieved passages.

Four quantities set the scale. Closed book (R0), the model reaches balanced accuracy 0.6769 at coverage 0.173 under E1 and 0.5493 at full coverage under E2. Given three BM25-retrieved passages (R2), it reaches 0.8229 [0.7866, 0.8579] at coverage 0.899 under E1 and 0.8100 [0.7763, 0.8415] at full coverage under E2. Given the full text of the cited article (R1, defined on the 289 article-attributing claims), 0.9164 [0.8804, 0.9494] at coverage 0.830 under E1 and 0.8615 [0.8207, 0.8987] at full coverage under E2. A string-containment rule with no language model, applied to the *same* three retrieved passages (R3-BM25), reaches 0.5938 [0.5598, 0.6261] at full coverage. The information index λ = accuracy(P1) + accuracy(P5) − 1, which is 0 for a system that cannot separate a correctly cited provision from a mis-attributed one whatever its raw accuracy, is 0.987 and 0.988 for R1, 0.804 and 0.829 for R2, and −0.043 for R3-BM25.

Three readings follow.

**The language model contributes over string matching on identical evidence.** R2 and R3-BM25 receive the same retrieved passages; the difference is that R2 asks a model to judge them and R3-BM25 applies a containment rule. The paired difference is +0.2292 in balanced accuracy under E1, 95% CI [+0.1939, +0.2635], and +0.2162 under E2, 95% CI [+0.1818, +0.2493]. Both intervals exclude zero, so this contrast is not a bare point difference: on this claim set the judgement step is separable from the evidence being present. The λ figures make the same point in a form that is harder to reach by chance: string matching over these passages scores −0.043, indistinguishable from no information on the P1-versus-P5 contrast, while R2 scores 0.804 and 0.829. Whatever the retrieved passages contain, a lexical rule cannot use it and the model can.

**A perfect citation is worth about five to nine points over BM25, but the two arms are not scored on the same items.** R1 exceeds R2 by 0.0935 under E1 and 0.0515 under E2. This is the cost of using an untuned retriever instead of the cited article — but R1 is defined only on the 289 article-attributing claims while R2 covers all 473, so this contrast is not paired: it confounds evidence quality with item composition, no paired interval is available for it, and it should be read as indicative. Under E2 the R1 and R2 intervals overlap ([0.8207, 0.8987] against [0.7763, 0.8415]). Under E1 they do not: R1's lower bound of 0.8804 lies above R2's upper bound of 0.8579, so the two intervals are disjoint. An earlier draft described them as touching, which is wrong in the direction that understates the E1 gap. Disjoint unpaired intervals are still not a paired test, and the item sets still differ, so the caution above stands on its own grounds rather than on interval overlap.

**Retrieval recall does not bound grounded accuracy, and we measured this rather than assuming it.** BM25 at k = 3 places the cited unit among the retrieved passages for 79 of 289 article-level claims, a recall of 0.2734. It would be natural to infer that a grounded arm built on that retriever inherits 0.2734 as a ceiling. That inference is wrong: R2, built on exactly those retrieved passages, reaches balanced accuracy 0.8229 under E1 and 0.8100 under E2, with intervals whose lower bounds are 0.7866 and 0.7763. Recall measures whether the *cited* unit was retrieved; it does not measure whether the retrieved units were sufficient to judge the claim. Two mechanisms could produce this and our design does not separate them: the retrieved passages may support a verdict without being the cited unit — much Turkish regulatory text repeats near-identical phrasing across articles, so a neighbouring provision often settles a numeric or currency claim — or the model may be completing from parametric knowledge it also displayed in the closed-book arm. We report the gap between recall and end-to-end accuracy as measured and unattributed. Any claim that R2's performance is retrieval-driven would require an ablation we did not run.

**Determinism.** Within-arm agreement for `qwen2.5:32b-instruct` was 1.0000 in both R1 and R2 across the three pairwise run comparisons, at 1,524 calls per run: the arm is fully deterministic at this setting, and majority voting over three runs changed nothing for this model. This narrows a finding that would otherwise have been stated too broadly. The non-determinism we recorded elsewhere (17 of 20 items agreeing across runs) belongs to `llama3.2:3b`, which was also the model that dropped the output-format instruction. Both observations are properties of that one model, not of grounded prompting or of local serving in general. We therefore do not recommend three-run majority voting as a general requirement for local grounded arms; we recommend measuring within-arm agreement per model and voting only where it is below 1.

**What this changes about deployment.** The closed-book operating point for this model — balanced accuracy 0.5493 at full coverage under E2, or 0.6769 on the 17% of items it will speak about under E1 — does not support use as a screening aid on Turkish building regulation. The same model, same weights, same host, given the governing article or even three lexically retrieved passages, operates between 0.7763 and 0.9494 across the four grounded intervals. The design recommendation that follows is not "use a larger model" and not "do not use language models here": it is that the provision must be supplied. An architecture that asks a model to recall the Development Law is being asked to do the one thing this benchmark measures it failing at, and the fix is a retrieval or citation-resolution step that puts the text in front of it, not a better recall.

**The corpus deviation does not carry the result.** The refined corpus was a declared deviation from what the pre-registration named, and a deviation that improves the primary numbers is exactly the kind that a reader should distrust. The mandatory sensitivity arm of EK-6 §3 settles it: rerunning every grounded arm over the pre-registered 1,366-unit corpus moves balanced accuracy by between 0.007 and 0.019, and no paired interval excludes zero (§4.6.5). The refinement was adopted for a reason internal to the design — making the supplied unit the cited unit — and it turns out not to be load-bearing for any conclusion. Had it been, the honest report would have been that the paper's grounded results rest on a post hoc corpus change.

## 5.5 The rule baseline, and one circularity we cannot remove

The rule-based baseline R3-rule, which uses no language model, scores 473/473 on the refined corpus with the v7a gold and 466/473 on the raw corpus with the same gold. A negative control that shuffles the claim-to-rule pairing across five seeds averages 0.5315, so the score is not an artefact of the scoring path. The seven items R3-rule fails on the raw corpus (1.48% of the set) are the seven that the expert panel had frozen: 246, 257, 304, 360, 364, 382, 393. This convergence should not be described as independent replication. R3-rule did not generate those labels; it *failed* on them, which is to say it marked the same seven items. Moreover, the gold correction and the R3-rule failure both trace to the same corpus observation — the merged-clause parsing that the refined corpus repairs. The two views are consistent, but they are two views of one observation, and we report the agreement as a consistency check rather than as corroboration by an independent instrument.

R3-rule's 473/473 is also not evidence that the task is easy. R3-rule reads only the claim identifier and the claim text, and applies rules written against the corpus the claims were generated from; it is a control on the scoring path, not a competitor. R3-BM25 (§4.6) is the honest lexical comparison — a string rule over retrieved passages, with no privileged knowledge of how the claims were built — and it scores 0.5938 [0.5598, 0.6261].

A related circularity applies to the currency probe (P6): the corpus amendment-year field and the claim-set amendment note derive from the same regular expression applied to the same PDFs. The independent channel is the check against official consolidated text on mevzuat.gov.tr, which matched on 20 of 20 sampled items with 0 mismatches, and whose article counts reproduced our parser exactly (3194: 49, 4708: 15, 6331: 39). That check covers three laws only.

## 5.6 What would count as acceptable

Calling a system "not usable" requires a threshold, and this study did not establish one. A screening aid inside a building-inspection workflow would plausibly be judged on three quantities: the share of incorrect statements about the code that pass through unflagged, the share of the workload still requiring human reading, and whether the tool's own uncertainty signal can be trusted enough to route work. Our design measures analogues of the first two — balanced accuracy and coverage — but it does not measure the cost asymmetry between a missed error and a false alarm in a real office, and without that asymmetry a numeric pass mark cannot be set from these data. We therefore state the operating points and leave the threshold to the adopting organisation.

What can be said concretely, in closed book: the best hosted configuration observed here commits on 0.615 of items at balanced accuracy 0.6920 with an expected calibration error of 0.0373, meaning its stated confidence tracks its actual hit rate closely — the way a gauge that reads 5 mm when the true gap is 5 mm is in calibration. Its forced-choice counterpart reaches full coverage (1.000) at balanced accuracy 0.6242 with ECE 0.0634. The second hosted model reaches 0.5298 [0.489, 0.570] at coverage 0.710 with ECE 0.2263 — an interval that includes 0.5 and a confidence signal far from calibrated. Any of these leaves a substantial residue of items for human review.

Grounding moves the numbers into a different band but does not by itself settle the question. R2 at 0.8229 [0.7866, 0.8579] (E1, coverage 0.899) and 0.8100 [0.7763, 0.8415] (E2, coverage 1.000) still misses roughly one claim in five, and a workflow that treats an 18–19% error rate on regulatory statements as acceptable would have to say why. A second constraint applies to any threshold set from these data: the gold labels themselves carry an estimated contextual error rate of 6.7% in the audited frame, 95% CI [1.6%, 11.8%] (§6), so a threshold drawn to separate configurations by less than a few points is drawing on resolution the reference standard does not have. What the grounded arms establish is where the engineering effort belongs: on getting the provision in front of the model and on measuring the retriever, rather than on selecting among closed-book models. An organisation with a threshold in mind should apply it to a grounded configuration measured on its own document set, since the retrieval component — the part these results show to matter and the part we tested least — is the one that will differ most between deployments.

# 6 Limitations

**The second expert pass is negative, and it bounds the gold standard.** Section 3.6 reports first-pass agreement of κ = 1.000 on the verdict axis and κ = 0.860 on the item-quality axis (n = 150). Those figures describe a pass that shows the rater the same quoted sentence the label was derived from. The second pass asked the harder question — is the claim true of the whole article, read in the source — on 60 items across three strata, and its result is worse in every respect. Inter-rater agreement is Cohen's κ = 0.722 (p_o = 0.897, p_e = 0.628, n = 58). The six disagreements all run in the same direction, {(false, true): 6}, and a sign test on that asymmetry gives p = 0.0312, so the disagreement is systematic rather than random. The audit report's own reading is that the two raters are applying different rules — one asking whether the provision appears in the source at all, the other whether it appears *under the stated conditions* — which is a definitional difference, not measurement noise, and cannot be closed by averaging the two codings. Eight items were routed to a consensus file; that consensus was not held before this paper was written, so the second pass is reported as an open finding and not as a resolved one.

**The positive control on the expert audit failed.** Two items with known gold errors were seeded into the second pass as controls. Under the strict rule — an error counts as caught only if both raters flag it — 0 of 2 were caught. Under the lenient rule — at least one rater flags it — 1 of 2 were caught. The audit report therefore designates the lenient rule as the primary measure and the strict rule as a lower bound, and it states that the first pass's clean sheet of 0 defects in 150 codes must be read in the same light: a procedure whose controls do not all fire cannot certify an absence of defects.

**Contextual gold-label error rate.** Under the lenient rule the stratum-weighted rate is 5 of 33 in the flagged stratum (15.2%, 95% CI [6.7%, 30.9%]) and 1 of 25 in the clean stratum (4.0%, 95% CI [0.7%, 19.5%]). Correcting for the two-stage sampling gives a frame estimate of 6.7%, 95% CI [1.6%, 11.8%], over the 138-item first-pass frame, and 8.8% when the stratum weights are projected onto the whole claim set. Under the strict rule no event was observed in 58 items, which we report as 0 of 58 with a one-sided 95% upper bound of 6.2% rather than as a zero rate. Accuracy figures throughout this paper are measured against labels carrying a defect rate of that order, and differences between configurations of a few points should be read with that in mind.

**The first-pass quality flag is a tendency, not a validated predictor.** Items the first pass flagged as less than clean failed the second pass at 15.2% against 4.0% for items both raters called clean, a lift of 3.8×. Fisher's exact test on that table gives p = 0.2216. The direction is as intended, the sample is too small to establish it, and we report the lift as a tendency; no predictive validity is claimed for the flag, and it is not used to weight or filter any result.

**Single run against three.** The repeated hosted run is one run; the archive baseline is three. A single value cannot itself establish a range, so the drop to 0.6422 is a comparison of one observation against a previously measured band, not a comparison of two bands.

**What "version" does not mean here.** We observed a change in the behaviour of a hosted endpoint on a fixed item set between two dates. We did not observe, and were not told, any vendor release, weight change or serving change; no vendor version identifier was recorded. "Version drift" is our label for a behavioural difference, not a claim about the provider's internals.

**Provenance of the harness comparison.** As set out in §5.3, the archived runs carry no script hash, and the identity of the variant A prompts was re-derived from archived source rather than read from run records.

**Δ is exploratory.** The selectivity measure Δ was added in the pre-registration addendum (EK-1 §3) after the main pre-registration and after the run had completed, though before any accuracy metric was computed. The addendum itself marks it exploratory and applies no multiplicity correction to it. It carries the evidential weight of an exploratory analysis, not of a pre-specified test, and the paper's confirmatory abstention result is the condition contrast BAcc(E1) − BAcc(E2), reported with the Bonferroni-2 intervals of §5.2.

**Deviation from the pre-registered coverage rule.** The main pre-registration (§3) declared that a cell answering fewer than 80% of items would not be scored. The addendum (EK-1 §1) redefined that threshold to apply to the parsable-response rate rather than to the commitment rate, on the ground that commitment rate is the dependent variable and gating on it would classify the measured behaviour as non-compliance. The redefinition was made after the run completed and before any accuracy metric was computed, and it rests on the definition of the two rates rather than on what the results showed. It is nonetheless a deviation from the frozen protocol, and the addendum states that it must be declared in the paper. Two models are excluded by the corrected rule on response rate (`llama3.2:1b` at 0.545, `llama3.2:3b-instruct-q4_K_M` at 0.674), both because they echo the claim text instead of emitting a label. Four further cells — the `qwen2.5:7b-instruct` quantisations, at 6, 24, 18 and 16 committed answers — pass the response-rate gate but fall under the separate minimum-n reporting rule of EK-1 §2 and carry no scored figure. Twelve of the eighteen E1 / variant A cells are therefore scored, and the six that are not support no statement in this paper.

**Multiplicity leaves two models, one of them marginal.** After the pre-registered Bonferroni correction over eighteen models, two open-weight configurations exclude 0.5, and the second does so by 0.0017 (`gemma3:27b`, lower bound 0.5017). Conclusions about the open-weight arm should be read at that strength. The uncorrected count of four is reported alongside so that a reader who prefers per-cell inference can see both.

**The grounded arms cover one model.** R0, R1, R2 and R3-BM25 were run on `qwen2.5:32b-instruct` only. `gemma3:27b`, the other model surviving the correction and the one with near-full closed-book coverage, was not run in any grounded arm, so we cannot say whether the closed-book-to-grounded gain reported in §5.4 generalises across local models, across model sizes, or to the hosted arm. The grounded results are one model on one corpus.

**R2's success is not decomposed.** BM25 recall on the article-attributing subset is 0.2734 while R2 reaches balanced accuracy 0.8229 [0.7866, 0.8579]; the two mechanisms that could explain the difference — sufficient but non-cited passages, and parametric completion — were not separated by an ablation. Reported as measured.

**One untuned retriever.** BM25 at k = 3 is the only retrieval configuration tested, and its recall of 0.2734 over the 1,755-unit corpus characterises that configuration alone. Two observations bound how that recall figure may be read. Within the primary configuration it does not cap grounded accuracy (§4.6.4). Across corpora it does not order it either: the 1,366-unit corpus retrieves the cited unit more often (0.3010) and scores marginally lower in all four grounded cells (§4.6.5). Neither observation says that retrieval is unimportant; both say that this recall number is not the quantity that predicts accuracy here, and we did not measure what is.

**R1 and R2 are not scored on the same items.** R1 is defined on the 289 article-attributing claims and R2 on all 473, so the R1 − R2 difference has no paired interval and is reported as a point difference only. The paired contrast in this paper is R2 − R3-BM25, which is computed on identical items and identical evidence.

**Determinism is a per-model measurement.** Within-arm agreement of 1.0000 was measured for `qwen2.5:32b-instruct` in R1 and R2. It is not a property of local serving generally: `llama3.2:3b` agreed on 17 of 20 items across runs in the same setting.

**Independent currency verification is partial.** The check against official text covers 3194, 4708 and 6331. The building-inspection implementation regulation (YDUY) was not covered, leaving 43 currency claims without independent verification.

**Mechanism unmeasured.** We report what changed in the outputs; we did not measure why. Whether the shift in abstention selectivity reflects decoding, serving, prompt handling or something else is outside what these runs can determine.

**Two effect sizes.** The condition contrast and Δ move in the same direction but by different relative amounts (56% and 28%), and the archive Δ band is wide. Readers should treat the magnitude of the selectivity decrease as uncertain.

**Suppressed cells.** In 8 of 56 cells fewer than 50 confidence-bearing records were available, and calibration and Brier figures were suppressed there rather than reported at low precision.

**Repository history was reconstructed.** Access to the original machine was lost and the repository was rebuilt from packaged archives (`REKONSTRUKSIYON.md`). File contents are verifiable against archive checksums — the sealed claim generator carries an identical SHA-256 in two independently packaged archives, and 31 of 31 files in the handover package match byte for byte — but commit timestamps are not: that each pre-registration was written before the run it governs cannot be demonstrated from git history, which begins on 27.08.2026. The dates written inside the pre-registration texts and the file modification times inside the archives support the ordering; they are weaker than a commit stamp, and we do not present them as equivalent.

# 7 Conclusions

RUHSAT-Bench evaluates 473 claims about six frozen Turkish regulatory documents under two response conditions. The gold labels were adjudicated by two domain experts in two passes, and the two passes disagree about how firm the standard is. The first pass, which shows the rater the quoted sentence the label came from, reaches decision-level Cohen's κ = 1.000 [1.000, 1.000] and quality-level κ = 0.860 [0.759, 0.961] on 150 items. The second pass, which requires the rater to open the source and read the whole article, reaches κ = 0.722 on 58 items, with all six disagreements in one direction (sign test p = 0.0312) and its seeded positive control caught 1 of 2 under the lenient rule and 0 of 2 under the strict one. It estimates a contextual label-error rate of 6.7%, 95% CI [1.6%, 11.8%], in the audited frame. The benchmark is therefore usable for separations larger than that rate and should not be used to certify smaller ones.

Four results carry over to practice.

First, the open-weight closed-book arm is a coverage–accuracy trade-off rather than a flat failure, and how much of it survives depends on the correction. Eighteen local configurations produced an E1 / variant A cell and twelve of them are scored; four exclude chance on uncorrected per-cell intervals, and after the pre-registered Bonferroni correction over eighteen models, two do — `qwen2.5:32b-instruct` (lower bound 0.5349) at coverage 0.173, and `gemma3:27b` (lower bound 0.5017, a margin of 0.0017) at coverage 0.970. There is signal in the local arm, and at that strength it does not support deployment.

Second, abstention frequency and abstention quality can move independently, and the value of abstention is model-specific. Across the archived and repeated hosted runs the abstention count fell 2.2% while the confirmatory condition contrast fell 56% and the exploratory selectivity measure Δ fell 28%. A deployment that monitors abstention rate alone would not have seen this. Across the two hosted models, the same confirmatory contrast is +0.0678 with a Bonferroni-2 interval of [+0.0190, +0.1170] for `claude-sonnet-5`, which excludes zero, and −0.0260 with [−0.0659, +0.0183] for `claude-haiku-4.5`, which does not: abstention is worth something for one of the two models and nothing measurable for the other.

Third, a hosted model's behaviour on a frozen item set moved outside its own previously measured run-to-run range while the harness was, as far as source inspection can establish, unchanged. Qualifying such a tool is therefore a dated statement, and it calls for a retained frozen item set and scheduled re-qualification, in the same sense in which a torque wrench carries a calibration expiry.

Fourth, the closed-book deficit is a deficit of the architecture, not of the task. Given the cited article, `qwen2.5:32b-instruct` reaches balanced accuracy 0.9164 [0.8804, 0.9494] (E1, coverage 0.830) and 0.8615 [0.8207, 0.8987] (E2); given three BM25-retrieved passages, 0.8229 [0.7866, 0.8579] and 0.8100 [0.7763, 0.8415]; asked the same claims with nothing supplied, 0.6769 on the 17% of items it will answer and 0.5493 when forced. A string-matching rule over the *same* retrieved passages reaches 0.5938 [0.5598, 0.6261], and the paired difference R2 − R3-BM25 is +0.2292 [+0.1939, +0.2635] under E1 and +0.2162 [+0.1818, +0.2493] under E2, both excluding zero: roughly 22 points of the grounded result come from the model's judgement of the evidence rather than from the evidence being present. The practical implication is direct: do not deploy a closed-book configuration against Turkish building regulation, and put engineering effort into supplying the governing provision. We add two cautions to that recommendation — the grounded arms were run on one model, and the retriever's recall of 0.2734 on the article-attributing subset shows the retrieval component is the least examined part of the pipeline, and it is the component a deployment would have to characterise against its own documents.

We do not set a numeric acceptance threshold, because the cost asymmetry that would define one was not measured. We report operating points instead, together with the limits under which they should be read: one repeated run, one untuned retriever, grounded arms on a single model, a second expert pass whose disagreement is systematic and whose consensus is not yet held, partial independent currency verification, an unmeasured mechanism, a deviation from the pre-registered coverage rule that we declare in §6, and a repository whose commit history was reconstructed.

---

# References

*Every entry below was checked against the OpenAlex record on 29.08.2026 and appears in `makale/ATIF_DOGRULAMA.md`. No source that failed verification is cited in this paper. Entries carry the fields present in that record — authors, title, venue, year, DOI or arXiv identifier; author initials, volume and page numbers are to be completed from the publisher records at proof stage rather than supplied from memory here.*

Chen, et al., 2024. Automated building information modeling compliance check through a large language model combined with deep learning. *Buildings* 14(7). doi:10.3390/buildings14071983

Chow, 1970. On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory*. doi:10.1109/tit.1970.1054406

Dahl, et al., 2024. Large legal fictions: profiling legal hallucinations in large language models. *Journal of Legal Analysis*. doi:10.1093/jla/laae003

Eastman, et al., 2009. Automatic rule-based checking of building designs. *Automation in Construction*. doi:10.1016/j.autcon.2009.07.002

El-Yaniv and Wiener, 2010. On the foundations of noise-free selective classification. *Journal of Machine Learning Research*. doi:10.5555/1756006.1859904

Geifman and El-Yaniv, 2017. Selective classification for deep neural networks. arXiv:1705.08500

Guo, et al., 2017. On calibration of modern neural networks. *International Conference on Machine Learning (ICML)*. arXiv:1706.04599

Jiang, et al., 2021. How can we know when language models know? On the calibration of language models for question answering. *Transactions of the Association for Computational Linguistics*. doi:10.1162/tacl_a_00407

Kadavath, et al., 2022. Language models (mostly) know what they know. arXiv:2207.05221

Lin, et al., 2022. Teaching models to express their uncertainty in words. arXiv:2205.14334

Magesh, et al., 2025. Hallucination-free? Assessing the reliability of leading AI legal research tools. *Journal of Empirical Legal Studies*. doi:10.1111/jels.12413

Naeini, et al., 2015. Obtaining well calibrated probabilities using Bayesian binning. *AAAI Conference on Artificial Intelligence*. doi:10.1609/aaai.v29i1.9602

Robertson and Zaragoza, 2009. The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*. doi:10.1561/1500000019

Solihin and Eastman, 2015. Classification of rules for automated BIM rule checking development. *Automation in Construction*. doi:10.1016/j.autcon.2015.03.003

Xiong, et al., 2024. Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. *International Conference on Learning Representations (ICLR) 2024*. arXiv:2306.13063. — *The arXiv preprint is dated 2023 and the conference version 2024; this paper cites the ICLR 2024 version throughout.*

Zhang and El-Gohary, 2013. Semantic NLP-based information extraction from construction regulatory documents for automated compliance checking. *Journal of Computing in Civil Engineering*. doi:10.1061/(asce)cp.1943-5487.0000346 — *cited as 2013; an earlier draft of this paper dated the same work to 2016, which is incorrect.*

Zhou and El-Gohary, 2016. Ontology-based automated information extraction from building energy conservation codes. *Automation in Construction*. doi:10.1016/j.autcon.2016.09.004 — *cited as 2016; an earlier draft of this paper dated it 2017, which is incorrect.*

## Standard

IEC 61508. *Functional safety of electrical/electronic/programmable electronic safety-related systems.* International Electrotechnical Commission, Geneva. — *A standard rather than a journal article. It lies outside OpenAlex coverage and its bibliographic entry could not be verified against the IEC catalogue; the edition and part number should be completed from the IEC catalogue before submission.*

## Primary legal sources

The six documents that constitute the corpus were frozen as PDF files and are distributed with the benchmark under SHA-256 checksums (§3.2): Law No. 3194 on Development (`3194_imar_kanunu.pdf`, 49 articles); Law No. 4708 on Building Inspection (`4708_yapi_denetimi.pdf`, 15 articles) and its implementing regulation (`yapi_denetim_uygulama_yon.pdf`, 36 units); Law No. 6331 on Occupational Health and Safety (`6331_isg_kanunu.pdf`, 39 articles) and the risk-assessment regulation issued under it (`isg_risk_yonetmeligi.pdf`, 19 units); and the Turkish Building Earthquake Code, TBDY 2018 (`TBDY_2018.pdf`, 1,208 units in the raw parse, 1,523 in the refined corpus).

---
