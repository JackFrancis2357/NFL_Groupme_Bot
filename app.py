import os
import requests
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
        r = requests.get("https://www.espn.com/nfl/standings")
        tree = html.fromstring(r.content)

        nfl_results_df = pd.DataFrame(0, index=range(32), columns=['Team Name', 'Wins', 'Losses', 'Ties'])
        base_xpath = '//*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/'

        ctr = 0
        # AFC Teams
        for i in range(1, 21):
            cur_team_data = tree.xpath(f'{base_xpath}div[1]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
            team_name = [td.text_content().strip() for td in cur_team_data]
            if not team_name:
                continue
            cur_team_wins = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
            cur_team_loss = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
            cur_team_tie = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

            wins = [td.text_content().strip() for td in cur_team_wins]
            losses = [td.text_content().strip() for td in cur_team_loss]
            ties = [td.text_content().strip() for td in cur_team_tie]
            nfl_results_df.iloc[ctr, :] = team_name[0], wins[0], losses[0], ties[0]
            ctr += 1

        # NFC Teams
        for i in range(1, 21):
            cur_team_data = tree.xpath(f'{base_xpath}div[2]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
            team_name = [td.text_content().strip() for td in cur_team_data]
            if not team_name:
                continue
            cur_team_wins = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
            cur_team_loss = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
            cur_team_tie = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

            wins = [td.text_content().strip() for td in cur_team_wins]
            losses = [td.text_content().strip() for td in cur_team_loss]
            ties = [td.text_content().strip() for td in cur_team_tie]
            nfl_results_df.iloc[ctr, :] = team_name[0], wins[0], losses[0], ties[0]
            ctr += 1

        jack_teams = ['Baltimore Ravens', 'Tennessee Titans', 'New York Jets', 'Miami Dolphins',
                      'New England Patriots', 'Atlanta Falcons', 'San Francisco 49ers', 'Arizona Cardinals']
        jordan_teams = ['Jacksonville Jaguars', 'Kansas City Chiefs', 'Las Vegas Raiders', 'Detroit Lions',
                        'Minnesota Vikings', 'Chicago Bears', 'Dallas Cowboys', 'Seattle Seahawks']
        patrick_teams = ['Cincinnati Bengals', 'Cleveland Browns', 'Houston Texans', 'Denver Broncos',
                         'Green Bay Packers', 'New Orleans Saints', 'Philadelphia Eagles', 'New York Giants']
        nate_teams = ['Pittsburgh Steelers', 'Indianapolis Colts', 'Buffalo Bills', 'Los Angeles Chargers',
                      'Carolina Panthers', 'Tampa Bay Buccaneers', 'Washington', 'Los Angeles Rams']

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

        msg1 = f'Jack: {list_of_records[0]}-{list_of_records[1]} \n'
        msg2 = f'Jordan: {list_of_records[2]}-{list_of_records[3]} \n'
        msg3 = f'Patrick: {list_of_records[4]}-{list_of_records[5]} \n'
        msg4 = f'Nathan: {list_of_records[6]}-{list_of_records[7]}'

        send_message(msg1 + msg2 + msg3 + msg4)

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
