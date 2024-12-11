from database.models import BlockChain, Network, Transaction, Doctor
import pytest
import json



@pytest.fixture
def network():
    return Network(num_facilities=1)


def test_create_facility_chain():
    network = Network(num_facilities=1)
    facility_id = "facility_1"


    network.create_facility_chain(facility_id)

    assert facility_id in network.facilities
    assert isinstance(network.facilities[facility_id], BlockChain)

def test_create_facility_chain_duplicate(network):
    facility_id = "facility_1"
    network.create_facility_chain(facility_id)
    with pytest.raises(ValueError, match=f"Blockchain for facility {facility_id} already exists"):
        network.create_facility_chain(facility_id)

@pytest.fixture
def doctor():
    return Doctor(id=1, name="Dr. Wilson", email="wilson@hospital.com")

@pytest.fixture
def transaction(doctor):
    data = json.dumps({"experiment_1": "34.5", "experiment_2": "67.8", "experiment_3": "123.0"})
    transaction = doctor.create_transaction(patient_id=42, data=data)
    return transaction

def test_emit_transaction_nonexistent_facility(network, transaction):
    with pytest.raises(ValueError, match="Facility .* not found"):
        network.emit_transaction("nonexistent_facility", transaction)


# def test_add_block_to_facility(network, mocker):
#     facility_id = "facility_1"
#     mock_add_block = mocker.patch.object(BlockChain, "_add_block")
#     network.create_facility_chain(facility_id)
#     network.add_block_to_facility(facility_id)
#     mock_add_block.assert_called_once()

@pytest.fixture
def mock_blockchain(mocker):
    mock = mocker.patch("database.models.blockChain.BlockChain")
    mock.return_value.is_valid.return_value = True
    return mock

def test_add_block_to_nonexistent_facility(network):
    with pytest.raises(ValueError, match="Facility .* not found"):
        network.add_block_to_facility("nonexistent_facility")


def test_validate_all_chains(network):
    facility_id_1 = "facility_1"
    facility_id_2 = "facility_2"
    network.create_facility_chain(facility_id_1)
    network.create_facility_chain(facility_id_2)
    assert network.validate_all_chains(2)


# def test_validate_all_chains_invalid(network, mocker):
#     facility_id = "facility_1"
#     mock_invalid_blockchain = mocker.patch("database.models.blockChain.BlockChain")
#     mock_invalid_blockchain.is_valid.return_value = False
#     network.facilities[facility_id] = mock_invalid_blockchain
#     assert not network.validate_all_chains(2)
