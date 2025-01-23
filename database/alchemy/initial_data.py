from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.alchemy.doctorData import DoctorData, Base
from database.alchemy.passwords import hash_password


engine = create_engine("sqlite:///../../doctors.db")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

test_data = [
    ("John Smith", "john.smith@email.com", "10001", "doctorjohn123"),
    ("Maria Lopez", "maria.lopez@email.com", "10002", "maria789"),
    ("Michael Davis", "michael.davis@email.com", "10003", "passwordsecure1"),
    ("Emily Johnson", "emily.johnson@email.com", "10004", "emily1111"),
    ("David White", "david.white@email.com", "10005", "davidpassword456"),
    ("Sarah Brown", "sarah.brown@email.com", "10006", "sarahB22"),
    ("William Moore", "william.moore@email.com", "10007", "william4207"),
    ("Lisa Taylor", "lisa.taylor@email.com", "10008", "lisasecurepass"),
    ("James Anderson", "james.anderson@email.com", "10009", "james7890"),
    ("Laura Thomas", "laura.thomas@email.com", "10010", "laurapwd999"),
]

# Add doctors to the session
for name, email, license_number, plain_password in test_data:
    hashed_password, salt = hash_password(plain_password)
    doctor = DoctorData(
        name=name,
        email=email,
        license_number=license_number,
        hashed_password=hashed_password,
        salt=salt,
    )
    session.add(doctor)

session.commit()



