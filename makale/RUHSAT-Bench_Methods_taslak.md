# 3. Methods

> **Draft status.** Every figure below is taken from a script output committed to the
> project repository; the corresponding artefact is named in a bracketed note so it can be
> re-derived. Section 3.6 is deliberately left open pending the expert-audit design
> decision. Two parameter values are marked `[verify]` — read them off the generator
> source rather than trusting this draft.

---

## 3.1 Corpus and provenance

The benchmark draws on six Turkish regulatory documents spanning construction permitting,
building inspection, occupational health and safety, and seismic design:

| Code | Document | Origin | Retrieved | Consolidated text | Amendments after retrieval |
|---|---|---|---|---|---|
| 3194 | İmar Kanunu | mevzuat.gov.tr | 14.07.2026 | yes (189 amendment marks) | none detected |
| 4708 | Yapı Denetimi Hakkında Kanun | mevzuat.gov.tr | 22.05.2026 | yes (118) | none detected |
| 6331 | İş Sağlığı ve Güvenliği Kanunu | mevzuat.gov.tr | 09.12.2025 | yes (63) | none detected |
| ISGRISK | İSG Risk Değerlendirmesi Yönetmeliği | mevzuat.gov.tr | 25.07.2026 | yes; never amended | none |
| YDUY | Yapı Denetimi Uygulama Yönetmeliği | mevzuat.gov.tr | 25.07.2026 | yes (406) | not re-checked |
| TBDY | Türkiye Bina Deprem Yönetmeliği 2018, technical annex | resmigazete.gov.tr | as published, 18.03.2018 | n/a (annex) | not re-checkable |

Retrieval dates were recovered from PDF document metadata rather than from records kept by
hand, which also established that ISGRISK and YDUY were obtained from the same
consolidated-text service. That fact carries evidential weight: YDUY, drawn from that
service two days apart, carries 406 amendment marks while ISGRISK carries none, so the
absence of marks in ISGRISK reflects an unamended regulation rather than a rendering that
omits the apparatus.

**Currency verification.** Because a legislation benchmark is only meaningful relative to a
point in time, each source for which a second retrieval was possible was re-downloaded at
freeze time and compared with the corpus copy along two renderer-independent measures.
First, the sets of amendment dates (`d/m/yyyy` tokens) in the two texts were compared; only
dates later than the corpus retrieval date can indicate an amendment made after retrieval.
Second, the 6-gram coverage of every quoted sentence used in the benchmark was measured in
both texts. For 3194, 4708 and 6331 no post-retrieval amendment date appeared and no quoted
sentence lost coverage; the ISGRISK copies were character-identical. Raw length and
amendment-mark counts differed slightly between copies (0.05–0.17%) but were shown to be
artefacts of the two PDF renderers and are not reported as evidence either way.
*[artefact: `sonuclar/belge_guncellik.txt`]*

TBDY 2018 is published in two parts — a six-article framing regulation and a technical
annex of roughly four hundred pages — and the corpus holds the annex as published. It is
reported at its publication date, and this is stated as a limitation in Section 3.7.

---

## 3.2 Claim generation

Claims were produced by a deterministic generator (`uret_iddia_v3_6.py`) that was sealed
before any evaluation run and never re-executed; all subsequent corrections were applied
post hoc as auditable rules, so that claim identifiers remain stable across the study.

Candidate sentences were extracted per article and passed through a conservative filter
that rejects sentences outside a length band `[verify]`, sentences containing a reference to
another numbered statute, and sentences with more than one unbalanced parenthesis. The
filter is deliberately over-restrictive; Section 3.4 shows that this choice is what
eliminates a specific class of label error, at a measured cost in recall.

Six probe families were instantiated, each with subtypes:

| Probe | Manipulation | Subtypes |
|---|---|---|
| P1 | verbatim provision, correctly attributed | verbatim, article-cited |
| P2 | a quantity in the provision is altered | swap |
| P3 | the document's enactment year is stated | correct / incorrect / in-force |
| P4 | a non-existent document or obligation is invoked | fabricated document, fabricated TBDY clause |
| P5 | provision attributed to the wrong article or the wrong document | article-shift, law-shuffle |
| P6 | statement about a provision's amendment history | year given / never amended |

Surface form is held constant within each contrasting pair, so that P1, P2 and P5 items are
lexically indistinguishable and can only be separated by knowledge of the source. Section
3.5 reports a leak audit confirming this property, and one place where it originally failed.

---

## 3.3 Evaluation protocol

Each claim is presented under two conditions. **E1** permits abstention with a three-way
response (true / false / not sure); **E2** forces a binary choice. Reporting therefore
separates *coverage* (the fraction of items on which a model commits) from *committed
accuracy*, and adds balanced accuracy, Youden's J, d′ and expected calibration error.
Balanced accuracy is reported per probe only where both classes are present within that
probe; where a probe contains a single gold class, accuracy within it is a measure of
response bias rather than of knowledge, and is reported as such.

---

## 3.4 Gold-label quality assurance

The QA design proceeds from a single premise: a claim generator that manipulates real legal
text can produce items whose gold label is wrong for reasons the generator cannot see. Five
deterministic layers were applied, each with an explicit positive control.

**L1 — Source identity.** Every quoted sentence was located in the source document and
checked against the article recorded for it. No swallowed articles were found under either
strict or loose heading detection, and all locatable sentences matched their recorded
article. *[`sonuclar/kaynak_dogrulama_v2.txt`]*

**L2 — Accidental truth.** A manipulated claim is only reliably false if the manipulation
does not happen to produce a true statement. Two tests address this. For article-shift
items, the shift target was checked against every article in which the sentence occurs; no
collision was found. For law-shuffle items, the quoted sentence was searched in the target
document. All coverages were zero — a null that required a positive control to interpret.
Measuring the same sentences against their *own* document returned a minimum coverage of
0.95 and a median of 1.00, establishing that the test discriminates. A ceiling measurement
then explained the null: of fourteen genuine cross-document sentence repeats in the corpus,
none survives the sentence filter of Section 3.2, so the pool of sentences that could
produce accidental truth is empty by construction. The conservative filter buys label
validity at the cost of recall, and this is the quantitative statement of that trade-off.
*[`sonuclar/kapsanma_kalibrasyon_temiz.txt`]*

**L3 — Surgical cleaning.** Five rules identify defective source sentences: intra-paragraph
splicing, cross-statute reference, chapter headings, broken suffixes, and all-caps headings.
Rule scope proved to matter more than rule content. Applied to claim text as well as to the
quoted sentence, the cross-statute rule matched the generator's own citation frame and
discarded 209 claims, halving the set and selectively removing almost every item derived
from the three numbered statutes — a loss that would have confounded probe effects with
source document. Applied only to quoted sentences, and only to probes whose proposition is
*derived from* a sentence, the same rules remove 14 claims traceable to 5 defective
sentences, with per-document survival between 95% and 100%. The cleaner verifies itself:
seven claims known to be defective must be dropped and are, and claims dropped only by the
earlier over-broad scope must survive and do. *[`sonuclar/temizlik_raporu_v39.txt`]*

**L4 — Rendering-artefact repair.** Three sources were obtained as word-processor exports
whose text extraction inserts spaces inside words; these breaks had propagated into claim
text. They are detected by comparing against a second, independent rendering of the same
document: a token pair is a break when its concatenation exists in the clean text *and* the
pair never occurs adjacently there — the second condition being what prevents legitimate
collocations from being merged. Thirty-one claims were repaired, covering both missing and
displaced spaces. Each repair is validated by re-measuring coverage against the clean text;
mean coverage rose from 0.590 to 0.969 and no repair had to be reverted. An independent
re-run of the currency audit over the repaired set reports zero remaining losses.
*[`sonuclar/kelime_onarim.txt`]*

**L5 — Design-leak audit.** Gold labels were checked for recoverability from surface form.
Within P1, P2 and P5 this holds: the sum of accuracy on the all-true and all-false families
is 1.03 on average across evaluated cells, i.e. within noise of the value implied by
response bias alone, so the families are lexically indistinguishable. P6 was the exception —
its two templates mapped one-to-one onto the two gold labels, making a quarter of the set
solvable without legal knowledge. The existing evaluation was checked for exploitation of
this cue and showed none (mean balanced-accuracy gain of +0.016 over eight cells), but since
that cohort performs at chance throughout, this is evidence that current results are
uncontaminated rather than evidence that the cue is unexploitable. The two missing cells
were therefore generated with fresh identifiers, leaving existing identifiers untouched, so
that each template now carries both labels in equal proportion. *[`sonuclar/p6_kestirilebilirlik.txt`, `sonuclar/p6_denge_raporu.txt`]*

Two genuine gold errors were found across all layers, of distinct kinds: one item in which a
numeric manipulation fell on a cross-reference rather than on a substantive quantity, and
one item that was a chapter heading rather than a proposition yet carried a *true* label.

The released set contains 473 claims `[verify: final gold balance]`.

---

## 3.5 A rejected approach: model consensus as a label auditor

Before the deterministic layers were built, an ensemble of five locally-hosted models under
both conditions was evaluated as a screening instrument for gold errors. Every model–
condition cell returned a Youden's J of 0.14 or below. A simulation with injected label
errors put the screen's precision at 4.5%, against 2.4% for selecting the same number of
items at random — a lift of roughly 1.8× and not distinguishable from chance at this sample
size. Flag rates also varied by a factor of about eight across probe families in a pattern
that tracks probe difficulty rather than label error. The approach was abandoned. We report
it because the negative result is informative: an ensemble that is itself near chance on the
task cannot audit the labels of that task, and the deterministic checks above were built in
its place. *[`sonuclar/konsensus_rapor.txt`, `sonuclar/konsensus_dogrulama.txt`]*

---

## 3.6 Expert audit

*[Pending design decision. The instrument is built and validated: a blind stratified
workbook of 150 items — random and flagged strata, gold hidden, order randomised per rater,
with eight seeded attention probes as a positive control on the raters themselves — plus a
merge script computing Cohen's κ, design-weighted gold-error rates with finite-population
correction, and a Fisher test of whether consensus flags predict label errors. The section
will report either two independent raters with κ, a single rater with agreement against gold
and no reliability statistic, or the audit as future work.]*

---

## 3.7 Limitations

The TBDY 2018 annex is used as published in 2018; unlike the other sources it has no
independent second rendering, so neither its currency nor its freedom from word-break
artefacts could be verified by the methods above, and it supplies roughly a third of the
claims. Three probe families contain a single gold class by construction, so within-probe
balanced accuracy is undefined for them and comparisons are made between matched subtypes
instead. Item counts for P2, P3 and P4 remain below forty, limiting per-probe precision.
Finally, the corpus covers six documents in one national jurisdiction; the abstention
behaviour reported here should not be assumed to transfer to other legal systems without
replication.
