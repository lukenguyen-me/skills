#!/usr/bin/env python3
"""Check App Store and Play Store field limits and forbidden characters."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

APP_STORE_SYMBOLS = frozenset("✓✔•‣◦†‡")
PLAY_COMPACT_SYMBOLS = frozenset("★☆")
HTML_RE = re.compile(r"</?[A-Za-z][^>]*>")
PLAY_COMPACT_FORMAT_RE = re.compile(
    r"\n|\?\?|!!|\?!|!\?!|<>|\\\\|---|\*\*\*|\+_\+|\(\(|\$%\^|~&~|~~~"
)
WORD_RE = re.compile(r"[\w]+", re.UNICODE)

# Limits are the source of truth for this checker. Keep the store references
# in sync when a limit changes.
APP_FIELDS = {
    "app name": {"max_characters": 30, "forbid_app_store_symbols": True},
    "subtitle": {"max_characters": 30, "forbid_app_store_symbols": True},
    "promotional text": {"max_characters": 170, "forbid_app_store_symbols": True},
    "description": {"max_characters": 4000, "forbid_app_store_symbols": True},
    "keywords": {"max_bytes": 100, "forbid_app_store_symbols": True},
    "version notes": {"max_characters": 4000, "forbid_app_store_symbols": True},
}

PLAY_FIELDS = {
    "app title": {"max_characters": 30, "forbid_play_compact_symbols": True},
    "short description": {"max_characters": 80, "forbid_play_compact_symbols": True},
    "full description": {"max_characters": 4000},
    "version notes": {"max_characters": 500},
}

STORES = {"app": APP_FIELDS, "play": PLAY_FIELDS}


def contains_emoji(text: str) -> bool:
    for char in text:
        code = ord(char)
        if 0x1F300 <= code <= 0x1FAFF or 0x2600 <= code <= 0x27BF:
            return True
        if 0xFE00 <= code <= 0xFE0F or 0x200D == code:
            return True
        if unicodedata.category(char) == "So" and code > 0x2000:
            return True
    return False


def analyze_field(value: str, options: dict) -> dict:
    characters = len(value)
    byte_count = len(value.encode("utf-8"))
    errors: list[str] = []

    max_characters = options.get("max_characters")
    if max_characters is not None and characters > max_characters:
        errors.append(f"exceeds {max_characters} characters ({characters})")

    max_bytes = options.get("max_bytes")
    if max_bytes is not None and byte_count > max_bytes:
        errors.append(f"exceeds {max_bytes} UTF-8 bytes ({byte_count})")

    if HTML_RE.search(value):
        errors.append("contains HTML markup")

    if options.get("forbid_app_store_symbols"):
        if any(char in APP_STORE_SYMBOLS for char in value):
            errors.append("contains an App Store-prohibited symbol")
        if contains_emoji(value):
            errors.append("contains emoji")

    if options.get("forbid_play_compact_symbols"):
        if contains_emoji(value) or any(char in PLAY_COMPACT_SYMBOLS for char in value):
            errors.append("contains a symbol prohibited in compact Play Store fields")
        if PLAY_COMPACT_FORMAT_RE.search(value):
            errors.append("contains formatting prohibited in compact Play Store fields")

    return {"characters": characters, "bytes": byte_count, "errors": errors}


def words(value: str) -> list[str]:
    return [match.group(0).casefold() for match in WORD_RE.finditer(value)]


def find_duplicate_keywords(keyword_value: str, name_and_subtitle: str = "") -> list[str]:
    keywords = [item.strip().casefold() for item in keyword_value.split(",") if item.strip()]
    errors: list[str] = []
    seen: set[str] = set()
    title_words = set(words(name_and_subtitle))

    for keyword in keywords:
        if keyword in seen:
            errors.append(f"duplicate keyword: {keyword}")
        seen.add(keyword)
        for keyword_word in words(keyword):
            if keyword_word in title_words:
                errors.append(f"keyword repeats name or subtitle word: {keyword_word}")

    return list(dict.fromkeys(errors))


def extract_text_fields(markdown: str) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    section = ""
    field = ""
    collecting = False
    value_lines: list[str] = []

    for line in markdown.split("\n"):
        if not collecting and line.startswith("## "):
            section = line[3:].strip()
            continue
        if not collecting and line.startswith("### "):
            field = line[4:].strip().casefold()
            continue
        if not collecting and line.strip() == "```text":
            collecting = True
            value_lines = []
            continue
        if collecting and line.strip() == "```":
            fields.append(
                {
                    "section": section,
                    "field": field,
                    "value": "\n".join(value_lines).strip(),
                }
            )
            collecting = False
            value_lines = []
            continue
        if collecting:
            value_lines.append(line)

    return fields


def infer_store(path: Path, store: str | None) -> str:
    if store:
        return store
    name = path.name.casefold()
    if "play" in name:
        return "play"
    if "app" in name:
        return "app"
    raise SystemExit("Pass --store app or --store play when the file name does not include app or play.")


def limit_label(result: dict, options: dict) -> str:
    if "max_bytes" in options:
        return f"{result['bytes']}/{options['max_bytes']} UTF-8 bytes"
    return f"{result['characters']}/{options['max_characters']} characters"


def print_list(store: str | None) -> int:
    selected = [store] if store else ["app", "play"]
    for name in selected:
        print(f"# {name}")
        for field, options in STORES[name].items():
            if "max_bytes" in options:
                print(f"{field}: {options['max_bytes']} UTF-8 bytes")
            else:
                print(f"{field}: {options['max_characters']} characters")
        print()
    return 0


def check_value(store: str, field: str, value: str, name_and_subtitle: str = "") -> list[str]:
    fields = STORES[store]
    if field not in fields:
        known = ", ".join(fields)
        raise SystemExit(f"Unknown {store} field '{field}'. Known fields: {known}")
    options = fields[field]
    result = analyze_field(value, options)
    errors = list(result["errors"])
    if store == "app" and field == "keywords":
        errors.extend(find_duplicate_keywords(value, name_and_subtitle))
    prefix = f"{store} / {field}: "
    lines = [f"{prefix}{limit_label(result, options)}"]
    lines.extend(f"{prefix}{error}" for error in errors)
    for line in lines:
        print(line)
    return errors


def check_markdown(path: Path, store: str) -> list[str]:
    markdown = path.read_text(encoding="utf-8")
    fields = extract_text_fields(markdown)
    catalog = STORES[store]
    errors: list[str] = []
    locale_names: dict[str, str] = {}
    locale_subtitles: dict[str, str] = {}

    for entry in fields:
        if entry["field"] in {"app name", "app title"}:
            locale_names[entry["section"]] = entry["value"]
        if entry["field"] == "subtitle":
            locale_subtitles[entry["section"]] = entry["value"]

    for entry in fields:
        field = entry["field"]
        if field not in catalog:
            continue
        options = catalog[field]
        result = analyze_field(entry["value"], options)
        label = f"{path.name} / {entry['section']} / {field}"
        print(f"{label}: {limit_label(result, options)}")
        field_errors = list(result["errors"])
        if store == "app" and field == "keywords":
            title = f"{locale_names.get(entry['section'], '')} {locale_subtitles.get(entry['section'], '')}"
            field_errors.extend(find_duplicate_keywords(entry["value"], title))
        for error in field_errors:
            print(f"{label}: {error}")
        errors.extend(field_errors)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="Print field limits")
    parser.add_argument("--store", choices=sorted(STORES), help="app or play")
    parser.add_argument("--field", help="Field name, for example 'version notes'")
    parser.add_argument("--text", help="Field value to check")
    parser.add_argument("--file", type=Path, help="Read a single field value from a file")
    parser.add_argument("--markdown", type=Path, help="Validate fenced text fields in a store document")
    parser.add_argument("--name-subtitle", default="", help="App name plus subtitle, used for keyword checks")
    args = parser.parse_args(argv)

    if args.list:
        return print_list(args.store)

    if args.markdown:
        store = infer_store(args.markdown, args.store)
        errors = check_markdown(args.markdown, store)
        return 1 if errors else 0

    if not args.store or not args.field:
        parser.error("checking a field requires --store and --field")

    if args.text is not None:
        value = args.text
    elif args.file:
        value = args.file.read_text(encoding="utf-8").strip()
    else:
        value = sys.stdin.read()

    errors = check_value(args.store, args.field.casefold(), value, args.name_subtitle)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
