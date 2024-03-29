import logging
import os

from flask import Flask, render_template, request, session
from flask_bootstrap import Bootstrap

# import draft
from configs import Config
from flask_session import Session
from helpers import groupme_lib, setup_logger
from src.app_helper_functions import get_current_week, get_teams
from src.get_homepage_data import get_homepage_data, get_homepage_standings
from src.groupme_bot_functions import (get_schedule, get_standings,
                                       get_standings_message,
                                       return_contestant, send_message)

setup_logger.config_logger()
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET")
app.config["SESSION_TYPE"] = "filesystem"
FLASK_DEBUG = True
Session(app)

logger = logging.getLogger(__name__)

@app.route("/", methods=["GET", "POST"])
def homepage():
    week = get_current_week()
    (
        matchups,
        matchups_columns,
        matchups_two,
        owner_matchups,
        owner_matchups_columns,
        current_week_record_df,
    ) = get_homepage_data(week)
    logger.info("Finished getting homepage data")
    standings_docs, standings_columns = get_homepage_standings(current_week_record_df, week)
    logger.info("Finished getting homepage standings")
    logger.info("Rendering Page")
    return render_template(
        "nfl_wins_homepage.html",
        matchups=matchups,
        columns=matchups_columns,
        matchups_two=matchups_two,
        owner_matchups=owner_matchups,
        owner_matchups_columns=owner_matchups_columns,
        standings=standings_docs,
        standings_columns=standings_columns,
    )


@app.route("/groupmebot", methods=["POST"])
def webhook():
    # json we receive for every message in the chat
    data = request.get_json()
    logging.info(f"Received: {data}")

    # The user_id of the user who sent the most recent message
    current_user = data["user_id"]
    groupme_users = groupme_lib.get_users()

    # make sure the bot never replies to itself
    if current_user == os.getenv("GROUPME_BOT_ID"):
        return

    # current message to be parsed
    current_message = data["text"].lower().strip()
    split_current_message = current_message.split()

    ######################
    ##### DRAFT LOGIC #####
    ######################
    # TODO Enable Draft with Postgres on Render and other DB functionality. Commenting out to get core functionaltiy
    # if Config["draft_enabled"]:
    #     # Start draft if it isn't already active
    #     if current_message.lower() == "start draft" and not draft.draft_active():
    #         draft_init_message = draft.init_draft(groupme_users, Config["custom_draft_order"])
    #         return send_message(draft_init_message)

    #     if not draft.draft_active():
    #         return

    #     if current_message.lower() == "draft available teams":
    #         return send_message(f"Teams Available:\n{draft.get_teams_remaining()}")
    #     elif current_message.lower() == "draft status":
    #         teams_draft_message = draft.teams_drafted(Config["season"])
    #         return send_message(teams_draft_message)
    #     elif current_message.lower().startswith("draft"):
    #         selection_message = draft.make_selection(current_user, current_message)
    #         return send_message(selection_message)

    # Only if message is something we want to reply to do we request data from ESPN
    if current_message in Config["RESPONSES"]:
        week = get_current_week()
        standings = get_standings(week)

        # If message is 'standings', print Jack, Jordan, Nathan, Patrick records
        if current_message == "standings":
            logging.info(f"Forming standings message with standings: {standings}")
            message = get_standings_message(standings)
            return send_message(message)

        elif current_message == "standings right now":
            message = get_standings_message(standings)
            return send_message(message.upper())

        # Message options - either all teams, a player's teams, or print help

        elif len(split_current_message) == 2 and split_current_message[-1] == "teams":
            name = current_message.split()[0].capitalize()
            if name in ["Jack", "Jordan", "Patrick", "Nathan", "All"]:
                return_contestant(name, standings)
            elif name == "My":
                user = next(item for item in groupme_users if item["user_id"] == current_user)["name"].split()[0]
                return_contestant(user, standings)
        elif current_message == "nfl bot help":
            options = Config["RESPONSES"]
            header = "Input options for the NFL Wins Tracker bot:\n"
            message = header + "\n".join(options)
            return send_message(message)

    elif current_message[:4].lower() == "!who":
        # I think this can be teams_list = [get_teams()] but will test later
        teams = get_teams()
        teams_list = [teams["Jack"], teams["Jordan"], teams["Nathan"], teams["Patrick"]]
        names = ["Jack", "Jordan", "Nathan", "Patrick"]
        team_id = current_message[6:]
        for owner in range(4):
            if team_id in teams_list[owner]:
                return send_message(names[owner])
            else:
                for team in teams_list[owner]:
                    if team_id in team:
                        return send_message(names[owner])
    elif current_message == "weblink":
        host = (
            Config["BASE_CONFIG"]["test_url"] if Config["ENVIRONMENT"] == "TEST" else Config["BASE_CONFIG"]["prod_url"]
        )
        return send_message(host)

    elif split_current_message[0] == "schedule":
        if len(split_current_message) == 1:
            return ""
        else:
            team_id = split_current_message[1].capitalize()
            starting_week = get_current_week()
            try:
                if (
                    split_current_message[0] == "schedule"
                    and split_current_message[2] == "next"
                    and split_current_message[3].isdigit()
                ):
                    finishing_week = starting_week + int(split_current_message[3])
            except IndexError:
                finishing_week = 19
            get_schedule(team_id, starting_week, finishing_week=finishing_week)


# if __name__ == '__main__':
#     app.run()
if __name__ == "__main__":
    try:
        session.clear()
    except:
        pass
    app.run(port=6432, debug=True)
