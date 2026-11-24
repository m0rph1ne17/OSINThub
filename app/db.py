import json
import sqlite3
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    get_db().executescript('''
    CREATE TABLE IF NOT EXISTS scans (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      target_type TEXT NOT NULL,
      target TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      results_json TEXT NOT NULL
    );
    ''')
    get_db().commit()

def save_scan(kind, target, results):
    cur = get_db().execute(
        "INSERT INTO scans(target_type,target,status,results_json) VALUES(?,?,?,?)",
        (kind, target, "completed", json.dumps(results, ensure_ascii=False)))
    get_db().commit()
    return cur.lastrowid

def list_scans(limit=100):
    return get_db().execute(
        "SELECT id,target_type,target,status,created_at FROM scans ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall()

def get_scan(scan_id):
    row = get_db().execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
    if row is None:
        return None
    item = dict(row)
    item["results"] = json.loads(item.pop("results_json"))
    return item
