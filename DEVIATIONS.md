# Deviations from the preregistered plan

## D1 — Live re-freeze on run date (2026-08-07) instead of the registered 2026-07-21 snapshot
- **Prereg basis:** OSF "Existing Data" registration; §2 states all confirmatory numbers derive
  from the frozen 2026-07-21 snapshot (openFDA release 2026-07-06). §3.3 records the frozen
  descriptive counts: 15,556 devices, 13,288 with summary, 1,687 recalled.
- **What we did:** re-ran Stage 0 live on 2026-08-07, generating a NEW snapshot from the current
  openFDA database. Expected effect: device/recall counts drift upward vs. §3.3 (FDA DB growth).
- **Why (author decision):** to evaluate the largest possible device corpus, capturing all FDA
  510(k) clearances up to the run date (2026-08-07) rather than stopping at the 2026-07-21 snapshot.
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
