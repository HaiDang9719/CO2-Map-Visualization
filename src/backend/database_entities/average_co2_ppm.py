from sqlalchemy import Column, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AvgCO2PPM(Base):
    __tablename__ = 'co2_ppm'

    id = Column('id', Integer, primary_key=True)
    date = Column('date', Date)
    monthly_avg = Column('monthly_avg', Float)
