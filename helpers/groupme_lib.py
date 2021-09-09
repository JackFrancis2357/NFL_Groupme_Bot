import json
import os
import requests

from configs import Config


def get_users(group_id=Config["group_id"], ids_only=False):
    """Get users for a specified group - default of Buttered Toast."""
    users_json = requests.get(
        f"https://api.groupme.com/v3/groups/{group_id}?token={os.getenv('TOKEN')}"
    ).json()["response"]["members"]

    if ids_only:
        ids = []
        for member in users_json:
            ids.append(member["user_id"])
        return ids

    return users_json


def get_groups(group=None):
    """Get groups for authorized user - or a specified group."""
    request_url = "https://api.groupme.com/v3/groups"

    if group:
        request_url += f"/{group}"

    return requests.get(
        f"{request_url} + ?token={os.getenv('TOKEN_DEV')}"
    )
