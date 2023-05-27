from geoalchemy2 import Geometry
from sqlalchemy import Column, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Country(Base):
    __tablename__ = 'countries_with_center'

    id = Column('gid', Integer, primary_key=True)
    ISO_code = Column('code', Text)
    name = Column('name_en', Text)
    boundaries = Column('boundary', Geometry)
    center = Column('center', Geometry)
