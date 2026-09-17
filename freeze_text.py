#!/usr/bin/env python3
"""
freeze_text.py — freeze (or verify) the extracted-text corpus that Stage 3 reads.

Why: summary PDFs are fetched live from accessdata.fda.gov in Stage 2, and FDA does not
serve an identical set on every run (see DEVIATIONS.md D5). Stages 3-8 therefore read a
FROZEN copy of the extracted text in data/text/, and this script records what that copy is.

  python freeze_text.py            # write TEXT_SNAPSHOT.json + TEXT_SNAPSHOT_files.csv
  python freeze_text.py --check    # verify data/text/ still matches the frozen record

Both output files live at the repo root so they are committed to git (data/ and snapshot/
are git-ignored and archived on OSF). data/text/ itself is archived on OSF alongside the PDFs.
"""
import csv, hashlib, json, os, sys, datetime

MANIFEST = "data/download_manifest.csv"
TEXT_DIR = "data/text"
OUT_JSON = "TEXT_SNAPSHOT.json"
OUT_CSV = "TEXT_SNAPSHOT_files.csv"


def sha256_file(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(buf)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def retrieved_knumbers():
    with open(MANIFEST, newline="") as f:
        rows = list(csv.DictReader(f))
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    ks = sorted(r["k_number"] for r in rows if r["status"] == "200")
    return ks, counts


def frozen_knumbers():
    """The frozen document list: every K-number recorded in TEXT_SNAPSHOT_files.csv (committed to git).
    Stages 3-8 build their document set from THIS, not from data/download_manifest.csv, so a verifier
    whose own Stage 2 retrieved a slightly different set of PDFs still analyses exactly the frozen corpus."""
    with open(OUT_CSV, newline="") as f:
        return sorted(r["k_number"] for r in csv.DictReader(f))


def hash_corpus(ks):
    """Per-file hashes plus one aggregate hash over (k_number, sha256) in sorted order."""
    per_file = []
    agg = hashlib.sha256()
    missing = []
    for k in ks:
        p = os.path.join(TEXT_DIR, f"{k}.txt")
        if not os.path.exists(p):
            missing.append(k)
            continue
        h = sha256_file(p)
        per_file.append((k, h, os.path.getsize(p)))
        agg.update(f"{k}\t{h}\n".encode())
    return per_file, agg.hexdigest(), missing


def freeze():
    ks, counts = retrieved_knumbers()
    per_file, corpus_hash, missing = hash_corpus(ks)
    if missing:
        sys.exit(f"ERROR: {len(missing)} retrieved documents have no text file in {TEXT_DIR} "
                 f"(first: {missing[:5]}). Run Stage 3's extraction cell once, then freeze.")
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k_number", "sha256", "bytes"])
        w.writerows(per_file)
    record = {
        "frozen_on": datetime.date.today().isoformat(),
        "text_dir": TEXT_DIR,
        "n_files": len(per_file),
        "corpus_sha256": corpus_hash,
        "manifest_sha256": sha256_file(MANIFEST),
        "manifest_status_counts": counts,
        "n_empty_text_files": sum(1 for _, _, b in per_file if b == 0),
        "extractor": "pymupdf (fitz) page.get_text(), pages joined with '\\n' — see 03_extract_edges",
        "note": "Stages 3-8 read ONLY these files. Re-running Stage 2 does not change them.",
    }
    json.dump(record, open(OUT_JSON, "w"), indent=2)
    print(f"FROZEN  {record['n_files']} text files | corpus sha256 {corpus_hash}")
    print(f"        manifest: {counts} | empty text files: {record['n_empty_text_files']}")
    print(f"        wrote {OUT_JSON} and {OUT_CSV} — commit both.")


def check():
    if not os.path.exists(OUT_JSON):
        sys.exit(f"ERROR: {OUT_JSON} not found — nothing to check against.")
    rec = json.load(open(OUT_JSON))
    ks = frozen_knumbers()                      # the frozen list, NOT the local manifest
    per_file, corpus_hash, missing = hash_corpus(ks)
    frozen = {r["k_number"]: r["sha256"] for r in csv.DictReader(open(OUT_CSV, newline=""))}
    changed = [k for k, h, _ in per_file if frozen.get(k) != h]
    ok = (corpus_hash == rec["corpus_sha256"]) and not missing and not changed
    local_extra = [f for f in os.listdir(TEXT_DIR) if f.endswith(".txt") and f[:-4] not in frozen] if os.path.isdir(TEXT_DIR) else []
    print(f"frozen {rec['frozen_on']}: {rec['n_files']} files | found locally: {len(per_file)} of them")
    print(f"  missing {len(missing)} | changed {len(changed)} | extra local text files not in the freeze (ignored): {len(local_extra)}")
    print(f"  corpus sha256 frozen {rec['corpus_sha256'][:16]}… now {corpus_hash[:16]}…")
    print("RESULT: PASS — data/text/ matches the frozen record." if ok else
          "RESULT: FAIL — data/text/ differs from the frozen record. Restore it from OSF.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    check() if "--check" in sys.argv else freeze()
