#!/usr/bin/env bash
# Install or update the develop-feature Grok Build workflow.
# Default: user scope (~/.grok), reusable across repositories.
# Never overwrites a project develop-feature.toml.

set -euo pipefail

usage() {
  cat <<'EOF'
Install the develop-feature Grok Build workflow.

Usage:
  ./install.sh [--user | --project] [--link | --copy] [--update]

Scopes
  --user      Install into ~/.grok (default). Available in every repository.
  --project   Install into the current repository's .grok directory.

Layout
  --copy      Copy files (default). Required for the .rhai — Grok skips
              symlinked workflow scripts.
  --link      Copy the .rhai (same as --copy) and symlink only the git helper.

Other
  --update    Same as a normal install: overwrite the workflow and helper,
              leave project config alone.
  -h, --help  Show this help.

The installer never overwrites:
  .grok/develop-feature.toml
  ~/.grok/develop-feature.toml
EOF
}

SCOPE="user"
MODE="copy"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) SCOPE="user" ;;
    --project) SCOPE="project" ;;
    --copy) MODE="copy" ;;
    --link|--symlink) MODE="link" ;;
    --update) ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
RHAI_SRC="$SRC_DIR/develop-feature.rhai"
HELPER_SRC="$SRC_DIR/scripts/git_state.py"
EXAMPLE_TOML="$SRC_DIR/examples/develop-feature.toml.example"

if [[ ! -f "$RHAI_SRC" ]]; then
  echo "missing workflow source: $RHAI_SRC" >&2
  exit 1
fi
if [[ ! -f "$HELPER_SRC" ]]; then
  echo "missing helper source: $HELPER_SRC" >&2
  exit 1
fi

if [[ "$SCOPE" == "user" ]]; then
  GROK_HOME="${GROK_HOME:-$HOME/.grok}"
  DEST_WORKFLOWS="$GROK_HOME/workflows"
  DEST_LIB="$GROK_HOME/lib/develop-feature"
  DEST_TOML="$GROK_HOME/develop-feature.toml"
else
  if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "--project requires a git repository (run from the target repo)" >&2
    exit 1
  fi
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  DEST_WORKFLOWS="$REPO_ROOT/.grok/workflows"
  DEST_LIB="$REPO_ROOT/.grok/lib/develop-feature"
  DEST_TOML="$REPO_ROOT/.grok/develop-feature.toml"
fi

mkdir -p "$DEST_WORKFLOWS" "$DEST_LIB"

relpath_to() {
  python3 -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' "$1" "$2"
}

install_file() {
  local src="$1"
  local dest="$2"
  local allow_link="$3"
  mkdir -p "$(dirname "$dest")"
  rm -f "$dest"
  if [[ "$MODE" == "link" && "$allow_link" == "1" ]]; then
    local rel
    rel="$(relpath_to "$src" "$(dirname "$dest")")"
    ln -sfn "$rel" "$dest"
  else
    cp "$src" "$dest"
  fi
}

# Grok discovers only regular files in workflows/*.rhai. Symlinks are ignored.
install_file "$RHAI_SRC" "$DEST_WORKFLOWS/develop-feature.rhai" 0
install_file "$HELPER_SRC" "$DEST_LIB/git_state.py" 1
chmod +x "$DEST_LIB/git_state.py"

TOML_NOTE="left existing $DEST_TOML unchanged"
if [[ ! -f "$DEST_TOML" && -f "$EXAMPLE_TOML" ]]; then
  if [[ "$SCOPE" == "project" ]]; then
    cp "$EXAMPLE_TOML" "$DEST_TOML"
    TOML_NOTE="wrote example config to $DEST_TOML (edit it)"
  else
    TOML_NOTE="no user-level toml written; add .grok/develop-feature.toml per repository"
  fi
fi

python3 "$DEST_LIB/git_state.py" self-check >/dev/null

cat <<EOF
Installed develop-feature ($SCOPE, $MODE)

  workflow  $DEST_WORKFLOWS/develop-feature.rhai
  helper    $DEST_LIB/git_state.py
  config    $TOML_NOTE

Invoke from a Grok Build session in the target repository:

  /develop-feature {"ticket":"<parent-spec-ticket>"}
  /workflow develop-feature {"ticket":"<parent-spec-ticket>"}

Plan only (no implementation):

  /workflow develop-feature {"ticket":"<parent-spec-ticket>","mode":"plan"}
EOF
