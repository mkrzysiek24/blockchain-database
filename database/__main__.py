import json
from logging import basicConfig, getLogger
from os.path import basename

from database.models import Block, BlockChain, Transaction, User

logger = getLogger(basename(__file__))
basicConfig(level="INFO")
logger.info(
    "Starting application",
)

try:
    # blockchain model
    blockchain = BlockChain()

    # 2 users
    doctor1 = User(
        id=1,
        name="doctor1",
        email="doctor1@",
    )
    doctor2 = User(
        id=2,
        name="doctor2",
        email="doctor2@",
    )
    patient1 = User(
        id=3,
        name="patient1",
        email="patient1@",
    )

    # create transactions
    for i in range(4):
        transaction1 = Transaction(
            id=24151515151 + i,
            sender_id=1,
            recipient_id=3,
            data=json.dumps(
                {
                    "experiment_1": f"{34.5 * i}",
                    "experiment_2": f"{67.8 * i}",
                    "experiment_3": f"{123.0 * i}",
                },
            ),
        )

        # Emitowanie transakcji
        blockchain.emit_transaction(transaction1)

    print(blockchain.model_dump_json(indent=2))
    logger.info("Job done")
except Exception as e:
    logger.error(f"Error: {e}")
    exit()
