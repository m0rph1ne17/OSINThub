import json
from pathlib import Path

def markdown_report(scan):
    lines = [f"# OSINThub report — scan #{scan['id']}", "",
             f"- **Type:** {scan['target_type']}", f"- **Target:** `{scan['target']}`",
             f"- **Created:** {scan['created_at']}", f"- **Status:** {scan['status']}", "",
             "## Summary", "", scan["results"].get("summary", ""), "", "## Findings", ""]
    for finding in scan["results"].get("findings", []):
        lines += ["### " + finding.get("label", "Finding"), "", "```json",
                  json.dumps(finding.get("value"), indent=2, ensure_ascii=False), "```", ""]
    execution = scan["results"].get("execution")
    if execution:
        lines += ["## Tool execution", "", "```json",
                  json.dumps(execution, indent=2, ensure_ascii=False), "```", ""]
    lines += ["## Limitations", ""] + ["- " + x for x in scan["results"].get("limitations", [])]
    lines += ["", "Generated locally by OSINThub. Verify findings independently."]
    return "\n".join(lines)

def write_report(scan, base_dir):
    folder = Path(base_dir) / "data" / "reports"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"scan-{scan['id']}.md"
    path.write_text(markdown_report(scan), encoding="utf-8")
    return path
