# OSINThub by dysph0r1a

Local-first OSINT dashboard for authorized public-source research. Supports Debian 13 and Termux.

## Features
- Flask dashboard with responsive dark UI
- Username: built-in public search links plus optional Sherlock and Maigret integrations
- Email: basic syntax and public DNS checks
- Phone: optional numbering-plan parsing with `phonenumbers`
- Domain: DNS, RDAP and certificate-transparency references
- Optional theHarvester, Subfinder, and WhatWeb integrations
- SQLite scan history
- Markdown and JSON report downloads
- Tool execution timeouts, validated inputs, bounded output capture, and per-tool enable/disable controls

## Install
See [INSTALLATION.md](INSTALLATION.md) for Debian 13, Termux, and optional tool installation instructions.

Run:
```bash
source .venv/bin/activate
python run.py
```
Open http://127.0.0.1:5000 on the same device.

Data is stored in `data/osinthub.db` and `data/reports/`. Do not commit actual scan data, reports, `.env`, or credentials. The app binds to localhost by default.

Use only targets you are authorized to research. The integrations do not bypass authentication, access private accounts, guess passwords, take over accounts, or identify private subscribers. External tools can make requests to third-party services and may be subject to rate limits and terms of service.
