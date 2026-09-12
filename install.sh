#!/usr/bin/env bash
# Install the CFEA skills + cfea-test-lock hook into a target repo (project-
# scoped) or into ~/.claude (user-scoped, applies to every repo).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "Usage:"
  echo "  $0 <target-repo-path>   # project-scoped install (<repo>/.claude/)"
  echo "  $0 --user               # user-scoped install (~/.claude/)"
  exit 1
}

[ $# -ge 1 ] || usage

if [ "$1" == "--user" ]; then
  CLAUDE_DIR="$HOME/.claude"
else
  TARGET="$1"
  [ -d "$TARGET" ] || { echo "Target repo not found: $TARGET"; exit 1; }
  CLAUDE_DIR="$TARGET/.claude"
fi

SKILLS_DEST="$CLAUDE_DIR/skills"
HOOKS_DEST="$CLAUDE_DIR/hooks"
SETTINGS="$CLAUDE_DIR/settings.json"

mkdir -p "$SKILLS_DEST" "$HOOKS_DEST"

for skill in "$SCRIPT_DIR"/skills/cfea-*; do
  name="$(basename "$skill")"
  rm -rf "${SKILLS_DEST:?}/$name"
  cp -R "$skill" "$SKILLS_DEST/$name"
  echo "installed skill: $name"
done

rm -rf "${HOOKS_DEST:?}/cfea-test-lock"
cp -R "$SCRIPT_DIR/hooks/cfea-test-lock" "$HOOKS_DEST/cfea-test-lock"
echo "installed hook: cfea-test-lock"

python3 "$SCRIPT_DIR/install/merge_settings.py" "$SETTINGS" "$SCRIPT_DIR/hooks/cfea-test-lock/settings.snippet.json"
echo "merged hook config into $SETTINGS"

echo
echo "Done. Next: open the target repo in Claude Code and run the cfea-bootstrap skill."
