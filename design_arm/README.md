# Design-related recall arm (post hoc)

Separate arm responding to the recall-scope concern: a K-number linked to a recall is not evidence that the predicate's design was defective, because recalls can be limited to lots, components, packaging or labeling. This arm restricts exposure to design-related recalls.

**Status:** post hoc, not preregistered. Add an entry to ../DEVIATIONS.md before reporting.

## Fixed decisions (2026-10-15)
- Unit of classification: FDA recall event (res_event_number).
- Exposure: a predicate linked to at least one design-related recall event.
- Recall date: the predicate's earliest design-related recall (not its first recall of any kind).
- Successor exclusion: unchanged from the primary analysis (a citing device with any recall is excluded), so this arm is nested within the primary.
- Classification: FDA root cause mapped to five categories by cause_map.py. Every in-scope other_unclear event, plus a stratified validation sample (40 per auto-mapped category, seed 20261015), is coded by two blinded reviewers using CODEBOOK.md; disagreements are adjudicated.
- If coded categories agree poorly with the FDA mapping for any category, hand-code that whole category instead of relying on the mapping.

## Run order (working directory = design_arm/)
1. D1_recall_events.ipynb: event-level recall table and FDA mapping
2. D2_manual_coding.ipynb: Part A builds blinded sheets; Part B (after coding) computes kappa, adjudication, final codes
3. D3_design_analysis.ipynb: persistent-recalled-predicate analysis per exposure arm

Reads only ../snapshot/recall_raw.json.gz and files in ../data/ (corpus, edges, recalled_nodes, expected_values). Writes only inside design_arm/. The parent pipeline is untouched.
