from flask import Blueprint, current_app, jsonify, redirect, render_template, url_for
from sqlalchemy import text

from .models import Reading, db
from .service import run_check

bp = Blueprint("main", __name__)


@bp.post("/check-now")
def check_now():
    """Trigger an immediate weather fetch and redirect back to dashboard."""
    run_check(current_app._get_current_object())
    return redirect(url_for("main.dashboard"))


@bp.get("/")
def dashboard():
    readings = Reading.query.order_by(Reading.recorded_at.desc()).limit(20).all()
    return render_template(
        "dashboard.html",
        readings=readings,
        latest=readings[0] if readings else None,
        threshold=current_app.config["TEMP_THRESHOLD_C"],
        city=current_app.config["CITY"],
    )


@bp.get("/api/readings")
def api_readings():
    readings = Reading.query.order_by(Reading.recorded_at.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in readings])


@bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return jsonify(status="unhealthy"), 503
    return jsonify(status="ok")
