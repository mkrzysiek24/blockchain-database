from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DoctorData(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    license_number = Column(String, nullable=True)

    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)

