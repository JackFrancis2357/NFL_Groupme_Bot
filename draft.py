import random

from helpers import templates


class Draft:
    def __init__(self, participants, draft_order=None):
        self.season = "2021"
        self.participants = participants
        self.draft_order = draft_order or self.set_draft_order()
        self.current_user = None
        self.team_count = 0

    def init_draft(self):
        self.current_user = self.draft_order[0]

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
            rank.update(
                {
                    par: random.random()
                }
            )

        # Sort the decimal values in ascending order
        sorted_order = sorted([value for value in rank.values()])

        # Reorder the keys (participants) based on the order decimals
        draft_order = []
        for sor in sorted_order:
            for key, value in rank.items():
                if value == sor:
                    draft_order.append(key)

        return draft_order
