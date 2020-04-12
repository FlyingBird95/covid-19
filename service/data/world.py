from collections import namedtuple

from sqlalchemy import func

from covid19.database import db
from service.data.models import Deaths, Confirmed, Recovered, TimestampSerializable


class Result(TimestampSerializable):

    def __init__(self, moment, amount):
        self.moment = moment
        self.amount = amount


class World(object):
    """Contains the sum of all locations."""

    @staticmethod
    def _get_stat_query(cls):
        return [Result(moment, amount) for moment, amount in (
            db.session.query(cls.moment, func.sum(cls.amount))
                .group_by(cls.moment)
                .order_by(cls.moment)
                .all()
        )]

    @property
    def confirmations(self):
        return self._get_stat_query(Confirmed)

    @property
    def deaths(self):
        return self._get_stat_query(Deaths)

    @property
    def recovered(self):
        return self._get_stat_query(Recovered)
