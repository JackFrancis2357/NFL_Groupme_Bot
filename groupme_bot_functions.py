import logging
import os
import requests
import pandas as pd
from lxml import html
from app_helper_functions import get_teams, get_start_final_date
import configs


def send_message(msg):
    url = "https://api.groupme.com/v3/bots/post"
    payload = {"bot_id": os.getenv("GROUPME_BOT_ID"), "text": msg}
    try:
        response = requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        logging.error(e)
    return response.status_code


def return_contestant(name, standings):
    if name == "All":
        teams = standings.loc[:, "Team"].tolist()
        wins = [int(i) for i in standings.loc[:, "Wins"].tolist()]
        losses = [int(i) for i in standings.loc[:, "Losses"].tolist()]
        message = str()
        for i in range(0, len(teams)):
            message += teams[i] + ": " + str(wins[i]) + "-" + str(losses[i]) + "\n"

        return send_message(message)
    else:
        teams = standings.loc[standings["Name"] == name, "Team"].tolist()
        wins = [int(i) for i in standings.loc[standings["Name"] == name, "Wins"].tolist()]
        losses = [int(i) for i in standings.loc[standings["Name"] == name, "Losses"].tolist()]
        message = str()
        for i in range(0, len(teams)):
            message += teams[i] + ": " + str(wins[i]) + "-" + str(losses[i]) + "\n"

        return send_message(message)


def get_standings_message(standings):
    names = standings["Name"].unique().tolist()
    logging.info(f"Names to be sorted for standings message: {names}")
    names.sort()
    wins = [int(i) for i in standings.groupby("Name").sum().reset_index()["Wins"].tolist()]
    losses = [int(i) for i in standings.groupby("Name").sum().reset_index()["Losses"].tolist()]
    ties = [int(i) for i in standings.groupby("Name").sum().reset_index()["Ties"].tolist()]
    message = str()
    for i in range(0, len(names)):
        message += names[i] + ": " + str(wins[i]) + "-" + str(losses[i]) + "-" + str(ties[i]) + "\n"
    return message


def get_standings(current_week):
    start_date, final_date = get_start_final_date(current_week)
    standings = pd.DataFrame(0, index=range(32), columns=["Team", "Wins", "Losses", "Ties"])
    espn_score_data = requests.get(
        f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={start_date}-{final_date}"
    ).json()
    ctr = 0
    for event in espn_score_data["events"]:
        for competition in event["competitions"]:
            for competitor in competition["competitors"]:
                record = competitor["records"][0]["summary"]
                full_name = competitor["team"]["displayName"]
                record_split = record.split("-")
                wins = record_split[0]
                losses = record_split[1]
                try:
                    ties = record_split[2]
                except IndexError:
                    ties = 0
                standings.iloc[ctr, :] = full_name, wins, losses, ties
                ctr += 1
    # Get teams and their owners and remove `all` key to prevent all teams matching in team-name mask below
    teams = get_teams()
    teams.pop("all")

    for owner, tm in teams.items():
        standings.loc[standings["Team"].isin(tm), "Name"] = owner
    standings[["Wins", "Losses", "Ties"]] = standings[["Wins", "Losses", "Ties"]].apply(pd.to_numeric)
    return standings


def get_schedule(team_id, starting_week, finishing_week=18):
    for k, v in configs.team_mapping_configs.items():
        if team_id in k:
            team_abbreviation = v[0]

    nfl_schedule_df = pd.read_csv("./2023_NFL_Schedule_Grid.csv")
    try:
        schedule = nfl_schedule_df.loc[nfl_schedule_df["Team"] == team_abbreviation]
    except:
        return ""

    schedule_columns = schedule.columns.tolist()[starting_week:finishing_week]
    opponents = [x for x in schedule.iloc[0, starting_week:finishing_week]]

    message = ""
    for col, opp in zip(schedule_columns, opponents):
        message += col + ": " + opp + "\n"

    return send_message(message)
