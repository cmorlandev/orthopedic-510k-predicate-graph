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
- Stage 1 (corpus): [filled after run]
- Stage 2 (PDFs): 
- Stage 3 (edges): 
- Stage 4 (recalls): 
- Stage 5 (classify): 
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
