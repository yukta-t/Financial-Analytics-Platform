import logging
import os

os.makedirs("logs", exist_ok=True)

def setup_logger():

    logging.basicConfig(
        level=logging.INFO,

        format=(
            "%(asctime)s | "     #timestamp
            "%(levelname)s | "
            "%(message)s"
        ),

        handlers=[
            logging.FileHandler(
                "logs/app.log"
            ),

            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)