#!/usr/bin/env python3
"""
Build a hand-adjudication worksheet for the 510(k) predicate-graph verification
(verifier manual step 9 / quickstart step 18).

Run from the repository root AFTER notebook 03 has produced
data/validation_sample.csv.

    python spotcheck_worksheet.py            # 5 + 5 stratified, seed 20260828
    python spotcheck_worksheet.py -n 20      # bigger sample
    python spotcheck_worksheet.py --seed 7   # different draw

Writes spotcheck_worksheet.csv (fill in the verdict column by hand) and
spotcheck_worksheet.txt (the same rows with the extracted local context, so
you can see what the pipeline saw next to what the document says).

Why stratified: PROXIMITY_ONLY is the weaker extraction tier and the place
false positives concentrate, but it is only ~26% of edges, so a simple random
draw of 10 would give ~2-3 of them. Sampling each tier separately gives a
usable per-tier precision. Do NOT pool the two tiers into one precision
number without weighting them back to their population shares.
"""

import argparse
import csv
import json
import os
import random
import re
import sys
from pathlib import Path

FDA_LOOKUP = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k}"
CONTEXT_CHARS = 320


def find_col(fieldnames, *candidates):
    low = {f.lower(): f for f in fieldnames}
    for c in candidates:
        if c in low:
            return low[c]
    for c in candidates:
        for f in fieldnames:
            if c in f.lower():
                return f
    return None


def load_sample(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit(f"{path} is empty")
    fn = rows[0].keys()
    dev = find_col(fn, "device_knumber", "device_k", "k_number", "device")
    pred = find_col(fn, "predicate_knumber", "predicate_k", "predicate")
    conf = find_col(fn, "confidence", "tier", "conf")
    if not dev or not pred:
        sys.exit(f"could not identify device/predicate columns in {list(fn)}")
    return rows, dev, pred, conf


def local_text_path(k):
    for cand in (Path("data/text") / f"{k}.txt",
                 Path("data/text") / f"{k.upper()}.txt"):
        if cand.is_file():
            return cand
    return None


PDF_DIRS = [Path("data/pdf"), Path("data/pdfs"), Path("data/summaries"),
            Path("data/pdf_cache"), Path("data")]


def local_pdf_path(k):
    for d in PDF_DIRS:
        if not d.is_dir():
            continue
        for cand in (d / f"{k}.pdf", d / f"{k.upper()}.pdf",
                     d / f"{k.lower()}.pdf"):
            if cand.is_file():
                return cand
    return None


def contexts_for(k_device, k_pred):
    """Return the snippets of the device's extracted text around the predicate
    K-number -- i.e. exactly what the pipeline had to work from."""
    p = local_text_path(k_device)
    if p is None:
        return ["(no local extracted text for this device)"]
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"(could not read {p}: {exc})"]
    bare = k_pred.lstrip("Kk").lstrip("0")
    pat = re.compile(r"[Kk]\s*0*" + re.escape(bare) + r"\b")
    out = []
    for m in pat.finditer(txt):
        a = max(0, m.start() - CONTEXT_CHARS // 2)
        b = min(len(txt), m.end() + CONTEXT_CHARS // 2)
        snip = " ".join(txt[a:b].split())
        out.append(snip)
        if len(out) >= 3:
            break
    return out or [f"(!! {k_pred} does NOT appear in the extracted text -- "
                   f"flag this: the edge may be a parsing artefact)"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n-per-tier", type=int, default=5,
                    help="edges to draw PER confidence tier (default 5)")
    ap.add_argument("-d", "--devices", type=int, default=None,
                    help="INSTEAD of per-tier edge sampling: draw this many "
                         "DEVICES and include every edge each one has. This "
                         "is the efficient way to work (one PDF open per "
                         "device) and matches the analyst's own design "
                         "(60 devices). Recommended: -d 20")
    ap.add_argument("--seed", type=int, default=20260828,
                    help="record this in your report (default 20260828)")
    ap.add_argument("--sample", default="data/validation_sample.csv")
    args = ap.parse_args()

    if not Path(args.sample).is_file():
        sys.exit(f"{args.sample} not found -- run notebook 03 first, and run "
                 f"this from the repository root")

    rows, dev, pred, conf = load_sample(args.sample)

    # group by tier
    tiers = {}
    for r in rows:
        t = (r.get(conf) or "UNSPECIFIED").strip() if conf else "UNSPECIFIED"
        tiers.setdefault(t, []).append(r)

    rng = random.Random(args.seed)
    picked = []
    if args.devices:
        # cluster sample: pick devices, take ALL of each device's edges
        by_dev = {}
        for r in rows:
            by_dev.setdefault(r[dev], []).append(r)
        dev_ids = sorted(by_dev)
        take = min(args.devices, len(dev_ids))
        chosen = rng.sample(dev_ids, take)
        for k in chosen:
            for r in by_dev[k]:
                t = (r.get(conf) or "UNSPECIFIED").strip() if conf else "UNSPECIFIED"
                picked.append((t, r))
        mode = (f"{take} devices drawn at random, ALL edges of each included "
                f"({len(picked)} edges over {take} devices)")
    else:
        for t in sorted(tiers):
            pool = tiers[t]
            take = min(args.n_per_tier, len(pool))
            picked.extend((t, r) for r in rng.sample(pool, take))
        mode = (f"{args.n_per_tier} edges per confidence tier, stratified "
                f"-- NOT a simple random sample of edges")

    if args.devices:
        picked.sort(key=lambda tr: (tr[1][dev], tr[1][pred]))

    # ---------------------------------------------------------------- CSV
    with open("spotcheck_worksheet.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "device_knumber", "predicate_knumber", "tier",
                    "local_pdf", "fda_url", "verdict_YES_NO_UNCLEAR",
                    "note"])
        for i, (t, r) in enumerate(picked, 1):
            lp = local_pdf_path(r[dev])
            w.writerow([i, r[dev], r[pred], t, lp or "",
                        FDA_LOOKUP.format(k=r[dev]), "", ""])

    # ---------------------------------------------------------------- TXT
    lines = []
    lines.append("HAND ADJUDICATION WORKSHEET")
    lines.append(f"sample file : {args.sample}")
    lines.append(f"seed        : {args.seed}   (record this in your report)")
    lines.append(f"selection   : {mode}")
    lines.append(f"tiers found : "
                 + ", ".join(f"{t} (n={len(v)})" for t, v in sorted(tiers.items())))
    lines.append("")
    lines.append("For each row: open the FDA URL, find the 510(k) summary "
                 "document, and decide whether the")
    lines.append("predicate K-number is genuinely put forward as a PREDICATE "
                 "for this device -- as opposed to")
    lines.append("being mentioned in a reference list, a standards "
                 "discussion, or a contrast ('unlike K...').")
    lines.append("Record YES / NO / UNCLEAR in spotcheck_worksheet.csv.")
    lines.append("")
    lines.append("The 'pipeline saw' snippets below are from the locally "
                 "extracted text. They show what the")
    lines.append("edge rule matched on. Compare them against the real "
                 "document, not instead of it.")
    lines.append("")
    for i, (t, r) in enumerate(picked, 1):
        lines.append("=" * 74)
        lines.append(f"[{i}] device {r[dev]}   ->   predicate {r[pred]}    "
                     f"tier: {t}")
        lines.append(f"    FDA:   {FDA_LOOKUP.format(k=r[dev])}")
        lp = local_pdf_path(r[dev])
        lines.append(f"    PDF:   {lp if lp else '(no local PDF found)'}")
        lt = local_text_path(r[dev])
        lines.append(f"    text:  {lt if lt else '(none)'}")
        lines.append("    verdict: ______  (YES / NO / UNCLEAR)")
        lines.append("")
        for j, snip in enumerate(contexts_for(r[dev], r[pred]), 1):
            lines.append(f"    pipeline saw #{j}:")
            lines.append(f"      ...{snip}...")
            lines.append("")
    lines.append("=" * 74)
    lines.append("")
    lines.append("When done, report PER TIER:")
    lines.append("   SECTION_HEADED : __ of __ confirmed")
    lines.append("   PROXIMITY_ONLY : __ of __ confirmed")
    lines.append("and say how the rows were chosen (stratified, seed above).")
    lines.append("Do not pool the tiers into one precision figure without "
                 "weighting to population shares")
    lines.append("(SECTION_HEADED 74.1%, PROXIMITY_ONLY 25.9% of 30,487 edges).")
    if args.devices:
        lines.append("")
        lines.append("NOTE on device-mode sampling: edges within one device "
                     "are correlated -- if a PDF")
        lines.append("parsed badly, all of that device's edges fail together. "
                     "A plain binomial interval")
        lines.append("slightly understates the uncertainty. Report the device "
                     "count alongside the edge")
        lines.append("count so a reader can see the clustering "
                     "(the analyst's 121 edges came from 60")
        lines.append("devices the same way).")

    Path("spotcheck_worksheet.txt").write_text("\n".join(lines),
                                               encoding="utf-8")

    print(f"picked {len(picked)} edges "
          + ", ".join(f"{t}:{sum(1 for x,_ in picked if x==t)}"
                      for t in sorted(tiers)))
    print("wrote spotcheck_worksheet.csv  (fill in the verdict column)")
    print("wrote spotcheck_worksheet.txt  (context to read alongside)")


if __name__ == "__main__":
    main()
