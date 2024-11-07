from logging import getLogger
from os.path import basename

logger = getLogger(basename(__file__))
logger.info(
    "Starting application",
)

try:
    logger.info("Job done")
except Exception as e:
    logger.error(f"Error: {e}")
    exit()
