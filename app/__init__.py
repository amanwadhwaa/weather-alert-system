import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from .config import load_config
from .models import db
from .routes import bp
from .service import run_check


def create_app(test_config=None):
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    if app.config["SCHEDULER_ENABLED"] and not app.config.get("TESTING"):
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            run_check, "interval", args=[app],
            minutes=app.config["CHECK_INTERVAL_MINUTES"],
            next_run_time=None,  # replaced below to run once shortly after start
            id="weather-check",
        )
        scheduler.start()
        scheduler.modify_job("weather-check", next_run_time=_soon())
        app.extensions["scheduler"] = scheduler

    return app


def _soon():
    from datetime import datetime, timedelta
    return datetime.now().astimezone() + timedelta(seconds=5)
