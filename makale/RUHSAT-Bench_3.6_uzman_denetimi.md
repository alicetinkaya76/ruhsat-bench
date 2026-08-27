# 3.6 Expert audit — and 4.x Results

> Every figure is from a committed script output. Bracketed notes name the artefact.
> One placeholder remains: the adjudicated consensus figure, pending the reconciliation
> meeting over the eight items in `sonuclar/gecis2_uzlasi.csv`.

---

## 3.6 Expert audit

Two civil-engineering and occupational-safety specialists audited the gold labels in two
passes. The passes ask different questions, and the difference between them is itself a
result (Section 4.x).

### 3.6.1 Instrument common to both passes

Items were presented in a spreadsheet showing the claim, the sentence it was derived from,
and the article that sentence was taken from. The gold label, the probe family, the
manipulation template and the sampling stratum were withheld. Row order was randomised
separately for each rater so that fatigue and position effects would not be correlated
between them. Before distribution, each workbook was checked programmatically for schema
conformity, complete stratum coverage, dropdown validity, and leakage of any withheld field
into a visible cell; the leakage scanner is itself verified against a deliberately
contaminated copy on every run. *[`sonuclar/kitap_dogrulama.txt`]*

### 3.6.2 First pass — verdict against the cited evidence

A stratified sample of 150 items was drawn: 100 from items not flagged by the model-
consensus screen of Section 3.5, and 50 from flagged items, allocated across probe families,
with design weights recorded per item. Eight additional attention probes were inserted —
genuine items whose claim text was altered so that it contradicts its own quoted sentence,
with a known correct label — as a positive control on rater diligence. Raters gave two
independent judgements per item: a **verdict** (true / false / not sure) and an **item
quality** rating (clean / context-dependent / corrupted), the latter deliberately orthogonal
to truth, since a deliberately false claim can be a perfectly well-formed benchmark item.

Both raters caught 8 of 8 attention probes. Neither used the abstention option on any of the
158 items. Inter-rater agreement was κ = 1.000 on the verdict axis (observed agreement
1.000, chance 0.543, n = 150) and κ = 0.860, 95% CI [0.759, 0.961], on the quality axis
(observed 0.953, chance 0.667). Independence was verified from the free-text rationales,
which were distinct on all 112 items where both raters wrote one.

**The perfect verdict agreement is a property of the instrument, not a sign of an easy
gold set.** Because the workbook displays the quoted sentence and its article, and because
the gold label was itself derived from those same facts, most probe families reduce to a
comparison rather than a recall task: an altered quantity differs visibly from the quote, a
shifted article citation differs visibly from the recorded article. Two attentive readers
should agree completely, and the axis therefore establishes that the generator's
manipulation is recoverable from the displayed evidence — an internal-consistency check —
rather than validating the label against the legislation. The families that do require
external knowledge (enactment years, existence of a cited document) comprise 32 of the 150
sampled items.

No verdict differed from the gold label on any of the 150 items. With zero events this
bounds the label error rate at 2.50% (95%, one-sided) for the mechanically verifiable class;
it is not an estimate of zero. Because both strata also contained zero events, the planned
test of whether consensus flags predict label errors had no power and is not reported as
evidence either way. *[`sonuclar/kappa_raporu.txt`]*

### 3.6.3 Second pass — verdict against the full article

The first pass cannot reach the error class in which a sentence, lifted out of its article,
no longer expresses what the article expresses: a condition carried from a preceding
paragraph, an anaphor, or an exception stated further down. The rater sees the same
decontextualised sentence the generator saw, and can err with it.

A second pass of 60 items therefore changed the question: raters were instructed to open the
source document and read the whole article before deciding, with the quoted sentence
demoted from evidence to starting point. Three strata were used: a **census of all 33 items**
that either rater had rated as less than clean in the first pass; a **random 25 of the 105**
items both had rated clean, without which only the flagged-item rate would be estimable; and
**two seeded items** removed during cleaning whose gold labels are independently known to be
wrong, as a positive control on this pass's power. Item text was taken from the repaired set
of Section 3.4, so that items flagged in the first pass only because of a word-break defect
would now be seen in corrected form.

Agreement fell to κ = 0.722 (observed 0.897, chance 0.628, n = 58). All six disagreements
ran in the same direction (sign test p = 0.031), which identifies them as a systematic
difference in criterion rather than measurement noise: one rater asked whether the provision
appears in the source, the other whether it appears *under the stated conditions*. In one
item the second rater's own written rationale records the contextual restriction and still
assigns a true label. Disagreements of this kind cannot be averaged; they were referred to
adjudication, with the decision rule fixed before the individual items were discussed.
*[`sonuclar/gecis2_uzlasi.csv`]*

The positive control is the pass's most consequential output. Of the two seeded errors, one
was detected by one rater and missed by the other; the second is a weak control because its
gold label coincides with the correct answer for an unrelated reason. **A rule requiring
both raters to disagree with gold therefore demonstrably misses a real label error**, and
the lenient rule — at least one rater disagreeing — is used as the primary criterion, with
the strict rule reported as a lower bound.

Under the lenient rule the contextual defect rate was 15.2% (5/33) among items previously
rated less than clean and 4.0% (1/25) among items previously rated clean, giving a
design-weighted estimate of 6.7%, 95% CI [1.6%, 11.8%], over the 138-item first-pass frame.
Compounding the two sampling stages projects 8.8% to the full claim set; the interval for
the compounded figure is wider than the one quoted and is not reported. Under the strict
rule no event was observed in 58 items, bounding the rate at 6.2% (95%, one-sided).
*[`sonuclar/gecis2_raporu.txt`]*

The first pass's quality axis was 3.8 times more likely to flag an item that the second pass
found contextually defective, but at this sample size the association is not significant
(Fisher exact p = 0.22) and is reported as a tendency, not as predictive validity.

---

## 4.x Results — what the two passes show

The two passes examined the same benchmark and disagreed about it, and the disagreement is
interpretable rather than troubling.

| | First pass | Second pass |
|---|---|---|
| Question | claim consistent with the quoted sentence? | claim true of the whole article? |
| κ (verdict) | 1.000 | 0.722 |
| Disagreements | 0 of 150 | 6 of 58, all one direction (p = 0.031) |
| Label errors found | 0 (≤ 2.50%, one-sided) | 6.7% [1.6%, 11.8%] |
| Positive control | 8/8 mechanical probes | 1/2 real gold errors |

An audit that shows the rater the same evidence the label was built from re-derives the
generator's logic and returns near-perfect agreement and nothing else. Requiring the rater
to consult the source instead halves the agreement and surfaces a defect class that five
deterministic layers, a model-consensus screen, and a 150-item expert pass had all missed.
The practical implication generalises beyond this benchmark: **for any dataset whose labels
are derived from an excerpt, an audit conducted on that excerpt cannot validate the label.**

The second finding concerns audit decision rules. Requiring unanimity among raters is the
intuitive way to avoid false positives, and on this data it would have discarded the one
real label error the audit found. Where the defect class is subtle enough that competent
raters differ, unanimity buys precision at a cost in sensitivity that a positive control
makes visible and that is otherwise invisible.

The third concerns what the residual risk actually is. The deterministic layers reduced
mechanical defects to a measured near-zero, and the first pass confirmed it. What remains is
semantic and concentrated: roughly one item in twelve states a provision without the
condition under which it holds. That is the number a user of this benchmark needs, and no
automated check in this study would have produced it.
