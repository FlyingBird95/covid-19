from sqlalchemy import desc, UniqueConstraint

from covid19.database import SurrogatePK, Model, Column, db, relationship


class Location(SurrogatePK, Model):
    """Location of the collected data."""

    __tablename__ = 'locations'

    country = Column(db.String(80), unique=True, nullable=False)
    country_code = Column(db.String(10), nullable=False)

    confirmations = relationship("Confirmed", lazy='select')
    deaths = relationship("Deaths", lazy='select')
    recoveries = relationship("Recovered", lazy='select')

    @classmethod
    def get_china(cls):
        """China is a special country, since the virus started here, thus we have more non-negative data-points."""
        return cls.query.filter_by(country="China").one()

    @property
    def last_confirmed(self):
        obj = Confirmed.query.filter_by(location=self).order_by(desc(Confirmed.moment)).first()
        return obj if obj is not None else Confirmed()

    @property
    def last_recovered(self):
        obj = Recovered.query.filter_by(location=self).order_by(desc(Recovered.moment)).first()
        return obj if obj is not None else Recovered()

    @property
    def last_death(self):
        obj = Deaths.query.filter_by(location=self).order_by(desc(Deaths.moment)).first()
        return obj if obj is not None else Deaths()

    def get_people_sick(self, i):
        """Returns the amount of people that are still sick."""
        return self.confirmations[i].amount - self.recoveries[i].amount - self.deaths[i].amount

    @property
    def day1(self):
        """Returns the first day with more confirmed cases than China's first day.
        This can be used for aligning the data."""
        return self.confirmations[self.day1_index].moment

    @property
    def day1_index(self):
        """Returns the first day with an infected person."""
        index = 0
        for obj in self.confirmations:
            if obj.amount > 50:
                return index
            index += 1
        return 0

    @classmethod
    def get_by_country(cls, country):
        return cls.query.filter(Location.country == country).one()

    @classmethod
    def exists(cls, country):
        return cls.query.filter(Location.country == country).count() >= 1

    def remove_data_points(self):
        """Removes all data points in Recovered, Confirmed and Deaths that belong to this location."""
        Recovered.query.filter_by(location=self).delete()
        Confirmed.query.filter_by(location=self).delete()
        Deaths.query.filter_by(location=self).delete()


class TimestampSerializableMixin(object):
    def serialize(self):
        return {
            'moment': self.moment.isoformat(),
            'amount': int(self.amount),
        }


class StatsFuncsMixin(object):

    @classmethod
    def get_for(cls, location_id, moment):
        return cls.query.filter_by(location_id=location_id, moment=moment).one()

    @classmethod
    def exists(cls, obj):
        return cls.query.filter(
            cls.location_id == obj.location_id,
            cls.amount == obj.amount,
            cls.moment == obj.moment,
        ).count() >= 1


class Confirmed(SurrogatePK, StatsFuncsMixin, TimestampSerializableMixin, Model):
    """Total number of confirmed cases at a certain moment in a location."""

    __tablename__ = 'confirmations'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'),)

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))
    location = relationship("Location")

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, default=0, nullable=False)


class Deaths(SurrogatePK, StatsFuncsMixin, TimestampSerializableMixin, Model):
    """Total number of deaths at a certain moment in a location."""

    __tablename__ = 'deaths'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'),)

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))
    location = relationship("Location")

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, default=0, nullable=False)


class Recovered(SurrogatePK, StatsFuncsMixin, TimestampSerializableMixin, Model):
    """Total number of recoveries at a certain moment in a location."""

    __tablename__ = 'recoveries'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'),)

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))
    location = relationship("Location")

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, default=0, nullable=False)
