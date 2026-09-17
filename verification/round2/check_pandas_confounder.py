#!/usr/bin/env python3
"""
check_pandas_confounder.py — distinguish two explanations for the +1/+3/+2/+1
shift in persistent_predicates / post_recall_citations / downstream_devices /
first_after_recall between the verifier's August rebuild and the analyst's run.

    (a) the four extra documents the verifier retrieved (11 extra edges)
    (b) pandas version: K060694's recall date is recorded as year 0012;
        pandas 2.1.4 drops it as unparseable, pandas >=2.2 parses it

Run from the repository root:

    python check_pandas_confounder.py

Three tests, in order of decisiveness.

1. Installed pandas version. The study pins 2.1.4. If that is what ran, (b)
   cannot apply and (a) stands.
2. Whether K060694's recorded recall date parses in the installed pandas, and
   whether K060694 is in the recalled set and carries citations at all.
3. Whether any of the 11 edges from the four extra documents has a RECALLED
   predicate. persistent_predicates counts recalled devices still cited as
   predicates, so an edge whose predicate is not recalled cannot move it. If
   none of the 11 touches a recalled predicate, (a) cannot produce the
   +1/+3/+2/+1 shift and (b) is the explanation.

Writes pandas_confounder_check.txt.
"""
import sys, csv, glob
from pathlib import Path

OUT = []
EXTRA_DOCS = ["K021661", "K041939", "K192214", "K192217"]
SUSPECT = "K060694"


def say(s=""):
    print(s)
    OUT.append(s)


def find_csv(*names):
    for n in names:
        for p in (Path(n), Path("data") / n):
            if p.is_file():
                return p
    return None


def read(p):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def col(rows, *subs):
    if not rows:
        return None
    for s in subs:
        for c in rows[0]:
            if s in c.lower():
                return c
    return None


say("=" * 72)
say("TEST 1 — installed pandas version")
say("=" * 72)
try:
    import pandas as pd
    ver = pd.__version__
    say(f"  pandas {ver}")
    pinned = ver.startswith("2.1.4")
    say(f"  study pins 2.1.4 -> {'MATCH' if pinned else 'DIFFERENT'}")
    if pinned:
        say("  => explanation (b) cannot apply to this run.")
    else:
        say("  => explanation (b) is live; continue to tests 2 and 3.")
except Exception as e:
    say(f"  pandas not importable: {e}")
    sys.exit(1)

req = find_csv("requirements.txt")
if req is None and Path("requirements.txt").is_file():
    req = Path("requirements.txt")
if req and req.suffix == ".txt":
    pins = [l.strip() for l in req.read_text().splitlines()
            if l.strip().lower().startswith("pandas")]
    say(f"  requirements.txt says: {pins or '(no pandas pin found)'}")

say()
say("=" * 72)
say(f"TEST 2 — {SUSPECT}'s recorded date, read from the frozen snapshot")
say("=" * 72)
import gzip, json
raw = Path("snapshot/recall_raw.json.gz")
vals = {}
if raw.is_file():
    with gzip.open(raw, "rt", encoding="utf-8", errors="replace") as fh:
        blob = json.load(fh)
    recs = blob.get("results", blob) if isinstance(blob, dict) else blob
    hits = [r for r in recs if SUSPECT in json.dumps(r)]
    say(f"  {raw}: {len(recs):,} records, {len(hits)} mentioning {SUSPECT}")
    for r in hits[:2]:
        vals = {k: v for k, v in r.items()
                if isinstance(v, str) and ("date" in k.lower() or "year" in k.lower())}
        say(f"    date fields: {vals}")
else:
    say(f"  {raw} not found — cannot read the authoritative value")

say()
say("  how the INSTALLED pandas handles each recorded date value:")
for k, v in (vals or {}).items():
    r1 = pd.to_datetime(v, errors="coerce")
    try:
        r2 = pd.to_datetime(v, format="%Y%m%d", errors="coerce")
    except Exception as e:
        r2 = f"{type(e).__name__}"
    flag = "" if str(r1) == "NaT" and str(r2) == "NaT" else "   <== PARSES"
    say(f"    {k}={v!r:12} to_datetime {r1!s:24} format=%Y%m%d {r2!s:24}{flag}")

say()
say("  NOTE: on pandas 2.3.3 a year-0012 date returns NaT via to_datetime,")
say("  format=%Y%m%d, and the datetime64[s]/[ms] casts added in 2.2. So")
say("  'pandas >=2.2 parses it' does not hold for those paths. A path that")
say("  builds np.datetime64(..., 's') and casts to [ns] DOES silently wrap")
say("  0012-03-15 to 1765-11-11 instead of erroring, which would count as a")
say("  valid early recall. Which path Stage 4/6 takes decides whether the")
say("  version matters; that needs the analyst's code, not this script.")

say()
say("=" * 72)
say("TEST 3 — do the 11 extra edges touch a RECALLED predicate?")
say("=" * 72)
edges_p = find_csv("predicate_edges_verifier_rule1_30487.csv", "predicate_edges.csv")
rec_p = find_csv("recalled_nodes.csv")
if edges_p is None or rec_p is None:
    say(f"  need both edge and recalled-node files; found "
        f"edges={edges_p} recalled={rec_p}")
else:
    erows = read(edges_p)
    rrows = read(rec_p)
    dc = col(erows, "device")
    pc = col(erows, "predicate")
    rc = col(rrows, "knumber", "k_number", "device")
    recalled = {r[rc].strip() for r in rrows if r.get(rc)}
    say(f"  {edges_p}: {len(erows):,} edges (device={dc!r} predicate={pc!r})")
    say(f"  {rec_p}: {len(recalled):,} recalled devices")
    say()
    touching = 0
    for d in EXTRA_DOCS:
        sub = [r for r in erows if r.get(dc, "").strip() == d]
        for r in sub:
            pred = r[pc].strip()
            hit = pred in recalled
            touching += hit
            say(f"    {d} -> {pred}   predicate recalled: {'YES' if hit else 'no'}")
        if not sub:
            say(f"    {d} -> (no edges)")
    say()
    say(f"  edges from the four extra documents whose predicate is recalled: {touching}")
    if touching == 0:
        say("  => the 11 edges cannot move persistent_predicates,")
        say("     post_recall_citations, downstream_devices or first_after_recall.")
        say("     Explanation (a) accounts for the EDGE COUNT only; the")
        say("     +1/+3/+2/+1 derived shift must come from elsewhere -- (b).")
    else:
        say("  => the 11 edges can contribute to the derived quantities.")
        say("     (a) remains viable; compare the magnitude against +1/+3/+2/+1.")

Path("pandas_confounder_check.txt").write_text("\n".join(OUT) + "\n")
print("\n[written] pandas_confounder_check.txt")
