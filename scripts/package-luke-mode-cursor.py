#!/usr/bin/env python3
"""Prepare a standalone Luke Mode skill with Cursor's native invocation policy."""

import argparse
from pathlib import Path
import re
import shutil
import tempfile


def package(destination: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "skills" / "luke-mode"
    destination = destination.expanduser()
    if destination.name != "luke-mode":
        raise ValueError("The destination folder must be named luke-mode.")
    if destination.exists() or destination.is_symlink():
        raise ValueError("The destination exists. Inspect it before updating.")
    destination = destination.resolve()
    if (
        source == destination
        or source in destination.parents
        or destination in source.parents
    ):
        raise ValueError("The destination must be outside the source skill.")

    skill = (source / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        raise ValueError("The source skill has no YAML frontmatter.")
    frontmatter, separator, body = skill[4:].partition("\n---\n")
    if not separator:
        raise ValueError("The source skill has unclosed YAML frontmatter.")
    if re.search(r"^disable-model-invocation:", frontmatter, re.MULTILINE):
        raise ValueError("The source already defines Cursor invocation policy.")
    cursor_skill = f"---\n{frontmatter}\ndisable-model-invocation: true\n---\n{body}"

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".luke-mode-", dir=destination.parent) as staging:
        prepared = Path(staging) / "luke-mode"

        def ignore_entrypoint(folder: str, _names: list[str]) -> list[str]:
            return ["SKILL.md"] if Path(folder) == source else []

        shutil.copytree(source, prepared, ignore=ignore_entrypoint)
        (prepared / "SKILL.md").write_text(cursor_skill, encoding="utf-8")
        if destination.exists() or destination.is_symlink():
            raise ValueError(
                "The destination appeared during packaging. Inspect it before updating."
            )
        prepared.rename(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New skill folder, ending in luke-mode")
    args = parser.parse_args()
    try:
        package(args.destination)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot package Luke Mode: {error}\n")
    print(f"Prepared {args.destination.expanduser().resolve()}")
    print("Cursor policy: disable-model-invocation: true. Invoke with /luke-mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
