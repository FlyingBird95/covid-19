# -*- coding: utf-8 -*-
"""Admin section."""
from flask import Blueprint, render_template
from flask_login import login_required

from service.data import populate

blueprint = Blueprint("admin", __name__, url_prefix="/admin", static_folder="../static")


@blueprint.route("/")
@login_required
def overview():
    """Return the overview page."""
    return render_template("stats/overview.html")


@blueprint.route("/fetch")
@login_required
def fetch():
    """Return the overview page."""
    populate.fetch()

    return render_template("stats/overview.html")
