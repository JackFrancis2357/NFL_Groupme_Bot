import os
import requests


def send_message(msg):
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
