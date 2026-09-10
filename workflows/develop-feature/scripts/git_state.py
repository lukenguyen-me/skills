#!/usr/bin/env python3
"""Deterministic git and run-state helper for the develop-feature workflow.

Agents call this script. The workflow engine cannot run git itself.
Never merge into a protected base branch. Never push. Never create a PR.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROTECTED_BRANCHES = frozenset(
    {
        "main",
        "master",
        "develop",
        "trunk",
        "production",
        "prod",
        "release",
    }
)

STATE_DIRNAME = ".grok/develop-feature-state"


class HelperError(Exception):
    def __init__(self, message: str, extra: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.extra = extra or {}


def git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise HelperError(f"git {' '.join(args)} failed: {detail}")
    return (result.stdout or "").strip()


def git_root() -> Path:
    try:
        return Path(git("rev-parse", "--show-toplevel")).resolve()
    except HelperError as exc:
        raise HelperError("not a git repository") from exc


def current_branch(root: Path) -> str:
    name = git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    if name == "HEAD":
        raise HelperError("detached HEAD; checkout a branch before continuing")
    return name


def is_dirty(root: Path) -> bool:
    return bool(git("status", "--porcelain", cwd=root))


def sanitize_id(value: str) -> str:
    text = value.strip()
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text)
    text = text.strip("-._")
    return text or "ticket"


def is_protected(name: str) -> bool:
    short = name.rsplit("/", 1)[-1].lower()
    return name.lower() in PROTECTED_BRANCHES or short in PROTECTED_BRANCHES


def detect_base_branch(root: Path) -> str:
    symbolic = git("symbolic-ref", "refs/remotes/origin/HEAD", cwd=root, check=False)
    if symbolic:
        # refs/remotes/origin/main
        parts = symbolic.strip().split("/")
        if parts:
            return parts[-1]
    for candidate in ("main", "master", "develop"):
        if git("rev-parse", "--verify", "--quiet", f"refs/heads/{candidate}", cwd=root, check=False):
            return candidate
        if git("rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{candidate}", cwd=root, check=False):
            return candidate
    return current_branch(root)


def ref_exists(root: Path, ref: str) -> bool:
    out = git("rev-parse", "--verify", "--quiet", ref, cwd=root, check=False)
    return bool(out)


def emit(payload: dict[str, Any], ok: bool = True) -> int:
    payload.setdefault("ok", ok)
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if ok else 1


def state_path(root: Path, parent_id: str) -> Path:
    return root / STATE_DIRNAME / f"{sanitize_id(parent_id)}.json"


def read_state(root: Path, parent_id: str) -> dict[str, Any]:
    path = state_path(root, parent_id)
    if not path.exists():
        return {
            "parent_id": parent_id,
            "status": "new",
            "base_branch": "",
            "parent_branch": "",
            "children": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(root: Path, parent_id: str, data: dict[str, Any]) -> Path:
    path = state_path(root, parent_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def child_entry(state: dict[str, Any], child_id: str) -> dict[str, Any] | None:
    for item in state.get("children") or []:
        if str(item.get("id")) == str(child_id):
            return item
    return None


def upsert_child(state: dict[str, Any], child_id: str, **fields: Any) -> None:
    children = list(state.get("children") or [])
    for item in children:
        if str(item.get("id")) == str(child_id):
            item.update(fields)
            item["id"] = child_id
            state["children"] = children
            return
    entry = {"id": child_id, "status": "pending"}
    entry.update(fields)
    children.append(entry)
    state["children"] = children


def cmd_info(_args: argparse.Namespace) -> int:
    root = git_root()
    base = detect_base_branch(root)
    payload = {
        "git_root": str(root),
        "current_branch": current_branch(root),
        "base_branch": base,
        "dirty": is_dirty(root),
        "head": git("rev-parse", "HEAD", cwd=root),
        "state_dir": str(root / STATE_DIRNAME),
        "protected_branches": sorted(PROTECTED_BRANCHES),
    }
    return emit(payload)


def cmd_prepare_parent(args: argparse.Namespace) -> int:
    root = git_root()
    branch = args.branch
    base = args.base or detect_base_branch(root)
    if is_protected(branch) or branch == base:
        raise HelperError(
            f"refusing to use protected or base branch {branch!r} as the parent feature branch",
            {"branch": branch, "base": base},
        )
    if is_dirty(root) and current_branch(root) != branch:
        raise HelperError(
            "working tree is dirty; commit or stash before creating/checking out the parent branch",
            {"status": git("status", "--porcelain", cwd=root)},
        )

    created = False
    if ref_exists(root, f"refs/heads/{branch}"):
        git("checkout", branch, cwd=root)
    else:
        start = base
        if ref_exists(root, f"refs/remotes/origin/{base}"):
            start = f"origin/{base}"
        elif not ref_exists(root, f"refs/heads/{base}"):
            raise HelperError(f"base branch {base!r} does not exist")
        git("branch", "--no-track", branch, start, cwd=root)
        git("checkout", branch, cwd=root)
        created = True

    parent_id = args.parent
    state = read_state(root, parent_id)
    state.update(
        {
            "parent_id": parent_id,
            "status": "prepared",
            "base_branch": base,
            "parent_branch": branch,
            "parent_sha": git("rev-parse", "HEAD", cwd=root),
        }
    )
    path = write_state(root, parent_id, state)
    return emit(
        {
            "action": "prepare-parent",
            "created": created,
            "parent_id": parent_id,
            "parent_branch": branch,
            "base_branch": base,
            "sha": state["parent_sha"],
            "state_path": str(path),
        }
    )


def cmd_start_child(args: argparse.Namespace) -> int:
    root = git_root()
    child_branch = args.branch
    parent_branch = args.parent_branch
    if is_protected(child_branch):
        raise HelperError(f"refusing protected child branch {child_branch!r}")
    if child_branch == parent_branch:
        raise HelperError("child branch must differ from the parent branch")
    if is_dirty(root):
        raise HelperError(
            "working tree is dirty; commit the current child before starting the next one",
            {"status": git("status", "--porcelain", cwd=root)},
        )
    if not ref_exists(root, f"refs/heads/{parent_branch}"):
        raise HelperError(f"parent branch {parent_branch!r} does not exist")

    git("checkout", parent_branch, cwd=root)
    created = False
    if ref_exists(root, f"refs/heads/{child_branch}"):
        git("checkout", child_branch, cwd=root)
    else:
        git("checkout", "-b", child_branch, parent_branch, cwd=root)
        created = True

    if args.parent and args.child:
        state = read_state(root, args.parent)
        upsert_child(
            state,
            args.child,
            status="implementing",
            branch=child_branch,
            base_sha=git("rev-parse", "HEAD", cwd=root),
        )
        write_state(root, args.parent, state)

    return emit(
        {
            "action": "start-child",
            "created": created,
            "child_branch": child_branch,
            "parent_branch": parent_branch,
            "sha": git("rev-parse", "HEAD", cwd=root),
        }
    )


def cmd_integrate_child(args: argparse.Namespace) -> int:
    root = git_root()
    child_branch = args.branch
    parent_branch = args.parent_branch
    if is_protected(parent_branch):
        raise HelperError(
            f"refusing to merge into protected branch {parent_branch!r}",
            {"parent_branch": parent_branch},
        )
    if child_branch == parent_branch:
        # Already on the integration branch; just record the SHA.
        git("checkout", parent_branch, cwd=root)
        sha = git("rev-parse", "HEAD", cwd=root)
        if args.parent and args.child:
            state = read_state(root, args.parent)
            upsert_child(state, args.child, status="integrated", sha=sha, branch=child_branch)
            state["status"] = "in_progress"
            state["parent_sha"] = sha
            write_state(root, args.parent, state)
        return emit(
            {
                "action": "integrate-child",
                "merged": False,
                "already_on_parent": True,
                "parent_branch": parent_branch,
                "sha": sha,
            }
        )

    if is_dirty(root):
        raise HelperError(
            "working tree is dirty; commit on the child branch before integrating",
            {"status": git("status", "--porcelain", cwd=root)},
        )
    if not ref_exists(root, f"refs/heads/{child_branch}"):
        raise HelperError(f"child branch {child_branch!r} does not exist")
    if not ref_exists(root, f"refs/heads/{parent_branch}"):
        raise HelperError(f"parent branch {parent_branch!r} does not exist")

    git("checkout", parent_branch, cwd=root)
    merge_args = ["merge", "--no-edit"]
    if args.ff:
        merge_args.append("--ff")
    else:
        merge_args.append("--no-ff")
    merge_args.append(child_branch)
    git(*merge_args, cwd=root)
    sha = git("rev-parse", "HEAD", cwd=root)

    deleted = False
    if args.delete_child:
        git("branch", "-d", child_branch, cwd=root)
        deleted = True

    if args.parent and args.child:
        state = read_state(root, args.parent)
        upsert_child(
            state,
            args.child,
            status="integrated",
            sha=sha,
            branch=child_branch,
        )
        state["status"] = "in_progress"
        state["parent_sha"] = sha
        write_state(root, args.parent, state)

    return emit(
        {
            "action": "integrate-child",
            "merged": True,
            "parent_branch": parent_branch,
            "child_branch": child_branch,
            "deleted_child_branch": deleted,
            "sha": sha,
        }
    )


def cmd_state_read(args: argparse.Namespace) -> int:
    root = git_root()
    path = state_path(root, args.parent)
    data = read_state(root, args.parent)
    data["state_path"] = str(path)
    data["exists"] = path.exists()
    return emit(data)


def cmd_state_mark(args: argparse.Namespace) -> int:
    root = git_root()
    state = read_state(root, args.parent)
    fields: dict[str, Any] = {"status": args.status}
    if args.sha:
        fields["sha"] = args.sha
    if args.branch:
        fields["branch"] = args.branch
    if args.note:
        fields["note"] = args.note
    upsert_child(state, args.child, **fields)
    if args.status == "failed":
        state["status"] = "stopped"
        state["stop_reason"] = args.note or f"child {args.child} failed"
    path = write_state(root, args.parent, state)
    return emit({"action": "state-mark", "state_path": str(path), "state": state})


def cmd_assert_not_base(args: argparse.Namespace) -> int:
    if is_protected(args.branch) or args.branch == args.base:
        raise HelperError(
            f"branch {args.branch!r} is protected or equals base {args.base!r}"
        )
    return emit({"action": "assert-not-base", "branch": args.branch, "base": args.base})


def cmd_self_check(_args: argparse.Namespace) -> int:
    """Non-mutating checks used by the package smoke test."""
    root = git_root()
    base = detect_base_branch(root)
    checks = {
        "git_root": str(root),
        "base_branch": base,
        "main_is_protected": is_protected("main"),
        "feature_not_protected": not is_protected("feat/SMOKE-1"),
        "sanitize": sanitize_id("Feat 123/foo") == "Feat-123-foo",
        "state_path_parent": str(state_path(root, "FEAT/123")).endswith(
            f"{STATE_DIRNAME}/FEAT-123.json"
        ),
    }
    failed = [key for key, value in checks.items() if value is False]
    return emit({"action": "self-check", "checks": checks, "failed": failed}, ok=not failed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Git and run-state helper for the develop-feature workflow"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="print repo, branch, and dirty state")
    sub.add_parser("self-check", help="non-mutating sanity checks")

    p = sub.add_parser("prepare-parent", help="create or checkout the parent feature branch")
    p.add_argument("--parent", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--base", default="")

    p = sub.add_parser("start-child", help="create or checkout a child branch from the parent")
    p.add_argument("--branch", required=True)
    p.add_argument("--parent-branch", required=True)
    p.add_argument("--parent", default="")
    p.add_argument("--child", default="")

    p = sub.add_parser("integrate-child", help="merge a child branch into the parent")
    p.add_argument("--branch", required=True)
    p.add_argument("--parent-branch", required=True)
    p.add_argument("--parent", default="")
    p.add_argument("--child", default="")
    p.add_argument("--ff", action="store_true", help="allow fast-forward instead of --no-ff")
    p.add_argument(
        "--delete-child",
        action="store_true",
        help="delete the local child branch after a successful merge",
    )

    p = sub.add_parser("state-read", help="read the run-state file")
    p.add_argument("--parent", required=True)

    p = sub.add_parser("state-mark", help="update one child's status in the run-state file")
    p.add_argument("--parent", required=True)
    p.add_argument("--child", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--sha", default="")
    p.add_argument("--branch", default="")
    p.add_argument("--note", default="")

    p = sub.add_parser("assert-not-base", help="refuse protected/base branch names")
    p.add_argument("--branch", required=True)
    p.add_argument("--base", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    commands = {
        "info": cmd_info,
        "self-check": cmd_self_check,
        "prepare-parent": cmd_prepare_parent,
        "start-child": cmd_start_child,
        "integrate-child": cmd_integrate_child,
        "state-read": cmd_state_read,
        "state-mark": cmd_state_mark,
        "assert-not-base": cmd_assert_not_base,
    }
    try:
        return commands[args.command](args)
    except HelperError as exc:
        payload = {"ok": False, "error": str(exc)}
        payload.update(exc.extra)
        return emit(payload, ok=False)


if __name__ == "__main__":
    sys.exit(main())
