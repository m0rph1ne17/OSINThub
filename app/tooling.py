import ipaddress
import os
import re
import shutil
import subprocess
import tempfile

from .investigations import valid_domain

MAX_OUTPUT_CHARS = 60000

TOOLS = {
    "sherlock": {
        "name": "Sherlock", "binary": "sherlock", "target_type": "username",
        "timeout": 180,
        "description": "Searches public websites for accounts matching a username.",
        "install": "pipx install sherlock-project",
        "upstream": "https://github.com/sherlock-project/sherlock",
    },
    "maigret": {
        "name": "Maigret", "binary": "maigret", "target_type": "username",
        "timeout": 240,
        "description": "Builds a public username-search report across supported sites.",
        "install": "pipx install maigret",
        "upstream": "https://github.com/soxoj/maigret",
    },
    "theharvester": {
        "name": "theHarvester", "binary": "theHarvester", "target_type": "domain",
        "timeout": 240,
        "description": "Collects public domain and email-related intelligence from configured sources.",
        "install": "Install in a separate supported Python environment; see INSTALLATION.md.",
        "upstream": "https://github.com/laramies/theHarvester",
    },
    "subfinder": {
        "name": "Subfinder", "binary": "subfinder", "target_type": "domain",
        "timeout": 240,
        "description": "Discovers subdomains using passive sources.",
        "install": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "upstream": "https://github.com/projectdiscovery/subfinder",
    },
    "whatweb": {
        "name": "WhatWeb", "binary": "whatweb", "target_type": "domain",
        "timeout": 120,
        "description": "Identifies technologies exposed by a public website using low-aggression mode.",
        "install": "Install Ruby, then follow the upstream WhatWeb installation instructions.",
        "upstream": "https://github.com/urbanadventurer/WhatWeb",
    },
}

class ToolError(Exception):
    pass

def tool_status(settings):
    rows = []
    for tool_id, meta in TOOLS.items():
        executable = shutil.which(meta["binary"])
        rows.append({
            "id": tool_id, "name": meta["name"], "target_type": meta["target_type"],
            "description": meta["description"], "install": meta["install"],
            "upstream": meta["upstream"], "installed": bool(executable),
            "executable": executable, "enabled": bool(settings.get(tool_id, False)),
            "timeout": meta["timeout"],
        })
    return rows

def validate_tool_target(tool_id, target):
    if tool_id not in TOOLS:
        raise ValueError("Unknown tool.")
    value = (target or "").strip()
    if not value:
        raise ValueError("Enter a target.")
    target_type = TOOLS[tool_id]["target_type"]
    if target_type == "username":
        value = value.lstrip("@")
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", value):
            raise ValueError("Username must contain 1–64 letters, numbers, dots, underscores, or hyphens.")
        return value

    domain = valid_domain(value)
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        pass
    else:
        raise ValueError("Use a public domain name, not an IP address.")
    if "." not in domain or domain.endswith((".local", ".localhost", ".test", ".invalid")):
        raise ValueError("Use a fully qualified public domain name.")
    return domain

def _command(tool_id, executable, target):
    if tool_id in ("sherlock", "maigret"):
        return [executable, target]
    if tool_id == "theharvester":
        return [executable, "-d", target, "-b", "crtsh,certspotter"]
    if tool_id == "subfinder":
        return [executable, "-d", target, "-silent"]
    if tool_id == "whatweb":
        return [executable, "--aggression=1", "--no-errors", "https://" + target]
    raise ToolError("No command adapter exists for this tool.")

def run_tool(tool_id, target):
    clean_target = validate_tool_target(tool_id, target)
    meta = TOOLS[tool_id]
    executable = shutil.which(meta["binary"])
    if not executable:
        raise ToolError(f"{meta['name']} is not installed or is not available on PATH.")

    with tempfile.TemporaryDirectory(prefix="osinthub-tool-") as temp_dir:
        command = _command(tool_id, executable, clean_target)
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        try:
            completed = subprocess.run(
                command, cwd=temp_dir, env=env, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                errors="replace", timeout=meta["timeout"], check=False, shell=False,
            )
            stdout = completed.stdout[-MAX_OUTPUT_CHARS:]
            stderr = completed.stderr[-MAX_OUTPUT_CHARS:]
            status = "completed" if completed.returncode == 0 else "completed_with_errors"
            summary = f"{meta['name']} finished with exit code {completed.returncode}."
            execution = {
                "tool": tool_id, "exit_code": completed.returncode, "timed_out": False,
                "duration_limit_seconds": meta["timeout"], "arguments": command[1:],
            }
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", "replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", "replace")
            stdout, stderr = stdout[-MAX_OUTPUT_CHARS:], stderr[-MAX_OUTPUT_CHARS:]
            status = "timed_out"
            summary = f"{meta['name']} exceeded its {meta['timeout']}-second execution limit."
            execution = {
                "tool": tool_id, "exit_code": None, "timed_out": True,
                "duration_limit_seconds": meta["timeout"], "arguments": command[1:],
            }

    findings = [{"label": "Tool output", "value": stdout or "(No standard output.)"}]
    if stderr:
        findings.append({"label": "Standard error", "value": stderr})
    return {
        "summary": summary, "findings": findings, "execution": execution,
        "limitations": [
            "Tool output is unverified third-party data; validate important findings independently.",
            "Results depend on each tool's sources, network access, rate limits, and configuration.",
            "Only run against usernames or domains you are authorized to research.",
        ],
    }, status
