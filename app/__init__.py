import os
import secrets
import hmac
from pathlib import Path
from flask import Flask, abort, request, session
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("OSINTHUB_SECRET_KEY") or secrets.token_hex(32)
    app.config["DATABASE"] = str(Path(__file__).resolve().parent.parent / "data" / "osinthub.db")
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    @app.context_processor
    def inject_csrf_token():
        token = session.setdefault("_csrf_token", secrets.token_urlsafe(32))
        return {"csrf_token": token}

    @app.before_request
    def protect_state_changes():
        if request.method == "POST":
            expected = session.get("_csrf_token", "")
            supplied = request.form.get("_csrf_token", "")
            if not expected or not supplied or not hmac.compare_digest(expected, supplied):
                abort(400, description="Invalid or missing CSRF token.")

    with app.app_context():
        init_db()
    from .routes import bp
    app.register_blueprint(bp)
    return app
