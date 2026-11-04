# Source coverage and precision review

The default is an editorial transformation that retains substantive meaning and precision. Rewriting, integrating related information, and removing repetitive expression are expected; completeness does not mean verbatim transcription or reproducing source page layouts. Preserve each actual meeting agenda, issue brief, condition, supporting note and annex. Source order matters for agendas, procedures and chronological records. Duplicate writing can be combined without deleting distinct facts.

## Private inventory

Create this inventory from the original documents before drafting. Include a unit for each substantive section or embedded asset. `source_location` identifies the file and a section/page/table/paragraph that a reviewer can locate. Do not include this working inventory in reader-facing HTML.

```json
{
  "units": [
    {
      "id": "brief-a",
      "heading": "Agenda item A: Service capacity",
      "kind": "issue-brief",
      "source_location": "Meeting binder, agenda item A, briefing paragraphs 1–8",
      "status": "included",
      "target_blocks": [{"page_id":"service-capacity","block_id":"capacity-requirements"}],
      "required_text": ["12:00 on 4 November 2026"]
    }
  ]
}
```

Give guide blocks stable IDs. Map units to actual substantive blocks, not merely pages with matching titles. `required_text` holds selective exact anchors taken from the source before drafting: precision-sensitive values with relevant units/qualifiers, dates, identifiers and genuinely verbatim passages. Ordinary explanations and recommendations may be faithfully rewritten. Do not use entire background paragraphs or issue briefings as exact anchors. Obligations, exclusions, negation and relationships still require a semantic review; copying a sentence is not the universal way to verify them. Empty arrays are permissible when a unit contains no precision-sensitive passage; do not omit relevant anchors to make validation pass. Whitespace and Unicode normalization are tolerated; wording, case, punctuation and numbers otherwise remain exact.

`status` is `included`, `merged` or `excluded`. Excluded units require `reason` and an `exclusion_code` from `duplicate`, `blank`, `noninformative`, `user-excluded`. A duplicate also requires `duplicate_of` referencing another unit; a user exclusion requires `user_scope_reference` identifying the user's instruction. Never mark substantive material blank or duplicate to bypass coverage. Excluded units have no destinations.

Legacy `target_page_ids` inventories remain readable without `--strict`. New conversions must use block mappings and source locations:

```bash
python scripts/check_coverage.py source-inventory.json guide.json --strict
python scripts/validate_refract.py guide.json
python scripts/render_refract.py guide.json --output guide.html --fail-on-warnings --inventory source-inventory.json
```

## Independent fidelity review

The script rejects missing/empty targets and altered or absent supplied anchors. It cannot establish that the inventory is complete, that the anchors really came from the source, or that surrounding meaning was preserved. Cross-check independently against the full source, including attachments, captions, footnotes and the last sections. Verify that mandatory language, exceptions, scope, alternatives and proposed-versus-approved status remain connected correctly. Do not rewrite expected anchors to match an incorrect output, and do not paste redundant original wording into the guide merely to satisfy them.

For long sources, process sections with persistent intermediate files and assemble the complete guide. Keep source identities and version dates distinguishable across multiple documents. Do not infer which conflicting source is authoritative.

A reader should be able to use the substantive HTML without routinely reopening the source for essential information. If extraction is incomplete, a critical asset is missing or the format cannot represent a necessary structure, identify the exact limitation beside the download. Do not claim complete replacement.


## Editable coverage and visual assets

Map ordinary prose and tables to editable non-image blocks. The checker rejects an image-only mapping for a textual unit, and text hidden in an image alt/caption cannot satisfy that unit's exact anchors. Genuine visual units use an accurate `kind`: `figure`, `diagram`, `map`, `photograph` or `interface-screenshot`. Do not misclassify source prose as a figure. A meaningful cropped source visual may be retained; screenshots of entire PDF pages are not a default conversion or evidence of coverage. The checker cannot inspect image meaning or establish that an asset was correctly classified.

Fidelity and usability are separate requirements. After coverage review, use plausible reader questions to inspect the transformed guide. A text dump with complete mappings still fails the editorial task. See `transformation.md` for a worked example.
