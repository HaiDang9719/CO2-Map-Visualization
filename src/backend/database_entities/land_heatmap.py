from sqlalchemy import Column, Text, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LandHeatmap(Base):
    __tablename__ = 'land_heatmap_grid'

    id = Column('id', Integer, primary_key=True)
    latitude = Column('latitude', Float)
    longitude = Column('longitude', Float)
    slope = Column('slope', Float)
