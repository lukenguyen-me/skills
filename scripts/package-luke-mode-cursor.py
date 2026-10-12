#!/usr/bin/env python3
"""Prepare one self-contained Luke Mode bundle for Cursor."""

import argparse
from pathlib import Path
import re
import shutil
import tempfile


SKILL_NAMES = (
    "luke-mode",
    "setup-luke-mode",
    "sync-matt-pocock-skills",
)
EXPLICIT_ONLY = frozenset({"luke-mode"})


def cursor_entrypoint(source: Path) -> str:
    skill = (source / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        raise ValueError(f"{source.name} has no YAML frontmatter.")
    frontmatter, separator, body = skill[4:].partition("\n---\n")
    if not separator:
        raise ValueError(f"{source.name} has unclosed YAML frontmatter.")
    if source.name not in EXPLICIT_ONLY:
        return skill
    existing = re.search(r"^disable-model-invocation:\s*(.*)$", frontmatter, re.MULTILINE)
    if existing:
        if existing.group(1).strip() != "true":
            raise ValueError(f"{source.name} must be explicit-only.")
        return skill
    return f"---\n{frontmatter}\ndisable-model-invocation: true\n---\n{body}"


def package(destination: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "skills" / "luke-mode"
    destination = destination.expanduser()
    if destination.name != "luke-mode":
        raise ValueError("The destination folder must be named luke-mode.")
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"{destination} exists. Inspect it before updating.")
    destination = destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("The destination must be outside the source bundle.")
    sources = {"luke-mode": source}
    sources.update({name: source / "skills" / name for name in SKILL_NAMES[1:]})
    entrypoints = {
        skill.relative_to(source) / "SKILL.md": cursor_entrypoint(skill)
        for skill in sources.values()
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".luke-mode-", dir=destination.parent) as staging:
        prepared = Path(staging) / "luke-mode"
        shutil.copytree(source, prepared)
        for relative, content in entrypoints.items():
            (prepared / relative).write_text(content, encoding="utf-8")
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"{destination} appeared during packaging.")
        prepared.rename(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        type=Path,
        help="New luke-mode folder containing both bundled sub-skills",
    )
    args = parser.parse_args()
    try:
        package(args.destination)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot package Luke Mode: {error}\n")
    print(f"Prepared {args.destination.expanduser().resolve()}")
    print(f"Included bundled skills: {', '.join(SKILL_NAMES[1:])}.")
    print("Cursor explicit-only: /luke-mode.")
    print("Setup and sync support matching requests and routing from Luke Mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
