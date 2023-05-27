from database_entities.country import Country
from sqlalchemy import Column, Date, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CountryWithAverageTemperature(Base):
    __tablename__ = 'land_temperature_average'

    country_id = Column('CountryID', Text, ForeignKey(Country.id), primary_key=True)
    country = relationship(Country)
    year = Column(Date, primary_key=True)
    average_temperature = Column('Average Temperature', Float)
