import json

import pytest
from pydantic import ValidationError

from database.models import Doctor, Patient


def test_key_generation():
    doctor = Doctor(id=1, name="Dr. Wilson", email="wilson@hospital.com")
    patient = Patient(id=2, name="Carol White", email="carol@email.com")

    # Key generation
    assert doctor.public_key is not None
    assert doctor.private_key is not None
    assert patient.public_key is not None
    assert patient.private_key is not None

def test_transaction_creation():
    doctor = Doctor(id=1, name="Dr. Wilson", email="wilson@hospital.com")
    patient = Patient(id=2, name="Carol White", email="carol@email.com")
    
    # Include the patient's public key when creating the transaction
    data = json.dumps({"experiment_1": "34.5", "experiment_2": "67.8", "experiment_3": "123.0"})
    transaction = doctor.create_transaction(
        patient_id=patient.id,
        data=data,
        patient_public_key_pem=patient.public_key  # Add this parameter
    )
    
    assert transaction.doctor_id == doctor.id
    assert transaction.patient_id == patient.id
    assert transaction.signature is not None
    assert isinstance(transaction.signature, str)

def test_transaction_data_integrity():
    doctor = Doctor(id=1, name="Dr. Smith", email="smith@hospital.com")
    patient = Patient(id=2, name="Bob Jones", email="bob@email.com")
    
    data = json.dumps({"blood_pressure": "120/80", "temperature": "37.0", "heart_rate": "72"})
    

    transaction = doctor.create_transaction(
        patient_id=patient.id,
        data=data,
        patient_public_key_pem=patient.public_key
    )
    
 
    decrypted_data = doctor.decrypt_transaction_data(transaction, 'doctor_key')
    

    assert decrypted_data == json.loads(data)
    
   
    modified_transaction = transaction.model_copy()
    modified_transaction.signature = "tampered_signature"
    assert not modified_transaction.is_valid(doctor.public_key)

def test_multiple_transactions():
    doctor = Doctor(id=1, name="Dr. Brown", email="brown@hospital.com")
    patient = Patient(id=2, name="Jane Smith", email="jane@email.com")
    
    transactions = []
    for i in range(3):
        data = json.dumps({f"test_{i}": f"value_{i}"})
        tx = doctor.create_transaction(
            patient_id=patient.id,
            data=data,
            patient_public_key_pem=patient.public_key  # Add this parameter
        )
        transactions.append(tx)
    
    for tx in transactions:
        assert tx.doctor_id == doctor.id
        assert tx.patient_id == patient.id
        assert tx.is_valid(doctor.public_key)

def test_transaction_with_empty_data():
    doctor = Doctor(id=1, name="Dr. Wilson", email="wilson@hospital.com")
    patient = Patient(id=2, name="Carol White", email="carol@email.com")
    
    empty_data = json.dumps({})
    with pytest.raises(ValueError):
        doctor.create_transaction(
            patient_id=patient.id,
            data=empty_data,
            patient_public_key_pem=patient.public_key  # Add this parameter
        )

def test_transaction_with_wrong_patient_id():
    doctor = Doctor(id=1, name="Dr. Wilson", email="wilson@hospital.com")
    patient = Patient(id=2, name="Carol White", email="carol@email.com")
    
    data = json.dumps({"experiment_1": "34.5", "experiment_2": "67.8", "experiment_3": "123.0"})
    with pytest.raises(ValidationError):
        transaction = doctor.create_transaction(
            patient_id=-1,  # Invalid ID
            data=data,
            patient_public_key_pem=patient.public_key  # Add this parameter
        )