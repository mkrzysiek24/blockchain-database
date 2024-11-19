import json
from logging import basicConfig, getLogger
from os.path import basename

from models.blockChain import BlockChain
from models.doctor import Doctor
from models.patient import Patient

logger = getLogger(basename(__file__))
basicConfig(level="INFO")
logger.info(
    "Starting application",
)

try:
    # blockchain model
    blockchain = BlockChain()

    doctors = [
        Doctor(
            id=1,
            name="doctor1",
            email="doctor1@",
        ),
        Doctor(
            id=2,
            name="doctor2",
            email="doctor2@",
        ),
    ]

    patient1 = Patient(
        id=3,
        name="patient1",
        email="patient1@",
    )

    # Add doctors to global blockchain user database
    blockchain.doctors = doctors

    # Create transactions
    for _ in range(3):
        for i, doctor in enumerate(blockchain.doctors):
            transaction = doctor.create_transaction(
                patient_id=patient1.id,
                data=json.dumps(
                    {
                        "experiment_1": f"{34.5 * i}",
                        "experiment_2": f"{67.8 * i}",
                        "experiment_3": f"{123.0 * i}",
                    },
                ),
            )

            # Emit transaction to blockchain
            blockchain.emit_transaction(transaction)

    print(blockchain.model_dump_json(indent=1))
    logger.info("Job done")
except Exception as e:
    logger.error(f"Error: {e}")
    exit()
