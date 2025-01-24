import base64
import json
import os
from datetime import datetime, timedelta

import pytest

from database.models import Block, BlockChain, Doctor, Patient, Transaction


@pytest.fixture
def doctor():
    return Doctor(
        id=1,
        name="Dr. Smith",
        license_number="MED123",
    )


@pytest.fixture
def patient():
    return Patient(
        id=1,
        name="John Doe",
        insurance_number="INS456",
    )


@pytest.fixture
def example_transaction(doctor, patient):

    aes_key = os.urandom(32)
    iv = os.urandom(16)
    encrypted_data = b"some encrypted data"  # In real case this would be actually encrypted

    mock_encrypted_data = {
        "encrypted_data": base64.b64encode(encrypted_data).decode(),
        "iv": base64.b64encode(iv).decode(),
        "doctor_key": base64.b64encode(encrypted_data).decode(),  # Simplified for test
        "patient_key": base64.b64encode(encrypted_data).decode(),  # Simplified for test
    }
    json_data = json.dumps(mock_encrypted_data)

    return Transaction(
        doctor_id=1,
        patient_id=1,
        data=json_data,
        date=datetime.now(),
    )


@pytest.fixture
def example_block(example_transaction):
    return Block.create_block(
        transactions=[example_transaction],
        previous_hash="0" * 64,
        difficulty=2,
    )


@pytest.fixture
def create_block(example_transaction):
    def _create_block(previous_hash: str):
        return Block.create_block(
            transactions=[example_transaction],
            previous_hash=previous_hash,
            difficulty=2,
        )

    return _create_block


def test_manually_create_valid_blockchain(create_block):
    blockchain = BlockChain()

    # Create a chain of blocks
    block1 = create_block(previous_hash="0" * 64)
    block2 = create_block(previous_hash=block1.hash)
    block3 = create_block(previous_hash=block2.hash)

    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    # Verify the blockchain
    assert len(blockchain.chain) == 3
    assert blockchain.is_valid(2)


def test_invalid_blockchain_wrong_order(create_block):
    """
    Tests that a blockchain is invalid when blocks are added in the wrong order.
    This simulates an attempt to tamper with the blockchain's sequence.
    """
    blockchain = BlockChain()

    block1 = create_block(previous_hash="0" * 64)
    block2 = create_block(previous_hash=block1.hash)
    block3 = create_block(previous_hash=block2.hash)

    blockchain.chain.append(block2)
    blockchain.chain.append(block1)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert not blockchain.is_valid(2)  # Should fail validation due to wrong order


def test_invalid_blockchain_wrong_hash(create_block):
    """
    Tests that a blockchain is invalid when a block references an incorrect previous hash.
    This simulates tampering with the chain's cryptographic links.
    """
    blockchain = BlockChain()

    # Create a block and then corrupt its hash for the next block
    block1 = create_block(previous_hash="0" * 64)
    corrupted_hash = block1.hash[1:] + "1"  # Change one character of the hash

    # Create subsequent blocks with the corrupted hash
    block2 = create_block(previous_hash=corrupted_hash)
    block3 = create_block(previous_hash=block2.hash)

    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert not blockchain.is_valid(2)  # Should fail validation due to hash mismatch


def test_invalid_blockchain_invalid_block(create_block):
    """
    Tests that a blockchain is invalid when one of its blocks has been tampered with.
    This simulates direct modification of a block's hash.
    """
    blockchain = BlockChain()

    # Create valid blocks
    block1 = create_block(previous_hash="0" * 64)
    block2 = create_block(previous_hash=block1.hash)
    block3 = create_block(previous_hash=block2.hash)

    # Tamper with the last block's hash
    block3.hash = block3.hash[1:] + "1"

    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    assert len(blockchain.chain) == 3
    assert not blockchain.is_valid(2)  # Should fail validation due to tampered block


def test_emit_transaction_without_time_delta(example_transaction):

    blockchain = BlockChain()
    blockchain.last_block_added = datetime.now()

    blockchain.emit_transaction(example_transaction)
    assert example_transaction in blockchain.emitted_transactions
    assert len(blockchain.chain) == 0
    assert blockchain.is_valid(2)


def test_emit_transaction_with_time_delta(create_block, example_transaction):
    """
    Tests that transactions are properly added to a new block when the time delta has elapsed.
    """
    blockchain = BlockChain()

    block1 = create_block(previous_hash="0" * 64)
    block2 = create_block(previous_hash=block1.hash)
    block3 = create_block(previous_hash=block2.hash)

    blockchain.chain.append(block1)
    blockchain.chain.append(block2)
    blockchain.chain.append(block3)

    blockchain.last_block_added = datetime.now() - timedelta(minutes=45)

    blockchain.emit_transaction(example_transaction)

    # Transaction should be in a new block, not in pending
    assert example_transaction not in blockchain.emitted_transactions
    assert len(blockchain.chain) == 4
    assert blockchain.is_valid(2)


def test_emit_transaction_with_time_delta_empty(example_transaction):

    blockchain = BlockChain()
    blockchain.last_block_added = datetime.now() - timedelta(minutes=45)

    # Emit a transaction to empty blockchain
    blockchain.emit_transaction(example_transaction)

    # Should create first block with the transaction
    assert example_transaction not in blockchain.emitted_transactions
    assert len(blockchain.chain) == 1
    assert blockchain.is_valid(2)
