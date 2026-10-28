"""
firm_families.py — corporate-family map for the same-firm analysis (06c; post hoc, D8).

Each entity is matched by a regular expression on the lower-cased firm name (510(k) applicant or
recalling firm). An entity belongs to one or more GROUPS, each from a date (None = from the start).
Two firms are treated as the same corporate family at date t if they share a group that BOTH had
joined by t ("family at the time of submission", author decision 2026-10-27). Firms that match no
entity fall back to the crude first-word name match.

Acquisition dates are completion dates, verified 2026-10-27 against the sources listed.
"""
import re
import pandas as pd

ENTITIES = [  # (regex, [(group, since)]), checked in order; first match wins
    (r"depuy|codman|johnson ?& ?johnson",     [("J&J", None)]),
    (r"synthes",                              [("Synthes", None), ("J&J", "2012-06-14")]),   # J&J press release 2012-06-14
    (r"stryker|osteonics",                    [("Stryker", None)]),
    (r"howmedica",                            [("Howmedica", None), ("Stryker", "1998-12-04")]),  # Stryker 8-K
    (r"memometal",                            [("Memometal", None), ("Stryker", "2011-07-06")]),  # Stryker release
    (r"small bone innovations",               [("SBI", None), ("Stryker", "2014-08-01")]),        # Stryker release (N. America)
    (r"\bk2m\b",                              [("K2M", None), ("Stryker", "2018-11-09")]),        # Stryker release
    (r"orthohelix",                           [("OrthoHelix", None), ("Tornier", "2012-10-04"),   # Tornier 10-Q
                                               ("Wright", "2015-10-01"), ("Stryker", "2020-11-11")]),
    (r"tornier",                              [("Tornier", None), ("Wright", "2015-10-01"),        # Wright-Tornier merger
                                               ("Stryker", "2020-11-11")]),                       # Stryker release
    (r"wright ?medical|wrightmedical",        [("Wright", None), ("Stryker", "2020-11-11")]),
    (r"zimmer",                               [("Zimmer", None)]),
    (r"spinal concepts|abbott spine",         [("Abbott Spine", None), ("Zimmer", "2008-10-16")]),  # Zimmer release
    (r"lanx",                                 [("Lanx", None), ("Biomet", "2013-11-01"),             # Biomet 8-K
                                               ("Zimmer", "2015-06-24")]),
    (r"biomet|\bebi\b",                       [("Biomet", None), ("Zimmer", "2015-06-24")]),          # Zimmer Biomet release
    (r"paragon ?28",                          [("Paragon 28", None), ("Zimmer", "2025-04-21")]),      # Zimmer Biomet release
    (r"medtronic|warsaw orthopedic",          [("Medtronic", None)]),
    (r"sofamor|danek",                        [("Sofamor Danek", None), ("Medtronic", "1999-01-27")]),
    (r"kyphon",                               [("Kyphon", None), ("Medtronic", "2007-11-02")]),
    (r"smith ?& ?nephew",                     [("Smith & Nephew", None)]),
    (r"arthrocare",                           [("ArthroCare", None), ("Smith & Nephew", "2014-05-29")]),
    (r"\bdjo\b",                              [("DJO", None)]),
    (r"encore medical|reable",                [("Encore", None), ("DJO", "2007-11-20")]),              # DJO-ReAble merger
    (r"lima ?corporate",                      [("Lima", None), ("DJO", "2024-01-03")]),                # Enovis 8-K
    (r"orthofix",                             [("Orthofix", None)]),
    (r"blackstone medical",                   [("Blackstone", None), ("Orthofix", "2006-09-22")]),     # Orthofix 8-K
    (r"seaspine",                             [("SeaSpine", None), ("Orthofix", "2023-01-05")]),       # SeaSpine 8-K
    (r"globus",                               [("Globus", None)]),
    (r"nuvasive",                             [("NuVasive", None), ("Globus", "2023-09-01")]),         # Globus release
    (r"\brti\b|regeneration technologies",    [("RTI", None)]),
    (r"pioneer surgical",                     [("Pioneer", None), ("RTI", "2013-07-16")]),             # RTI 8-K
    (r"conmed",                               [("CONMED", None)]),
    (r"in2bones",                             [("In2Bones", None), ("CONMED", "2022-06-13")]),         # CONMED 8-K
    (r"spinal elements",                      [("Spinal Elements", None)]),
    (r"amendia",                              [("Amendia", None), ("Spinal Elements", "2017-04-17")]),  # Amendia acquires Spinal Elements
    (r"aesculap|b\.? ?braun",                 [("B. Braun", None)]),
    (r"exactech", [("Exactech", None)]), (r"arthrex", [("Arthrex", None)]), (r"medacta", [("Medacta", None)]),
    (r"integra", [("Integra", None)]), (r"alphatec", [("Alphatec", None)]), (r"conformis", [("Conformis", None)]),
    (r"united orthopedic", [("United Orthopedic", None)]), (r"u ?& ?i\b", [("U&I", None)]),
    (r"waldemar link", [("Waldemar Link", None)]), (r"corin\b", [("Corin", None)]), (r"microport", [("MicroPort", None)]),
    (r"trilliant", [("Trilliant", None)]), (r"acu ?med", [("Acumed", None)]), (r"genesys", [("Genesys Spine", None)]),
    (r"corentec", [("Corentec", None)]), (r"materialise", [("Materialise", None)]),
    (r"orthopediatrics", [("OrthoPediatrics", None)]), (r"ortho development", [("Ortho Development", None)]),
    (r"signature orthopaedics", [("Signature Orthopaedics", None)]),
]
_COMPILED = [(re.compile(rx), [(g, pd.Timestamp(s) if s else None) for g, s in m]) for rx, m in ENTITIES]

def memberships(name):
    n = (name or "").lower()
    for rx, m in _COMPILED:
        if rx.search(n):
            return m
    return None

def _crude(s):
    s = (s or "").lower()
    for t in [",", ".", " inc", " llc", " corporation", " corp", " ltd", " gmbh", " co", " usa", " us", " ag", " l.p", " lp", " sa"]:
        s = s.replace(t, " ")
    w = s.split()
    return w[0] if w else ""

def same_family(name_a, name_b, when):
    """True if the two firm names belong to one corporate family at date `when` (falls back to crude match)."""
    ma, mb = memberships(name_a), memberships(name_b)
    if ma and mb and pd.notna(when):
        ga = {g for g, s in ma if s is None or s <= when}
        gb = {g for g, s in mb if s is None or s <= when}
        if ga & gb:
            return True
    ca, cb = _crude(name_a), _crude(name_b)
    return bool(ca) and ca == cb
