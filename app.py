import logging
import os

import pandas as pd
import requests
from lxml import html
from flask import Flask, request

from configs import Config
from helpers import setup_logger

setup_logger.config_logger()

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    # The web hook that's called every time a message is sent in the chat.
    # The function receives the following JSON in a POST
    #       Credit: GroupMe Bot API V3
    #
    # {
    #   "attachments": [],
    #   "avatar_url": "http://i.groupme.com/123456789",
    #   "created_at": 1302623328,
    #   "group_id": "1234567890",
    #   "id": "1234567890",
    #   "name": "John",
    #   "sender_id": "12345",
    #   "sender_type": "user",
    #   "source_guid": "GUID",
    #   "system": false,
    #   "text": "Hello world ☃☃",
    #   "user_id": "1234567890"
    # }

    # json we receive for every message in the chat
    data = request.get_json()

    # The user_id of the user who sent the most recently message
    currentuser = data['user_id']
    user_json = requests.get(
        f"https://api.groupme.com/v3/groups/{data['group_id']}?token={os.getenv('TOKEN')}"
    ).json()
    groupme_users = dict()

    for member in user_json['response']['members']:
        groupme_users.update({member['user_id']: member['name']})

    # make sure the bot never replies to itself
    if currentuser == os.getenv('GROUPME_BOT_ID'):
        return

    # current message to be parsed
    currentmessage = data['text'].lower().strip()

    def return_contestant(name=str):
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

    # Only if message is something we want to reply to do we request data from ESPN
    if currentmessage in Config['Responses']:
        r = requests.get(f"{Config['espn_url']}")
        tree = html.fromstring(r.content)

        nfl_results_df = pd.DataFrame(0, index=range(32), columns=['Team', 'Wins', 'Losses', 'Ties'])
        base_xpath = '//*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/'

        ctr = 0
        # AFC Teams
        for i in range(1, 21):

            try:
                # Try to get team name - if playoff code has been added, span[3] is ARI; span[4] is Arizona Cardinals
                cur_team_data = tree.xpath(f'{base_xpath}div[1]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')

                if len(cur_team_data[0].text_content()) < 4:
                    cur_team_data = tree.xpath(f'{base_xpath}div[1]/div/div[2]/table/tbody/tr[{i}]/td/div/span[4]/a')
                team_name = cur_team_data[0].text_content()
            except:
                continue

            cur_team_wins = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
            cur_team_loss = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
            cur_team_tie = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

            wins = int(cur_team_wins[0].text_content())
            losses = int(cur_team_loss[0].text_content())
            ties = int(cur_team_tie[0].text_content())
            nfl_results_df.iloc[ctr, :] = team_name, wins, losses, ties
            ctr += 1

        # NFC Teams
        for i in range(1, 21):
            cur_team_data = tree.xpath(f'{base_xpath}div[2]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
            try:
                cur_team_data = tree.xpath(f'{base_xpath}div[2]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
                if len(cur_team_data[0].text_content()) < 4:
                    cur_team_data = tree.xpath(f'{base_xpath}div[2]/div/div[2]/table/tbody/tr[{i}]/td/div/span[4]/a')
                team_name = cur_team_data[0].text_content()
            except:
                continue

            cur_team_wins = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
            cur_team_loss = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
            cur_team_tie = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

            wins = int(cur_team_wins[0].text_content())
            losses = int(cur_team_loss[0].text_content())
            ties = int(cur_team_tie[0].text_content())
            nfl_results_df.iloc[ctr, :] = team_name, wins, losses, ties
            ctr += 1

        # TODO: Fix This
        jack_teams = configs.base_configs['Jack']
        jordan_teams = configs.base_configs['Jordan']
        nathan_teams = configs.base_configs['Nathan']
        patrick_teams = configs.base_configs['Patrick']
        all_teams = jack_teams + jordan_teams + patrick_teams + nathan_teams

        name_team = pd.DataFrame(columns=['Name', 'Team'])
        name_team['Team'] = all_teams
        for team_list, name in zip([jack_teams, jordan_teams, nathan_teams, patrick_teams],
                                   ['Jack', 'Jordan', 'Nathan', 'Patrick']):
            name_team.loc[name_team['Team'].isin(team_list), 'Name'] = name

        standings = name_team.merge(nfl_results_df, how='left', on='Team')

        # If message is 'standings', print Jack, Jordan, Nathan, Patrick records
        if currentmessage == 'standings':
            names = standings['Name'].unique().tolist()
            names.sort()
            wins = [int(i) for i in standings.groupby('Name').sum().reset_index()['Wins'].tolist()]
            losses = [int(i) for i in standings.groupby('Name').sum().reset_index()['Losses'].tolist()]
            message = str()
            for i in range(0, len(names)):
                message += names[i] + ': ' + str(wins[i]) + '-' + str(losses[i]) + '\n'
            print(message)

            return send_message(message)

        elif currentmessage == 'mother fucking standings':
            names = standings['Name'].unique().tolist()
            names.sort()
            wins = [int(i) for i in standings.groupby('Name').sum().reset_index()['Wins'].tolist()]
            losses = [int(i) for i in standings.groupby('Name').sum().reset_index()['Losses'].tolist()]
            message = str()
            for i in range(0, len(names)):
                message += names[i] + ': ' + str(wins[i]) + '-' + str(losses[i]) + '\n'
            print(message)

            return send_message(message.upper())

        # Message options - either all teams, a player's teams, or print help
        elif currentmessage == "patrick teams":
            return_contestant('Patrick')
        elif currentmessage == "jordan teams":
            return_contestant('Jordan')
        elif currentmessage == "nathan teams":
            return_contestant('Nathan')
        elif currentmessage == "jack teams":
            return_contestant('Jack')
        elif currentmessage == "all teams":
            return_contestant('All')
        elif currentmessage == 'nfl bot help':
            options = Config['Responses']
            header = "Input options for the NFL Wins Tracker bot:\n"
            message = header + "\n".join(options)
            return send_message(message)
        elif currentmessage == 'my teams':
            return_contestant(groupme_users[currentuser].split()[0])
    elif currentmessage[:4].lower() == '!who':
        jack_teams = configs.base_configs['Jack']
        jordan_teams = configs.base_configs['Jordan']
        nathan_teams = configs.base_configs['Nathan']
        patrick_teams = configs.base_configs['Patrick']
        teams_list = [jack_teams, jordan_teams, nathan_teams, patrick_teams]
        names = ['Jack', 'Jordan', 'Nathan', 'Patrick']
        team_id = currentmessage[6:]
        for owner in range(4):
            if team_id in teams_list[owner]:
                return send_message(names[owner])
            else:
                for team in teams_list[owner]:
                    if team_id in team:
                        return send_message(names[owner])


def send_message(msg):
    # sends a POST request to the GroupMe API with the message to be sent by the bot
    #
    # @Param msg : message to be sent to GroupMe chat

    url = 'https://api.groupme.com/v3/bots/post'

    payload = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg
    }

    try:
        response = requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(e)

    return response.status_code