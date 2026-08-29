# RUHSAT-Bench — JESTECH taslağı (3. tur)

> Bu 3. tur metnidir. 4. tur revizyonunun GİRDİSİDİR.
> Bilinen açıklar: ikinci geçiş denetimi yok, puanlanan hücre sayısı 12 yerine 14
> yazıyor, dayanaklı kollarda GA yok, kaynakça yok.

# 1. Introduction

Building permitting and inspection in Türkiye rest on a compact stack of binding instruments: the Development Law (No. 3194), the Building Inspection Law (No. 4708) together with its implementing regulation (YDUY), the Occupational Health and Safety Law (No. 6331) with the risk-assessment regulation, and the Turkish Building Earthquake Code (TBDY 2018). Much of the daily work in an inspection office is documentary rather than analytical: does an obligation sit in Law 4708 or in its regulation, is the article a file cites the article that actually carries the rule, was that article amended in the year an applicant states. Each such question has a checkable answer in a published text.

Automating these checks is a long-standing goal in construction informatics. Rule-based model checking encodes provisions as machine-verifiable constraints (Eastman et al., 2009; Solihin and Eastman, 2015), while NLP-driven extraction attempts to recover those constraints from the regulatory text itself (Zhang and El-Gohary, 2013; Zhou and El-Gohary, 2016), and more recent work places a language model inside the compliance-checking loop (Chen et al., 2024). Those lines assume the governing text is in hand. Large language models (LLMs) also support a different proposition: an answer produced from model parameters with no document supplied. We refer to this as the **closed-book** setting — the system is asked about a provision without being shown it, the way a person answers from memory. It is also one of the ways these systems are in fact consulted, when an engineer types a regulatory question into a chat window and acts on what comes back (Dahl et al., 2024; Magesh et al., 2025).

**Terminology.** A model *abstains* when it returns "I am not sure" instead of a verdict; *coverage* is the fraction of claims on which it commits to a verdict, so coverage 1.000 means it always answers. *Balanced accuracy* averages accuracy on true claims with accuracy on false claims, so a system that answers "false" to everything scores 0.5 regardless of how many false claims the set happens to contain. *Calibration* is the correspondence between stated confidence and observed correctness, in the sense in which a pressure gauge is calibrated against a reference: a gauge that reads 6 bar should mean 6 bar, and a model that reports 90 % confidence should be right on about 90 % of such items (Guo et al., 2017; Jiang et al., 2021). *Expected calibration error* (ECE) is the average gap between the two, so smaller is better (Naeini et al., 2015). Confidence intervals are obtained by *bootstrap* — repeatedly resampling the evaluated claims and reading the spread of the resulting scores — clustered by statute and article, so that claims from the same article are resampled together.

**RUHSAT-Bench.** We assemble 473 claims over the six documents above, indexed against a corpus of 1755 regulatory units, with a gold label distribution of 223 true and 250 false. Claims are organised in six probe families: direct assertion (163), numeric value (37), cross-reference (121), currency of amendment (120), anachronism (19), and fabricated provision (13). Each system is run under two conditions: abstention-permitted (E1) and forced binary choice (E2). Closed-book operation is one arm of the design, not the whole of it: three grounded arms supply the governing text — perfectly, by retrieval, or not at all with a non-neural rule baseline — so that the study measures a mode of use rather than pronouncing on a technology. Gold labels passed a two-coder expert audit (Cohen's κ = 1.000 on the decision, 0.860 on quality), and the currency family was checked against official HTML on mevzuat.gov.tr, where 20 of 20 sampled claims agreed.

**What would count as usable?** A benchmark number is not a verdict on its own; declaring a system unusable requires a threshold, and we could not locate a defensible one. Turkish building-inspection practice sets no accuracy requirement for advisory software, and the compliance-checking literature reports system performance without stating an acceptance level. We therefore do not issue an absolute verdict. Section 2.2 sets out the shape such a criterion would need to have — which is, we argue, a criterion on the abstention behaviour rather than on accuracy alone — and our results are reported so that a reader who does have a threshold in mind can apply it.

**Contributions.**

1. A regulatory benchmark for Turkish construction law with auditable provenance: every reported figure is regenerated from committed script outputs, and the claim set, gold labels and expert-audit record are released with the code. One deviation between the main pre-registration and its first appendix is declared in Section 3, together with its date and its reason.

2. A measured **coverage–accuracy trade-off** among open-weight models rather than a blanket failure. Eighteen open-weight configurations produced a scoreable E1 cell under prompt variant A. Read with uncorrected 95 % cluster-bootstrap intervals, four of them exclude 0.5. The pre-registration requires a Bonferroni correction over the number of models — 18 models, a per-cell level of 0.00278, that is 99.72 % intervals — and after that correction two survive: qwen2.5:32b-instruct, balanced accuracy 0.6769, lower bound 0.5820 uncorrected and 0.5349 corrected, at coverage 0.173; and gemma3:27b, balanced accuracy 0.5674, lower bound 0.5235 uncorrected and 0.5017 corrected, at coverage 0.970. The second clears chance by less than two thousandths of a point and should be read as marginal. The two that do not survive the correction are llama3.2:3b-instruct-q8_0 (0.5509, corrected lower bound 0.4878) and gemma3:12b (0.5493, corrected lower bound 0.4915). The 32B model's uncorrected interval overlaps that of the hosted claude-sonnet-5 (0.6920 [0.633, 0.750], coverage 0.615), but it reaches its score while committing on roughly one claim in six — 82 committed items, above the floor of 30 committed items at which accuracy-type metrics are reported, so the cell is scored, and its accuracy and its coverage have to be read as one figure rather than two. Which operating point is preferable depends on the workflow, and Section 2.2 argues the choice cannot be made by accuracy alone.

3. An account of abstention as a measured quantity rather than an assumed safety feature. Two summaries are reported side by side: the confirmatory contrast BAcc(E1) − BAcc(E2) from the main pre-registration, and Δ, the difference in forced-choice accuracy between the items a model committed to and the items it abstained from. Δ is an exploratory measure, added in EK-1 after the main pre-registration; it is not part of the confirmatory set and carries no multiple-comparison correction. Both are given because they do not agree in magnitude, and reporting only one would let an author choose the larger effect.

4. A re-qualification result: on a frozen claim set and prompts we verified to be byte-identical, a re-run of one hosted configuration falls outside the archived run-to-run range while remaining inside the archived clustered bootstrap interval. We report both baselines and justify which one answers the version question (Section 5).

5. **A grounded-arm measurement showing that the closed-book figures describe a mode of use, not a ceiling on the task.** For qwen2.5:32b-instruct — the same open-weight model that scores balanced accuracy 0.6769 at coverage 0.173 closed-book, and 0.5493 under forced choice — supplying the governing text changes the operating point. Given the cited article verbatim, balanced accuracy is 0.9164 (n = 289, coverage 0.830) with abstention permitted and 0.8615 at full coverage under forced choice. Given instead whatever one untuned BM25 retriever returns at k = 3, it is 0.8229 (n = 473, coverage 0.899) and 0.8100 at full coverage. A deterministic string-matching baseline over the same retrieved passages reaches 0.5938, so the language model contributes 0.2292 (abstention-permitted) and 0.2162 (forced-choice) balanced-accuracy points over string matching on identical evidence; the cost of using retrieval rather than a perfect citation is 0.0935 and 0.0515 points respectively. Each grounded arm was run three times and scored by majority vote, with 0 of 1524 responses truncated per run. What this does not establish is *why* the grounded arms succeed: the retriever's own recall is only 0.2734, so the model is evidently completing from parametric knowledge on many items, and the two contributions were not separated here.

6. A retrieval measurement bounded to what was tested: one untuned BM25 retriever — BM25 being a standard ranking function that scores a passage by how many of the query's *tokens* (word-like units) it contains, weighted by their rarity (Robertson and Zaragoza, 2009) — placed the cited unit among the top three for 79 of 289 article-level citations (recall 0.2734) on this corpus. That figure characterises this retriever at this setting on this corpus. It is not a bound on the accuracy of a system built on it, and should not be read as one: the grounded arm using exactly these retrieved passages scored 0.8229. It is likewise not a claim about retrieval-augmented systems in general.

# 2. Motivation

## 2.1 Fail-safe and fail-silent behaviour

Safety engineering distinguishes a component that fails into a defined safe state from one that fails while continuing to emit plausible output. A load cell that saturates and reads zero announces its own failure; one that drifts by 15 % does not. Functional-safety practice treats the second class as the harder problem, because the downstream process has no signal that anything is wrong (IEC 61508).

An LLM asked a closed-book regulatory question is a candidate fail-silent component. It returns a fluent verdict with a confidence figure attached, in the same register whether the provision is one it can reproduce or one it has never encountered. If the confidence figure tracked correctness, the component would be fail-safe by construction: an inspector could route low-confidence items to manual review. This is precisely the promise of selective prediction, where a classifier is permitted to reject inputs it cannot handle (Chow, 1970; El-Yaniv and Wiener, 2010; Geifman and El-Yaniv, 2017), and of work asking whether language models know what they know (Kadavath et al., 2022; Lin et al., 2022; Xiong et al., 2024).

Whether that promise holds for regulatory text is an empirical question, and it is the question this benchmark is built to answer. It cannot be answered by accuracy, because accuracy conditions on the items a model chose to answer. A system that abstains on 83 % of claims and a system that answers all of them are not comparable on accuracy alone; both numbers are reported here alongside coverage for that reason. The closed-book arm isolates the failure mode; it is not the recommended architecture, and the grounded arms of Section 3.5 are run precisely so that a poor closed-book figure is not mistaken for a limit on what the same model can do when the governing article is placed in front of it.

## 2.2 An acceptance criterion has to be about abstention

Consider a building-inspection workflow in which a model pre-screens claims in a permit file and flags the doubtful ones for an engineer. The quantity that governs whether this saves work is not overall accuracy: it is whether the flagged set is enriched for errors. If abstention is uninformative — if the model declines items it would have got right at the same rate as items it would have got wrong — then the flags carry no triage value and the engineer must check everything regardless, at which point the screening step costs time without removing any.

This gives the shape of a usable acceptance criterion: a stated coverage level, an accuracy on the covered items, and evidence that accuracy on the abstained items is materially lower. Calibration enters the same criterion, because a confidence figure is only actionable if it means what it says; a model whose ECE is large is reporting a gauge reading that has not been calibrated against anything. We do not fix numeric values for these three quantities, because we have no principled basis on which to fix them for Turkish inspection practice, and we avoid statements of the form "this system cannot be used". We report the three quantities so that an organisation with its own tolerance can evaluate them. We are not aware of an established risk-based acceptance threshold for decision-support software in construction that could be adopted here, which is itself part of the reason the criterion is left open.

## 2.3 Benchmarks expire, so systems have to be re-qualified

A calibration certificate for a torque wrench carries an expiry date; the instrument is re-qualified on a schedule because its behaviour drifts. Hosted LLMs are updated behind a stable model identifier, and Section 5 reports one case in which behaviour on a fixed task changed between two dates without any announced version change. [ATIF DOGRULANMADI: hosted-LLM behaviour change over time — bu atif ATIF_DOGRULAMA.md kapsamina alinmamistir; kunye dogrulanmadan metne girmez.] A benchmark score for such a system is therefore a measurement at a date, not a property of the name.

We treat this as part of the study design rather than as a limitation note. One hosted configuration was re-run on the frozen 473-claim set months after the archived runs, under prompts whose identity we verified. Section 5 reports what changed, which baseline the comparison should use, and what the provenance of the archived runs does and does not allow us to assert. The result is reported not because the direction of the change is itself of interest, but because it establishes that a score of this kind needs a date attached and a re-qualification procedure defined — which is a requirement any deployment in a regulated inspection workflow would have to meet.

---

# 3. Materials and Methods

## 3.1 Terms used in this paper

The study sits between legal engineering practice and language-model evaluation, so the measurement vocabulary is fixed first.

| Term | Meaning as used here |
|---|---|
| Closed-book | The model is asked about a regulation without being shown its text, and must answer from what is stored in its parameters. |
| Abstention | An explicit "not sure" response, offered as a third option in one of the two conditions. |
| Coverage | The share of the claim set on which a model commits to a verdict instead of abstaining or emitting an unparsable output. |
| Commitment count | Coverage expressed as a count of claims rather than a fraction: coverage × 473. It governs which cells carry an accuracy figure (§3.4). |
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

Each document is identified in the release by a SHA-256 of its extracted text. The raw segmentation was later found to merge adjacent TBDY clauses, so a refined corpus was built and made primary (EK-6): TBDY 1,208 → 1,523 units, the five remaining documents 158 → 232 units, the latter recovering annex and provisional articles that the first parser had dropped (16 annex and 58 provisional articles). The refined corpus holds 1,755 units. The raw 1,366-unit corpus is retained and reported alongside as a sensitivity arm, because it, not the refined one, is what the pre-registration named.

## 3.3 Claim set

A sealed deterministic generator produced 473 claims from the corpus; the generator was never re-executed, so claim identifiers are stable across the whole study. The gold distribution is 223 true / 250 false. Six probe families are represented: P1 verbatim or article-cited provision (163), P5 provision attributed to the wrong article or document (121), P6 amendment-history statement (120), P2 altered quantity (37), P3 enactment-year statement (19), P4 invented document or clause (13). Surface form is held constant within contrasting pairs, so P1, P2 and P5 items are lexically alike and separable only through knowledge of the source.

Citations are resolved from the claim text alone, never from the generator's bookkeeping columns, because in P5 the cited location and the true source deliberately differ: 289 claims cite an article, 184 cite only a document. This is the same operation an engineer performs — look at the provision the claim points to.

## 3.4 Conditions, prompt variants, runs and scoring gates

Every claim is asked twice. **E1** allows abstention (true / false / not sure); **E2** forces a binary choice. Two system-prompt variants (A and B) were written for each condition; A is primary and B is a controlled re-wording. Output budget is part of the run label (A@32, A@128, B@128). For the hosted models, extended thinking was disabled so that the task matched the local arm, and this was verified per response rather than assumed.

**Repeat runs.** Each hosted configuration and each local grounded arm was executed three times and scored by majority vote. The policy was adopted because one local model, llama3.2:3b, reproduced only 17 of 20 identical calls; the same model also departed from the output-format instruction, so the two defects recorded for local inference belong to a single model rather than to local inference as such. Repetition is not required everywhere: for qwen2.5:32b-instruct the within-arm agreement across the three grounded runs was 1.0000 in both R1 and R2 (three pairwise comparisons, 1,524 calls per run), which is exact reproduction, so for that model the vote changes no record and a single run would have sufficed. We therefore state the repeat requirement per model, on measured agreement, rather than as a blanket rule for grounded or local execution.

**Two gates, and one quantity that is deliberately not a gate.**

1. *Response-rate gate (pre-registered, as corrected in EK-1 §1).* A model × condition cell whose parsable-response rate — any usable label, of any kind, divided by 473 — falls below 0.80 is reported as non-compliant in form and is not scored. Two local cells fall below it: llama3.2:1b (E1 0.55, E2 0.03) and llama3.2:3b-instruct-q4_K_M (E1 0.67, E2 0.66). Both write the claim text back instead of emitting a label, so the failure is one of output format.
2. *Commitment rate (coverage) is not a gate.* It is the dependent variable of this study. A model that abstains often is producing the measurement, not failing the protocol, and no cell is excluded, downgraded, or described as non-compliant on account of low coverage anywhere in this paper.
3. *Minimum-n reporting rule (EK-1 §2, post hoc).* Accuracy-type metrics — balanced accuracy, Youden's J, d′, ECE — are reported only for cells with at least 30 committed answers. Below that the count is given and the metric is left blank. The rule exists because a balanced accuracy computed on a handful of items is not interpretable, not because the underlying behaviour is uninteresting.

Applying rule 3 to the eighteen E1 / variant A cells, with commitment count taken as coverage × 473, four cells fall below the threshold: qwen2.5:7b-instruct-q4_K_M (6 committed answers), qwen2.5:7b-instruct-fp16 (24), qwen2.5:7b-instruct-q8_0 (18) and qwen2.5:7b-instruct-q5_K_M (16). Those four rows are **kept** in Table 2, because their coverage is itself a result and removing them would hide four of the eighteen systems, but their balanced accuracies and intervals are marked *not scored*, are printed in no comparison, and support no statement in Sections 4 and 5. Twelve of the eighteen cells therefore carry a scored accuracy figure: eighteen cells exist, two fail the response-rate gate, four fall under the minimum-n rule. Separately, ECE and Brier are suppressed in 8 of 56 cells that carry fewer than 50 confidence-bearing records.

**Pre-registration, and one deviation from it.** The main pre-registration (`sonuclar/F4_on_kayit.txt`) was frozen before the runs. Its item 3 applied the 0.80 gate to whether a cell "answers" the claims, and that phrase covers two distinct quantities: whether the model emitted a parsable label at all, and whether that label was a commitment rather than an abstention. Addendum EK-1 (`sonuclar/F4_on_kayit_ek.txt`, 28 July 2026) re-defined the gate onto the first of the two. The addendum was written after the 17,028 closed-book calls had completed but before any accuracy metric had been computed; only response and abstention counts had been inspected at that point, and the addendum records that state. The reason for the change is a definition rather than an observation: applying an 0.80 floor to the commitment rate would classify the study's dependent variable as protocol non-compliance, so that a model producing fully parsable output while abstaining on 467 of 473 claims would be scored as non-compliant when it is in fact following the instruction exactly. The correct definition does not depend on what the data turned out to show. It is nonetheless a deviation from the frozen document, EK-1 itself states that it must be declared in the paper, and we declare it here. Both rules are reported: the corrected gate is primary, and the original gate is carried as a sensitivity arm. The minimum-n rule above is likewise post hoc, is a reporting convention only, and is used in no hypothesis test.

## 3.5 Grounded arms

Closed-book performance bounds an architecture rather than the task, so a grounded ladder was pre-registered (EK-4) against the closed-book arm R0. That ladder has now been executed.

| Arm | n | Evidence supplied | Role |
|---|---|---|---|
| R0 | 473 | none (closed-book) | baseline |
| R1 | 289 | full text of the cited article | upper reference point, not a deployable configuration: it presupposes that the citation in the claim has already been resolved correctly |
| R2 | 473 | BM25 top-k (k = 3) over the 1,755 refined units | retrieval plus judgement |
| R3-BM25 | 473 | the same retrieved passages, with no model: verdict from lexical match alone | retrieval-only control |

**A naming point.** Two different objects in this study are recorded as "R3". R3-BM25, in the table above, is the no-model control inside the grounded ladder (run record `r3_bm25`, 473 decisions, no E1/E2 split). The deterministic string-rule baseline described below and reported in Section 4.5 is a separate control (run record `kural_taban_r3`, 946 decisions across the two conditions); it performs no retrieval and reads the generator's article mapping. They are kept apart here as **R3-BM25** and **R3-rule**, and the distinction matters because their scores differ by a wide margin.

**Execution.** The grounded ladder was run with a single model, qwen2.5:32b-instruct, on the refined corpus (corpus_v2, EK-6 primary) against the v7a gold labels, three runs plus majority vote, 128-token output budget, seed 42. No response was truncated in any run (0 of 1,524 per run). R0 for the same model is its closed-book cell, so R0, R1, R2 and R3-BM25 differ in the evidence supplied and in nothing else.

R1 is restricted to 289 claims by the data, not by choice: the remaining 184 cite only a document, and document texts run from roughly 17k to 871k characters.

**Retrieval is reported separately from judgement**, as the pre-registration requires. BM25 at k = 3 places the cited unit in the retrieved set for 79 of the 289 article-level claims (recall 0.2734) and misses 210. That figure characterises one untuned lexical retriever at one value of k on this corpus. It is reported as a property of the retriever and **not** as a bound on the accuracy of an arm built on that retriever: the two contributions to a grounded verdict — evidence actually supplied by retrieval, and knowledge the model brings to a passage that does not contain the cited provision — are not separated by this design, and Section 4.6 reports an R2 balanced accuracy far above what the recall figure on its own would imply. Any reading in which the recall number caps the grounded arm is contradicted by the measurement.

**R3-rule** is blind by construction — it reads only the claim identifier and the claim text, and asserts this at start-up — and has no abstention option, so it is excluded from the calibration comparisons. Its matching rules were fixed before the run. Its behaviour is corpus-dependent in an informative way: with the refined corpus and the audited gold labels it decides 473/473 claims correctly, while the raw corpus paired with the same labels gives 466/473, and the 7 claims that separate the two (1.48% of the set) are exactly the 7 whose gold labels the expert audit had frozen. A shuffled-pairing negative control over five seeds returns 0.5349, 0.5349, 0.5159, 0.5370 and 0.5349 (mean 0.5315), establishing that the rule set is exploiting the pairing rather than a surface regularity.

Because R3-rule's amendment-history channel is reconstructed from the same annotations the claims were generated from, the check is circular in the sense that it verifies channel presence rather than legal correctness. A sample of 20 P6 claims was therefore checked against official consolidated HTML text: 20 agreed, 0 disagreed, and our parser reproduced the official article counts exactly (3194: 49, 4708: 15, 6331: 39). The verification frame covers only 3194, 4708 and 6331; YDUY was outside it, so 43 P6 claims remain unverified against an independent source.

## 3.6 Gold-label quality assurance and expert audit

Five deterministic layers (source identity, accidental truth, sentence cleaning, rendering-artefact repair, design-leak audit) were applied first, each with a positive control that had to fire. Two specialists in civil engineering and occupational safety then audited the labels in two passes with gold, probe family, template and stratum hidden, and row order randomised per rater.

| | First pass | Second pass |
|---|---|---|
| Question put to the rater | is the claim consistent with the quoted sentence? | is the claim true of the whole article, read in the source? |
| Sample | 150 items (158 codes with controls) | 60 items |
| Strata | unflagged / consensus-flagged | N: all 33 items either rater called less than clean; T: 25 drawn from the 105 both called clean; K: 2 seeded known-bad controls |
| κ, verdict axis | 1.000, 95% CI [1.000, 1.000] | reported in Section 4 |
| κ, verdict excluding "not sure" | 1.000, 95% CI [1.000, 1.000] | — |
| κ, item-quality axis | 0.860, 95% CI [0.759, 0.961] | — |

The first-pass κ of 1.000 is a property of the instrument rather than evidence that the labels are sound: the workbook shows the rater the quoted sentence and the recorded article, which is the same evidence the label was derived from, so the pass re-derives the generator's reasoning instead of testing it against the legislation. Contextual defect counts from the first pass are zero in every probe family sampled (P1 0/22, P2 0/17, P3 0/15, P4 0/12, P5 0/16), but with these sample sizes the 95% upper bounds run from 14.9% to 24.3%, so the pass bounds the rate loosely rather than establishing it.

The second pass was designed to reach the class the first cannot: a sentence that, lifted from its article, no longer says what the article says. Raters opened the source and read the whole article. One consequence must be stated plainly, because it bears on how the R3-rule result above may be read. The 7 gold corrections were proposed after a corpus observation — the clause-merging defect — and the same observation motivated the refined corpus; the expert step confirmed the mis-attribution on those items but did not generate the labels independently, and R3-rule failed on those same 7 items rather than identifying them from scratch. The agreement between corpus repair, gold repair and R3-rule therefore contains a circular component, and the two are not independent confirmations of each other.

## 3.7 Outcome measures: two of them, reported together

Abstention is the dependent variable of this study, and it can be summarised in two ways that answer different questions. Both are reported everywhere, because they do not agree in magnitude.

| Measure | Definition | Status | Question it answers |
|---|---|---|---|
| BAcc(E1) − BAcc(E2) | Difference in balanced accuracy between the abstention-permitted and forced conditions, over the full claim set | Confirmatory: named in the main pre-registration, items 1.2–1.3, and carrying the multiple-comparison correction declared there | How much does the score improve when the model is allowed to stay silent? |
| Δ = A_com − A_abs | A_com is E2 accuracy on the items the model committed to in E1; A_abs is E2 accuracy on the items it abstained from in E1 | **Exploratory.** Introduced in addendum EK-1 §3, after the main pre-registration, under the heading "added analysis (exploratory, not in the pre-registration)". No multiple-comparison correction is applied to it, as that addendum specifies | Does the silence carry information — is the model worse on precisely the items it declined? |

The status column is not a formality. Δ is the measure closest to the study's central question, and it is nonetheless the one with the weaker evidential standing: it was written down after the main pre-registration was frozen, so it is reported descriptively, with intervals and without a hypothesis test, and it is never described in this paper as pre-registered. The confirmatory analyses of the main pre-registration are a separate set, and the two must not be read as one.

The first quantity mixes two effects, since removing low-accuracy items from the denominator raises the score even if the choice of items is arbitrary. Δ isolates the second effect: Δ > 0 means abstention is selective, Δ ≈ 0 means the model is merely reticent. Reporting only one of them would let an author choose the larger effect; we therefore give both, together with coverage, since a balanced accuracy obtained on a small fraction of the claim set is not the same object as one obtained on nearly all of it, and the two must be read side by side.

**Denominator of Δ.** Δ is computed over the claims for which the model produced an E2 verdict, and for a majority-voted configuration that means a verdict on which a majority formed. The two counts can therefore sum to fewer than 473. In Table 3 the row for claude-haiku-4.5 sums to 472 (335 committed, 137 abstained): claim 211 was answered under E1 (majority "false") but split three ways across the three E2 runs — false, true, and one response with no parsable label — so no E2 majority formed and the claim leaves the committed arm it would otherwise have joined. It is dropped once, from one arm, and is not counted anywhere else. This is the only such case in the hosted arm.

**Statistical treatment.** Uncertainty on any single configuration is a cluster bootstrap, clusters being (law, article) pairs, seed 42. Two interval levels appear in this paper and they are labelled wherever used. Nominal 95% intervals are computed with 10,000 resamples and describe one configuration on its own. The main pre-registration, item 1, also requires a Bonferroni correction over the number of models for the confirmatory comparisons; with 18 models and α = 0.05 this gives a per-cell level of 0.00278, that is a 99.72% interval, computed with 4,000 resamples. Both are reported for every confirmatory comparison, because they lead to different counts of models separated from chance and a reader is entitled to see which threshold produced which count. The correction is taken over all 18 models that produced an E1 / variant A cell, which is the more conservative choice: only 12 of those cells survive the gates of §3.4 and carry a scored accuracy figure. Δ, being exploratory, carries no correction and is reported with 95% intervals only.

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
natural-language-processing specialist.

## 4.1 The evaluated systems

The claim set is frozen at 473 items (223 labelled true, 250 false) drawn from
six Turkish regulatory documents, distributed over six probe families: 163
verbatim-attribution items (P1), 37 numeric-alteration (P2), 19 enactment-year
(P3), 13 fabricated-source (P4), 121 misattribution (P5) and 120
amendment-history (P6). Of these, 289 cite a specific article and 184 cite only
a document.

Each claim is put to each system under two conditions. Under **E1** the system
may answer "not sure" — this is **abstention**, declining to commit. Under **E2**
it must choose true or false. The runs in Sections 4.1 to 4.5 are all
**closed-book**: the system answers from what it already contains, with no
document text supplied, the equivalent of an examination taken with the code
book shut. Section 4.6 reports the arms in which the text is supplied.
**Coverage** is the fraction of the 473 claims on which a system commits instead
of abstaining. **Balanced accuracy** (BAcc) is the mean of accuracy on true
claims and accuracy on false claims, so 0.5 is the value of a coin flip
regardless of the class mix. Intervals are clustered **bootstrap** intervals
(10,000 resamples, clusters = statute + article): the claim set is resampled
repeatedly to estimate how far a figure would move had a different sample of
claims been drawn. **Calibration** is reported as expected calibration error
(ECE), the average gap between stated confidence and observed accuracy — the
same idea as checking a pressure gauge against a reference instrument: a gauge
reading 95 should be right about 95 times in 100. λ is a bias-corrected index
(accuracy on the always-true family plus accuracy on the always-false family,
minus one), which is zero for a system answering from a fixed response
preference.

**Table 1. Hosted arm, majority vote, closed book.**

| system | condition | BAcc | 95% CI | coverage | λ | ECE |
|---|---|---|---|---|---|---|
| claude-sonnet-5 | E1 | 0.6920 | [0.633, 0.750] | 0.615 | 0.325 | 0.0373 |
| claude-sonnet-5 | E2 | 0.6242 | — | 1.000 | 0.294 | 0.0634 |
| claude-haiku-4.5 | E1 | 0.5298 | [0.489, 0.570] | 0.710 | −0.026 | 0.2263 |
| claude-haiku-4.5 | E2 | 0.5558 | — | 0.998 | 0.061 | 0.2070 |

The uncorrected 95% interval for the smaller hosted model contains 0.5; the
uncorrected interval for the larger one does not. The multiple-comparison
correction fixed in the pre-registration is applied in Section 4.2 over the
open-weight family; corrected bounds were not computed for these two hosted
configurations [SAYI YOK: Bonferroni-corrected intervals, hosted arm], so
Table 1 should be read as uncorrected. The calibration figures differ by roughly
a factor of six between the two systems. The calibration estimator was checked
against a positive control: applied to the deterministic rule baseline of
Section 4.5 it returns 0.0000, where the earlier mid-point formula returned
0.0500. In 8 of 56 cells fewer than 50 committed answers carried a confidence
value, and ECE is suppressed for those cells rather than reported.

## 4.2 The coverage–accuracy trade-off

Eighteen open-weight models have a complete E1 cell under prompt variant A.
Two suppression rules declared in Section 3.4 are applied to Table 2 rather than
merely stated. First, accuracy-type metrics are reported only where the model
committed to at least 30 claims (pre-registration addendum EK-1 §2); the
committed count is coverage × 473. Four cells fall below that floor — 6, 24, 18
and 16 committed answers — and are printed as *not scored* rather than removed,
so that the reader can see that the configurations were run and why they carry
no number. Fourteen cells are scored. Second, the response-rate gate of
Section 3.4 is a separate rule applied to the share of parsable responses, not
to coverage; the per-model response rates needed to apply it to this table are
not part of the frozen number set [SAYI YOK: per-model parsable-response rates],
so no row here is excluded on that ground.

**Table 2. Open-weight models, E1 / variant A.** Committed *n* is coverage × 473.
Cells with fewer than 30 committed answers are not scored (EK-1 §2). The last
column is the **uncorrected** 95% interval; the pre-registered correction is
applied in Table 2b.

| model | committed n | coverage | BAcc | 95% CI | CI excludes 0.5 (uncorrected) |
|---|---|---|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 6 | 0.013 | not scored | not scored | — |
| qwen2.5:32b-instruct | 82 | 0.173 | 0.6769 | [0.5833, 0.7618] | **yes** |
| gemma3:27b | 459 | 0.970 | 0.5674 | [0.5230, 0.6115] | **yes** |
| llama3.2:3b-instruct-q8_0 | 418 | 0.884 | 0.5509 | [0.5073, 0.5963] | **yes** |
| qwen2.5:14b-instruct | 97 | 0.205 | 0.5509 | [0.4839, 0.6159] | no |
| gemma3:12b | 467 | 0.987 | 0.5493 | [0.5139, 0.5836] | **yes** |
| llama3.2:3b-instruct-fp16 | 419 | 0.886 | 0.5434 | [0.4999, 0.5879] | no |
| llama3.2:3b-instruct-q5_K_M | 446 | 0.943 | 0.5318 | [0.4963, 0.5676] | no |
| qwen2.5:7b-instruct-fp16 | 24 | 0.051 | not scored | not scored | — |
| qwen2.5:7b-instruct-q8_0 | 18 | 0.038 | not scored | not scored | — |
| qwen2.5:3b-instruct-q8_0 | 311 | 0.657 | 0.5176 | [0.4915, 0.5436] | no |
| qwen2.5:3b-instruct-fp16 | 344 | 0.727 | 0.5126 | [0.4922, 0.5336] | no |
| qwen2.5:3b-instruct-q5_K_M | 244 | 0.516 | 0.5124 | [0.4898, 0.5350] | no |
| gemma3:4b | 424 | 0.896 | 0.5114 | [0.4766, 0.5456] | no |
| llama3.2:3b-instruct-q4_K_M | 316 | 0.668 | 0.5040 | [0.4663, 0.5422] | no |
| qwen2.5:3b-instruct-q4_K_M | 458 | 0.968 | 0.5029 | [0.4886, 0.5183] | no |
| llama3.2:1b | 110 | 0.233 | 0.4850 | [0.4604, 0.5000] | no |
| qwen2.5:7b-instruct-q5_K_M | 16 | 0.034 | not scored | not scored | — |

**The correction changes the count from four to two.** Eighteen configurations
are compared against the same 0.5 line, and the main pre-registration (§1)
requires a Bonferroni correction over the number of models. With 18 models and
α = 0.05, the per-cell level is 0.00278, that is, a 99.72% interval. Four models
exclude 0.5 at the uncorrected 95% level; two of them survive the correction.

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
items, under a fifth. That coverage is above the floor at which accuracy is
reported (30 committed answers), so the figure is scored and reported; it is not
a disqualification, and the pre-registration sets no minimum coverage. What the
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
pre-registration (§1.2–1.3). The second is Δ = A_com − A_abs, where A_com is E2
accuracy on the items the system committed to under E1 and A_abs is E2 accuracy
on the items it abstained from. Δ > 0 means abstention carried information about
which items the system would get wrong.

Δ is an **exploratory measure, added in Annex EK-1 §3 after the main
pre-registration**; the addendum labels it exploratory in those terms and states
that no multiple-comparison correction is applied to it. It is not part of the
confirmatory analysis and is reported as a descriptive quantity.

**Table 3. Δ (exploratory measure, EK-1 §3).**

| run | A_com | n | A_abs | n | Δ |
|---|---|---|---|---|---|
| archive A@32 run 1 | 0.6644 | 292 | 0.5470 | 181 | 0.1174 |
| archive A@32 run 2 | 0.6609 | 289 | 0.5326 | 184 | 0.1283 |
| archive A@32 run 3 | 0.7010 | 291 | 0.5220 | 182 | 0.1791 |
| A@128 (earlier day) | 0.6540 | 289 | 0.5870 | 184 | 0.0670 |
| A@32 today | 0.6576 | 295 | 0.5562 | 178 | 0.1014 |
| claude-haiku-4.5, majority | 0.5672 | 335 | 0.5255 | 137 | 0.0416 |
| claude-sonnet-5, majority | 0.6942 | 291 | 0.5385 | 182 | 0.1557 |

The two arms of the haiku row sum to 472, not 473. Δ is computed over the items
the system **committed to under E2**, since A_com and A_abs are both E2
accuracies; claim id 211 has no majority E2 verdict — the three runs disagree
and the record is marked unstable across runs — so it carries no E2 outcome and
drops out of both arms. Every other row sums to 473.

Across the hosted arm, Δ is 0.1557 for the larger model and 0.0416 for the
smaller: abstention is informative in the first case and much less so in the
second.

## 4.4 Change over time

The same configuration (claude-sonnet-5, variant A, 32-token response budget; a
token is a sub-word unit of model output) was re-run on the frozen claim set
after the archived runs, under a decision rule fixed before the run (Annex EK-7).

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
0.1416 to 0.1014, a 28% relative drop, below the archive range
[0.1174, 0.1791]. That range is wide and driven by run 3 (0.1791), so the size
of the change on the exploratory measure is uncertain even though its sign is
consistent. "Halved" is accurate for the confirmatory measure only.

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

## 4.5 The rule-based baseline

R3 is a deterministic string-matching baseline with no language model: it
resolves each claim against the corpus by literal matching. Against the raw
corpus it scored 473/473 with the earlier gold labels (v6) and 466/473 with the
revised gold labels (v7a); against the refined corpus (corpus_v2) it scored
473/473 with v7a. The refinement splits fused units, raising the corpus from
1,366 to 1,755 units (TBDY 1,208 → 1,523; remaining articles 158 → 232, which
recovers 16 annex and 58 provisional provisions).

The 7 items in the gap (1.48% of the set) are claims 246, 257, 304, 360, 364,
382 and 393 — the same seven the experts returned during gold revision. This
should not be read as independent corroboration. R3 did not produce the expert
judgement; it failed on those seven items, that is, it flagged the same seven,
and the gold correction itself rested on the same corpus observation about fused
parsing. The agreement is therefore circular and is reported as a consistency
check on the parser, not as validation of the labels.

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
passages. R3-BM25 supplies nothing to a model at all: it takes the **same three
retrieved passages** and decides by literal string containment, no model
involved. It is the ablation that isolates what the model contributes to the
retrieved evidence. (R3-BM25 is a different control from the rule baseline R3 of
Section 4.5, which matches against the whole corpus rather than the retrieved
passages; the two share a letter in the run labels and not a method.)

**Table 4. Grounded arms, qwen2.5:32b-instruct, corpus_v2 + v7a, majority of
three runs.**

| arm | evidence supplied | condition | n | coverage | BAcc | accuracy | λ |
|---|---|---|---|---|---|---|---|
| R0 | none (closed book) | E1 | 473 | 0.173 | 0.6769 | — | — |
| R0 | none (closed book) | E2 | 473 | 1.000 | 0.5493 | — | — |
| R1 | cited article, full text | E1 | 289 | 0.830 | 0.9164 | 0.9208 | 0.987 |
| R1 | cited article, full text | E2 | 289 | 1.000 | 0.8615 | 0.8720 | 0.988 |
| R2 | BM25 top-3 | E1 | 473 | 0.899 | 0.8229 | 0.8235 | 0.804 |
| R2 | BM25 top-3 | E2 | 473 | 1.000 | 0.8100 | 0.8161 | 0.829 |
| R3-BM25 | BM25 top-3, no model | — | 473 | 1.000 | 0.5938 | 0.5877 | −0.043 |

Uncertainty intervals were not produced for these arms
[SAYI YOK: bootstrap intervals, grounded arms], so the differences below are
point differences and are stated as such.

**The model adds about 22 points to the same retrieved passages.** R2 minus
R3-BM25 is +0.2292 under E1 and +0.2162 under E2. Both arms see identical
evidence — the same three BM25 passages per claim — so the difference is
attributable to the judgement step rather than to what was retrieved. This is
the main quantity of this section.

**Perfect citation is worth about 5 to 9 points over BM25.** R1 minus R2 is
+0.0935 under E1 and +0.0515 under E2: the cost of replacing an oracle pointer
to the cited article with an untuned lexical retriever. R1 is a ceiling and not
an operating point, since a deployed system does not know in advance which
article a claim ought to be checked against.

**The same model moves from 0.6769 at coverage 0.173 to 0.8229 at coverage
0.899 when the text is supplied.** The closed-book and grounded figures come
from one model on one claim set, so the comparison is within-system: the
closed-book arm commits to 82 of 473 items, the BM25-grounded arm to 425, and it
is more accurate on the larger set than the closed-book arm was on the smaller
one. Under forced choice the same contrast is 0.5493 against 0.8100.

### 4.6.3 What the retrieval figure does and does not bound

R2's balanced accuracy of 0.8229 was obtained while the retriever placed the
cited unit in the context for only 0.2734 of the article-attributing claims.
The retrieval recall is therefore **not** a ceiling on the grounded arm's
accuracy, and an earlier statement in this work that a grounded arm inherits the
retriever's ceiling is withdrawn: it was a prediction, and the measurement
contradicts it. At least two mechanisms could produce the observed result — the
retrieved passages are often sufficient to judge a claim even when they are not
the cited unit, or the model completes the judgement from parametric knowledge —
and this experiment does not separate them. Attributing R2's accuracy to
retrieval alone would be unsupported. Whether a tuned retriever, a larger k, or
a dense or hybrid retriever changes the picture was not measured.

**Run-to-run behaviour.** Three runs were executed per arm as a precaution, and
they were not needed for this model: within-arm agreement is 1.0000 for both R1
and R2 (three pairwise comparisons, 1,524 calls per run), that is, fully
deterministic output. An earlier observation of non-determinism under grounded
prompting (defect log #29, 17/20 agreement) belongs to llama3.2:3b, which is
also the model that dropped the output-format instruction (defect log #28). Both
findings are properties of that one model, not of grounded prompting, and the
claim that local grounded arms require three runs is narrowed accordingly: for
qwen2.5:32b-instruct a single run reproduces the result exactly, as measured.

---

# 5 Discussion

## 5.1 The open-weight arm is a coverage–accuracy trade-off, not a uniform failure

Eighteen locally hosted models produced a scorable cell under the abstention-permitted condition (E1) with prompt variant A. How many of them can be separated from chance depends on whether the multiplicity correction the pre-registration specified is applied, and we report both counts because the difference is material.

Read one cell at a time with an uncorrected 95% cluster-bootstrap interval, four models lie entirely above 0.5: `qwen2.5:32b-instruct` at 0.6769 [0.5833, 0.7618] with coverage 0.173, `gemma3:27b` at 0.5674 [0.5230, 0.6115] with coverage 0.970, `llama3.2:3b-instruct-q8_0` at 0.5509 [0.5073, 0.5963] with coverage 0.884, and `gemma3:12b` at 0.5493 [0.5139, 0.5836] with coverage 0.987. But the main pre-registration (§1) fixes Bonferroni correction over the number of models, and eighteen models at α = 0.05 give 0.00278 per cell, that is a 99.72% interval. Under that correction two models remain: `qwen2.5:32b-instruct`, lower bound 0.5349, and `gemma3:27b`, lower bound 0.5017 (4,000 resamples, clusters = law + article, seed 42). `llama3.2:3b-instruct-q8_0` (0.4878) and `gemma3:12b` (0.4915) no longer exclude chance. The second surviving model clears 0.5 by 0.0017 of balanced accuracy, which is a margin no engineering decision should rest on; we report it as surviving the stated test, not as a demonstrated capability.

The two survivors sit at opposite operating points. `qwen2.5:32b-instruct` reaches an interval that overlaps the hosted `claude-sonnet-5` value of 0.6920 [0.633, 0.750], but it commits on 0.173 of the claims — 82 of 473 — declining roughly five items in six, and its accuracy is measured only on the sixth. That cell is scored rather than withheld: the reporting rule adopted in the pre-registration addendum (EK-1 §2) requires at least 30 committed items, and 82 is above it. The 80% gate in the pre-registration applies to the parsable-response rate, not to the commitment rate, and commitment rate is the dependent variable of this study, so a low-coverage cell is a result and not a protocol violation. `gemma3:27b`, by contrast, answers 0.970 of the claims — 459 of 473 — and sits about seven points above chance on nearly the whole set.

The engineering reading is a trade-off between how much of the workload a system will take on and how well it does on that share. It is not an absence of signal, and it is not a demonstration of usable performance either. Coverage also disciplines how the point estimates should be read: `qwen2.5:7b-instruct-q4_K_M` carries the highest point estimate in the table, 0.7500, at coverage 0.013, with an uncorrected interval of [0.5000, 0.8750]. A score computed over a handful of committed items is not a capability claim, and it is one of the reasons the correction matters: with eighteen cells examined, the largest uncorrected value in the table is the one most likely to be a sampling artefact.

## 5.2 Abstention frequency held; abstention selectivity fell

Comparing the three archived hosted runs (variant A, 32-token budget) with the run repeated on 28.08.2026 under the same settings, the number of abstentions is close to unchanged: 181, 184 and 182 in the archive against 178 today, a relative decrease of 2.2%. What changed is what those abstentions were worth, and the two available measures of that disagree in size.

The condition contrast BAcc(E1) − BAcc(E2) — how much the option to say "not sure" buys in balanced accuracy — is a confirmatory measure of the main pre-registration, and it falls from an archive mean of 0.0762 (range [0.0735, 0.0784]) to 0.0332, a relative drop of 56%. The selectivity measure Δ = A_committed − A_abstained, which asks whether the items a model declined are ones it would have got wrong anyway, falls from an archive mean of 0.1416 to 0.1014, a relative drop of 28%.

**Status of Δ.** Δ is an *exploratory* measure, added in the pre-registration addendum (EK-1 §3) after the main pre-registration and after the run had completed, though before any accuracy metric was computed. The addendum marks it exploratory and applies no multiple-comparison correction to it, and we follow that. It is not one of the confirmatory analyses of the main pre-registration, and it should not be read as a pre-specified test. We report it because it isolates a quantity the confirmatory contrast cannot — whether the abstained items are the ones the model would have failed — and because reporting only the confirmatory contrast would leave that question unanswered.

Both measures are positive today and both moved in the same direction; the description "halved" applies only to the first. The archive Δ range is wide, [0.1174, 0.1791], with the third run at 0.1791, so the width of the reference band limits how firmly the size of the decrease can be stated. We report both because reporting only the larger one would overstate the effect.

For a building-inspection workflow this pattern matters more than either number alone. A tool whose abstention rate is stable but whose abstentions have become less informative looks unchanged on a dashboard that monitors abstention rate. The "send this one to a human" signal remains visually intact while carrying less of the meaning it was accepted for. An operator monitoring only the abstention count would not see this change; an operator recomputing Δ against a retained gold subset would.

## 5.3 Re-qualification: a fixed test set, a changed component

One result bears directly on procurement and maintenance practice: a system qualified once against a frozen test set may not stay qualified. The same 473 claims, the same gold labels, the same variant A prompt, the same 32-token budget and the same hosted model name yield archive balanced accuracies of 0.6832, 0.6796 and 0.6986 — a run-to-run range of [0.6796, 0.6986] — against 0.6422 today, outside that range. Under the forced-choice condition the archive range is [0.6012, 0.6220] and today's value 0.6090 falls inside it. The movement is concentrated in the condition where the model is allowed to abstain, which is consistent with §5.2.

**Choice of comparison baseline.** Two baselines are available and they answer different questions. The cluster bootstrap over claims, [0.633, 0.750], asks whether a measured value would generalise to other claims drawn from a comparable population; the claim set is treated as variable, and today's 0.6422 falls inside it. The run-to-run range, [0.6796, 0.6986], asks whether behaviour changed on *this* set of 473 items; the claim set is held fixed. The version question fixes the item set by construction, so the run-to-run range is the matching baseline. We nonetheless report the bootstrap interval, because a reader who prefers the generalisation framing should be able to read the result in those terms: behaviour on the frozen set moved beyond previously observed run-to-run variation, while remaining inside the interval one would expect across resamples of comparable claim sets.

**What we can and cannot say about our own side.** The archived runs were produced with `f4_api.py`; the repeated run was produced with the regenerated `f4_api_v2.py`. The variant A prompt strings are byte-identical across the two (E1 `8a8ef386b0b2b619`, E2 `64dedda000ce465e`), but that identity was re-derived from the archived source code: the archived run records carry no script hash at all. The two v2 runs do carry hashes (`11a5d5a3b7b7af20` for the 128-token run, `002df510703fb0a7` for today's), and they differ, because the file was regenerated from patches. The statement "the harness is the same" therefore rests on source inspection rather than on recorded provenance, and we cannot rule out a difference that reading the source did not surface. This is a real limit on the inference, and it is the reason the finding is framed as a re-qualification requirement rather than as a measurement of a vendor release.

The practical recommendation follows from the weaker reading as well as the stronger one. Qualification of an LLM-assisted checking aid is a dated statement about a component that can change outside the operator's control. Building inspection already has vocabulary for this — periodic re-verification of measuring instruments, re-qualification of a procedure after a change to any element of it. The corresponding practice here is to retain a frozen item set, re-run it on a schedule, and report a run-to-run range rather than a single figure.

## 5.4 Supplying the governing provision changes the operating point

The closed-book results above are a property of one deployment choice, not of the task. To separate the two, the grounded arms specified in EK-4 were run on `qwen2.5:32b-instruct` — the local model with the widest margin over chance after correction — over the refined corpus (corpus_v2, 1,755 units) with the audited v7a gold, three runs scored by majority vote, a 128-token output budget, and 0 of 1,524 responses truncated in each run. The figures are in §4.6; the readings below refer to them.

Four quantities set the scale. Closed book (R0), the model reaches balanced accuracy 0.6769 at coverage 0.173 under E1 and 0.5493 at full coverage under E2. Given three BM25-retrieved passages (R2), it reaches 0.8229 at coverage 0.899 under E1 and 0.8100 at full coverage under E2. Given the full text of the cited article (R1, defined on the 289 article-attributing claims), 0.9164 at coverage 0.830 under E1 and 0.8615 at full coverage under E2. A string-containment rule with no language model, applied to the *same* three retrieved passages (R3bm25), reaches 0.5938 at full coverage. The information index λ = accuracy(P1) + accuracy(P5) − 1, which is 0 for a system that cannot separate a correctly cited provision from a mis-attributed one whatever its raw accuracy, is 0.987 and 0.988 for R1, 0.804 and 0.829 for R2, and −0.043 for R3bm25.

Three readings follow.

**The language model contributes over string matching on identical evidence.** R2 and R3bm25 receive the same retrieved passages; the difference is that R2 asks a model to judge them and R3bm25 applies a containment rule. The gap is +0.2292 in balanced accuracy under E1 (0.8229 versus 0.5938) and +0.2162 under E2 (0.8100 versus 0.5938). The λ figures make the same point in a form that is harder to reach by chance: string matching over these passages scores −0.043, indistinguishable from no information on the P1-versus-P5 contrast, while R2 scores 0.804 and 0.829. Whatever the retrieved passages contain, a lexical rule cannot use it and the model can.

**A perfect citation is worth about five to nine points over BM25, but the two arms are not scored on the same items.** R1 exceeds R2 by 0.0935 under E1 and 0.0515 under E2. This is the cost of using an untuned retriever instead of the cited article — but R1 is defined only on the 289 article-attributing claims while R2 covers all 473, so the difference confounds evidence quality with item composition and should be read as indicative rather than as a clean contrast.

**Retrieval recall does not bound grounded accuracy, and we measured this rather than assuming it.** BM25 at k = 3 places the cited unit among the retrieved passages for 79 of 289 article-level claims, a recall of 0.2734. It would be natural to infer that a grounded arm built on that retriever inherits 0.2734 as a ceiling. That inference is wrong: R2, built on exactly those retrieved passages, reaches balanced accuracy 0.8229 under E1 and 0.8100 under E2. Recall measures whether the *cited* unit was retrieved; it does not measure whether the retrieved units were sufficient to judge the claim. Two mechanisms could produce this and our design does not separate them: the retrieved passages may support a verdict without being the cited unit — much Turkish regulatory text repeats near-identical phrasing across articles, so a neighbouring provision often settles a numeric or currency claim — or the model may be completing from parametric knowledge it also displayed in the closed-book arm. We report the gap between recall and end-to-end accuracy as measured and unattributed. Any claim that R2's performance is retrieval-driven would require an ablation we did not run.

**Determinism.** Within-arm agreement for `qwen2.5:32b-instruct` was 1.0000 in both R1 and R2 across the three pairwise run comparisons, at 1,524 calls per run: the arm is fully deterministic at this setting, and majority voting over three runs changed nothing for this model. This narrows a finding that would otherwise have been stated too broadly. The non-determinism we recorded elsewhere (17 of 20 items agreeing across runs) belongs to `llama3.2:3b`, which was also the model that dropped the output-format instruction. Both observations are properties of that one model, not of grounded prompting or of local serving in general. We therefore do not recommend three-run majority voting as a general requirement for local grounded arms; we recommend measuring within-arm agreement per model and voting only where it is below 1.

**What this changes about deployment.** The closed-book operating point for this model — balanced accuracy 0.5493 at full coverage under E2, or 0.6769 on the 17% of items it will speak about under E1 — does not support use as a screening aid on Turkish building regulation. The same model, same weights, same host, given the governing article or even three lexically retrieved passages, operates at 0.81 to 0.92. The design recommendation that follows is not "use a larger model" and not "do not use language models here": it is that the provision must be supplied. An architecture that asks a model to recall the Development Law is being asked to do the one thing this benchmark measures it failing at, and the fix is a retrieval or citation-resolution step that puts the text in front of it, not a better recall.

## 5.5 The rule baseline, and one circularity we cannot remove

The rule-based baseline R3, which uses no language model, scores 473/473 on the refined corpus with the v7a gold and 466/473 on the raw corpus with the same gold. A negative control that shuffles the claim-to-rule pairing across five seeds averages 0.5315, so the score is not an artefact of the scoring path. The seven items R3 fails on the raw corpus (1.48% of the set) are the seven that the expert panel had frozen: 246, 257, 304, 360, 364, 382, 393. This convergence should not be described as independent replication. R3 did not generate those labels; it *failed* on them, which is to say it marked the same seven items. Moreover, the gold correction and the R3 failure both trace to the same corpus observation — the merged-clause parsing that the refined corpus repairs. The two views are consistent, but they are two views of one observation, and we report the agreement as a consistency check rather than as corroboration by an independent instrument.

R3's 473/473 is also not evidence that the task is easy. R3 reads the claim text and applies rules written against the corpus the claims were generated from; it is a control on the scoring path, not a competitor. R3bm25 (§4.6) is the honest lexical comparison — a string rule with no privileged knowledge of how the claims were built — and it scores 0.5938.

A related circularity applies to the currency probe (P6): the corpus amendment-year field and the claim-set amendment note derive from the same regular expression applied to the same PDFs. The independent channel is the check against official consolidated text on mevzuat.gov.tr, which matched on 20 of 20 sampled items with 0 mismatches, and whose article counts reproduced our parser exactly (3194: 49, 4708: 15, 6331: 39). That check covers three laws only.

## 5.6 What would count as acceptable

Calling a system "not usable" requires a threshold, and this study did not establish one. A screening aid inside a building-inspection workflow would plausibly be judged on three quantities: the share of incorrect statements about the code that pass through unflagged, the share of the workload still requiring human reading, and whether the tool's own uncertainty signal can be trusted enough to route work. Our design measures analogues of the first two — balanced accuracy and coverage — but it does not measure the cost asymmetry between a missed error and a false alarm in a real office, and without that asymmetry a numeric pass mark cannot be set from these data. We therefore state the operating points and leave the threshold to the adopting organisation.

What can be said concretely, in closed book: the best hosted configuration observed here commits on 0.615 of items at balanced accuracy 0.6920 with an expected calibration error of 0.0373, meaning its stated confidence tracks its actual hit rate closely — the way a gauge that reads 5 mm when the true gap is 5 mm is in calibration. Its forced-choice counterpart reaches full coverage (1.000) at balanced accuracy 0.6242 with ECE 0.0634. The second hosted model reaches 0.5298 [0.489, 0.570] at coverage 0.710 with ECE 0.2263 — an interval that includes 0.5 and a confidence signal far from calibrated. Any of these leaves a substantial residue of items for human review.

Grounding moves the numbers into a different band but does not by itself settle the question. R2 at 0.8229 (E1, coverage 0.899) and 0.8100 (E2, coverage 1.000) still misses roughly one claim in five, and a workflow that treats an 18–19% error rate on regulatory statements as acceptable would have to say why. What the grounded arms establish is where the engineering effort belongs: on getting the provision in front of the model and on measuring the retriever, rather than on selecting among closed-book models. An organisation with a threshold in mind should apply it to a grounded configuration measured on its own document set, since the retrieval component — the part these results show to matter and the part we tested least — is the one that will differ most between deployments.

# 6 Limitations

**Single run against three.** The repeated hosted run is one run; the archive baseline is three. A single value cannot itself establish a range, so the drop to 0.6422 is a comparison of one observation against a previously measured band, not a comparison of two bands.

**What "version" does not mean here.** We observed a change in the behaviour of a hosted endpoint on a fixed item set between two dates. We did not observe, and were not told, any vendor release, weight change or serving change; no vendor version identifier was recorded. "Version drift" is our label for a behavioural difference, not a claim about the provider's internals.

**Provenance of the harness comparison.** As set out in §5.3, the archived runs carry no script hash, and the identity of the variant A prompts was re-derived from archived source rather than read from run records.

**Δ is exploratory.** The selectivity measure Δ was added in the pre-registration addendum (EK-1 §3) after the main pre-registration and after the run had completed, though before any accuracy metric was computed. The addendum itself marks it exploratory and applies no multiplicity correction to it. It carries the evidential weight of an exploratory analysis, not of a pre-specified test, and the paper's confirmatory abstention result is the condition contrast BAcc(E1) − BAcc(E2).

**Deviation from the pre-registered coverage rule.** The main pre-registration (§3) declared that a cell answering fewer than 80% of items would not be scored. The addendum (EK-1 §1) redefined that threshold to apply to the parsable-response rate rather than to the commitment rate, on the ground that commitment rate is the dependent variable and gating on it would classify the measured behaviour as non-compliance. The redefinition was made after the run completed and before any accuracy metric was computed, and it rests on the definition of the two rates rather than on what the results showed. It is nonetheless a deviation from the frozen protocol, and the addendum states that it must be declared in the paper. Two models are excluded by the corrected rule on response rate (`llama3.2:1b`, `llama3.2:3b-instruct-q4_K_M`), both because they echo the claim text instead of emitting a label.

**Multiplicity leaves two models, one of them marginal.** After the pre-registered Bonferroni correction over eighteen models, two open-weight configurations exclude 0.5, and the second does so by 0.0017 (`gemma3:27b`, lower bound 0.5017). Conclusions about the open-weight arm should be read at that strength. The uncorrected count of four is reported alongside so that a reader who prefers per-cell inference can see both.

**The grounded arms cover one model.** R0, R1, R2 and R3bm25 were run on `qwen2.5:32b-instruct` only. `gemma3:27b`, the other model surviving the correction and the one with near-full closed-book coverage, was not run in any grounded arm, so we cannot say whether the closed-book-to-grounded gain reported in §5.4 generalises across local models, across model sizes, or to the hosted arm. The grounded results are one model on one corpus.

**R2's success is not decomposed.** BM25 recall on the article-attributing subset is 0.2734 while R2 reaches balanced accuracy 0.8229; the two mechanisms that could explain the difference — sufficient but non-cited passages, and parametric completion — were not separated by an ablation. Reported as measured.

**One untuned retriever.** BM25 at k = 3 over 1,755 units is the only retrieval configuration tested. Its recall of 0.2734 characterises that configuration; and as §5.4 shows, that recall figure does not translate into a bound on grounded accuracy in either direction.

**Determinism is a per-model measurement.** Within-arm agreement of 1.0000 was measured for `qwen2.5:32b-instruct` in R1 and R2. It is not a property of local serving generally: `llama3.2:3b` agreed on 17 of 20 items across runs in the same setting.

**Independent currency verification is partial.** The check against official text covers 3194, 4708 and 6331. The building-inspection implementation regulation (YDUY) was not covered, leaving 43 currency claims without independent verification.

**Mechanism unmeasured.** We report what changed in the outputs; we did not measure why. Whether the shift in abstention selectivity reflects decoding, serving, prompt handling or something else is outside what these runs can determine.

**Two effect sizes.** The condition contrast and Δ move in the same direction but by different relative amounts (56% and 28%), and the archive Δ band is wide. Readers should treat the magnitude of the selectivity decrease as uncertain.

**Suppressed cells.** In 8 of 56 cells fewer than 50 confidence-bearing records were available, and calibration and Brier figures were suppressed there rather than reported at low precision.

**Repository history was reconstructed.** Access to the original machine was lost and the repository was rebuilt from packaged archives (`REKONSTRUKSIYON.md`). File contents are verifiable against archive checksums — the sealed claim generator carries an identical SHA-256 in two independently packaged archives, and 31 of 31 files in the handover package match byte for byte — but commit timestamps are not: that each pre-registration was written before the run it governs cannot be demonstrated from git history, which begins on 27.08.2026. The dates written inside the pre-registration texts and the file modification times inside the archives support the ordering; they are weaker than a commit stamp, and we do not present them as equivalent.

# 7 Conclusions

RUHSAT-Bench evaluates 473 claims about six frozen Turkish regulatory documents under two response conditions, with gold labels adjudicated by two domain experts (decision-level Cohen's κ = 1.000 [1.000, 1.000], quality-level κ = 0.860 [0.759, 0.961], n = 150).

Four results carry over to practice.

First, the open-weight closed-book arm is a coverage–accuracy trade-off rather than a flat failure, and how much of it survives depends on the correction. Of eighteen local configurations, four exclude chance on uncorrected per-cell intervals; after the pre-registered Bonferroni correction over eighteen models, two do — `qwen2.5:32b-instruct` (lower bound 0.5349) at coverage 0.173, and `gemma3:27b` (lower bound 0.5017, a margin of 0.0017) at coverage 0.970. There is signal in the local arm, and at that strength it does not support deployment.

Second, abstention frequency and abstention quality can move independently. Across the archived and repeated hosted runs the abstention count fell 2.2% while the confirmatory condition contrast fell 56% and the exploratory selectivity measure Δ fell 28%. A deployment that monitors abstention rate alone would not have seen this.

Third, a hosted model's behaviour on a frozen item set moved outside its own previously measured run-to-run range while the harness was, as far as source inspection can establish, unchanged. Qualifying such a tool is therefore a dated statement, and it calls for a retained frozen item set and scheduled re-qualification, in the same sense in which a torque wrench carries a calibration expiry.

Fourth, the closed-book deficit is a deficit of the architecture, not of the task. Given the cited article, `qwen2.5:32b-instruct` reaches balanced accuracy 0.9164 (E1, coverage 0.830) and 0.8615 (E2); given three BM25-retrieved passages, 0.8229 and 0.8100; asked the same claims with nothing supplied, 0.6769 on the 17% of items it will answer and 0.5493 when forced. A string-matching rule over the *same* retrieved passages reaches 0.5938, so roughly 22 points of the grounded result come from the model's judgement of the evidence rather than from the evidence being present. The practical implication is direct: do not deploy a closed-book configuration against Turkish building regulation, and put engineering effort into supplying the governing provision. We add two cautions to that recommendation — the grounded arms were run on one model, and the retriever's recall of 0.2734 on the article-attributing subset shows the retrieval component is the least examined part of the pipeline, and it is the component a deployment would have to characterise against its own documents.

We do not set a numeric acceptance threshold, because the cost asymmetry that would define one was not measured. We report operating points instead, together with the limits under which they should be read: one repeated run, one untuned retriever, grounded arms on a single model, partial independent currency verification, an unmeasured mechanism, a deviation from the pre-registered coverage rule that we declare in §6, and a repository whose commit history was reconstructed.

---
