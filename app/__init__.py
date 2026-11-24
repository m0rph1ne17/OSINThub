import os
from pathlib import Path
from flask import Flask
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("OSINTHUB_SECRET_KEY", "local-dev-change-me")
    app.config["DATABASE"] = str(Path(__file__).resolve().parent.parent / "data" / "osinthub.db")
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()
    from .routes import bp
    app.register_blueprint(bp)
    return app
