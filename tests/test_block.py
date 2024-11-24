import json
from datetime import datetime

import pytest

from database.models import Block, Transaction


@pytest.fixture
def example_transaction():
    return Transaction(
        doctor_id=1,
        patient_id=1,
        data=json.dumps({"treatment": "X-ray", "notes": "blank"}),
        date=datetime.now(),
    )


def previous_hash():
    return "0" * 64


@pytest.fixture
def example_block(example_transaction):
    return Block(timestamp=datetime.now(), transactions=[example_transaction], previous_hash=previous_hash())


def test_create_block(example_block):
    block = example_block

    assert block.id is not None
    assert block.timestamp is not None
    assert len(block.transactions) == 1
    assert block.previous_hash == previous_hash()
    assert block.hash is None


def test_calculate_hash(example_block):
    block = example_block
    block_hash = block._calculate_hash()

    assert block_hash is not None
    assert len(block_hash) == 64


def test_proof_of_work(example_block):
    block = example_block
    difficulty = 2
    block.proof_of_work(difficulty)

    assert block.hash is not None
    assert block.hash.startswith("0" * difficulty)


def test_is_valid_valid_block(example_block):
    block = example_block
    difficulty = 2
    block.proof_of_work(difficulty)

    assert block.is_valid(difficulty) is True


def test_is_valid_invalid_block(example_block):
    block = example_block
    block.hash = "invalid"
    difficulty = 2

    assert block.is_valid(difficulty) is False
