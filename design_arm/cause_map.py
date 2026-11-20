"""FDA root cause -> study recall-cause category (design arm, post hoc).

Fixed 2026-10-15, before any manual coding. Manual coding (D2) overrides this
mapping only for events in the review set. Any root cause not listed here
falls to other_unclear and is reported by D1.
"""
DESIGN = "design"
MANUFACTURING = "manufacturing_process"
LABELING = "labeling"
PACKAGING = "packaging_sterility"
UNCLEAR = "other_unclear"
CATEGORIES = [DESIGN, MANUFACTURING, LABELING, PACKAGING, UNCLEAR]
SCOPES = ["system_wide", "subset_models_lots", "unclear"]

FDA_ROOT_CAUSE_MAP = {
    # design-related
    "Device Design": DESIGN,
    "Component design/selection": DESIGN,
    "Software design": DESIGN,
    "Software Design Change": DESIGN,
    # manufacturing or process
    "Process control": MANUFACTURING,
    "Process change control": MANUFACTURING,
    "Process design": MANUFACTURING,
    "Nonconforming Material/Component": MANUFACTURING,
    "Employee error": MANUFACTURING,
    "Mixed-up of materials/components": MANUFACTURING,
    "Vendor change control": MANUFACTURING,
    "Component change control": MANUFACTURING,
    "Equipment maintenance": MANUFACTURING,
    "Manufacturing material removal": MANUFACTURING,
    "Material/Component Contamination": MANUFACTURING,
    "Environmental control": MANUFACTURING,
    "Release of Material/Component prior to receiving test results": MANUFACTURING,
    "Finished device change control": MANUFACTURING,
    "Software design (manufacturing process)": MANUFACTURING,
    "Storage": MANUFACTURING,
    "Reprocessing Controls": MANUFACTURING,
    # labeling or instructions
    "Labeling design": LABELING,
    "Labeling mix-ups": LABELING,
    "Error in labeling": LABELING,
    "Labeling Change Control": LABELING,
    "Labeling False and Misleading": LABELING,
    "Incorrect or no expiration date": LABELING,
    # packaging or sterility
    "Packaging": PACKAGING,
    "Packaging process control": PACKAGING,
    "Packaging change control": PACKAGING,
    "Package design/selection": PACKAGING,
    # other or unclear -> always sent to manual coding
    "Other": UNCLEAR,
    "Under Investigation by firm": UNCLEAR,
    "Unknown/Undetermined by firm": UNCLEAR,
    "Pending": UNCLEAR,
    "No Marketing Application": UNCLEAR,
    "Use error": UNCLEAR,
    "Software change control": UNCLEAR,
}


def map_root_cause(rc):
    if not isinstance(rc, str) or not rc.strip():
        return UNCLEAR
    return FDA_ROOT_CAUSE_MAP.get(rc.strip(), UNCLEAR)
