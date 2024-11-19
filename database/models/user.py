from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    public_key: Optional[str] = None
    _private_key: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Generowanie kluczy RSA
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Serializowanie klucza prywatnego do formatu PEM
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serializowanie klucza publicznego do formatu PEM
        public_key_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Przypisanie kluczy do atrybutów w formacie PEM
        self._private_key = private_key_pem.decode()
        self.public_key = public_key_pem.decode()
