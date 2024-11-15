from typing import Any, List, Optional

from pydantic import BaseModel, Json

from database.models.transaction import Transaction


class Block(BaseModel):
    id: int
    data: List[Transaction] = []
    hash: str
    prev_hash: str
    prev_id: int

    # póki co identyfikator transakcji to id_bloku i numer transakcji w bloku (indeks w liscie)
    def add_transaction(self, new_transaction: Transaction):
        # Walidacja transakcji - sprawdzenie podpisu
        if not new_transaction.is_valid():
            raise Exception("Error")

        # Dodanie transakcji
        self.data.append(new_transaction)
