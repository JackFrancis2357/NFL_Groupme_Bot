import yaml

from helpers.sql_lib import check_or_create_table, _get_sql_connection
from testing_nfl_espn import jack_teams, jordan_teams, nate_teams, patrick_teams, nfl_results_df


#########################
### MIGRATE TO SQLITE ###
#########################


def migrate_team_owners(teams, owner, season):

    with _get_sql_connection() as conn:
        cursor = conn.cursor()

        for team in teams:
            cursor.execute(f"INSERT INTO teams (owner, team, season) VALUES ('{owner}', '{team}', '{season}');")
            conn.commit()


def migrate_team_records(team_mapping, season):
    """Add team records to database."""

    for team in team_mapping["TEAMS"]:
        team_dict = team_mapping["TEAMS"][team]
        team_result = nfl_results_df[nfl_results_df["Team Name"] == team_dict["Abbrev"]]

        with _get_sql_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO seasons (season, team, abbrev, division, conference, wins, losses, ties) VALUES ('{season}', '{team}', '{team_dict['Abbrev']}', '{team_dict['Division']}', '{team_dict['Conference']}', '{team_result['Wins'].iloc[0]}', '{team_result['Losses'].iloc[0]}', '{team_result['Ties'].iloc[0]}');")
            conn.commit()


if __name__ == "__main__":

    query_owners = "CREATE TABLE IF NOT EXISTS teams (owner string, team string, season string, wins number, losses number, tie number);"
    query_season = "CREATE TABLE IF NOT EXISTS seasons (season string, team string, abbrev string, division string, conference string, wins number, losses number, ties number);"

    owners = {
        "Jordan": jordan_teams,
        "Jack": jack_teams,
        "Nathan": nate_teams,
        "Patrick": patrick_teams
    }

    check_or_create_table(query_owners)
    for owner in owners:
        migrate_team_owners(owners[owner], owner, "2020")

    with open("../config/team_mapping.yaml", "r") as yaml_file:
        team_mapping = yaml.safe_load(yaml_file)

    check_or_create_table(query_season)
    migrate_team_records(team_mapping, "2020")
