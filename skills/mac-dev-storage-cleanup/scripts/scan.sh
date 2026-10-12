#!/bin/bash
# Read-only scan for the mac-dev-storage-cleanup skill.
#
# Usage: scan.sh [--roots a:b] [--out FILE] | --print-roots
#
# Prints a size report by tier and writes the plan to FILE (default
# $TMPDIR/dev-cleanup-plan.tsv) for clean.sh. It changes nothing else.
# Plan columns (tab separated, none empty): tier id kb label action target project
#   tier   safe | old | ask | report
#   action cmd (target = command key) | trash | prune (old entries of a dir) |
#          artifact | worktree | none
#   kb     0 means the size is unknown or the item is informational
#   project  repo path for artifact and worktree rows, else "-"

DIR=$(cd "$(dirname "$0")" && pwd)
. "$DIR/lib.sh"

OUT="${TMPDIR:-/tmp}"; OUT="${OUT%/}/dev-cleanup-plan.tsv"
ROOTS_ARG=""
MODE=scan
while [ $# -gt 0 ]; do
  case "$1" in
    --roots) ROOTS_ARG="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --print-roots) MODE=roots; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

ROOTS=$(resolve_roots "$ROOTS_ARG")
if [ "$MODE" = roots ]; then
  [ -n "$ROOTS" ] && printf '%s\n' "$ROOTS"
  exit 0
fi

: > "$OUT" || { echo "cannot write $OUT" >&2; exit 1; }
N=0

emit() { # tier kb label action target [project]
  local tier="$1" kb="$2" label="$3" action="$4" target="$5" project="${6:--}"
  case "$target$label" in *"$TAB"*|*$'\n'*) return 0 ;; esac
  N=$((N + 1))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$tier" "$N" "$kb" "$label" "$action" "$target" "$project" >> "$OUT"
}

# A path that moves to the Trash when chosen; skipped when missing or empty.
emit_dir() { # tier label path
  local kb
  [ -e "$3" ] || return 0
  kb=$(kb_of "$3")
  [ "$kb" -gt 0 ] || return 0
  emit "$1" "$kb" "$2" trash "$3"
}

# Dotted-version helpers for awk: cmp(a,b) is 1, 0, or -1.
AWK_CMP='function cmp(a,b,  x,y,n,m,i){n=split(a,x,".");m=split(b,y,".");if(m>n)n=m;
  for(i=1;i<=n;i++){if(x[i]+0>y[i]+0)return 1;if(x[i]+0<y[i]+0)return -1}return 0}'

scan_claude_junk() {
  local n d e kb
  for n in debug shell-snapshots statsig paste-cache; do
    d="$HOME/.claude/$n"
    [ -d "$d" ] || continue
    kb=0
    while IFS= read -r e; do kb=$((kb + $(kb_of "$e"))); done < <(old_entries "$d")
    [ "$kb" -gt 0 ] && emit safe "$kb" "Claude junk older than a day: ~/.claude/$n" prune "$d"
  done
  return 0
}

# A cache cleared by an official command; skipped when its folder is missing or empty.
emit_cache() { # label command-key path
  local kb
  [ -d "$3" ] || return 0
  kb=$(kb_of "$3")
  [ "$kb" -gt 0 ] && emit safe "$kb" "$1" cmd "$2"
}

scan_caches() {
  local p
  emit_dir safe "Xcode DerivedData (rebuilds on the next build)" "$HOME/Library/Developer/Xcode/DerivedData"
  have npm && emit_cache "npm cache" npm-cache "$HOME/.npm"
  if have pnpm; then
    p=$(pnpm store path 2>/dev/null)
    [ -n "$p" ] && emit_cache "pnpm store (upper bound: prune removes unreferenced packages only)" pnpm-prune "$p"
  fi
  if have brew; then
    p=$(brew --cache 2>/dev/null)
    [ -n "$p" ] && emit_cache "Homebrew downloads (upper bound: cleanup also removes old versions)" brew-cleanup "$p"
  fi
  have pod && emit_cache "CocoaPods cache" pod-cache "$HOME/Library/Caches/CocoaPods"
  return 0
}

scan_simulators() {
  local u total=0 count=0 platform ver uuid
  have xcrun || return 0
  while IFS= read -r u; do
    total=$((total + $(kb_of "$HOME/Library/Developer/CoreSimulator/Devices/$u")))
    count=$((count + 1))
  done < <(xcrun simctl list devices unavailable 2>/dev/null |
    grep -Eo '[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}' | sort -u)
  [ "$count" -gt 0 ] && emit safe "$total" "$count unavailable simulator device(s)" cmd simctl-unavailable

  # A runtime is outdated when a newer one of the same platform and major
  # version is installed; the only iOS 18 runtime stays beside iOS 26.
  # Sizes are not exposed.
  while IFS="$TAB" read -r platform ver uuid; do
    emit old 0 "Simulator runtime $platform $ver (size unknown; a newer $platform ${ver%%.*}.x is installed)" cmd "runtime:$uuid"
  done < <(xcrun simctl runtime list 2>/dev/null | awk "$AWK_CMP"'
    /^(iOS|watchOS|tvOS|visionOS) [0-9]/ {
      uuid = ""
      for (i = 3; i <= NF; i++)
        if (length($i) == 36 && $i ~ /^[0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9A-Fa-f]+$/) uuid = $i
      if (uuid == "" || seen[uuid]++) next
      split($2, v, "."); key = $1 " " v[1]
      n++; group[n] = key; plat[n] = $1; ver[n] = $2; id[n] = uuid
      if (!(key in top) || cmp($2, top[key]) > 0) top[key] = $2
    }
    END { for (i = 1; i <= n; i++) if (cmp(ver[i], top[group[i]]) < 0) print plat[i] "\t" ver[i] "\t" id[i] }')
}

scan_xcode() {
  local d name kb a bid ver plist
  local base="$HOME/Library/Developer/Xcode"

  # DeviceSupport: keep the newest 2 always; the rest only when older than 90 days.
  if [ -d "$base/iOS DeviceSupport" ]; then
    while IFS= read -r name; do
      d="$base/iOS DeviceSupport/$name"
      [ "$(age_days "$d")" -gt 90 ] && emit_dir old "iOS DeviceSupport $name (older than 90 days)" "$d"
    done < <(ls -1t "$base/iOS DeviceSupport" 2>/dev/null | sed 1,2d)
  fi

  # Archives: per app, keep the newest archive of the newest CFBundleShortVersionString.
  [ -x /usr/libexec/PlistBuddy ] || return 0
  local rows
  rows=$(mktemp "${TMPDIR:-/tmp}/dev-cleanup-archives.XXXXXX") || return 0
  for a in "$base"/Archives/*/*.xcarchive; do
    [ -d "$a" ] || continue
    plist="$a/Info.plist"
    bid=$(/usr/libexec/PlistBuddy -c 'Print :ApplicationProperties:CFBundleIdentifier' "$plist" 2>/dev/null)
    ver=$(/usr/libexec/PlistBuddy -c 'Print :ApplicationProperties:CFBundleShortVersionString' "$plist" 2>/dev/null)
    [ -n "$bid" ] && [ -n "$ver" ] || continue
    printf '%s\t%s\t%s\t%s\n' "$bid" "$ver" "$(mtime_of "$a")" "$a" >> "$rows"
  done
  while IFS="$TAB" read -r ver a; do
    kb=$(kb_of "$a")
    emit ask "$kb" "Xcode archive $(basename "$a" .xcarchive) v$ver (superseded; its dSYMs for crash reports go with it)" trash "$a"
  done < <(awk -F'\t' "$AWK_CMP"'
    FNR == 1 { pass++ }
    pass == 1 { if (!($1 in top) || cmp($2, top[$1]) > 0) top[$1] = $2 }
    pass == 2 && cmp($2, top[$1]) == 0 { if (!($1 in mt) || $3 + 0 > mt[$1] + 0) { mt[$1] = $3; keep[$1] = $4 } }
    pass == 3 && $4 != keep[$1] { print $2 "\t" $4 }' "$rows" "$rows" "$rows")
  rm -f "$rows"
}

# True when nothing in the top levels of $1 changed in 30 days. A build
# rewrites files inside caches/<version>; the folder's own date stays put.
gradle_idle() { [ -z "$(find "$1" -maxdepth 3 -mtime -30 2>/dev/null | head -n 1)" ]; }

scan_gradle() {
  local d ver
  for d in "$HOME"/.gradle/caches/[0-9]*; do
    [ -d "$d" ] && gradle_idle "$d" &&
      emit_dir old "Gradle ${d##*/} caches unused 30+ days (rebuild when needed)" "$d"
  done
  # A wrapper distribution is in use while its version's caches are.
  for d in "$HOME"/.gradle/wrapper/dists/gradle-*; do
    [ -d "$d" ] || continue
    ver=${d##*/gradle-}; ver=${ver%-bin}; ver=${ver%-all}
    gradle_idle "$d" || continue
    [ -d "$HOME/.gradle/caches/$ver" ] && ! gradle_idle "$HOME/.gradle/caches/$ver" && continue
    emit_dir old "Gradle $ver distribution unused 30+ days (re-downloads when needed)" "$d"
  done
  return 0
}

scan_downloads() {
  local f
  while IFS= read -r f; do
    emit_dir old "Download older than 30 days: ${f##*/}" "$f"
  done < <(find "$HOME/Downloads" -maxdepth 1 -type f -mtime +30 \( -iname '*.dmg' -o -iname '*.pkg' \
    -o -iname '*.zip' -o -iname '*.tar.gz' -o -iname '*.tgz' -o -iname '*.xip' -o -iname '*.ipa' -o -iname '*.apk' \) 2>/dev/null)
}

scan_android() {
  local sdk="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}"
  local avdhome="${ANDROID_AVD_HOME:-$HOME/.android/avd}"
  local d name pkg avdm sdkm
  avdm=$(find_tool avdmanager) || avdm=""
  sdkm=$(find_tool sdkmanager) || sdkm=""

  for d in "$avdhome"/*.avd; do
    [ -d "$d" ] || continue
    name=$(basename "$d" .avd)
    if [ -n "$avdm" ]; then
      emit ask "$(kb_of "$d")" "Android emulator (AVD) $name" cmd "avd:$name"
    else
      emit report "$(kb_of "$d")" "Android emulator (AVD) $name (avdmanager not found)" none "$d"
    fi
  done

  [ -d "$sdk" ] || return 0
  # One row per installed package; the package id is the directory path with ';' separators.
  for d in "$sdk"/platforms/android-* "$sdk"/build-tools/* "$sdk"/ndk/* "$sdk"/system-images/*/*/*; do
    [ -d "$d" ] || continue
    pkg=${d#"$sdk"/}; pkg=$(printf '%s' "$pkg" | tr '/' ';')
    case "$pkg" in *[!A-Za-z0-9._\;-]*) continue ;; esac
    if [ -n "$sdkm" ]; then
      emit ask "$(kb_of "$d")" "Android SDK package $pkg" cmd "sdk:$pkg"
    else
      emit report "$(kb_of "$d")" "Android SDK package $pkg (sdkmanager not found)" none "$d"
    fi
  done
}

scan_version_managers() {
  local d
  for d in "$HOME"/.nvm/versions/node/* "$HOME"/.pyenv/versions/*; do
    [ -d "$d" ] || continue
    case "$d" in
      */.nvm/*) emit_dir ask "Node version ${d##*/} (nvm)" "$d" ;;
      *) emit_dir ask "Python version ${d##*/} (pyenv)" "$d" ;;
    esac
  done
}

scan_docker() {
  local count
  have docker && docker info >/dev/null 2>&1 || return 0
  # Stopped containers can hold data in their own layer, so this is ask-first.
  emit ask 0 "Docker prune: stopped containers, dangling images, unused networks, build cache (volumes stay; size unknown, see docker system df)" cmd docker-prune
  count=$(docker volume ls -q -f dangling=true 2>/dev/null | wc -l | tr -d ' ')
  [ "$count" -gt 0 ] &&
    emit ask 0 "$count Docker volume(s) no container uses. Their data is lost (size unknown)" cmd docker-volumes
  return 0
}

scan_user_data() {
  local d
  for d in "$HOME/Library/Application Support/MobileSync/Backup"/*; do
    emit_dir ask "iOS device backup ${d##*/}" "$d"
  done
  if [ -d "$HOME/.Trash" ] && [ "$(kb_of "$HOME/.Trash")" -gt 0 ]; then
    emit ask "$(kb_of "$HOME/.Trash")" "Empty the Trash, including what this run moves there (permanent)" cmd empty-trash
  fi
}

scan_chat_history() {
  local f="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
  [ -d "$HOME/.claude/projects" ] &&
    emit report "$(kb_of "$HOME/.claude/projects")" "Claude chat history: set cleanupPeriodDays in ~/.claude/settings.json" none "$HOME/.claude/projects"
  [ -d "$HOME/.codex/sessions" ] &&
    emit report "$(kb_of "$HOME/.codex/sessions")" "Codex sessions: no built-in cleanup; ask the user before touching" none "$HOME/.codex/sessions"
  [ -f "$f" ] &&
    emit report "$(kb_of "$f")" "Cursor chat store: use Delete Old Chats and GC Agent KV Blobs in Cursor" none "$f"
  return 0
}

scan_projects() {
  local p a w reason list
  [ -n "$ROOTS" ] || return 0
  list=$(mktemp "${TMPDIR:-/tmp}/dev-cleanup-projects.XXXXXX") || return 0
  printf '%s\n' "$ROOTS" | list_projects > "$list"
  while IFS= read -r p <&3; do
    # Agent worktrees: offer only the clean and pushed ones.
    while IFS= read -r w <&4; do
      [ -d "$w" ] || continue
      if reason=$(worktree_removable "$w"); then
        emit ask "$(kb_of "$w")" "Git worktree $(tilde "$w") (clean, pushed, last commit $(git -C "$w" log -1 --format=%cr 2>/dev/null))" worktree "$w" "$p"
      else
        emit report "$(kb_of "$w")" "Git worktree $(tilde "$w") (kept: $reason)" none "$w"
      fi
    done 4< <(git -C "$p" worktree list --porcelain 2>/dev/null | awk '/^worktree /{n++; if (n > 1) {sub(/^worktree /, ""); print}}')

    if reason=$(in_progress "$p"); then
      emit report 0 "In progress, kept: $(tilde "$p") ($reason)" none "$p"
      continue
    fi
    while IFS= read -r a <&4; do
      emit report "$(kb_of "$a")" "Build artifact $(tilde "$a")" artifact "$a" "$p"
    done 4< <(list_artifacts "$p")
  done 3< "$list"
  rm -f "$list"
}

render() {
  local t title rows total
  echo "Project roots: $([ -n "$ROOTS" ] && printf '%s' "$ROOTS" | tr '\n' ' ' || echo 'none found; ask the user for their projects folder and rerun with --roots')"
  for t in safe old ask report; do
    case "$t" in
      safe) title="SAFE (caches and junk that regenerate)" ;;
      old) title="OLD-ONLY (past the age threshold)" ;;
      ask) title="ASK FIRST (name each id)" ;;
      report) title="REPORT ONLY (nothing here is deleted without a named project)" ;;
    esac
    rows=$(awk -F'\t' -v t="$t" '$1 == t' "$OUT" | sort -t "$TAB" -k3,3nr)
    [ -n "$rows" ] || continue
    total=$(printf '%s\n' "$rows" | awk -F'\t' '{s += $3} END {print s + 0}')
    printf '\n== %s: %s listed, %s ==\n' "$title" "$(printf '%s\n' "$rows" | wc -l | tr -d ' ')" "$(human_kb "$total")"
    printf '%s\n' "$rows" | awk -F'\t' '
      function hsize(k) { if (k >= 1048576) return sprintf("%.1f GB", k / 1048576); if (k >= 1024) return sprintf("%.0f MB", k / 1024); return (k > 0 ? k " KB" : "-") }
      { printf "  [%s] %9s  %s\n", $2, hsize($3), $4 }'
  done
  printf '\nPlan file: %s\n' "$OUT"
}

scan_claude_junk
scan_caches
scan_simulators
scan_xcode
scan_gradle
scan_downloads
scan_android
scan_version_managers
scan_docker
scan_user_data
scan_chat_history
scan_projects
render
