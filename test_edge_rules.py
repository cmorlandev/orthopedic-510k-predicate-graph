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


# ---- Rule 2 v2 (DEVIATIONS.md D10): the three audit documents from the 2026-10 largest-component check

def test_k180373_font_encoded_reference_heading():
    t = _load("K180373")
    if t is None:
        return print("skip K180373 (no text file)")
    r = er.extract(t, "K180373", _valid(t))
    assert sorted(p for p, _ in r["rule2"]) == ["K143158", "K150481", "K152011"], r["rule2"]
    assert [(p, z) for p, z, _, _ in r["excluded"]] == [("K081171", "reference")]
    r1 = er.extract(t, "K180373", _valid(t), rule2_version="v1")      # v1 reproduces the old leak
    assert "K081171" in [p for p, _ in r1["rule2"]]


def test_k161569_reference_heading_not_at_line_start():
    t = _load("K161569")
    if t is None:
        return print("skip K161569 (no text file)")
    r = er.extract(t, "K161569", _valid(t))
    assert sorted(p for p, _ in r["rule2"]) == ["K081171", "K943549"], r["rule2"]
    assert all(z == "reference" for _, z, _, _ in r["excluded"])
    assert len(r["excluded"]) == 6


def test_k171595_reference_device_remention_stays_excluded():
    t = _load("K171595")
    if t is None:
        return print("skip K171595 (no text file)")
    r = er.extract(t, "K171595", _valid(t))
    assert sorted(p for p, _ in r["rule2"]) == ["K000080", "K021932", "K024060", "K112028",
                                                 "K130092", "K962011"], r["rule2"]
    assert sorted(p for p, _, _, _ in r["excluded"]) == ["K082792", "K091967"]


# ---- regressions found when v2 first ran on the full corpus (2026-10-21)

def test_k172235_parenthetical_label_does_not_swallow_primary_family():
    t = _load("K172235")
    if t is None:
        return print("skip K172235 (no text file)")
    r = er.extract(t, "K172235", _valid(t))
    kept = {p for p, _ in r["rule2"]}
    assert {"K150062", "K090299", "K042344"} <= kept, sorted(kept)   # primary predicate and its family
    assert r["excluded"] == []


def test_k191972_primary_predicate_recurring_in_reference_section_is_kept():
    t = _load("K191972")
    if t is None:
        return print("skip K191972 (no text file)")
    r = er.extract(t, "K191972", _valid(t))
    assert "K170705" in [p for p, _ in r["rule2"]]
    assert [(p, z) for p, z, _, _ in r["excluded"]] == [("K180972", "reference")]


def test_k182119_reference_predicate_label_is_excluded():
    t = _load("K182119")
    if t is None:
        return print("skip K182119 (no text file)")
    r = er.extract(t, "K182119", _valid(t))
    assert sorted(p for p, _ in r["rule2"]) == ["K090390", "K091974", "K113174", "K132328"]
    assert [(p, z) for p, z, _, _ in r["excluded"]] == [("K171689", "reference")]


def test_k170119_nonbreaking_space_heading_is_not_decoded():
    t = _load("K170119")
    if t is None:
        return print("skip K170119 (no text file)")
    v = _valid(t)
    v1 = {p for p, _ in er.extract(t, "K170119", v, rule2_version="v1")["rule2"]}
    v2 = {p for p, _ in er.extract(t, "K170119", v)["rule2"]}
    assert v2 <= v1, sorted(v2 - v1)                       # v2 never adds edges here
    assert not ({"K153782", "K160597", "K160958", "K161230"} & v2)   # listed under REFERENCE\xa0DEVICES
    assert er._decode_line("REFERENCE\xa0DEVICES") is None


def test_synthetic_parenthetical_label_opens_no_zone():
    t = ("Predicate Devices:\nFoo (primary predicate)\nK111111\nBar (reference predicate)\nK222222\n"
         "Baz\nK333333\nDevice Description:\nblah\n")
    r = er.extract(t, "K999999", {"K111111", "K222222", "K333333"})
    assert sorted(p for p, _ in r["rule2"]) == ["K111111", "K222222", "K333333"]


def test_synthetic_predicate_and_reference_heading_is_not_a_zone():
    t = "Predicate and Reference Devices:\nK111111\nK222222\nDevice Description:\nblah predicate\n"
    r = er.extract(t, "K999999", {"K111111", "K222222"})
    assert sorted(p for p, _ in r["rule2"]) == ["K111111", "K222222"]


def test_synthetic_reference_device_also_named_predicate_is_kept():
    t = ("Reference Device: K222222\nDevice Description:\nblah\n"
         "Primary Predicate: Foo (K222222)\nConclusion:\nsubstantially equivalent\n")
    r = er.extract(t, "K999999", {"K222222"})
    assert [p for p, _ in r["rule2"]] == ["K222222"]


def test_decoder_ignores_k_numbers_and_ordinary_words():
    assert er._decode_line("K081171") is None
    assert er._decode_line("Description") is None
    assert er._decode_line("5HIHUHQFH3UHGLFDWHV") == "ReferencePredicates"
    assert er._decode_line("5HIHUHQFH\x033UHGLFDWHV\x03") == "Reference Predicates"   # encoded spaces


def test_no_cue_no_edges():
    r = er.extract("nothing here K111111", "K999999", {"K111111"})
    assert r["rule1"] == [] and r["rule2"] == []


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok ", name)
