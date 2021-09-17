import pandas as pd
from app_helper_functions import get_team_abb, get_team_owner, get_owner_hex_value
from groupme_bot_functions import get_standings
import datetime
import json
import requests


def get_homepage_data(current_week):
    matchups_df = pd.read_csv('./Weekly_Matchups.csv')
    current_matchups = matchups_df[f'Wk_{current_week}_Matchups']
    away_home_teams = current_matchups.str.split(pat='at', expand=True)
    away_home_teams.columns = ['Away', 'Home']
    away_home_teams['Away'] = away_home_teams['Away'].map(lambda x: x.rstrip())
    away_home_teams['Home'] = away_home_teams['Home'].map(lambda x: x.lstrip())

    ja_t, jo_t, pa_t, na_t = get_team_abb()
    weekly_matchups_df = pd.DataFrame(0, index=['jack', 'jordan', 'patrick', 'nathan'],
                                      columns=['jack', 'jordan', 'patrick', 'nathan'])

    # Get current scores
    nfl_season_start = datetime.datetime.strptime('09/07/2021', '%m/%d/%Y')
    final_date = nfl_season_start + datetime.timedelta(weeks=current_week)
    start_date = final_date - datetime.timedelta(days=6)
    final_date = datetime.datetime.strftime(final_date, '%Y%m%d')
    start_date = datetime.datetime.strftime(start_date, '%Y%m%d')

    score_dict = get_current_scores(start_date, final_date)

    matchups_columns = away_home_teams.columns
    matchups = []
    matchups_two = []
    for i in range(away_home_teams.shape[0]):
        away_team = away_home_teams['Away'][i]
        away_score = score_dict[away_team]
        home_team = away_home_teams['Home'][i]
        home_score = score_dict[home_team]
        away_owner, away_color = get_team_owner(str(away_team), ja_t, jo_t, pa_t, na_t)
        home_owner, home_color = get_team_owner(str(home_team), ja_t, jo_t, pa_t, na_t)

        doc = {
            'Away': away_team,
            'Away_Score': away_score,
            'Away_Owner': away_color,
            'Home': home_team,
            'Home_Score': home_score,
            'Home_Owner': home_color
        }
        if i < 8:
            matchups.append(doc)
        else:
            matchups_two.append(doc)

        weekly_matchups_df.loc[away_owner, home_owner] += 1
        weekly_matchups_df.loc[home_owner, away_owner] += 1

    owner_matchups = []
    for i in range(weekly_matchups_df.shape[0]):
        weekly_matchups_df.iloc[i, i] /= 2
        doc = {
            'owner': weekly_matchups_df.columns[i].capitalize(),
            'owner_color': get_owner_hex_value(weekly_matchups_df.columns[i]),
            'jack': weekly_matchups_df.iloc[i, 0],
            'jordan': weekly_matchups_df.iloc[i, 1],
            'patrick': weekly_matchups_df.iloc[i, 2],
            'nathan': weekly_matchups_df.iloc[i, 3],
        }
        owner_matchups.append(doc)

    owner_matchups_columns = [x.capitalize() for x in weekly_matchups_df.columns.tolist()]
    owner_matchups_columns.insert(0, 'Table')

    return matchups, matchups_columns, matchups_two, owner_matchups, owner_matchups_columns


def get_homepage_standings():
    standings = get_standings()

    standings = standings.drop(['Team'], axis=1)
    standings = standings.groupby(by='Name').sum().reset_index()
    standings_columns = standings.columns.tolist()
    standings_docs = []
    for i in range(standings.shape[0]):
        doc = {
            'owner': standings.iloc[i, 0],
            'owner_color': get_owner_hex_value(standings.iloc[i, 0].lower()),
            'wins': standings.iloc[i, 1],
            'losses': standings.iloc[i, 2],
            'ties': standings.iloc[i, 3]

        }
        standings_docs.append(doc)
    return standings_docs, standings_columns


def get_current_scores(start_date, final_date):
    score_dict = {}
    espn_score_data = requests.get(
        f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={start_date}-{final_date}").json()
    for event in espn_score_data['events']:
        for competition in event['competitions']:
            for competitor in competition['competitors']:
                score_dict[competitor['team']['abbreviation']] = competitor['score']
    return score_dict
