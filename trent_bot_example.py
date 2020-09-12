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

import o
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
    if (currentuser == os.getenv('GROUPME_BOT_USER_ID')):
        return

    # dictionary that maps valid string to their functions
    commands = map_strings_to_functions()

    # look if the message is a command
    command_function_requested = commands.get(currentmessage)

    if (command_function_requested) is not None:
        # here if the user requested a valid command, perform it
        command_function_requested(currentuser)
    else:
        # user's message was not a valid command, parse it
        parse_normal_user_message(currentmessage, currentuser)

    return "ok", 200

def map_strings_to_functions():
    # returns a dictionary that maps user strings to their requested, supported function.
    #
    # Using this we can simply get the function from the dictionary and since all functions take the
    # same parameter(s) we just pass them for every call even if that specific function may not
    # use it. Doing this also allows us to have all valid commands in a central location so we
    # can print them out easily for users going forward.
    #
    # The key to this working is that all supported commands take common parameter(s) so we can
    # call each command with the same, generic parameter(s) and they will make use of them if needed

    # create a combined dictionary of all commands
    all_commands = {**common_commands(), **privileged_commands()}
    return all_commands

def common_commands():
    # returns a mapping of commands strings to function references that any user may use
    common_commands = {'!commands' : commands, '!privcommands' : privcommands}
    return common_commands

def privileged_commands():
    # returns a mapping of command strings to function reference that only privileged users may use
    priv_commands = {'!list' : listusers, '!alertall' : alertall}
    return priv_commands

def listusers(user):
    # PRIVILEGED COMMAND
    #
    # Retrieves a list of the group's current users (nicknames) and sends the string representation
    #
    # @Param user : The user_id of the user requesting to perform this command

    if user_is_privileged(user):
        group_members = get_group_members()
        send_message(str(group_members))

def alertall(user):
    # PRIVILEGED COMMAND
    #
    # alerts all users in the chat by @mentioning them all individually in a message.
    # This alerts them because when you @mention somebody in a GroupMe chat it bypasses
    # their mute settings and they receive a push notification
    #
    # @Param user : the user_id of the user requesting to perform this command

    if user_is_privileged(user):
        # gets current json representation of the group
        members_json =  get_group_members_json()

        # create dictionary that maps from member usernames to their userid's
        members_dict = create_members_dict(members_json)

        # msg      = the message string to be sent with the mentions
        #               i.e -- '@trent @john @etc...'
        # loci     = nested list where each list contains the start location of the mention
        #            and the length of the mention
        #               i.e -- [[0, 10], [10, 20], ...]
        # user_ids = a list of the user_ids we want to mention
        #               i.e -- [1234, 5678, ...]
        msg = ''
        loci = []
        user_ids = []

        # loops through all current members and builds the message and
        # the loci / user_ids lists for mentioning all users in a single message
        current_pos_in_string = 0
        for member in members_dict:
            msg += '@' + member + ' '
            loci.append([current_pos_in_string, current_pos_in_string + len(msg)])
            user_ids.append(members_dict.get(member))
            current_pos_in_string += len(msg)

        url = 'https://api.groupme.com/v3/bots/post'

        # mentions are sent as attachments to the text
        payload = {
            'attachments' : [
                    {
                    'type': 'mentions',
                    'loci': loci,
                    'user_ids': user_ids
                    }
                ],
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text' : msg
            }

        r = requests.post(url, json = payload)

def commands(user):
    # COMMON COMMAND
    #
    # lists the current commands any user may use
    #
    # @Param user : the user_id of the user requesting to perform this command

    # build string of all common commands
    common_commands_str = (', '.join('"' + command + '"' for command in common_commands()))

    # spacing for message sending
    msg = ('Current commands are as follows:         %s' % common_commands_str)
    send_message(msg)

def privcommands(user):
    # COMMON COMMAND
    #
    # lists the commands only privileged user may use
    #
    # @Param user : the user_id of the user requesting to perform this command

    # build_string of all privileged commands
    priv_commands_str = (', '.join('"' + command + '"' for command in privileged_commands()))

    msg = ('Current privileged commands are as follows: %s --  please note use of '
           'these commands require elevated privileges granted by the administrator '
           'of this bot' % priv_commands_str)
    send_message(msg)

def bmwjoke():
    # HIDDEN COMMAND
    #
    # Corrects someone whose message contains "BMW" by replying with a random BMW joke message

    bmw_responses = ['bimmuh*', 'It\'s pronounced Bavarian Motorworks you slob', 'Beemer*',
                     'Is it an E46 though?', '*Perfect weight distribution*', 'OwO beemie weemie OwO',
                     'BMuWuuuuu*', 'The greatest car company in the world*', 'The Vanos problem is totally overblown',
                     'The cooling systems are FINE', 'My E46 was my only friend in college', 'RIP Conner',
                     'Should have taken the E46 instead of the Porsche -Paul Walker', 'I\'m going to manual swap it']
    send_message(random.choice(bmw_responses))

def joke():
    # HIDDEN COMMAND
    #
    # Used to reply anytime a user speaks in the chat that in the JOKE_USERS config variable
    joke_responses = ['Stop.', 'BMW is the best you\'re right', 'e46?']

    send_message(random.choice(joke_responses))

def command_not_recognized():
    # HIDDEN COMMAND
    #
    # sends a message letting a user know their command was not recognized
    # then sends what the current commands are

    msg = 'Sorry, your command was not recognized, use !commands to see valid user commands'
    send_message(msg)

def user_not_privileged():
    # HIDDEN COMMAND
    #
    # helper function that sends a message explaining the user does not have sufficient
    # permissions to perform a requested command

    msg = "Sorry, you don't have sufficient privileges to perform the requested command"
    send_message(msg)

def send_message(msg):
    # sends a POST request to the GroupMe API with the message to be sent by the bot
    #
    # @Param msg : message to be sent to GroupMe chat

    url = 'https://api.groupme.com/v3/bots/post'

    payload = {
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text' : msg
           }

    response = requests.post(url, json = payload)

def parse_normal_user_message(message, user):
    # parse a normal user message so we can look for invalid command attempts and perform
    # joke responses if we so wish
    #
    # @Param user_message : message to parse
    # @Param user : the user_id of the user requesting to perform this command

    # check for invalid commands
    if message[0] == '!':
        command_not_recognized()

    # check for joke responses, can be toggled on/off in 'parse_for_joke_responses'
    else:
        parse_for_joke_responses(message, user)

def parse_for_joke_responses(user_message, user):
    # parse the user's message and check for whatever jokes / responses we would like to send
    # back, we put this in it's own function so we can remove and or toggle it easily
    #
    # @Param user_message : message to parse
    # @Param user : the user_id of the user requesting to perform this command

    # toggle joke responses on and off here
    joke_responses_enabled = True

    # if jokes are off simply return and skip parsing
    if not joke_responses_enabled:
        return

    # here if we want to start checking for joke responses
    if "bmw" in user_message:
        bmwjoke()

    elif user_in_joke_users(user):
        joke()

def get_group_members():
    # creates and returns a list of all current users nicknames

    # retrieves a json (python dictionary) format of all current members in the group
    members_json = get_group_members_json()

    # creates a list of all user's current nicknames in chat
    members = []
    for member in members_json:
        members.append(member.get("nickname"))

    return sorted(members)

def get_group_members_json():
    # returns a json representation of all members in the chat

    url = 'https://api.groupme.com/v3/groups/' + os.getenv('GROUPME_GROUP_ID')

    data = {
            'token' : os.getenv('GROUPME_BOT_ACCESS_TOKEN')
           }

    response = requests.get(url, params = data)

    # retrieves the json format of all members currently in the chat
    members_json = response.json().get("response").get("members")

    return members_json

def create_members_dict(members_json):
    # parse the previously created members json and create a dictionary that
    # maps from their current GroupMe nickname to their user_id
    #
    # @Param members_json : GroupMe json format of all members in chat

    # maps each member's current nickname to their user_id
    members_dict = {}
    for member in members_json:
        members_dict[member.get("nickname")] = member.get("user_id")

    return members_dict

def user_is_privileged(user):
    # returns True if the user is able to use privileged commands and False otherwise.
    # if false is going to be returned we send a message to the chat saying so
    #
    # @Param user : the user_id to check for privilege

    # list of current user_ids with elevated privileges
    priv_users = ast.literal_eval(os.getenv('PRIV_USERS'))

    if user in priv_users:
        return True
    else:
        # user not privileged, send message saying so and return false
        user_not_privileged()
        return False

def user_in_joke_users(user):
    # returns True if user is in the current list of joke users
    #
    # @Param user : the user_id to check for privilege

    joke_users = ast.literal_eval(os.getenv('JOKE_USERS'))
    return user in joke_users
