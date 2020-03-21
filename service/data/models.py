from sqlalchemy import desc, UniqueConstraint

from covid19.database import SurrogatePK, Model, Column, db, relationship


class Location(SurrogatePK, Model):
    """Location of the collected data."""

    __tablename__ = 'locations'
    __table_args__ = (UniqueConstraint('country', 'province'), )

    country = Column(db.String(80), nullable=False)
    country_code = Column(db.String(10), nullable=False)
    longitude = Column(db.Integer, nullable=False)
    latitude = Column(db.Integer, nullable=False)
    last_updated = Column(db.DateTime, nullable=True)
    province = Column(db.String(80), nullable=True)

    confirmations = relationship("Confirmed", backref="location")
    deaths = relationship("Deaths", backref="location")
    recoveries = relationship("Recovered", backref="location")

    @classmethod
    def get_by_country_and_province(cls, country, province):
        return cls.query.filter(Location.country == country, Location.province == province).one()

    @classmethod
    def exists(cls, country, province):
        return cls.query.filter(Location.country == country, Location.province == province).count() >= 1


class Confirmed(SurrogatePK, Model):
    """Total number of confirmed cases at a certain moment in a location."""

    __tablename__ = 'confirmations'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'), )

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, nullable=False)

    @classmethod
    def get_latest(cls, location=None):
        return cls.query().filter_by(location=location).order_by(desc(Confirmed.moment)).one()

    @classmethod
    def exists(cls, confirmed):
        return cls.query.filter(
            Confirmed.location_id == confirmed.location_id,
            Confirmed.amount == confirmed.amount,
            Confirmed.moment == confirmed.moment,
        ).count() >= 1


class Deaths(SurrogatePK, Model):
    """Total number of deaths at a certain moment in a location."""

    __tablename__ = 'deaths'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'), )

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, nullable=False)

    @classmethod
    def get_latest(cls, location=None):
        return cls.query().filter_by(location=location).order_by(desc(Deaths.moment)).one()

    @classmethod
    def exists(cls, deaths):
        return cls.query.filter(
            Deaths.location_id == deaths.location_id,
            Deaths.amount == deaths.amount,
            Deaths.moment == deaths.moment,
        ).count() >= 1


class Recovered(SurrogatePK, Model):
    """Total number of recoveries at a certain moment in a location."""

    __tablename__ = 'recoveries'
    __table_args__ = (UniqueConstraint('location_id', 'moment', 'amount'), )

    location_id = Column(db.Integer, db.ForeignKey('locations.id'))

    moment = Column(db.DateTime, nullable=False)
    amount = Column(db.Integer, nullable=False)

    @classmethod
    def get_latest(cls, location=None):
        return cls.query().filter_by(location=location).order_by(desc(Recovered.moment)).one()

    @classmethod
    def exists(cls, recovered):
        return cls.query.filter(
            Recovered.location_id == recovered.location_id,
            Recovered.amount == recovered.amount,
            Recovered.moment == recovered.moment,
        ).count() >= 1
