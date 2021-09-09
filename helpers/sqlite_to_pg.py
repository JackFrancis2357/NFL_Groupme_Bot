import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine

import sql_lib

# NOTE! Postgres connection details are not static - check Heroku before running
dev_postgres_conn = {
    "host": "ec2-35-153-114-74.compute-1.amazonaws.com",
    "database": "dd0de9nhnoavf8",
    "user": "xctojdwwdgumac",
    # Login to Heroku Dashboard to get password
    "password": ""
}
prod_postgres_conn = {
    "host": "ec2-44-196-146-152.compute-1.amazonaws.com",
    "database": "d424tf4roqenvg",
    "user": "pobtgnjbbismvz",
    "password": ""
}
dev_uri = "postgresql://xctojdwwdgumac:<<PASSWORD>>@ec2-35-153-114-74.compute-1.amazonaws.com:5432/dd0de9nhnoavf8"
prod_uri = "postgresql://pobtgnjbbismvz:<<PASSWORD>>@ec2-44-196-146-152.compute-1.amazonaws.com:5432/d424tf4roqenvg"

seasons_df = pd.read_sql_query("SELECT * FROM seasons;", sql_lib._get_sql_connection())
engine = create_engine(prod_uri)

# Drop table if exists and add dataframe to the database
engine.execute("DROP TABLE IF EXISTS seasons;")
seasons_df.to_sql('seasons', engine)

# Make sure it's there
with pg.connect(**dev_postgres_conn) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM seasons;")
print(cur.fetchall())
