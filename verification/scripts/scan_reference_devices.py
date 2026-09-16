#!/usr/bin/env python3
"""
Corpus-wide scan for edges that originate in a "Reference Device" section.

Why this matters more than the compatibility-table scan. In FDA 510(k)
terminology a REFERENCE device is a formally distinct thing from a PREDICATE:
it is cited for supporting data, test methods, standards or labelling
precedent, and carries no substantial-equivalence claim. Auditing K190123
against its source document showed that all five of its SECTION_HEADED false
positives came from a section headed "V. Reference Device:" -- not from a
compatibility table. Reference-device sections are a standard element of
modern 510(k) summaries, so unlike compatibility tables they may affect a
large share of the corpus, and they contaminate the HIGH-confidence tier.

Run from the repository root.

    python scan_reference_devices.py

Reads data/text/*.txt and data/predicate_edges.csv. Writes
reference_device_scan.txt and reference_device_edges.csv (every edge whose
K-number appears inside a reference-device section).

Attribution rule: a K-number is attributed to the reference section only if it
appears there and NOT also inside a predicate section of the same document --
a device can legitimately be both, as K170444 is in K190123.
"""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

KN = re.compile(r"\bK\s*0*(\d{6})\b")

REF_HEAD = re.compile(
    r"^[^\S\n]{0,8}(?:[IVXivx]{1,5}\s*[.)]\s*|\d{1,2}\s*[.)]\s*)?"
    r"reference\s+(?:device|product)s?\b[^\n]{0,40}$", re.I | re.M)
PRED_HEAD = re.compile(
    r"^[^\S\n]{0,8}(?:[IVXivx]{1,5}\s*[.)]\s*|\d{1,2}\s*[.)]\s*)?"
    r"(?:legally\s+marketed\s+)?predicate\s+device(?:s)?\b[^\n]{0,40}$",
    re.I | re.M)
# any plausible next-section heading
NEXT_HEAD = re.compile(
    r"^[^\S\n]{0,8}(?:[IVXivx]{1,5}\s*[.)]\s+[A-Z][^\n]{0,80}"
    r"|\d{1,2}\s*[.)]\s+[A-Z][^\n]{0,80}"
    r"|[A-Z][A-Za-z /,&()-]{3,70}:)[^\S\n]*$", re.M)


def span_after(txt, m, cap=2500):
    start = m.end()
    nxt = NEXT_HEAD.search(txt, start)
    end = min(nxt.start(), start + cap) if nxt else min(len(txt), start + cap)
    return txt[start:end]


def knums(s):
    return {"K" + g.zfill(6) for g in KN.findall(s)}


def main():
    tdir, efile = Path("data/text"), Path("data/predicate_edges.csv")
    for p in (tdir, efile):
        if not p.exists():
            sys.exit(f"{p} not found -- run from the repository root")

    with open(efile, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    fn = list(rows[0].keys())
    low = {f.lower(): f for f in fn}
    c_dev = low.get("device_knumber") or next(f for f in fn if "device" in f.lower())
    c_pred = low.get("predicate_knumber") or next(f for f in fn if "predicat" in f.lower())
    c_tier = low.get("confidence") or low.get("tier")

    edges = defaultdict(list)
    for r in rows:
        edges[r[c_dev]].append((r[c_pred], r.get(c_tier, "") if c_tier else ""))
    total_edges = sum(len(v) for v in edges.values())

    n_docs = n_ref = n_pred_sec = 0
    ref_edges, tier_ct = [], Counter()
    both_ct = 0
    for i, (dev, elist) in enumerate(edges.items(), 1):
        if i % 2000 == 0:
            print(f"  read {i}/{len(edges)}", file=sys.stderr)
        f = tdir / f"{dev}.txt"
        if not f.is_file():
            continue
        n_docs += 1
        txt = f.read_text(encoding="utf-8", errors="replace")
        rm = REF_HEAD.search(txt)
        pm = PRED_HEAD.search(txt)
        if pm:
            n_pred_sec += 1
        if not rm:
            continue
        n_ref += 1
        ref_ks = knums(span_after(txt, rm))
        pred_ks = knums(span_after(txt, pm)) if pm else set()
        for pred, tier in elist:
            if pred in ref_ks:
                if pred in pred_ks:
                    both_ct += 1
                    continue
                ref_edges.append((dev, pred, tier))
                tier_ct[tier] += 1

    out = []

    def say(s=""):
        print(s)
        out.append(s)

    say("CORPUS SCAN: EDGES ORIGINATING IN A \"REFERENCE DEVICE\" SECTION")
    say()
    say(f"edge-bearing documents with readable text : {n_docs:,}")
    say(f"  with a predicate-device section heading : {n_pred_sec:,} "
        f"({100*n_pred_sec/max(n_docs,1):.1f}%)")
    say(f"  with a reference-device section heading : {n_ref:,} "
        f"({100*n_ref/max(n_docs,1):.1f}%)")
    say()
    say(f"edges whose K-number appears in a reference section : "
        f"{len(ref_edges):,} of {total_edges:,} "
        f"({100*len(ref_edges)/total_edges:.2f}%)")
    say(f"  excluded because the same K-number is ALSO in the predicate")
    say(f"  section of that document (legitimately both) : {both_ct:,}")
    say()
    if tier_ct:
        say("by confidence tier:")
        for t, c in tier_ct.most_common():
            say(f"  {t or '(blank)':16} {c:,}")
        say()
        sh = tier_ct.get("SECTION_HEADED", 0)
        say(f"  SECTION_HEADED edges from reference sections: {sh:,}")
        say(f"  -> {100*sh/22580:.2f}% of the 22,580 SECTION_HEADED edges, i.e.")
        say(f"     contamination of the tier the study treats as "
            f"high-confidence")
        say(f"     and of sens_high_conf specifically.")
    say()
    say("CALIBRATION FROM THE HAND ADJUDICATION")
    say("  In K190123, all 5 SECTION_HEADED false positives were reference-")
    say("  section citations, and all 5 were adjudicated NO. That is a single")
    say("  document: the observed false-positive rate for this class is 5/5,")
    say("  which is a point estimate on n=5, not a measured rate. The count")
    say("  above is the population at risk, NOT an estimate of spurious edges.")
    say()
    say("  What would settle it: adjudicate 20-30 reference-section edges drawn")
    say("  from reference_device_edges.csv across different documents. If they")
    say("  are uniformly NO, every edge counted above is spurious and the")
    say("  correction is exact rather than estimated.")
    say()
    say("NOTE ON INTERPRETATION")
    say("  Whether these edges SHOULD be in the graph is a definitional")
    say("  question for the analyst, not a defect per se. Notebook 03's own")
    say("  instruction says \"genuine predicate/reference citation\", which")
    say("  reads as deliberately including them; the verifier manual section 9")
    say("  says \"genuinely cited as predicates\", which excludes them. The")
    say("  study's claims are about predicate relationships, so the strict")
    say("  reading is the one the conclusions require -- but the analyst should")
    say("  state which was intended.")

    with open("reference_device_edges.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["device_knumber", "predicate_knumber", "tier"])
        w.writerows(ref_edges)

    Path("reference_device_scan.txt").write_text("\n".join(out) + "\n",
                                                 encoding="utf-8")
    print("\n[written] reference_device_scan.txt")
    print(f"[written] reference_device_edges.csv ({len(ref_edges):,} rows)")


if __name__ == "__main__":
    main()
