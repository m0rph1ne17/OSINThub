#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git dnsutils
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p data/reports
[ -f .env ] || cp .env.example .env
echo "Installed. Run: source .venv/bin/activate && python run.py"
