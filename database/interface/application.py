import json
from logging import getLogger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database.alchemy import DoctorData, hash_password, verify_password
from database.models import *

logger = getLogger(__name__)

engine = create_engine("sqlite:///../doctors.db")
Session = sessionmaker(bind=engine)


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
            salt=salt
        )

        self.session.add(doctor)
        self.session.commit()
        logger.info("Doctor registered successfully!")
        return True

    def _login(self):
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
                email=record.email
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
            email=record.email
        )
        logger.info(f"Logged in as {self.doctor.name}")
        return True

    def _emit_transaction(self):
        if self.doctor:
            # providing patient's id - obligatory
            patient_id = int(input("Patient id: "))

            # providing additional data - optional
            data = {"notes": ""}
            while True:
                print("Add data to transaction; to stop, leave key blank")
                key = input("key: ")
                if key == "":
                    break
                value = input("value: ")
                data[key] = value

            # create transaction
            transaction = self.doctor.create_transaction(
                patient_id=patient_id,
                data=json.dumps(data)
            )

            # emit transaction to blockchain
            self.network.emit_transaction(
                self.facility_id,
                transaction
            )
            logger.info("Transaction emitted successfully")
        else:
            logger.error("Can't emit transaction while not logged in")

    def _show_blockchain(self):
        for block in self.network.facilities[self.facility_id].chain:
            print(f"Block {block.id}, with {len(block.transactions)} transactions; added at {block.timestamp.time()}")

    def main_loop(self):
        inp = "0"
        while inp != "3":
            inp = input("Choose 1. to emit new transaction, 2. to show current blockchain or 3. to leave\n")
            if inp == "1":
                self._emit_transaction()
            elif inp == "2":
                self._show_blockchain()

    def run(self):
        print(f"Welcome in Facility {self.facility_id} blockchain system!")
        authorized = False
        while not authorized:
            inp = input("Choose 1 to log in and 2 to sign up: ")
            if inp == "1":
                authorized = self._login()
            elif inp == "2":
                authorized = self._sign_up()
        self.main_loop()
        record = self.session.query(DoctorData).filter(DoctorData.id == 1).first()

    def run(self):
        print(f"Welcome in Facility {self.facility_id} blockchain system!")
        authorized = False
        while not authorized:
            inp = input("Choose 1 to log in and 2 to sign up: ")
            if inp == "1":
                authorized = self._login()
            elif inp == "2":
                authorized = self._sign_up()
        self.main_loop()
