# Independent verification — Orthopedic 510(k) Predicate-Graph Study

Verifier: Gant Duncan · Rebuild run 2026-08-26 to 2026-09-15
Repository: cmorlandev/orthopedic-510k-predicate-graph

Everything in this folder was produced by the verifier. No file in the
repository outside this folder was modified, and `00_freeze_snapshot` was
never run.

## Start here

**`adjudication_summary.txt`** is the authoritative findings document. Where
any other file in this folder disagrees with it, it governs. It carries a
superseded section retained deliberately so the reasoning trail is visible;
that section says so at its head.

## Outcome in one paragraph

Twelve of twenty reference values reproduced exactly. Eight differ, all in the
same direction and all by under 0.3%; the cause is that the summary PDFs sit
outside the frozen snapshot and are re-fetched live, so an 18-day gap between
the analyst's Stage 2 and the verifier's yields additional documents. The
MAUDE comparison reproduced with the same direction and significance. Hand
adjudication of 266 candidate edges across 60 documents -- the complete
199-edge validation sample plus two targeted samples -- gives 81.4% precision
on the validation sample against the verifier-manual criterion and 83.9-85.9%
against the preregistration's own criterion. The shortfall is not diffuse
error: it comes from two identifiable document structures, and a corpus
estimate stratified by K-number load puts roughly 3,572 of 30,487 edges
(11.7%, interval 7.3-22.4%) outside what the hypotheses describe as a
predicate citation. That estimate is calibrated on 244 of the 266 verdicts --
the validation sample plus the 11-25 bin sample, both of which bin cleanly by
K-number load. The 22 reference-section verdicts are excluded from it by
design and calibrate the reference population separately. No implementation defect was
found -- the extractor is faithful to the registered edge rule, which is
itself maximal by design. The OSF registration predates the confirmatory run
by eleven days and checks out.

## What is in here

| file | what it is |
|---|---|
| `adjudication_summary.txt` | findings F1-F12, both hand adjudications, all arithmetic |
| `adjudication_199_edges.csv` | 199 verdicts — complete validation sample, 45 devices |
| `reference_adjudication_22_edges.csv` | 22 verdicts — reference-section sample, 12 devices |
| `bin11_25_adjudication_45_edges.csv` | 45 verdicts with location notes — 11-25 K-number bin, 3 devices |
| `bin11_25_worksheet.xlsx` | the filled 11-25 bin worksheet (primary record) |
| `spotcheck_worksheet.xlsx` | the filled worksheet as adjudicated (primary record) |
| `reference_worksheet.xlsx` | the filled reference worksheet, converted from the verifier's Numbers original |
| `spotcheck_result.txt` | per-tier precision, Wilson intervals, the 37 NO rows itemised |
| `preflight_report.txt` | snapshot hashes, notebook-independence check, library versions |
| `compare_output.txt` | Stage 15 comparison against `expected_values_REFERENCE.json` |
| `compatibility_scan.txt` + `_devices.csv` | corpus scan for compatibility-table documents |
| `reference_device_scan.txt` + `reference_device_edges.csv` | corpus scan for reference-device sections; the 1,136 attributed edges enumerated |
| `spurious_edge_estimate.txt` | corpus estimate binned by K-number load, calibrated on the 199 verdicts |
| `K190123_text.txt` | extracted text supporting the full 25-edge audit of that document |
| `prereg_extracted_text.txt` | extracted preregistration text, so every quotation is checkable |

## Scope of hand adjudication

The verifier manual (section 9) asks for two or three devices. This
verification adjudicated three samples:

  199 edges /  45 documents   complete validation sample drawn by notebook 03
   45 edges /   3 documents   11-25 K-number bin, with per-edge location notes
   22 edges /  12 documents   reference-section targeted sample
  266 edges /  60 documents   total

All three were read by a single adjudicator. There is no second reader and no
inter-rater agreement statistic -- the same limitation the study's own
validation carries. The two targeted samples are not random draws from the
corpus and must not be pooled into a single precision figure; they calibrate
specific populations, and `adjudication_summary.txt` keeps them separate.

## On the two representations of each adjudication

Every verdict appears twice in this folder, deliberately rather than
redundantly: once in the spreadsheet the verifier typed into, and once in a
CSV extracted from it. Either can be checked against the other, and a reviewer
who cannot open a spreadsheet can still read the CSV in the pull-request diff.

  199-edge sample   spotcheck_worksheet.xlsx   <->  adjudication_199_edges.csv
  reference sample  reference_worksheet.xlsx   <->  reference_adjudication_22_edges.csv

This is not belt-and-braces for its own sake. During assembly of this folder a
file named `spotcheck_worksheet.xlsx`, recovered from a removable drive, turned
out to contain 10 rows and no verdict column -- an early draft from the
worksheet script's default 5-edges-per-tier setting, not the adjudication. It
had the right filename and plausible columns, and would have entered the
repository unnoticed as the verdict record. It was caught because its file size
disagreed with a copy whose contents had already been verified. The two
representations exist so that any such substitution is detectable rather than
invisible.

Reading `.xlsx` requires `openpyxl`, which is not part of the study's
`requirements.txt`; `tally_spotcheck.py` accepts Excel input and needs it.
`pip install openpyxl` in the `verify` environment.

The verifier's original Numbers file (`reference_worksheet.numbers`) is
retained locally and available on request. It is not committed: the format is
proprietary and unreadable to most reviewers, and the converted `.xlsx` above
is a faithful copy (22 rows, 12 devices, 16 NO / 6 YES, checked after
conversion).

## Re-running the verifier scripts

All scripts take paths relative to the working directory, so run them from the
**repository root**, not from this folder:

```bash
conda activate verify
cd <repository root>

python verification/scripts/preflight_verifier.py
python verification/scripts/tally_spotcheck.py --csv verification/adjudication_199_edges.csv
python verification/scripts/scan_compatibility_sections.py
python verification/scripts/scan_reference_devices.py
python verification/scripts/estimate_spurious_edges.py --adjudicated verification/adjudication_199_edges.csv
```

`spotcheck_worksheet.py` draws a fresh worksheet and **overwrites**
`spotcheck_worksheet.csv` in the working directory. The adjudicated verdicts
live in `adjudication_199_edges.csv`; do not rely on `spotcheck_worksheet.csv`
in the repository root, which is an empty regenerated copy.

## Environment

Python 3.11 in a dedicated conda environment (`verify`) rather than a system
3.11 — the machine's system Python is 3.13.9. Exact library versions are in
`preflight_report.txt`.

## Conditional findings

Findings F2-F5 concern the locked §5 edge rule and are quoted from the
`PREREGISTRATION.docx` copy in this repository, which is labelled "Version 1.0
(draft for review)" and still contains `[to be completed]` placeholders. The
verifier did not open the registered copy on OSF to confirm the two are
identical. Those four findings are therefore conditional on the repository
copy being faithful to the registered text. The repository should ship the
registered version, or a link to the registration, rather than a draft marked
not-for-registration.

## Verifier independence

The verifier was added as a contributor to the OSF project `osf.io/utr47` on
2026-09-15, and appears in the contributor list of the registration. To be
stated plainly by the verifier in the pull request: when involvement began,
whether any finding was discussed with the analyst before filing, and that
contributor status was conferred after the verification work was complete.
