import logging


def config_logger():
    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(filename)s | %(message)s',
        filename="bot.log",
        level=logging.INFO)
    logging.info("Logging configuration initialized.")
