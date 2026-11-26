# OSINThub installation and Phase 2 integrations

## Core application

### Debian 13
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git dnsutils build-essential libxml2-dev libxslt1-dev pkg-config
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

### Termux
```bash
pkg update && pkg upgrade -y
pkg install -y python git clang rust libffi openssl libxml2 libxslt pkg-config ruby golang
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open `http://127.0.0.1:5000` on the same device. The dashboard binds to localhost by default.

## Phase 2: optional external tools

Open **Tool integrations** in the dashboard. Tools are disabled by default. Install a tool separately, ensure its executable is on the same `PATH` used to start OSINThub, then refresh the integrations page and enable it.

Do not install all tools into OSINThub's Flask virtual environment. Several have independent runtimes and dependency trees. Keep external tools isolated where possible.

### Sherlock (username search)
Official project: https://github.com/sherlock-project/sherlock

```bash
python -m pipx install sherlock-project
```
If `pipx` is not available, follow upstream instructions. Sherlock's official project lists pipx, pip/uv, Docker, and community packages. Community Debian packages are not maintained by the Sherlock project; prefer an isolated Python installation.

### Maigret (username search)
Official project: https://github.com/soxoj/maigret

```bash
python -m pipx install maigret
```
Maigret requires Python 3.10 or newer. On Termux, native dependencies such as `libxml2` and `libxslt` may be needed when pip builds `lxml` from source:
```bash
pkg install libxml2 libxslt clang make pkg-config
```
Retry using Maigret's own installation instructions and verify with `maigret --help`. Do not assume the build succeeded until that command works.

### theHarvester (domain/email-related public-source research)
Official project: https://github.com/laramies/theHarvester

The current upstream installation page specifies a Python 3.14 source environment and recommends `uv sync` from its repository. This may not match the Python version supplied by every Debian/Termux environment. Install it in a separate environment that meets current upstream requirements, then make the `theHarvester` executable available to OSINThub's process. The adapter uses the passive `crtsh` and `certspotter` sources; other providers may require API keys and configuration.

Upstream instructions: https://github.com/laramies/theHarvester/wiki/Installation

### Subfinder (passive subdomain discovery)
Official project: https://github.com/projectdiscovery/subfinder

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```
Ensure the Go binary directory (commonly `$(go env GOPATH)/bin`) is on `PATH` before launching OSINThub. Some passive sources require optional provider API keys. The integration uses default passive-source behavior and does not configure API keys.

### WhatWeb (website technology identification)
Official project: https://github.com/urbanadventurer/WhatWeb

WhatWeb is Ruby-based. Install Ruby, then follow the official repository's installation instructions. The OSINThub adapter uses aggression level 1, the default low-aggression mode. It still makes an HTTP request to the target, so only use it on a domain you own or are explicitly authorized to assess.

## Integration behavior and limits

- Each integration is disabled by default and must be enabled from the dashboard.
- The app checks for the executable on `PATH`; it does not install tools automatically.
- Each run has a fixed timeout and bounded captured-output size.
- Commands are launched as argument arrays with `shell=False`; user input is validated and is never interpreted as shell syntax.
- Tool runs are saved as individual history entries and included in Markdown/JSON exports.
- Output is captured after completion; this phase does not stream live progress.
- A timeout or non-zero exit is recorded rather than treated as a successful result.
- API keys are not required for the configured default commands. Optional provider keys are not configured by this phase.
- Findings are leads, not identity proof. Third-party tools can produce false positives, incomplete results, and rate-limit errors.

## Data and privacy

SQLite history: `data/osinthub.db`. Markdown reports: `data/reports/`. Do not commit actual scan data, reports, `.env`, API credentials, or private investigation material. The repository `.gitignore` excludes local data files.
