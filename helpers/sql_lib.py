import logging
import os
import sqlite3 as sql

import psycopg2 as pg

from configs import Config


def _get_sql_connection():
    if Config["sql_flavor"] == "postgres":
        return pg.connect(os.environ["DATABASE_URL"])
    else:
        return sql.connect("helpers/history_sandbox.db")


def execute_query(query):
    with _get_sql_connection() as conn:
        logging.info("Database connection established.")
        result = None
        try:
            logging.info(f"Running query: {query}")
            cursor = conn.cursor()
            result = cursor.execute(query)
            conn.commit()
            logging.info("Query executed successfully.")
        except Exception as err:
            logging.error(f"Error executing query: {query}")
            logging.error(err)
        if result:
            return result.fetchall()


# TODO: Make this dynamic - pass in table name with fields and types and generate the query
def check_or_create_table(query):
    conn = _get_sql_connection()
    conn.execute(query)
