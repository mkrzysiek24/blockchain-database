import base64
import json
import os
from datetime import datetime
from typing import Any, Optional, cast

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pydantic import Json

from .transaction import Transaction
from .user import User


class Doctor(User):
    license_number: Optional[str] = None

    def create_transaction(self, patient_id: int, data: Json[Any], patient_public_key_pem: str) -> Transaction:
        """Creates and signs an encrypted transaction"""
        try:
            decoded_data = json.loads(data) if isinstance(data, str) else data
            if not decoded_data:
                raise ValueError("Transaction data cannot be empty")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON data")
        # Create initial transaction
        transaction = Transaction(
            doctor_id=self.id,
            patient_id=patient_id,
            data=json.dumps(data),
            date=datetime.now(),
        )

        # Generate AES key and IV for encryption
        aes_key = os.urandom(32)
        iv = os.urandom(16)

        # Encrypt the data using AES
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        # Convert data to bytes and pad
        data_bytes = str(data).encode("utf-8")
        padded_data = self._pad_data(data_bytes)
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Encrypt AES key for both doctor and patient
        patient_public_key = serialization.load_pem_public_key(
            patient_public_key_pem.encode(),
        )
        doctor_public_key = serialization.load_pem_public_key(
            self.public_key.encode(),
        )

        # Store encrypted keys and IV in the data field
        transaction.data = {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "iv": base64.b64encode(iv).decode(),
            "doctor_key": base64.b64encode(
                doctor_public_key.encrypt(
                    aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                ),
            ).decode(),
            "patient_key": base64.b64encode(
                patient_public_key.encrypt(
                    aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                ),
            ).decode(),
        }

        # Sign the transaction
        transaction_data = transaction.serialize().encode()
        private_key = serialization.load_pem_private_key(
            self.private_key.encode(),
            password=None,
        )
        private_key = cast(RSAPrivateKey, private_key)

        signature = private_key.sign(
            transaction_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        transaction.signature = base64.b64encode(signature).decode()

        return transaction

    def decrypt_transaction(self, transaction: Transaction) -> Any:
        """Decrypts transaction data using doctor's key"""
        return self.decrypt_transaction_data(transaction, "doctor_key")

    @staticmethod
    def _pad_data(data: bytes) -> bytes:
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    @staticmethod
    def _unpad_data(padded_data: bytes) -> bytes:
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
