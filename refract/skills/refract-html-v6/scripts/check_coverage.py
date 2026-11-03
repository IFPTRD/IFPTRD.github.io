#!/usr/bin/env python3
"""Check an author-built source inventory against the finished Refract JSON.

Usage:
    python scripts/check_coverage.py source-inventory.json guide.json

This verifies mapping completeness and page references. It CANNOT prove that
the LLM enumerated every original source section or preserved every fact.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

VALID_STATUSES = {"included", "merged", "excluded"}
ALLOWED_EXCLUSIONS = ("duplicate", "blank", "noninformative", "out of scope", "out-of-scope", "user excluded", "user-excluded")

def check_coverage(inventory: dict, guide: dict) -> list[str]:
    errors = []
    if not isinstance(inventory, dict):
        return ["source inventory must be a JSON object"]
    if not isinstance(guide, dict):
        return ["guide must be a JSON object"]
    units = inventory.get("units")
    pages = guide.get("pages")
    if not isinstance(units, list) or not units:
        errors.append("source inventory units must be a nonempty array")
        return errors
    if not isinstance(pages, list) or not pages:
        errors.append("guide pages must be a nonempty array")
        return errors
    page_ids = {p.get("id") for p in pages if isinstance(p, dict) and isinstance(p.get("id"), str)}
    used = set()
    for i, unit in enumerate(units):
        label = f"units[{i}]"
        if not isinstance(unit, dict):
            errors.append(f"{label}: expected an object")
            continue
        uid = unit.get("id")
        heading = unit.get("heading")
        kind = unit.get("kind")
        status = unit.get("status")
        targets = unit.get("target_page_ids")
        if not isinstance(uid, str) or not uid.strip():
            errors.append(f"{label}.id: required nonempty string")
        elif uid in used:
            errors.append(f"{label}.id: duplicate source unit ID {uid}")
        else:
            used.add(uid)
        if not isinstance(heading, str) or not heading.strip():
            errors.append(f"{label}.heading: source heading is required")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(f"{label}.kind: source unit kind is required")
        if status not in VALID_STATUSES:
            errors.append(f"{label}.status: must be included, merged or excluded")
            continue
        if status == "excluded":
            reason = unit.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{label}.reason: excluded source unit requires explicit reason")
            elif not any(token in reason.lower() for token in ALLOWED_EXCLUSIONS):
                errors.append(f"{label}.reason: exclusions allowed only for duplicates, blank/noninformative items, or user-explicit exclusions")
            if targets not in ([], None):
                errors.append(f"{label}.target_page_ids: excluded units must not claim page coverage")
            continue
        if not isinstance(targets, list) or not targets:
            errors.append(f"{label}.target_page_ids: source unit not assigned to any guide page")
            continue
        for target in targets:
            if not isinstance(target, str) or target not in page_ids:
                errors.append(f"{label}.target_page_ids: unknown guide page {target!r}")
    return errors

def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 2:
        print("Usage: check_coverage.py source-inventory.json guide.json", file=sys.stderr)
        return 2
    try:
        inventory = json.loads(Path(argv[0]).read_text(encoding="utf-8-sig"))
        guide = json.loads(Path(argv[1]).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    errors = check_coverage(inventory, guide)
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    if errors:
        print(f"FAIL: {len(errors)} source mapping error(s); correct before rendering", file=sys.stderr)
        return 1
    print(f"PASS: {len(inventory['units'])} inventoried source units mapped to {len(guide['pages'])} guide pages.")
    print("NOTE: This cannot prove the inventory itself is complete or the content is faithfully retained. Review against the source.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
