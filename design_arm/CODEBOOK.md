# Recall-cause codebook (design arm)

**Unit:** one FDA recall event (review_id). Code only from the columns in your sheet: firm, product description, reason for recall, affected lots or models (code_info), and firm action. FDA's own root-cause field is deliberately removed. Do not look events up in FDA databases while coding.

Code the **root failure mode** (why units were defective), not the consequence or the corrective action.

## category (enter exactly one)
- **design**: the defect arises from the device as designed or specified: geometry, dimensions, mechanical strength, specified materials, design of a component, or device software. Every unit built to specification would carry the problem.
- **manufacturing_process**: units deviate from their specification because of how they were made: process control, machining or finishing errors, nonconforming or contaminated material, supplier problems, wrong component assembled, employee error.
- **labeling**: labels, IFU, surgical technique guides, expiration dates, mislabeled size or side, unsupported claims, where the device itself conforms to its design.
- **packaging_sterility**: sterile barrier or package integrity, sterilization process or validation, seal failures.
- **other_unclear**: not enough information to decide; marketed without clearance; use error with no design or manufacturing defect; anything else.

## Decision rules
1. Wrong part in the box because of an assembly or kitting mix-up: manufacturing_process. Correct part with the wrong label: labeling.
2. Package or sterility failure, even if caused by a packaging design choice: packaging_sterility (the device design is not implicated).
3. A labeling or IFU change issued because the device performs worse than intended under normal use: design.
4. A component that fails because its specification is inadequate: design. Because a supplier did not meet the specification: manufacturing_process.
5. Defects in device software: design. Defects in manufacturing software or test equipment: manufacturing_process.
6. If the text supports two categories about equally, enter other_unclear and explain in notes.

## scope (enter exactly one)
- **system_wide**: all models, sizes or lots of the product described
- **subset_models_lots**: specific lots, serial numbers, sizes or models only
- **unclear**
