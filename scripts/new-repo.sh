#!/usr/bin/env bash
# Scaffold the standard agent-context files for a new ACTIVE workspace repo, so
# every project joins the ~/workdir/repos AGENTS hierarchy consistently.
#
# Usage:  new-repo.sh <dir>        # dir relative to $PWD (create it if absent)
# Example (from ~/workdir/repos):  ~/workdir/repos/config/scripts/new-repo.sh myapp
set -euo pipefail

name="${1:?usage: new-repo.sh <dir>}"
tmpl_dir="$(cd "$(dirname "$0")/../templates" && pwd)"
base="$(basename "$name")"

mkdir -p "$name"
for f in AGENTS.md CLAUDE.md; do
  if [[ -e "$name/$f" ]]; then
    echo "skip  $name/$f (already exists)"
    continue
  fi
  sed "s/{{NAME}}/$base/g" "$tmpl_dir/$f.tmpl" > "$name/$f"
  echo "wrote $name/$f"
done

# Seed the standard docs/ structure (see repos/docs/repo-docs-standardization.md):
# docs/README.md = current status + index; docs/decisions/ = verbatim decision notes.
mkdir -p "$name/docs/decisions"
if [[ -e "$name/docs/README.md" ]]; then
  echo "skip  $name/docs/README.md (already exists)"
else
  sed "s/{{NAME}}/$base/g" "$tmpl_dir/docs-README.md.tmpl" > "$name/docs/README.md"
  echo "wrote $name/docs/README.md"
fi
if [[ -e "$name/docs/decisions/TEMPLATE.md" ]]; then
  echo "skip  $name/docs/decisions/TEMPLATE.md (already exists)"
else
  cp "$tmpl_dir/decision.md.tmpl" "$name/docs/decisions/TEMPLATE.md"
  echo "wrote $name/docs/decisions/TEMPLATE.md"
fi

cat <<NOTE

Done. Now wire it into the workspace meta-repo (~/workdir/repos):
  1. add  /$base/  to  repos/.gitignore   (it's an independent repo, gitignored)
  2. add a row for it to the Active table in  repos/AGENTS.md
  3. fill in  $name/AGENTS.md  (overview, commands, conventions)
NOTE
