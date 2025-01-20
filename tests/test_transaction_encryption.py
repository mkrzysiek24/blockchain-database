# # # Regular medical data as JSON
# # transaction = Transaction(
# #     doctor_id=1,
# #     patient_id=2,
# #     data={
# #         "diagnosis": "Fever",
# #         "temperature": 38.5,
# #         "medications": ["Paracetamol", "Ibuprofen"],
# #         "next_visit": "2025-02-01"
# #     },
# #     date=datetime.now()
# # )

# # # Encrypted data still in JSON format
# # encrypted_transaction = Transaction(
# #     doctor_id=1,
# #     patient_id=2,
# #     data={
# #         "encrypted_data": "base64_encoded_string_here...",
# #         "iv": "base64_encoded_iv_here...",
# #         "doctor_key": "base64_encoded_doctor_key...",
# #         "patient_key": "base64_encoded_patient_key..."
# #     },
# #     date=datetime.now()
# # )


# import pytest
# from datetime import datetime, timedelta
# from database.models import BlockChain, Doctor, Network, User, Patient
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
#         id=2,
#         name="John Doe",
#         insurance_number="INS456"
#     )

# @pytest.fixture
# def medical_data():
#     return {
#         "diagnosis": "Healthy",
#         "notes": "Regular checkup",
#         "date": "2025-01-20"
#     }

# @pytest.fixture
# def transaction(doctor, patient, medical_data):
#     return doctor.create_transaction(
#         patient_id=patient.id,
#         data=medical_data,
#         patient_public_key_pem=patient.public_key
#     )

# @pytest.fixture
# def blockchain():
#     return BlockChain()

# def test_transaction_creation_and_encryption(self, doctor, patient, medical_data):
#         transaction = doctor.create_transaction(
#             patient_id=patient.id,
#             data=medical_data,
#             patient_public_key_pem=patient.public_key
#         )
        
#         assert transaction.doctor_id == doctor.id
#         assert transaction.patient_id == patient.id
#         assert transaction.is_encrypted()
#         assert transaction.signature is not None
# def test_transaction_decryption(self, doctor, patient, transaction):
#     # Doctor can decrypt
#     doctor_view = doctor.decrypt_transaction(transaction)
#     assert "diagnosis" in doctor_view
    
#     # Patient can decrypt
#     patient_view = patient.decrypt_transaction(transaction)
#     assert "diagnosis" in patient_view
    
#     # Both see the same data
#     assert doctor_view == patient_view