from datetime import datetime

import requests

from service.data.models import Location, Deaths, Confirmed, Recovered, Totals

URL = 'https://pomber.github.io/covid19/timeseries.json'
DATE_FORMAT = '%Y-%m-%d'


def get_datetime(date_string):
    """Returns a Datetime object."""
    return datetime.strptime(date_string, DATE_FORMAT)


def fetch():
    """Get the data from an external location and save into the database. Note that this might be a slow operation."""
    locations = requests.get(URL).json()
    deaths, confirmed, recovered = 0, 0, 0

    for country, data in locations.items():
        print(country)

        if not Location.exists(country=country):
            location = Location(country=country)
            location.save()
        else:
            location = Location.get_by_country(country)

        last_deaths, last_confirmed, last_recovered = 0, 0, 0
        for row in data:
            day = get_datetime(row['date'])
            last_recovered = save_row(Recovered, location, day, row['recovered'] or 0)
            last_confirmed = save_row(Confirmed, location, day, row['confirmed'] or 0)
            last_deaths = save_row(Deaths, location, day, row['deaths'] or 0)

        confirmed += last_confirmed
        deaths += last_deaths
        recovered += last_recovered

    set_value(Totals.CONFIRMED, confirmed)
    set_value(Totals.DEATHS, deaths)
    set_value(Totals.RECOVERED, recovered)


def set_value(key, value):
    obj = Totals.get_or_create(key)
    obj.value = value
    obj.save()


def save_row(cls, location, day, value):
    obj = cls(
        location_id=location.id,
        moment=day,
        amount=value,
    )
    if not cls.exists(obj):
        obj.save()
    return value
