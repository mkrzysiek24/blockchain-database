from typing import List

from pydantic import BaseModel

from .block import Block
from .doctor import Doctor
from .transaction import Transaction


class BlockChain(BaseModel):
    chain: List[Block] = []
    emitted_transactions: List[Transaction] = []
    doctors: List[Doctor] = []

    # zakładamy, że nasz chain zaczyna się zawsze od pustego bloku
    def __init__(self):
        super().__init__()
        root_block = Block(id=0, hash="-1", prev_hash="-1", prev_id=-1)

        self.chain = [root_block]

    def _add_block(self):
        # lista transakcji bloku
        new_data = self.emitted_transactions[:2]
        self.emitted_transactions = self.emitted_transactions[2:]

        # zbieramy informacje nowego bloku
        last_block = self.chain[-1]
        new_id = last_block.id + 1
        new_hash = self.calculate_hash(new_id, new_data, last_block.hash)

        # tworzymy obiekt bloku
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
            new_block.add_transaction(transaction, public_key)

        # dodajemy go do blockchainu
        if len(new_block.data) >= 1:
            self.chain.append(new_block)

    def emit_transaction(self, transaction: Transaction):
        self.emitted_transactions.append(transaction)

        if len(self.emitted_transactions) >= 1:
            self._add_block()

    def is_valid(self) -> bool:
        return True

    @staticmethod
    def calculate_hash(block_id, data: List[Transaction], prev_hash: str) -> str:

        hash_string = str(block_id) + str(00000000000) + prev_hash
        return hash_string  # i potem jakies sha__ ??
        # return sha256(hash_string.encode()).hexdigest()
