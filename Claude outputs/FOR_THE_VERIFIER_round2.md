# Round 2 — what the verifier needs to do to close out

Cord Morlan, 2026-09-16. Response to `FOR_THE_ANALYST.md`. Branch `rule2-rerun`, pull request open.

## What was decided and done

Your recommendation (a) was adopted: the edge rule is restricted, the registered rule is kept as a sensitivity arm, and the change is recorded as a deviation (`DEVIATIONS.md` D4). The extracted text corpus is frozen (D5) and three post hoc sensitivity arms were added (D6): the registered maximal rule, recalled devices with `n/a` severity class, and the linked-only H4 comparison. `00_freeze_snapshot` was not run; `snapshot/` is unchanged. The August `expected_values.json` is preserved as `expected_values_REFERENCE_rule1_2026-08-08.json`.

The restricted rule (Rule 2) lives in `edge_rules.py`. It is Rule 1 minus any K-number whose every mention falls inside an exclusion zone: the span from a heading-like line denoting component/accessory compatibility or reference devices to the next line that begins a different section. A K-number mentioned at least once outside every zone is kept, so a predicate that also appears in a compatibility table survives. The rule is unit-tested on K190123 and K050441 (`test_edge_rules.py`) and reproduces your verdicts on both: K190123 keeps only K170444; K050441 keeps K921301 and K943230.

Results from the re-run, all in `RUN_LOG.md` Part Five:

| | Rule 1 (registered) | Rule 2 (primary) |
|---|---|---|
| edges | 30,476 (= August, exact) | 29,234 |
| removed | — | 1,242 in 538 documents (920 reference-device zones, 322 compatibility zones) |
| H1 persistent / citations / downstream | 938 / 2,877 / 1,873 (= August, exact) | 921 / 2,712 / 1,798 |
| H2 first-after-recall | 381 | 382 |
| H3 max gap | 21 | 21 |
| connected / largest component / depth | 12,010 / 11,734 / 30 | 11,960 / 11,638 / 30 |

H4: 17 vs 0 median events, 1.085 vs 0.000 per device-year, linkage 84.3% vs 49.6%, p = 1.0e-113. Linked-only: 1,156 vs 680 devices, 28 vs 7, 1.76 vs 0.50, p = 7.0e-35. Stage 8: 17/17.

Rule 1 reproducing the August H1 triple exactly from the frozen text is the confirmation of your eight-field diagnosis: with retrieval held fixed, the drift disappears and the only remaining difference between the two graphs is the rule.

## What is still open

**Rule 2 removed 1,242 edges. Your corpus-wide estimate was ~3,572.** The rule catches the structured cases (headed reference-device sections, headed compatibility sections and tables) and evidently not the rest of what you rejected. Whether the remainder are prose enumerations without a heading, tables whose caption doesn't use the words the rule looks for, or something else, is the question only your verdicts can answer. This is the main item below.

**The registered §5 has still not been compared against the repo's draft copy.** That is on Cord (OSF link in `RUN_LOG.md` Part One), but if you get to it first, say so in the PR. It decides whether D4 reads as a deviation from the registered rule or a correction toward it.

## Tasks

### 1. Reproduce the Rule 2 run on the frozen inputs

Pull `rule2-rerun`. Get `data/text/` from Cord (12,388 files; it will be on OSF, but for now a direct transfer is fine) and put it under `data/`. Then, from the repo root:

```
python freeze_text.py --check        # must print PASS — your copy of the text matches TEXT_SNAPSHOT.json
python test_edge_rules.py            # five ok lines
```

Run notebooks 01, 03, 04, 05, 06, 08 in order (Restart Kernel and Run All Cells). Skip 02: nothing reads the PDFs any more. Then:

```
python compare_to_reference.py
```

Every field must now match exactly, including the four that used to sit in the drift tier. There is no tolerance. If any field differs, report it before anything else; it means the frozen inputs are not identical between the two machines.

07 is optional and will not match: it reads the live MAUDE endpoint. If you run it, report direction and the linked-only result, as before.

### 2. Reconcile Rule 2 against your 266 verdicts

`data/excluded_edges.csv` (attached to the PR; also produced by your own Stage 3 run) lists every edge Rule 2 removed, with the zone type and the heading line that opened the zone. Join it to your two adjudication CSVs on (device, predicate) and sort every adjudicated edge into four cells:

| | removed by Rule 2 | kept by Rule 2 |
|---|---|---|
| you rejected | correct removal | **miss** — list each, with where in the document the number sits |
| you accepted | **error** — list each, with the heading that removed it | correct retention |

The two bold cells are what matter. For the misses, a one-line note per edge on the document structure (prose sentence, unheaded table, table with a caption the rule didn't recognise, list under an unexpected heading) is what will let the rule be tightened deterministically rather than by guesswork. For the errors, the heading text is already in the CSV; what's needed is why the K-number is a true predicate despite sitting there.

Also report the same four-cell table restricted to the 199-edge complete validation sample, since that is the only one of your three samples that is a random draw.

### 3. Re-adjudicated precision under Rule 2

`data/validation_sample.csv` now holds the Rule 2 edges for the same 60 seed-42 devices; `data/validation_sample_rule1.csv` holds the Rule 1 edges for comparison. Because you already have verdicts on all Rule 1 edges in that sample, Rule 2 precision on identical material is just a count: surviving edges, how many of them you accepted, Wilson interval. Report it alongside the Rule 1 figure (81.4%, 75.4–86.2%) and by tier (`NEAR_CUE` / `DISTANT_CUE`).

### 4. Reconcile the reference-device count

Your `reference_device_edges.csv` enumerates 1,136 candidate reference-section edges. Rule 2 removed 920 from reference zones. Which of your 1,136 did it keep, and does the heading in those documents differ from the "Reference Device:" pattern the rule expects? If your file was produced by a broader pattern, say what it was.

### 5. K190123 → K170444

Your consistency item. The document names K170444 under "IV. Predicate Device:" and again in Table #1, so YES is correct and Rule 2 keeps it. Confirm the CSV reads YES and close the item.

### 6. Review the written record

`DEVIATIONS.md` D1 (date corrected to 2026-08-08), D3–D6, and `RUN_LOG.md` Stages 1–5 and Part Five. Two specific things: whether D4 describes what you found accurately, and whether the contributor-status wording matches what you wrote in section 9 of your report. Your Stage 2 retrieval count (12,392) and Cord's (12,388, now recorded from the manifest) are both in D5; check the numbers against your `preflight_report.txt`.

### 7. Update the verification record

Add a Round 2 section to `verification/PULL_REQUEST.md` with the `compare_to_reference.py` result on the frozen inputs, the four-cell reconciliation, the Rule 2 precision, and the reference-device reconciliation. Once it's in, the reproduction result the manuscript cites is that run, not `08_verify`.

## What happens with your answers

If the reconciliation shows Rule 2 removes what you rejected and keeps what you accepted, the numbers above go into the manuscript as they stand. If it shows a class of misses with a recognisable structure, the rule gets one more exclusion pattern, another unit test, and one more Stage 3–8 pass, and the manuscript waits for that. Either way the decision about which is the last thing that changes before the manuscript is written from the run log.
