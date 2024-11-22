from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import BaseModel, Field, model_validator


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
