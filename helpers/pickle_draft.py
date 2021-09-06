import logging
import pickle

from helpers import sql_lib


def pickle_draft_object(instance):
    """Save the Draft object to a pickle file."""
    try:
        pickle_string = pickle.dumps(instance)

        if not sql_lib.execute_query("SELECT * FROM draft;"):
            operation = "INSERT INTO draft VALUES(%s)"
        else:
            operation = "UPDATE draft SET object=%s"

        # Use the connection directly here to use the %s syntax
        with sql_lib._get_sql_connection().cursor() as cur:
            cur.execute(operation, (pickle_string))
    except Exception as err:
        logging.error(f"Error pickling Draft object to database: {err}")


def get_draft_object():
    """Get the Draft object from pickle file."""
    try:
        result = sql_lib.execute_query("SELECT * FROM draft;")
        return pickle.loads(result[0][0])
    except Exception as err:
        logging.error(f"Error unpickling object from database: {err}")
