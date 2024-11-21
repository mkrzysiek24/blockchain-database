import base64
from datetime import datetime
from typing import Any, Optional, cast
from uuid import uuid4

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from pydantic import BaseModel, Field, Json, field_validator


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    doctor_id: int
    patient_id: int
    data: Json[Any]
    date: datetime
    signature: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @field_validator("data")
    def validate_data_not_empty_json(cls, value):
        if not value or (isinstance(value, dict) and not value):
            raise ValueError("Data cannot be empty")
        return value

    def is_valid(self, public_key_pem: str) -> bool:
        try:
            if not self.signature:
                raise ValueError("No signature provided")

            if not public_key_pem:
                raise ValueError("Public key is required and cannot be None")

            # Decode the base64-encoded signature
            signature_bytes = base64.b64decode(self.signature)

            # Serialize the transaction data for verification
            transaction_data = (
                f"{self.id}|" f"{self.doctor_id}|" f"{self.patient_id}|" f"{self.date.isoformat()}|" f"{self.data}"
            ).encode()

            # Load the public key from PEM format
            public_key = serialization.load_pem_public_key(public_key_pem.encode())

            # Cast public key to RSAPublicKey
            public_key = cast(RSAPublicKey, public_key)

            # Verify the signature using the doctor's public key
            public_key.verify(
                signature_bytes,
                transaction_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            return False
