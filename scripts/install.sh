#!/usr/bin/env bash
set -euo pipefail
TARGET_DIR=${1:-/opt/outlook-kb-autoresponder}
mkdir -p "$TARGET_DIR"
cp -a . "$TARGET_DIR/"
cd "$TARGET_DIR"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
mkdir -p logs data
printf 'Installed to %s\n' "$TARGET_DIR"
printf 'Next: copy .env.example to .env and configure your mailbox credentials.\n'
