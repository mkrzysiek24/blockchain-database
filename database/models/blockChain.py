import json
import sys
from datetime import datetime, timedelta
from logging import getLogger
from typing import List

from pydantic import BaseModel, Field

from .block import Block
from .doctor import Doctor
from .transaction import Transaction


logger = getLogger(__name__)


class BlockChain(BaseModel):
    chain: List[Block] = Field(default_factory=list)
    emitted_transactions: List[Transaction] = Field(default_factory=list)
    doctors: List[Doctor] = Field(default_factory=list)
    last_block_added: datetime = Field(default_factory=datetime.now)    # last time a block was added
    time_delta: timedelta = Field(default=timedelta(seconds=30))        # time between adding blocks

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

        # if there are no transactions to add, return
        if len(self.emitted_transactions) == 0:
            return

        # Create new block
        if len(self.chain) == 0:
            new_block = Block.create_block(self.emitted_transactions, "0" * 64)
        else:
            last_block = self.chain[-1]
            new_block = Block.create_block(self.emitted_transactions, last_block.hash)

        for transaction in self.emitted_transactions:
            # TODO: Error handling
            public_key = next(
                (doctor.public_key for doctor in self.doctors if doctor.id == transaction.doctor_id),
                None,
            )
            if public_key is not None:
                new_block.add_transaction(transaction, public_key)

        self.chain.append(new_block)
        self.last_block_added = datetime.now()
        self.emitted_transactions = []

    def emit_transaction(self, transaction: Transaction):
        self.emitted_transactions.append(transaction)

        if datetime.now() - self.last_block_added >= self.time_delta:
            self._add_block()



