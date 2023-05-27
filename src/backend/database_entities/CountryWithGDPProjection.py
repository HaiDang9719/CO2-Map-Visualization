from database_entities.country import Country
from sqlalchemy import Column, Date, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CountryWithGDPProjection(Base):
    __tablename__ = 'gross_domestic_product_change_prediction'

    country_code = Column('Country Identifier', Text, ForeignKey(Country.ISO_code), primary_key=True)
    country = relationship(Country)
    year = Column('Year', Date, primary_key=True)
    gdp_projection = Column('Projected Gross Domestic Product Change', Float)
