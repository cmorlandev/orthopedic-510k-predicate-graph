#!/usr/bin/env python3
"""
identify_text_diffs.py — name the documents where the local text corpus differs
from the frozen record, and count what they contribute to the edge graph.

Run from the repository root on the rule2-rerun branch:

    python identify_text_diffs.py

Reads TEXT_SNAPSHOT_files.csv (the committed per-file hash manifest) and hashes
the local data/text/ files. Reports three groups:

  CHANGED   — present in both, different content. These must be replaced with
              the analyst's copies before Stage 3's corpus-hash check can pass.
  EXTRA     — present locally, absent from the freeze. These are summaries FDA
              served the verifier and 404'd for the analyst; move them aside.
  MISSING   — in the freeze, absent locally. Expected to be empty.

Then joins the affected documents against data/predicate_edges.csv to show how
many edges they carry, which is what the +11 edge difference has to come out of.

Writes text_corpus_diffs.txt.
"""
import csv, hashlib, sys
from pathlib import Path

MANIFEST = Path("TEXT_SNAPSHOT_files.csv")
TEXTDIR = Path("data/text")
EDGES = Path("data/predicate_edges.csv")
OUT = []


def say(s=""):
    print(s)
    OUT.append(s)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest():
    if not MANIFEST.is_file():
        sys.exit(f"{MANIFEST} not found — are you on the rule2-rerun branch?")
    with open(MANIFEST, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit(f"{MANIFEST} is empty")
    cols = rows[0].keys()
    kcol = next((c for c in cols if c.lower() in
                 ("file", "filename", "path", "knumber", "k_number", "name")), None)
    hcol = next((c for c in cols if "sha" in c.lower() or c.lower() == "hash"), None)
    if kcol is None or hcol is None:
        sys.exit(f"could not identify columns in {MANIFEST}: {list(cols)}")
    say(f"manifest columns: key={kcol!r} hash={hcol!r} | {len(rows):,} rows")
    return {Path(r[kcol]).stem: r[hcol].strip().lower() for r in rows}


def main():
    frozen = load_manifest()
    local = {p.stem: p for p in sorted(TEXTDIR.glob("*.txt"))}
    say(f"local data/text/: {len(local):,} files")
    say()

    missing = sorted(set(frozen) - set(local))
    extra = sorted(set(local) - set(frozen))
    shared = sorted(set(frozen) & set(local))

    changed = []
    for k in shared:
        if sha256(local[k]) != frozen[k]:
            changed.append(k)

    say("=" * 70)
    say(f"CHANGED  {len(changed)}  (present in both, content differs)")
    for k in changed:
        p = local[k]
        say(f"  {k}  local {p.stat().st_size:>8,} bytes  "
            f"local sha {sha256(p)[:12]}…  frozen sha {frozen[k][:12]}…")
    say()
    say(f"EXTRA    {len(extra)}  (local only — analyst got 404 for these)")
    for k in extra:
        say(f"  {k}  {local[k].stat().st_size:>8,} bytes")
    say()
    say(f"MISSING  {len(missing)}  (in freeze, absent locally)")
    for k in missing:
        say(f"  {k}")
    say("=" * 70)

    affected = changed + extra
    if not affected:
        say("\ncorpus matches the freeze exactly — Stage 3 will run.")
    elif EDGES.is_file():
        with open(EDGES, newline="", encoding="utf-8-sig") as fh:
            erows = list(csv.DictReader(fh))
        dcol = next((c for c in erows[0] if "device" in c.lower()), None)
        say(f"\nEDGE CONTRIBUTION OF THE {len(affected)} AFFECTED DOCUMENTS")
        say(f"(from {EDGES}, {len(erows):,} edges, device column {dcol!r})")
        tot = 0
        for k in affected:
            n = sum(1 for r in erows if r[dcol] == k)
            tot += n
            tag = "changed" if k in changed else "extra  "
            say(f"  {tag}  {k}  {n:>3} outgoing edges")
        say(f"  total across affected documents: {tot}")
        say()
        say("The +11 edge difference between the two graphs (30,487 vs 30,476)")
        say("must come out of this set. Edges from EXTRA documents are present")
        say("only in the verifier's graph; edges from CHANGED documents may")
        say("differ in either direction.")

    say("\nTO MAKE THE CORPUS MATCH THE FREEZE:")
    say(f"  1. ask the analyst for his copies of the {len(changed)} CHANGED files")
    say(f"  2. move the {len(extra)} EXTRA files out of data/text/ (do not delete —")
    say("     they are evidence for the retrieval-instability finding)")
    say("  3. re-run: python freeze_text.py --check   (expect PASS)")

    Path("text_corpus_diffs.txt").write_text("\n".join(OUT) + "\n")
    print("\n[written] text_corpus_diffs.txt")


if __name__ == "__main__":
    main()
