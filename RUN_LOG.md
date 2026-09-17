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
