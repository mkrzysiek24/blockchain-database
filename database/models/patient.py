from typing import Optional
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from pydantic import BaseModel

from .user import User


class Patient(User):
    insurance_number: Optional[str] = None

    def decrypt_transaction(self, encrypted_data: bytes) -> str:

        private_key_pem = self.private_key.encode()
        private_key = load_pem_private_key(
            private_key_pem,
            password=None,
        )

     
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return decrypted_data.decode()