import base64
from datetime import datetime
from pydantic import Json
from models.transaction import Transaction
from models.user.user import User
from models.user.patient import Patient
from typing import Any
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class Doctor(User):
    license_number: str

    def create_transaction(self, patient_id: int, data: Json[Any]) -> Transaction:
        transaction = Transaction(
            doctor_id=self.id,
            patient_id=patient_id,
            data=data,
            date=datetime.now()
        )
        
        # Serialize the transaction data
        transaction_data = (
            f"{transaction.id}|"
            f"{transaction.doctor_id}|"
            f"{transaction.patient_id}|"
            f"{transaction.date.isoformat()}|"
            f"{transaction.data}"
        ).encode()

        # Sign the transaction data with the doctor's private key
        transaction_signature = self._private_key.sign(
            transaction_data,
            # Use PSS padding with SHA-256
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encode the signature in base64
        transaction.signature = base64.b64encode(transaction_signature).decode()

        return transaction