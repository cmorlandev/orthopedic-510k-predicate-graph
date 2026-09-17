## Round 2 verification — complete

Pushed to this branch as `ae0f4f9`; cherry-picked to `main` as `b437a54`.
Everything below is in `verification/round2/` — start with
`rule2_reconciliation_report.md`.

**Read `CORRECTION_NOTICE.md` first.** Six of my Round 1 validation-sample
verdicts were wrong and are corrected; two figures in the filed report moved.
Your reconciliation task is what surfaced them.

---

### Task 1 — reproduction on the frozen inputs: PASS

`freeze_text.py --check` PASS · `test_edge_rules.py` 5/5 · notebooks 01, 03, 04,
05, 06, 08 Restart-and-Run-All in order, 02 skipped · `compare_to_reference.py`:

```
RESULT: PASS — all deterministic values reproduce exactly.
```

**29 of 29 fields exact**, including `text_corpus_sha256` character for
character and `sens_maximal_rule [938, 2877, 1873]`. Evidence:
`task1_compare_to_reference.txt`, `task1_expected_values_verifier.json`.

The Stage 3 gate fix works — `12388 documents in the frozen text corpus`, my four
extra documents correctly ignored. Thanks for turning that round the same day.

Scope worth stating explicitly in the manuscript: this reproduces everything
**downstream of the frozen text**, which is every preregistered confirmatory
quantity except H4. Stage 2 retrieval remains non-reproducible (that is D5, not a
gap) and Stage 7 reads MAUDE live.

### The eight-field finding is closed from both directions

Forward: the four summaries FDA served me and 404'd for you —
**K021661 (0 edges), K041939 (1), K192214 (8), K192217 (2)** — carry exactly
**11** edges. 30,487 − 11 = 30,476.

Three of those eleven cite **recalled** predicates, which accounts for all four
derived deltas by four independent counts:

| field | delta | why |
|---|---|---|
| `post_recall_citations` | +3 | the three edges with a recalled predicate |
| `downstream_devices` | +2 | the two citing documents, K192214 and K192217 |
| `persistent_predicates` | +1 | K112429 had 0 citations in your graph (K042695 has 9, K061211 has 3) |
| `first_after_recall` | +1 | K112429 recalled 2017-03-17, K192214 cleared 2019-10-11 — its only citation, 938 days later |

Reverse: `sens_maximal_rule` reproduces the August triple on my machine too.
Hold retrieval fixed and the difference vanishes.

**Also: every one of the 12,388 summaries we both retrieved extracted to
byte-identical text** (`identify_text_diffs.py`, `text_corpus_diffs.txt`).
PyMuPDF output was identical across two machines eighteen days apart. Extraction
is not a source of variation in this study; retrieval is the only one, and D5 can
say that as a measured claim.

**The pandas confounder in §8 of the state-of-play memo is ruled out.** My env
runs the pinned **2.1.4** (`requirements.txt`: `pandas==2.1.4`). Separately, its
premise does not hold: K060694's recall dates in `snapshot/recall_raw.json.gz` are
2005-08-23 / 2005-10-07 / 2005-12-08, ordinary dates with no year-0012 value in
any of that device's 153 recall records. Worth keeping as a hazard note for
unpinned runs, but it is not an alternative explanation. Evidence:
`check_pandas_confounder.py`, `pandas_confounder_check.txt`.

### Rule 2 performance, re-scored on the corrected verdicts

On the 199-edge seed-42 sample — the only random draw:

| | value |
|---|---|
| sensitivity to my rejections | **90.7%** (39/43) |
| precision of its removals | **97.5%** (39/40) |
| precision on surviving edges | **97.5%** (155/159) |
| false removals | **1** |
| Rule 1 → Rule 2 precision, identical material | **78.4% → 97.5%** |

Do not quote a pooled figure over all 266 verdicts (that would read 56.2%) — two
of the three samples are targeted draws deliberately enriched for the failure
modes. The 90.7% is the unbiased estimate.

The 1,242-vs-~4,110 gap is the high-K-load stratum, essentially in full: Rule 2
catches ~90% of rejections in ordinary documents and, on the evidence of one
document, nothing in the enumerating ones. Files:
`rule2_reconciliation_266_edges.csv`, `rule2_misses_32.csv`,
`rule2_false_removals_7.csv`, `rule2_precision_199sample.csv`.

### Three defects in `edge_rules.py`

All in `_zone_start` / `_heading_like`, not in zone termination. `diagnose_zones.py`
reproduces each.

**A — `COMPAT` matches FDA product-code names.** K213591's zone opened on
`fixation appliance and accessories (primary)`, which is the regulation name, not
a section. **91 removals across 38 documents** come from these, 56 of them
NEAR_CUE. `--runaway` finds **23 zones covering 28-57% of their document**, every
one a product-code variant: `accessories`, `appliances and accessories Sec.
888.3030 Class II LXT`, `Rod, Fixation, Intramedullary and Accessories (CFR
888.3020)`. Suggest vetoing candidates that also match a CFR citation, a class
designation, or a bare `accessories` line. **This is the one genuine false
removal.**

**B — the 60-character bare-line threshold is too tight.** One document has five
`compatibility information for DePuy …` headings at 62-73 characters, all
rejected for being 2-13 characters too long.

**C — K243839's misses are prose, no heading at all.** `NO EXCLUSION ZONES
FOUND`, 21 edges, 20 rejected. The candidates are sentences: *"The Alteon HA
Femoral Stems are compatible with the same femoral components…"*. A
heading-anchored rule cannot reach this. Either a separate sentence-level pattern
or report the residual as a measured limitation — your call, and it is the one
design decision in here.

### Written record — nine edits

Full detail in `TASK6_written_record_review.md`. Every arithmetic check in
RUN_LOG and DEVIATIONS passes; these are the figures that moved plus the
hygiene items.

1. D4 corpus estimate → 13.5% / 8.2-24.8% / ~4,110, and name the denominator graph.
2. D4 concentration → 6 of 45 documents, 43 rejections; remaining 39 were 123/123.
3. D4 precision → 78.4% (72.2-83.5) where cited.
4. D4: soften "independent" to the second-analyst formulation.
5. D5: add the 146 empty text files to the coverage cascade.
6. RUN_LOG: Stage 4 count, Stage 5 Class III, Stage 3 tier split, Part One public URL; plus a Part Four cross-reference so 121/121 and 78.4% are not read as contradicting (different samples, different criteria; under §8's criterion mine is 83.9%).
7. RUN_LOG Part Five Stage 3: Rule 1 `devices with >=1 edge` should read **8,978**, not 8,981 — 8,981 was my August figure on the 30,487-edge graph. My reproduction prints 8,978, matching §4 of your memo.
8. Tooling: `freeze_text.py` should require an explicit `--freeze` and reject unknown flags (`--help` performed a freeze and overwrote `TEXT_SNAPSHOT.json`; reverted with `git checkout --`). `estimate_spurious_edges.py` accepted a targeted-draw calibration without complaint and returned 22.31% where the correct input gives 13.48%.
9. `test_edge_rules.py`: add K241000 (five reference zones in one 52k-character document) and ideally K072326, K221844, K233507 — all now known to carry rejections and none currently covered.

### One thing you may want for the manuscript

**K112429 → K192214 is a clean worked example of H2.** A Class II recall
(Z-2072-2017, Eden Spine Europe SA) for *"implants … disassembled by surgeons
because of unscrewing completely the locking screw"*, and 2.57 years later a new
device is cleared citing that recalled device as its predicate — its only
citation in the corpus. It survives Rule 2. H2 reports 382 such devices; this is
one of them with recall reason, dates and provenance all traceable. A named
instance does work an aggregate count cannot.

### Still yours

The **OSF §5 check** — it decides whether D4 is a rule change or an
implementation correction, and therefore the wording of the deviation paragraph.
Everything else on my side is done.
