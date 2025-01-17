import json
from logging import getLogger

from database.models import Doctor, Network

logger = getLogger(__name__)


class Application:

    def __init__(self):
        self.network = Network()
        self.facility_id = "abc"
        self.doctor = None
        # todo: choosing facility and validation
        print(f"Welcome in {self.facility_id} blockchain system!")
        self.network.create_facility_chain(self.facility_id)

    # todo: validation from network; also, add option to log in
    def _sign_up(self):
        doctor_id = int(input("Your doctor id: "))
        doctor_name = input("Your name: ")
        doctor_email = input("Your email: ")
        self.doctor = Doctor(
            id=doctor_id,
            name=doctor_name,
            email=doctor_email,
        )
        logger.info("logged as default doctor")

    # for testing purpose only
    def _log_as_default(self):
        self.doctor = Doctor(
            id=1234,
            name="doctor_name",
            email="doctor@gmail.com",
        )
        logger.info("logged as default doctor")

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
                data=json.dumps(data),
            )

            # emit transaction to blockchain
            self.network.emit_transaction(
                self.facility_id,
                transaction,
            )
            logger.info("Transaction emitted successfully")
        else:
            logger.error("Can't emit transaction while not logged in")

    # for testing purpose only
    def _show_blockchain(self):
        for block in self.network.facilities[self.facility_id].chain:
            print(f"Block {block.id}, with {len(block.transactions)} transactions; added at {block.timestamp.time()}")

    def main_loop_testing(self):
        self._log_as_default()
        inp = "0"
        while inp != "3":
            inp = input("Choose 1. to emit new transaction, 2. to show current blockchain or 3. to leave\n")
            if inp == "1":
                self._emit_transaction()
            elif inp == "2":
                self._show_blockchain()
