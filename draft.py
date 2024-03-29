import json
import logging

from configs import Config
from helpers import sql_lib, templates


def get_teams():
    """Get a list of teams from the database."""
    result = sql_lib.execute_query("SELECT team_name FROM team;")
    teams_list = []

    if result:
        for res in result:
            teams_list.append(res[0])
    return teams_list


def teams_drafted(season):
    """Get a list of teams drafted so far."""
    result = sql_lib.execute_query(
        f"SELECT team_name " f"FROM season " f"JOIN team " f"ON season.team_id = team.id " f"WHERE season='{season}';"
    )
    teams_list = []

    drafted_string = ""
    if result:
        for res in result:
            teams_list.append(res[0])
    for team in teams_list:
        drafted_string += f"{team}\n"
    return templates.teams_drafted.format(drafted_string)


def draft_team(user, team, season, position):
    """Enter the draft selection in the database."""

    # Get team ID given name
    team_id = sql_lib.execute_query(f"SELECT team.id FROM team where UPPER(team_name)='{team}';")[0][0]

    # Record draft selection
    _ = sql_lib.execute_query(
        f"INSERT INTO season (season, owner_id, team_id, draft_position) "
        f"SELECT '{season}' as season, player.id, {team_id} as team_id, {position} as draft_position "
        f"FROM player "
        f"WHERE player.groupme_user_id='{user}';"
    )


def check_team_draft_status(team, season):
    """Check if a team has already been drafted this year."""
    query = (
        f"SELECT * FROM season JOIN team on season.team_id  = team.id"
        f" WHERE upper(team_name)='{team}' AND season='{season}';"
    )
    return True if sql_lib.execute_query(query) else False


def get_teams_remaining():
    query_results = sql_lib.execute_query(
        f"SELECT team_name FROM team"
        f" JOIN (select id from team where not exists (select from season where season='{Config['season']}'"
        f" and team.id=season.team_id)) as team_result on team.id=team_result.id;"
    )
    result_string = ""
    for res in query_results:
        result_string += f"{res[0]}\n"
    return result_string


def get_username_by_id(user_id, participants):
    """Helper method to get name given ID."""
    for user in participants:
        if user["user_id"] == user_id:
            return user["name"]


def make_selection(user, message):
    logging.info(f"Received message: {message} from {user}")
    query_results = sql_lib.execute_query(f"select * from draft where season='{Config['season']}';")
    current_user = query_results[0][2]
    participants = query_results[0][0]
    team_count = sql_lib.execute_query(f"select count(*) from season where season='{Config['season']}';")[0][0]

    # Don't let a user draft out of turn
    if user != current_user:
        logging.info("User out of turn - returning message")
        return templates.out_of_turn.format(get_username_by_id(current_user, participants))

    # Parse out a valid team
    selection = message.split("draft ")[1]
    teams = [team.upper() for team in get_teams()]

    if check_team_draft_status(selection.upper(), Config["season"]):
        # TODO: Add draft status method
        logging.info("Selection has already been taken - returning message")
        return templates.selection_taken.format(selection.title())

    if selection.upper() in teams:
        logging.info(f"Valid selection of: {selection.upper()}")
        logging.info("Logging user selection in database")
        draft_team(current_user, selection.upper(), Config["season"], team_count + 1)

        # Send a message to the group that the pick has been made
        # Use this variable to hold the user who picked - current user will now be the next up
        # Reallyyyy need to refactor this at some point
        pick_made_by = get_username_by_id(current_user, participants)

        # Set the next drafter - update current_user variable to reflect this
        set_current_drafter()
        current_user = sql_lib.execute_query(f"select current_drafter from draft where season='{Config['season']}';")[
            0
        ][0]

        ack_message = templates.draft_acknowledgment.format(
            team_count + 1, pick_made_by, selection.title(), get_username_by_id(current_user, participants)
        )

        # End the draft if all teams are drafted
        if team_count + 1 >= int(Config["num_teams"]):
            logging.info("End of draft! Returning message")
            sql_lib.execute_query(f"update draft set active={False};")
            return templates.end_message.format(Config["season"])

        logging.info("Successful pick made - returning message")
        return ack_message
    else:
        logging.info("Invalid selection received - returning message")
        return templates.draft_failure.format(selection)


def draft_active():
    result = sql_lib.execute_query(f"select active from draft where season='{Config['season']}';")
    if result:
        return result[0][0]


def init_draft(participants, draft_order=None, snake=True):
    current_drafter = draft_order[0]
    participants_string = json.dumps(participants).replace("'", '"')
    draft_order_string = json.dumps(draft_order).replace("'", '"').replace("[", "{").replace("]", "}")
    query = f"insert into draft(participants, draft_order, current_drafter, snake, season, active) values ('{participants_string}', '{draft_order_string}', '{current_drafter}', {snake}, '{Config['season']}', {True});"
    sql_lib.execute_query(query, update=True)
    welcome_message = templates.draft_welcome_message.format(
        Config["season"],
        get_username_by_id(draft_order[0], participants),
        get_username_by_id(draft_order[1], participants),
        get_username_by_id(draft_order[2], participants),
        get_username_by_id(draft_order[3], participants),
        get_username_by_id(draft_order[0], participants),
    )
    return welcome_message


def set_current_drafter():
    query_results = sql_lib.execute_query(f"select * from draft where season='{Config['season']}';")
    draft_order = query_results[0][1]
    current_user = query_results[0][2]
    snake = query_results[0][3]

    # Handle the snake draft scenario
    if snake and current_user == draft_order[-1]:
        # Reverse the draft order
        logging.info("Reversing the draft order for snake")
        draft_order_reverse = draft_order[::-1]
        draft_order_reverse = json.dumps(draft_order_reverse).replace("'", '"').replace("[", "{").replace("]", "}")
        sql_lib.execute_query(f"update draft set draft_order='{draft_order_reverse}';", update=True)
        # Current user stays the same - snake
        return

    # Core draft indexing
    for index in range(len(draft_order)):
        if draft_order[index] == current_user:
            current_user = draft_order[index + 1]
            sql_lib.execute_query(f"update draft set current_drafter={current_user};", update=True)
            logging.info(f"Current user set: {current_user}")
            return


# class Draft:
#     def __init__(self, participants, draft_order=None, snake=True):
#         self.season = Config["season"]
#         self.participants = participants
#         self.draft_order = draft_order or self.set_draft_order()
#         self.current_user = None
#         self.team_count = 0
#         self.snake = snake
#
#     def init_draft(self):
#         self.set_current_drafter()
#
#         welcome_message = templates.draft_welcome_message.format(
#             self.season,
#             self._get_username_by_id(self.draft_order[0]),
#             self._get_username_by_id(self.draft_order[1]),
#             self._get_username_by_id(self.draft_order[2]),
#             self._get_username_by_id(self.draft_order[3]),
#             self._get_username_by_id(self.draft_order[0])
#         )
#         return welcome_message
#
#     def set_draft_order(self):
#         """Randomly order participants for the draft."""
#
#         rank = {}
#         logging.info("Randomizing draft order")
#
#         # Assign each participant a random decimal
#         for par in self.participants:
#             rank.update({par["user_id"]: random.random()})
#
#         # Sort the decimal values in ascending order
#         sorted_order = sorted([value for value in rank.values()])
#
#         # Reorder the keys (participants) based on the order decimals
#         draft_order = []
#         for sor in sorted_order:
#             for key, value in rank.items():
#                 if value == sor:
#                     draft_order.append(key)
#
#         return draft_order
#
#     # TODO: This would be better done with a generator - research
#     def set_current_drafter(self):
#         if not self.current_user:
#             self.current_user = self.draft_order[0]
#             logging.info(f"Current user set: {self.current_user}")
#             return
#
#         # Handle the snake draft scenario
#         if self.snake and self.current_user == self.draft_order[-1]:
#             # Reverse the draft order
#             logging.info("Reversing the draft order for snake")
#             self.draft_order = self.draft_order[::-1]
#             # Current user stays the same - snake
#             return
#
#         # Core draft indexing
#         for index in range(len(self.draft_order)):
#             if self.draft_order[index] == self.current_user:
#                 self.current_user = self.draft_order[index + 1]
#                 logging.info(f"Current user set: {self.current_user}")
#                 return
#
#     def get_teams_drafted(self):
#         teams = teams_drafted(self.season)
#         drafted_string = ""
#         for team in teams:
#             drafted_string += f"{team}\n"
#         return templates.teams_drafted.format(drafted_string)
#
#     def make_selection(self, user, message):
#
#         logging.info(f"Received message: {message} from {user}")
#
#         # Don't let a user draft out of turn
#         if user != self.current_user:
#             logging.info("User out of turn - returning message")
#             return templates.out_of_turn.format(
#                 self._get_username_by_id(self.current_user)
#             )
#
#         # Parse out a valid team
#         selection = message.split("draft ")[1]
#         teams = [team.upper() for team in get_teams()]
#
#         if check_team_draft_status(selection.upper(), self.season):
#             # TODO: Add draft status method
#             logging.info("Selection has already been taken - returning message")
#             return templates.selection_taken.format(selection.title())
#
#         if selection.upper() in teams:
#             logging.info(f"Valid selection of: {selection.upper()}")
#             logging.info("Logging user selection in database")
#             draft_team(
#                 self._get_username_by_id(self.current_user),
#                 selection.upper(),
#                 self.season,
#                 self.team_count + 1
#             )
#
#             # Send a message to the group that the pick has been made
#             # Use this variable to hold the user who picked - current user will now be the next up
#             # Reallyyyy need to refactor this at some point
#             pick_made_by = self._get_username_by_id(self.current_user)
#             self.set_current_drafter()
#             self.team_count += 1
#             ack_message = templates.draft_acknowledgment.format(
#                 self.team_count,
#                 pick_made_by,
#                 selection.title(),
#                 self._get_username_by_id(self.current_user)
#             )
#
#             # End the draft if all teams are drafted
#             if self.team_count >= int(Config["num_teams"]):
#                 logging.info("End of draft! Returning message")
#                 return templates.end_message.format(self.season)
#
#             logging.info("Successful pick made - returning message")
#             return ack_message
#         else:
#             logging.info("Invalid selection received - returning message")
#             return templates.draft_failure.format(selection)
#
#     def _get_username_by_id(self, user_id):
#         """Helper method to get name given ID."""
#         for user in self.participants:
#             if user["user_id"] == user_id:
#                 return user["name"]
