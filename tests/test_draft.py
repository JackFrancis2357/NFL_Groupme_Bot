import os
import json

# Needs to run before Draft import
os.chdir("/Users/Patrick/PycharmProjects/git-nfl-groupme-bot/NFL_Groupme_Bot")

from draft import Draft

with open("tests/users.json", "r") as json_file:
    users = json.load(json_file)

draft_instance = Draft(users)
print(draft_instance.init_draft())

# Get current user
current_user = None
for user in users:
    if user["user_id"] == draft_instance.current_user:
        current_user = user
        break

print(draft_instance.make_selection(current_user, "draft Kansas City Chiefs"))
