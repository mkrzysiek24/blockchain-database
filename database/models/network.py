from collections import defaultdict

from pydantic import BaseModel

from database.models import Block, BlockChain, Transaction


class Network(BaseModel):
    def __init__(self, num_facilities):
        self.num_facilities = num_facilities
        facilities: dict[str, BlockChain] = {}
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
