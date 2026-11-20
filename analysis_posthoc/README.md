# analysis_posthoc

These scripts produce the reported values that do not come from a pipeline notebook. Most are post hoc analyses added during review, plus a few descriptive counts. Each script reads only the frozen August 8, 2026 inputs (`snapshot/`, `data/`, `TEXT_SNAPSHOT_files.csv`, `verification/round2/`, `design_arm/`). None of them downloads anything or changes a pipeline file. Outputs go to `data/posthoc/`.

They are archived for transparency and reproducibility. They are not part of the registered pipeline, and Stage 8 does not check them. `run_all.py` runs every script and compares its output with the values reported in the manuscript and Supplement 1. It prints PASS or FAIL for each value.

## Run
From the repository root, after Stages 01 to 06c (and with `design_arm/validation/KEY_do_not_share.csv` in place for ph08):

```bash
python analysis_posthoc/run_all.py        # about 1 to 2 minutes; prints "227 of 227 reported values reproduced"
```

To run one script, use `python analysis_posthoc/ph03_timing.py`. Each script prints its JSON output.

## Scripts and where their values appear

| Script | Values | Used in |
|---|---|---|
| `ph01_table1_figure2.py` | persistence by recall class, body region and year made public, with 5-year KM; Figure 2 KM estimates and numbers at risk; eTable 8 numbers at risk and not-estimable cells; prior-use split | Article Table 1, Figure 2, Results; eTable 8 |
| `ph02_recall_status_family.py` | recall open, terminated or between at receipt; open design-related recalls; sensitivity with undated records closed; same- vs other-family citations; device-level family split; family-map vs first-word matches; timing categories (90 and 180 days) | Article Table 2, Results, Discussion; eMethods 7; eTable 7 |
| `ph03_timing.py` | split of the 356 devices first cited after recall; time to last citing submission; counts near end of follow-up; citations by later-recalled citing devices; predicates per later device; recall initiation to public date | Results; eMethods 5; eTable 7 note |
| `ph04_as_registered.py` | analysis exactly as preregistered (Rule 1 and calendar-year rule), with and without the K060694 correction; check against the Stage 6 year-rule values | Table 2 note; eTables 1, 4 and 6 |
| `ph05_network_corpus.py` | connectivity of recalled devices; chronology of links; De Novo records; product codes with devices (`etable2_product_code_counts.csv`); readable summaries by clearance period; text-file sizes; H2 by predicate clearance era | Results; eResults; eMethods 1 and 2; eTable 2 |
| `ph06_validation_maude.py` | primary-rule precision on the 199-link sample; sample composition, overlap and rejections; MAUDE two-proportion z test; MAUDE unlabeled-family sum | Results; eTable 3; eMethods 3 and 6 |
| `ph07_severity_dating.py` | severity class by recall era; Enforcement Report start; devices without a class; public-date and Class I/II dating checks | Limitations; eMethods 4 |
| `ph08_design_validation_frame.py` | sampling frame of the design-label validation sample (1,237 events) and a check that the 120 sampled events come from it | eMethods 8 |

`_common.py` holds the shared loaders. `reported_values.json` lists the 227 reported values that `run_all.py` checks.

## Provenance
These scripts consolidate the one-off computations made during manuscript revision from October to November 2026. The originals were `tables/t.py`, `t3.py`, `fig2.py` and the red-team `r1_compute.py` to `r4_compute.py`. Paths are now relative to the repository root, and each value is written to JSON. All 227 values were reproduced exactly on November 19, 2026, in the project environment (Python 3.11.7, pandas 2.1.4). Recall initiation dates must be valid (1976 or later), as in Stage 5. A newer pandas parses K060694's corrupted date (0012-12-06), and without this rule that adds 1 open-recall citation. The exploratory harm-analysis runs of November 9 and 10 are not included. They are disclosed in the registered addendum, and their results are not reported.
