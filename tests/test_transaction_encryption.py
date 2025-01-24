import pytest

from database.models import Doctor, Patient


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
        id=2,
        name="John Doe",
        insurance_number="INS456",
    )


@pytest.fixture
def medical_data():
    return {
        "diagnosis": "Healthy",
        "notes": "Regular checkup",
        "date": "2025-01-20",
    }


@pytest.fixture
def transaction(doctor, patient, medical_data):
    return doctor.create_transaction(
        patient_id=patient.id,
        data=medical_data,
        patient_public_key_pem=patient.public_key,
    )


def test_transaction_creation_and_encryption(doctor, patient, medical_data):
    """
    Tests that medical data is properly encrypted when creating a transaction.
    Verifies that the encryption preserves doctor and patient access while
    securing the medical data.
    """
    transaction = doctor.create_transaction(
        patient_id=patient.id,
        data=medical_data,
        patient_public_key_pem=patient.public_key,
    )

    # Verify transaction properties
    assert transaction.doctor_id == doctor.id
    assert transaction.patient_id == patient.id
    assert transaction.is_encrypted()
    assert transaction.signature is not None

    # Verify encryption package structure
    encryption_package = transaction.get_encryption_package()
    assert encryption_package is not None
    assert all(key in encryption_package for key in ["encrypted_data", "iv", "doctor_key", "patient_key"])


def test_transaction_decryption(doctor, patient, transaction):
    """
    Tests that both doctor and patient can properly decrypt the medical data
    and see identical information.
    """
    # Doctor decryption
    doctor_view = doctor.decrypt_transaction_data(transaction, "doctor_key")
    assert "diagnosis" in doctor_view
    assert doctor_view["diagnosis"] == "Healthy"

    # Patient decryption
    patient_view = patient.decrypt_transaction_data(transaction, "patient_key")
    assert "diagnosis" in patient_view
    assert patient_view["diagnosis"] == "Healthy"

    # Verify data integrity
    assert doctor_view == patient_view

    # Verify all fields are present
    expected_fields = {"diagnosis", "notes", "date"}
    assert all(field in doctor_view for field in expected_fields)
