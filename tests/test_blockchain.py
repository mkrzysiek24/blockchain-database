from datetime import datetime, timedelta
from random import randint
from unittest.mock import MagicMock

import pytest
import json

from database.models import Transaction, Block, BlockChain


@pytest.fixture
def example_transaction() -> Transaction:
    return Transaction(
        doctor_id=randint(1, 999),
        patient_id=randint(1, 999),
        data=json.dumps({"treatment": "X-ray", "notes": "blank"}),
        date=datetime.now(),
    )


@pytest.fixture
def example_block(example_transaction):
    def create_block(previous_hash: str = "0" * 64):
        return Block.create_block(transactions=[example_transaction], previous_hash=previous_hash, difficulty=2)

    return create_block


def test_manually_create_valid_blockchain(example_block):
    blockchain = BlockChain()
    block1 = example_block(previous_hash="0" * 64)
    block2 = example_block(previous_hash=block1.hash)
    block3 = example_block(previous_hash=block2.hash)

    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert blockchain.is_valid(2)


def test_invalid_blockchain_wrong_order(example_block):
    blockchain = BlockChain()
    block1 = example_block(previous_hash="0" * 64)
    block2 = example_block(previous_hash=block1.hash)
    block3 = example_block(previous_hash=block2.hash)

    blockchain.chain.append(block2)
    blockchain.chain.append(block1)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert not blockchain.is_valid(2)


def test_invalid_blockchain_wrong_hash(example_block):
    blockchain = BlockChain()
    block1 = example_block(previous_hash="0" * 64)

    corrupted_hash = block1.hash[1:] + "1"
    block2 = example_block(previous_hash=corrupted_hash)
    block3 = example_block(previous_hash=block2.hash)

    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert not blockchain.is_valid(2)


def test_invalid_blockchain_invalid_block(example_block):
    blockchain = BlockChain()
    block1 = example_block(previous_hash="0" * 64)
    block2 = example_block(previous_hash=block1.hash)
    block3 = example_block(previous_hash=block2.hash)

    block3.hash = block3.hash[1:] + "1"
    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert not blockchain.is_valid(2)


def test_emit_transaction_without_time_delta(example_transaction):
    blockchain = BlockChain()
    blockchain.last_block_added = datetime.now()

    blockchain.emit_transaction(example_transaction)

    assert example_transaction in blockchain.emitted_transactions
    assert len(blockchain.chain) == 0
    assert blockchain.is_valid(2)


def test_emit_transaction_with_time_delta(example_transaction, example_block):
    blockchain = BlockChain()
    block1 = example_block(previous_hash="0" * 64)
    block2 = example_block(previous_hash=block1.hash)
    block3 = example_block(previous_hash=block2.hash)
    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    blockchain.last_block_added = datetime.now() - timedelta(seconds=20)
    blockchain.emit_transaction(example_transaction)

    assert example_transaction not in blockchain.emitted_transactions
    assert len(blockchain.chain) == 4
    assert blockchain.is_valid(2)


def test_emit_transaction_with_time_delta_empty(example_transaction):
    blockchain = BlockChain()
    blockchain.last_block_added = datetime.now() - timedelta(seconds=20)
    blockchain.emit_transaction(example_transaction)

    assert example_transaction not in blockchain.emitted_transactions
    assert len(blockchain.chain) == 1
    assert blockchain.is_valid(2)
