"""
test_edge_rules.py — unit tests for the two edge rules.  Run:  python -m pytest test_edge_rules.py -q
(or simply: python test_edge_rules.py)

The two fixture documents are the ones identified in the independent verification
(2026-09) as carrying every false-positive edge in the validation sample:
  K190123 — MicroPort CoCr Femoral Heads: 1 predicate, 5 reference devices, two
            "Component and Accessory Compatibility" tables with a literal "510(k)" column
  K050441 — Biomet Taper 2 Porous Femoral Stem: 2 predicates, then an Indications-for-Use
            paragraph enumerating compatible components with their K-numbers
"""
import os
import edge_rules as er

TXT = "data/text"


def _load(k):
    p = os.path.join(TXT, f"{k}.txt")
    if not os.path.exists(p):
        return None
    return open(p, encoding="utf-8").read()


def _valid(*texts):
    v = set()
    for t in texts:
        v |= set(er.KPAT.findall(t))
    return v


def test_k190123_keeps_only_the_predicate():
    t = _load("K190123")
    if t is None:
        return print("skip K190123 (no text file)")
    r = er.extract(t, "K190123", _valid(t))
    assert len(r["rule1"]) == 42, len(r["rule1"])
    assert [p for p, _ in r["rule2"]] == ["K170444"], r["rule2"]
    kinds = {p: z for p, z, _, _ in r["excluded"]}
    assert kinds["K932222"] == "reference" and kinds["K173898"] == "reference"
    assert kinds["K061547"] == "compat" and kinds["K150302"] == "compat"   # first and last table rows
    assert len(r["excluded"]) == 41


def test_k050441_keeps_both_predicates():
    t = _load("K050441")
    if t is None:
        return print("skip K050441 (no text file)")
    r = er.extract(t, "K050441", _valid(t))
    assert len(r["rule1"]) == 8
    assert [p for p, _ in r["rule2"]] == ["K921301", "K943230"]
    assert all(z == "compat" for _, z, _, _ in r["excluded"])


def test_synthetic_predicate_named_twice_survives():
    t = ("510(k) Summary\nIV.\nPredicate Device:\nFoo System (K111111)\n"
         "X.\nComponent and Accessory Compatibility:\nTable #1: Compatible parts\n510(k)\n"
         "K111111\nFoo Shell\nK222222\nBar Liner\nXI.\nConclusion:\nsubstantially equivalent.\n")
    r = er.extract(t, "K999999", {"K111111", "K222222"})
    assert [p for p, _ in r["rule2"]] == ["K111111"]
    assert [p for p, _, _, _ in r["excluded"]] == ["K222222"]


def test_synthetic_reference_heading_inline():
    t = "Predicate Device: K111111\nReference Device: K222222\nDevice Description:\nblah\n"
    r = er.extract(t, "K999999", {"K111111", "K222222"})
    assert [p for p, _ in r["rule2"]] == ["K111111"]


def test_no_cue_no_edges():
    r = er.extract("nothing here K111111", "K999999", {"K111111"})
    assert r["rule1"] == [] and r["rule2"] == []


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok ", name)
