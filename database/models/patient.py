from typing import Optional, Any
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from pydantic import BaseModel

from .user import User
from .transaction import Transaction

class Patient(User):
    insurance_number: Optional[str] = None
    
    def decrypt_transaction(self, transaction: Transaction) -> Any:
        """Decrypts transaction data using patient's key"""
        return self.decrypt_transaction_data(transaction, 'patient_key')