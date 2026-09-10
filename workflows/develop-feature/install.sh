#!/usr/bin/env bash
# Install or update the develop-feature Grok workflow or Codex skill.
# Default: user scope (~/.grok), reusable across repositories.
# Never overwrites a project develop-feature.toml.

set -euo pipefail

usage() {
  cat <<'EOF'
Install the develop-feature Grok Build workflow or Codex skill.

Usage:
  ./install.sh [--grok | --codex] [--user | --project] [--link | --copy] [--update]

Runtime
  --grok      Install the Grok Rhai workflow (default).
  --codex     Install the Codex skill into ~/.agents/skills or .agents/skills.

Scopes
  --user      Install for all repositories (default).
  --project   Install into the current repository.

Layout
  --copy      Copy files (default). Required for the .rhai — Grok skips
              symlinked workflow scripts. Codex copies all skill resources.
  --link      Grok: copy .rhai and symlink helper. Codex: symlink skill files.

Other
  --update    Same as a normal install: overwrite the workflow and helper,
              leave project config alone.
  -h, --help  Show this help.

The installer never overwrites:
  .grok/develop-feature.toml
  ~/.grok/develop-feature.toml
  .codex/develop-feature.toml
  Codex config.toml (select model/effort when launching Codex)
EOF
}

SCOPE="user"
MODE="copy"
RUNTIME="grok"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --grok) RUNTIME="grok" ;;
    --codex) RUNTIME="codex" ;;
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

# Keep Codex as a native, self-contained skill; Rhai remains Grok-only.
if [[ "$RUNTIME" == "codex" ]]; then
  if [[ "$SCOPE" == "user" ]]; then
    DEST_SKILL="$HOME/.agents/skills/develop-feature"
    CODEX_TOML=""
  else
    REPO_ROOT="$(git rev-parse --show-toplevel)" || {
      echo "--project requires a git repository (run from the target repo)" >&2
      exit 1
    }
    DEST_SKILL="$REPO_ROOT/.agents/skills/develop-feature"
    CODEX_TOML="$REPO_ROOT/.codex/develop-feature.toml"
  fi
  for resource in SKILL.md README.md scripts/git_state.py references/lifecycle.md examples/develop-feature.toml.example; do
    src="$SRC_DIR/$resource"
    dest="$DEST_SKILL/$resource"
    if [[ ! -f "$src" ]]; then
      echo "missing skill resource: $src" >&2
      exit 1
    fi
    if [[ "$src" -ef "$dest" && ! -L "$dest" ]]; then
      echo "refusing to overwrite source with itself: $dest" >&2
      exit 1
    fi
    mkdir -p "$(dirname "$dest")"
    rm -f "$dest"
    if [[ "$MODE" == "link" ]]; then
      ln -s "$src" "$dest"
    else
      cp "$src" "$dest"
    fi
  done
  # Preserve the fallback config of an existing Grok project.
  if [[ -n "$CODEX_TOML" && ! -e "$CODEX_TOML" && ! -e "$REPO_ROOT/.grok/develop-feature.toml" ]]; then
    mkdir -p "$(dirname "$CODEX_TOML")"
    cp "$EXAMPLE_TOML" "$CODEX_TOML"
  fi
  python3 "$DEST_SKILL/scripts/git_state.py" self-check >/dev/null
  cat <<EOF
Installed develop-feature for Codex ($SCOPE, $MODE)

  skill     $DEST_SKILL/SKILL.md
  helper    $DEST_SKILL/scripts/git_state.py

Start Codex in the target repository:

  codex -m gpt-5.6-sol -c 'model_reasoning_effort="xhigh"'

Then invoke (workers use gpt-5.6-sol / high):

  \$develop-feature {"ticket":"<parent-spec-ticket>"}
  \$develop-feature {"ticket":"<parent-spec-ticket>","mode":"plan"}

Existing project configuration is preserved. Codex config.toml is unchanged.
EOF
  exit 0
fi

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
install_file "$SRC_DIR/references/lifecycle.md" "$DEST_LIB/lifecycle.md" 1
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
  strategy  $DEST_LIB/lifecycle.md
  config    $TOML_NOTE

Invoke from a Grok Build session in the target repository:

  /develop-feature {"ticket":"<parent-spec-ticket>"}
  /workflow develop-feature {"ticket":"<parent-spec-ticket>"}

Plan only (no implementation):

  /workflow develop-feature {"ticket":"<parent-spec-ticket>","mode":"plan"}
EOF
