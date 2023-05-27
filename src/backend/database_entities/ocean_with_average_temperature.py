from database_entities.ocean import Ocean
from sqlalchemy import Column, Date, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class OceanWithAverageTemperature(Base):
    __tablename__ = 'ocean_temperature_average'

    ocean_id = Column('OceanID', Text, ForeignKey(Ocean.id), primary_key=True)
    ocean = relationship(Ocean)
    year = Column(Date, primary_key=True)
    average_temperature = Column('Average Temperature', Float)
