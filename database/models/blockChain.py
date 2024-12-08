import json
import sys
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from .block import Block
from .doctor import Doctor
from .transaction import Transaction


# zaimplementować to, żeby blockchain sprawdzał poprawność każdego z bloku
# walidacja blockchainu jeszcze jakaś oprócz sprawdzania haszy?
# zależność od czasu, a nie liczby emitowanych transakcji
class BlockChain(BaseModel):
    chain: List[Block] = Field(default_factory=list)
    emitted_transactions: List[Transaction] = Field(default_factory=list)
    doctors: List[Doctor] = Field(default_factory=list)

    def __init__(self):
        super().__init__()
        self.chain = []

    # blockchain validation
    # checking if block at chain[i] has prev "pointer" at chain[i-1] (hashes are right)
    # also, validating all blocks
    def is_valid(self, difficulty: int) -> bool:
        if len(self.chain) == 0:
            return True
        for i in range(0, len(self.chain)-1):
            if self.chain[i+1].previous_hash != self.chain[i].hash or not self.chain[i].is_valid(difficulty):
                return False
        if self.chain[-1].is_valid(difficulty):
            return True

    def _add_block(self):
        new_data = self.emitted_transactions[:2]
        self.emitted_transactions = self.emitted_transactions[2:]

        # Create new block
        last_block = self.chain[-1]
        # new_id = last_block.id + 1
        new_block = Block.create_block(new_data, last_block.hash)

        for transaction in new_data:
            # TODO: Error handling
            public_key = next(
                (doctor.public_key for doctor in self.doctors if doctor.id == transaction.doctor_id),
                None,
            )
            if public_key is not None:
                new_block.add_transaction(transaction, public_key)

        # Add to blockchain
        if len(new_block.data) >= 1:
            self.chain.append(new_block)

    def emit_transaction(self, transaction: Transaction):
        self.emitted_transactions.append(transaction)

        if len(self.emitted_transactions) >= 1:
            self._add_block()


