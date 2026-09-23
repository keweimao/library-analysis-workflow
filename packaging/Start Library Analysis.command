#!/bin/bash
cd "$(dirname "$0")" || exit 1
export PYTHONUTF8=1
for candidate in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(not ((3,12) <= sys.version_info < (3,15)))' 2>/dev/null; then
    "$candidate" launcher.py
    result=$?
    if [ "$result" -ne 0 ]; then read -r -p "Press Return to close..."; fi
    exit "$result"
  fi
done
echo "Python 3.12-3.14 is required. Install from https://www.python.org/downloads/macos/ and run this file again."
open https://www.python.org/downloads/macos/
read -r -p "Press Return to close..."
