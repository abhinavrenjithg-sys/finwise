#!/usr/bin/env bash
# FinWise - Smart Financial Calculator : one-click start (Linux / macOS)
# Run with:  bash run.sh
cd "$(dirname "$0")" || exit 1

PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && \
     "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    PY="$candidate"
    break
  fi
done

if [ -z "$PY" ]; then
  echo
  echo " Python 3.9 or newer was not found."
  if [ "$(uname)" = "Darwin" ]; then
    echo " Install it from https://www.python.org/downloads/ and run this again."
    open "https://www.python.org/downloads/" 2>/dev/null
  else
    echo " Ubuntu/Debian:  sudo apt install python3 python3-venv python3-pip"
    echo " Fedora:         sudo dnf install python3"
  fi
  read -r -p " Press Enter to close..." _
  exit 1
fi

"$PY" launcher.py
status=$?
if [ $status -ne 0 ]; then
  read -r -p " Press Enter to close..." _
fi
exit $status
