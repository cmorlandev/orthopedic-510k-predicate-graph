# Correction to the filed verification report

Gant Duncan, 2026-09-16. Applies to `verification/PULL_REQUEST.md` and
`verification/adjudication_summary.txt` as committed in `c9e96a5`, and to the
GitHub Issue containing that report.

## What was wrong

Six rows of the 199-edge validation sample were adjudicated **YES** that should
read **NO** under the criterion the verifier manual specifies — *genuinely cited
as predicates*.

| device | predicate | tier | was | is |
|---|---|---|---|---|
| K221844 | K171808 | NEAR_CUE | YES | **NO** |
| K221844 | K190830 | NEAR_CUE | YES | **NO** |
| K241000 | K212746 | DISTANT_CUE | YES | **NO** |
| K241000 | K230295 | DISTANT_CUE | YES | **NO** |
| K241000 | K232303 | DISTANT_CUE | YES | **NO** |
| K241000 | K233980 | DISTANT_CUE | YES | **NO** |

## How it was found, and the evidence

Reconciling Rule 2 against the 266 verdicts surfaced these as edges the rule
removed but the verifier had accepted. Instrumenting `exclusion_zones()` showed
the zones were correctly bounded (4.1% of K221844; five zones of 2.0-3.1% in
K241000) and that each K-number has no mention anywhere outside its zone. Reading
the source text settles it. K221844, lines 223-227:

```
Primary predicate: GS Medical Co.  - AnyPlus PEEK Cage (K100516)
Additional predicate: Huvexel Co. Ltd. - Galaxy PEEK Cage (K122872)
Reference Devices:
K171808 - TDM Small Locking Plate and Screw System
K190830 - TDM Screw System
```

The document names its predicates explicitly and separately, then lists these two
as reference devices. K241000 repeats the pattern in each of its seventeen
sections — `Primary Predicate: K063633 ...` followed by `Reference Devices:`
listing all four of the affected K-numbers.

These are FDA reference devices, not predicates. The original YES verdicts
applied the preregistration §8 criterion (predicate **or** reference) rather than
the manual's narrower one, inconsistently with the other reference-section
verdicts in the same sample, which were recorded NO.

## What changes

| quantity | as filed | corrected |
|---|---|---|
| validation-sample precision, manual's criterion | 81.4% (75.4-86.2) | **78.4%** (72.2-83.5) |
| — NEAR_CUE | 93.3% | 91.8% (85.9-95.4) |
| — DISTANT_CUE | 56.9% | 50.8% (38.9-62.5) |
| precision under preregistration §8 criterion | 83.9% | **83.9%** (unchanged) |
| Rule 2 false removals | 7 | **1** |
| Rule 2 removal precision | 82.5% | **97.5%** |
| Rule 2 sensitivity to rejections | 89.2% | **90.7%** |
| Rule 2 precision on surviving edges | 97.5% | 97.5% (unchanged) |

## What does not change

No conclusion in the filed report. The corrected interval (72.2-83.5%) overlaps
the filed one throughout, and F5 — that the registered rule measures a broader
construct than the hypotheses describe — is **strengthened**: the gap between the
manual's criterion and §8's widens from 2.5 to 5.5 percentage points, which is
the construct gap stated more sharply.

The §8 figure is unchanged because those six edges were already counted YES
within it.

## Revised corpus estimate

The corpus-wide estimate was recalibrated on the corrected verdicts. **Use
`adjudication_244_corrected.csv`, not the 266-row file** — the reference-targeted
draw of 22 edges was deliberately enriched for rejections and is not a stratum of
the K-number binning, so it cannot calibrate any bin. Pooling it inflates the
estimate to 22.31%, of which most is the targeted draw rather than the
correction.

| | estimate | share of 30,487 | interval |
|---|---|---|---|
| as filed (244 verdicts) | ~3,572 | 11.72% | 2,232-6,823 |
| **corrected (244 verdicts)** | **~4,110** | **13.48%** | 2,501-7,559 |
| *pooled with targeted draw (266) — invalid* | *6,802* | *22.31%* | *discard* |

Per-bin, corrected:

| K-numbers | docs | edges | adjud | FP | rate | 95% CI | est. |
|---|---|---|---|---|---|---|---|
| 1-2 | 4,176 | 6,103 | 25 | 0 | 0.0% | 0.0-13.3 | 0 |
| 3-5 | 3,412 | 12,208 | 53 | 3 | 5.7% | 1.9-15.4 | 691 |
| 6-10 | 1,121 | 7,756 | 68 | 12 | 17.6% | 10.4-28.4 | 1,369 |
| 11-25 | 244 | 3,392 | 45 | 20 | 44.4% | 30.9-58.8 | 1,508 |
| 26+ | 28 | 1,028 | 53 | 28 | 52.8% | 39.7-65.6 | 543 |
| total | 8,981 | 30,487 | 244 | 63 | **13.48%** | 8.20-24.79 | **4,110** |

Only two bins moved: 3-5 (1 → 3 FP, K221844's two corrections) and 26+ (24 → 28,
K241000's four). The monotone rise with plateau at the top is unchanged, so the
K-load mechanism stands.

The filed interval (2,232-6,823) contains the corrected point estimate, so this
is a revision within the stated uncertainty rather than a contradiction of it.

Until that re-run, the corpus estimate in the filed report should be read as a
figure pending revision, not as a superseded one.

## Disclosure

This correction was found by the verifier during Round 2 and is reported here
with the same prominence as the original figure, per §7 of the preregistration.
It arose from an intra-rater inconsistency in a single-adjudicator sample, which
is the limitation already recorded in section 8 of the filed report; this is an
instance of it rather than a new limitation.

Both corrected files are committed alongside this notice:
`adjudication_266_corrected.csv` (all 266 rows, with a note on each corrected
row) and `verdict_corrections_6.csv` (the six rows alone).
