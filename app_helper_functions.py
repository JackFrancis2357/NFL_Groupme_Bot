from configs import Config
import configs
import datetime
import numpy as np


def get_team_list(teams_list):
    team_abb_list = []
    for team in teams_list:
        team_abb_list.append(configs.team_mapping_configs[team][0])
    return team_abb_list


def get_teams():
    jack_teams = Config['Jack']
    jordan_teams = Config['Jordan']
    nathan_teams = Config['Nathan']
    patrick_teams = Config['Patrick']

    return jack_teams, jordan_teams, nathan_teams, patrick_teams


def get_team_abb():
    jack_teams, jordan_teams, nathan_teams, patrick_teams = get_teams()

    jack_t = get_team_list(jack_teams)
    jordan_t = get_team_list(jordan_teams)
    nathan_t = get_team_list(nathan_teams)
    patrick_t = get_team_list(patrick_teams)

    return jack_t, jordan_t, patrick_t, nathan_t


def get_owner_hex_value(name):
    if name == 'jack':
        return '#41B3A3'
    elif name == 'jordan':
        return '#E8A87C'
    elif name == 'patrick':
        return '#C38D9E'
    elif name == 'nathan':
        return '#E27D60'


def get_team_owner(team, ja_t, jo_t, pa_t, na_t):
    if team in ja_t:
        name = 'jack'
        return name, get_owner_hex_value(name)
    elif team in jo_t:
        name = 'jordan'
        return name, get_owner_hex_value(name)
    elif team in pa_t:
        name = 'patrick'
        return name, get_owner_hex_value(name)
    elif team in na_t:
        name = 'nathan'
        return name, get_owner_hex_value(name)
    else:
        return 'whoops'


def get_current_week():
    nfl_season_start = datetime.datetime.strptime('09/07/2021', '%m/%d/%Y')
    cur_date = datetime.datetime.today()
    delta = cur_date - nfl_season_start
    return max(1, int(np.floor(delta.days / 7) + 1))