import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, send_from_directory, url_for
from sqlalchemy import event

from models import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.media import media_bp


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(__name__)
    instance_dir = BASE_DIR / "instance"
    instance_dir.mkdir(exist_ok=True)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "fallback-dev-key"),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{instance_dir / 'social_misuse.db'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(BASE_DIR / "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    )

    Path(app.config["UPLOAD_FOLDER"]).mkdir(exist_ok=True)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/")
    def index():
        return redirect(url_for("media.feed"))

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def set_sqlite_pragmas(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=OFF")
            cursor.execute("PRAGMA synchronous=OFF")
            cursor.close()

        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
