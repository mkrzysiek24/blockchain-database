# import json
# from datetime import datetime
# import pytest
# import base64
# import os
# from database.models import Block, Transaction, Doctor, Patient

# @pytest.fixture
# def doctor():
#     return Doctor(
#         id=1,
#         name="Dr. Smith",
#         license_number="MED123"
#     )

# @pytest.fixture
# def patient():
#     return Patient(
#         id=1,
#         name="John Doe",
#         insurance_number="INS456"
#     )

# @pytest.fixture
# def example_transaction(doctor, patient):
#     # Create encrypted data structure that matches what doctor.create_transaction would make
#     aes_key = os.urandom(32)
#     iv = os.urandom(16)
#     encrypted_data = b"some encrypted data"  # In real case this would be actually encrypted

#     mock_encrypted_data = {
#         'encrypted_data': base64.b64encode(encrypted_data).decode(),
#         'iv': base64.b64encode(iv).decode(),
#         'doctor_key': base64.b64encode(encrypted_data).decode(),  # Simplified for test
#         'patient_key': base64.b64encode(encrypted_data).decode()  # Simplified for test
#     }

#     return Transaction(
#         doctor_id=1,
#         patient_id=1,
#         data=mock_encrypted_data,  # Use the encrypted data structure
#         date=datetime.now(),
#     )

# @pytest.fixture
# def previous_hash():
#     return "0" * 64

# @pytest.fixture
# def example_block(example_transaction):
#     return Block.create_block(
#         transactions=[example_transaction],
#         previous_hash=previous_hash(),
#         difficulty=2
#     )

# def test_create_block(example_block):
#     block = example_block
#     assert block.id is not None
#     assert block.timestamp is not None
#     assert len(block.transactions) == 1
#     assert block.previous_hash == previous_hash()
#     assert block.hash is not None

# # def test_calculate_hash(example_block):
# #     block = example_block
# #     block_hash = block._calculate_hash()
# #     assert block_hash is not None
# #     assert len(block_hash) == 64

# # def test_proof_of_work(example_block):
# #     block = example_block
# #     difficulty = 2
# #     block.proof_of_work(difficulty)
# #     assert block.hash is not None
# #     assert block.hash.startswith("0" * difficulty)

# # def test_is_valid_valid_block(example_block):
# #     block = example_block
# #     difficulty = 2
# #     block.proof_of_work(difficulty)
# #     assert block.is_valid(difficulty) is True

# # def test_is_valid_invalid_block(example_block):
# #     block = example_block
# #     block.hash = "invalid"
# #     difficulty = 2
# #     assert block.is_valid(difficulty) is False