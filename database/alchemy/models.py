from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from database.alchemy.engine import engine

Base = declarative_base()


class PatientData(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    insurance_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    private_key = Column(String, nullable=False)


class DoctorData(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    license_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)


# Create tables
Base.metadata.create_all(engine)
