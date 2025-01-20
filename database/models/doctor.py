import base64
from datetime import datetime
from typing import Any, Optional, cast

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509 import Certificate, load_pem_x509_certificate
from pydantic import Json

from .transaction import Transaction
from .user import User


class Doctor(User):
    license_number: Optional[str] = None

    def load_public_key(self, pem_data: str) -> Certificate:
        return load_pem_x509_certificate(pem_data.encode())

    def create_transaction(self, patient_id: int, data: Json[Any], patient_public_key_pem: str) -> Transaction:
        transaction = Transaction(
            doctor_id=self.id,
            patient_id=patient_id,
            data=data,
            date=datetime.now(),
        )

        # public keys of the doctor and the patient
        doctor_public_key = self.load_public_key(self.public_key)
        patient_public_key = self.load_public_key(patient_public_key_pem)

        # Encrypt using both pyblic keys
        encrypted_data = transaction.encrypt_for_recipients([doctor_public_key, patient_public_key])
        transaction.data = encrypted_data


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

        transaction.signature = base64.b64encode(transaction_signature).decode()

        return transaction