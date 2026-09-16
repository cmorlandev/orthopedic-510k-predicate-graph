# Task 6 — review of DEVIATIONS.md D1, D3-D6 and RUN_LOG.md

Gant Duncan, 2026-09-16. Reviewed against `preflight_report.txt`, the
adjudication CSVs, and the Round 2 reconciliation.

## Verdict

The written record is accurate, unusually complete, and discloses the things it
would be easiest to omit. D5 in particular reports the verifier's retrieval count
alongside the analyst's and withdraws §2's static-documents claim outright. Six
items need changing, five of them numbers that moved after this review found an
error in the verifier's own adjudication.

## Arithmetic checks — all pass

| check | result |
|---|---|
| 30,476 − 1,242 = 29,234 | ✓ |
| 920 reference + 322 compat = 1,242 | ✓ |
| NEAR_CUE 21,541 + DISTANT_CUE 7,693 = 29,234 | ✓ |
| Class I 11 + II 1,306 + III 18 + n/a 356 = 1,691 | ✓ |
| manifest 12,388 + 924 + 1 = 13,313 | ✓ |
| devices losing all edges: 8,981 − 8,942 = 39 ≈ 0.29% coverage line | ✓ |
| linked-only n: 1,372 × 84.3% ≈ 1,156; × 49.6% ≈ 680 | ✓ |
| `sens_maximal_rule` [938/2877/1873] = the 2026-08-08 H1 triple | ✓ exact |

That last row is the substantive confirmation of the eight-field diagnosis: with
retrieval held fixed, Rule 1 on the frozen text reproduces August exactly, and
the only remaining difference between the two graphs is the rule.

## D4 — accurate as written, but five figures have moved

D4 describes the finding correctly: the extractor implements §5 exactly, the
discrepancy is in what §5 captures, and errors are concentrated rather than
diffuse. Rule 2's construction, the unit tests, the `excluded_edges.csv`
disclosure and the post-hoc labelling are all stated properly. Two of the three
offending structures it names are the ones the adjudication found.

**Required changes.** Six verdicts in the verifier's validation sample were
corrected on 2026-09-16 (see `CORRECTION_NOTICE.md`): K221844 → K171808, K190830
and K241000 → K212746, K230295, K232303, K233980 were recorded YES and should
read NO — each document names its predicates explicitly and separately, then
lists these under `Reference Devices:`. Consequently:

| in D4 | as written | should read |
|---|---|---|
| corpus estimate | 11.7%, interval 7.3-22.4%, ~3,572 of 30,487 | **13.5%, interval 8.2-24.8%, ~4,110 of 30,487** |
| concentration | 4 of 45 documents produced all 37 rejections | **6 of 45 documents produced all 43 rejections** |
| clean remainder | remaining 41 documents were 155/155 correct | **remaining 39 documents were 123/123 correct** |
| precision (if cited) | 81.4% | **78.4%**, 95% CI 72.2-83.5 |

The concentration claim survives the correction — 6 documents of 45 still hold
every rejection — but the two new ones are the reference-only documents, so the
mechanism list should mention that a reference section can account for a
document's entire error load.

**Unit-test gap.** `test_edge_rules.py` covers K190123 and K050441. Four further
documents in the validation sample are now known to carry rejections —
**K072326, K221844, K233507, K241000** — and none is tested. K241000 is the
useful one to add: five separate `Reference Devices:` zones in a 52,085-character
document, which exercises multi-zone handling.

**Denominator note.** The corpus estimate was computed on the verifier's
`predicate_edges.csv` (30,487 edges), not Cord's Rule 1 graph (30,476). The
percentage is unaffected to two decimals (13.48% vs 13.49%), but D4 should say
which graph the denominator is.

## D4 — one wording point on independence

D4 says "independent hand adjudication ... (second analyst, 2026-08/09)". The
parenthetical is right; "independent" is doing more work than the facts support.
The verifier was added as a project contributor on 2026-08-09 — after
registration and one day after the confirmatory run, so he could not have
influenced the plan, the rule, the code or the reference values, but contributor
status preceded the verification. Section 9 of the verification report states
this. Suggested: "hand adjudication by a second analyst who joined the project
after the confirmatory run and contributed to neither the plan nor the pipeline".
The manuscript should not say "independently verified" without that clause.

## D5 — accurate, and the numbers match the verifier's own record

Retrieval counts (12,392 verifier / 12,388 analyst), the +0.036% edge delta, all
four field deltas and the 0.262% maximum all match `preflight_report.txt` and the
filed comparison exactly. The choice to freeze the analyst's 2026-08-08
extraction rather than the verifier's later pull is the right one — it is the
confirmatory-run basis — and D5 says so explicitly.

**One addition worth making.** `TEXT_SNAPSHOT.json` records **146 empty text
files** among the 12,388, and Part Five notes them. That number belongs in the
manuscript's coverage cascade, which currently stops at "retrieved": 15,581
devices → 13,313 with a summary listed → 12,388 retrieved → 12,242 with any
extractable text → 8,942 with ≥1 Rule 2 edge. A scanned PDF with no text layer
can hold no edges under either rule, and stating that pre-empts the question.

**One safety point on the tooling.** `python freeze_text.py --help` does not
print help. The unrecognized argument is ignored and the script performs a
freeze, overwriting `TEXT_SNAPSHOT.json` and `TEXT_SNAPSHOT_files.csv` with
whatever is in `data/text/`. This happened during this review and was reverted
with `git checkout --`. Given that the file exists precisely to detect corpus
drift, freezing should require an explicit `--freeze` and unknown flags should
error. The same argument applies to `estimate_spurious_edges.py`, which accepted
a targeted-draw calibration file without complaint and returned 22.31% where the
correct input gives 13.48%.

## D1, D2, D3, D6 — no changes needed

**D1** — the date correction to 2026-08-08 is recorded and matches
`SNAPSHOT.json` and the run log. The integrity argument is sound: the §3.4
confirmatory quantities did not exist at registration, so expanding the corpus
cannot expose them to hindsight. The registered snapshot is preserved at
`snapshot_registered_2026-07-21/`, which closes the item the verification raised
about the registered basis being unreproducible.

**D2** — the near-DAG handling is correct and conservative: the locked rule is
not altered, `is_dag` is reported false, and depth is computed on the
condensation. Reporting 30,472/30,476 as temporally valid is the right level of
detail.

**D6** — all four post-hoc arms are labelled as such and each has a stated
reason. `sens_class_na` addresses the 356-device gap the verification raised, and
the linked-only H4 arm addresses the differential-linkage confound with the
direction holding (1.76 vs 0.50, p = 7.0e-35). The §9 non-pilot panel is
implemented and skips cleanly when `pilot_codes.txt` is absent.

## RUN_LOG.md — four blanks and one cross-reference

| location | issue |
|---|---|
| Part One | public registration URL / DOI still `TODO`. The view-only link is not citable. |
| Part Three, Stage 4 | `[count from data/recall_links.csv]` — still blank |
| Part Three, Stage 5 | `Class III [fill]` — blank, though Part Five gives 18 |
| Part Three, Stage 3 | tier split recorded as "as in Stage 6 sensitivity" rather than as numbers |
| Part Four | records 100.0% (121/121) with no pointer to the verifier's figure |

Stage 2 is now filled in (12,388 / 924 / 1, recorded 2026-09-16 from the
manifest), which closes the gap the verification flagged — that was the one
number capable of settling the eight-field difference outright, and it does.

**Part Four needs a cross-reference, not a change.** A reader who sees 100.0%
(121/121) in the run log and 78.4% in the verification report will assume one of
them is wrong. They measure different things: different samples, and different
criteria — §8's predicate-or-reference criterion for the analyst's 121, the
manual's narrower predicate-only criterion for the verifier's 199. Under §8's
criterion the verifier's sample gives 83.9%. One line under Part Four saying so
would prevent the inference.

## Summary of requested edits

1. D4: corpus estimate → 13.5% / 8.2-24.8% / ~4,110, and name the denominator graph.
2. D4: concentration → 6 of 45 documents, 43 rejections, 39 documents 123/123.
3. D4: precision → 78.4% (72.2-83.5) where cited.
4. D4: soften "independent" to the second-analyst formulation.
5. D5: add the 146 empty text files to the coverage cascade.
6. RUN_LOG: fill Stage 4, Stage 5 Class III, Stage 3 tier split, Part One URL; add the Part Four cross-reference.
7. Tooling: `--freeze` should be explicit in `freeze_text.py`; both scripts should reject unrecognized arguments.
8. `test_edge_rules.py`: add K241000 (multi-zone) and ideally K072326, K221844, K233507.
