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
