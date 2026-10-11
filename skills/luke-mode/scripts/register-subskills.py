#!/usr/bin/env python3
"""Expose Luke's bundled commands in one explicit harness skill root."""

import argparse
import os
from pathlib import Path


SKILL_NAMES = (
    "setup-luke-mode",
    "sync-matt-pocock-skills",
)


def register(root: Path) -> list[Path]:
    bundle = Path(__file__).resolve().parents[1]
    root = root.expanduser().resolve()
    if root == bundle or bundle in root.parents:
        raise ValueError("The command root must be outside the Luke bundle.")
    targets = {name: bundle / "skills" / name for name in SKILL_NAMES}
    pending = []
    for name, source in targets.items():
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"Missing bundled skill: {source}")
        target = root / name
        if target.exists() or target.is_symlink():
            if target.is_symlink() and target.resolve() == source:
                continue
            raise ValueError(f"{target} conflicts with this bundle; inspect it first.")
        pending.append((target, source))
    root.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for target, source in pending:
            target.symlink_to(os.path.relpath(source, root), target_is_directory=True)
            created.append(target)
    except OSError:
        for target in reversed(created):
            target.unlink()
        raise
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", type=Path, help="Active harness skill root")
    args = parser.parse_args()
    try:
        created = register(args.skill_root)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot register Luke commands: {error}\n")
    print(f"Registered {len(created)} new commands in {args.skill_root.expanduser()}.")
    print("Refresh harness discovery if needed; bundled routes work immediately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
