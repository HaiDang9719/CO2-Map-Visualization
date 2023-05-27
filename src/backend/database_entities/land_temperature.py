from sqlalchemy import Column, Text, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LandTemperature(Base):
    __tablename__ = 'land_temperature'

    id = Column('id', Integer, primary_key=True)
    station_id = Column('station_id', Text)
    date = Column('date', Date)
    temperature = Column('temperature', Float)
