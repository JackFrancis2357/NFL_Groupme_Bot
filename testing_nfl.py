import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import html

r = requests.get("https://www.pro-football-reference.com/years/2020/")
tree = html.fromstring(r.content)

nfl_results_df = pd.DataFrame(0, index=range(32), columns=['Team Name', 'Wins', 'Losses'])

ctr = 0
for i in range(1, 21):
    cur_team_data = tree.xpath(f'//*[@id="AFC"]/tbody/tr[{i}]/td')
    team_data = [td.text_content().strip() for td in cur_team_data]
    if team_data[0][:3] == 'AFC' or team_data[0][:3] == 'NFC':
        continue
    cur_team_wins, cur_team_loss = team_data[0], team_data[1]
    current_team = tree.xpath(f'//*[@id="AFC"]/tbody/tr[{i}]/th')
    team_name = [td.text_content().strip() for td in current_team]
    nfl_results_df.iloc[ctr, :] = team_name[0], cur_team_wins, cur_team_loss
    ctr += 1

    # NFC
    cur_team_data = tree.xpath(f'//*[@id="NFC"]/tbody/tr[{i}]/td')
    team_data = [td.text_content().strip() for td in cur_team_data]
    if team_data[0][:3] == 'AFC' or team_data[0][:3] == 'NFC':
        continue
    cur_team_wins, cur_team_loss = team_data[0], team_data[1]
    current_team = tree.xpath(f'//*[@id="NFC"]/tbody/tr[{i}]/th')
    team_name = [td.text_content().strip() for td in current_team]
    nfl_results_df.iloc[ctr, :] = team_name[0], cur_team_wins, cur_team_loss
    ctr += 1

jack_teams = ['Baltimore Ravens', 'Tennessee Titans', 'New York Jets', 'Miami Dolphins',
              'New England Patriots', 'Atlanta Falcons', 'San Francisco 49ers', 'Arizona Cardinals']
jordan_teams = ['Jacksonville Jaguars', 'Kansas City Chiefs', 'Las Vegas Raiders', 'Detroit Lions',
                'Minnesota Vikings', 'Chicago Bears', 'Dallas Cowboys', 'Seattle Seahawks']
patrick_teams = ['Cincinnati Bengals', 'Cleveland Browns', 'Houston Texans', 'Denver Broncos',
                 'Green Bay Packers', 'New Orleans Saints', 'Philadelphia Eagles', 'New York Giants']
nate_teams = ['Pittsburgh Steelers', 'Indianapolis Colts', 'Buffalo Bills', 'Los Angeles Chargers',
              'Carolina Panthers', 'Tampa Bay Buccaneers', 'Washington Football Team', 'Los Angeles Rams']

list_of_teams = [jack_teams, jordan_teams, patrick_teams, nate_teams]
list_of_records = []

for team in list_of_teams:
    current_wins = 0
    current_losses = 0
    for i in range(8):
        current_wins += int(nfl_results_df['Wins'][nfl_results_df['Team Name'] == team[i]])
        current_losses += int(nfl_results_df['Losses'][nfl_results_df['Team Name'] == team[i]])
    list_of_records.append(current_wins)
    list_of_records.append(current_losses)

print(f'Jack: {list_of_records[0]}-{list_of_records[1]}')
print(f'Jordan: {list_of_records[2]}-{list_of_records[3]}')
print(f'Patrick: {list_of_records[4]}-{list_of_records[5]}')
print(f'Nathan: {list_of_records[6]}-{list_of_records[7]}')

