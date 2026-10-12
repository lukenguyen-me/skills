#!/bin/bash
# Shared helpers for scan.sh and clean.sh. Source this file; do not run it.
# Targets macOS /bin/bash 3.2 and the BSD userland: no associative arrays,
# mapfile, GNU flags, or `set -u` with arrays.

# Directory names treated as regenerable build output. Each one is removable
# only beside its marker file (see marker_ok).
ARTIFACT_NAMES="node_modules .next .nuxt dist build Pods .build .gradle .venv"
ACTIVE_DAYS=14
TAB=$(printf '\t')
LOG_FILE="$HOME/Library/Logs/dev-cleanup.log"

# find(1) arguments that match .git and every artifact name; wrap in \( \).
PRUNE_ARGS=(-name .git)
for _n in $ARTIFACT_NAMES; do PRUNE_ARGS+=(-o -name "$_n"); done

have() { command -v "$1" >/dev/null 2>&1; }

# Disk use of a path in KB; 0 when missing.
kb_of() { du -sk "$1" 2>/dev/null | awk '{k=$1} END {print k+0}'; }

mtime_of() { stat -f %m "$1" 2>/dev/null || echo 0; }

age_days() { echo $(( ($(date +%s) - $(mtime_of "$1")) / 86400 )); }

expand_tilde() {
  case "$1" in
    "~") echo "$HOME" ;;
    "~/"*) echo "$HOME/${1#\~/}" ;;
    *) echo "$1" ;;
  esac
}

tilde() {
  case "$1" in
    "$HOME"/*) printf '~%s' "${1#"$HOME"}" ;;
    *) printf '%s' "$1" ;;
  esac
}

human_kb() {
  awk -v k="$1" 'BEGIN { if (k >= 1048576) printf "%.1f GB", k / 1048576; else if (k >= 1024) printf "%.0f MB", k / 1024; else printf "%d KB", k }'
}

# Prints the existing project roots as absolute paths, one per line: the given
# colon-separated list, else $PROJECTS_ROOT, else the common folders.
resolve_roots() {
  local list="${1:-$PROJECTS_ROOT}" r
  local -a parts
  if [ -n "$list" ]; then
    IFS=: read -r -a parts <<< "$list"
  else
    parts=("$HOME/Developer" "$HOME/Projects" "$HOME/Code" "$HOME/src" \
      "$HOME/Documents/projects" "$HOME/Documents/Developer" "$HOME/dev" "$HOME/workspace")
  fi
  for r in "${parts[@]}"; do
    [ -n "$r" ] || continue
    r=$(expand_tilde "$r")
    r=$(cd "$r" 2>/dev/null && pwd) && echo "$r"
  done | sort -u
}

# Reads roots on stdin; prints every git repo (a .git directory) up to four levels down.
list_projects() {
  local r
  while IFS= read -r r; do
    find "$r" -maxdepth 4 \( -name node_modules -o -name Pods -o -name .build -o -name .venv \
      -o -name Library -o -name .Trash \) -prune -o -type d -name .git -print -prune 2>/dev/null
  done | sed 's|/\.git$||' | sort -u
}

is_artifact_name() {
  local n
  for n in $ARTIFACT_NAMES; do [ "$1" = "$n" ] && return 0; done
  return 1
}

# True when artifact dir name $1 sits beside a file that proves what it is.
marker_ok() {
  local name="$1" dir="$2" m
  case "$name" in
    node_modules|.next|.nuxt) set -- package.json ;;
    dist) set -- package.json pyproject.toml setup.py ;;
    build) set -- package.json build.gradle build.gradle.kts settings.gradle settings.gradle.kts CMakeLists.txt pubspec.yaml ;;
    Pods) set -- Podfile ;;
    .build) set -- Package.swift ;;
    .gradle) set -- build.gradle build.gradle.kts settings.gradle settings.gradle.kts ;;
    .venv) set -- pyproject.toml requirements.txt setup.py Pipfile ;;
    *) return 1 ;;
  esac
  for m in "$@"; do [ -f "$dir/$m" ] && return 0; done
  return 1
}

# True when artifact dir $1 is tracked by git.
artifact_tracked() {
  [ -n "$(git -C "${1%/*}" ls-files -- "${1##*/}" 2>/dev/null | head -n 1)" ]
}

# True when project $2 is the nearest repo of artifact $1. An artifact of a
# nested repo or a worktree inside the project belongs to that repo instead.
artifact_in_project() {
  local top want
  top=$(git -C "${1%/*}" rev-parse --show-toplevel 2>/dev/null) || return 1
  want=$(cd "$2" 2>/dev/null && pwd -P) || return 1
  [ "$top" = "$want" ]
}

# Prints the artifact dirs of project $1 that sit beside their marker and are untracked.
list_artifacts() {
  local a
  while IFS= read -r a; do
    [ "${a##*/}" = .git ] && continue
    marker_ok "${a##*/}" "${a%/*}" || continue
    artifact_tracked "$a" && continue
    artifact_in_project "$a" "$1" || continue
    echo "$a"
  done < <(find "$1" -maxdepth 4 -type d \( "${PRUNE_ARGS[@]}" \) -prune -print 2>/dev/null)
}

# Prints the first change in project $1 that is real work: untracked artifact
# dirs (an unignored build/) do not count.
first_dirty_line() {
  git -C "$1" status --porcelain 2>/dev/null | while IFS= read -r line; do
    case "$line" in
      "?? "*)
        base=${line#"?? "}; base=${base%/}; base=${base##*/}
        is_artifact_name "$base" && continue ;;
    esac
    echo "$line"
    break
  done
}

# Returns 0 and prints the reason when project $1 is in progress: a commit or
# file change in the last 14 days, or dirty, stashed, or unpushed git work.
in_progress() {
  local p="$1" now ct hit
  now=$(date +%s)
  ct=$(git -C "$p" log -1 --format=%ct 2>/dev/null)
  if [ -n "$ct" ] && [ $((now - ct)) -lt $((ACTIVE_DAYS * 86400)) ]; then
    echo "commit in last $ACTIVE_DAYS days"; return 0
  fi
  if [ -n "$(first_dirty_line "$p")" ]; then echo "uncommitted changes"; return 0; fi
  if [ -n "$(git -C "$p" stash list 2>/dev/null | head -n 1)" ]; then echo "stashed work"; return 0; fi
  # A repo without remotes has nothing to push.
  if [ -n "$(git -C "$p" remote 2>/dev/null | head -n 1)" ] &&
     [ -n "$(git -C "$p" log --branches --not --remotes --oneline 2>/dev/null | head -n 1)" ]; then
    echo "unpushed commits"; return 0
  fi
  hit=$(find "$p" -maxdepth 6 \( "${PRUNE_ARGS[@]}" \) -prune -o -type f -mtime -"$ACTIVE_DAYS" \
    ! -name .DS_Store -print 2>/dev/null | head -n 1)
  if [ -n "$hit" ]; then echo "files changed in last $ACTIVE_DAYS days"; return 0; fi
  return 1
}

# Prints the first untracked protected file (.env*, keys, profiles) in worktree $1.
untracked_secret() {
  local f rel
  while IFS= read -r f; do
    rel=${f#"$1"/}
    git -C "$1" ls-files --error-unmatch -- "$rel" >/dev/null 2>&1 || { echo "$rel"; return 0; }
  done < <(find "$1" \( -name .git -o -name node_modules \) -prune -o -type f \( -name '.env*' \
    -o -name '*.keystore' -o -name '*.jks' -o -name '*.p12' -o -name '*.pem' -o -name '*.mobileprovision' \) -print 2>/dev/null)
  return 1
}

# Returns 0 when worktree $1 can go: no changes, HEAD on a remote branch, and no
# untracked protected file (git worktree remove deletes ignored files for good).
# Otherwise prints why it stays.
worktree_removable() {
  local f
  if [ -n "$(git -C "$1" status --porcelain 2>/dev/null | head -n 1)" ]; then echo "uncommitted changes"; return 1; fi
  if [ -z "$(git -C "$1" branch -r --contains HEAD 2>/dev/null | head -n 1)" ]; then echo "unpushed commits"; return 1; fi
  f=$(untracked_secret "$1")
  if [ -n "$f" ]; then echo "holds untracked $f"; return 1; fi
  return 0
}

# Prints the entries of dir $1 older than a day. Claude Code sessions that are
# running keep using their newer files.
old_entries() { find "$1" -mindepth 1 -maxdepth 1 -mtime +1 2>/dev/null; }

# Prints the path of an Android SDK tool, looking on PATH and in the SDK.
find_tool() {
  local sdk="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}" t
  if have "$1"; then command -v "$1"; return 0; fi
  for t in "$sdk"/cmdline-tools/*/bin/"$1" "$sdk/tools/bin/$1"; do
    [ -x "$t" ] && { echo "$t"; return 0; }
  done
  return 1
}

log_action() { # action target result
  mkdir -p "${LOG_FILE%/*}"
  printf '%s\t%s\t%s\t%s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$1" "$2" "$3" >> "$LOG_FILE"
}
