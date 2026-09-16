#!/usr/bin/env python3
"""
diagnose_zones.py — instrument edge_rules.exclusion_zones() on specific documents.

Run from the repository root AFTER data/text/ is in place:

    python diagnose_zones.py K221844 K241000 K213591        # the 7 false removals
    python diagnose_zones.py K243839                        # the 20 missed edges
    python diagnose_zones.py --runaway                      # scan the whole corpus

Answers two questions the four-cell reconciliation left open.

1. FALSE REMOVALS. exclusion_zones() closes a zone only when a _zone_end() line
   is found; if none follows, the zone runs to len(text). An unterminated
   "Reference Devices:" near the end of a document therefore excludes the whole
   remainder, which would remove true predicates named after it. For each named
   document this prints every zone with its span as a percentage of the
   document, and flags any zone covering more than 25%.

2. MISSES. For a document whose compatibility enumeration Rule 2 did not catch,
   this prints the candidate heading lines that _zone_start() rejected, with the
   reason, so a new exclusion pattern can be written against real text rather
   than guessed.

--runaway scans every document with an extracted text file and lists those with
a zone covering more than 25% of the document, worst first. That is the
corpus-wide version of question 1.
"""
import sys, json, glob, os
from pathlib import Path

sys.path.insert(0, ".")
import edge_rules as er

TEXT_DIRS = ["data/text", "data/texts", "text"]


def text_path(kn):
    for d in TEXT_DIRS:
        for ext in (".txt", ""):
            p = Path(d) / f"{kn}{ext}"
            if p.is_file():
                return p
    hits = [Path(p) for d in TEXT_DIRS for p in glob.glob(f"{d}/*{kn}*")]
    return hits[0] if hits else None


def load_corpus_knumbers():
    for cand in ("data/corpus.csv", "corpus.csv"):
        if os.path.isfile(cand):
            import csv
            with open(cand, newline="", encoding="utf-8-sig") as fh:
                rows = list(csv.DictReader(fh))
            for col in ("knumber", "k_number", "device_knumber", "K_NUMBER"):
                if rows and col in rows[0]:
                    return {r[col].strip() for r in rows if r[col].strip()}
    return None


def report(kn, valid):
    p = text_path(kn)
    if p is None:
        print(f"\n=== {kn} — NO TEXT FILE FOUND in {TEXT_DIRS} ===")
        return
    txt = p.read_text(encoding="utf-8", errors="replace")
    zones = er.exclusion_zones(txt)
    n = len(txt)
    print(f"\n=== {kn} — {p}  ({n:,} chars, {txt.count(chr(10))+1} lines) ===")
    if not zones:
        print("  NO EXCLUSION ZONES FOUND")
    for a, b, kind, head in zones:
        pct = 100 * (b - a) / n
        flag = "  <== RUNAWAY ZONE" if pct > 25 else ""
        tail = " [runs to end of document]" if b >= n else ""
        print(f"  {kind:9} {a:>7}-{b:<7} {pct:5.1f}%  {head[:64]!r}{tail}{flag}")

    if valid:
        out = er.extract(txt, kn, valid)
        print(f"  rule1 {len(out['rule1'])} edges | rule2 {len(out['rule2'])} "
              f"| excluded {len(out['excluded'])}")
        for pred, kind, head, conf in out["excluded"]:
            print(f"    excluded {pred}  {kind:9} {conf:11} {head[:52]!r}")

    # heading-like lines that did NOT open a zone but mention compatibility-ish words
    print("  -- heading-like lines rejected as zone starts (candidate new patterns) --")
    shown = 0
    for line in txt.splitlines():
        s = line.strip()
        if not s or er._zone_start(s) is not None:
            continue
        if not er.COMPAT.search(s) and not er.REFDEV.match(s) \
           and "reference" not in s.lower() and "compat" not in s.lower():
            continue
        why = ("not heading-like (len %d%s)" % (len(s), ", ends '.'" if s.endswith(".") else "")
               if not er._heading_like(s)
               else "SECTION_WORDS veto" if er.COMPAT.search(s)
               else "REFDEV pattern did not match")
        print(f"    {why:34} {s[:70]!r}")
        shown += 1
        if shown >= 12:
            print("    ... (truncated)")
            break
    if shown == 0:
        print("    (none)")


def runaway_scan(valid, thresh=25.0):
    files = [Path(p) for d in TEXT_DIRS for p in glob.glob(f"{d}/*.txt")]
    print(f"scanning {len(files):,} text files for zones covering >{thresh:.0f}% "
          f"of a document")
    bad = []
    for p in files:
        txt = p.read_text(encoding="utf-8", errors="replace")
        n = len(txt) or 1
        for a, b, kind, head in er.exclusion_zones(txt):
            pct = 100 * (b - a) / n
            if pct > thresh:
                bad.append((pct, p.stem, kind, b >= n, head[:60]))
    bad.sort(reverse=True)
    print(f"{len(bad):,} runaway zones in {len({b[1] for b in bad}):,} documents\n")
    print(f"{'pct':>6}  {'document':12} {'kind':9} {'to_EOF':6}  heading")
    for pct, stem, kind, eof, head in bad[:40]:
        print(f"{pct:6.1f}  {stem:12} {kind:9} {str(eof):6}  {head!r}")
    if len(bad) > 40:
        print(f"... and {len(bad)-40:,} more")
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    valid = load_corpus_knumbers()
    if valid is None:
        print("note: corpus.csv not found — skipping per-document edge counts\n")
    if "--runaway" in args:
        runaway_scan(valid)
    else:
        if not args:
            args = ["K221844", "K241000", "K213591", "K243839"]
            print("no documents given; using the 7 false removals + the 20 misses")
        for kn in args:
            report(kn, valid)
