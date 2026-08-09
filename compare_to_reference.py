#!/usr/bin/env python3
"""Verifier check: compare YOUR rebuilt data/expected_values.json to the analyst's
expected_values_REFERENCE.json. Every value is deterministic (computed from the frozen
snapshot), so all fields must match EXACTLY. Run this after you've run notebooks 01-08.

  python compare_to_reference.py
"""
import json, sys, os

ref_path = "expected_values_REFERENCE.json"
new_path = "data/expected_values.json"
if not os.path.exists(new_path):
    sys.exit(f"ERROR: {new_path} not found — run notebooks 01-06 first (they write it).")

ref = json.load(open(ref_path))
new = json.load(open(new_path))

print(f"{'field':28} {'analyst (reference)':>22} {'your rebuild':>22}  result")
print("-" * 82)
mismatches = 0
for k in ref:
    a, b = ref[k], new.get(k, "<missing>")
    ok = (a == b)
    if not ok:
        mismatches += 1
    print(f"{k:28} {str(a):>22} {str(b):>22}  {'PASS' if ok else 'FAIL <<<'}")

print("-" * 82)
if mismatches == 0:
    print("RESULT: PASS — all deterministic values reproduce exactly.")
    print("(MAUDE / Stage 7 numbers live in data/maude_comparison.json and are reported 'as of' your")
    print(" run date; they read the live FDA endpoint and are expected to be >= the analyst's.)")
else:
    print(f"RESULT: {mismatches} FIELD(S) DIFFER — investigate before signing off.")
    print("Common causes: you ran Stage 0 (used a fresh snapshot instead of the analyst's), a")
    print("different networkx/pandas version, or notebooks run out of order. See FOR_THE_VERIFIER.md.")
    sys.exit(1)
