import datetime
import numpy as np
from pytz import timezone

import configs
from configs import Config
from helpers import sql_lib


def get_team_list(teams_list):
    team_abb_list = []
    for team in teams_list:
        if team == 'San Francisco 49Ers':
            team = 'San Francisco 49ers'
        team_abb_list.append(configs.team_mapping_configs[team][0])
    return team_abb_list


def fix_49ers(team):
    for i, tm in enumerate(team):
        if tm == 'San Francisco 49Ers':
            team[i] = 'San Francisco 49ers'
    return team


def get_teams():
    # TODO: Refactor this to at least be a dict of lists so we aren't hard-coding so much
    if Config['ENVIRONMENT'] == 'local_dev':
        teams = {
            "Jack": Config["Jack"],
            "Jordan": Config["Jordan"],
            "Nathan": Config["Nathan"],
            "Patrick": Config["Patrick"]
        }
    else:
        teams = {}
        base_query = "SELECT team_name FROM season " \
                     "JOIN team on team.id = season.team_id " \
                     "JOIN player on player.id = season.owner_id " \
                     "WHERE player_name='{}' and season='{}';"
        teams["Jack"] = [team[0].title() for team in sql_lib.execute_query(base_query.format("Jack Francis", "2022"))]
        teams["Jordan"] = [team[0].title() for team in
                           sql_lib.execute_query(base_query.format("Jordan Holland", "2022"))]
        teams["Patrick"] = [team[0].title() for team in
                            sql_lib.execute_query(base_query.format("Patrick Cooper", "2022"))]
        teams["Nathan"] = [team[0].title() for team in sql_lib.execute_query(base_query.format("Nathan Lee", "2022"))]

    # Check for 49Ers
    teams['Jack'] = fix_49ers(teams['Jack'])
    teams['Jordan'] = fix_49ers(teams['Jordan'])
    teams['Patrick'] = fix_49ers(teams['Patrick'])
    teams['Nathan'] = fix_49ers(teams['Nathan'])

    all_teams = []
    for lst in teams.values():
        all_teams += [val for val in lst]
    teams["all"] = all_teams
    for big_team in all_teams:
        for i, team in enumerate(big_team):

            # Title uppercases the first letter, so the e gets capitalized in 49ers
            if team == 'San Francisco 49Ers':
                big_team[i] = 'San Francisco 49ers'

    return teams


def get_team_abb():
    teams = get_teams()

    jack_t = get_team_list(teams["Jack"])
    jordan_t = get_team_list(teams["Jordan"])
    nathan_t = get_team_list(teams["Nathan"])
    patrick_t = get_team_list(teams["Patrick"])

    return jack_t, jordan_t, nathan_t, patrick_t


def get_owner_hex_value(name):
    if name == 'jack':
        return '#41B3A3'
    elif name == 'jordan':
        return '#E8A87C'
    elif name == 'nathan':
        return '#E27D60'
    elif name == 'patrick':
        return '#C38D9E'


def get_team_owner(team, ja_t, jo_t, na_t, pa_t):
    if team in ja_t:
        name = 'jack'
        return name, get_owner_hex_value(name)
    elif team in jo_t:
        name = 'jordan'
        return name, get_owner_hex_value(name)
    elif team in na_t:
        name = 'nathan'
        return name, get_owner_hex_value(name)
    elif team in pa_t:
        name = 'patrick'
        return name, get_owner_hex_value(name)
    else:
        return 'whoops'


def get_current_week():
    tz = timezone('EST')
    nfl_season_start = datetime.datetime.strptime(Config["nfl_season_start_date"], '%m/%d/%Y')
    cur_date = datetime.datetime.now(tz).replace(tzinfo=None)
    delta = cur_date - nfl_season_start
    return max(1, int(np.floor(delta.days / 7) + 1))
