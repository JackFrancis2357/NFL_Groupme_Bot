import logging

LOGGER = logging.getLogger()
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(filename)s | %(message)s',
    filename="bot.log",
    level=logging.INFO)
