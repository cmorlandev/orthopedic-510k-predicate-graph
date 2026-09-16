#!/usr/bin/env python3
"""
Select edges from documents whose K-number load falls in a given range, so a
specific bin of estimate_spurious_edges.py can be calibrated by hand.

The 11-25 bin was left uncalibrated by the first adjudication: 244 documents
and 3,392 edges (11.1% of the graph) with no adjudicated edge in them. This
script writes the edges from documents in that range, which
spotcheck_worksheet.py can then turn into a worksheet.

Counting is identical to estimate_spurious_edges.py -- distinct K-numbers in
the extracted text, excluding the document's own number -- so a document
selected here lands in the same bin there.

    python select_bin_documents.py                     # 11-25, all of them
    python select_bin_documents.py --min 26            # the 26+ bin
    python select_bin_documents.py --out my_edges.csv

Then:
    python spotcheck_worksheet.py -d 3 --sample bin_11_25_edges.csv
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

KNUM = re.compile(r"\bK\s*0*(\d{6})\b")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=11, dest="lo")
    ap.add_argument("--max", type=int, default=25, dest="hi")
    ap.add_argument("--edges", default="data/predicate_edges.csv")
    ap.add_argument("--textdir", default="data/text")
    ap.add_argument("--out", default=None)
    ap.add_argument("--exclude", default="adjudication_199_edges.csv",
                    help="already-adjudicated edges to leave out "
                         "(pass '' to disable)")
    a = ap.parse_args()
    out = a.out or f"bin_{a.lo}_{a.hi}_edges.csv"

    for p in (a.edges, a.textdir):
        if not Path(p).exists():
            sys.exit(f"{p} not found -- run from the repository root")

    with open(a.edges, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    fn = list(rows[0].keys())
    low = {f.lower(): f for f in fn}
    c_dev = low.get("device_knumber") or next(f for f in fn if "device" in f.lower())
    c_pred = low.get("predicate_knumber") or next(f for f in fn if "predicat" in f.lower())
    c_tier = low.get("confidence") or low.get("tier")

    done = set()
    if a.exclude and Path(a.exclude).is_file():
        with open(a.exclude, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                d = r.get("device_knumber"); p = r.get("predicate_knumber")
                if d and p:
                    done.add((d, p))
        print(f"[excluding {len(done):,} already-adjudicated edges]",
              file=sys.stderr)

    edges = defaultdict(list)
    for r in rows:
        edges[r[c_dev]].append((r[c_pred], r.get(c_tier, "") if c_tier else ""))

    tdir = Path(a.textdir)
    picked, n_docs, no_text = [], 0, 0
    for i, (dev, elist) in enumerate(edges.items(), 1):
        if i % 2000 == 0:
            print(f"  read {i}/{len(edges)}", file=sys.stderr)
        f = tdir / f"{dev}.txt"
        if not f.is_file():
            no_text += 1
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        own = dev.lstrip("Kk").lstrip("0")
        load = len({m for m in KNUM.findall(txt) if m.lstrip("0") != own})
        if not (a.lo <= load <= a.hi):
            continue
        n_docs += 1
        for pred, tier in elist:
            if (dev, pred) in done:
                continue
            picked.append((dev, pred, tier, load))

    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["device_knumber", "predicate_knumber", "tier", "knums_in_doc"])
        w.writerows(picked)

    print(f"\nK-number load {a.lo}-{a.hi}: {n_docs:,} documents, "
          f"{len(picked):,} un-adjudicated edges")
    if n_docs:
        print(f"  mean {len(picked)/n_docs:.2f} edges per document")
    print(f"  documents with edges but no readable text, skipped: {no_text:,}")
    print(f"\n[written] {out}")
    print(f"\nnext:  python spotcheck_worksheet.py -d 3 --sample {out}")


if __name__ == "__main__":
    main()
