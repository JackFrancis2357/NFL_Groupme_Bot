import datetime
import logging

import numpy as np
from pytz import timezone

from configs import Config

# from helpers import sql_lib

logger = logging.getLogger(__name__)


def get_team_abb_list(teams_list):
    team_abb_list = []
    for team in teams_list:
        team_abb_list.append(Config["TEAMS"][team]["Abbrev"])
    return team_abb_list


def get_teams():
    # TODO: Refactor this to at least be a dict of lists so we aren't hard-coding so much
    if Config["ENVIRONMENT"] == "local_dev":
        teams = {
            "Jack": Config["USER_TEAMS"]["Jack"],
            "Jordan": Config["USER_TEAMS"]["Jordan"],
            "Nathan": Config["USER_TEAMS"]["Nathan"],
            "Patrick": Config["USER_TEAMS"]["Patrick"],
        }
        all_teams = []
        for lst in teams.values():
            all_teams += [val for val in lst]
        teams["all"] = all_teams
        logger.info("Successfully called ESPN and got a response")
    else:
        # TODO Enable Team selection with Postgres on Render and other DB functionality. Commenting out for now
        # else:
        #     teams = {}
        #     base_query = (
        #         "SELECT team_name FROM season "
        #         "JOIN team on team.id = season.team_id "
        #         "JOIN player on player.id = season.owner_id "
        #         "WHERE player_name='{}' and season='{}';"
        #     )
        #     teams["Jack"] = [team[0].title() for team in sql_lib.execute_query(base_query.format("Jack Francis", "2022"))]
        #     teams["Jordan"] = [
        #         team[0].title() for team in sql_lib.execute_query(base_query.format("Jordan Holland", "2022"))
        #     ]
        #     teams["Patrick"] = [
        #         team[0].title() for team in sql_lib.execute_query(base_query.format("Patrick Cooper", "2022"))
        #     ]
        #     teams["Nathan"] = [team[0].title() for team in sql_lib.execute_query(base_query.format("Nathan Lee", "2022"))]

        # all_teams = []
        # for lst in teams.values():
        #     all_teams += [val for val in lst]
        # teams["all"] = all_teams
        pass
    return teams


def get_start_final_date(current_week):
    # Get current scores
    nfl_season_start = datetime.datetime.strptime(Config["BASE_CONFIG"]["nfl_season_start_date"], "%m/%d/%Y")
    final_date = nfl_season_start + datetime.timedelta(weeks=current_week)
    start_date = final_date - datetime.timedelta(days=6)
    final_date = datetime.datetime.strftime(final_date, "%Y%m%d")
    start_date = datetime.datetime.strftime(start_date, "%Y%m%d")
    return start_date, final_date


def get_team_abb():
    teams = get_teams()

    jack_t = get_team_abb_list(teams["Jack"])
    jordan_t = get_team_abb_list(teams["Jordan"])
    nathan_t = get_team_abb_list(teams["Nathan"])
    patrick_t = get_team_abb_list(teams["Patrick"])

    return jack_t, jordan_t, nathan_t, patrick_t


def get_team_owner(team, ja_t, jo_t, na_t, pa_t):
    if team in ja_t:
        name = "Jack"
    elif team in jo_t:
        name = "Jordan"
    elif team in na_t:
        name = "Nathan"
    elif team in pa_t:
        name = "Patrick"
    else:
        return "whoops"
    return name, Config["USERS"][name]["hexcolor"]


def get_current_week():
    tz = timezone("EST")
    nfl_season_start = datetime.datetime.strptime(Config["BASE_CONFIG"]["nfl_season_start_date"], "%m/%d/%Y")
    cur_date = datetime.datetime.now(tz).replace(tzinfo=None)
    delta = cur_date - nfl_season_start
    return max(1, int(np.floor(delta.days / 7) + 1))
