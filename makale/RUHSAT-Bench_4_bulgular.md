# 4 Results

> Every figure below is from a committed script output. Sources are named in
> brackets. Confirmatory analyses were fixed in `sonuclar/F4_on_kayit.txt` and
> amended, before any accuracy metric was computed, in `F4_on_kayit_ek1.txt`,
> `_ek2.txt` and `_ek3.txt`. Analyses added after the fact are marked
> exploratory wherever they appear.

## 4.1 The evaluated systems

Eighteen open-weight models were run locally under both conditions on all 473
claims (17,028 calls). Two failed the pre-registered response gate — they echoed
the claim text instead of emitting a label — leaving sixteen. Two hosted models
were added to establish a ceiling, each run three times with a majority vote,
with extended thinking disabled so that the protocol matched the local arm
(verified: zero thinking tokens; response rate 1.00).
*[`f4_metrikler.csv`, `f4_metrikler_frontier.csv`, `f4_metrikler_haiku.csv`]*

## 4.2 No open-weight model exceeds chance

Across the sixteen valid local models, balanced accuracy ranges from 0.48 to
0.64 and Youden's J from −0.04 to +0.28. The single highest J belongs to a cell
with 82 committed answers.

The bias-corrected index is the more informative number. λ = accuracy(P1) +
accuracy(P5) − 1 is zero for any model that answers from response bias alone,
because a model with bias *b* scores *b* on the always-true family and *1 − b*
on the always-false one. Across local models λ has a median near 0.04 and a
maximum of +0.206. Knowledge beyond response bias is therefore on the order of
three to nine percentage points.

Self-reported confidence carries no information about correctness anywhere in
the local arm: the AUROC of stated confidence for predicting error ranges from
0.46 to 0.54, and expected calibration error from 0.21 to 0.44. Models report
high confidence — one model gave 95 on 53% of items — while performing at
chance.

## 4.3 Abstention without selectivity

Abstention rates in the abstention-permitted condition span the full range, from
0% to 99%, and vary more with model family and quantisation than with anything
resembling competence. Four quantisations of one 7B model abstain on 95–99% of
items; three sizes of another family abstain on 1–10%. Within a single 3B model,
quantisation moves abstention from 2% to 48% non-monotonically while leaving
balanced accuracy unchanged.

The question that matters is whether abstention tracks competence. For each
model we compared its forced-condition accuracy on the items it abstained from
with its forced-condition accuracy on the items it committed to. **No local
model reaches significance.** The largest difference is +0.12 (p = 0.39); most
are below +0.08. Models abstain, sometimes almost always, without discriminating
what they abstain from. *[`f4_rapor.txt` §1.5]*

## 4.4 Forced choice manufactures a signal

Removing the abstention option does not simply convert silence into answers; it
changes the answers. Among items committed under both conditions, three
quantisations of one 3B model reverse 72%, 73% and 80% of their own verdicts,
and all three answer *false* to every item under forced choice. Eight of
thirty-six cells are degenerate, assigning one label to at least 90% of their
committed answers, in both directions: three cells at 100% *false*, four at
94–97% *false*, one at 91% *true*.

A paired test on correctness misses this entirely. For one model, accuracy on
the always-true family falls from 0.70 to 0.39 while accuracy on the
always-false family rises from 0.39 to 0.64; overall accuracy is unchanged and
McNemar returns p = 0.49. The response distribution had inverted. Any evaluation
that reports only accuracy would record this model as stable across conditions.
*[`f4_rapor.txt` §1.3b, §1.3c]*

## 4.5 The measurement is unstable; the bias-corrected index is not

Six models were re-run with the system prompt reworded and the task otherwise
identical. Across the nine cells with at least thirty committed answers in both
variants, the probability of answering *true* moves by 0.335 on average and by
as much as 0.723. λ moves by 0.044. The ratio is **7.5×**.
*[`varyant_kararlilik.csv`]*

Committed accuracy barely moves at all (mean 0.028), and this is the most
easily misread number in the study. Accuracy is stable because it is pinned at
chance, not because the measurement is reliable. A researcher reporting accuracy
alone would reword a prompt, observe the same figure, and conclude that the
measurement was robust — while what the model actually said had changed
completely.

## 4.6 A capability threshold, not a gradient

Two hosted models were run under the identical protocol.

| | local (16) | claude-haiku-4-5 | claude-sonnet-5 |
|---|---|---|---|
| λ (E1 / E2) | median 0.04 | −0.018 / +0.067 | **+0.334 / +0.300** |
| balanced accuracy (E1) | 0.48–0.64 | 0.53 | **0.70** |
| Youden J (E1) | −0.04–0.28 | 0.07 | **0.39** |
| ECE (E1) | 0.21–0.44 | 0.231 | **0.036** |
| abstention rate (E1) | 0–99% | 27% | 38% |
| abstention selective? | no model | no (Δ +0.05, p = 0.32) | **yes (Δ +0.16, p = 0.0005)** |
| verdict reversal E1→E2 | 13–80% | 15% | **9%** |
| degenerate cells | 8 of 36 | 0 | 0 |

The smaller hosted model patterns with the open-weight models on every axis. It
is from the same provider, reached through the same API, under the same prompts,
the same protocol and the same majority-vote procedure as the larger one. The
difference between the two is therefore not an artefact of hosting, family or
tooling: it is capability. The picture is a discontinuity rather than a smooth
gradient, and the smaller hosted model is the control that establishes it.

The larger model's abstention is selective in the sense the abstention
literature intends: it withholds an answer on 38% of items and is sixteen points
more accurate on what remains. Its calibration error is an order of magnitude
below every other system tested.

The clearest single illustration is the currency probe. Asked whether a given
article was amended in a given year, the larger model **abstained on all 69
such items** — it declined the entire sub-family it could not do. On the
adjacent template, where the claim asserts that an article was never amended, it
answered *false* to all 51 committed items regardless of truth. Within one probe
family the model shows two distinct failure modes: where it knows it does not
know, it is silent; where it does not know that, it applies a constant label.
Local models answered the same 69 items with high stated confidence.

## 4.7 What no system can do

The currency probe was rebalanced into a 2×2 design during dataset construction
precisely so that template-matching could not be mistaken for knowledge. It now
functions as a diagnostic. Every local model sits at balanced accuracy ≈ 0.50 on
it, visibly assigning a single label to all 120 items; under the earlier
unbalanced design the same behaviour would have read as roughly 50% accuracy.
Neither hosted model does better. Determining whether a specific article was
amended in a specific year is unsolved across every system tested, from 1B to
frontier.

The cross-reference probe separates in the predicted direction for the more
capable systems: attributing a provision to the wrong *document* is detected
more often than attributing it to the wrong *article* within the right document
(0.72 vs 0.49 for the larger hosted model). The distinction is absent or
reversed in the weaker systems, so it is reported as capability-dependent rather
than as a property of the probe.

## 4.8 Reliability of the hosted arm

The hosted provider does not accept a temperature parameter for these models, so
determinism could not be fixed and was measured instead. Under the final
protocol, three independent runs agreed unanimously on 84% (E1) and 88% (E2) of
items for the larger model and 73% / 81% for the smaller; pairwise agreement was
0.89/0.92 and 0.82/0.87. Four and nine items respectively produced no majority
and are recorded as undetermined. All reported hosted figures are majority votes
over three runs. The local arm was fully deterministic: a complete re-run
reproduced all 946 outputs byte-for-byte.

An exploratory question the hosted arm makes available, and the deterministic
local arm does not: is cross-run instability a better error signal than stated
confidence? It is not. For both hosted models, stated confidence predicts error
better than instability does (AUROC differences of −0.027 to −0.085). Where a
model's confidence carries information at all, it carries more than its own
variability does.
