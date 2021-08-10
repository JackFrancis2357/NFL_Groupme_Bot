import sqlite3 as sql

from testing_nfl_espn import jack_teams, jordan_teams, nate_teams, patrick_teams


def get_sql_connection():
    return sql.connect("history.db")


def migrate_team_owners(teams, owner, season):

    with get_sql_connection() as conn:
        cursor = conn.cursor()

        for team in teams:
            cursor.execute(f"INSERT INTO teams (owner, team, season) VALUES ('{owner}', '{team}', '{season}');")
            conn.commit()


def check_or_create_table(table_name):
    conn = get_sql_connection()
    query = f"CREATE TABLE IF NOT EXISTS {table_name} (owner string, team string, season string, wins number, losses number, tie number)"
    conn.execute(query)

if __name__ == "__main__":
    teams = {
        "Jack": jack_teams,
        "Jordan": jordan_teams,
        "Nathan": nate_teams,
        "Patrick": patrick_teams
    }

    check_or_create_table("teams")
    for team in teams:
        migrate_team_owners(teams[team], team, "2020")
