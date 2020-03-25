from functools import wraps

from flask import flash, redirect, url_for

from service.data.models import Location


def with_location(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'location_id' in kwargs:
            location = Location.query.get(kwargs.pop('location_id'))
            if location is not None:
                return func(*args, location=location, **kwargs)
            flash('Location cannot be found', "info")
            return redirect(url_for('stats.overview'))
        raise ValueError("Could not find mandatory keyword argument 'location_id'.")
    return wrapper


def with_china(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        china = Location.get_china()
        return func(*args, china=china, **kwargs)
    return wrapper
