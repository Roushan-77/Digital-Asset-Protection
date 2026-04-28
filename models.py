from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    media = db.relationship("Media", back_populates="owner", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="media")


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False)
    uploaded_media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    gemini_response = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False, default="Medium")
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    original_media = db.relationship("Media", foreign_keys=[original_media_id])
    uploaded_media = db.relationship("Media", foreign_keys=[uploaded_media_id])
    uploader = db.relationship("User")
