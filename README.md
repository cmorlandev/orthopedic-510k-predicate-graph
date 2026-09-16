# Orthopedic 510(k) Predicate-Graph Study — 154-code confirmatory analysis

A retrospective, observational network analysis of predicate-device citations among U.S. FDA
510(k)-cleared orthopedic implants, examining how recalled devices persist as predicates for later
clearances. Descriptive; no intervention; no manufacturer naming.

- **Preregistration (OSF):** registered and timestamped before analysis; **under embargo until January**
  (auto-publishes then). Public URL/DOI to be added on release. _(Not yet publicly citable.)_
- **OSF project + frozen data:** private pending journal submission. Public URL/DOI to be added on release.
- **Analysis plan of record:** `PREREGISTRATION.docx` (the locked contract)
- **Full manual:** `PROJECT_RUN_MANUAL.docx`
- **What actually happened + any departures from the plan:** `RUN_LOG.md`, `DEVIATIONS.md`

> **The golden rule of order:** the analysis plan was registered on OSF **before** any confirmatory
> quantity was computed (register → freeze → analyze). This repository is the *analyze* step; the
> registration timestamp precedes every result here.

---

## What this repo contains (and deliberately does not)

**In the repo:** the 9 analysis notebooks (`00`–`08`), this README, `requirements.txt`, the
preregistration and manual, and the run/deviation logs. The small derived result tables in `data/`
may also be included.

**NOT in the repo** (see `.gitignore`) — obtained from the **OSF project**, not GitHub:
- `snapshot/` — the dated frozen FDA data the whole analysis is built on (~16 MB)
- `data/text/` — the **frozen** extracted text of the 12,388 retrieved summaries (~120 MB); its hashes ARE in the repo (`TEXT_SNAPSHOT.json`, `TEXT_SNAPSHOT_files.csv`) and Stage 3 checks them before running
- `data/summaries/` — the source PDFs (~5 GB); provenance only, no stage reads them once the text is frozen
- `.env` — your personal openFDA API key (never commit this)

---

## Reproducing / verifying this analysis (independent Verifier — Part Five §5.4)

You are reproducing the **analyst's frozen run**, so you must use the **same frozen snapshot**, not a
fresh live pull.

### 0. Prerequisites
- **Python 3.11** (see `requirements.txt` for the exact interpreter/package versions used).
- `pip install -r requirements.txt`
- **A free openFDA API key.** Get one in ~30 s at <https://open.fda.gov/apis/authentication>, then:
  ```bash
  export OPENFDA_KEY=your_key_here      # notebooks 02 and 07 read this from the environment
  ```
  Without a key the live FDA endpoints will rate-limit and stall. Use **your own** key — the
  analyst's is not shared.
- **The frozen snapshot.** Download the `snapshot/` files from the OSF project into a local
  `snapshot/` folder at the repo root. This is what makes your numbers match the analyst's.

### 1. ⛔ Do NOT run Stage 0 (`00_freeze_snapshot`)
Stage 0 pulls a **new live** snapshot dated to *your* run day, which would differ from the analyst's
frozen data and cause spurious mismatches. It is included only for provenance. **Skip it.** The
analysis runs entirely from the frozen `snapshot/` you downloaded from OSF.

### 2. Run the pipeline in order
Launch JupyterLab **from the repo root** so relative paths resolve, and **Run All Cells** on each:

| Stage | Notebook | Network | ~Time | Produces |
|---|---|---|---|---|
| 1 | `01_corpus.ipynb` | none | secs | `data/corpus.csv` |
| 2 | `02_download_pdfs.ipynb` | accessdata.fda.gov | **1–3 h** | `data/summaries/*.pdf` (resumable) — **verifiers skip this**: use the frozen `data/text/` from OSF (D5) |
| 3 | `03_extract_edges.ipynb` | none | ~10 min | `data/predicate_edges.csv` (Rule 2, primary), `predicate_edges_rule1.csv`, `excluded_edges.csv`, validation samples — reads the **frozen** `data/text/` only |
| 4 | `04_recalls.ipynb` | none | secs | `data/recall_links.csv` |
| 5 | `05_classify.ipynb` | none | secs | `data/recalled_nodes.csv` |
| 6 | `06_graph_and_analysis.ipynb` | none | ~1 min | **`data/expected_values.json`** (the results) |
| 7 | `07_maude.ipynb` | api.fda.gov | ~15 min | `data/maude_comparison.json` (H4) |
| 8 | `08_verify.ipynb` | none | secs | PASS/FAIL against `expected_values.json` |

**Fast check:** if the analyst also deposited the derived `data/*.csv` on OSF, you can run
`08_verify.ipynb` alone to re-check every headline number in seconds before committing to the full
rebuild.

### 3. What "matches" means
- **Deterministic quantities (H1–H3, H5, graph metrics, edge counts)** are computed entirely from the frozen
  snapshot and frozen text corpus and must match **exactly**. (Before D5, edge-derived counts could drift by
  ~0.3% between runs because Stage 2 re-fetched PDFs live; that is no longer the case.)
- **H4 / MAUDE (Stage 7)** reads the *live* adverse-event endpoint, whose event counts grow over
  time. Its magnitude will drift upward on a later run; the **direction** (recalled > matched, test
  significant) is what is being confirmed. This is disclosed in the preregistration.

### 4. Hand spot-check + open a verification PR
Pick 2–3 devices, open their summaries on accessdata.fda.gov, and confirm the edges in
`predicate_edges.csv` reflect the documents. Then open a pull request titled
`Independent verification — <name>, <date>` recording, per headline number, the analyst's value vs.
your recomputed value (PASS/FAIL) plus your spot-check. The analyst reviews and merges.

---

## Known issues already fixed in the notebooks (robustness only, not analysis changes)

These are engineering fixes to make the fetch work and survive FDA's servers. **They do not alter the
edge rule, the graph construction, the statistical tests, or any confirmatory quantity** (§5–§8 of the
preregistration are unchanged).

1. **`02_download_pdfs` sends a browser `User-Agent`.** accessdata.fda.gov returns HTTP 404 to
   Python's default urllib agent, so without this the download retrieves **zero** PDFs.
2. **`07_maude` throttles and retries.** openFDA rate-limits (~240 req/min); the MAUDE step makes
   thousands of per-device calls, so `event_count` throttles (~150/min) and retries transient
   429/5xx with backoff, and uses `OPENFDA_KEY` when set.
3. **`06`/`08` compute max chain depth on the graph condensation.** See Deviation D2 below.

## Deviations from the registered plan (full detail in `DEVIATIONS.md`)

- **D1 — live re-freeze.** The analysis was run on a snapshot re-frozen on the run date (to capture
  the largest device corpus to date) rather than the earlier registered snapshot. Confirmatory
  quantities were still not computed until after registration, so no result was exposed to hindsight;
  the pre-specified §5–§8 rules were applied unchanged. The original registered snapshot is preserved.
- **D4 — restricted edge rule (Rule 2) is primary** after independent adjudication found ~12% of registered-rule edges were compatibility-table or reference-device citations, not predicates; the registered rule is reported as a sensitivity arm. **D5 — frozen text corpus**: summary retrieval from FDA is not stable across runs, so `data/text/` is now a hashed, frozen input. **D6 — post hoc sensitivity arms** (maximal rule, `n/a` recall class, linked-only H4, §9 non-pilot panel). Tier names `SECTION_HEADED`/`PROXIMITY_ONLY` → `NEAR_CUE`/`DISTANT_CUE` (same rule).
- **D2 — near-acyclicity.** The predicate graph is not strictly acyclic: ~5 of 30,476 edges (one
  mutual-citation 2-cycle + 4 forward-in-time edges) prevent a strict DAG. Per author decision, the
  edge set is **left exactly as the §5 rule produced it** and this is reported honestly; max chain
  depth is computed on the graph's condensation (= 30).

---

## Repository layout
```
├── 00_freeze_snapshot.ipynb   # provenance only — DO NOT run for verification
├── 01_corpus … 08_verify.ipynb
├── PREREGISTRATION.docx        # the locked plan
├── PROJECT_RUN_MANUAL.docx     # full how-to
├── RUN_LOG.md                  # checkpoints, results, hypothesis outcomes
├── DEVIATIONS.md               # D1, D2
├── requirements.txt            # pinned environment
├── .gitignore                  # excludes .env, snapshot/, PDFs, text cache
├── snapshot/                   # (from OSF, not git) frozen FDA data
└── data/                       # derived outputs; PDFs + text are OSF-only
```

## Result summary (2026-08-08 run under the registered rule; superseded by the Rule 2 re-run — see `RUN_LOG.md` Part Five)
All five preregistered hypotheses were confirmed: H1 (938 persistent recalled predicates; 2,877
post-recall citations), H2 (381 first-cited-after-recall), H3 (21-year max persistence gap), H4
(recalled median 1.07 vs 0.00 events/yr; one-sided Mann-Whitney p ≈ 6.4e-118), H5 (direction holds in
all three sensitivity subsets). Stage 8 verify: 15/15 checks pass.

## Citation
On release, cite **both** the OSF preregistration (timestamped plan) and the OSF project DOI (data +
code). Both are currently withheld: the registration is embargoed until January and the project stays
private until journal submission. The DOIs will be filled in here when they are made public. Report any
further deviations in `DEVIATIONS.md`.
