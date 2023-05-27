from geoalchemy2 import Geometry
from sqlalchemy import Column, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Ocean(Base):
    __tablename__ = 'oceans_with_center'

    id = Column('gid', Integer, primary_key=True)
    type = Column('featurecla', Text)
    name = Column('name_en', Text)
    boundaries = Column('boundary', Geometry)
    center = Column(Geometry)
