from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OceanAverageTemperatureAggregated(Base):
    __tablename__ = 'ocean_temperature_average_aggregated'

    year = Column(Date, primary_key=True)
    location = Column(Geometry, primary_key=True)
    average_temperature = Column('Average Temperature', Float)
