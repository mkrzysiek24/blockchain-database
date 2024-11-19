from typing import Any, List, Optional

from pydantic import BaseModel, Json

from .transaction import Transaction


class Block(BaseModel):
    id: int
    data: List[Transaction] = []
    hash: str
    prev_hash: str
    prev_id: int

    def add_transaction(self, new_transaction: Transaction, public_key: str):
        # Walidacja transakcji - sprawdzenie podpisu

        if not new_transaction.is_valid(public_key):
            raise Exception("Error")

        # Dodanie transakcji
        self.data.append(new_transaction)
