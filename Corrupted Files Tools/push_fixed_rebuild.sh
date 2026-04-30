#!/data/data/com.termux/files/usr/bin/bash
set -e
python "Corrupted Files Tools/validate_rebuilt_structure.py"
git add -A
git commit -m "Apply fully fixed Corrupted Files rebuild" || true
git push
