#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git dnsutils build-essential libxml2-dev libxslt1-dev pkg-config ruby-full golang-go
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p data/reports
[ -f .env ] || cp .env.example .env
echo "OSINThub Python environment installed."
echo "Optional integrations have separate installation instructions in INSTALLATION.md."
echo "Run: source .venv/bin/activate && python run.py"
