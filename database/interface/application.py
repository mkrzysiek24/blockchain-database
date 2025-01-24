import json
from logging import getLogger

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.alchemy import DoctorData, PatientData, hash_password, verify_password
from database.models import Doctor, Network, Patient

logger = getLogger(__name__)

engine = create_engine("sqlite:///doctors.db")
Session = sessionmaker(bind=engine)


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_pem.decode()


def generate_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return private_pem.decode()


class Application:

    def __init__(self):
        self.network = Network()
        self.facility_id = "abc"
        self.doctor = None
        self.session = Session()
        self.network.create_facility_chain(self.facility_id)

    def _sign_up(self):
        doctor_name = input("Your name: ")
        doctor_email = input("Your email: ")
        license_number = input("Your license number: ")
        password = input("Your password: ")

        hashed_password, salt = hash_password(password)

        doctor = DoctorData(
            name=doctor_name,
            email=doctor_email,
            license_number=license_number,
            hashed_password=hashed_password,
            salt=salt,
        )

        self.session.add(doctor)
        self.session.commit()
        logger.info("Doctor registered successfully!")
        return True

    def _login_doctor(self):
        email = input("Your email: ")
        password = input("Your password: ")
        record = self.session.query(DoctorData).filter(DoctorData.email == email).first()

        if not record:
            print("Doctor not found!")
            return False

        if verify_password(password, record.hashed_password, record.salt):
            self.doctor = Doctor(
                id=record.id,
                name=record.name,
                email=record.email,
            )
            print(f"Welcome back, Dr. {record.name}")
            return True
        else:
            print("Incorrect password!")
            return False

    def _log_as_default(self):
        record = self.session.query(DoctorData).filter(DoctorData.id == 1).first()
        self.doctor = Doctor(
            id=record.id,
            name=record.name,
            email=record.email,
        )
        logger.info(f"Logged in as {self.doctor.name}")
        return True

    def _emit_transaction(self):
        if self.doctor:
            patient_id = int(input("Patient id: "))

            patient = self.session.query(PatientData).filter(PatientData.id == patient_id).first()
            if not patient:
                logger.error("Patient not found")
                return

            data = {"notes": ""}
            while True:
                print("Add data to transaction; to stop, leave key blank")
                key = input("key: ")
                if key == "":
                    break
                value = input("value: ")
                data[key] = value

            transaction = self.doctor.create_transaction(
                patient_id=patient_id,
                data=json.dumps(data),
                patient_public_key_pem=patient.public_key,
            )

            self.network.emit_transaction(self.facility_id, transaction)
            logger.info("Transaction emitted successfully")

    def _see_transactions(self):
        if not self.patient:
            logger.error("No patient logged in")
            return

        patient_transactions = []
        for block in self.network.facilities[self.facility_id].chain:
            for transaction in block.transactions:
                if transaction.patient_id == self.patient.id:
                    decrypted_data = self.patient.decrypt_transaction(transaction)
                    patient_transactions.append(
                        {
                            "doctor_id": transaction.doctor_id,
                            "date": transaction.date,
                            "data": decrypted_data,
                        },
                    )

        if not patient_transactions:
            print("No transactions found")
            return

        for tx in patient_transactions:
            doctor = self.session.query(DoctorData).filter(DoctorData.id == tx["doctor_id"]).first()
            print("\n" + "=" * 50)
            print(f"Date: {tx['date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Doctor: Dr. {doctor.name if doctor else 'Unknown'}")
            print("\nMedical Data:")
            for key, value in tx["data"].items():
                print(f"  {key.title()}: {value}")
            print("=" * 50)

    def _show_blockchain(self):
        for block in self.network.facilities[self.facility_id].chain:
            print(f"Block {block.id}, with {len(block.transactions)} transactions; added at {block.timestamp.time()}")

    def main_loop_doc(self):
        while True:
            inp = input("Choose 1. to emit new transaction, 2. to show current blockchain, 3. to leave, 4. to logout\n")
            if inp == "1":
                self._emit_transaction()
            elif inp == "2":
                self._show_blockchain()
            elif inp == "3":
                exit()
            elif inp == "4":
                self.doctor = None
                return self.run()

    def main_loop_patient(self):
        while True:
            inp = input("See all the transaction - press 1, to leave press 2, to logout press 3\n")
            if inp == "1":
                self._see_transactions()
            elif inp == "2":
                exit()
            elif inp == "3":
                self.patient = None
                return self.run()

    def _sign_up_patient(self):
        patient_name = input("Your name: ")
        patient_email = input("Your email: ")
        insurance_number = input("Your insurance number: ")
        password = input("Your password: ")

        hashed_password, salt = hash_password(password)

        # Generate key pair
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

        patient = PatientData(
            name=patient_name,
            email=patient_email,
            insurance_number=insurance_number,
            hashed_password=hashed_password,
            salt=salt,
            public_key=public_pem.decode(),
            private_key=private_pem.decode(),
        )

        self.session.add(patient)
        self.session.commit()
        logger.info("Patient registered successfully!")
        print(f"Your ID is: {patient.id}")
        return True

    def _login_patient(self):
        email = input("Your email: ")
        password = input("Your password: ")
        record = self.session.query(PatientData).filter(PatientData.email == email).first()

        if not record:
            print("Patient not found!")
            return False

        if verify_password(password, record.hashed_password, record.salt):
            self.patient = Patient(
                id=record.id,
                name=record.name,
                email=record.email,
                private_key=record.private_key,
                public_key=record.public_key,
            )
            print(f"Welcome, {record.name}")
            return True
        else:
            print("Incorrect password!")
            return False

    def run(self):
        print(f"Welcome to Facility {self.facility_id} blockchain system!")
        authorized = False
        is_patient = False

        while not authorized:
            user = input("Doctor - choose 1, Patient - choose 2: ")
            inp = input("Choose 1 to log in and 2 to sign up: ")

            if user == "1":  # Doctor
                if inp == "1":
                    authorized = self._login_doctor()
                elif inp == "2":
                    authorized = self._sign_up()
            elif user == "2":  # Patient
                is_patient = True
                if inp == "1":
                    authorized = self._login_patient()
                elif inp == "2":
                    authorized = self._sign_up_patient()

        if is_patient:
            self.main_loop_patient()
        else:
            self.main_loop_doc()
