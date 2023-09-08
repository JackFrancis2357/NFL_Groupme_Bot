import pandas as pd
import requests
from lxml import html

# from helpers.setup_logger import LOGGER
import logging

r = requests.get("https://www.espn.com/nfl/standings/_/season/2020")
tree = html.fromstring(r.content)

nfl_results_df = pd.DataFrame(0, index=range(32), columns=["Team Name", "Wins", "Losses", "Ties"])
base_xpath = '//*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/'
# //*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/div[1]/div/div[2]/div/div[2]/table/tbody/tr[1]
# //*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/div[1]/div/div[2]/div/div[2]/table/tbody/tr[2]/td[1]/span

ctr = 0

# AFC Teams
for i in range(1, 21):
    cur_team_data = tree.xpath(f"{base_xpath}div[1]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a")
    team_name = [td.text_content().strip() for td in cur_team_data]
    if not team_name:
        continue
    cur_team_wins = tree.xpath(f"{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span")
    cur_team_loss = tree.xpath(f"{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span")
    cur_team_tie = tree.xpath(f"{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span")

    wins = [td.text_content().strip() for td in cur_team_wins]
    losses = [td.text_content().strip() for td in cur_team_loss]
    ties = [td.text_content().strip() for td in cur_team_tie]
    nfl_results_df.iloc[ctr, :] = team_name[0], wins[0], losses[0], ties[0]
    ctr += 1

# NFC Teams
for i in range(1, 21):
    cur_team_data = tree.xpath(f"{base_xpath}div[2]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a")
    team_name = [td.text_content().strip() for td in cur_team_data]
    if not team_name:
        continue
    cur_team_wins = tree.xpath(f"{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span")
    cur_team_loss = tree.xpath(f"{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span")
    cur_team_tie = tree.xpath(f"{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span")

    wins = [td.text_content().strip() for td in cur_team_wins]
    losses = [td.text_content().strip() for td in cur_team_loss]
    ties = [td.text_content().strip() for td in cur_team_tie]
    nfl_results_df.iloc[ctr, :] = team_name[0], wins[0], losses[0], ties[0]
    ctr += 1

jack_teams = [
    "Baltimore Ravens",
    "Tennessee Titans",
    "New York Jets",
    "Miami Dolphins",
    "New England Patriots",
    "Atlanta Falcons",
    "San Francisco 49ers",
    "Arizona Cardinals",
]
jordan_teams = [
    "Jacksonville Jaguars",
    "Kansas City Chiefs",
    "Las Vegas Raiders",
    "Detroit Lions",
    "Minnesota Vikings",
    "Chicago Bears",
    "Dallas Cowboys",
    "Seattle Seahawks",
]
patrick_teams = [
    "Cincinnati Bengals",
    "Cleveland Browns",
    "Houston Texans",
    "Denver Broncos",
    "Green Bay Packers",
    "New Orleans Saints",
    "Philadelphia Eagles",
    "New York Giants",
]
nate_teams = [
    "Pittsburgh Steelers",
    "Indianapolis Colts",
    "Buffalo Bills",
    "Los Angeles Chargers",
    "Carolina Panthers",
    "Tampa Bay Buccaneers",
    "Washington",
    "Los Angeles Rams",
]

list_of_teams = [jack_teams, jordan_teams, patrick_teams, nate_teams]
list_of_records = []

logging.info("This is a test from the dataframe file")
# LOGGER.info("Now printing the dataframe head.")
# print(nfl_results_df.head())
