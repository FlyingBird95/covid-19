# -*- coding: utf-8 -*-
"""Stats section."""

from flask import Blueprint, render_template, jsonify, url_for

from covid19.extensions import cache
from covid19.stats.wrappers import with_location, with_china
from service.data.models import Location
from service.data.predict import PredictConfirmations, PredictDeaths

blueprint = Blueprint("stats", __name__, url_prefix="/stats", static_folder="../static")


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
@with_china
def details(location, china):
    return render_template('stats/location.html', location=location, china=china)


@blueprint.route('/location/<int:location_id>/json')
@with_location
@with_china
def details_json(location, china):
    start_index = location.day1_index

    return jsonify({
        'confirmed': [obj.serialize() for obj in location.confirmations],
        'recovered': [obj.serialize() for obj in location.recoveries],
        'deaths': [obj.serialize() for obj in location.deaths],
        'compare': {
            'location': [obj.amount for obj in location.confirmations[start_index:]],
            'china': [obj.amount for obj in china.confirmations],
        },
        'name': location.country,
    })


@blueprint.route('/location/<int:location_id>/json-future')
@with_location
def details_json_future(location):
    """Let's predict the future."""
    confirmations = PredictConfirmations(location=location)
    deaths = PredictDeaths(location=location)

    return jsonify({
        'name': location.country,
        'confirmations': confirmations.to_json(),
        'deaths': deaths.to_json(),
    })
