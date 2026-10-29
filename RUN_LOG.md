# RUN LOG — Orthopedic 510(k) Predicate-Graph Study (154-code confirmatory)

## Part One — OSF registration
- Status: COMPLETED by author.
- OSF view-only link (private review): https://osf.io/utr47/overview?view_only=9537bfe687db43d98ba3ec1c37d192eb
- TODO for manuscript: record the PUBLIC registration URL / DOI (the frozen registration's own GUID,
  without the ?view_only= token). The view-only link above is anonymized and not citable as the
  permanent preregistration reference.

## Part Two — Data freeze
- Decision: RE-FREEZE LIVE on run date (see DEVIATIONS.md D1).
- Registered snapshot (preserved): snapshot_registered_2026-07-21/  (2026-07-21; 15,556 devices)
- New live snapshot: snapshot/  (date + counts filled in from Stage 0 checkpoint below)
- Stage 0 checkpoint (live re-freeze, 2026-08-08):
  - date 2026-08-08 | codes 154 | devices 15,581 | summaries 13,313 | recalls 6,297 | enforcement 4,096
  - enforcement hard-failed: 0 (rate-limited re-fetch; no silent drops)
  - growth vs registered 2026-07-21: devices +25, summaries +25, recalls +12, enforcement +7

## Part Three — Pipeline checkpoints
- Stage 1 (corpus): 15,581 unique devices | 13,313 with Summary (matches SNAPSHOT.json)
- Stage 2 (PDFs): DONE 2026-08-08 — manifest 13,313 rows: 12,388 retrieved (93.1%) | 924 HTTP 404 | 1 error
  (recorded 2026-09-16 from data/download_manifest.csv; the verifier's 2026-08-26 rebuild retrieved 12,392 — see DEVIATIONS D5)
- Stage 3 (edges): 30,476 edges | SECTION_HEADED/PROXIMITY_ONLY split as in Stage 6 sensitivity
- Stage 4 (recalls): [count from data/recall_links.csv]
- Stage 5 (classify): 1,691 recalled corpus devices | worst-class: Class II 1,306 | Class I 11 | n/a 356 | Class III [fill]
- Stage 6 (graph & analysis — expected_values.json): DONE 2026-08-08
  - corpus 15,581 | edges 30,476 | recalled 1,691 (10.9%)
  - is_dag false (one mutual-citation 2-cycle; see DEVIATIONS D2) | max_chain_depth 30 (via condensation)
  - persistent_predicates 938 | post_recall_citations 2,877 | downstream_devices 1,873
  - first_after_recall 381 | max_gap_years 21
  - sensitivity [persist/cites/downstream]: classI+II [718/2141/1436]; high_conf [838/2209/1563]; combined [654/1660/1214]
- Stage 7 (MAUDE, with openFDA API key): DONE 2026-08-08
  - family totals: events 850,885 | deaths 2,443 | injuries 645,900
  - match rate recalled 84% vs matched 49% | median events 17 vs 0 | events/yr 1.07 vs 0.00
  - one-sided Mann-Whitney U p = 6.4e-118
- Stage 8 (verify): DONE 2026-08-08 — 15/15 checks PASS (all headline numbers reproduce; is_dag False, max_chain_depth 30)

## Part Four — Hand validation
- Edge precision (Wilson 95% CI): 100.0% (121/121), Wilson 95% CI 96.9–100.0%. Single adjudicator.
  - by tier: SECTION_HEADED 86/86 (CI 95.7–100%); PROXIMITY_ONLY 35/35 (CI 90.1–100%)
  - 0 false positives, 0 indeterminate. Sample = 60 devices, seed 42 (prereg §8).

## Hypotheses vs. pre-registered criteria (§7)
- H1: CONFIRMED — persistent 938 > 0 AND post-recall citations 2,877 >= 50
- H2: CONFIRMED — first-cited-after-recall 381 > 0
- H3: CONFIRMED — max gap 21 yr > 10
- H4: CONFIRMED — recalled median events/yr 1.07 > matched 0.00; Mann-Whitney p=6.4e-118 < 0.05
- H5: CONFIRMED — H1 direction holds in all 3 sensitivity subsets


---

## Part Five — 2026-09-16 re-run (frozen text, Rule 2 primary; DEVIATIONS D4–D6)
Inputs: snapshot/ (2026-08-08, unchanged) + frozen data/text/ (TEXT_SNAPSHOT.json corpus sha256
27646debf7d7176cb6bd4d7e9aa2ce36af133f77caf1b94c0e7fd82fe4322607). Branch: rule2-rerun.
- freeze_text.py: 2026-09-16 — 12,388 text files frozen | manifest 12,388 retrieved / 924 HTTP 404 / 1 error
  - 146 text files are empty (PDF has no text layer; scanned image) — these documents can hold no edges under either rule
- Stage 3 (edges): 2026-09-16 — Rule 1 edges 30,476 (= August run, exact) | Rule 2 edges 29,234 | excluded 1,242 (4.1%)
  in 538 documents (reference-device sections 920 / compatibility sections & tables 322)
  - Rule 2 confidence NEAR_CUE 21,541 / DISTANT_CUE 7,693 | devices with >=1 edge 8,942 (Rule 1: 8,981)
  - coverage (Rule 2): cue 87.5% | resolvable 72.2% | excluded-only 0.29% | name-only 2.8% | out-of-scope 12.2%
- Stage 6: 2026-09-16
  - edges 29,234 | connected 11,960 | largest component 11,638 | is_dag False | max_chain_depth 30 (condensation)
  - persistent_predicates 921 | post_recall_citations 2,712 | downstream_devices 1,798 | first_after_recall 382 | max_gap_years 21
  - sens class_I_II [703/1997/1361] | high_conf [816/2087/1496] | combined [634/1554/1149]
  - sens maximal_rule (Rule 1) [938/2877/1873] — reproduces the 2026-08-08 H1 triple exactly | class_na [210/704/583]
  - recalled by worst class: Class I 11 | Class II 1,306 | Class III 18 | n/a 356 (of 1,691)
  - §9 non-pilot panel: skipped — pilot_codes.txt absent (add the nine pilot codes and re-run Stage 6 to report it)
- Stage 7 (MAUDE, live, 2026-09-16): family events 860,135 | deaths 2,462 | injuries 652,041
  - recalled predicates 1,372 vs matched 1,372 | match 84.3% vs 49.6% | median events 17 vs 0 | events/yr 1.085 vs 0.000
  - one-sided Mann-Whitney U p = 1.0e-113
  - linked-only (post hoc, D6): n 1,156 vs 680 | median events 28 vs 7 | events/yr 1.76 vs 0.50 | p = 7.0e-35
- Stage 8 (self-consistency): 17/17 PASS
- Reference file: expected_values_REFERENCE.json replaced with the Rule 2 run; Rule 1 reference preserved as
  expected_values_REFERENCE_rule1_2026-08-08.json
- Independent reproduction (compare_to_reference.py, second analyst on the frozen inputs): [pending]

## Hypotheses vs. pre-registered criteria (§7) — Rule 2 primary
- H1: CONFIRMED — persistent 921 > 0 AND post-recall citations 2,712 >= 50
- H2: CONFIRMED — first-cited-after-recall 382 > 0
- H3: CONFIRMED — max gap 21 yr > 10
- H4: CONFIRMED — recalled median events/yr 1.085 > matched 0.000; p = 1.0e-113 < 0.05
  (linked-only: 1.76 > 0.50, p = 7.0e-35 — direction holds after removing differential non-linkage)
- H5: CONFIRMED — H1 direction holds in all 3 preregistered sensitivity subsets; also in maximal_rule and class_na


---

## Part Six — 2026-10-21/22 re-run (Rule 2 v2; exact-date post-recall rule; K060694 rescued; DEVIATIONS D8, D10)
Inputs unchanged: snapshot/ (2026-08-08) + frozen data/text/ (corpus sha256 27646debf7d7…).
Code changes: edge_rules.py (Rule 2 v2), test_edge_rules.py (16 tests), 03_extract_edges, 05_classify,
06_graph_and_analysis, 08_verify.
- Stage 3 (edges): 2026-10-21 — Rule 1 30,476 (unchanged) | Rule 2 v1 29,234 (= Part Five) | Rule 2 v2 28,562
  - v1 → v2: 672 edges dropped in 345 documents (all reference-device zones), 0 added — data/rule2_v1_vs_v2.csv
  - devices with >=1 edge: 8,928 (v1: 8,942)
- Stage 5: 2026-10-22 — recall dates ignored as invalid: 1 (K060694, Z-0660-2013, "0012-12-06");
  K060694 anchored on 2008-03-13. Recalled corpus devices 1,691; worst class unchanged.
- Stage 6: 2026-10-22 — post_recall_rule = received_after_public
  - edges 28,562 | connected 11,923 | largest component 11,588 | is_dag False | max_chain_depth 30
  - recalled devices with a public date 1,689 of 1,691
  - persistent_predicates 893 | post_recall_citations 2,553 | downstream_devices 1,709 | first_after_recall 356 | max_gap_years 21
  - sens_year_rule (manuscript-v5 rule) [910/2643/1762] | first_after_recall (year rule) 376
  - sens class_I_II [680/1883/1298] | high_conf [789/1949/1418] | combined [613/1454/1088]
  - sens maximal_rule (Rule 1) [925/2793/1825] | class_na [206/661/546]
- Stage 7 (MAUDE): 2026-10-22 — every query restricted to reports received on or before the snapshot date
  (date_received:[19000101 TO 20260808]); check HRS 38,827 as of snapshot vs 39,163 live on the run date
  - family events 856,492 | deaths 2,461 | injuries 649,620 (as of 2026-08-08)
  - recalled predicates 1,360 vs matched 1,360 (seed 42; re-drawn from Rule 2 v2 edges)
  - match 84.5% vs 51.5% | median events 17 vs 1 | events/yr 1.087 vs 0.043 | one-sided Mann-Whitney U p = 9.0e-102
  - linked-only (D6): n 1,149 vs 700 | median events 28 vs 8 | events/yr 1.75 vs 0.60 | p = 1.0e-29
  - Limitation: MAUDE is a live database. Reports received before the cutoff can later be edited,
    reclassified or removed, so these counts may not be fully reproducible by a later run.
- Stage 8 (self-consistency): 19/19 PASS
- Stage 6b (denominators/KM, D7): 2026-10-27 — evaluable 1,689 | persistent 893 (52.9%) | >=5 y follow-up 58.6%
  | prior use 56.4% vs none 47.7% | cumulative incidence 20.2 / 46.1 / 57.6% at 1 / 5 / 10 y | median time to
  first post-recall citing submission 1.7 y | matched comparator (prior-use matched, n 1,519) 53.3% vs 40.3%,
  +13.0 pts (10.5–15.6)
- Stage 6c (recall timing, D8): 2026-10-27 — 2,837 citations cleared after recall initiation: A 2,553 | B 119 |
  C 159 | U 6 | lag 90 d A 2,435 [859/2435/1631] | lag 180 d A 2,323 [834/2323/1553] | year-rule citations
  received after public 2,510 of 2,643 | crude same-firm share of A 43.3% (lower bound; no family map)
- Stage 8 re-run with Tier 3 (06b/06c re-derived independently): 2026-10-27 — 30/30 PASS
- Stage 6d (largest component): 2026-10-28 — 11,588 devices | 28,322 edges | 111 product codes | 2,852 roots | top
  root K990148 reaches 1,257 (10.8%) | 44 roots reach >=5% | cross-code edges 9,743 (34.4%) | same-code edges only:
  72 families of >=10 devices, largest 994 | direct hip<->spine edges 5 (audited; see DEVIATIONS D10)
- Design arm D3: 2026-10-28 — any-recall arm reproduces parent (893/2553/1709; high_conf 789/1949/1418; rule1
  925/2793/1825; first_after 356; max gap 21) | design (FDA mapping, preliminary) 168/430/360, 288 exposed |
  design + unclear 379/1031/811
- Figures (09_figures.py, repo-relative paths, current rule): 2026-10-28 — figures/fig_lineages, fig_structure
- Public-date check (2026-10-27): recall-database posting dates start 2002-12; Enforcement Report dates in the
  snapshot start ~2012; some postings are batch entries. Effect can only lower the primary counts.
- Reference file: expected_values_REFERENCE.json replaced with the Part Six run (2026-10-22); Part Five reference
  preserved as expected_values_REFERENCE_rule2v1_2026-09-16.json
- Independent reproduction (compare_to_reference.py, second analyst): [pending]

## Hypotheses vs. pre-registered criteria (§7) — Part Six primary
- H1: CONFIRMED — persistent 893 > 0 AND post-recall citations 2,553 >= 50
- H2: CONFIRMED — first-cited-after-recall 356 > 0
- H3: CONFIRMED — max gap 21 yr > 10
- H4: CONFIRMED — recalled median events/yr 1.087 > matched 0.043; p = 9.0e-102 < 0.05
  (linked-only: 1.75 > 0.60, p = 1.0e-29)
- H5: CONFIRMED — H1 direction holds in all 3 preregistered sensitivity subsets; also in maximal_rule, class_na and year_rule
