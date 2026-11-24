# OSINThub by dysph0r1a

Local-first OSINT dashboard for authorized public-source research. Supports Debian 13 and Termux.

## MVP features
- Flask dashboard and responsive dark UI
- Username: public search links (no account access or identity verification)
- Email: basic syntax and public DNS checks
- Phone: optional numbering-plan parsing with `phonenumbers`
- Domain: DNS records plus RDAP and certificate-transparency links
- SQLite scan history
- Markdown and JSON report downloads

## Install
Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git dnsutils
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

Termux:
```bash
pkg update && pkg upgrade -y
pkg install -y python git clang rust libffi openssl
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```
Open http://127.0.0.1:5000 on the same device.

Data is stored in `data/osinthub.db` and `data/reports/`. Do not commit actual scan data, reports, `.env`, or credentials. The app binds to localhost by default. Use only targets you are authorized to research. No private-account access, password guessing, authentication bypass, account takeover, or subscriber lookup is implemented.
