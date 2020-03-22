from datetime import datetime

import requests

from service.data.models import Location, Deaths, Confirmed, Recovered, Totals

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
    deaths, confirmed, recovered = 0, 0, 0

    for loc in locations:
        country = loc['country']
        province = loc['province']
        print(loc['country'] + ' - ' + str(loc['id']))

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

        confirmed += fetch_confirmed(location, timelines['confirmed'])
        deaths += fetch_deaths(location, timelines['deaths'])
        recovered += fetch_recovered(location, timelines['recovered'])

    confirmed_total = Totals.get_or_create(Totals.CONFIRMED)
    confirmed_total.value = confirmed
    confirmed_total.save()

    deaths_total = Totals.get_or_create(Totals.DEATHS)
    deaths_total.value = deaths
    deaths_total.save()

    recovered_total = Totals.get_or_create(Totals.RECOVERED)
    recovered_total.value = recovered
    recovered_total.save()


def fetch_confirmed(location, data):
    for moment, amount in data['timeline'].items():
        obj = Confirmed(
            location_id=location.id,
            moment=get_datetime(moment),
            amount=amount,
        )
        if not Confirmed.exists(obj):
            obj.save()
    return amount


def fetch_deaths(location, data):
    for moment, amount in data['timeline'].items():
        obj = Deaths(
            location_id=location.id,
            moment=get_datetime(moment),
            amount=amount,
        )
        if not Deaths.exists(obj):
            obj.save()
    return amount

def fetch_recovered(location, data):
    for moment, amount in data['timeline'].items():
        obj = Recovered(
            location_id=location.id,
            moment=get_datetime(moment),
            amount=amount,
        )
        if not Recovered.exists(obj):
            obj.save()
    return amount
