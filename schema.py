from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, BigInteger, Boolean, Sequence, Index, Date
from sqlalchemy.orm import relationship, backref

from base import Base


class Pilot(Base):
    __tablename__ = 'pilots'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    losses = relationship("KillMail")
    attackers = relationship("Attacker")

    def __repr__(self):
        return "<Pilot(name='%s')>" % self.name


class Alliance(Base):
    __tablename__ = 'alliances'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    losses = relationship("KillMail")
    attackers = relationship("Attacker")

    def __repr__(self):
        return "<Alliance(name='%s')>" % self.name


class Corporation(Base):
    __tablename__ = 'corporations'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    losses = relationship("KillMail")
    attackers = relationship("Attacker")

    def __repr__(self):
        return self.name


class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    solarsystems = relationship("SolarSystem", backref="regions")

    def __repr__(self):
        return "<Region(name='%s')>" % self.name


class Constellation(Base):
    __tablename__ = 'constellations'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)


class SolarSystem(Base):
    __tablename__ = 'solarsystems'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    constellation_id = Column(Integer, ForeignKey('constellations.id'), nullable=False)
    security = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    killmails = relationship("KillMail")

    def __repr__(self):
        return "<Solarsystem(name='%s')>" % self.name


class Attacker(Base):
    __tablename__ = 'attackers'

    id = Column(Integer, Sequence('attackers_id_seq'), primary_key=True)
    pilot_id = Column(Integer, ForeignKey('pilots.id'))
    killmail_id = Column(Integer, ForeignKey('killmails.id'), nullable=False)
    corporation_id = Column(Integer, ForeignKey('corporations.id'))
    alliance_id = Column(Integer, ForeignKey('alliances.id'))
    ship_id = Column(Integer, ForeignKey('evetypes.id'))
    weapon_id = Column(Integer, ForeignKey('evetypes.id'))
    damage = Column(Integer, nullable=False)
    killingblow = Column(Boolean, nullable=False)


class KillMail(Base):
    __tablename__ = 'killmails'

    id = Column(Integer, primary_key=True)
    pilot_id = Column(Integer, ForeignKey('pilots.id'))
    solarsystem_id = Column(Integer, ForeignKey('solarsystems.id'), nullable=False)
    corporation_id = Column(Integer, ForeignKey('corporations.id'), nullable=False)
    alliance_id = Column(Integer, ForeignKey('alliances.id'))
    solarsystem_id = Column(Integer, ForeignKey('solarsystems.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    ship_id = Column(Integer, ForeignKey('evetypes.id'), nullable=False)
    attackers = relationship("Attacker", backref="killmails")


class EveCategory(Base):
    __tablename__ = 'evecategories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    published = Column(Boolean, nullable=True)


class EveGroup(Base):
    __tablename__ = 'evegroups'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    category_id = Column(Integer, ForeignKey('evecategories.id'), nullable=False)
    icon_id = Column(Integer)
    anchorable = Column(Boolean, nullable=False)
    anchored = Column(Boolean, nullable=False)
    fittable_non_singleton = Column(Boolean, nullable=False)
    published = Column(Boolean, nullable=False)
    use_base_price = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<EveGroup(name='%s')>" % self.name


class EveType(Base):
    __tablename__ = 'evetypes'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('evegroups.id'), nullable=False)
    name = Column(String(255))
    published = Column(Boolean, nullable=False)
    portion_size = Column(Integer, nullable=False)

    radius = Column(Float)
    volume = Column(Float)
    capacity = Column(Float)
    mass = Column(Float)
    race_id = Column(Float)
    sof_faction_name = Column(String(50))
    base_price = Column(Float)
    marketgroup_id = Column(Integer)
    graphic_id = Column(Integer)
    sound_id = Column(Integer)

    def __repr__(self):
        return "<Evetype(name='%s')>" % self.name


class Drop(Base):
    __tablename__ = 'drops'

    id = Column(Integer, Sequence('attackers_id_seq'), primary_key=True)
    killmail_id = Column(Integer, ForeignKey('killmails.id'), nullable=False)
    evetype_id = Column(Integer, ForeignKey('evetypes.id'), nullable=False)
    dropped = Column(Integer, nullable=False)
    destroyed = Column(Integer, nullable=False)
    singleton = Column(Boolean, nullable=False)
    flag = Column(Integer)


class PriceCurrent(Base):
    __tablename__ = 'pricecurrent'

    id = Column(Integer, Sequence('pricecurrent_id_seq'), primary_key=True)
    evetype_id = Column(Integer, ForeignKey('evetypes.id'), nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)


class PriceHistory(Base):
    __tablename__ = 'pricehistory'

    id = Column(Integer, Sequence('pricehistory_id_seq'), primary_key=True)
    evetype_id = Column(Integer, ForeignKey('evetypes.id'), nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    low = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    avg = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    orders = Column(Integer, nullable=False)
    day = Column(Date, nullable=False)


class ItemLossHistory(Base):
    __tablename__ = 'itemlosshistory'

    id = Column(Integer, Sequence('pricehistory_id_seq'), primary_key=True)
    evetype_id = Column(Integer, ForeignKey('evetypes.id'), nullable=False)
    volume = Column(Integer, nullable=False)
    day = Column(Date, nullable=False)


class ScraperStatus(Base):
    __tablename__ = 'scraperstatus'

    id = Column(Integer, Sequence('scraperstatus_id_seq'), primary_key=True)
    source_name = Column(String(50), nullable=False)
    last_scrape = Column(DateTime, nullable=False)
    last_id = Column(Integer, nullable=False)
