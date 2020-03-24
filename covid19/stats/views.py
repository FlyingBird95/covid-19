# -*- coding: utf-8 -*-
"""Stats section."""
from functools import wraps

from flask import Blueprint, render_template, jsonify, url_for

from covid19.extensions import cache
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
    return render_template("stats/overview.html")


@blueprint.route('/overview-json')
@cache.cached(timeout=50)
def overview_json():
    locations = Location.query.all()
    content = [
        {
            'country': loc.country,
            'confirmed': loc.last_confirmed.amount or 0,
            'recovered': loc.last_recovered.amount or 0,
            'death': loc.last_death.amount or 0,
            'url': url_for('stats.details', location_id=loc.id),
        } for loc in locations
    ]
    return jsonify({"data": content})


@blueprint.route('/location/<int:location_id>')
@with_location
def details(location):
    return render_template('stats/location.html', location=location)


@blueprint.route('/location/<int:location_id>/json')
@with_location
def details_json(location):
    return jsonify({
        'confirmed': [obj.serialize() for obj in location.confirmations],
        'recovered': [obj.serialize() for obj in location.recoveries],
        'deaths': [obj.serialize() for obj in location.deaths],
    })
