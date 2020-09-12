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

    if currentmessage == 'coltssuck':
        msg = 'This is working'
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
