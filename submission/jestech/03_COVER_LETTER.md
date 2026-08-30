# Cover letter

To the Editor,
*Engineering Science and Technology, an International Journal*

Dear Editor,

I submit for your consideration **"Measuring abstention, not accuracy: a
re-qualification benchmark for language-model decision support on Turkish
construction and occupational-safety regulation."**

This is a measurement study about **qualifying decision-support software**, not
a study about language models. The engineering question it addresses is the one
a building-inspection organisation faces before it lets any automated tool near
a compliance decision: on what evidence would the tool be accepted, and how
would anyone know it had stopped meeting that criterion. We argue that for this
class of tool the acceptance criterion cannot be accuracy alone, and has to be
stated over the tool's ability to decline the cases it cannot handle — the
fail-silent versus fail-safe distinction familiar from functional safety.

We build the measurement instrument this requires: 473 true/false claims over
six frozen Turkish regulatory documents (the Development Law No. 3194, the
Building Inspection Law No. 4708 and its implementing regulation, the
Occupational Health and Safety Law No. 6331 and its risk-assessment regulation,
and the Turkish Building Earthquake Code TBDY 2018), each claim scored under a
condition permitting an explicit "not sure" and a condition forcing a binary
verdict. Gold labels were audited by two domain specialists in two blinded
passes, and we report that audit in full, including its negative result: the
second pass, which asked the raters to read the whole article rather than the
quoted sentence, produced systematic disagreement (Cohen's κ = 0.722, sign test
p = 0.0312) where the first had produced none.

Three results seem to us to be of engineering interest.

1. **Closed-book use is not defensible on this material, but retrieval-grounded
   use reaches a materially different operating point.** On the pre-registered
   primary comparison, a 32B open-weight model gains +0.2607 in balanced
   accuracy under forced choice when three retrieved passages are supplied
   (95% CI [+0.2218, +0.2964]), and +0.3552 when the cited article is supplied
   (95% CI [+0.3112, +0.3984]).

2. **The judgement step is separable from the presence of evidence.** Against a
   string-matching rule applied to the *same* retrieved passages, the model adds
   +0.2292 in balanced accuracy (95% CI [+0.1939, +0.2635]). Supplying the text
   is not by itself what produces the result.

3. **A qualified component behaved differently on a frozen test set, and
   forced-choice accuracy did not register it.** A hosted model re-run about four weeks later on the frozen claim set,
   at the same budget and with byte-identical prompts, held its forced-choice accuracy
   inside its archived range while its abstention-permitted accuracy fell
   outside it, with the number of abstentions barely moving. We do not claim the
   size of that change: its paired interval contains zero, and the manuscript
   says so. What the run shows is that the two conditions moved differently,
   which is precisely what a forced-choice benchmark cannot register. In
   engineering practice this is the situation of a qualified tool whose
   behaviour on its own acceptance test is no longer what it was.

The study was pre-registered before the runs, and every deviation from the
pre-registration is declared in the paper rather than absorbed. Where a
pre-registered correction weakens a result we report the weakened figure: one of
our two open-weight models clears chance, after the pre-registered Bonferroni
correction, by 0.0017 in balanced accuracy, and we say so in those terms. We
have deliberately made no claim of comprehensiveness or coverage anywhere in the
paper; the corpus is six documents, the retrieval configuration is one untuned
BM25 at k = 3, and the limitations section states what each of those bounds.

The benchmark, the frozen source documents with checksums, the
pre-registrations, the expert audit workbooks and the analysis code are released
so that the re-qualification measurement can be repeated by others on their own
schedule, which is the point of the paper.

The manuscript is original and is not under consideration elsewhere. I declare
no conflict of interest.

Yours sincerely,

Ali Çetinkaya
Department of Computer Engineering, Faculty of Technology
Selçuk University, Konya, Türkiye
ali.cetinkaya@selcuk.edu.tr · ORCID 0000-0002-7747-6854
