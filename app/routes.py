import json
from io import BytesIO
from pathlib import Path
from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from .db import get_scan, get_tool_settings, list_scans, save_scan, set_tool_enabled
from .investigations import investigate
from .reports import write_report
from .tooling import TOOLS, ToolError, run_tool, tool_status

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template("index.html", scans=list_scans(8))

@bp.post("/scan")
def scan():
    kind, target = request.form.get("target_type", ""), request.form.get("target", "")
    try:
        results = investigate(kind, target)
        scan_id = save_scan(kind, target.strip(), results)
        return redirect(url_for("main.detail", scan_id=scan_id))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index"))

@bp.get("/tools")
def tools():
    return render_template("tools.html", tools=tool_status(get_tool_settings()))

@bp.post("/tools/<tool_id>/toggle")
def toggle_tool(tool_id):
    if tool_id not in TOOLS:
        abort(404)
    enabled = request.form.get("enabled") == "1"
    current = {item["id"]: item for item in tool_status(get_tool_settings())}
    if enabled and not current[tool_id]["installed"]:
        flash(f"{current[tool_id]['name']} is not installed or is not on PATH.", "error")
        return redirect(url_for("main.tools"))
    set_tool_enabled(tool_id, enabled)
    flash(f"{current[tool_id]['name']} {'enabled' if enabled else 'disabled'}.", "success")
    return redirect(url_for("main.tools"))

@bp.post("/tools/run")
def run_integration():
    tool_id = request.form.get("tool_id", "")
    target = request.form.get("target", "")
    if tool_id not in TOOLS:
        abort(404)
    if not get_tool_settings().get(tool_id, False):
        flash("Enable this integration before running it.", "error")
        return redirect(url_for("main.tools"))
    try:
        results, status = run_tool(tool_id, target)
        scan_id = save_scan(tool_id, target.strip(), results, status=status)
        return redirect(url_for("main.detail", scan_id=scan_id))
    except (ValueError, ToolError) as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.tools"))

@bp.get("/history")
def history():
    return render_template("history.html", scans=list_scans(200))

@bp.get("/scan/<int:scan_id>")
def detail(scan_id):
    scan = get_scan(scan_id)
    if scan is None:
        abort(404)
    return render_template("detail.html", scan=scan)

@bp.get("/scan/<int:scan_id>/report.md")
def report_md(scan_id):
    scan = get_scan(scan_id)
    if scan is None:
        abort(404)
    path = write_report(scan, Path(__file__).resolve().parent.parent)
    return send_file(path, as_attachment=True, download_name=f"osinthub-scan-{scan_id}.md")

@bp.get("/scan/<int:scan_id>/report.json")
def report_json(scan_id):
    scan = get_scan(scan_id)
    if scan is None:
        abort(404)
    payload = json.dumps(scan, indent=2, ensure_ascii=False)
    return send_file(BytesIO(payload.encode()), mimetype="application/json",
                     as_attachment=True, download_name=f"osinthub-scan-{scan_id}.json")
