import logging
import sys


def config_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Log everything to std out because Heroku logs this
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s | %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    logging.info("Logging configuration initialized.")
