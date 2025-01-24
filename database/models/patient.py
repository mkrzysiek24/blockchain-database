from typing import Any, Optional

from .transaction import Transaction
from .user import User


class Patient(User):
    insurance_number: Optional[str] = None

    def decrypt_transaction(self, transaction: Transaction) -> Any:
        """Decrypts transaction data using patient's key"""
        return self.decrypt_transaction_data(transaction, "patient_key")
