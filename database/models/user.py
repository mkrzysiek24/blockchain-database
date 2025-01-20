from typing import Optional, Any, cast
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pydantic import BaseModel, Field, model_validator, Json
from .transaction import Transaction

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    private_key: str = Field(default=None)
    public_key: str = Field(default=None)

    @model_validator(mode="before")
    def generate_keys(cls, values):
        if not values.get("private_key"):
            values["private_key"] = cls.generate_private_key_pem()
        if not values.get("public_key"):
            values["public_key"] = cls.generate_public_key_pem(values.get("private_key"))
        return values

    @staticmethod
    def generate_private_key_pem():
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        return private_key_pem

    @staticmethod
    def generate_public_key_pem(private_key_pem: str):
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
        )
        public_key_pem = (
            private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )
        return public_key_pem

    def decrypt_transaction_data(self, transaction: Transaction, key_type: str) -> Any:
        """
        Decrypts transaction data using the user's private key
        key_type: either 'doctor_key' or 'patient_key'
        """
        if not transaction.is_encrypted():
            raise ValueError("Transaction data is not encrypted")

        encrypted_package = transaction.get_encryption_package()
        if not encrypted_package:
            raise ValueError("Could not get encryption package")

        # Decode all base64 encoded data
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
        iv = base64.b64decode(encrypted_package['iv'])
        encrypted_key = base64.b64decode(encrypted_package[key_type])

        # Decrypt the AES key using private key
        private_key = serialization.load_pem_private_key(
            self.private_key.encode(),
            password=None
        )
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the data using the AES key
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding and convert back to original format
        unpadded_data = self._unpad_data(padded_data)
        return eval(unpadded_data.decode())

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