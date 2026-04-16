#!/bin/bash
# pfconfig.sh
# Wrapper to launch the Python-based TUI Picframe Config editor
cd "$(dirname "$0")"
python3 pfconfig.py "$@"
