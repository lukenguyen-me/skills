#!/usr/bin/env python3
"""Prepare Luke Mode and its four companion skills for Cursor in one skill root."""

import argparse
from pathlib import Path
import re
import shutil
import tempfile


SKILL_NAMES = (
    "luke-mode",
    "setup-luke-mode",
    "sync-matt-pocock-skills",
    "create-verification-skill",
    "maintain-verification-skill",
)
EXPLICIT_ONLY = frozenset(
    {"luke-mode", "create-verification-skill", "maintain-verification-skill"}
)


def cursor_entrypoint(source: Path) -> str:
    skill = (source / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        raise ValueError(f"{source.name} has no YAML frontmatter.")
    frontmatter, separator, body = skill[4:].partition("\n---\n")
    if not separator:
        raise ValueError(f"{source.name} has unclosed YAML frontmatter.")
    if source.name not in EXPLICIT_ONLY:
        return skill
    if re.search(r"^disable-model-invocation:", frontmatter, re.MULTILINE):
        raise ValueError("The source already defines Cursor invocation policy.")
    return f"---\n{frontmatter}\ndisable-model-invocation: true\n---\n{body}"


def package(destination: Path) -> None:
    skill_root = Path(__file__).resolve().parents[1] / "skills"
    sources = {name: skill_root / name for name in SKILL_NAMES}
    destination = destination.expanduser()
    if destination.name != "luke-mode":
        raise ValueError("The destination folder must be named luke-mode.")
    destinations = {name: destination.parent / name for name in SKILL_NAMES}

    def check_destinations() -> None:
        for target in destinations.values():
            if target.exists() or target.is_symlink():
                raise ValueError(f"{target} exists. Inspect it before updating.")

    check_destinations()
    destinations = {name: target.resolve() for name, target in destinations.items()}
    for source in sources.values():
        for target in destinations.values():
            if source == target or source in target.parents or target in source.parents:
                raise ValueError("The destination must be outside the source skills.")
    entrypoints = {name: cursor_entrypoint(source) for name, source in sources.items()}

    target_root = destinations["luke-mode"].parent
    target_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".luke-mode-", dir=target_root) as staging:
        for name, source in sources.items():
            prepared = Path(staging) / name

            def ignore_entrypoint(folder: str, _names: list[str]) -> list[str]:
                return ["SKILL.md"] if Path(folder) == source else []

            shutil.copytree(source, prepared, ignore=ignore_entrypoint)
            (prepared / "SKILL.md").write_text(entrypoints[name], encoding="utf-8")
        check_destinations()
        published = []
        try:
            for name, target in destinations.items():
                if target.exists() or target.is_symlink():
                    raise ValueError(f"{target} appeared during packaging.")
                (Path(staging) / name).rename(target)
                published.append(target)
        except (OSError, ValueError):
            for target in reversed(published):
                target.rename(Path(staging) / target.name)
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        type=Path,
        help="New luke-mode folder; all four companions are created beside it",
    )
    args = parser.parse_args()
    try:
        package(args.destination)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot package Luke Mode: {error}\n")
    print(f"Prepared {args.destination.expanduser().resolve()}")
    print(f"Prepared sibling skills: {', '.join(SKILL_NAMES[1:])}.")
    print(
        "Cursor explicit-only: /luke-mode, /create-verification-skill, "
        "/maintain-verification-skill."
    )
    print("Setup and sync support matching requests and routing from Luke Mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
