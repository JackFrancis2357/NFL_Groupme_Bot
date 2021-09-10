import logging
import os
import requests
import pandas as pd
from lxml import html
from app_helper_functions import get_teams
import configs


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'
    payload = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg
    }
    try:
        response = requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        logging.error(e)
    return response.status_code


def return_contestant(name, standings):
    if name == 'All':
        teams = standings.loc[:, 'Team'].tolist()
        wins = [int(i) for i in standings.loc[:, 'Wins'].tolist()]
        losses = [int(i) for i in standings.loc[:, 'Losses'].tolist()]
        message = str()
        for i in range(0, len(teams)):
            message += teams[i] + ': ' + str(wins[i]) + '-' + str(losses[i]) + '\n'

        return send_message(message)
    else:
        teams = standings.loc[standings['Name'] == name, 'Team'].tolist()
        wins = [int(i) for i in standings.loc[standings['Name'] == name, 'Wins'].tolist()]
        losses = [int(i) for i in standings.loc[standings['Name'] == name, 'Losses'].tolist()]
        message = str()
        for i in range(0, len(teams)):
            message += teams[i] + ': ' + str(wins[i]) + '-' + str(losses[i]) + '\n'

        return send_message(message)


def get_standings_message(standings):
    names = standings['Name'].unique().tolist()
    names.sort()
    wins = [int(i) for i in standings.groupby('Name').sum().reset_index()['Wins'].tolist()]
    losses = [int(i) for i in standings.groupby('Name').sum().reset_index()['Losses'].tolist()]
    message = str()
    for i in range(0, len(names)):
        message += names[i] + ': ' + str(wins[i]) + '-' + str(losses[i]) + '\n'
    return (message)


def get_team_data_espn(tree, base_xpath, i, conference_div):
    try:
        cur_team_data = tree.xpath(f'{base_xpath}div[{conference_div}]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
        if len(cur_team_data[0].text_content()) < 4:
            cur_team_data = tree.xpath(
                f'{base_xpath}div[{conference_div}]/div/div[2]/table/tbody/tr[{i}]/td/div/span[4]/a')
        team_name = cur_team_data[0].text_content()
    except IndexError:
        return 'error', '', '', ''

    cur_team_wins = tree.xpath(
        f'{base_xpath}div[{conference_div}]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
    cur_team_loss = tree.xpath(
        f'{base_xpath}div[{conference_div}]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
    cur_team_tie = tree.xpath(
        f'{base_xpath}div[{conference_div}]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

    wins = int(cur_team_wins[0].text_content())
    losses = int(cur_team_loss[0].text_content())
    ties = int(cur_team_tie[0].text_content())

    return team_name, wins, losses, ties


def get_standings():
    r = requests.get("https://www.espn.com/nfl/standings")
    tree = html.fromstring(r.content)

    nfl_results_df = pd.DataFrame(0, index=range(32), columns=['Team', 'Wins', 'Losses', 'Ties'])
    base_xpath = '//*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/'
    ctr = 0
    # AFC Teams
    for i in range(1, 21):
        team_name, wins, losses, ties = get_team_data_espn(tree=tree, base_xpath=base_xpath, i=i, conference_div=1)
        if team_name == 'error':
            continue
        nfl_results_df.iloc[ctr, :] = team_name, wins, losses, ties
        ctr += 1

    # NFC Teams
    for i in range(1, 21):
        team_name, wins, losses, ties = get_team_data_espn(tree=tree, base_xpath=base_xpath, i=i, conference_div=2)
        if team_name == 'error':
            continue
        nfl_results_df.iloc[ctr, :] = team_name, wins, losses, ties
        ctr += 1

    jack_teams, jordan_teams, patrick_teams, nathan_teams = get_teams()
    all_teams = jack_teams + jordan_teams + patrick_teams + nathan_teams

    name_team = pd.DataFrame(columns=['Name', 'Team'])
    name_team['Team'] = all_teams
    for team_list, name in zip([jack_teams, jordan_teams, nathan_teams, patrick_teams],
                               ['Jack', 'Jordan', 'Nathan', 'Patrick']):
        name_team.loc[name_team['Team'].isin(team_list), 'Name'] = name

    standings = name_team.merge(nfl_results_df, how='left', on='Team')

    return standings


def get_schedule(team_id, starting_week, finishing_week=18):
    for k, v in configs.team_mapping_configs.items():
        if team_id in k:
            team_abbreviation = v[0]

    nfl_schedule_df = pd.read_csv('./2021_NFL_Schedule_Grid.csv')
    try:
        schedule = nfl_schedule_df.loc[nfl_schedule_df['Team'] == team_abbreviation]
    except:
        return ''

    schedule_columns = schedule.columns.tolist()[starting_week:finishing_week]
    opponents = [x for x in schedule.iloc[0, starting_week:finishing_week]]

    message = ''
    for col, opp in zip(schedule_columns, opponents):
        message += col + ': ' + opp + '\n'

    return send_message(message)
