from flask import Blueprint, render_template

from models import Report
from routes.auth import current_user, login_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard")
@login_required
def dashboard():
    user = current_user()
    reports = (
        Report.query.join(Report.original_media)
        .filter_by(owner_id=user.id)
        .order_by(Report.timestamp.desc())
        .all()
    )
    return render_template("dashboard.html", reports=reports)
