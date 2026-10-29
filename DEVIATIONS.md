# Deviations from the preregistered plan

## D1 — Live re-freeze on run date (2026-08-08) instead of the registered 2026-07-21 snapshot
- **Prereg basis:** OSF "Existing Data" registration; §2 states all confirmatory numbers derive
  from the frozen 2026-07-21 snapshot (openFDA release 2026-07-06). §3.3 records the frozen
  descriptive counts: 15,556 devices, 13,288 with summary, 1,687 recalled.
- **What we did:** re-ran Stage 0 live on 2026-08-08, generating a NEW snapshot from the current
  openFDA database. Expected effect: device/recall counts drift upward vs. §3.3 (FDA DB growth).
- **Why (author decision):** to evaluate the largest possible device corpus, capturing all FDA
  510(k) clearances up to the run date (2026-08-08) rather than stopping at the 2026-07-21 snapshot.
  The authors judged that maximizing the number of instruments/devices analyzed outweighs holding to
  the earlier frozen counts.
- **Integrity note:** because the confirmatory quantities in prereg §3.4 (edges, graph metrics,
  persistence counts, MAUDE comparison) were NOT computed at registration, expanding the corpus by
  re-freezing does not expose those quantities to hindsight; the pre-specified rules, thresholds, and
  tests (§5-§8) are applied unchanged to the larger frozen set. The §3.3 descriptive counts remain
  reported as the registered figures, with the new live counts reported alongside.
- **Mitigation:** the original registered snapshot is preserved in
  `snapshot_registered_2026-07-21/`; the confirmatory pipeline can be re-run against it at any time
  to reproduce the registration-basis numbers.
- **Date correction (2026-09-16):** an earlier version of this entry gave the re-freeze date as
  2026-08-07. `snapshot/SNAPSHOT.json` and `RUN_LOG.md` record 2026-08-08, which is correct.


## D2 — §6 acyclicity: graph is a near-DAG (reported honestly; edge set unchanged)
- **Finding:** the predicate graph is not strictly acyclic. Of 30,476 edges, ~5 are anomalous:
  one mutual-citation 2-cycle (K012634 <-> K012645) and 4 forward-in-time edges (predicate cleared
  9-79 days AFTER the citing device). 30,472/30,476 (100.0%) are temporally valid.
- **Handling (Option A, chosen by author):** the locked §5 edge rule is NOT altered; all edges kept.
  §6 "confirm acyclicity" is reported honestly as near-acyclic (is_dag = false, one 2-node SCC).
- **Max chain depth:** computed on the graph's condensation (collapses the single SCC) = 30.
  Stage 6 originally emitted the sentinel -1 on any non-DAG; notebooks 06 and 08 were patched to
  compute depth via nx.condensation so the §6 quantity is reported (30) and Stage 8 verify does not
  crash on the near-DAG. This is a reporting/computation fix; no confirmatory quantity changed.


## D3 — Fresh validation sample
- Stage 3 draws a fresh random sample of 60 devices (seed 42) for hand adjudication of edge
  precision (prereg §8). Recorded here for completeness; referenced as D3 in README and notebooks.


## D4 — Restricted edge rule (Rule 2) adopted as primary after independent verification (2026-09)
- **Prereg basis:** §5 defines an edge as every other in-corpus K-number mentioned in any summary
  that contains a predicate cue. §4's hypotheses concern substantial-equivalence (predicate) lineage.
- **What the verification found:** independent hand adjudication of 266 candidate edges across 60
  documents (second analyst, 2026-08/09) estimated that 11.7% of §5 edges (95% interval 7.3–22.4%;
  ~3,572 of 30,487) are not substantial-equivalence citations. The extractor implements §5 exactly;
  the discrepancy is in what §5 captures. Errors were not diffuse: in the validation sample, 4 of 45
  documents produced all 37 rejections and the remaining 41 documents were 155/155 correct. The
  offending structures are (a) *Component and Accessory Compatibility* sections and tables — lists of
  parts usable *with* the device, often with a literal "510(k)" column header, which the cue-proximity
  tier also matches — and (b) *Reference Device* sections, a formally distinct FDA category carrying
  no equivalence claim.
- **What we did:** added Rule 2 (`edge_rules.py`): Rule 1 minus any K-number whose every mention lies
  inside an exclusion zone. An exclusion zone runs from a heading-like line denoting component/
  accessory compatibility or reference devices to the next line that begins a different section. A
  K-number mentioned at least once outside every zone is kept (a predicate that also appears in a
  compatibility table remains a predicate). The rule is deterministic, unit-tested on the two
  documents that carried the validation-sample errors (`test_edge_rules.py`), and every removed edge is
  listed with its excluding heading in `data/excluded_edges.csv`.
- **Reporting:** Rule 2 is the primary analysis. The registered Rule 1 graph is reported in full as the
  `sens_maximal_rule` sensitivity arm, so the effect of the restriction is visible. This is a deviation
  from §5 and from §8's closed sensitivity list, adopted post hoc and disclosed as such in the
  manuscript; the reason is construct validity, not the direction or size of any result. Precision under
  Rule 2 is re-adjudicated on the same 266 candidate edges / 60 documents.
- **Tier names:** `SECTION_HEADED` / `PROXIMITY_ONLY` are renamed `NEAR_CUE` / `DISTANT_CUE`. The rule
  (strong cue within 300 characters) is unchanged; the old names implied section detection that the
  pipeline never performed.


## D5 — Frozen extracted-text corpus (2026-09)
- **Prereg basis:** §2 describes the summary PDFs as static documents; Stage 2 fetches them live from
  accessdata.fda.gov at analysis time.
- **What the verification found:** retrieval is not stable across runs. An independent rebuild 18 days
  after the confirmatory run retrieved 12,392 of 13,313 listed summaries against the analyst's 12,388,
  and obtained 30,487 edges against 30,476 (+0.036%), with `persistent_predicates` +1,
  `post_recall_citations` +3, `downstream_devices` +2, `first_after_recall` +1 (largest delta 0.262%)
  and every graph-structural metric identical. Those eight fields were therefore non-reproducible by
  construction.
- **What we did:** the extracted text in `data/text/` (PyMuPDF output, one file per retrieved summary)
  is now a frozen input. `freeze_text.py` records per-file SHA-256 hashes and one corpus hash in
  `TEXT_SNAPSHOT.json` / `TEXT_SNAPSHOT_files.csv` (committed to git); `data/text/` itself is archived
  on OSF with the snapshot. Stage 3 verifies the corpus hash before running and never opens a PDF.
  Stage 8's former ±2% "drift" tier is retired: every value is now exact.
- **Which corpus is frozen:** the analyst's 2026-08-08 extraction (12,388 documents; manifest: 12,388
  retrieved / 924 not found / 1 error), i.e. the confirmatory-run basis. The verifier's later pull is
  reported as the +0.04% stability evidence in the manuscript's reproducibility statement.
- **§2 correction:** the "static documents" statement is withdrawn in the manuscript.


## D6 — Post hoc sensitivity analyses added after verification (2026-09)
None of these were in §8's closed list; all are labelled post hoc in the manuscript.
- `sens_maximal_rule` — H1 triple on the registered Rule 1 graph (see D4).
- `sens_class_na` — H1 triple restricted to recalled devices whose worst severity class is `n/a`
  (no enforcement record with a classification; 356 of 1,691 in the 2026-08-08 run). `sens_class_I_II`
  silently dropped these; they are now reported as their own arm, with the class distribution.
- **Linked-only H4** — the adverse-event comparison restricted to devices with ≥1 MAUDE event in both
  arms. Device-name linkage succeeded for 84% of recalled and 49% of matched devices, so the matched
  arm's median of zero is produced by non-linkage alone; the linked-only comparison removes that
  left-censoring. Written to `data/maude_comparison.json` under `linked_only`.
- **§9 independence panel** (pre-specified as optional in §9): H1–H3 quantities on the subgraph of
  devices in the 145 non-pilot product codes. Runs when `pilot_codes.txt` (the nine pilot codes, one
  per line) is present; written to `expected_values.json` under `panel_nonpilot`.


## D7 — Alternative denominators and time-to-event analysis (post hoc, 2026-10-09)
- **Critique addressed:** 921/1,690 (54.5%) is a crude proportion, not a standardized probability of
  post-recall reuse; recalled devices differ in follow-up time and in prior predicate use.
- **What we did:** reported the persistent-predicate proportion under alternative denominators
  (follow-up ≥3, ≥5, ≥10 years; prior vs no prior predicate use; in-family opportunity), the cumulative
  incidence of first post-recall citation (1 − Kaplan–Meier, administrative censoring at the last
  corpus clearance), and an exploratory benchmark against matched non-recalled devices (same product
  code and clearance year, index date = the recalled device's recall date). Competing risks were not
  modelled: public data contain no event that ends predicate eligibility.
- **Reporting:** all post hoc. The matched comparator is reported in Results as exploratory and worded
  "recall did not reduce later predicate use", with no causal implication (author decision 2026-10-21).
- **Status (2026-10-27):** now pipeline stage `06b_denominators.ipynb`, run on the D8/D10 definitions:
  Rule 2 v2 edges; outcome = a non-recalled 510(k) received after the recall was public; time origin
  = the public date; prior use = cited by a 510(k) received before it. Evaluable 1,689; persistent 893
  (52.9%, 95% CI 50.5–55.2); cumulative incidence 20.2% at 1 y, 46.1% at 5 y, 57.6% at 10 y; matched
  comparator (also matched on prior use) 53.3% vs 40.3%, +13.0 points (10.5–15.6). The 2026-10-09
  numbers (Rule 2 v1, year rule, K060694 excluded) are superseded. Checked by Stage 8 Tier 3.

## D8 — Post-recall timing on exact dates; K060694 rescued (post hoc, 2026-10-13 / 2026-10-21)
- **Prereg basis / manuscript v5:** a citation was post-recall if the citing device's clearance YEAR
  was later than the predicate's recall YEAR. That rule can count a citation whose 510(k) was submitted
  before the recall existed, or before it was public.
- **What the reanalysis found (2026-10-13, Rule 2 v1 edges):** of 2,712 year-rule citations, 2,578
  (95.1%) were submitted after the recall was public, 76 (2.8%) after initiation but before posting,
  51 (1.9%) before initiation, 7 (0.3%) uncertain.
- **What we changed (author decision 2026-10-21):** the PRIMARY post-recall rule is now
  "citing 510(k) date_received > the predicate's recall public date", where the public date is the
  earliest of the FDA recall-database posting (`event_date_posted`) and the weekly Enforcement Report
  listing (`report_date`) across the predicate's linked recalls. The year rule is no longer applied as
  a pre-filter. All dates come from the frozen 2026-08-08 snapshot. The year rule is reported as the
  `sens_year_rule` sensitivity arm. Stage 6 switch: `POST_RECALL_RULE`.
- **K060694:** its earliest recall record (Z-0660-2013) carries the corrupted initiation date
  "0012-12-06". Stage 5 now takes each device's earliest VALID recall date (parsed; ≥1976; ≤ snapshot)
  and lists ignored dates in `data/recall_dates_ignored.csv` (one record). K060694 is anchored on its
  2008-03-13 recall. No other device's date changed.
- **Effect:** see RUN_LOG Part Six. Primary triple 893 / 2,553 / 1,709 (year rule 910 / 2,643 / 1,762),
  on Rule 2 v2 edges.
- **Timing analysis (2026-10-27):** now pipeline stage `06c_recall_timing.ipynb`. Of the 2,837 citations
  from non-recalled devices cleared after the recall began: received after public 2,553 (90.0%),
  after initiation but before public 119 (4.2%), before initiation 159 (5.6%), uncertain 6. Requiring
  public posting ≥90 / ≥180 days before receipt leaves 2,435 / 2,323 citations (859 / 834 predicates).
  Within the 2,643 year-rule citations, 2,510 (95.0%) were received after public. Public dates before
  2012 come from recall-database postings alone, some batch-entered later; a delayed public date can only
  move a citation out of the primary count, so the primary counts are conservative.

## D9 — Design-related recall arm (post hoc, 2026-10-15)
- **Critique addressed:** a K-number linked to a recall does not show that the predicate's design was
  defective; recalls can be limited to lots, components, packaging or labelling.
- **What we did:** a separate arm (`design_arm/`) restricting exposure to predicates linked to ≥1
  design-related recall event. Unit = FDA recall event (`res_event_number`); recall date = earliest
  design-related recall; successor exclusion unchanged (any recall), so the arm is nested in the
  primary analysis. FDA root cause is mapped to five categories (`cause_map.py`); all unclear events
  and a 40-per-category validation sample are dual-coded by blinded reviewers with adjudication;
  agreement (Cohen's kappa) and FDA-mapping concordance are reported.
- **Coders (2026-10-22):** two investigators (C.M., G.D.) code independently, blinded to FDA's root-cause
  field and to validation-sample membership (neither opens `coding/review_key.csv` before both sheets are
  returned); a third author not involved in coding adjudicates disagreements.
- **Status (2026-10-28):** `D3_design_analysis.ipynb` now uses the D8 rule and D10 edges; its any-recall arm
  reproduces the parent exactly (893 / 2,553 / 1,709). Preliminary, with FDA's root-cause mapping:
  design-related 168 / 430 / 360 (288 exposed devices); design + unclear 379 / 1,031 / 811. Final counts
  await the manual coding.

## D10 — Rule 2 revised (v2) after the largest-component audit (2026-10-21)
- **What the audit found:** Rule 2 (D4) kept FDA reference devices as predicate edges in three
  situations: (1) reference headings that do not START with "Reference Device", e.g. "Legally Marketed
  Reference Devices Used to Support Substantial Equivalence:" (K161569); (2) font-encoded headings, where
  PyMuPDF extracts "Reference Predicates" as "5HIHUHQFH3UHGLFDWHV" (K180373); (3) reference devices
  re-mentioned in body text (materials, biocompatibility), which D4's "mentioned once outside a zone"
  rescue let back in (K171595).
- **What we changed (`edge_rules.py`, `rule2_version="v2"`, author decision 2026-10-21):** reference
  headings are recognised anywhere in a heading line ending in ":" that names no predicate; spaceless
  font-encoded heading tokens are decoded for heading detection only; a K-number that a document
  INTRODUCES under a reference heading stays excluded unless another mention is on a line naming it a
  predicate. Parenthetical table labels and lines carrying a K-number never open a zone. "Reference
  Predicate(s)" labels are treated as reference devices (author decision). Compatibility zones are
  unchanged from D4.
- **Validation:** the first v2 draft over-reached (primary predicates dropped via table labels and
  recurring mentions; one non-breaking-space heading mis-decoded). All were corrected before adoption;
  every dropped edge whose K-number also appeared beside the word "predicate" was read in its source
  text. 16 unit tests (`test_edge_rules.py`). v1 is retained and reproduces D4 exactly.
- **Effect:** Rule 2 v1 29,234 edges → v2 28,562; 672 edges dropped in 345 documents, all from
  reference-device zones; none added. Every change is listed in `data/rule2_v1_vs_v2.csv`.
- **Known limits (2026-10-28 component audit):** v2 cannot exclude a reference device that is labelled on
  the same line as its K-number (K152893 → K132788, "Reference Predicate Device – … (K132788)") or that is
  named only in running text (K210263 → K181963). Both kept as edges; not fixed, to avoid the over-reach
  seen in the first v2 draft. Of the 9 direct hip↔spine edges under v1, 5 remain under v2: 3 are genuine
  predicates whose product codes sit in different body-region regulations, 2 are these two cases.
- **Pending:** the second analyst's validation join is repeated on the v2 edge set.
