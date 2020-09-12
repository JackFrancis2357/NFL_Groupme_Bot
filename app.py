# TrentBot
#
# A small python bot built to help with the administration of large GroupMe
# group chats. Run on heroku free dynos and reads user messages to activate
# commands.
#
# Types of commands:
# PRIVILEGEDD - requesting user must be in the Heroku config variable 'PRIV_USERS'
# COMMAND - any requesting user is able to make the command be executed
# HIDDEN - contextual command, cannot be requested explicity
#
# Built by Trent Prynn

import os
import json
import requests
import random
import ast
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import html

from flask import Flask, request

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

    # current message to be parsed
    currentmessage = data['text'].lower().strip()

    # make sure the bot never replies to itself
    if currentuser == os.getenv('GROUPME_BOT_ID'):
        return

    if currentmessage == 'colts suck':
        r = requests.get("https://www.pro-football-reference.com/years/2020/")
        tree = html.fromstring(r.content)

        nfl_results_df = pd.DataFrame(0, index=range(32), columns=['Team Name', 'Wins', 'Losses'])

        ctr = 0
        for i in range(1, 21):
            cur_team_data = tree.xpath(f'//*[@id="AFC"]/tbody/tr[{i}]/td')
            team_data = [td.text_content().strip() for td in cur_team_data]
            if team_data[0][:3] == 'AFC' or team_data[0][:3] == 'NFC':
                continue
            cur_team_wins, cur_team_loss = team_data[0], team_data[1]
            current_team = tree.xpath(f'//*[@id="AFC"]/tbody/tr[{i}]/th')
            team_name = [td.text_content().strip() for td in current_team]
            nfl_results_df.iloc[ctr, :] = team_name[0], cur_team_wins, cur_team_loss
            ctr += 1

            # NFC
            cur_team_data = tree.xpath(f'//*[@id="NFC"]/tbody/tr[{i}]/td')
            team_data = [td.text_content().strip() for td in cur_team_data]
            if team_data[0][:3] == 'AFC' or team_data[0][:3] == 'NFC':
                continue
            cur_team_wins, cur_team_loss = team_data[0], team_data[1]
            current_team = tree.xpath(f'//*[@id="NFC"]/tbody/tr[{i}]/th')
            team_name = [td.text_content().strip() for td in current_team]
            nfl_results_df.iloc[ctr, :] = team_name[0], cur_team_wins, cur_team_loss
            ctr += 1

        jack_teams = ['Baltimore Ravens', 'Tennessee Titans', 'New York Jets', 'Miami Dolphins',
                      'New England Patriots', 'Atlanta Falcons', 'San Francisco 49ers', 'Arizona Cardinals']
        jordan_teams = ['Jacksonville Jaguars', 'Kansas City Chiefs', 'Las Vegas Raiders', 'Detroit Lions',
                        'Minnesota Vikings', 'Chicago Bears', 'Dallas Cowboys', 'Seattle Seahawks']
        patrick_teams = ['Cincinnati Bengals', 'Cleveland Browns', 'Houston Texans', 'Denver Broncos',
                         'Green Bay Packers', 'New Orleans Saints', 'Philadelphia Eagles', 'New York Giants']
        nate_teams = ['Pittsburgh Steelers', 'Indianapolis Colts', 'Buffalo Bills', 'Los Angeles Chargers',
                      'Carolina Panthers', 'Tampa Bay Buccaneers', 'Washington Football Team', 'Los Angeles Rams']

        list_of_teams = [jack_teams, jordan_teams, patrick_teams, nate_teams]
        list_of_records = []

        for team in list_of_teams:
            current_wins = 0
            current_losses = 0
            for i in range(8):
                current_wins += int(nfl_results_df['Wins'][nfl_results_df['Team Name'] == team[i]])
                current_losses += int(nfl_results_df['Losses'][nfl_results_df['Team Name'] == team[i]])
            list_of_records.append(current_wins)
            list_of_records.append(current_losses)

        msg = f'Jack: {list_of_records[0]}-{list_of_records[1]} \
        Jordan: {list_of_records[2]}-{list_of_records[3]} \
        Patrick: {list_of_records[4]}-{list_of_records[5]} \
        Nathan: {list_of_records[6]}-{list_of_records[7]}'

        send_message(msg)

    return "ok", 200


def send_message(msg):
    # sends a POST request to the GroupMe API with the message to be sent by the bot
    #
    # @Param msg : message to be sent to GroupMe chat

    url = 'https://api.groupme.com/v3/bots/post'

    payload = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg
    }

    response = requests.post(url, json=payload)
