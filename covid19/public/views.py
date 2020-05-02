# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_user, login_required, logout_user

from covid19.extensions import login_manager, cache
from covid19.public.forms import LoginForm
from covid19.user.models import User
from covid19.utils import flash_errors
from service.data.world import World

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/")
@cache.cached(timeout=50)
def home():
    """Home page."""
    world = World()
    return render_template(
        "public/home.html",
        deaths=world.last_deaths,
        confirmed=world.last_confirmed,
        recovered=world.last_recovered,
        updated=world.last_updated,
    )


@blueprint.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            redirect_url = request.args.get("next") or url_for("admin.overview")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/login.html", form=form)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))