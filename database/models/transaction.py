import base64
from datetime import datetime
from typing import Any, Dict, Optional, cast
from uuid import uuid4

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from pydantic import BaseModel, ConfigDict, Field, Json, field_validator


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    doctor_id: int
    patient_id: int
    data: Json[Any]  # This can hold both regular and encrypted data
    date: datetime
    signature: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("data")
    def validate_data(cls, value: Optional[dict]):
        if not value:
            raise ValueError("Data cannot be empty")

        # If this is encrypted data, validate encryption fields
        if isinstance(value, dict) and "encrypted_data" in value:
            required_fields = {"encrypted_data", "iv", "doctor_key", "patient_key"}
            if not all(field in value for field in required_fields):
                raise ValueError(f"Encrypted data must contain all required fields: {required_fields}")

        return value

    @field_validator("date")
    def validate_date(cls, value: datetime):
        if not value:
            raise ValueError("Date is empty")
        if value > datetime.now():
            raise ValueError("Date can't be in future")
        return value

    @field_validator("doctor_id")
    def validate_doctor_id(cls, value: int):
        if not value or value < 0:
            raise ValueError("Doctor id not provided")
        return value

    @field_validator("patient_id")
    def validate_patient_id(cls, value: int):
        if not value or value < 0:
            raise ValueError("Patient id not provided")
        return value

    def serialize(self) -> str:
        """
        Creates a string representation of the transaction for signing/verification

        """
        transaction_data = (
            f"{self.id}|" f"{self.doctor_id}|" f"{self.patient_id}|" f"{self.date.isoformat()}|" f"{self.data}"
        )
        return transaction_data

    def is_valid(self, public_key_pem: str) -> bool:
        """
        Verifies the transaction signature using the doctor's public key
        """
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

    def is_encrypted(self) -> bool:
        """
        Checks if the transaction data is encrypted
        """
        return (
            isinstance(self.data, dict)
            and "encrypted_data" in self.data
            and "iv" in self.data
            and "doctor_key" in self.data
            and "patient_key" in self.data
        )

    def get_encryption_package(self) -> Optional[Dict[str, str]]:
        """
        Returns the encryption package if the data is encrypted
        """
        if self.is_encrypted():
            return {
                "encrypted_data": self.data["encrypted_data"],
                "iv": self.data["iv"],
                "doctor_key": self.data["doctor_key"],
                "patient_key": self.data["patient_key"],
            }
        return None
