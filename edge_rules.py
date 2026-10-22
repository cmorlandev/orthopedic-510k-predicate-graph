"""
edge_rules.py — the two deterministic predicate-edge rules for the
Orthopedic 510(k) Predicate-Graph Study.

RULE 1 (registered, preregistration §5): in any summary containing a predicate cue
(predicate / substantially equivalent / reference device), every OTHER in-corpus
K-number mentioned anywhere in the text becomes an edge predicate -> device.

RULE 2 (restricted, adopted after independent verification, DEVIATIONS.md D4; revised D10):
Rule 1, minus K-numbers whose every mention falls inside an EXCLUSION ZONE.
An exclusion zone is the span of text from a heading-like line that denotes
  (a) component / accessory compatibility, or
  (b) FDA reference devices,
to the next heading-like line that starts a different section.
A K-number mentioned at least once OUTSIDE every exclusion zone is kept
(e.g. a device named under "Predicate Device:" and again in a compatibility
table is still a predicate).

RULE 2 VERSIONS (DEVIATIONS.md D10). `extract(..., rule2_version=...)`:
  "v1" — the 2026-09 rule exactly as D4 adopted it (kept for reproduction).
  "v2" — the default. Three fixes found in the 2026-10 largest-component audit:
    1. Reference-device headings are found anywhere in a heading line that ends in
       ":" and names no predicate, e.g. "Legally Marketed Reference Devices Used to
       Support Substantial Equivalence:" (K161569). v1 matched only headings that
       START with "Reference Device".
    2. Font-encoded heading lines (PyMuPDF output where every character is shifted
       by a fixed code-point offset, e.g. K180373's "5HIHUHQFH3UHGLFDWHV" =
       "ReferencePredicates") are decoded before zone detection. Decoding is used
       only to recognise headings; K-number positions are never altered.
       Parenthetical table labels ("(Reference Predicate)") and lines carrying a
       K-number label one entry, not a section, so they never open a v2 zone.
    3. A K-number the document INTRODUCES in a REFERENCE zone (its first mention
       is there) stays excluded even when it is mentioned again elsewhere, unless
       that other mention sits on a line that explicitly names it a predicate.
       "Reference Predicate(s)" labels count as reference devices (author
       decision, 2026-10-21). v1 kept it on any outside mention, so a
       reference device re-mentioned in a materials or biocompatibility paragraph
       (K171595's K082792; K161569's K151264) leaked back in. Compatibility zones
       keep the v1 behaviour, because real predicates often recur in compatibility
       tables.

Both rules label each edge by cue proximity:
  NEAR_CUE     — a strong cue (predicate / reference device) within 300 characters
                 of the K-number's first non-excluded mention  (was: SECTION_HEADED)
  DISTANT_CUE  — otherwise                                     (was: PROXIMITY_ONLY)
Neither label involves section-structure detection; the names are descriptive only.

Everything here is pure functions over the extracted text so that the rule can be
unit-tested on individual documents (see test_edge_rules.py).
"""
import re

KPAT = re.compile(r"\bK\d{6}\b")
CUE = re.compile(r"(?i)predicate|substantial(?:ly)?\s+equival|reference\s+device")
CUE_STRONG = re.compile(r"(?i)predicate|reference\s+device")
WINDOW = 300

# ---------------------------------------------------------------- headings --
HEADING_MAX = 120                      # a heading-like line is at most this long
NUMBERED = re.compile(r"^\W*(?:[IVXLC]{1,6}|\d{1,2}(?:\.\d+)*|[A-Z])[.)]\s*")   # "X.", "5.1", "B)"
BARE_NUMERAL = re.compile(r"^\W*(?:[IVXLC]{1,6}|\d{1,2}(?:\.\d+)*|[A-Z])[.)]?\s*$")  # "XI." alone on a line

# zone (a): component / accessory compatibility
COMPAT = re.compile(r"(?i)\b(?:compatib\w*|accessor(?:y|ies)|mating\s+components?|"
                    r"components?\s+(?:for\s+use|that\s+can\s+be\s+used|to\s+be\s+used)\s+with)\b")
# zone (b): FDA reference devices — heading only, e.g. "V. Reference Device:" / "Reference Devices"
#   matches "Reference Device:", "V. Reference Devices", "Reference Device(s): K123456 …"
REFDEV = re.compile(r"(?i)^\W*(?:[IVXLC]{1,6}[.)]|\d{1,2}(?:\.\d+)*[.)]?|[A-Z][.)])?\s*"
                    r"(?:additional\s+)?reference\s+devices?(?:\s*\(s\))?\s*(?::|$)")
# v2: reference-device heading anywhere in the line ("Legally Marketed Reference Devices …:"),
#     also "Reference Predicate(s)" as some sponsors label them
REFDEV_ANY = re.compile(r"(?i)reference\s*(?:devices?|predicates?)(?:\s*\(s\))?")
REFDEV_WHOLE = re.compile(r"(?i)\W*reference\s*(?:devices?|predicates?)(?:\s*\(s\))?\W*")
PRED_WORD = re.compile(r"(?i)predicate")
DECODE_CUES = re.compile(r"(?i)reference|predicate|compatib|accessor")
# headings that always END a zone (a new section has begun)
SECTION_WORDS = re.compile(r"(?i)\b(?:predicate|substantial(?:ly)?\s+equival|conclusion|"
                           r"device\s+description|indications?\s+for\s+use|intended\s+use|"
                           r"performance|testing|technological\s+characteristics|summary|"
                           r"discussion|comparison|classification|sterili[sz]ation|biocompatib\w*)\b")


def _heading_like(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > HEADING_MAX:
        return False
    if s.endswith(":"):
        return True
    if re.match(r"(?i)^\W*table\b", s):
        return True
    if NUMBERED.match(s):
        return True
    return len(s) <= 60 and not s.endswith(".")


def _decode_line(s: str):
    """
    v2. Some PDFs extract with a font whose glyphs are shifted by a fixed code-point
    offset ("5HIHUHQFH3UHGLFDWHV" -> "ReferencePredicates", offset 29). For a single
    spaceless token that is not a K-number, try each offset; return the decoded text
    only if it is all letters AND contains a zone/section cue word. Otherwise None.
    """
    s = s.strip()
    # only spaceless tokens (any whitespace, incl. non-breaking spaces, means ordinary text),
    # never K-numbers, and never a line that already reads as a cue word
    if re.search(r"\s", s) or len(s) < 6 or KPAT.search(s) or DECODE_CUES.search(s):
        return None
    for shift in range(1, 65):
        try:
            d = "".join(chr(ord(c) + shift) for c in s)
        except ValueError:
            return None
        letters = d.replace(" ", "")                                   # encoded spaces decode to " "
        if letters.isascii() and letters.isalpha() and DECODE_CUES.search(d):
            return d.strip()
    return None


def _zone_start(line: str, version: str = "v1"):
    """Return 'compat' / 'reference' if this line opens an exclusion zone, else None."""
    s = line.strip()
    if version == "v2":
        s = _decode_line(s) or s
    if not _heading_like(s):
        return None
    if REFDEV.match(s):
        return "reference"
    if version == "v2" and "(" not in s and ")" not in s and not KPAT.search(s):
        # parenthetical row/column labels ("(Reference Predicate)", "… VLP, reference predicate)")
        # label a single table entry, not a section, so they never open a zone
        m = REFDEV_ANY.search(s)
        if m:
            rest = s[:m.start()] + s[m.end():]
            whole = REFDEV_WHOLE.fullmatch(s)
            if not PRED_WORD.search(rest) and (s.endswith(":") or whole):
                return "reference"
    if COMPAT.search(s) and not SECTION_WORDS.search(re.sub(COMPAT, "", s)):
        return "compat"
    return None


SECTION_TITLE = re.compile(r"(?i)^\W*(?:[IVXLC]{1,6}[.)]|\d{1,2}(?:\.\d+)*[.)]?|[A-Z][.)])?\s*"
                           r"(?:[A-Za-z/&\-\s]{0,40})?"
                           r"(?:predicate|substantial(?:ly)?\s+equival\w*|conclusions?|"
                           r"device\s+description|indications?\s+for\s+use|intended\s+use|"
                           r"performance(?:\s+data)?|(?:non-?clinical\s+)?testing|"
                           r"technological\s+characteristics|discussion|comparison|"
                           r"classification|sterili[sz]ation|biocompatib\w*)"
                           r"[A-Za-z/&\-\s()]{0,40}:?\s*$")


def _zone_end(line: str, version: str = "v1") -> bool:
    """
    A line that begins a different section ends any open zone. Page headers/footers,
    table rows and running titles must NOT end a zone, so this is deliberately strict:
      - a bare numeral / roman numeral on its own line ("XI.")
      - a heading-like line ending in ":" (but not a table caption)
      - a whole-line section title ("Conclusion", "V. Predicate Devices")
    """
    s = line.strip()
    if version == "v2":
        s = _decode_line(s) or s
    if not _heading_like(s):
        return False
    if BARE_NUMERAL.match(s):
        return True
    if s.endswith(":") and not re.match(r"(?i)^\W*table\b", s):
        return True
    return bool(SECTION_TITLE.match(s))


def exclusion_zones(text: str, version: str = "v1"):
    """
    Yield (start_char, end_char, kind, heading) for every exclusion zone in `text`.
    Zones are located on the line structure produced by PyMuPDF get_text().
    """
    zones = []
    pos = 0
    open_zone = None          # (start_char, kind, heading)
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        kind = _zone_start(stripped, version)
        if kind is not None:
            if open_zone is not None:                       # back-to-back zones
                zones.append((open_zone[0], pos, open_zone[1], open_zone[2]))
            open_zone = (pos, kind, stripped)   # zone includes the heading line itself ("Reference Device: K123456")
        elif open_zone is not None and _zone_end(stripped, version):
            zones.append((open_zone[0], pos, open_zone[1], open_zone[2]))
            open_zone = None
        pos += len(line)
    if open_zone is not None:
        zones.append((open_zone[0], len(text), open_zone[1], open_zone[2]))
    return zones


def _in_zone(idx: int, zones):
    for a, b, kind, head in zones:
        if a <= idx < b:
            return kind, head
    return None


def _confidence(text: str, idx: int) -> str:
    window = text[max(0, idx - WINDOW): idx + WINDOW]
    return "NEAR_CUE" if CUE_STRONG.search(window) else "DISTANT_CUE"


def _line_at(text: str, idx: int) -> str:
    a = text.rfind("\n", 0, idx) + 1
    b = text.find("\n", idx)
    return text[a: len(text) if b == -1 else b]


def _named_predicate_on_line(text: str, idx: int) -> bool:
    """v2: the mention's own line calls it a predicate (and not a 'reference predicate')."""
    line = REFDEV_ANY.sub("", _line_at(text, idx))
    return bool(PRED_WORD.search(line))


def extract(text: str, device: str, valid: set, rule2_version: str = "v2"):
    """
    Apply both rules to one document. `rule2_version` = "v2" (default) or "v1" (see top).

    Returns dict with:
      has_cue        bool
      found          list of every K-number string in the text (with repeats)
      rule1          list of (predicate, confidence)                 — registered rule
      rule2          list of (predicate, confidence)                 — restricted rule
      excluded       list of (predicate, zone_kind, zone_heading, rule1_confidence)
      zones          list of (start, end, kind, heading)
    """
    has_cue = bool(CUE.search(text))
    mentions = [(m.group(0), m.start()) for m in KPAT.finditer(text)]
    found = [k for k, _ in mentions]
    out = {"has_cue": has_cue, "found": found, "rule1": [], "rule2": [], "excluded": [], "zones": []}
    if not has_cue:
        return out

    in_corpus = sorted({k for k in found if k in valid and k != device})
    zones = exclusion_zones(text, rule2_version)
    out["zones"] = zones

    for pred in in_corpus:
        positions = [i for k, i in mentions if k == pred]      # whole-word mentions only
        first = positions[0]
        # Rule 1 confidence uses text.find() exactly as the 2026-08-08 notebook did, so the
        # registered-rule tiers (sens_high_conf) reproduce bit-for-bit.
        conf1 = _confidence(text, text.find(pred))
        out["rule1"].append((pred, conf1))

        outside = [i for i in positions if _in_zone(i, zones) is None]
        if rule2_version == "v2" and outside:
            # the document INTRODUCES it as a reference device: its first mention is in a
            # reference zone. A device first listed elsewhere (e.g. under "Primary Predicate")
            # is never dropped just because it recurs inside a reference section.
            first_kind = (_in_zone(first, zones) or ("",))[0]
            in_ref = [first] if first_kind == "reference" else []
            if in_ref and not any(_named_predicate_on_line(text, i) for i in outside):
                kind, head = _in_zone(in_ref[0], zones)
                out["excluded"].append((pred, kind, head, conf1))
                continue
        if outside:
            out["rule2"].append((pred, _confidence(text, outside[0])))
        else:
            kind, head = _in_zone(first, zones)
            out["excluded"].append((pred, kind, head, conf1))
    return out
