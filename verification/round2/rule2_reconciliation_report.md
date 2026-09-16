# Round 2 — reconciliation of Rule 2 against the 266 hand verdicts

> **SUPERSEDED IN PART — read this first.** The four-cell tables and precision
> figures in sections below were computed against the verifier's verdicts as
> originally filed. Six of those verdicts were subsequently found to be wrong and
> corrected (`CORRECTION_NOTICE.md`). The corrected figures are:
>
> | quantity | in the sections below | corrected |
> |---|---|---|
> | validation-sample precision, manual's criterion | 81.4% | **78.4%** (72.2-83.5) |
> | Rule 2 false removals | 7 | **1** (only K213591 → K202496) |
> | Rule 2 removal precision | 82.5% | **97.5%** (39/40) |
> | Rule 2 sensitivity to rejections | 89.2% | **90.7%** (39/43) |
> | Rule 2 precision on 159 survivors | 97.5% | 97.5% (unchanged) |
> | corpus estimate | ~3,572 (11.72%) | **~4,110 (13.48%)**, 2,500-7,558 |
> | error concentration | 4 of 45 documents, 37 rejections | **6 of 45, 43 rejections**; remaining 39 documents 123/123 |
>
> The six corrected edges are K221844 → K171808, K190830 and K241000 → K212746,
> K230295, K232303, K233980: each document names its predicates explicitly and
> separately, then lists these under `Reference Devices:`. They were recorded YES
> and should read NO under the manual's criterion.
>
> Nothing in the interpretation changes. The correction runs in Rule 2's favour —
> six of its seven apparent false removals were the rule working correctly — and
> it widens the gap between the manual's criterion and §8's from 2.5 to 5.5
> percentage points, which states the construct-validity finding more sharply.
> The sections below are retained unedited so the correction is auditable.

Gant Duncan, 2026-09-16. Tasks 2, 3, 4 and 5 of `FOR_THE_VERIFIER_round2.md`.
Task 1 (the frozen-input re-run) is pending the `data/text/` transfer.

All inputs: `excluded_edges.csv` (1,242 rows), `predicate_edges_rule1.csv`
(30,476 rows), `edge_rules.py`, and the three adjudication CSVs committed in
`verification/`.

## Counts reconcile exactly

30,476 − 1,242 = 29,234 edges; 538 documents carry an exclusion; 920 reference
zones + 322 compat zones = 1,242. Excluded confidence split: 926 NEAR_CUE,
316 DISTANT_CUE. All 1,242 exclusions are Rule 1 edges, and **all 266
adjudicated edges are present in the frozen-text Rule 1 graph** — so the
reconciliation below has no coverage gap.

## Task 2 — four-cell reconciliation

### Complete 199-edge validation sample (the only random draw)

| | removed by Rule 2 | kept |
|---|---|---|
| you rejected (NO) | 33 | **4** |
| you accepted (YES) | **7** | 155 |

- Rule 2 sensitivity to adjudicated rejections: **89.2%** (33/37)
- Rule 2 precision of its own removals: **82.5%** (33/40)

### All 266 adjudicated edges

| | removed | kept |
|---|---|---|
| rejected (NO) | 41 | 32 |
| accepted (YES) | 7 | 186 |

Sensitivity 56.2% (41/73). **This figure should not be quoted as Rule 2's
performance.** Two of the three samples are targeted draws deliberately
enriched for the failure modes; pooling them with the random draw understates
the rule. The 89.2% above is the unbiased estimate.

### Per sample

| sample | n | draw | sensitivity to rejections |
|---|---|---|---|
| validation 199 | 199 | random (seed 42, 45 documents) | 89.2% (33/37) |
| bin 11-25 | 45 | targeted, 3 documents | 0% (0/20) |
| reference-section | 22 | targeted, 12 documents | 50% (8/16) |

### The 32 misses, and where they are

`rule2_misses_32.csv`. They sit in **10 documents**, not 32:

| document | missed | sample | recorded location |
|---|---|---|---|
| K243839 | 20 | bin 11-25 | compatibility |
| K233507 | 3 | validation 199 | — |
| K223801 | 2 | reference-section | — |
| K072326, K173964, K192683, K200854, K231699, K232792, K253992 | 1 each | — | — |

**The 0% sensitivity in the 11-25 stratum rests on one document.** All 20 of
its misses are in K243839, a compatibility enumeration whose heading Rule 2 does
not recognise. Whether that generalises to the other 243 documents in that
stratum is untested — it is one document, and the document is the independent
unit.

## Why 1,242 and not ~3,572

A model, not a measurement, using the sensitivities measured above against the
stratified estimate:

| stratum | estimated spurious | measured Rule 2 sensitivity | predicted removals |
|---|---|---|---|
| bins 3-10 | 1,598 | 89.2% | ~1,425 |
| bins 11+ | 1,972 | ~0% (one document) | ~0 |
| predicted total | | | **~1,425** |
| actual | | | **1,242** |

The gap is not weak performance in ordinary documents — it is the high-K-load
strata, essentially in full. Rule 2 works where most documents live and does not
reach the enumerating documents where the estimated mass is concentrated.

Two consequences. Extending the rule to unheaded compatibility enumerations is
where the remaining ~2,000 edges are, and it needs real text to write against
rather than guesswork (`diagnose_zones.py` below). And the estimate itself rests
on 45 adjudicated edges in the 11-25 bin drawn from 3 documents, so widening
that sample would sharpen both numbers at once.

## Task 3 — precision on identical material

Same 60 seed-42 devices, same 199 Rule 1 edges, 40 removed, 159 surviving.

| rule | tier | edges | accepted | precision | Wilson 95% |
|---|---|---|---|---|---|
| Rule 1 | NEAR_CUE | 134 | 125 | 93.3% | 87.7-96.4% |
| Rule 1 | DISTANT_CUE | 65 | 37 | 56.9% | 44.8-68.2% |
| Rule 1 | both | 199 | 162 | **81.4%** | 75.4-86.2% |
| Rule 2 | NEAR_CUE | 123 | 122 | 99.2% | 95.5-99.9% |
| Rule 2 | DISTANT_CUE | 36 | 33 | 91.7% | 78.2-97.1% |
| Rule 2 | both | 159 | 155 | **97.5%** | 93.7-99.0% |

**81.4% → 97.5%** on identical material. The 40 removed edges comprise 33 true
rejections and 7 true predicates lost. DISTANT_CUE is the tier that changes
most: 56.9% → 91.7%, because that is where the enumerations sat.

## The 7 false removals — a code-level hypothesis

`rule2_false_removals_7.csv`.

| device | predicate | tier | zone | heading |
|---|---|---|---|---|
| K221844 | K171808, K190830 | NEAR_CUE | reference | `Reference Devices:` |
| K241000 | K212746, K230295, K232303, K233980 | DISTANT_CUE | reference | `Reference Devices:` |
| K213591 | K202496 | NEAR_CUE | compat | `fixation appliance and accessories (primary)` |

Rule 2 keeps a K-number mentioned at least once outside every zone, so for these
to be removed, every mention must fall inside a zone. **The likely cause is in
`exclusion_zones()`:** a zone is closed only when a `_zone_end()` line is found,
and otherwise runs to `len(text)`:

```python
if open_zone is not None:
    zones.append((open_zone[0], len(text), open_zone[1], open_zone[2]))
```

An unterminated `Reference Devices:` heading near the end of a document
therefore excludes the whole remainder — including any predicate named after it.
There is no maximum-zone-length guard, and `test_edge_rules.py` covers only
K190123 and K050441, neither of which exercises this path.

This is demonstrable on synthetic text. With a terminator present, the zone
bounds correctly at 21.6% of the document. With the same heading and no
terminator, the zone covers 73.0% of the document, runs to EOF, and swallows a
K-number the text explicitly calls "the predicate device" — `rule1` 2 edges,
`rule2` 0 edges, both excluded.

**Suggested fixes, either or both:** close an open zone at the first blank-line
block followed by a non-zone heading; and cap a zone at some fraction of the
document, on the grounds that a reference-device list is never half a summary.
Add a unit test on an unterminated zone.

The alternative explanation — that these seven are genuine reference citations
the verifier marked YES under the predicate-*or*-reference criterion rather than
the manual's narrower one — cannot be excluded without the source text, and
`K241000`'s four edges being DISTANT_CUE is mildly consistent with it. The
diagnostic settles which.

## Task 4 — reference-device reconciliation

| | edges |
|---|---|
| my `reference_device_edges.csv` | 1,136 |
| Rule 2 removals from reference zones | 920 |
| overlap | 656 |
| mine, kept by Rule 2 | 480 |
| Rule 2's, not in my file | 264 |

My file was produced by a **broader pattern**, which answers Cord's question
directly:

```
mine     (scan_reference_devices.py, REF_HEAD):
  reference\s+(?:device|product)s?\b[^\n]{0,40}$
Cord's   (edge_rules.py, REFDEV):
  (?:additional\s+)?reference\s+devices?(?:\s*\(s\))?\s*(?::|$)
```

Mine is broader on two axes: it matches **"reference product"** as well as
"reference device", and it allows **up to 40 characters of trailing text** after
the term, so `Reference Devices used in mechanical testing` is a heading to my
scanner and not to Rule 2. Rule 2 additionally requires `_heading_like()`, which
takes a line of ≤60 characters not ending in a period, so a long descriptive
reference heading fails there too.

Of the 480 mine-but-kept, the split is informative:

- **155** are in documents where Rule 2 *did* find a reference zone — so the
  K-number also appears outside it and the keep-if-mentioned-outside clause
  fired. These are probably correct retentions, and 6 of the 22 hand verdicts in
  the reference sample were YES for exactly that reason.
- **325** are in documents where Rule 2 found **no** reference zone at all — the
  heading-pattern difference above. Worst affected: K182321 (14), K142531 (11),
  then K162944, K241597, K233476, K161592 (6 each).

Tier split of the 480: 408 NEAR_CUE, 72 DISTANT_CUE.

The 264 Rule 2 removals absent from my file are the converse — headings his
pattern catches and mine did not, most likely the `additional reference
devices` and `reference device(s)` variants.

Neither enumeration is a ground truth. Mine was always stated as a floor with
unmeasured under-detection; this comparison measures the disagreement for the
first time, and the 325 give a concrete list to widen the rule against.

## Task 5 — K190123 → K170444

Closed. `adjudication_199_edges.csv` reads **YES**, tier `SECTION_HEADED`
(= NEAR_CUE), with the other 24 rows for that document all NO. Consistent with
Rule 2 keeping only K170444.

## Two items for the analyst

**`first_after_recall` rose when edges were removed** — 381 under Rule 1, 382
under Rule 2. Presumably removing a pair's earliest citation promotes a later
one past the recall date. Plausible, but counterintuitive enough that a reviewer
will stop on it, and it needs one sentence of explanation. Note that Rule 2's
382 coincidentally equals the verifier's Round 1 Rule 1 value from a different
retrieval; the two are unrelated.

**`rule2-rerun` branches from `b9344ae`**, which predates the verification
commit, so `verification/` is absent from that branch. The merge must preserve
it.

## Files

| file | contents |
|---|---|
| `rule2_reconciliation_266_edges.csv` | every adjudicated edge, its verdict, whether Rule 2 removed it, and its four-cell assignment |
| `rule2_misses_32.csv` | the 32 rejected-but-kept edges |
| `rule2_false_removals_7.csv` | the 7 accepted-but-removed edges with the heading that removed each |
| `rule2_precision_199sample.csv` | the precision table above |
| `diagnose_zones.py` | zone instrumentation; run from the repo root once `data/text/` is in place |

`diagnose_zones.py` usage:

```bash
python diagnose_zones.py K221844 K241000 K213591   # the 7 false removals
python diagnose_zones.py K243839                   # the 20 missed edges
python diagnose_zones.py --runaway                 # corpus-wide runaway zones
```

The first prints every zone with its span as a percentage of the document and
flags anything over 25%. The second prints the heading-like lines
`_zone_start()` rejected, with the reason, so a new exclusion pattern can be
written against real text. The third is the corpus-wide count of runaway zones,
which bounds how many true predicates the current rule may be discarding.

---

# Addendum — zone diagnostics on real documents

Run 2026-09-16 with `diagnose_zones.py` against the verifier's own 12,392-file
text corpus. The runaway-zone hypothesis in the section above is **wrong in its
mechanism and right that there is a defect**. Three separate problems, all in
`_zone_start` / `_heading_like` rather than in zone termination.

## Finding A — COMPAT matches FDA product-code names (91 removals)

`K213591`, the compat false removal:

```
compat  5339-5575  2.5%  'fixation appliance and accessories (primary)'
rule1 3 edges | rule2 2 | excluded 1
  excluded K202496  compat  NEAR_CUE  'fixation appliance and accessories (primary)'
```

The zone is 2.5% of the document — correctly bounded, not a runaway. But the
heading is not a compatibility section at all: **it is the device's own FDA
product-code / regulation name.** `COMPAT` matches the word "accessories" in it,
and the `SECTION_WORDS` veto does not fire because the line contains none of the
veto words.

Classifying all 1,242 removals by their opening heading:

| zone kind | heading | removals |
|---|---|---|
| compat | genuine compatibility heading | 231 |
| compat | **product-code / regulation name** | **91** |
| reference | reference heading | 920 |

**91 removals (7.3% of all removals, 56 of them NEAR_CUE) across 38 documents
come from product-code-name zones.** Representative headings:

```
accessories                                                    14
accessories.                                                   13
fixation appliances and accessories                             7
appliances and accessories Sec. 888.3030 Class II LXT           4
Appliances and Accessories (21 CFR 888.3030, Class 11,          4
Rod, Fixation, Intramedullary and Accessories (CFR 888.3020)    3
Fastener Appliances and Accessories;  Class II                  3
```

A product-code line typically sits near the top of a summary, so the zone it
opens runs until the next `_zone_end()` line and can cover a large share of the
document. The `--runaway` scan found **23 zones covering 28-57% of their
document, every one of them `compat`**, and every heading is a product-code
variant: `accessories`, `Accessories`, `appliances and accessories`,
`and accessories (21 CFR 888.3030)`, `fixation appliance and accessories`.

**Fix:** veto a candidate compat heading that also matches a regulation citation
(`21 CFR`, `888.\d+`, `Sec. 888`), a class designation (`Class I{1,3}`), a
three-letter product code, or that is a bare `accessories` / `appliances and
accessories` line. These are classification metadata, not section headings.

## Finding B — the 60-character heading threshold excludes real compat headings

`_heading_like()` accepts a line ending in `:`, a `Table` caption, a numbered
line, or any line of **≤60 characters** not ending in a period. Real
compatibility headings in these documents run past that:

```
not heading-like (len 65)  'compatibility information for DePuy ATTUNETM Revision Knee System'
not heading-like (len 73)  'compatibility information for DePuy Knee Prosthesis System Universal S'
not heading-like (len 63)  'compatibility information for DePuy Sigma PS Femoral Components'
not heading-like (len 66)  'compatibility information for DePuy S-ROMTM NOILES™ Rotating Hinge'
not heading-like (len 62)  'compatibility information for DePuy P.F.C. ™ SIGMA™ Total Knee'
```

Five genuine compatibility headings in one document, all 62-73 characters, all
rejected for being 2-13 characters too long. **Fix:** raise the bare-line
threshold, or accept any length up to `HEADING_MAX` when `COMPAT` matches and the
product-code veto in Finding A does not.

## Finding C — K243839's 20 misses are prose, not headings

```
=== K243839 — 14,625 chars, 300 lines ===
  NO EXCLUSION ZONES FOUND
  rule1 21 edges | rule2 21 | excluded 0
```

The rejected candidates are complete sentences:

```
SECTION_WORDS veto         'The Alteon HA Femoral Stems are compatible with the same femoral compo'
not heading-like (len 85)  'The Alteon HA Femoral Stems are compatible with the same acetabular co'
not heading-like (len 83)  'The subject and predicate devices are composed of the same or similar '
```

This answers Cord's question directly: **the remainder are prose enumerations
with no heading of any kind.** A heading-anchored rule cannot reach them, and
widening `_heading_like` far enough to catch a sentence would make every line a
heading candidate.

**Fix, if it is worth doing:** a separate sentence-level rule — a K-number in a
sentence matching `is/are compatible with`, `for use with`, `may be used with`
and containing no cue word is excluded — kept distinct from the zone mechanism
and unit-tested on K243839. Worth weighing against the alternative of reporting
the residual as a measured limitation, since 20 of the 21 edges in this document
are affected and prose enumeration may be rare outside the high-K-load stratum.

## Revised reading of the 7 false removals

Finding A explains `K213591 → K202496` outright: a product-code zone, not a
compatibility section. The six `Reference Devices:` removals in `K221844` and
`K241000` are a different matter — those zones are genuine reference headings,
so either the K-number truly appears only inside the reference list (making the
verifier's YES a predicate-*or*-reference judgement rather than a defect in the
rule), or a `_zone_end()` line is being missed. The zone percentages for those
two documents settle it and should be read off the top of the
`diagnose_zones.py K221844 K241000 K213591` output.

## Two new corpus facts

`TEXT_SNAPSHOT.json` records **146 empty text files** among the 12,388 retrieved
— documents that extracted to nothing and can therefore contribute no edges.
The verifier's own freeze reports the same 146. This belongs in the coverage
cascade, which previously stopped at "12,392 retrieved".

The manifest accounting reconciles the eight-field finding exactly:

| | verifier | analyst |
|---|---|---|
| retrieved (`200`) | 12,392 | 12,388 |
| unavailable | 921 (`404`) | 924 (`404`) + 1 (`-1`) |
| attempted | 13,313 | 13,313 |

Four documents FDA served the verifier and returned 404 for the analyst, plus
four whose extracted text differs between the two retrievals — eight documents
of divergence, which is the residual behind the +11 edges.

## A safety note on freeze_text.py

`python freeze_text.py --help` does not print help. The unrecognized argument is
ignored and **the script performs a freeze**, overwriting `TEXT_SNAPSHOT.json`
and `TEXT_SNAPSHOT_files.csv` with the local corpus. This happened during this
session and was reverted with `git checkout --`. A script whose default action
destroys the reference record it exists to protect should require an explicit
`--freeze`, and should reject unknown flags.
