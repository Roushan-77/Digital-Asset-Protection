from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from models import Media, Report, db
from routes.auth import current_user, login_required
from utils.gemini import analyze_image_with_gemini, extract_risk_level
from utils.hashing import compare_hashes, generate_perceptual_hash


media_bp = Blueprint("media", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
HAMMING_THRESHOLD = 24


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@media_bp.get("/feed")
@login_required
def feed():
    media_items = Media.query.order_by(Media.created_at.desc()).all()
    my_uploads = Media.query.filter_by(owner_id=current_user().id).order_by(Media.created_at.desc()).all()
    return render_template("feed.html", media_items=media_items, my_uploads=my_uploads)


@media_bp.post("/upload")
@login_required
def upload():
    user = current_user()
    file = request.files.get("image")
    if not file or not file.filename:
        flash("Please choose an image to upload.", "danger")
        return redirect(url_for("media.feed"))
    if not allowed_file(file.filename):
        flash("Upload a PNG, JPG, JPEG, or WEBP image.", "danger")
        return redirect(url_for("media.feed"))

    filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
    save_path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    file.save(save_path)

    try:
        uploaded_hash = generate_perceptual_hash(save_path)
    except ValueError as exc:
        save_path.unlink(missing_ok=True)
        flash(str(exc), "danger")
        return redirect(url_for("media.feed"))

    closest_media = None
    closest_distance = None
    existing_media = Media.query.filter(Media.owner_id != user.id).all()
    for existing in existing_media:
        distance = compare_hashes(uploaded_hash, existing.hash)
        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_media = existing

    is_similar = closest_media is not None and closest_distance <= HAMMING_THRESHOLD
    media = Media(
        owner_id=user.id,
        file_path=filename,
        hash=uploaded_hash,
        is_flagged=is_similar,
    )
    db.session.add(media)
    db.session.flush()

    if is_similar:
        similarity_score = round(1 - (closest_distance / 64), 3)
        context_text = (
            "This image is similar to another sports media asset. Analyze whether this is "
            "unauthorized reuse, if it appears modified (cropped, watermark removed), and "
            "classify risk (Low/Medium/High). Give a short explanation."
        )
        gemini_response = analyze_image_with_gemini(str(save_path), context_text)
        report = Report(
            original_media_id=closest_media.id,
            uploaded_media_id=media.id,
            uploader_id=user.id,
            similarity_score=similarity_score,
            gemini_response=gemini_response,
            risk_level=extract_risk_level(gemini_response),
        )
        db.session.add(report)
        flash("This content may belong to another user.", "warning")
        flash(f"Alert created for @{closest_media.owner.username}.", "danger")
    else:
        flash("Upload saved as an original media asset.", "success")

    db.session.commit()
    return redirect(url_for("media.feed"))


@media_bp.get("/detections/<int:report_id>")
@login_required
def detection_detail(report_id: int):
    user = current_user()
    report = db.session.get(Report, report_id)
    if not report:
        flash("Detection report not found.", "danger")
        return redirect(url_for("media.feed"))
    if report.original_media.owner_id != user.id:
        flash("This alert belongs to another user.", "danger")
        return redirect(url_for("dashboard.dashboard"))
    return render_template("detection_detail.html", report=report)
