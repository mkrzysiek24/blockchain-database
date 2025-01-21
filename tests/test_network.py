import pytest
from datetime import datetime
from unittest.mock import Mock
from database.models import Network, BlockChain, Transaction, Doctor, Patient
import os
import base64
import json
# pip install pytest-mock
@pytest.fixture
def network():

    return Network(num_facilities=2)  #
@pytest.fixture
def doctor():
    return Doctor(
        id=1,
        name="Dr. Smith",
        license_number="MED123"
    )
@pytest.fixture
def patient():
    return Patient(
        id=1,
        name="John Doe",
        insurance_number="INS456"
    )
def test_add_block_to_facility(network, mocker):
   
    
    facility_id = "facility_1"
    network.create_facility_chain(facility_id)
    

    spy = mocker.spy(network.facilities[facility_id], "_add_block")
    
    network.add_block_to_facility(facility_id)
    
    # Verify the method was called exactly once
    assert spy.call_count == 1

@pytest.fixture
def example_transaction(doctor, patient):
    
    aes_key = os.urandom(32)
    iv = os.urandom(16)
    encrypted_data = b"some encrypted data"  # In real case this would be actually encrypted

    mock_encrypted_data = {
        'encrypted_data': base64.b64encode(encrypted_data).decode(),
        'iv': base64.b64encode(iv).decode(),
        'doctor_key': base64.b64encode(encrypted_data).decode(),  # Simplified for test
        'patient_key': base64.b64encode(encrypted_data).decode()  # Simplified for test
    }
    json_data = json.dumps(mock_encrypted_data)

    return Transaction(
        doctor_id=1,
        patient_id=1,
        data=json_data,  
        date=datetime.now(),
    )



def test_emit_transaction_to_facility(network, example_transaction):
    """
    Tests that transactions are properly routed to the correct facility chain.
    This verifies the network's transaction routing capabilities.
    """
    facility_id = "facility_1"
    network.create_facility_chain(facility_id)
    
    # Emit a transaction to the facility
    network.emit_transaction(facility_id, example_transaction)
    
    # Verify the transaction was added to the facility's pending transactions
    facility_chain = network.facilities[facility_id]
    assert example_transaction in facility_chain.emitted_transactions

def test_multiple_facility_chains(network):
    """
    Tests that the network can properly manage multiple facility chains
    simultaneously. This is essential for distributed operation.
    """
    # Create multiple facility chains
    facility_ids = ["facility_1", "facility_2", "facility_3"]
    
    for facility_id in facility_ids:
        network.create_facility_chain(facility_id)
    
    # Verify each facility has its own chain
    for facility_id in facility_ids:
        assert facility_id in network.facilities
        assert isinstance(network.facilities[facility_id], BlockChain)
        assert network.facilities[facility_id] is not None
        
    # Verify chains are independent
    assert len(set(id(chain) for chain in network.facilities.values())) == len(facility_ids)