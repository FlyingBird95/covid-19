from datetime import datetime

import requests
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from service.data.models import Location, Deaths, Confirmed, Recovered

URL = 'https://coronavirus-tracker-api.herokuapp.com/v2/locations?timelines=1'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
DATE_FORMAT_2 = '%Y-%m-%dT%H:%M:%SZ'


def get_datetime(date_string):
    """Returns a Datetime object."""
    try:
        return datetime.strptime(date_string, DATE_FORMAT)  # first try with milliseconds.
    except ValueError:
        return datetime.strptime(date_string, DATE_FORMAT_2)  # try without milliseconds.


def fetch():
    """Get the data from an external location and save into the database. Note that this might be a slow operation."""
    data = requests.get(URL).json()
    locations = data['locations']

    for loc in locations:
        country = loc['country']
        province = loc['province']

        if Location.exists(country=country, province=province):
            location = Location.get_by_country_and_province(country=country, province=province)
            location.update(last_updated=get_datetime(loc['last_updated']))
        else:
            location = Location(
                country=country,
                country_code=loc['country_code'],
                last_updated=get_datetime(loc['last_updated']),
                province=province,
                longitude=loc['coordinates']['longitude'],
                latitude=loc['coordinates']['latitude'],
            )
            location.save()

        timelines = loc['timelines']

        fetch_confirmed(location, timelines['confirmed'])
        fetch_deaths(location, timelines['deaths'])
        fetch_recovered(location, timelines['recovered'])


def fetch_confirmed(location, data):
    for moment, amount in data['timeline'].items():
        obj = Confirmed(
            location_id=location.id,
            moment=get_datetime(moment),
            amount=amount,
        )
        if not Confirmed.exists(obj):
            obj.save()


def fetch_deaths(location, data):
    for moment, amount in data['timeline'].items():
        obj = Deaths(
            location_id=location.id,
            moment=get_datetime(moment),
            amount=amount,
        )
        if not Deaths.exists(obj):
            obj.save()


def fetch_recovered(location, data):
    for moment, amount in data['timeline'].items():
        obj = Recovered(
            location_id=location.id,
            moment=get_datetime(moment),
            amount=amount,
        )
        if not Recovered.exists(obj):
            obj.save()
