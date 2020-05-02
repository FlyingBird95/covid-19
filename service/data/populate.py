from datetime import datetime

import requests

from service.data.models import Location, Deaths, Confirmed, Recovered
from service.data.wrappers import with_retry

DATA = 'https://covidapi.info/api/v1/country/{country_code}'
COUNTRIES = 'https://raw.githubusercontent.com/backtrackbaba/covid-api/master/data/' \
            'country_name_to_iso.json'
DATE_FORMAT = '%Y-%m-%d'


def get_value(obj, key, default=0):
    return obj[key] if key in obj and obj[key] is not None else default


def fetch_countries():
    """Get the countries from an external location and save into the database."""
    countries = requests.get(COUNTRIES).json()
    Recovered.query.delete()
    Confirmed.query.delete()
    Deaths.query.delete()
    Location.query.delete()  # delete all existing data

    for country, country_code in countries.items():
        if not Location.exists(country=country):
            Location(country=country, country_code=country_code).save()
    print('Done')


def get_country_data(location):
    """Returns none if the data cannot be retrieved."""
    print('{}: {}'.format(datetime.now(), location.country))
    response = with_retry(
        lambda: requests.get(DATA.format(country_code=location.country_code))
    )
    if response is None:
        print('Deleting {}'.format(location.country))
        location.remove_data_points()
        location.delete()
        return None
    return response.json()


def fetch_data():
    """Get the data from an external location and save into the database."""
    for location in Location.query.all():
        try:
            data = get_country_data(location=location)
            if data is None:
                continue

            location.remove_data_points()

            for day_string, row in data['result'].items():
                moment = datetime.strptime(day_string, DATE_FORMAT)
                Recovered(location=location, moment=moment, amount=get_value(row, 'recovered')).save()
                Confirmed(location=location, moment=moment, amount=get_value(row, 'confirmed')).save()
                Deaths(location=location, moment=moment, amount=get_value(row, 'deaths')).save()
        except Exception as e:
            print(e)
            continue
