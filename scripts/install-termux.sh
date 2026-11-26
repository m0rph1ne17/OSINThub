#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
pkg update -y
pkg install -y python git clang rust libffi openssl libxml2 libxslt pkg-config ruby golang
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p data/reports
[ -f .env ] || cp .env.example .env
echo "OSINThub Python environment installed."
echo "Optional integrations have separate installation instructions in INSTALLATION.md."
echo "Run: source .venv/bin/activate && python run.py"
