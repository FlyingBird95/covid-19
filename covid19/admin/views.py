# -*- coding: utf-8 -*-
"""Admin section."""
from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint("admin", __name__, url_prefix="/admin", static_folder="../static")


@blueprint.route("/")
@login_required
def overview():
    """Return the overview page."""
    return render_template("stats/overview.html")
