from database.models import BlockChain, Network

# tests/test_network.py


def test_create_facility_chain():
    network = Network(num_facilities=1)
    facility_id = "facility_1"

    # Create a facility chain
    network.create_facility_chain(facility_id)

    # Check if the facility chain was created
    assert facility_id in network.facilities
    assert isinstance(network.facilities[facility_id], BlockChain)
