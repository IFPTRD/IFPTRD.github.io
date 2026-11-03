#!/usr/bin/env python3
"""Render an editable standalone Refract HTML guide from a validated JSON file.

Usage: python scripts/render_refract.py guide-content.json --output guide.html --fail-on-warnings
No external dependencies or network requests. The generated HTML can be imported into Refract Studio.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from validate_refract import check, normalize

FORMAT_VERSION = 1
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "guide-template.html"

def render(data, template_path=DEFAULT_TEMPLATE):
    template = template_path.read_text(encoding="utf-8-sig")
    tokens = ("__DATA_JSON__", "__EDITOR_MODE__", "__EDITOR_PAGE__")
    for token in tokens:
        if template.count(token) != 1:
            raise ValueError("Template must contain exactly one " + token)
    if 'id="guide-data"' not in template:
        raise ValueError("Template does not embed Refract guide data")
    # Do template substitutions before inserting user content.
    template = template.replace("__EDITOR_MODE__", "false").replace("__EDITOR_PAGE__", "null")
    safe = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    safe = (safe.replace("<", r"\u003c")
                .replace("&", r"\u0026")
                .replace("\u2028", r"\u2028")
                .replace("\u2029", r"\u2029"))
    return template.replace("__DATA_JSON__", safe)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Render standalone editable Refract HTML")
    parser.add_argument("input", type=Path, help="Refract JSON input file")
    parser.add_argument("--output", type=Path, default=Path("guide.html"))
    parser.add_argument("--normalize", action="store_true", help="Normalize known compatible block shapes")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Require all editorial warnings to be resolved")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print("ERROR: Invalid source JSON: " + str(exc), file=sys.stderr)
        return 2
    if args.normalize:
        normalize(data)
    errors, warnings = check(data)
    for warning in warnings:
        print("EDITORIAL WARNING: " + warning, file=sys.stderr)
    for error in errors:
        print("STRUCTURAL ERROR: " + error, file=sys.stderr)
    if errors:
        print("Rendering cancelled: correct the input JSON.", file=sys.stderr)
        return 2
    if warnings and args.fail_on_warnings:
        print("Rendering cancelled: resolve editorial warnings first.", file=sys.stderr)
        return 3
    try:
        if args.output.resolve() in (args.input.resolve(), args.template.resolve()):
            raise ValueError("Output cannot overwrite input or template")
        html = render(data, args.template)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 4
    print("CREATED: " + str(args.output) + " (" + str(len(data["pages"])) + " pages; Refract v" + str(FORMAT_VERSION) + ")")
    return 0

if __name__ == "__main__":
    sys.exit(main())
