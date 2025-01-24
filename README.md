# Blockchain-Based Medical Facility Database

This project is a simplified blockchain-based database for medical facilities. It integrates an external database to store keys for patients and doctors, allowing:
- **Doctors** to add encrypted transactions (e.g., medical records) to the blockchain.
- **Patients** to securely access their records.

All transactions are encrypted, ensuring only the doctor and the patient can read the data.


## Features

- **Patient Records Management**: Store and access medical records with full encryption.
- **Traceability**: Every change to the database is tracked on the blockchain.
- **Access Control**: Role-based access for doctors, patients.
- **Console Application for Management**: A userfriendly console application to interact with the blockchain system.

---

## Installation and Setup

Follow these steps to get the project up and running:

### 1. Clone the Repository
```bash
git clone https://github.com/mkrzysiek24/blockchain-database.git
```
```bash
cd blockchain-database
```
### 2. Install Requirements
```bash 
pip install -r requirements.txt
```
### 3. Run the Application
```bash 
python -m database
```
