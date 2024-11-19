from typing import List

from pydantic import BaseModel, Field

from .block import Block
from .doctor import Doctor
from .transaction import Transaction


class BlockChain(BaseModel):
    chain: List[Block] = Field(default_factory=list)
    emitted_transactions: List[Transaction] = Field(default_factory=list)
    doctors: List[Doctor] = Field(default_factory=list)

    def __init__(self):
        super().__init__()
        root_block = Block(id=0, hash="-1", prev_hash="-1", prev_id=-1)

        self.chain = [root_block]

    def _add_block(self):
        new_data = self.emitted_transactions[:2]
        self.emitted_transactions = self.emitted_transactions[2:]

        # Create new block
        last_block = self.chain[-1]
        new_id = last_block.id + 1
        new_hash = self.calculate_hash(new_id, new_data, last_block.hash)

        new_block = Block(
            id=new_id,
            hash=new_hash,
            prev_hash=last_block.hash,
            prev_id=last_block.id,
        )

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

    @staticmethod
    def is_valid() -> bool:
        return True

    @staticmethod
    def calculate_hash(block_id, data: List[Transaction], prev_hash: str) -> str:
        # Placeholder hash
        hash_string = str(block_id) + str(00000000000) + prev_hash
        return hash_string
