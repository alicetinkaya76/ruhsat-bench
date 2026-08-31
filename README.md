# RUHSAT-Bench

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22168590.svg)](https://doi.org/10.5281/zenodo.22168590)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

A 473-claim benchmark for measuring **whether a language model declines the
regulatory questions it cannot answer**, over six frozen Turkish construction and
occupational-safety documents.

Companion repository to *"Measuring abstention, not accuracy alone: a re-qualification
benchmark for language-model decision support on Turkish construction and
occupational-safety regulation"* (Ali Çetinkaya, Selçuk University).

This repository is the object the paper's data-availability statement points to.
Every number printed in the paper and in its supplementary material is
regenerated from files in here by scripts in here — there is a number sheet,
`sonuclar/makale_sayilari.txt`, that maps each figure to the script that produced
it, and no figure appears in the paper that is not in that sheet.

**The paper:** `makale/RUHSAT_JESTECH_ana_metin.md` · **supplementary material:**
`makale/RUHSAT_JESTECH_ek.md`

## What the benchmark measures

Each claim is asked twice: once where the system may answer *"not sure"* (E1) and
once where it must choose true or false (E2). A compliance tool that declines a
case hands it to a person; one that answers wrongly with the same fluency it uses
when right does not. Benchmarks that force a binary answer are blind to that
distinction, so this one measures both conditions on the same claims.

Claims fall into six probe families — direct assertion, numeric alteration,
cross-reference (real text attributed to the wrong provision), currency of
amendment, anachronism, and fabricated provision — so an aggregate score can be
decomposed rather than trusted whole. Two of the paper's findings come from that
decomposition: a hosted model whose 0.508 on amendment-currency questions turns
out to be a constant answer rather than guessing, and a lexical baseline whose
0.5938 comes entirely from probe base rates.

## What is in it

| path | what |
|---|---|
| `data/kaynak_pdf/` | the six frozen source documents, as PDF |
| `data/korpus/`, `data/korpus_v2/`, `data/korpus_madde/` | parsed corpora (1,366 / 1,755 / 1,440 units) |
| `data/iddialar/` | the 473-claim set in three gold-label versions (v6, v7a, v7b) and the expert-audit workbooks |
| `beyanlar/`, `sonuclar/F4_on_kayit*.txt` | the pre-registration and its eight annexes (EK-1 … EK-8) |
| `sonuclar/` | every run record (JSONL), every scoring and analysis output |
| `sonuclar/makale_sayilari.txt` | **the number sheet**: every figure in the paper, with the file and script it came from |
| `scripts/` | claim generation, corpus construction, runners, scorer, analysis |
| `hpc/` | the TF-HPC transfer layer used for the local-model runs |
| `makale/` | the manuscript, the supplementary material and the citation-verification record |
| `uzlasi/` | the coder reconciliation rule note and the seventeen-case workbook |
| `kusur_kutugu.md` | the defect log, including defects that are still open |
| `REKONSTRUKSIYON.md` | how the repository was reconstructed and what was lost |

## Reproducing the numbers

The chain runs end to end from the PDFs:

```
bash dogrula_linux.sh          # 17-step acceptance chain, must print 17/17
python scripts/f4_skor.py      # scoring (sealed; do not modify)
python scripts/f4_analiz.py    # analysis layer, produces f4_analiz.{txt,csv}
```

Pinned versions matter for one step: text extraction is byte-identical across
macOS and Linux only with `pypdf==5.9.0`. See `requirements.txt` and `ORTAM.md`.

## Two limits stated up front

**Provenance.** The version-control history of the development repository was
lost and the repository was reconstructed from dated hand-over packages, whose
SHA-256 checksums are recorded in `REKONSTRUKSIYON.md`. The claim that a
pre-registration was written before the run it governs rests on the dates in
those documents and on the packages that contain them, not on commit timestamps.

**Blinding.** The expert-audit workbooks identify the two coders only by role
(`INS_MUH`, `ISG_UZM`). No personal data is included in this archive.

**Seventeen provisional labels.** Seventeen claims remain labelled
`needs_human_review`; no human adjudication was completed for them. The released
labels are provisional for those items, and all principal results are reported
both with and without them (§4.6.5 of the paper). The claim identifiers are 25,
38, 60, 70, 123, 159, 189, 203, 211, 278, 310, 323, 351, 426, 444, 455 and 476.

**A shortcut this benchmark permits.** A baseline that reads no claim text and
predicts each template subtype's majority gold label scores 0.9860 balanced
accuracy, above every system reported in the paper; a probe-family-only baseline
scores 0.8503. This bounds what cross-arm comparisons on this claim set can
establish and is reported in §4.6.6. Anyone reusing this benchmark should
measure against those baselines, not against chance.

## Source documents

The six documents are Turkish primary legislation and regulation published in the
Resmî Gazete and distributed by the state. They are included so that the text
extraction, and therefore every downstream figure, can be reproduced byte for
byte; `MANIFEST.sha256` records a checksum for each.

## Licence

- Code (`scripts/`, `hpc/`): MIT.
- Data and documentation produced by this project (claim sets, gold labels, run
  records, analysis outputs, manuscript): CC BY 4.0.
- The source legislation PDFs are official texts of the Republic of Türkiye and
  are redistributed as received; no additional rights are claimed over them.
