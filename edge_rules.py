"""
edge_rules.py — the two deterministic predicate-edge rules for the
Orthopedic 510(k) Predicate-Graph Study.

RULE 1 (registered, preregistration §5): in any summary containing a predicate cue
(predicate / substantially equivalent / reference device), every OTHER in-corpus
K-number mentioned anywhere in the text becomes an edge predicate -> device.

RULE 2 (restricted, adopted after independent verification, DEVIATIONS.md D4):
Rule 1, minus K-numbers whose every mention falls inside an EXCLUSION ZONE.
An exclusion zone is the span of text from a heading-like line that denotes
  (a) component / accessory compatibility, or
  (b) FDA reference devices,
to the next heading-like line that starts a different section.
A K-number mentioned at least once OUTSIDE every exclusion zone is kept
(e.g. a device named under "Predicate Device:" and again in a compatibility
table is still a predicate).

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


def _zone_start(line: str):
    """Return 'compat' / 'reference' if this line opens an exclusion zone, else None."""
    s = line.strip()
    if not _heading_like(s):
        return None
    if REFDEV.match(s):
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


def _zone_end(line: str) -> bool:
    """
    A line that begins a different section ends any open zone. Page headers/footers,
    table rows and running titles must NOT end a zone, so this is deliberately strict:
      - a bare numeral / roman numeral on its own line ("XI.")
      - a heading-like line ending in ":" (but not a table caption)
      - a whole-line section title ("Conclusion", "V. Predicate Devices")
    """
    s = line.strip()
    if not _heading_like(s):
        return False
    if BARE_NUMERAL.match(s):
        return True
    if s.endswith(":") and not re.match(r"(?i)^\W*table\b", s):
        return True
    return bool(SECTION_TITLE.match(s))


def exclusion_zones(text: str):
    """
    Yield (start_char, end_char, kind, heading) for every exclusion zone in `text`.
    Zones are located on the line structure produced by PyMuPDF get_text().
    """
    zones = []
    pos = 0
    open_zone = None          # (start_char, kind, heading)
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        kind = _zone_start(stripped)
        if kind is not None:
            if open_zone is not None:                       # back-to-back zones
                zones.append((open_zone[0], pos, open_zone[1], open_zone[2]))
            open_zone = (pos, kind, stripped)   # zone includes the heading line itself ("Reference Device: K123456")
        elif open_zone is not None and _zone_end(stripped):
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


def extract(text: str, device: str, valid: set):
    """
    Apply both rules to one document.

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
    zones = exclusion_zones(text)
    out["zones"] = zones

    for pred in in_corpus:
        positions = [i for k, i in mentions if k == pred]      # whole-word mentions only
        first = positions[0]
        # Rule 1 confidence uses text.find() exactly as the 2026-08-08 notebook did, so the
        # registered-rule tiers (sens_high_conf) reproduce bit-for-bit.
        conf1 = _confidence(text, text.find(pred))
        out["rule1"].append((pred, conf1))

        outside = [i for i in positions if _in_zone(i, zones) is None]
        if outside:
            out["rule2"].append((pred, _confidence(text, outside[0])))
        else:
            kind, head = _in_zone(first, zones)
            out["excluded"].append((pred, kind, head, conf1))
    return out
