# Independent verification — Orthopedic 510(k) Predicate-Graph Study

**Verifier:** Gant Duncan
**Rebuild:** 2026-08-26 to 2026-09-16, macOS, Python 3.11 (conda env `verify`)
**Snapshot verified:** 2026-08-08, SHA-256 of all four files recorded in `verification/preflight_report.txt`
**Evidence:** `verification/` — 26 files. Start with `verification/adjudication_summary.txt`.

---

## Verdict

**Reproduced with explained differences, plus one substantive methodological finding.**

Twelve of twenty reference values reproduced exactly. Eight differ, all in the
same direction and none by more than 0.3%; the cause is structural and is not a
defect in either the pipeline or this rebuild. The MAUDE comparison reproduced
with the same direction, the same effect measures and the same significance.

No implementation defect was found anywhere. The extractor is faithful to the
preregistered edge rule. The substantive finding is that the preregistered rule
measures something broader than the hypotheses describe, and hand adjudication
of 266 candidate edges measures how much broader.

`00_freeze_snapshot` was never run. No notebook source was modified — verified
cell-by-cell against `HEAD` for all eight notebooks.

---

## 1. What reproduced exactly

| | value |
|---|---|
| `corpus_devices` | 15,581 |
| `connected_nodes` | 12,010 |
| `largest_component` | 11,734 |
| `recalled_nodes` | 1,691 |
| `pct_recalled` | 10.9 |
| `max_chain_depth` | 30 |
| `max_gap_years` | 21 |
| `is_dag` | False |
| `cov_resolvable_pct` | 72.5 |
| `cov_out_of_scope_pct` | 12.2 |
| `snapshot_date` | 2026-08-08 |
| plus one further field | — |

Stage checkpoints also matched the snapshot manifest: 15,581 unique devices and
13,313 with a summary, against `n_510k_raw` and `n_with_summary`. Record counts
in all three snapshot data files matched `SNAPSHOT.json` exactly (15,581 /
6,297 / 4,096), and the four files' hashes are recorded.

**An integrity check that passes and is worth stating:** the shipped
`expected_values_REFERENCE.json` matches the analyst's contemporaneous
`RUN_LOG.md` on all fourteen Stage 6 values. The reference was not adjusted
after the fact.

**And the registration checks out.** The OSF registration (OSF Registries, OSF
Preregistration template, embargoed) is dated 2026-07-28 17:17:21 — eleven days
before the confirmatory run on 2026-08-08. §12 step 1 is satisfied and the
anti-HARKing protection described in §1 is intact. An embargoed registration is
still an immutable timestamped snapshot; only public visibility is deferred.

## 2. What did not reproduce, and why

| field | analyst | this rebuild | delta | rel. |
|---|---|---|---|---|
| `edges` | 30,476 | 30,487 | +11 | +0.036% |
| `persistent_predicates` | 938 | 939 | +1 | +0.107% |
| `post_recall_citations` | 2,877 | 2,880 | +3 | +0.104% |
| `downstream_devices` | 1,873 | 1,875 | +2 | +0.107% |
| `first_after_recall` | 381 | 382 | +1 | +0.262% |
| `sens_class_I_II` | [718, 2141, 1436] | [719, 2144, 1438] | [+1, +3, +2] | |
| `sens_high_conf` | [838, 2209, 1563] | [839, 2212, 1565] | [+1, +3, +2] | |
| `sens_combined` | [654, 1660, 1214] | [655, 1663, 1216] | [+1, +3, +2] | |

Every difference is positive and the largest is 0.262%. All three sensitivity
triples shifted by the identical `[+1, +3, +2]`.

**Cause: the summary PDFs are not in the frozen snapshot.** The snapshot holds
three metadata files. The ~12,400 summary PDFs — the only place predicate
relationships are written — are fetched live from accessdata.fda.gov by Stage 2.
Stage 2 ran here on 2026-08-26, eighteen days after the analyst's. Additional
documents became retrievable in that window, which adds outgoing edges without
adding nodes — consistent with `connected_nodes` and `largest_component` being
identical while `edges` rose by 11.

Corroborating evidence: identical metadata hashes; every difference positive;
node counts unchanged; and accessdata.fda.gov returned application errors during
the adjudication window, observed directly, confirming the source is not stable
between runs.

Three causes the comparison script suggests are excluded. Not a wrong snapshot —
`snapshot_date` and `corpus_devices` both pass. Not library drift — that moves
graph metrics in both directions and would move `largest_component`,
`connected_nodes`, `max_chain_depth` or `is_dag`, all of which are identical.
Not out-of-order execution — every stage was run with Restart-and-Run-All in
sequence.

**This makes the eight fields non-reproducible by construction, not by error.**
§2 of the preregistration states the summary PDFs "are static documents"; the
evidence above contradicts that. The claim in `FOR_THE_VERIFIER.md` that every
reference value is "deterministic, computed only from the frozen snapshot" does
not hold for these eight.

*Still open:* `RUN_LOG.md`'s Stage 1-5 entries are blank, so the analyst's Stage
2 retrieval count was never recorded. A figure near 12,381 would close this
outright. See question 3.

## 3. MAUDE (manual step 17) — passes

| measure | analyst | this rebuild | |
|---|---|---|---|
| family events | 850,885 | 855,261 | +0.51% |
| deaths | 2,443 | 2,458 | +0.61% |
| injuries | 645,900 | 648,700 | +0.43% |
| match rate, recalled arm | 84% | 84% | identical |
| match rate, matched arm | 49% | 49% | identical |
| median events | 17 vs 0 | 17 vs 0 | identical |
| events/device-year | 1.07 vs 0.00 | 1.07 vs 0.00 | identical |
| Mann-Whitney | p = 6.4e-118 | p = 5.21e-118 | both ≪ 0.05 |

Pulled 2026-09-15, twenty days after the analyst's. Direction holds, the test is
significant, and counts grew 0.4-0.6% exactly as the manual anticipates for live
MAUDE.

The match rates reproducing **exactly** strengthens rather than dissolves the
confounding concern in F11 below: a 35-point gap that reproduces to the
percentage point is structural, not noise.

## 4. Hand adjudication — 266 edges, 60 documents

The manual (§9) asks for two or three devices. Three samples were adjudicated,
all by a single reader.

**Sample A — the complete validation sample** (199 candidate edges, 45
edge-bearing documents; notebook 03 drew 60 documents with retrievable text, 45
of which had at least one extracted edge — 75%, which independently corroborates
the reported `cov_resolvable_pct` of 72.5%).

| criterion | precision | Wilson 95% CI |
|---|---|---|
| manual §9, "genuinely cited as predicates" | 162/199 = **81.4%** | 75.4-86.2% |
| prereg §8, "predicate/reference citations" | 167/199 = 83.9% | 78.2-88.4% |
| prereg §8, most generous reading | 171/199 = 85.9% | 80.4-90.1% |

Per tier, on the manual criterion: `SECTION_HEADED` 134 edges, 93.3%;
`PROXIMITY_ONLY` 65 edges, 56.9%.

**The structure matters more than the rate.** All 37 rejections came from 4 of
the 45 documents:

| | documents | edges | rejections | precision |
|---|---|---|---|---|
| ordinary documents | 41 | 155 | **0** | **100.0%** (CI 97.6-100%) |
| enumerating documents | 4 | 44 | 37 | 15.9% |

**Sample B — the 11-25 K-number bin** (45 edges, 3 documents), adjudicated to
calibrate the one corpus stratum Sample A left empty, recording for each edge
*where in the document* the K-number sits:

| document | edges | accepted | rejected | location |
|---|---|---|---|---|
| K160652 | 11 | 11 | 0 | all under a predicate heading |
| K163577 | 13 | 13 | 0 | all under a predicate heading |
| K243839 | 21 | 1 | 20 | compatible-components enumeration |

44.4% rejected (CI 30.9-58.8%). Location notes: 25 "predicate", 20
"compatibility", **zero** "reference".

**Sample C — reference-section targeted** (22 edges, 12 documents), calibrating
the reference-device population rather than testing for a defect: 72.7%
reference-only (CI 51.8-86.8%), 76.5% within `SECTION_HEADED`.

Samples B and C are targeted draws and are **not** pooled into a single
precision figure.

**One document was audited in full.** K190123's PDF was read end to end and all
25 of its verdicts checked against the source. Every verdict was correct and
tracked the document's own section structure: the single K-number under "IV.
Predicate Device" accepted, the five under "V. Reference Device" rejected, the
nineteen in "X. Component and Accessory Compatibility" rejected. Extracted text
is in `verification/K190123_text.txt` so the audit is checkable.

## 5. Corpus-wide estimate

Every edge-bearing document was binned by the number of distinct K-numbers in
its extracted text; the rejection rate within each bin was measured from the
adjudicated edges falling in it and applied to all corpus edges in that bin.
Phrase-independent, and calibrated on 244 verdicts (Samples A and B; Sample C is
excluded because it does not bin by K-number load).

| K-numbers | docs | edges | adjud | rejected | rate | 95% CI | est. non-predicate |
|---|---|---|---|---|---|---|---|
| 1-2 | 4,176 | 6,103 | 25 | 0 | 0.0% | 0.0-13.3% | 0 |
| 3-5 | 3,412 | 12,208 | 53 | 1 | 1.9% | 0.3-9.9% | 230 |
| 6-10 | 1,121 | 7,756 | 68 | 12 | 17.6% | 10.4-28.4% | 1,368 |
| 11-25 | 244 | 3,392 | 45 | 20 | 44.4% | 30.9-58.8% | 1,507 |
| 26+ | 28 | 1,028 | 53 | 24 | 45.3% | 32.7-58.5% | 465 |
| **total** | 8,981 | 30,487 | 244 | 57 | **11.72%** | 7.32-22.38% | **~3,572** |

**~3,572 of 30,487 edges (11.7%), interval 2,232-6,823 (7.3-22.4%).** No bin is
uncalibrated.

The rate rises monotonically and then plateaus above roughly ten K-numbers —
0.0%, 1.9%, 17.6%, 44.4%, 45.3% — which is the dose-response a
document-structure mechanism predicts and diffuse extraction noise would not.

**Mechanism split, stated at the precision it deserves:**

| | estimate | status |
|---|---|---|
| total | ~3,572 (11.7%) | calibrated on hand verdicts, independent of both scans |
| reference-device citations | **≥** ~826 (≥2.7%) | a floor |
| compatibility and similar | **≤** ~2,746 (≤9.0%) | the remainder |

826 is a floor, not a point estimate: Sample C measured the reference scanner's
over-attribution (27% of detected reference edges were also predicates) but
nothing measures its under-detection, and only 59.5% of documents had a
detectable predicate heading at all.

**Two corpus scans are included as lower bounds only.** The
compatibility-phrase scan detected 111 of 12,392 documents (0.90%); checked
against the five documents adjudication identified as carrying compatibility
enumerations it caught 2 (sensitivity 40%, CI 12-77%), and adjudication met such
documents in 3-5 of 48 (6.2-10.4%). Cite these scans for worked examples, not
for prevalence. The reference-section scan enumerates 1,136 edges by name in
`verification/reference_device_edges.csv`, 999 of them `SECTION_HEADED` (4.4% of
that tier), across 778 documents (8.7%).

**Clustering caveat.** Rejections concentrate in documents — 4 of 45 in Sample
A, 1 of 3 in Sample B carried every failure. The document, not the edge, is the
independent unit, so the per-bin Wilson intervals above are optimistic. A
cluster bootstrap over documents on Sample A gives a materially wider interval.

## 6. Findings

Numbering follows `verification/adjudication_summary.txt`, where the full text
and arithmetic for each finding is recorded.

**F1. Registration confirmed; §12 step 1 satisfied.** Registered 2026-07-28,
eleven days before the confirmatory run. An earlier working note in this
verification recorded the study as apparently unregistered; that is **withdrawn
in full**. Four items remain: (a) the repository ships `PREREGISTRATION.docx`
marked "Version 1.0 (draft for review)" with `[to be completed]` placeholders
and the instruction "Nothing here should be publicly registered until the author
team has confirmed the hypotheses and criteria reflect their intent" — the
repository should ship the registered version or a link to it; (b) the embargo
end date is unknown, so the manuscript cannot yet direct readers to a public
registration; (c) verifier independence, see §9 below; (d) a third contributor,
Tanner Livsey, appears on the registration but nowhere in the repository,
`RUN_LOG.md` or `DEVIATIONS.md`.

**F2. The reference-device edges are the locked rule, not a defect.** §5
verbatim: "Predicate cue: a case-insensitive match of predicate, substantially
equivalent, or *reference device* in the summary text." §8 defines precision
over "genuine predicate/reference citations". Reference citations are correct by
the registered criterion.

**F3. Nor is the compatibility-table behaviour. The rule is maximal.** §5
verbatim: "in any summary containing a predicate cue, **every other in-corpus
K-number present in the text** is recorded as an incoming predicate edge."
Compatibility tables, accessory lists, standards discussions — all of it, by
design. **All 37 rejections in Sample A are the rule behaving exactly as
specified. Zero implementation defects were found.**

**F4. `SECTION_HEADED` does not mean what its name says.** §5: "SECTION_HEADED
if a cue occurs within 300 characters of the K-number's first mention;
otherwise PROXIMITY_ONLY." Both tiers are proximity rules differing only in
window width; there is no section-structure detection anywhere in the pipeline.
This explains K190123 exactly — the heading "V. Reference Device:" is itself a
cue, so the K-numbers beneath it fall inside the window. The name will mislead
manuscript readers, and it limits what `sens_high_conf` can be claimed to show:
a tighter-proximity subset, not a structurally verified one.

**F5. The substantive finding is construct validity, not implementation.** §4's
hypotheses concern substantial-equivalence lineage — devices "cited as
predicates", persistence of predicate citations, downstream devices, chain
depth. §5 counts co-occurrence of a K-number in a document that mentions
predicates anywhere. These are different constructs, and §4 measures the gap:
even on the most generous preregistered reading, 28 of 199 adjudicated edges are
neither predicate nor reference citations. The registration's own public
description — "network analysis of predicate-device citations … how recalled
devices persist as predicates" — states the construct, not the
operationalisation. The study can defend its numbers as faithful to its plan;
it cannot defend the plan as measuring predicate lineage.

**F6. The analyst's 121/121 needs no explanation.** Under §8's criterion
reference citations are genuine and enumerating documents are rare, so a clean
result is the expected outcome of applying the registered criterion to an
ordinary draw. Two earlier speculations in this verification — that the analyst
adjudicated loosely, and that their draw was unusually lucky — are **withdrawn**
and should not be read into this report.

**F7. §2 asserts the PDFs are static. They are not.** See §2 above.

**F8. The validation sample is preregistered as non-reproducible.** §8 draws 60
devices with a fixed seed "from devices with downloaded text". The population
sampled from is run-dependent, so the seed does not reproduce the sample across
runs: 199 candidate edges over 45 edge-bearing devices here against the
analyst's 121. This is in the plan, not the code.

**F9. §9's independence option was pre-specified and not run.** §3.1-3.2
disclose that H1-H4 derive from a nine-code pilot whose devices are ~35% of this
corpus, making the confirmatory analysis an extension rather than a replication.
§9 offers the remedy — reporting on the 145 non-pilot codes only — and
pre-specifies it. No such field exists in `expected_values_REFERENCE.json` and no
result appears in `RUN_LOG.md`. It is labelled optional, so skipping it is not a
deviation, but the one measure offered for independence was not taken.

**F10. Items that resolve in the study's favour.** All three sensitivity
analyses *are* preregistered in §8 as a closed list with "no others will be
added post hoc" — an earlier concern that they might be post-hoc is resolved.
§7's thresholds were set in advance. D1's account of the registered counts is
accurate. §10 declares the ~16% name-only gap, MAUDE's passive-reporting floor
and the H4 confounding risk, all in advance. §3 discloses the pilot and
quantifies the overlap. §7 commits to reporting non-confirmation with equal
prominence. §10 makes no causal claim and names no manufacturer.

**F11. Registered versus actual, after the D1 re-freeze.** Every delta is
positive and under 1%: unique devices 15,556 to 15,581 (+25, +0.161%), with
summary 13,288 to 13,313 (+25), recall records 6,285 to 6,297 (+12),
enforcement 4,089 to 4,096 (+7), recalled devices 1,687 to 1,691 (+4),
unclassified severity 353 to 356 (+3). D1 traded departure from the locked
snapshot for 25 additional devices in 15,556. The registered counts D1 cites
are accurate.

**F12. Deviation policy met in form.** D1, D2 and D3 are logged with reason and
date per §11. One unresolved inconsistency: D1 dates the re-freeze 2026-08-07
(twice) while `RUN_LOG.md` and `SNAPSHOT.json` both say 2026-08-08.

**F13. Two analytic observations.** (a) `sens_class_I_II` restricts to Class
I+II = 1,317 devices, silently dropping the 356 recalled devices carrying no
severity class (21.1% of 1,691); and "Class I/II" is in practice Class II, which
is 1,306 of 1,317 (99.2%) — a reader may assume the most severe category carries
the signal. (b) The H4 comparison has a 35-point differential linkage gap
between arms (84% vs 49%); at 49% control matching, at least 51% of controls
score zero events because they could not be linked at all, so a control median
of exactly 0 is what non-linkage alone produces. §10 declares this risk in
advance; the reproduced match rates quantify it.

**F14. `08_verify` cannot fail.** Its "expected" values are read from the file
`06_graph_and_analysis` writes in the same run, so it is a self-consistency
check of the rebuild against itself. It cannot detect divergence from the
analyst and its 15/15 pass should not be presented as independent confirmation.
The real comparison is `compare_to_reference.py` (§2 above).

## 7. Recommendations

1. **Restrict the edge rule** to K-numbers appearing in a predicate or
   substantial-equivalence context, excluding reference-device sections and
   compatibility/accessory enumerations, and report the current graph as a
   sensitivity analysis. Failing that, rename the object throughout —
   "predicate-or-reference citation graph" — and restate the hypotheses in those
   terms.
2. **State the construct-validity limitation in the manuscript** with the
   measured precision attached: ~11.7% of edges (interval 7.3-22.4%) are not
   substantial-equivalence citations, and ≥2.7% are FDA reference-device
   citations rather than predicates.
3. **Rename the confidence tiers.** They are proximity windows, not section
   detection (F4).
4. **Either freeze the extracted PDF text into the snapshot** — which would make
   the study genuinely reproducible — **or restate the eight affected reference
   values as tolerance-bounded**. As written, every future verifier will hit the
   same mismatch with no way to distinguish it from a real error.
5. **Ship the registered preregistration**, or a link to the registration,
   rather than the draft copy (F1a).
6. **Add a review queue rather than an exclusion rule** for high-K-number
   documents. 1,393 documents carry ≥6 K-numbers and 40% of all edges; the
   signal screens but does not diagnose — one known-bad document has only 4
   K-numbers, and most high-load documents are clean.
7. **Report `08_verify` for what it is** (F12), and state whether the §9
   independence analysis will be run (F9).

## 8. Limitations of this verification

- **Single adjudicator throughout.** 266 edges across 60 documents, no second
  reader, no inter-rater agreement statistic — the same limitation the study's
  own validation carries. No notes were recorded against 36 of Sample A's 37
  rejections, so their individual reasoning is undocumented; K190123 was
  subsequently audited in full and K050441 examined directly.
- **F2-F5 are conditional.** They quote the repository's `PREREGISTRATION.docx`,
  which is the draft copy described in F1a. The registered copy was not opened
  to confirm the two are identical. If the registered §5 differs, these four
  findings must be re-derived.
- **Adjudication used locally retrieved PDFs.** A planned cross-check of ten
  documents against the live FDA database could not be performed:
  accessdata.fda.gov returned application errors throughout the window.
- **Clustering.** Per-bin intervals in §5 are edge-level and therefore
  optimistic; the document is the independent unit.
- **Both corpus scans are lower bounds,** with measured sensitivity of 40% for
  the compatibility scan and unmeasured sensitivity for the reference scan.
- **The 11-25 bin rests on three documents,** one of which carried all its
  failures.
- **Environment departures:** Python 3.11 in a conda environment rather than a
  system 3.11 (this machine's system Python is 3.13.9); exact library versions
  in `verification/preflight_report.txt`. The snapshot arrived as four loose
  files rather than `snapshot_for_verifier.zip`, so its integrity rests on the
  recorded hashes and on record counts matching `SNAPSHOT.json`, all of which
  check out. `chmod 644` was applied to the received snapshot files, which was
  unnecessary; contents are untouched and the hashes above still hold. An
  accidental nested clone was created and deleted before any pipeline stage ran;
  the verified run took place in the outer tree with `git status` clean apart
  from the verifier's own untracked files. `openpyxl` is needed to read the
  spreadsheets and is not in `requirements.txt`.
- **One near-miss worth disclosing.** A file named `spotcheck_worksheet.xlsx`,
  recovered from removable media while assembling `verification/`, proved to
  contain 10 rows and no verdict column — an early draft from the worksheet
  script's default settings. It had the right filename and plausible columns and
  would have entered this pull request as the adjudication record. It was caught
  because its size disagreed with a copy whose contents had already been
  verified. Every verdict is therefore committed twice, as a spreadsheet and as
  a CSV, so any such substitution is detectable.

## 9. Verifier independence

**Timeline.**

| date | event |
|---|---|
| 2026-07-28 | preregistration registered on OSF |
| 2026-08-08 | analyst's confirmatory run; `expected_values.json` written |
| 2026-08-09 | verifier added as a project contributor |
| 2026-08-24 | verification work begins |
| 2026-09-16 | verification filed (this report) |

The verifier joined the project the day after the confirmatory quantities were
computed and twelve days after the analysis plan was registered. He made no
contribution to the hypotheses (§4), the locked edge rule (§5), the
pre-specified thresholds (§7), the pipeline code, the data collection, or the
reference values, and had no opportunity to do so. His role on this study is
limited to this verification; the analyst is writing the manuscript. The
verifier manual's premise — a second person who did not build the study — is
satisfied.

**One qualification, for completeness.** Contributor status was conferred before
the verification began rather than after it, and the verifier appears in the
contributor list of the OSF registration. The verifier is therefore a project
contributor who performed the verification, not an arms-length external
reviewer. The protection is temporal — he arrived after the plan was locked and
after every reported number already existed — rather than organisational, and
readers should weigh the report on that basis.

**No prior discussion.** No finding in this report was discussed with the
analyst before it was filed. The questions in section 10 are being put to him
for the first time here, and the nine of them are the whole of what the
verifier is asking.

## 10. Questions for the analyst

1. **Is the registered §5 identical to the repository's draft copy?** F2-F5
   depend on it. Please also confirm the embargo end date.
2. **Was the 60-device validation sample adjudicated, by whom, and what
   precision did it yield split by confidence tier?** If Tanner Livsey performed
   it, please say so — a completed adjudication makes this report a cross-check
   of yours rather than an independent sample.
3. **What was your Stage 2 retrieval count?** A figure near 12,381 closes the
   eight-field difference outright. `RUN_LOG.md`'s Stage 1-5 entries are blank.
4. **Can the registered 2026-07-21 snapshot be provided?** §2's counts (15,556 /
   13,288 / 1,687) are preserved per D1, but the snapshot itself was not
   supplied to the verifier, so the registered basis cannot be reproduced.
5. **Was the edge rule intended to include FDA reference devices as predicate
   edges?** The answer determines whether ≥826 edges are a design choice or a
   defect, and it cannot be settled from the repository.
6. **How does the `n/a` severity class arise,** and is dropping those 356
   devices from `sens_class_I_II` intended?
7. **Is `n_enforcement_raw` = 4,096 the true total or a pagination ceiling?**
   §2's 4,089 at registration argues against a hard ceiling, but §2 describes a
   filtered quantity while the snapshot field is unfiltered.
8. **D1 dates the re-freeze 2026-08-07; `RUN_LOG.md` and `SNAPSHOT.json` say
   2026-08-08.** Which is correct?
9. **Will the §9 independence analysis on the 145 non-pilot codes be run?**

## Evidence

`verification/README.md` indexes all 26 files and documents how to re-run every
script. `verification/adjudication_summary.txt` is authoritative where any other
file disagrees with it.
