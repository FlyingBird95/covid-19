from sqlalchemy import desc, UniqueConstraint, func

from covid19.database import SurrogatePK, Model, Column, db, relationship


class Location(SurrogatePK, Model):
    """Location of the collected data."""

    __tablename__ = 'locations'
    __table_args__ = (UniqueConstraint('country', 'province'), )

    country = Column(db.String(80), nullable=False)
    country_code = Column(db.String(10), nullable=False)
    longitude = Column(db.Numeric, nullable=False)
    latitude = Column(db.Numeric, nullable=False)
    last_updated = Column(db.DateTime, nullable=True)
    province = Column(db.String(80), nullable=True)

    confirmations = relationship("Confirmed", lazy='select')
    deaths = relationship("Deaths", lazy='select')
    recoveries = relationship("Recovered", lazy='select')

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

    @classmethod
    def get_by_country_and_province(cls, country, province):
        return cls.query.filter(Location.country == country, Location.province == province).one()

    @classmethod
    def exists(cls, country, province):
        return cls.query.filter(Location.country == country, Location.province == province).count() >= 1

    @property
    def full_name(self):
        if self.province:
            return '{} - {}'.format(self.country, self.province)
        return self.country


class StatsFuncsMixin():

    @classmethod
    def get_latest(cls, location=None):
        return cls.query.filter_by(location=location).order_by(desc(Confirmed.moment)).one()

    @classmethod
    def exists(cls, obj):
        return cls.query.filter(
            cls.location_id == obj.location_id,
            cls.amount == obj.amount,
            cls.moment == obj.moment,
        ).count() >= 1

    @classmethod
    def get_total(cls, locations):
        return sum([db.session.query(func.max(cls.amount)).filter_by(location_id=loc.id).scalar() for loc in locations])

    def serialize(self):
        return {
            'moment': self.moment.isoformat(),
            'amount': self.amount,
        }


class Confirmed(SurrogatePK, StatsFuncsMixin, Model):
    """Total number of confirmed cases at a certain moment in a location."""

    __tablename__ = 'confirmations'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'), )

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))
    location = relationship("Location")

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, default=0, nullable=False)


class Deaths(SurrogatePK, StatsFuncsMixin, Model):
    """Total number of deaths at a certain moment in a location."""

    __tablename__ = 'deaths'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'), )

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))
    location = relationship("Location")

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, default=0, nullable=False)


class Recovered(SurrogatePK, StatsFuncsMixin, Model):
    """Total number of recoveries at a certain moment in a location."""

    __tablename__ = 'recoveries'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'), )

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))
    location = relationship("Location")

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, default=0, nullable=False)


class Totals(SurrogatePK, Model):
    """Store the totals for faster retrieveing."""
    CONFIRMED = 'confirmed'
    DEATHS = 'deaths'
    RECOVERED = 'recovered'

    __tablename__ = 'totals'

    key = Column(db.String(80), unique=True, nullable=False)
    value = Column(db.String(80), nullable=False)

    @classmethod
    def get_or_create(cls, key):
        instance = cls.query.filter_by(key=key).one_or_none()
        if not instance:
            instance = cls(key=key)
        return instance
