# -*- coding: utf-8 -*-
"""Stats section."""
from functools import wraps

from flask import Blueprint, render_template
from service.data.models import Location

blueprint = Blueprint("stats", __name__, url_prefix="/stats", static_folder="../static")


def with_location(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'location_id' in kwargs:
            location = Location.get_by_id(kwargs.pop('location_id'))
            return func(*args, location=location, **kwargs)
        raise ValueError("Could not find mandatory keyword argument 'location_id'.")
    return wrapper


@blueprint.route("/")
def overview():
    """Return the overview page."""
    locations = Location.query.all()
    return render_template("stats/overview.html", locations=locations)


@blueprint.route('/location/<int:location_id>')
@with_location
def location(location):
    return location.full_name
