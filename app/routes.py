import json
from io import BytesIO
from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from .db import get_scan, list_scans, save_scan
from .investigations import investigate
from .reports import write_report

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
    path = write_report(scan, __import__("pathlib").Path(__file__).resolve().parent.parent)
    return send_file(path, as_attachment=True, download_name=f"osinthub-scan-{scan_id}.md")

@bp.get("/scan/<int:scan_id>/report.json")
def report_json(scan_id):
    scan = get_scan(scan_id)
    if scan is None:
        abort(404)
    payload = json.dumps(scan, indent=2, ensure_ascii=False)
    return send_file(BytesIO(payload.encode()), mimetype="application/json",
                     as_attachment=True, download_name=f"osinthub-scan-{scan_id}.json")
