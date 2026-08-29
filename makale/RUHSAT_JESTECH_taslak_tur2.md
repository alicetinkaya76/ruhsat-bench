# RUHSAT-Bench — JESTECH taslağı (2. tur)

> **UYARI — BU TASLAK GÖNDERİLEMEZ.** İki denetim de bloke etti.
> Düzeltilecekler `makale/DUZELTME_LISTESI.md` ve `sonuclar/MAKALE_SAYILARI.txt`
> (D1/D2/D3 bölümü) içinde. Özellikle: Δ 'ön-kayıtlı' DEĞİL, Bonferroni
> sonrası 4 değil 2 model, kapsam-eşiği iddiası ön-kayda aykırı, üç atıfta
> yıl kayması. Bu dosya ÇERÇEVEYİ okumanız için verilmiştir.

# 1. Introduction

Building permitting and inspection in Türkiye rest on a compact stack of binding instruments: the Development Law (No. 3194), the Building Inspection Law (No. 4708) together with its implementing regulation (YDUY), the Occupational Health and Safety Law (No. 6331) with the risk-assessment regulation, and the Turkish Building Earthquake Code (TBDY 2018). Much of the daily work in an inspection office is documentary rather than analytical: does an obligation sit in Law 4708 or in its regulation, is the article a file cites the article that actually carries the rule, was that article amended in the year an applicant states. Each such question has a checkable answer in a published text.

Automating these checks is a long-standing goal in construction informatics. Rule-based model checking encodes provisions as machine-verifiable constraints (Eastman et al., 2009; Solihin and Eastman, 2015), while NLP-driven extraction attempts to recover those constraints from the regulatory text itself (Zhang and El-Gohary, 2016; Zhou and El-Gohary, 2017). Both lines assume the governing text is in hand. Large language models (LLMs) offer a different proposition: an answer produced from model parameters with no document supplied. We refer to this as the **closed-book** setting — the system is asked about a provision without being shown it, the way a person answers from memory. It is also one of the ways these systems are in fact consulted, when an engineer types a regulatory question into a chat window and acts on what comes back (Dahl et al., 2024; Magesh et al., 2025). [ATIF GEREKLI: LLM-based automated compliance checking in construction, 2023–2025]

**Terminology.** A model *abstains* when it returns "I am not sure" instead of a verdict; *coverage* is the fraction of claims on which it commits to a verdict, so coverage 1.000 means it always answers. *Balanced accuracy* averages accuracy on true claims with accuracy on false claims, so a system that answers "false" to everything scores 0.5 regardless of how many false claims the set happens to contain. *Calibration* is the correspondence between stated confidence and observed correctness, in the sense in which a pressure gauge is calibrated against a reference: a gauge that reads 6 bar should mean 6 bar, and a model that reports 90 % confidence should be right on about 90 % of such items (Guo et al., 2017; Jiang et al., 2021). *Expected calibration error* (ECE) is the average gap between the two, so smaller is better (Naeini et al., 2015). Confidence intervals are obtained by *bootstrap* — repeatedly resampling the evaluated claims and reading the spread of the resulting scores — clustered by statute and article, so that claims from the same article are resampled together.

**RUHSAT-Bench.** We assemble 473 claims over the six documents above, indexed against a corpus of 1755 regulatory units, with a gold label distribution of 223 true and 250 false. Claims are organised in six probe families: direct assertion (163), numeric value (37), cross-reference (121), currency of amendment (120), anachronism (19), and fabricated provision (13). Each system is run under two conditions: abstention-permitted (E1) and forced binary choice (E2). Gold labels passed a two-coder expert audit (Cohen's κ = 1.000 on the decision, 0.860 on quality), and the currency family was checked against official HTML on mevzuat.gov.tr, where 20 of 20 sampled claims agreed.

**What would count as usable?** A benchmark number is not a verdict on its own; declaring a system unusable requires a threshold, and we could not locate a defensible one. Turkish building-inspection practice sets no accuracy requirement for advisory software, and the compliance-checking literature reports system performance without stating an acceptance level. We therefore do not issue an absolute verdict. Section 2.2 sets out the shape such a criterion would need to have — which is, we argue, a criterion on the abstention behaviour rather than on accuracy alone — and our results are reported so that a reader who does have a threshold in mind can apply it.

**Contributions.**

1. A regulatory benchmark for Turkish construction law with auditable provenance: every reported figure is regenerated from committed script outputs, and the claim set, gold labels and expert-audit record are released with the code.
2. A measured **coverage–accuracy trade-off** among open-weight models rather than a blanket failure. Of the 18 locally hosted models with a scorable E1 cell under prompt variant A, four have 95 % bootstrap intervals excluding 0.5: qwen2.5:32b-instruct at balanced accuracy 0.6769 [0.5833, 0.7618] but coverage 0.173, and gemma3:27b (0.5674 [0.5230, 0.6115], coverage 0.970), llama3.2:3b-instruct-q8_0 (0.5509 [0.5073, 0.5963], coverage 0.884) and gemma3:12b (0.5493 [0.5139, 0.5836], coverage 0.987) at near-full coverage. The 32B model's interval overlaps the hosted claude-sonnet-5 (0.6920 [0.633, 0.750], coverage 0.615), but it reaches that score by answering roughly one claim in six and falls below the minimum-coverage threshold fixed in the pre-registration, so it is reported as non-compliant with the scoring protocol rather than as a competitive system. The three near-full-coverage models sit some 5–7 points above chance. Which of these is preferable depends on the workflow, and Section 2.2 argues the choice cannot be made by accuracy alone.
3. An account of abstention as a measured quantity rather than an assumed safety feature, using both the pre-registered selective-prediction contrast and the coverage-conditional accuracy difference, and reporting the two effect sizes separately because they do not agree in magnitude.
4. A re-qualification result: on a frozen claim set and prompts we verified to be byte-identical, a re-run of one hosted configuration falls outside the archived run-to-run range while remaining inside the archived clustered bootstrap interval. We report both baselines and justify which one answers the version question (Section 5).
5. A retrieval measurement bounded to what was tested: one untuned BM25 retriever — BM25 being a standard ranking function that scores a passage by how many of the query's *tokens* (word-like units) it contains, weighted by their rarity (Robertson and Zaragoza, 2009) — recovered 79 of 289 article-level citations at k = 3 (0.2734) on this corpus. This bounds what that retriever contributes here; it is not a claim about retrieval-augmented systems in general.

# 2. Motivation

## 2.1 Fail-safe and fail-silent behaviour

Safety engineering distinguishes a component that fails into a defined safe state from one that fails while continuing to emit plausible output. A load cell that saturates and reads zero announces its own failure; one that drifts by 15 % does not. Functional-safety practice treats the second class as the harder problem, because the downstream process has no signal that anything is wrong (IEC 61508).

An LLM asked a closed-book regulatory question is a candidate fail-silent component. It returns a fluent verdict with a confidence figure attached, in the same register whether the provision is one it can reproduce or one it has never encountered. If the confidence figure tracked correctness, the component would be fail-safe by construction: an inspector could route low-confidence items to manual review. This is precisely the promise of selective prediction, where a classifier is permitted to reject inputs it cannot handle (Chow, 1970; El-Yaniv and Wiener, 2010; Geifman and El-Yaniv, 2017), and of work asking whether language models know what they know (Kadavath et al., 2022; Lin et al., 2022; Xiong et al., 2024).

Whether that promise holds for regulatory text is an empirical question, and it is the question this benchmark is built to answer. It cannot be answered by accuracy, because accuracy conditions on the items a model chose to answer. A system that abstains on 83 % of claims and a system that answers all of them are not comparable on accuracy alone; both numbers are reported here alongside coverage for that reason.

## 2.2 An acceptance criterion has to be about abstention

Consider a building-inspection workflow in which a model pre-screens claims in a permit file and flags the doubtful ones for an engineer. The quantity that governs whether this saves work is not overall accuracy: it is whether the flagged set is enriched for errors. If abstention is uninformative — if the model declines items it would have got right at the same rate as items it would have got wrong — then the flags carry no triage value and the engineer must check everything regardless, at which point the screening step costs time without removing any.

This gives the shape of a usable acceptance criterion: a stated coverage level, an accuracy on the covered items, and evidence that accuracy on the abstained items is materially lower. Calibration enters the same criterion, because a confidence figure is only actionable if it means what it says; a model whose ECE is large is reporting a gauge reading that has not been calibrated against anything. We do not fix numeric values for these three quantities, because we have no principled basis on which to fix them for Turkish inspection practice, and we avoid statements of the form "this system cannot be used". We report the three quantities so that an organisation with its own tolerance can evaluate them. [ATIF GEREKLI: risk-based acceptance thresholds for decision-support software in construction]

## 2.3 Benchmarks expire, so systems have to be re-qualified

A calibration certificate for a torque wrench carries an expiry date; the instrument is re-qualified on a schedule because its behaviour drifts. Hosted LLMs are updated behind a stable model identifier, and their behaviour on a fixed task has been observed to change over time (Chen et al., 2024). A benchmark score for such a system is therefore a measurement at a date, not a property of the name.

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
| Balanced accuracy (BAcc) | The mean of accuracy on the true claims and accuracy on the false claims. 0.5 is the level reached by any strategy that ignores content — always answering "true", always "false", or answering at random. |
| Calibration / ECE | Whether a stated confidence matches observed correctness, in the sense in which a measuring instrument is calibrated: a gauge marked 95 must be right on about 95 of every 100 readings. Expected calibration error (ECE) is the average gap between the stated figure and the observed rate; 0 is a perfectly calibrated instrument, and a large ECE means an individual reading cannot be relied on even when the average happens to be correct. |
| Bootstrap | An uncertainty interval obtained by repeatedly resampling the data. We resample clusters, not single claims: a cluster is one (law, article) pair, 10,000 resamples, so that claims drawn from the same article are kept together. |
| BM25 | A classical keyword-scoring retrieval function that ranks text units against a query. One untuned retriever, used at k = 3. |
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

## 3.4 Conditions, prompt variants and runs

Every claim is asked twice. **E1** allows abstention (true / false / not sure); **E2** forces a binary choice. Two system-prompt variants (A and B) were written for each condition; A is primary and B is a controlled re-wording. Output budget is part of the run label (A@32, A@128, B@128). For the hosted models, extended thinking was disabled so that the task matched the local arm, and this was verified per response rather than assumed; each hosted configuration was run three times and scored by majority vote. Cells whose parsable-response rate falls under the pre-registered gate are reported as non-compliant instead of being scored, and accuracy-type metrics are suppressed in cells with too few committed answers. Under the same rule, ECE and Brier are suppressed in 8 of 56 cells that carry fewer than 50 confidence-bearing records.

## 3.5 Grounded arms

Closed-book performance is a lower bound on an architecture, not on the task, so three grounded arms were pre-registered (EK-4) against the closed-book arm R0.

| Arm | n | Evidence supplied | Role |
|---|---|---|---|
| R0 | 473 | none (closed-book) | baseline |
| R1 | 289 | full text of the cited article | ceiling, not a deployable estimate |
| R2 | 473 | BM25 top-k (k = 3) over the 1,755 units | retrieval-plus-judgement |
| R3 | 473 | none; deterministic string rules, no model | non-neural control |

R1 is restricted to 289 claims by the data, not by choice: the remaining 184 cite only a document, and document texts run from roughly 17k to 871k characters. R2's retrieval component is reported separately from its judgement component, as required by the pre-registration: BM25 at k = 3 places the cited unit in the retrieved set for 79 of 289 article-level claims (recall 0.2734) and misses 210. That figure characterises this single untuned retriever at this k on this corpus; it is not a statement about what retrieval can achieve in general.

R3 is blind by construction — it reads only the claim identifier and the claim text, and asserts this at start-up — and has no abstention option, so it is excluded from the calibration comparisons. Its matching rules were fixed before the run. Its behaviour is corpus-dependent in an informative way: with the refined corpus and the audited gold labels it decides 473/473 claims correctly, while the raw corpus paired with the same labels gives 466/473, and the 7 claims that separate the two (1.48% of the set) are exactly the 7 whose gold labels the expert audit had frozen. A shuffled-pairing negative control over five seeds returns 0.5349, 0.5349, 0.5159, 0.5370 and 0.5349 (mean 0.5315), establishing that the rule set is exploiting the pairing rather than a surface regularity.

Because R3's amendment-history channel is reconstructed from the same annotations the claims were generated from, the check is circular in the sense that it verifies channel presence rather than legal correctness. A sample of 20 P6 claims was therefore checked against official consolidated HTML text: 20 agreed, 0 disagreed, and our parser reproduced the official article counts exactly (3194: 49, 4708: 15, 6331: 39). The verification frame covers only 3194, 4708 and 6331; YDUY was outside it, so 43 P6 claims remain unverified against an independent source.

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

The second pass was designed to reach the class the first cannot: a sentence that, lifted from its article, no longer says what the article says. Raters opened the source and read the whole article. One consequence must be stated plainly, because it bears on how the R3 result above may be read. The 7 gold corrections were proposed after a corpus observation — the clause-merging defect — and the same observation motivated the refined corpus; the expert step confirmed the mis-attribution on those items but did not generate the labels independently, and the R3 arm failed on those same 7 items rather than identifying them from scratch. The agreement between corpus repair, gold repair and R3 therefore contains a circular component, and the two are not independent confirmations of each other.

## 3.7 Outcome measures: two of them, reported together

Abstention is the dependent variable of this study, and it can be summarised in two ways that answer different questions. Both are reported everywhere, because they do not agree in magnitude.

| Measure | Definition | Status | Question it answers |
|---|---|---|---|
| BAcc(E1) − BAcc(E2) | Difference in balanced accuracy between the abstention-permitted and forced conditions, over the full claim set | Confirmatory (main pre-registration, §1.2–1.3) | How much does the score improve when the model is allowed to stay silent? |
| Δ = A_com − A_abs | A_com is E2 accuracy on the items the model committed to in E1; A_abs is E2 accuracy on the items it abstained from in E1 | Pre-registered exploratory (EK-1 §3) | Does the silence carry information — is the model worse on precisely the items it declined? |

The first quantity mixes two effects, since removing low-accuracy items from the denominator raises the score even if the choice of items is arbitrary. Δ isolates the second effect: Δ > 0 means abstention is selective, Δ ≈ 0 means the model is merely reticent. Reporting only one of them would let an author choose the larger effect; we therefore give both, together with coverage, since a balanced accuracy obtained on a small fraction of the claim set is not the same object as one obtained on nearly all of it, and the two must be read side by side.

Uncertainty on any single configuration is a cluster bootstrap with 10,000 resamples, clusters being (law, article) pairs.

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
it must choose true or false. All runs reported here are **closed-book**: the
system answers from what it already contains, with no document text supplied,
the equivalent of an examination taken with the code book shut. **Coverage** is
the fraction of the 473 claims on which a system commits instead of abstaining.
**Balanced accuracy** (BAcc) is the mean of accuracy on true claims and accuracy
on false claims, so 0.5 is the value of a coin flip regardless of the class mix.
Intervals are 95% clustered **bootstrap** intervals (10,000 resamples, clusters =
statute + article): the claim set is resampled repeatedly to estimate how far a
figure would move had a different sample of claims been drawn. **Calibration** is
reported as expected calibration error (ECE), the average gap between stated
confidence and observed accuracy — the same idea as checking a pressure gauge
against a reference instrument: a gauge reading 95 should be right about 95 times
in 100. λ is a bias-corrected index (accuracy on the always-true family plus
accuracy on the always-false family, minus one), which is zero for a system
answering from a fixed response preference.

**Table 1. Hosted arm, majority vote, closed book.**

| system | condition | BAcc | 95% CI | coverage | λ | ECE |
|---|---|---|---|---|---|---|
| claude-sonnet-5 | E1 | 0.6920 | [0.633, 0.750] | 0.615 | 0.325 | 0.0373 |
| claude-sonnet-5 | E2 | 0.6242 | — | 1.000 | 0.294 | 0.0634 |
| claude-haiku-4.5 | E1 | 0.5298 | [0.489, 0.570] | 0.710 | −0.026 | 0.2263 |
| claude-haiku-4.5 | E2 | 0.5558 | — | 0.998 | 0.061 | 0.2070 |

The interval for the smaller hosted model contains 0.5; the interval for the
larger one does not. The calibration figures differ by roughly a factor of six
between the two. The calibration estimator was checked against a positive
control: applied to the deterministic rule baseline of Section 4.5 it returns
0.0000, where the earlier mid-point formula returned 0.0500. In 8 of 56 cells
fewer than 50 committed answers carried a confidence value, and ECE is
suppressed for those cells rather than reported.

## 4.2 The coverage–accuracy trade-off

Eighteen open-weight models have a complete E1 cell under prompt variant A.
Table 2 reports each with its coverage, which is what makes the pattern legible.

**Table 2. Open-weight models, E1 / variant A.**

| model | BAcc | 95% CI | coverage | CI excludes 0.5 |
|---|---|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 0.7500 | [0.5000, 0.8750] | 0.013 | no |
| qwen2.5:32b-instruct | 0.6769 | [0.5833, 0.7618] | 0.173 | **yes** |
| gemma3:27b | 0.5674 | [0.5230, 0.6115] | 0.970 | **yes** |
| llama3.2:3b-instruct-q8_0 | 0.5509 | [0.5073, 0.5963] | 0.884 | **yes** |
| qwen2.5:14b-instruct | 0.5509 | [0.4839, 0.6159] | 0.205 | no |
| gemma3:12b | 0.5493 | [0.5139, 0.5836] | 0.987 | **yes** |
| llama3.2:3b-instruct-fp16 | 0.5434 | [0.4999, 0.5879] | 0.886 | no |
| llama3.2:3b-instruct-q5_K_M | 0.5318 | [0.4963, 0.5676] | 0.943 | no |
| qwen2.5:7b-instruct-fp16 | 0.5286 | [0.4048, 0.6353] | 0.051 | no |
| qwen2.5:7b-instruct-q8_0 | 0.5250 | [0.3500, 0.6375] | 0.038 | no |
| qwen2.5:3b-instruct-q8_0 | 0.5176 | [0.4915, 0.5436] | 0.657 | no |
| qwen2.5:3b-instruct-fp16 | 0.5126 | [0.4922, 0.5336] | 0.727 | no |
| qwen2.5:3b-instruct-q5_K_M | 0.5124 | [0.4898, 0.5350] | 0.516 | no |
| gemma3:4b | 0.5114 | [0.4766, 0.5456] | 0.896 | no |
| llama3.2:3b-instruct-q4_K_M | 0.5040 | [0.4663, 0.5422] | 0.668 | no |
| qwen2.5:3b-instruct-q4_K_M | 0.5029 | [0.4886, 0.5183] | 0.968 | no |
| llama3.2:1b | 0.4850 | [0.4604, 0.5000] | 0.233 | no |
| qwen2.5:7b-instruct-q5_K_M | 0.4603 | [0.2778, 0.6143] | 0.034 | no |

Four of the eighteen have intervals that exclude 0.5. They do so in two
different ways, and the difference is the finding.

The first way is to answer rarely. qwen2.5:32b-instruct reaches 0.6769
[0.5833, 0.7618], an interval that overlaps the hosted claude-sonnet-5 value of
0.6920 [0.633, 0.750] — but it commits on 0.173 of the claim set, under a fifth
of the items. The model at the top of the table, qwen2.5:7b-instruct-q4_K_M, is
the limiting case: a point estimate of 0.7500 at a coverage of 0.013, with a
lower interval bound resting on 0.5000. At coverages of this order the estimate
carries little information about the remaining items, and the four cells with
coverage below 0.06 should be read as such.

The second way is to answer nearly everything and clear chance by a margin.
gemma3:27b (0.5674 at coverage 0.970), llama3.2:3b-instruct-q8_0 (0.5509 at
0.884) and gemma3:12b (0.5493 at 0.987) sit five to seven points above the 0.5
line at close to complete coverage. Their point estimates are above the smaller
hosted model's 0.5298, at higher coverage; the intervals overlap
([0.5230, 0.6115] against [0.489, 0.570]), so we do not claim a separation
between them.

This is a coverage–accuracy trade-off, not a uniform failure. The two ways of
exceeding chance answer different operational questions: one system is more
often right on a small selected slice, three are slightly better than a coin
across almost the whole set.

**What would count as acceptable.** Deciding whether either mode is usable in a
building-inspection workflow requires a threshold, and this study does not
supply one. A threshold would have to state the cost of a false acceptance (a
non-compliant claim passed) against a false rejection (a compliant claim
escalated), and the residual error rate the reviewing authority is willing to
carry, neither of which follows from the measurements here. Two observations
bear on such a decision without settling it. A system operating at coverage
0.173 leaves the large majority of items to a human reviewer, so its value
depends on whether the routing itself is cheap. A system at coverage near 0.97
and balanced accuracy near 0.55 returns a verdict on almost every item while
being wrong on nearly as many items as it is right, so its output would have to
be treated as a prompt for review rather than as a check. We therefore report
the measurements and refrain from a general verdict on usability.

## 4.3 What abstention buys: two measures

Abstention was priced two ways. The first is the difference
BAcc(E1) − BAcc(E2): what permitting "not sure" adds to committed accuracy. The
second is the pre-registered measure of Annex EK-1 §3, Δ = A_com − A_abs, where
A_com is E2 accuracy on the items the system committed to under E1 and A_abs is
E2 accuracy on the items it abstained from. Δ > 0 means abstention carried
information about which items the system would get wrong.

**Table 3. Pre-registered Δ.**

| run | A_com | n | A_abs | n | Δ |
|---|---|---|---|---|---|
| archive A@32 run 1 | 0.6644 | 292 | 0.5470 | 181 | 0.1174 |
| archive A@32 run 2 | 0.6609 | 289 | 0.5326 | 184 | 0.1283 |
| archive A@32 run 3 | 0.7010 | 291 | 0.5220 | 182 | 0.1791 |
| A@128 (earlier day) | 0.6540 | 289 | 0.5870 | 184 | 0.0670 |
| A@32 today | 0.6576 | 295 | 0.5562 | 178 | 0.1014 |
| claude-haiku-4.5, majority | 0.5672 | 335 | 0.5255 | 137 | 0.0416 |
| claude-sonnet-5, majority | 0.6942 | 291 | 0.5385 | 182 | 0.1557 |

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
are reported. BAcc(E1) − BAcc(E2) falls from a mean of 0.0762 to 0.0332, a 56%
relative drop and 44% of the archive mean, outside the archive range
[0.0735, 0.0784]. The pre-registered Δ falls from an archive mean of 0.1416 to
0.1014, a 28% relative drop, below the archive range [0.1174, 0.1791]. That
range is wide and driven by run 3 (0.1791), so the size of the change on the
pre-registered measure is uncertain even though its sign is consistent. "Halved"
is accurate for the first measure only.

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

## 4.6 Retrieval

BM25 is a standard lexical ranking function that scores passages by weighted
word overlap with the query. Over corpus_v2 (1,755 units) with the top three
passages retrieved per claim, it placed the cited unit among the retrieved
passages for 79 of the 289 article-attributing claims, a recall of 0.2734; 210
were missed.

This bounds the configuration measured, not retrieval in general: one lexical
retriever, untuned, at a single value of k, against a corpus in which many units
share near-identical legal phrasing. Under this configuration, a grounded arm
built on the same retriever inherits that ceiling on the article-attributing
subset, since the cited provision was absent from the supplied context in the
majority of those items. Whether a tuned retriever, a larger k, or a dense or
hybrid retriever closes the gap was not measured here, and end-to-end accuracy
for the grounded arms is not reported [SAYI YOK: grounded production run not
executed].

---

# 5 Discussion

## 5.1 The open-weight arm is a coverage–accuracy trade-off, not a uniform failure

Eighteen locally hosted models produced a scorable cell under the abstention-permitted condition (E1) with prompt variant A. Four of them have a 95% cluster-bootstrap interval for balanced accuracy that lies entirely above 0.5, and those four do not sit at the same operating point.

`qwen2.5:32b-instruct` reaches 0.6769 [0.5833, 0.7618]. That interval overlaps the hosted `claude-sonnet-5` value of 0.6920 [0.633, 0.750]. But it commits to an answer on 0.173 of the claims: it declines roughly five items in six, and its accuracy is measured only on the sixth. The other three trade in the opposite direction. `gemma3:27b` scores 0.5674 [0.5230, 0.6115] at coverage 0.970; `llama3.2:3b-instruct-q8_0` 0.5509 [0.5073, 0.5963] at coverage 0.884; `gemma3:12b` 0.5493 [0.5139, 0.5836] at coverage 0.987. These three answer nearly every claim and sit five to seven points above chance.

The engineering reading is a trade-off between how much of the workload a system will take on and how well it does on that share — not an absence of signal. One local configuration is comparable to the hosted system on the small slice it will speak about; three are near-complete in coverage and modestly better than a coin. The remaining fourteen cells have intervals that include 0.5, so on this item set they are not distinguishable from chance. Coverage also disciplines how point estimates should be read: `qwen2.5:7b-instruct-q4_K_M` carries the highest point estimate in the table, 0.7500, at coverage 0.013, with an interval of [0.5000, 0.8750]. A high score computed over a handful of committed items is not a capability claim.

## 5.2 Abstention frequency held; abstention selectivity fell

Comparing the three archived hosted runs (variant A, 32-token budget) with the run repeated on 28.08.2026 under the same settings, the number of abstentions is close to unchanged: 181, 184 and 182 in the archive against 178 today, a relative decrease of 2.2%. What changed is what those abstentions were worth, and the two available measures of that disagree in size.

The condition contrast BAcc(E1) − BAcc(E2) — how much the option to say "not sure" buys in balanced accuracy — falls from an archive mean of 0.0762 (range [0.0735, 0.0784]) to 0.0332, a relative drop of 56%. The pre-registered measure Δ = A_committed − A_abstained (pre-registration addendum 1, `sonuclar/F4_on_kayit_ek.txt`), which asks whether the items a model declined are ones it would have got wrong anyway, falls from an archive mean of 0.1416 to 0.1014, a relative drop of 28%. Both are positive today, and both moved in the same direction; the description "halved" applies only to the first. The archive Δ range is wide, [0.1174, 0.1791], with the third run an outlier at 0.1791, so the width of the reference band limits how firmly the size of the decrease can be stated. We report both measures because reporting only the larger one would overstate the effect.

For a building-inspection workflow this pattern matters more than either number alone. A tool whose abstention rate is stable but whose abstentions have become less informative looks unchanged on a dashboard that monitors abstention rate. The "send this one to a human" signal remains visually intact while carrying less of the meaning it was accepted for.

## 5.3 Re-qualification: a fixed test set, a changed component

The strongest operational finding is that a system qualified once against a frozen test set may not stay qualified. The same 473 claims, the same gold labels, the same variant A prompt, the same 32-token budget and the same hosted model name yield archive balanced accuracies of 0.6832, 0.6796 and 0.6986 — a run-to-run range of [0.6796, 0.6986] — against 0.6422 today, outside that range. Under the forced-choice condition the archive range is [0.6012, 0.6220] and today's value 0.6090 falls inside it. The movement is concentrated in the condition where the model is allowed to abstain, which is consistent with §5.2.

**Choice of comparison baseline.** Two baselines are available and they answer different questions. The cluster bootstrap over claims, [0.633, 0.750], asks whether a measured value would generalise to other claims drawn from a comparable population; the claim set is treated as variable, and today's 0.6422 falls inside it. The run-to-run range, [0.6796, 0.6986], asks whether behaviour changed on *this* set of 473 items; the claim set is held fixed. The version question fixes the item set by construction, so the run-to-run range is the matching baseline. We nonetheless report the bootstrap interval, because a reader who prefers the generalisation framing should be able to read the result in those terms: behaviour on the frozen set moved beyond previously observed run-to-run variation, while remaining inside the interval one would expect across resamples of comparable claim sets.

**What we can and cannot say about our own side.** The archived runs were produced with `f4_api.py`; the repeated run was produced with the regenerated `f4_api_v2.py`. The variant A prompt strings are byte-identical across the two (E1 `8a8ef386b0b2b619`, E2 `64dedda000ce465e`), but that identity was re-derived from the archived source code: the archived run records carry no script hash at all. The two v2 runs do carry hashes (`11a5d5a3b7b7af20` for the 128-token run, `002df510703fb0a7` for today's), and they differ, because the file was regenerated from patches. The statement "the harness is the same" therefore rests on source inspection rather than on recorded provenance, and we cannot rule out a difference that reading the source did not surface. This is a real limit on the inference, and it is the reason the finding is framed as a re-qualification requirement rather than as a measurement of a vendor release.

The practical recommendation follows from the weaker reading as well as the stronger one. Qualification of an LLM-assisted checking aid is a dated statement about a component that can change outside the operator's control. Building inspection already has vocabulary for this — periodic re-verification of measuring instruments, re-qualification of a procedure after a change to any element of it. The corresponding practice here is to retain a frozen item set, re-run it on a schedule, and report a run-to-run range rather than a single figure.

## 5.4 Grounding, rules, and one circularity we cannot remove

BM25 — a standard word-overlap retriever that ranks passages by shared terms — was run with k = 3 over the 1755-unit refined corpus and returned the cited article for 79 of the 289 article-level claims (0.2734), missing 210. This bounds what *this* retriever at *this* setting achieves on *this* corpus. It is a single, untuned, lexical configuration, and it does not support a general statement about what retrieval can contribute; a tuned or hybrid retriever was not tested here.

The rule-based baseline R3, which uses no language model, scores 473/473 on the refined corpus with the v7a gold and 466/473 on the raw corpus with the same gold. A negative control that shuffles the claim-to-rule pairing across five seeds averages 0.5315, so the score is not an artefact of the scoring path. The seven items R3 fails on the raw corpus (1.48% of the set) are the seven that the expert panel had frozen: 246, 257, 304, 360, 364, 382, 393. This convergence should not be described as independent replication. R3 did not generate those labels; it *failed* on them, which is to say it marked the same seven items. Moreover, the gold correction and the R3 failure both trace to the same corpus observation — the merged-clause parsing that the refined corpus repairs. The two views are consistent, but they are two views of one observation, and we report the agreement as a consistency check rather than as corroboration by an independent instrument.

A related circularity applies to the currency probe (P6): the corpus amendment-year field and the claim-set amendment note derive from the same regular expression applied to the same PDFs. The independent channel is the check against official consolidated text on mevzuat.gov.tr, which matched on 20 of 20 sampled items with 0 mismatches, and whose article counts reproduced our parser exactly (3194: 49, 4708: 15, 6331: 39). That check covers three laws only.

## 5.5 What would count as acceptable

Calling a system "not usable" requires a threshold, and this study did not establish one. A screening aid inside a building-inspection workflow would plausibly be judged on three quantities: the share of incorrect statements about the code that pass through unflagged, the share of the workload still requiring human reading, and whether the tool's own uncertainty signal can be trusted enough to route work. Our design measures analogues of the first two — balanced accuracy and coverage — but it does not measure the cost asymmetry between a missed error and a false alarm in a real office, and without that asymmetry a numeric pass mark cannot be set from these data. We therefore state the operating points and leave the threshold to the adopting organisation.

What can be said concretely: the best hosted configuration observed here commits on 0.615 of items at balanced accuracy 0.6920 with an expected calibration error of 0.0373, meaning its stated confidence tracks its actual hit rate closely — the way a gauge that reads 5 mm when the true gap is 5 mm is in calibration. Its forced-choice counterpart reaches full coverage (1.000) at balanced accuracy 0.6242 with ECE 0.0634. The second hosted model reaches 0.5298 [0.489, 0.570] at coverage 0.710 with ECE 0.2263 — an interval that includes 0.5 and a confidence signal far from calibrated. Any of these leaves a substantial residue of items for human review, and an organisation that cannot absorb that residue should not treat the tool as a filter.

# 6 Limitations

**Single run against three.** The repeated hosted run is one run; the archive baseline is three. A single value cannot itself establish a range, so the drop to 0.6422 is a comparison of one observation against a previously measured band, not a comparison of two bands.

**What "version" does not mean here.** We observed a change in the behaviour of a hosted endpoint on a fixed item set between two dates. We did not observe, and were not told, any vendor release, weight change or serving change; no vendor version identifier was recorded. "Version drift" is our label for a behavioural difference, not a claim about the provider's internals.

**Provenance of the harness comparison.** As set out in §5.3, the archived runs carry no script hash, and the identity of the variant A prompts was re-derived from archived source rather than read from run records.

**Independent currency verification is partial.** The check against official text covers 3194, 4708 and 6331. The building-inspection implementation regulation (YDUY) was not covered, leaving 43 currency claims without independent verification.

**One untuned retriever.** BM25 at k = 3 over 1755 units is the only retrieval configuration tested. Its recall of 0.2734 characterises that configuration, not retrieval generally.

**Mechanism unmeasured.** We report what changed in the outputs; we did not measure why. Whether the shift in abstention selectivity reflects decoding, serving, prompt handling or something else is outside what these runs can determine.

**Two effect sizes.** The condition contrast and the pre-registered Δ move in the same direction but by different relative amounts (56% and 28%), and the archive Δ band is wide. Readers should treat the magnitude of the selectivity decrease as uncertain.

**Suppressed cells.** In 8 of 56 cells fewer than 50 confidence-bearing records were available, and calibration and Brier figures were suppressed there rather than reported at low precision.

**Repository history was reconstructed.** Access to the original machine was lost and the repository was rebuilt from packaged archives (`REKONSTRUKSIYON.md`). File contents are verifiable against archive checksums, but commit timestamps are not: that each pre-registration was written before the run it governs cannot be demonstrated from git history. The dates inside the pre-registration texts and the file timestamps inside the archives support the claim; they are not equivalent to a commit stamp, and we do not present them as such.

# 7 Conclusions

RUHSAT-Bench evaluates 473 claims about six frozen Turkish regulatory documents under two response conditions, with gold labels adjudicated by two domain experts (decision-level Cohen's κ = 1.000 [1.000, 1.000], quality-level κ = 0.860 [0.759, 0.961], n = 150).

Three results carry over to practice. First, the open-weight arm is better described as a coverage–accuracy trade-off than as a flat failure: four of eighteen local configurations exclude chance, one of them at accuracy overlapping the hosted system but at 0.173 coverage, three near-complete in coverage at five to seven points above chance. Second, abstention frequency and abstention quality can move independently: across the archived and repeated hosted runs the abstention count fell 2.2% while the two measures of its informativeness fell 56% and 28%. Third, and most consequential for engineering practice, a hosted model's behaviour on a frozen item set moved outside its own previously measured run-to-run range while the harness was, as far as source inspection can establish, unchanged — which means that qualifying such a tool is a dated statement and calls for a retained frozen item set and scheduled re-qualification.

We do not set a numeric acceptance threshold, because the cost asymmetry that would define one was not measured. We report operating points instead, together with the limits — one repeated run, one untuned retriever, partial independent currency verification, an unmeasured mechanism, and a repository whose commit history was reconstructed — under which they should be read.

---
