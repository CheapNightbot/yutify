from flask import render_template

from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html", error=error), 404

@bp.app_errorhandler(403)
def page_not_found(error):
    return render_template("errors/403.html", error=error), 403


@bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("errors/500.html", error=error), 500
