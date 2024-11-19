import json

from database import Doctor, Patient


def test_transaction_data_integrity():
    doctor = Doctor(id=1, name="Dr. Smith", email="smith@hospital.com")
    patient = Patient(id=2, name="Bob Jones", email="bob@email.com")

    data = json.dumps({"blood_pressure": "120/80", "temperature": "37.0", "heart_rate": "72"})

    transaction = doctor.create_transaction(patient_id=patient.id, data=data)

    # Verify original data matches
    assert transaction.data == json.loads(data)

    # Verify transaction can't be tampered with
    modified_data = json.dumps({"blood_pressure": "140/90", "temperature": "38.5", "heart_rate": "90"})

    transaction.data = modified_data

    assert not transaction.is_valid(doctor.public_key)


def test_multiple_transactions():
    doctor = Doctor(id=1, name="Dr. Brown", email="brown@hospital.com")
    patient = Patient(id=2, name="Jane Smith", email="jane@email.com")

    # Create multiple transactions
    transactions = []
    for i in range(3):
        data = json.dumps({f"test_{i}": f"value_{i}"})
        tx = doctor.create_transaction(patient_id=patient.id, data=data)
        transactions.append(tx)

    # Verify each transaction
    for tx in transactions:
        assert tx.doctor_id == doctor.id
        assert tx.patient_id == patient.id
        assert tx.is_valid(doctor.public_key)


def test_transaction_with_empty_data():
    doctor = Doctor(id=1, name="Dr. Wilson", email="wilson@hospital.com")
    patient = Patient(id=2, name="Carol White", email="carol@email.com")

    empty_data = json.dumps({})

    transaction = doctor.create_transaction(patient_id=patient.id, data=empty_data)

    assert json.dumps(transaction.data, sort_keys=True) == empty_data
    assert transaction.is_valid(doctor.public_key)

    # Key generation
    assert doctor.public_key is not None
    assert doctor._private_key is not None
    assert patient.public_key is not None
    assert patient._private_key is not None

    # Transaction creation
    data = json.dumps({"experiment_1": "34.5", "experiment_2": "67.8", "experiment_3": "123.0"})
    transaction = doctor.create_transaction(patient_id=patient.id, data=data)

    assert transaction.doctor_id == doctor.id
    assert transaction.patient_id == patient.id
    assert transaction.signature is not None
    assert isinstance(transaction.signature, str)


def test_invalid_transaction():
    doctor = Doctor(id=1, name="doctor1", email="doctor1@")
    doctor2 = Doctor(id=3, name="doctor2", email="doctor2@")
    patient = Patient(id=2, name="patient1", email="patient1@")

    data = json.dumps({"experiment_1": "34.5", "experiment_2": "67.8", "experiment_3": "123.0"})
    transaction = doctor.create_transaction(patient_id=patient.id, data=data)

    # Weryfikacja transakcji z nieprawidłowym kluczem publicznym
    is_valid = transaction.is_valid(doctor2.public_key)

    # Sprawdzenie, że transakcja jest nieprawidłowa
    assert is_valid == False
