#!/usr/bin/env python3
"""
Corpus-wide scan for the document structure that caused every false-positive
edge in the hand adjudication: component/accessory compatibility sections and
tables listing cleared 510(k) numbers of parts that may be USED WITH the
subject device, rather than devices it claims substantial equivalence to.

Run from the repository root, after notebooks 02 and 03.

    python scan_compatibility_sections.py

Reads data/text/*.txt and data/predicate_edges.csv. Writes
compatibility_scan.txt (paste into the report) and
compatibility_scan_devices.csv (the affected devices and their edge counts).

Why this exists: the adjudication established that 37 of 37 false positives
came from 4 of 45 documents, and that ordinary documents produced 155 of 155
correct edges. That makes the corpus-wide question "how many documents have
this structure?", which is a text search rather than a re-adjudication.
"""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Observed within the 4 list-documents in the adjudicated sample.
OBSERVED_FP_RATE_IN_LIST_DOCS = 37 / 44

STRONG = [
    ("accessory_compat_heading",
     re.compile(r"component\s+and\s+accessor\w*\s+compatibilit", re.I)),
    ("compatibility_of_subject",
     re.compile(r"compatibilit\w*\s+of\s+the\s+subject\s+device", re.I)),
    ("compatible_X_including_510k",
     re.compile(r"compatible[^\n]{0,60}includ\w*\s+510\s*\(?k\)?", re.I)),
    ("compatible_components_indications",
     re.compile(r"compatible\s+components\s+that\s+can\s+be\s+used", re.I)),
]

WEAK = [
    ("compatible_shells_or_femoral",
     re.compile(r"compatible\s+(shells|liners|femoral|acetabular|stems)", re.I)),
    ("table_of_compatible",
     re.compile(r"table\s*#?\s*\d[^\n]{0,40}compatib", re.I)),
    ("may_be_used_with",
     re.compile(r"(may|can)\s+be\s+used\s+(in\s+combination\s+)?with[^\n]{0,80}"
                r"K\s*\d{6}", re.I)),
]

KNUM = re.compile(r"\bK\s*\d{6}\b")


def classify(txt):
    hits = [name for name, pat in STRONG if pat.search(txt)]
    if hits:
        return "STRONG", hits
    hits = [name for name, pat in WEAK if pat.search(txt)]
    if hits:
        return "WEAK", hits
    return "NONE", []


def main():
    tdir = Path("data/text")
    if not tdir.is_dir():
        sys.exit("data/text/ not found -- run this from the repository root "
                 "after notebook 02")

    files = sorted(tdir.glob("*.txt"))
    if not files:
        sys.exit("no .txt files in data/text/")

    edge_file = Path("data/predicate_edges.csv")
    edges_by_dev = Counter()
    tier_by_dev = defaultdict(Counter)
    if edge_file.is_file():
        with open(edge_file, newline="", encoding="utf-8-sig") as fh:
            rd = csv.DictReader(fh)
            fn = rd.fieldnames or []
            dcol = next((c for c in fn if c.lower() in
                         ("device_knumber", "device_k", "device")), None)
            tcol = next((c for c in fn if c.lower() in
                         ("confidence", "tier")), None)
            if dcol:
                for r in rd:
                    edges_by_dev[r[dcol]] += 1
                    if tcol:
                        tier_by_dev[r[dcol]][r[tcol]] += 1
    else:
        print("[warn] data/predicate_edges.csv not found -- edge attribution "
              "will be skipped", file=sys.stderr)

    buckets = defaultdict(list)
    marker_counts = Counter()
    for i, f in enumerate(files, 1):
        if i % 2000 == 0:
            print(f"  scanned {i}/{len(files)}", file=sys.stderr)
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        cls, hits = classify(txt)
        if cls == "NONE":
            buckets["NONE"].append((f.stem, 0))
            continue
        marker_counts.update(hits)
        buckets[cls].append((f.stem, len(KNUM.findall(txt))))

    out = []

    def say(s=""):
        print(s)
        out.append(s)

    n_total = len(files)
    n_strong = len(buckets["STRONG"])
    n_weak = len(buckets["WEAK"])

    say("CORPUS-WIDE SCAN FOR COMPATIBILITY-TABLE DOCUMENTS")
    say(f"documents scanned (data/text/*.txt): {n_total:,}")
    say()
    say(f"  STRONG marker (explicit compatibility section/table): "
        f"{n_strong:,}  ({100*n_strong/n_total:.2f}%)")
    say(f"  WEAK marker only (suggestive wording):                "
        f"{n_weak:,}  ({100*n_weak/n_total:.2f}%)")
    say(f"  no marker:                                            "
        f"{n_total-n_strong-n_weak:,}")
    say()
    say("marker frequencies:")
    for name, c in marker_counts.most_common():
        say(f"  {name:36} {c:,}")

    if edges_by_dev:
        say()
        say("EDGE ATTRIBUTION (from data/predicate_edges.csv)")
        tot_edges = sum(edges_by_dev.values())
        for cls in ("STRONG", "WEAK"):
            devs = [d for d, _ in buckets[cls]]
            e = sum(edges_by_dev.get(d, 0) for d in devs)
            with_edges = sum(1 for d in devs if edges_by_dev.get(d, 0))
            say(f"  {cls}: {with_edges:,} of {len(devs):,} such documents have "
                f"edges, carrying {e:,} edges "
                f"({100*e/tot_edges:.2f}% of {tot_edges:,})")
            if with_edges:
                say(f"        mean {e/with_edges:.2f} edges per such document "
                    f"(adjudicated list-documents averaged 11.0)")
            say(f"        at the observed {100*OBSERVED_FP_RATE_IN_LIST_DOCS:.1f}% "
                f"false-positive rate inside such documents,")
            say(f"        estimated spurious edges: "
                f"{int(e*OBSERVED_FP_RATE_IN_LIST_DOCS):,}")
        say()
        say("  Interpretation: this replaces the population-weighted "
            "extrapolation")
        say("  (~4,900 spurious, cluster CI 0.6-39.3%) with a count grounded "
            "in the")
        say("  actual corpus. Report the STRONG figure as primary and WEAK as "
            "an upper")
        say("  bound; confirm by opening two or three STRONG documents that "
            "were NOT")
        say("  in the adjudicated sample.")

    with open("compatibility_scan_devices.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["device_knumber", "marker_class", "k_numbers_in_text",
                    "edges_in_graph", "tiers"])
        for cls in ("STRONG", "WEAK"):
            for dev, nk in sorted(buckets[cls]):
                if edges_by_dev.get(dev, 0):
                    w.writerow([dev, cls, nk, edges_by_dev[dev],
                                dict(tier_by_dev.get(dev, {}))])

    Path("compatibility_scan.txt").write_text("\n".join(out) + "\n",
                                              encoding="utf-8")
    print("\n[written] compatibility_scan.txt")
    print("[written] compatibility_scan_devices.csv")


if __name__ == "__main__":
    main()
