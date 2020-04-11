import logging
from datetime import datetime

import requests

from service.data.models import Location, Deaths, Confirmed, Recovered, Totals

DATA = 'https://covidapi.info/api/v1/country/{country_code}'
COUNTRIES = 'https://raw.githubusercontent.com/backtrackbaba/covid-api/master/data/country_name_to_iso.json'
DATE_FORMAT = '%Y-%m-%d'


def get_datetime(date_string):
    """Returns a Datetime object."""
    return datetime.strptime(date_string, DATE_FORMAT)


def get_value(obj, key, default=0):
    if key in obj and obj[key] is not None:
        return max(obj[key], default)
    return default


def fetch_countries():
    """Get the countries from an external location and save into the database."""
    countries = requests.get(COUNTRIES).json()

    for country, country_code in countries.items():
        if not Location.exists(country=country):
            Location(country=country, country_code=country_code).save()
    logging.info('Done')


def fetch_data():
    """Get the data from an external location and save into the database."""
    deaths, confirmed, recovered = 0, 0, 0

    for location in Location.query.all():
        print(location.country)
        response = requests.get(DATA.format(country_code=location.country_code))
        retry = 0
        while response.status_code != 200 and retry < 3:
            response = requests.get(DATA.format(country_code=location.country_code))
            retry += 1
        if retry == 3:
            print('Deleting {}'.format(location.country))
            location.delete()
            continue
        data = response.json()

        last_deaths, last_confirmed, last_recovered = 0, 0, 0
        for day, row in data['result'].items():
            day = get_datetime(day)
            last_recovered = save_row(Recovered, location, day, get_value(row, 'recovered', last_recovered))
            last_confirmed = save_row(Confirmed, location, day, get_value(row, 'confirmed', last_confirmed))
            last_deaths = save_row(Deaths, location, day, get_value(row, 'deaths', last_deaths))

        confirmed += last_confirmed
        deaths += last_deaths
        recovered += last_recovered

    set_value(Totals.CONFIRMED, confirmed)
    set_value(Totals.DEATHS, deaths)
    set_value(Totals.RECOVERED, recovered)
    set_value(Totals.UPDATED, datetime.utcnow().isoformat())


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
    else:
        obj = cls.get_for(location_id=location.id, moment=day)
        obj.update(amount=value)
    return value
