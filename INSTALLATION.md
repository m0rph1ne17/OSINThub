# OSINThub installation guide

## Debian 13
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git dnsutils
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Termux
```bash
pkg update && pkg upgrade -y
pkg install -y python git clang rust libffi openssl
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open `http://127.0.0.1:5000` on the same device.

## Modules in this MVP
- Username: public search links; no automated account access.
- Email: basic syntax and domain DNS checks.
- Phone: optional numbering-plan parsing; no subscriber lookup.
- Domain: DNS records plus links to public RDAP and certificate transparency services.

## Data
SQLite history: `data/osinthub.db`. Markdown reports: `data/reports/`. Do not commit scan data, reports, `.env`, or credentials.

## GitHub
Create a **private** repository named `OSINThub` in your account, then:
```bash
git init
git branch -M main
git add .
git commit -m "Initial OSINThub MVP"
git remote add origin https://github.com/REPLACE_WITH_OWNER/OSINThub.git
git push -u origin main
```
Use GitHub CLI or a credential manager. Never embed tokens in source code.
