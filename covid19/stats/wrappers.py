from functools import wraps

from service.data.models import Location


def with_location(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'location_id' in kwargs:
            location = Location.get_by_id(kwargs.pop('location_id'))
            return func(*args, location=location, **kwargs)
        raise ValueError("Could not find mandatory keyword argument 'location_id'.")
    return wrapper


def with_china(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        china = Location.get_china()
        return func(*args, china=china, **kwargs)
    return wrapper
