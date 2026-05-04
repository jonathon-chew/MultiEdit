#!/usr/bin/env bash

# base script running
# run the main file, ignoring file updates in the venv and .git
python3 -m hotrun --file src/MultiEdit/__main__.py --python MultiEdit_venv/bin/python3.14 --arguments --before example --after eg --dry-run -i MultiEdit_venv .git hotrun.sh --ignore MultiEdit_venv .git
