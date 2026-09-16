#!/usr/bin/env python3
"""
Tally a completed hand-adjudication worksheet and compute per-tier precision
with Wilson 95% confidence intervals.

    python tally_spotcheck.py                        # reads spotcheck_worksheet.csv
    python tally_spotcheck.py --csv myfile.csv
    python tally_spotcheck.py --csv myfile.xlsx      # Excel also accepted

An .xlsx/.xls file is read via pandas (first sheet). A .csv is read with the
stdlib. Either way the verdict column is located by name, so it does not
matter which column letter it ended up in.

Reads the verdict column (YES / NO / UNCLEAR, case-insensitive; Y/N also
accepted) and writes spotcheck_result.txt, which you paste into the pull
request.

Two precision figures are reported per tier, and both belong in the report:

  adjudicable  - YES / (YES + NO), excluding UNCLEAR. The precision of the
                 edges you could actually decide.
  conservative - YES / (YES + NO + UNCLEAR), counting every UNCLEAR as a
                 failure. A lower bound that cannot be accused of
                 discarding inconvenient rows.

Wilson intervals are used because that is what the analyst used (their
121/121 -> 96.9% lower bound reproduces exactly under Wilson), so the numbers
are directly comparable.
"""

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

Z = 1.959964          # 95%
POP = {"SECTION_HEADED": 0.741, "PROXIMITY_ONLY": 0.259}
TOTAL_EDGES = 30487


def wilson(x, n, z=Z):
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def norm(v):
    v = str(v or "").replace("\u00a0", " ").strip().upper()
    if v in ("YES", "Y", "TRUE", "1"):
        return "YES"
    if v in ("NO", "N", "FALSE", "0"):
        return "NO"
    if v in ("UNCLEAR", "U", "?", "UNSURE", "AMBIGUOUS"):
        return "UNCLEAR"
    return ""


def find_col(fieldnames, *cands):
    low = {f.lower(): f for f in fieldnames}
    for c in cands:
        if c in low:
            return low[c]
    for c in cands:
        for f in fieldnames:
            if c in f.lower():
                return f
    return None


def read_rows(path):
    """Read the worksheet from .csv or .xlsx/.xls into a list of dicts."""
    suffix = Path(path).suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        try:
            import pandas as pd
        except ImportError:
            sys.exit(
                f"{path} is an Excel file and pandas is not installed.\n"
                f"Either install it (pip install pandas openpyxl) or, in "
                f"Excel, use\nFile > Save As > CSV UTF-8 and run this "
                f"script on the .csv instead.")
        try:
            df = pd.read_excel(path, dtype=str)
        except ImportError:
            sys.exit(
                f"reading {path} needs openpyxl (pip install openpyxl), or "
                f"save the sheet\nas CSV UTF-8 from Excel and use that.")
        df = df.where(df.notna(), "")
        return df.to_dict("records")
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None,
                    help="worksheet path; .csv or .xlsx. If omitted, looks "
                         "for spotcheck_worksheet.csv/.xlsx in this folder")
    args = ap.parse_args()

    if args.csv is None:
        for cand in ("spotcheck_worksheet.csv", "spotcheck_worksheet.xlsx",
                     "spotcheck_worksheet.xlsm", "spotcheck_worksheet.xls"):
            if Path(cand).is_file():
                args.csv = cand
                break
        else:
            sys.exit("no spotcheck_worksheet.csv or .xlsx found here -- pass "
                     "the path with --csv")

    if not Path(args.csv).is_file():
        sys.exit(f"{args.csv} not found")

    rows = read_rows(args.csv)
    if not rows:
        sys.exit("worksheet is empty")

    fn = list(rows[0].keys())
    c_ver = find_col(fn, "verdict_yes_no_unclear", "verdict",
                     "predicate_cited_as_predicate_yes_no_unclear", "cited")
    c_tier = find_col(fn, "tier", "confidence")
    c_dev = find_col(fn, "device_knumber", "device")
    c_pred = find_col(fn, "predicate_knumber", "predicate")
    c_note = find_col(fn, "note")
    if not c_ver:
        sys.exit(f"could not find a verdict column in {fn}")

    tally = defaultdict(lambda: defaultdict(int))
    devices = defaultdict(set)
    blank, nos, unclears = 0, [], []
    for r in rows:
        v = norm(r.get(c_ver))
        t = (r.get(c_tier) or "UNSPECIFIED").strip() or "UNSPECIFIED"
        if not v:
            blank += 1
            continue
        tally[t][v] += 1
        if c_dev:
            devices[t].add(r[c_dev])
        if v == "NO":
            nos.append(r)
        elif v == "UNCLEAR":
            unclears.append(r)

    out = []

    def say(s=""):
        print(s)
        out.append(s)

    say("HAND ADJUDICATION RESULT")
    say(f"worksheet: {args.csv}")
    say(f"rows: {len(rows)}   adjudicated: {len(rows)-blank}   blank: {blank}")
    if blank:
        say(f"  !! {blank} row(s) have no verdict yet -- they are excluded below")
    say()

    grand = defaultdict(int)
    for t in sorted(tally):
        y = tally[t]["YES"]; n = tally[t]["NO"]; u = tally[t]["UNCLEAR"]
        for k, v in (("YES", y), ("NO", n), ("UNCLEAR", u)):
            grand[k] += v
        nd = len(devices.get(t, ()))
        say("=" * 66)
        say(f"{t}    ({y+n+u} edges"
            + (f" over {nd} devices)" if nd else ")"))
        say(f"   YES {y}   NO {n}   UNCLEAR {u}")
        if y + n:
            lo, hi = wilson(y, y + n)
            say(f"   precision (adjudicable)  {100*y/(y+n):6.1f}%   "
                f"Wilson 95% CI {100*lo:.1f}-{100*hi:.1f}%")
        if y + n + u:
            lo2, hi2 = wilson(y, y + n + u)
            say(f"   precision (conservative) {100*y/(y+n+u):6.1f}%   "
                f"Wilson 95% CI {100*lo2:.1f}-{100*hi2:.1f}%")
            if t in POP:
                say(f"   -> at the conservative lower bound, up to "
                    f"{int(TOTAL_EDGES*POP[t]*(1-lo2)):,} of the "
                    f"{int(TOTAL_EDGES*POP[t]):,} {t} edges could be spurious")
    say("=" * 66)

    gy, gn, gu = grand["YES"], grand["NO"], grand["UNCLEAR"]
    say()
    say(f"POOLED (unweighted): YES {gy}  NO {gn}  UNCLEAR {gu}")
    if gy + gn:
        lo, hi = wilson(gy, gy + gn)
        say(f"   {100*gy/(gy+gn):.1f}%  Wilson 95% CI {100*lo:.1f}-{100*hi:.1f}%")
    say("   NOTE: the pooled figure mixes tiers in the proportions you")
    say("   SAMPLED, not the proportions in the graph (SECTION_HEADED 74.1%,")
    say("   PROXIMITY_ONLY 25.9%). Report the per-tier figures as primary.")

    if nos or unclears:
        say()
        say("ROWS NEEDING NARRATIVE IN THE REPORT")
        for label, group in (("NO", nos), ("UNCLEAR", unclears)):
            for r in group:
                d = r.get(c_dev, "?"); pr = r.get(c_pred, "?")
                nt = (r.get(c_note) or "").strip()
                say(f"  [{label}] {d} -> {pr}"
                    + (f"   note: {nt}" if nt else "   note: (none given)"))
        say()
        say("  Every NO and UNCLEAR should get a sentence in the pull request.")
        say("  A single documented false positive is the most informative")
        say("  result this check can produce -- do not bury it in a ratio.")
    else:
        say()
        say("No NO or UNCLEAR verdicts recorded.")
        say("  State the sample size and CI plainly: 'all N edges confirmed'")
        say("  is not the same claim as '100% precision across 30,487 edges'.")

    Path("spotcheck_result.txt").write_text("\n".join(out) + "\n",
                                            encoding="utf-8")
    print("\n[written] spotcheck_result.txt")


if __name__ == "__main__":
    main()
