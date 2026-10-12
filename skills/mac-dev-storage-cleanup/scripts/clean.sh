#!/bin/bash
# Deletion for the mac-dev-storage-cleanup skill. Run it only after the user confirmed.
#
# Usage:
#   clean.sh preflight                 fail while Xcode, Simulator, Android Studio, or Cursor runs
#   clean.sh stop-gradle               stop Gradle daemons
#   clean.sh run --plan FILE [--dry-run] [--tier safe|old]... [--project PATH]... [ID[,ID]...]
#
# run acts on rows of the plan that scan.sh wrote:
#   --tier safe|old   every row of that tier (ask and report rows need ids)
#   ID                one named row (ask-first rows are chosen this way)
#   --project PATH    the build artifacts of one project the user named (a path,
#                     or a folder name that is unique in the plan)
# Official commands run from a fixed list. Everything else moves to ~/.Trash,
# which frees space only once the Trash is emptied; an approved empty-trash row
# always runs last. Every action is logged to ~/Library/Logs/dev-cleanup.log.
# --dry-run changes nothing.

DIR=$(cd "$(dirname "$0")" && pwd)
. "$DIR/lib.sh"

DRY=0
CMD=()
PROJECTS=""
OK=0
FAIL=0
TRASHED_KB=0
EMPTIED=0

die() { echo "error: $*" >&2; exit 2; }

# ---- Safety checks -------------------------------------------------------

# True for paths that stay untouched whatever the plan says.
denied() {
  case "$1" in
    */.ssh|*/.ssh/*|*/.git|*/.git/*|*/.env|*/.env.*|*/Keychains|*/Keychains/*) return 0 ;;
    *.mobileprovision|*"/Provisioning Profiles"|*"/Provisioning Profiles/"*) return 0 ;;
    *.keystore|*.jks|*.p12|*.cer|*.pem) return 0 ;;
    */.claude.json|*/.claude/settings*|*/.claude/projects|*/.claude/projects/*|*/.codex/*|*/.cursor/*) return 0 ;;
    */Library/Mail|*/Library/Mail/*|*/Pictures/*|*/Library/Mobile\ Documents|*/Library/Mobile\ Documents/*) return 0 ;;
    /System|/System/*) return 0 ;;
  esac
  return 1
}

# The Claude Code folders whose old entries a prune row may move.
claude_junk_dir() {
  case "$1" in
    "$HOME/.claude/debug"|"$HOME/.claude/shell-snapshots"|"$HOME/.claude/statsig"|"$HOME/.claude/paste-cache") return 0 ;;
  esac
  return 1
}

# True for the only locations a plain trash row may touch.
allowed_location() {
  case "$1" in
    "$HOME/Library/Developer/Xcode/DerivedData") return 0 ;;
    "$HOME/Library/Developer/Xcode/Archives/"*|"$HOME/Library/Developer/Xcode/iOS DeviceSupport/"*) return 0 ;;
    "$HOME/.gradle/caches/"*|"$HOME/.gradle/wrapper/dists/"*) return 0 ;;
    "$HOME/Downloads/"*) return 0 ;;
    "$HOME/.nvm/versions/"*|"$HOME/.pyenv/versions/"*) return 0 ;;
    "$HOME/Library/Application Support/MobileSync/Backup/"*) return 0 ;;
  esac
  return 1
}

# Prints a free path in ~/.Trash for name $1; never an existing one.
trash_dest() {
  local dest="$HOME/.Trash/$1" n=1 ts
  ts=$(date +%Y%m%d-%H%M%S)
  while [ -e "$dest" ] || [ -L "$dest" ]; do
    dest="$HOME/.Trash/$1 $ts-$n"
    n=$((n + 1))
  done
  echo "$dest"
}

# ~/.Trash lives on the home volume. A move from another volume copies the data
# onto a disk that may be full, so such paths are refused.
same_volume() { [ "$(stat -f %d "$1" 2>/dev/null)" = "$(stat -f %d "$HOME" 2>/dev/null)" ]; }

# Moves $1 to the Trash, as name $3 when given. Mode "location" limits it to
# allowed_location; mode "any" is for project artifacts, whose own checks run
# first. Prints the result.
trash_path() {
  local p="$1" mode="$2" name="${3:-${1##*/}}" dest
  case "$p" in /*) ;; *) echo "refused: not an absolute path"; return 1 ;; esac
  case "$p" in */../*|*/..) echo "refused: path contains .."; return 1 ;; esac
  [ -e "$p" ] || [ -L "$p" ] || { echo "missing"; return 1; }
  [ -L "$p" ] && { echo "refused: symbolic link"; return 1; }
  if denied "$p"; then echo "refused: protected path"; return 1; fi
  if [ "$mode" = location ] && ! allowed_location "$p"; then echo "refused: outside the cleanup locations"; return 1; fi
  same_volume "$p" || { echo "refused: on another volume; delete it in Finder"; return 1; }
  if [ "$DRY" = 1 ]; then echo "would move to Trash"; return 0; fi
  mkdir -p "$HOME/.Trash" || { echo "failed: cannot create ~/.Trash"; return 1; }
  dest=$(trash_dest "$name")
  mv "$p" "$dest" 2>/dev/null || { echo "failed: could not move to Trash"; return 1; }
  echo "moved to Trash as ${dest##*/}"
}

# ---- Actions -------------------------------------------------------------

# Sets CMD to the official command for key $1. Fails on an unknown key or a bad name.
build_cmd() {
  local key="$1" arg tool
  CMD=()
  case "$key" in
    simctl-unavailable) CMD=(xcrun simctl delete unavailable) ;;
    npm-cache) CMD=(npm cache clean --force) ;;
    pnpm-prune) CMD=(pnpm store prune) ;;
    brew-cleanup) CMD=(brew cleanup --prune=all) ;;
    docker-prune) CMD=(docker system prune -f) ;;
    docker-volumes) CMD=(docker volume prune -f) ;;
    pod-cache) CMD=(pod cache clean --all) ;;
    empty-trash) CMD=(osascript -e 'tell application "Finder" to empty the trash') ;;
    runtime:*)
      arg=${key#runtime:}
      printf '%s' "$arg" | grep -Eq '^[0-9A-Fa-f]{8}(-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}$' || return 1
      CMD=(xcrun simctl runtime delete "$arg") ;;
    avd:*)
      arg=${key#avd:}
      printf '%s' "$arg" | grep -Eq '^[A-Za-z0-9._-]+$' || return 1
      tool=$(find_tool avdmanager) || return 1
      CMD=("$tool" delete avd -n "$arg") ;;
    sdk:*)
      arg=${key#sdk:}
      printf '%s' "$arg" | grep -Eq '^[A-Za-z0-9._;-]+$' || return 1
      tool=$(find_tool sdkmanager) || return 1
      CMD=("$tool" --uninstall "$arg") ;;
    *) return 1 ;;
  esac
}

do_cmd() {
  local out
  build_cmd "$1" || { echo "refused: unknown command or invalid name"; return 1; }
  have "${CMD[0]}" || [ -x "${CMD[0]}" ] || { echo "skipped: ${CMD[0]} not installed"; return 1; }
  if [ "$DRY" = 1 ]; then echo "would run: ${CMD[*]}"; return 0; fi
  out=$("${CMD[@]}" 2>&1) || { echo "failed: ${CMD[*]}: $(printf '%s' "$out" | tail -n 1)"; return 1; }
  echo "ran: ${CMD[*]}"
}

# Moves the entries of a Claude junk dir that are older than a day into one Trash folder.
do_prune() {
  local d="$1" e dest n=0
  claude_junk_dir "$d" || { echo "refused: not a Claude junk folder"; return 1; }
  [ -d "$d" ] && [ ! -L "$d" ] || { echo "missing"; return 1; }
  if [ "$DRY" = 1 ]; then echo "would move $(old_entries "$d" | wc -l | tr -d ' ') old entries to Trash"; return 0; fi
  mkdir -p "$HOME/.Trash" || { echo "failed: cannot create ~/.Trash"; return 1; }
  dest=$(trash_dest "claude-${d##*/}")
  mkdir "$dest" || { echo "failed: cannot create $dest"; return 1; }
  while IFS= read -r e; do
    mv "$e" "$dest/" 2>/dev/null && n=$((n + 1))
  done < <(old_entries "$d")
  echo "moved $n old entries to Trash as ${dest##*/}"
}

# A build artifact goes only when every check still holds at deletion time.
do_artifact() {
  local art="$1" proj="$2" reason rel
  case "$art" in "$proj"/*) ;; *) echo "refused: not inside the project"; return 1 ;; esac
  is_artifact_name "${art##*/}" || { echo "refused: not an artifact name"; return 1; }
  [ -d "$art" ] || { echo "missing"; return 1; }
  marker_ok "${art##*/}" "${art%/*}" || { echo "refused: no marker file beside it"; return 1; }
  artifact_tracked "$art" && { echo "refused: tracked by git"; return 1; }
  artifact_in_project "$art" "$proj" || { echo "refused: belongs to a nested repo or worktree"; return 1; }
  if reason=$(in_progress "$proj"); then echo "refused: project in progress ($reason)"; return 1; fi
  rel=${art#"$proj"/}
  trash_path "$art" any "${proj##*/} ${rel//\//-}"
}

do_worktree() {
  local wt="$1" proj="$2" out reason
  [ -d "$wt" ] || { echo "missing"; return 1; }
  reason=$(worktree_removable "$wt") || { echo "refused: $reason"; return 1; }
  if [ "$DRY" = 1 ]; then echo "would run: git worktree remove"; return 0; fi
  out=$(git -C "$proj" worktree remove "$wt" 2>&1) || { echo "failed: $(printf '%s' "$out" | tail -n 1)"; return 1; }
  echo "removed worktree"
}

# ---- Selection -----------------------------------------------------------

# Prints the --project value that names project $1; fails when none does.
project_selected() {
  local want
  while IFS= read -r want; do
    [ -n "$want" ] || continue
    case "$(expand_tilde "${want%/}")" in
      /*) [ "$(expand_tilde "${want%/}")" = "$1" ] && { echo "$want"; return 0; } ;;
      *) [ "${want%/}" = "${1##*/}" ] && { echo "$want"; return 0; } ;;
    esac
  done <<EOF
$PROJECTS
EOF
  return 1
}

# Runs one chosen row and records its outcome.
run_row() { # id kb label action target project
  local id="$1" kb="$2" label="$3" action="$4" target="$5" project="$6" msg rc
  case "$action" in
    cmd) msg=$(do_cmd "$target") ;;
    trash) msg=$(trash_path "$target" location) ;;
    prune) msg=$(do_prune "$target") ;;
    artifact) msg=$(do_artifact "$target" "$project") ;;
    worktree) msg=$(do_worktree "$target" "$project") ;;
    *) msg="refused: unknown action $action"; false ;;
  esac
  rc=$?
  echo "[$id] $label -> $msg"
  if [ "$rc" = 0 ]; then
    OK=$((OK + 1))
    case "$action" in trash|prune|artifact) TRASHED_KB=$((TRASHED_KB + kb)) ;; esac
    [ "$target" = empty-trash ] && [ "$DRY" = 0 ] && EMPTIED=1
  else
    FAIL=$((FAIL + 1))
  fi
  [ "$DRY" = 1 ] || log_action "$action" "$target" "$msg"
}

# ---- Subcommands ---------------------------------------------------------

cmd_preflight() {
  local app busy=""
  for app in ${DEV_CLEANUP_APPS:-Xcode Simulator studio Cursor}; do
    pgrep -x "$app" >/dev/null 2>&1 && busy="$busy $app"
  done
  if [ -n "$busy" ]; then
    echo "Still running:$busy. Quit these apps, then rerun preflight."
    return 1
  fi
  echo "ok: no blocking apps running"
}

cmd_stop_gradle() {
  if pkill -f '[G]radleDaemon' 2>/dev/null; then echo "stopped Gradle daemons"; else echo "no Gradle daemons running"; fi
}

cmd_run() {
  local plan="" ids="" tiers="" id kb label action target project tier want count
  local by_id by_tier matched="" named="" deferred=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --plan) plan="$2"; shift 2 ;;
      --dry-run) DRY=1; shift ;;
      --tier)
        case "$2" in safe|old) tiers="$tiers $2" ;; *) die "--tier accepts safe or old; name ask-first rows by id" ;; esac
        shift 2 ;;
      --project) [ -n "$2" ] || die "--project needs a path"; PROJECTS="$PROJECTS$2"$'\n'; shift 2 ;;
      -*) die "unknown option: $1" ;;
      *) case "$1" in *[!0-9,]*) die "ids are numbers: $1" ;; esac; ids="$ids,$1"; shift ;;
    esac
  done
  [ -n "$plan" ] && [ -f "$plan" ] || die "--plan FILE is required (run scan.sh first)"
  [ -n "$ids$tiers$PROJECTS" ] || die "nothing selected: pass ids, --tier, or --project"

  # A bare folder name must point at exactly one project in the plan.
  while IFS= read -r want; do
    case "$want" in ""|/*|"~"*) continue ;; esac
    count=$(awk -F'\t' -v n="${want%/}" '$5 == "artifact" { k = $7; sub(/.*\//, "", k); if (k == n) seen[$7] = 1 }
      END { c = 0; for (p in seen) c++; print c }' "$plan")
    [ "$count" -gt 1 ] && die "--project $want matches $count projects; pass the full path"
  done <<EOF
$PROJECTS
EOF

  while IFS="$TAB" read -r tier id kb label action target project <&3; do
    by_id=0; case ",$ids," in *",$id,"*) by_id=1; matched="$matched,$id" ;; esac
    by_tier=0; case " $tiers " in *" $tier "*) by_tier=1 ;; esac

    case "$action" in
      none)
        [ "$by_id" = 1 ] && echo "[$id] skipped: report only. $label"
        continue ;;
      artifact)
        if ! want=$(project_selected "$project"); then
          [ "$by_id" = 1 ] && echo "[$id] skipped: build artifacts go only with --project <name the user gave>"
          continue
        fi
        named="$named$want"$'\n' ;;
      *) [ "$by_id" = 1 ] || [ "$by_tier" = 1 ] || continue ;;
    esac

    # Emptying the Trash waits until everything else has moved there.
    if [ "$action" = cmd ] && [ "$target" = empty-trash ]; then
      deferred="$id$TAB$kb$TAB$label"
      continue
    fi
    run_row "$id" "$kb" "$label" "$action" "$target" "$project"
  done 3< "$plan"

  if [ -n "$deferred" ]; then
    IFS="$TAB" read -r id kb label <<EOF
$deferred
EOF
    run_row "$id" "$kb" "$label" cmd empty-trash -
  fi

  for id in $(printf '%s' "$ids" | tr ',' ' '); do
    case "$matched," in *",$id,"*) ;; *) echo "[$id] not in the plan"; FAIL=$((FAIL + 1)) ;; esac
  done
  while IFS= read -r want; do
    [ -n "$want" ] || continue
    printf '%s' "$named" | grep -Fxq -- "$want" ||
      echo "--project $want: no build artifacts in the plan (in progress, unknown, or none)"
  done <<EOF
$PROJECTS
EOF

  echo "done: $OK ok, $FAIL not done$([ "$DRY" = 1 ] && echo ' (dry run)')"
  if [ "$TRASHED_KB" -gt 0 ]; then
    if [ "$EMPTIED" = 1 ]; then
      echo "moved to Trash: $(human_kb "$TRASHED_KB"), then the Trash was emptied"
    else
      echo "$([ "$DRY" = 1 ] && echo 'would move' || echo 'moved') to Trash: $(human_kb "$TRASHED_KB"). The disk frees it once the Trash is emptied."
    fi
  fi
  [ "$FAIL" = 0 ]
}

sub="$1"; shift
case "$sub" in
  preflight) cmd_preflight ;;
  stop-gradle) cmd_stop_gradle ;;
  run) cmd_run "$@" ;;
  -h|--help|"") sed -n '2,19p' "$0" ;;
  *) die "unknown subcommand: $sub" ;;
esac
