#!/usr/bin/env python3
"""
Corpus-wide estimate of spurious predicate edges, calibrated on the hand
adjudication -- without relying on phrase matching.

Rationale. The adjudication established that every false-positive edge came
from documents that enumerate many cleared K-numbers (compatibility tables,
accessory lists). An ordinary 510(k) summary names 1-4 predicates; the two
inspected list-documents contained 9 and 50 K-numbers. That K-number LOAD is
a structural signal, independent of how the section happens to be worded --
which matters, because a regex scan of this corpus detected only 2 of the 4
documents known from adjudication to be pathological.

Method. Bin every edge-bearing document by how many distinct K-numbers its
extracted text contains. Within each bin, measure the observed false-positive
rate from the adjudicated edges that fall in it. Apply those rates to all
corpus edges in the same bin. Report per-bin and total, with Wilson intervals
and the adjudicated sample size behind every rate, so thinly-calibrated bins
are visible rather than hidden.

    python estimate_spurious_edges.py
    python estimate_spurious_edges.py --adjudicated my_verdicts.csv

Needs data/text/, data/predicate_edges.csv, and the adjudicated worksheet
(.csv or .xlsx). Writes spurious_edge_estimate.txt.
"""

import argparse
import csv
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

KNUM = re.compile(r"\bK\s*0*(\d{6})\b")
BINS = [(1, 2), (3, 5), (6, 10), (11, 25), (26, 10**9)]
Z = 1.959964

# Devices known pathological from the hand adjudication; used only to report
# where they land in the distribution, never to fit anything.
KNOWN_BAD = ["K190123", "K050441", "K233507", "K072326"]


def wilson(x, n, z=Z):
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def bin_of(k):
    for lo, hi in BINS:
        if lo <= k <= hi:
            return (lo, hi)
    return None


def bin_label(b):
    lo, hi = b
    return f"{lo}-{hi}" if hi < 10**9 else f"{lo}+"


def find_col(fn, *cands):
    low = {f.lower(): f for f in fn}
    for c in cands:
        if c in low:
            return low[c]
    for c in cands:
        for f in fn:
            if c in f.lower():
                return f
    return None


def read_table(path):
    suf = Path(path).suffix.lower()
    if suf in (".xlsx", ".xlsm", ".xls"):
        import pandas as pd
        for hdr in (0, 1):
            df = pd.read_excel(path, dtype=str, header=hdr).fillna("")
            if find_col(list(df.columns), "device_knumber", "device"):
                return df.to_dict("records")
        sys.exit(f"could not find a device column in {path}")
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if rows and not find_col(list(rows[0].keys()), "device_knumber", "device"):
        with open(path, newline="", encoding="utf-8-sig") as fh:
            next(fh)
            rows = list(csv.DictReader(fh))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adjudicated", default=None,
                    help="filled worksheet (.csv/.xlsx); default: looks for "
                         "adjudication_199_edges.csv then "
                         "spotcheck_worksheet.xlsx/.csv")
    ap.add_argument("--edges", default="data/predicate_edges.csv")
    ap.add_argument("--textdir", default="data/text")
    args = ap.parse_args()

    if args.adjudicated is None:
        for cand in ("adjudication_199_edges.csv", "spotcheck_worksheet.xlsx",
                     "spotcheck_worksheet.csv"):
            if Path(cand).is_file():
                args.adjudicated = cand
                break
        else:
            sys.exit("no adjudicated worksheet found -- pass --adjudicated")
    for p in (args.edges, args.textdir):
        if not Path(p).exists():
            sys.exit(f"{p} not found -- run from the repository root")

    # ---- all corpus edges
    rows = read_table(args.edges)
    fn = list(rows[0].keys())
    c_dev = find_col(fn, "device_knumber", "device")
    c_tier = find_col(fn, "confidence", "tier")
    corpus = defaultdict(list)
    for r in rows:
        corpus[r[c_dev]].append(r.get(c_tier, ""))
    print(f"corpus: {sum(len(v) for v in corpus.values()):,} edges over "
          f"{len(corpus):,} devices", file=sys.stderr)

    # ---- K-number load per document
    load = {}
    tdir = Path(args.textdir)
    for i, dev in enumerate(corpus, 1):
        if i % 2000 == 0:
            print(f"  read {i}/{len(corpus)}", file=sys.stderr)
        f = tdir / f"{dev}.txt"
        if not f.is_file():
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        own = dev.lstrip("Kk").lstrip("0")
        load[dev] = len({m for m in KNUM.findall(txt) if m.lstrip("0") != own})

    # ---- adjudicated verdicts
    adj = read_table(args.adjudicated)
    afn = list(adj[0].keys())
    a_dev = find_col(afn, "device_knumber", "device")
    a_ver = find_col(afn, "verdict_yes_no_unclear", "verdict")
    if not a_ver:
        sys.exit(f"no verdict column in {args.adjudicated} (cols: {afn})")
    seen = Counter()
    fp = Counter()
    for r in adj:
        v = str(r.get(a_ver) or "").replace("\u00a0", " ").strip().upper()
        if v in ("Y", "TRUE"):
            v = "YES"
        if v in ("N", "FALSE"):
            v = "NO"
        if v not in ("YES", "NO"):
            continue
        d = r[a_dev]
        if d not in load:
            continue
        b = bin_of(load[d])
        if b is None:
            continue
        seen[b] += 1
        if v == "NO":
            fp[b] += 1

    out = []

    def say(s=""):
        print(s)
        out.append(s)

    say("CORPUS ESTIMATE OF SPURIOUS EDGES, CALIBRATED ON HAND ADJUDICATION")
    say(f"edges file      : {args.edges}")
    say(f"adjudicated file: {args.adjudicated}")
    say(f"documents with edges and readable text: {len(load):,}")
    say()
    say("Binned by the number of distinct K-numbers in the source document.")
    say("FP rate is measured from adjudicated edges in that bin only.")
    say()
    hdr = (f"{'K-nums':>8} {'docs':>7} {'edges':>8} {'adjud':>6} {'FP':>4} "
           f"{'FP rate':>8} {'95% CI':>15} {'est. spurious':>14}")
    say(hdr)
    say("-" * len(hdr))

    tot_sp = tot_lo = tot_hi = 0.0
    tot_edges = 0
    uncal = []
    for b in BINS:
        devs = [d for d, k in load.items() if bin_of(k) == b]
        e = sum(len(corpus[d]) for d in devs)
        tot_edges += e
        n, x = seen[b], fp[b]
        if n == 0:
            say(f"{bin_label(b):>8} {len(devs):>7,} {e:>8,} {0:>6} {'-':>4} "
                f"{'no data':>8} {'-':>15} {'not estimable':>14}")
            uncal.append((bin_label(b), len(devs), e))
            continue
        rate = x / n
        lo, hi = wilson(x, n)
        tot_sp += e * rate
        tot_lo += e * lo
        tot_hi += e * hi
        say(f"{bin_label(b):>8} {len(devs):>7,} {e:>8,} {n:>6} {x:>4} "
            f"{100*rate:>7.1f}% {100*lo:>6.1f}-{100*hi:<6.1f}% "
            f"{int(e*rate):>14,}")

    say("-" * len(hdr))
    say(f"{'TOTAL':>8} {len(load):>7,} {tot_edges:>8,} "
        f"{sum(seen.values()):>6} {sum(fp.values()):>4} "
        f"{100*tot_sp/tot_edges:>7.2f}% {100*tot_lo/tot_edges:>6.2f}-"
        f"{100*tot_hi/tot_edges:<6.2f}% {int(tot_sp):>14,}")
    say()
    say(f"ESTIMATE: ~{int(tot_sp):,} spurious edges of {tot_edges:,} "
        f"({100*tot_sp/tot_edges:.2f}%)")
    say(f"   interval from per-bin Wilson bounds: "
        f"{int(tot_lo):,} to {int(tot_hi):,} "
        f"({100*tot_lo/tot_edges:.2f}-{100*tot_hi/tot_edges:.2f}%)")
    if uncal:
        say()
        say("UNCALIBRATED BINS -- no adjudicated edges landed here, so their")
        say("edges are EXCLUDED from the estimate above:")
        for lbl, nd, e in uncal:
            say(f"   {lbl:>8} K-numbers: {nd:,} docs, {e:,} edges unaccounted")
        say("   Adjudicating a handful of documents in these bins would close")
        say("   the gap; until then the total is a partial accounting.")

    say()
    say("WHERE THE KNOWN-PATHOLOGICAL DOCUMENTS LAND")
    for d in KNOWN_BAD:
        if d in load:
            say(f"   {d}: {load[d]:>3} K-numbers in text, "
                f"{len(corpus[d])} edges -> bin {bin_label(bin_of(load[d]))}")
        else:
            say(f"   {d}: no readable text found")
    say()
    say("If all four land in the high bins, K-number load separates the")
    say("failure mode without any dependence on section wording -- and the")
    say("recommendation to the analyst becomes a threshold rule rather than a")
    say("list of phrases to match.")

    Path("spurious_edge_estimate.txt").write_text("\n".join(out) + "\n",
                                                  encoding="utf-8")
    print("\n[written] spurious_edge_estimate.txt")


if __name__ == "__main__":
    main()
