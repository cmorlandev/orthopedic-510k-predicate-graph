# Independent verification — start here

You're reproducing a frozen, preregistered analysis. Follow these steps exactly; the notes marked
**⚠** are the things that will trip you up if skipped. Full detail is in `README.md`; this is the
condensed path. Budget ~2–3 hours (mostly an unattended download).

## 0. What you should have received
- **Access to this private GitHub repo** (the code) — you're reading it, so ✓.
- **`snapshot_for_verifier.zip`** — the frozen FDA data (16 MB). You unzip this into the repo.
- Everything else (the reference numbers, the checker) is already in this repo.

## 1. Set up (~10 min)
```bash
# in the repo folder
python --version                 # must be 3.11.x
pip install -r requirements.txt  # pinned versions — matters for an exact match
```

**⚠ Get your own free openFDA API key** (30 s, https://open.fda.gov/apis/authentication), then:
```bash
export OPENFDA_KEY=your_key_here    # needed for Stage 2 (downloads) and Stage 7 (MAUDE)
```
Without a key the FDA endpoints rate-limit and stall. Use YOUR key, not the analyst's.

**Unzip the frozen snapshot into the repo root** so the folder `snapshot/` sits next to the notebooks:
```bash
unzip snapshot_for_verifier.zip     # creates ./snapshot/
```

## 2. Run the pipeline
**⚠ Launch JupyterLab from the repo root** (so the notebooks' relative paths resolve):
```bash
jupyter lab
```

**⚠ Do NOT run `00_freeze_snapshot`.** That pulls a *new* live snapshot and your numbers won't match.
Use the frozen `snapshot/` you just unzipped.

Open each notebook **at the repo root** and **Run → Run All Cells**, in order:

| Run | Notebook | Time | Note |
|---|---|---|---|
| 1 | `01_corpus` | secs | |
| 2 | `02_download_pdfs` | **1–3 h** | the long step; resumable — if it stops, Run All again |
| 3 | `03_extract_edges` | ~10 min | |
| 4 | `04_recalls` | secs | |
| 5 | `05_classify` | secs | |
| 6 | `06_graph_and_analysis` | ~1 min | writes YOUR `data/expected_values.json` |
| 7 | `07_maude` | ~15 min | live FDA data — see note below |
| 8 | `08_verify` | secs | self-consistency check of your rebuild (expect 15/15) |

## 3. Confirm you reproduced the analyst's numbers
```bash
python compare_to_reference.py
```
This compares your rebuilt `data/expected_values.json` to the analyst's `expected_values_REFERENCE.json`.
**Every value is deterministic and must match EXACTLY.** A `PASS` means you reproduced the study.

**MAUDE / Stage 7 is the one exception:** it reads the *live* FDA adverse-event endpoint, whose counts
grow over time, so your `data/maude_comparison.json` numbers will be **≥** the analyst's. The
*direction* (recalled > matched, one-sided Mann-Whitney p < 0.05) is what's being confirmed, not the
exact magnitude. This is disclosed in the preregistration.

## 4. Spot-check a few edges by hand
Pick 2–3 devices, open their summaries at accessdata.fda.gov, and confirm the edges in
`data/predicate_edges.csv` match what the documents say.

## 5. Open a verification pull request
Title it `Independent verification — <your name>, <date>`. In the description, record, per headline
number, the analyst's value vs. your recomputed value (PASS/FAIL) plus your spot-check. The analyst
reviews and merges. That merged PR is the permanent record that someone who did not build the study
reproduced it.

## If something doesn't match
- **Many fields differ** → you probably ran Stage 0, or didn't unzip the analyst's `snapshot/`. Redo
  with the frozen snapshot, Stage 0 skipped.
- **One graph metric differs** → check your `networkx` version equals the pinned one.
- **Nothing downloads in Stage 2** → the browser User-Agent fix is already in the notebook; make sure
  you're on this repo's version and that `OPENFDA_KEY` is set.
