from sqlalchemy import Column, Text, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class YearlyStationAverage(Base):
    __tablename__ = 'yearly_average_temperature_by_station'

    station_id = Column('station_id', Text, primary_key=True)
    year = Column('Year', Date, primary_key=True)
    temperature = Column('Yearly avg Temperature', Float)
