import os
import requests
import pandas as pd
from lxml import html

from flask import Flask, redirect, url_for, request, session, render_template, make_response
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_login import LoginManager, login_user, login_required, UserMixin

import configs
from app_helper_functions import get_team_list, get_team_abb, get_team_owner, get_owner_hex_value, get_teams
from get_homepage_data import get_homepage_data
from groupme_bot_functions import return_contestant, send_message, get_standings_message, get_standings

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'dogs-are-the-best'
app.config['SESSION_TYPE'] = 'filesystem'
FLASK_DEBUG = True

Session(app)


# Login code
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = ''


@app.route('/', methods=['GET', 'POST'])
def homepage():
    week = 3
    matchups, matchups_columns, matchups_two, owner_matchups, owner_matchups_columns = get_homepage_data(week)

    return render_template('nfl_wins_homepage.html', matchups=matchups, columns=matchups_columns,
                           matchups_two=matchups_two, owner_matchups=owner_matchups,
                           owner_matchups_columns=owner_matchups_columns)


@app.route('/groupmebot', methods=['POST'])
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
        'https://api.groupme.com/v3/groups/' + data['group_id'] + '?' + 'token=' + os.getenv('TOKEN')).json()
    # Keeping commented to test out other functionality for a minute
    groupme_users = dict()
    for member in user_json['response']['members']:
        groupme_users.update({member['user_id']: member['name']})

    # make sure the bot never replies to itself
    if currentuser == os.getenv('GROUPME_BOT_ID'):
        return

    # current message to be parsed
    currentmessage = data['text'].lower().strip()

    # Only if message is something we want to reply to do we request data from ESPN
    if currentmessage in configs.base_configs['Responses']:
        standings = get_standings()

        # If message is 'standings', print Jack, Jordan, Nathan, Patrick records
        if currentmessage == 'standings':
            message = get_standings_message(standings)
            return send_message(message)

        elif currentmessage == 'mother fucking standings':
            message = get_standings_message(standings)
            return send_message(message.upper())

        # Message options - either all teams, a player's teams, or print help

        elif len(currentmessage.split()) == 2 and currentmessage.split()[-1] == 'teams':
            name = currentmessage.split()[0].capitalize()
            if name in ['Jack', 'Jordan', 'Patrick', 'Nathan', 'All']:
                return_contestant(name, standings)
        elif currentmessage == 'nfl bot help':
            options = configs.base_configs['Responses']
            header = "Input options for the NFL Wins Tracker bot:\n"
            message = header + "\n".join(options)
            return send_message(message)
        elif currentmessage == 'my teams':
            return_contestant(groupme_users[currentuser].split()[0])
    elif currentmessage[:4].lower() == '!who':
        # I think this can be teams_list = [get_teams()] but will test later
        jack_teams, jordan_teams, nathan_teams, patrick_teams = get_teams()
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


# if __name__ == '__main__':
#     app.run()
if __name__ == "__main__":
    try:
        session.clear()
    except:
        pass
    app.run(port=6432, debug=True)
