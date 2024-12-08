from datetime import datetime
from logging import getLogger
from typing import Optional
from uuid import uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from pydantic import BaseModel, Field, field_validator

from .transaction import Transaction

logger = getLogger(__name__)


class Block(BaseModel):
    id: int = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    transactions: list[Transaction]
    previous_hash: str
    hash: Optional[str] = None
    nonce: int = Field(default=0)


    @classmethod
    def create_block(cls, transactions: list, previous_hash: str, difficulty: int = 4):
        block = cls(
            transactions=transactions,
            previous_hash=previous_hash,
        )
        block.timestamp = datetime.now()
        block.proof_of_work(difficulty)
        return block

    @field_validator("transactions")
    def validate_transactions(cls, transactions: list[Transaction]):
        if not transactions:
            raise ValueError("Block must contain at least one transaction")
        return transactions

    def proof_of_work(self, difficulty: int):
        logger.info(f"Starting proof of work with difficulty: {difficulty} for block with id: {self.id}")
        target = "0" * difficulty
        self.nonce = 0
        self.hash = self._calculate_hash()
        logger.debug(f"Initial hash: {self.hash}")

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self._calculate_hash()
            logger.debug(f"Nonce: {self.nonce}, Hash: {self.hash}")

        logger.info(f"Proof of work completed. Final hash: {self.hash}")

    def _calculate_hash(self) -> str:
        block_data = (
            f"{self.id}|"
            f"{self.timestamp}|"
            f"{[transaction.model_dump() for transaction in self.transactions]}|"
            f"{self.previous_hash}|"
            f"{self.nonce}"
        ).encode()

        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(block_data)
        return digest.finalize().hex()

    def is_valid(self, difficulty: int) -> bool:
        logger.info("Validating block...")
        if not self.hash:
            logger.error("Hash is missing, invalid block")
            return False

        target = "0" * difficulty
        valid = self.hash == self._calculate_hash() and self.hash.startswith(target)
        logger.info("Block is valid" if valid else "Block is invalid")
        return valid
