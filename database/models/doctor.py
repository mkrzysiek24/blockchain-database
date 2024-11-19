import base64
from datetime import datetime
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pydantic import Json

from .transaction import Transaction
from .user import User


class Doctor(User):
    license_number: Optional[str] = None

    def create_transaction(self, patient_id: int, data: Json[Any]) -> Transaction:
        transaction = Transaction(doctor_id=self.id, patient_id=patient_id, data=data, date=datetime.now())

        # Serialize the transaction data
        transaction_data = (
            f"{transaction.id}|"
            f"{transaction.doctor_id}|"
            f"{transaction.patient_id}|"
            f"{transaction.date.isoformat()}|"
            f"{transaction.data}"
        ).encode()

        # Deserializowanie klucza prywatnego (format PEM)
        private_key_pem = self._private_key.encode()  # Zakładając, że _private_key jest w formacie PEM
        private_key = serialization.load_pem_private_key(
            private_key_pem, password=None  # Jeżeli prywatny klucz jest zaszyfrowany, należy podać hasło
        )

        # Podpisywanie danych transakcji
        transaction_signature = private_key.sign(
            transaction_data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        # Kodowanie podpisu w base64
        transaction.signature = base64.b64encode(transaction_signature).decode()

        return transaction
