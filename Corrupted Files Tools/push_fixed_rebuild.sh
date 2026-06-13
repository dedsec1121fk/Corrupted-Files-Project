#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python "Corrupted Files Tools/generate_snapshot_cards.py" --apply
python "Corrupted Files Tools/repair_paths.py" --apply
python "Corrupted Files Tools/rebuild_indexes.py"
python "Corrupted Files Tools/generate_visual_indexes.py"
python "Corrupted Files Tools/validate_rebuilt_structure.py"
python "Corrupted Files Tools/validate_event_image_attribution.py"
python "Corrupted Files Tools/run_tests.py"

if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "Git identity is not configured for this repository."
  echo 'Run: git config user.name "Your Name"'
  echo 'Run: git config user.email "you@example.com"'
  exit 1
fi

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Repair archive paths and improve offline reader"
fi
git push
