from typing import Dict, Set

from pydantic import BaseModel, Field

from .blockChain import BlockChain
from .transaction import Transaction


class Network(BaseModel):
    num_facilities: int = Field(default=1)
    facilities: Dict[str, BlockChain] = Field(default_factory=dict)
    doctors: Set[str] = Field(default_factory=set)

    def __init__(self, num_facilities=1):
        super().__init__()
        self.num_facilities = num_facilities
        self.facilities: dict[str, BlockChain] = {}
        self.doctors = set()

    def create_facility_chain(self, facility_id: str):
        if facility_id in self.facilities:
            raise ValueError(f"Blockchain for facility {facility_id} already exists")
        self.facilities[facility_id] = BlockChain()

    def emit_transaction(self, facility_id: str, transaction: Transaction):
        if facility_id not in self.facilities:
            raise ValueError(f"Facility {facility_id} not found")
        self.facilities[facility_id].emit_transaction(transaction)

    def add_block_to_facility(self, facility_id: str):
        if facility_id not in self.facilities:
            raise ValueError(f"Facility {facility_id} not found")
        self.facilities[facility_id]._add_block()

    def validate_all_chains(self) -> bool:
        return all(facility.is_valid() for facility in self.facilities.values())
