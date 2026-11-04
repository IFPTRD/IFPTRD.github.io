# Source coverage and precision review

The default is a complete, clearer replacement for the source's substantive content. Preserve each actual meeting agenda, issue brief, condition, supporting note and annex. Source order matters for agendas, procedures and chronological records. Duplicate writing can be combined without deleting distinct facts.

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
      "required_text": ["Requests must be received by 12:00 on 4 November 2026."]
    }
  ]
}
```

Give guide blocks stable IDs. Map units to actual substantive blocks, not merely pages with matching titles. `required_text` holds exact source passages selected before drafting: numbers with units, qualifications, dates, formal recommendations, obligations, exclusions and negation. Empty arrays are permissible when a unit contains no precision-sensitive passage; do not omit relevant anchors to make validation pass. Whitespace and Unicode normalization are tolerated; wording, case, punctuation and numbers otherwise remain exact.

`status` is `included`, `merged` or `excluded`. Excluded units require `reason` and an `exclusion_code` from `duplicate`, `blank`, `noninformative`, `user-excluded`. A duplicate also requires `duplicate_of` referencing another unit; a user exclusion requires `user_scope_reference` identifying the user's instruction. Never mark substantive material blank or duplicate to bypass coverage. Excluded units have no destinations.

Legacy `target_page_ids` inventories remain readable without `--strict`. New conversions must use block mappings and source locations:

```bash
python scripts/check_coverage.py source-inventory.json guide.json --strict
python scripts/validate_refract.py guide.json
python scripts/render_refract.py guide.json --output guide.html --fail-on-warnings --inventory source-inventory.json
```

## Independent fidelity review

The script rejects missing/empty targets and altered or absent supplied anchors. It cannot establish that the inventory is complete, that the anchors really came from the source, or that surrounding meaning was preserved. Cross-check independently against the full source, including attachments, captions, footnotes and the last sections. Verify that mandatory language, exceptions, scope, alternatives and proposed-versus-approved status remain connected correctly. Do not rewrite expected anchors to match an incorrect output.

For long sources, process sections with persistent intermediate files and assemble the complete guide. Keep source identities and version dates distinguishable across multiple documents. Do not infer which conflicting source is authoritative.

A reader should be able to use the substantive HTML without routinely reopening the source for essential information. If extraction is incomplete, a critical asset is missing or the format cannot represent a necessary structure, identify the exact limitation beside the download. Do not claim complete replacement.
