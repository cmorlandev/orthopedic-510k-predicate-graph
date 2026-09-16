#!/usr/bin/env python3
"""
Pre-flight and independence checks for the 510(k) predicate-graph verification.

Run from the repository root, AFTER unzipping snapshot_for_verifier.zip and
installing requirements.txt, but BEFORE running notebook 01.

Writes preflight_report.txt -- paste it into your verification pull request.

It answers four questions the manual does not ask you to check:
  1. Exactly which bytes am I reproducing from?  (hashes of the frozen snapshot)
  2. What does the snapshot say about its own provenance?
  3. Do notebooks 01-08 read the reference answers, or hardcode headline
     numbers?  If they do, a PASS would be circular rather than a rebuild.
  4. What library versions did I actually use?  (networkx in particular)
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(".").resolve()
OUT = []


def say(line=""):
    print(line)
    OUT.append(line)


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- 1. snapshot
def check_snapshot():
    say("=" * 72)
    say("1. FROZEN SNAPSHOT INTEGRITY")
    say("=" * 72)

    zips = sorted(ROOT.glob("snapshot_for_verifier*.zip"))
    for z in zips:
        say(f"zip   {z.name}")
        say(f"      sha256 {sha256(z)}")
        say(f"      bytes  {z.stat().st_size}")
        try:
            with zipfile.ZipFile(z) as zf:
                for info in sorted(zf.infolist(), key=lambda i: i.filename):
                    if info.is_dir():
                        continue
                    say(f"      member {info.filename}  crc32={info.CRC:08x}  "
                        f"{info.file_size} bytes")
        except zipfile.BadZipFile:
            say("      !! not a readable zip")
    if not zips:
        say("zip   (not found in repo root -- fine if you unzipped elsewhere "
            "and moved snapshot/ in, but then you cannot hash the original)")

    snap = ROOT / "snapshot"
    if not snap.is_dir():
        say("")
        say("!! FAIL  ./snapshot/ does not exist. Notebook 01 will not find "
            "the frozen data. Unzip the snapshot in the repo root.")
        return

    say("")
    say("unpacked ./snapshot/ :")
    members = sorted(p for p in snap.rglob("*") if p.is_file())
    for p in members:
        say(f"      {p.relative_to(ROOT)}  {p.stat().st_size} bytes")
        say(f"          sha256 {sha256(p)}")

    expected_gz = [p for p in members if p.name.endswith(".json.gz")]
    say("")
    say(f"      .json.gz count = {len(expected_gz)} (manual says 3) -> "
        f"{'OK' if len(expected_gz) == 3 else 'MISMATCH, ask the analyst'}")

    meta = snap / "SNAPSHOT.json"
    if meta.is_file():
        say("")
        say("      SNAPSHOT.json (provenance the analyst recorded):")
        try:
            obj = json.loads(meta.read_text())
            for line in json.dumps(obj, indent=2, sort_keys=True).splitlines():
                say(f"          {line}")
        except json.JSONDecodeError as exc:
            say(f"          !! unparseable: {exc}")
    else:
        say("      !! SNAPSHOT.json missing -- the snapshot carries no "
            "self-declared provenance. Ask the analyst.")


# ------------------------------------------------- 2. independence of rebuild
REF_TOKENS = [
    "expected_values_REFERENCE",
    "REFERENCE.json",
    "compare_to_reference",
]

def check_independence():
    say("")
    say("=" * 72)
    say("2. IS THE REBUILD INDEPENDENT OF THE REFERENCE ANSWERS?")
    say("=" * 72)
    say("A rebuild that reads expected_values_REFERENCE.json, or hardcodes a")
    say("headline number, cannot fail. Checking notebooks 01-08 for that.")
    say("")

    nbs = sorted(p for p in ROOT.glob("*.ipynb")
                 if re.match(r"0[1-8]", p.name))
    if not nbs:
        say("!! no 01-08 notebooks found in repo root -- are you in the "
            "right folder?")
        return

    flagged = 0
    for nb in nbs:
        src = extract_source(nb)
        hits = []
        for tok in REF_TOKENS:
            for m in re.finditer(re.escape(tok), src):
                line = src[:m.start()].count("\n") + 1
                hits.append(f"{tok} (src line ~{line})")
        if hits:
            flagged += 1
            say(f"  FLAG  {nb.name}")
            for h in hits:
                say(f"          {h}")
        else:
            say(f"  clean {nb.name}")

    say("")
    if flagged:
        say(f"-> {flagged} notebook(s) reference the analyst's answer file. "
            "Read those cells before you sign off: if the rebuild consumes "
            "the reference, a PASS is circular. Raise it with the analyst.")
    else:
        say("-> No notebook in 01-08 touches the reference file. The rebuild "
            "is independent of the target numbers on this check.")

    # seeds: determinism of the notebook 03 validation sample
    say("")
    say("Random seeds (notebook 03 draws a validation sample; without a "
        "fixed seed your sample, and any number derived from it, will not "
        "match):")
    seed_pat = re.compile(
        r"(random_state\s*=\s*\w+|np\.random\.seed\(\s*\w+\s*\)"
        r"|random\.seed\(\s*\w+\s*\)|default_rng\(\s*\w+\s*\)"
        r"|\bseed\s*=\s*\w+)")
    found_any = False
    for nb in nbs:
        src = extract_source(nb)
        seeds = sorted(set(seed_pat.findall(src)))
        if seeds:
            found_any = True
            say(f"  {nb.name}: " + ", ".join(seeds))
    if not found_any:
        say("  none found -> if any stage samples, ask the analyst how the "
            "sample is made reproducible.")


def extract_source(nb_path):
    try:
        nb = json.loads(nb_path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ""
    parts = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            parts.append("".join(cell.get("source", [])))
    return "\n".join(parts)


# ------------------------------------------------------------ 3. environment
def check_env():
    say("")
    say("=" * 72)
    say("3. ENVIRONMENT ACTUALLY IN USE")
    say("=" * 72)
    say(f"python     {sys.version.split()[0]}  ({sys.executable})")
    if not sys.version.startswith("3.11"):
        say("  !! manual pins Python 3.11.x -- a different minor version is "
            "a real source of spurious mismatches")

    for mod in ("networkx", "pandas", "numpy", "scipy", "requests"):
        try:
            m = __import__(mod)
            say(f"{mod:<10} {getattr(m, '__version__', 'unknown')}")
        except ImportError:
            say(f"{mod:<10} NOT INSTALLED")

    req = ROOT / "requirements.txt"
    if req.is_file():
        say("")
        say("requirements.txt pins:")
        for line in req.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                say(f"  {line}")

    say("")
    key = os.environ.get("OPENFDA_KEY")
    if key:
        say(f"OPENFDA_KEY set: yes (length {len(key)})")
    else:
        say("OPENFDA_KEY set: NO -- export it before notebooks 02 and 07")
    say("  (value deliberately not printed)")

    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        if rev.returncode == 0:
            say("")
            say(f"git commit {rev.stdout.strip()}")
            st = subprocess.run(["git", "status", "--porcelain"],
                                capture_output=True, text=True, timeout=10)
            dirty = [l for l in st.stdout.splitlines() if l.strip()]
            say(f"git worktree: {'CLEAN' if not dirty else 'MODIFIED'}")
            for l in dirty[:20]:
                say(f"  {l}")
            if dirty:
                say("  -> record why you changed tracked files, or reset "
                    "them; a modified worktree weakens the reproduction "
                    "claim")
    except (OSError, subprocess.SubprocessError):
        pass


# --------------------------------------------------------- 4. plan documents
def check_docs():
    say("")
    say("=" * 72)
    say("4. GOVERNING DOCUMENTS PRESENT?")
    say("=" * 72)
    say("You are signing off that the study matches its locked plan, not")
    say("only that it re-runs. These must exist and you must read them.")
    say("")
    for name in ("PREREGISTRATION.docx", "DEVIATIONS.md", "RUN_LOG.md",
                 "expected_values_REFERENCE.json", "compare_to_reference.py",
                 "FOR_THE_VERIFIER.md", "README.md",
                 "PROJECT_RUN_MANUAL.docx", "requirements.txt"):
        p = ROOT / name
        say(f"  {'OK  ' if p.is_file() else 'MISS'}  {name}")

    ref = ROOT / "expected_values_REFERENCE.json"
    if ref.is_file():
        say("")
        say(f"expected_values_REFERENCE.json sha256 {sha256(ref)}")
        try:
            obj = json.loads(ref.read_text())
            if isinstance(obj, dict):
                say(f"  {len(obj)} top-level fields you must reproduce:")
                for k in sorted(obj)[:60]:
                    say(f"    {k}")
        except json.JSONDecodeError:
            say("  !! unparseable")


def main():
    say("PRE-FLIGHT VERIFIER REPORT")
    say(f"repo root: {ROOT}")
    say("")
    check_snapshot()
    check_independence()
    check_env()
    check_docs()
    say("")
    say("=" * 72)
    say("Resolve every '!!' and 'FLAG' with the analyst before running 01-08.")
    say("=" * 72)
    Path("preflight_report.txt").write_text("\n".join(OUT) + "\n")
    print("\n[written] preflight_report.txt")


if __name__ == "__main__":
    main()
