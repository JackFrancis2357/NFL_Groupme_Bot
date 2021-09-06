import logging
import pickle


def pickle_draft_object(instance):
    """Save the Draft object to a pickle file."""
    try:
        with open("/app/draft_object", "wb") as pickle_file:
            pickle.dump(instance, pickle_file)
    except Exception as err:
        logging.error(f"Error pickling Draft object to file: {err}")


def get_draft_object():
    """Get the Draft object from pickle file."""
    try:
        with open("/app/draft_object", "rb") as pickle_file:
            return pickle.load(pickle_file)
    except Exception as err:
        logging.error(f"Error unpickling object from file: {err}")
