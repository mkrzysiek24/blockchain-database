import base64
from datetime import datetime
from typing import Any, Optional, cast

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from pydantic import Json

from .transaction import Transaction
from .user import User


class Doctor(User):
    license_number: Optional[str] = None

    def create_transaction(self, patient_id: int, data: Json[Any]) -> Transaction:
        transaction = Transaction(
            doctor_id=self.id,
            patient_id=patient_id,
            data=data,
            date=datetime.now(),
        )

        # Serialize the transaction data
        transaction_data = transaction.serialize().encode()

        # Deserialize private key (PEM format)
        private_key_pem = self.private_key.encode()
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
        )

        # Cast to RSAPrivateKey
        private_key = cast(RSAPrivateKey, private_key)

        # Sign transaction data
        transaction_signature = private_key.sign(
            transaction_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        # Encode signature in base64
        transaction.signature = base64.b64encode(transaction_signature).decode()

        return transaction
