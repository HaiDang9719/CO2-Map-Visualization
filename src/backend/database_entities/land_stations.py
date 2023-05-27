from sqlalchemy import Column, Text, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LandStations(Base):
    __tablename__ = 'land_stations'

    station_id = Column('station_id', Text, primary_key=True)
    name = Column('name', Text)
    latitude = Column('latitude', Float)
    longitude = Column('longitude', Float)
    elevation = Column('elevation', Float)
