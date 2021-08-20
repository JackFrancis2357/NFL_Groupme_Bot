import logging
import random

from configs import Config
from helpers import sql_lib, templates


def get_teams():
    """Get a list of teams from the database."""
    result = sql_lib.execute_query("SELECT team FROM seasons;")
    teams_list = []
    for res in result:
        teams_list.append(res[0])
    return teams_list


def draft_team(user, team, season, position):
    """Enter the draft selection in the database."""
    try:
        _ = sql_lib.execute_query(f"INSERT INTO teams VALUES ({user}, {team}, {season}, {position});")
    except Exception as err:
        logging.error(f"Error adding draft selection to database - {err}")
        raise err


class Draft:
    def __init__(self, participants, draft_order=None):
        self.season = "2021"
        self.participants = participants
        self.draft_order = draft_order or self.set_draft_order()
        self.current_user = None
        self.team_count = 0
        self.snake = False

    def init_draft(self):
        self.current_user = self.set_current_drafter()

        welcome_message = templates.draft_welcome_message.format(
            self.season,
            self.draft_order[0],
            self.draft_order[1],
            self.draft_order[2],
            self.draft_order[3],
            self.draft_order[0]
        )
        return welcome_message

    def set_draft_order(self):
        """Randomly order participants for the draft."""

        rank = {}

        # Assign each participant a random decimal
        for par in self.participants:
            rank.update({par["user_id"]: random.random()})

        # Sort the decimal values in ascending order
        sorted_order = sorted([value for value in rank.values()])

        # Reorder the keys (participants) based on the order decimals
        draft_order = []
        for sor in sorted_order:
            for key, value in rank.items():
                if value == sor:
                    draft_order.append(key)

        return draft_order

    # TODO: FIX
    def set_current_drafter(self):
        return next(iter(self.draft_order))

    def make_selection(self, user, message):

        # Don't let a user draft out of turn
        if user["user_id"] != self.current_user:
            return f"You cannot select out of turn! {self.current_user} is on the clock."

        # Parse out a valid team
        selection = message.split("draft ")[1]
        teams = [team.upper() for team in get_teams()]

        if selection.upper() in teams:
            draft_team(
                self.get_username_by_id(self.current_user),
                selection.upper(),
                self.season,
                self.team_count + 1
            )

            # Send a message to the group that the pick has been made
            next_drafter = self.set_current_drafter()
            self.team_count += 1
            ack_message = templates.draft_acknowledgment.format(
                self.team_count,
                self.current_user,
                next_drafter
            )
            self.current_user = next_drafter

            # End the draft if all teams are drafted
            if self.team_count >= int(Config["num_teams"]):
                return templates.end_message

            return ack_message
        else:
            return templates.draft_failure.format(selection)

    def get_username_by_id(self, id):
        """Helper method to get name given ID."""
        for user in self.participants:
            if user["user_id"] == id:
                return user["name"]

