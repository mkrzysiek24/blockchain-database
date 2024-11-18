import base64
from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, Json
from typing import Optional
from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))    
    doctor_id: int
    patient_id: int
    data: Json[Any]
    date: datetime
    signature: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def is_valid(self, public_key: str) -> bool:
        try:
            if not self.signature:
                raise ValueError("No signature provided")
            
            # Decode the base64-encoded signature
            signature_bytes = base64.b64decode(self.signature)
            
            # Serialize the transaction data for verification
            transaction_data = (
                f"{self.id}|"
                f"{self.doctor_id}|"
                f"{self.patient_id}|"
                f"{self.date.isoformat()}|"
                f"{self.data}"
            ).encode()

            # Verify the signature using the doctor's public key
            public_key.verify(
                signature_bytes,
                transaction_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            return False
