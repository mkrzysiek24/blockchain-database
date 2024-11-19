from typing import List

from pydantic import BaseModel, Field

from .transaction import Transaction


class Block(BaseModel):
    id: int
    data: List[Transaction] = Field(default_factory=list)
    hash: str
    prev_hash: str
    prev_id: int

    def add_transaction(self, new_transaction: Transaction, public_key: str):
        # Validate transaction - check signature
        if not new_transaction.is_valid(public_key):
            raise Exception("Error")

        # Add transaction to block
        self.data.append(new_transaction)
