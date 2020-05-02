from datetime import datetime

from sqlalchemy import func

from covid19.database import db
from service.data.models import Deaths, Confirmed, Recovered, TimestampSerializableMixin


class Result(TimestampSerializableMixin):

    def __init__(self, moment, amount):
        self.moment = moment
        self.amount = amount


class World(object):
    """Contains the sum of all locations."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recovered = self._get_stat_query(Recovered)
        self.confirmations = self._get_stat_query(Confirmed)
        self.deaths = self._get_stat_query(Deaths)

    @staticmethod
    def _get_stat_query(cls):
        return [Result(moment, amount) for moment, amount in (
            db.session.query(cls.moment, func.sum(cls.amount))
                .group_by(cls.moment)
                .order_by(cls.moment)
                .all()
        )]

    @property
    def last_confirmed(self):
        return self.confirmations[-1].amount if self.confirmations else 0

    @property
    def last_updated(self):
        return self.confirmations[-1].moment if self.confirmations else datetime(year=1970, month=1, day=1)

    @property
    def last_deaths(self):
        return self.deaths[-1].amount if self.deaths else 0

    @property
    def last_recovered(self):
        return self.recovered[-1].amount if self.recovered else 0
