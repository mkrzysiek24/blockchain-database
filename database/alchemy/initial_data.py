from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.alchemy.models import Base, DoctorData, PatientData
from database.alchemy.passwords import hash_password

# Create engine and tables
engine = create_engine("sqlite:///doctors.db")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# Doctor test data
test_data_doctors = [
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

# Add doctors
for name, email, license_number, plain_password in test_data_doctors:
    hashed_password, salt = hash_password(plain_password)
    doctor = DoctorData(
        name=name,
        email=email,
        license_number=license_number,
        hashed_password=hashed_password,
        salt=salt,
    )
    session.add(doctor)


# Patient test data
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem.decode(), public_pem.decode()


# Patient test data
test_data_patients = [
    ("John Patient", "johnp@email.com", "11112L", "patientjohn123"),
    ("Maria Patient", "mariap@email.com", "11113L", "maria789"),
]

# Add patients
for name, email, insurance_number, plain_password in test_data_patients:
    hashed_password, salt = hash_password(plain_password)
    private_key, public_key = generate_key_pair()
    patient = PatientData(
        name=name,
        email=email,
        insurance_number=insurance_number,
        hashed_password=hashed_password,
        salt=salt,
        public_key=public_key,
        private_key=private_key,
    )
    session.add(patient)

session.commit()
