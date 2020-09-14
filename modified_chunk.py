jack_teams = ['Baltimore Ravens', 'Tennessee Titans', 'New York Jets', 'Miami Dolphins',
              'New England Patriots', 'Atlanta Falcons', 'San Francisco 49ers', 'Arizona Cardinals']
jordan_teams = ['Jacksonville Jaguars', 'Kansas City Chiefs', 'Las Vegas Raiders', 'Detroit Lions',
                'Minnesota Vikings', 'Chicago Bears', 'Dallas Cowboys', 'Seattle Seahawks']
patrick_teams = ['Cincinnati Bengals', 'Cleveland Browns', 'Houston Texans', 'Denver Broncos',
                 'Green Bay Packers', 'New Orleans Saints', 'Philadelphia Eagles', 'New York Giants']
nate_teams = ['Pittsburgh Steelers', 'Indianapolis Colts', 'Buffalo Bills', 'Los Angeles Chargers',
              'Carolina Panthers', 'Tampa Bay Buccaneers', 'Washington Football Team', 'Los Angeles Rams']
all_teams = jack_teams + jordan_teams + patrick_teams + nate_teams

name_team = pd.DataFrame(columns = ['Name', 'Team'])
name_team['Team'] = all_teams
for team_list, name in zip([jack_teams, jordan_teams, nate_teams, patrick_teams], ['Jack', 'Jordan', 'Nathan', 'Patrick']):
    name_team.loc[name_team['Team'].isin(team_list), 'Name'] = name

r = requests.get("https://www.espn.com/nfl/standings")
tree = html.fromstring(r.content)

nfl_results_df = pd.DataFrame(0, index=range(32), columns=['Team', 'Wins', 'Losses', 'Ties'])
base_xpath = '//*[@id="fittPageContainer"]/div[3]/div/div[1]/section/div/section/div[2]/div/section/'

ctr = 0
# AFC Teams
for i in range(1, 21):
    cur_team_data = tree.xpath(f'{base_xpath}div[1]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
    try:
        team_name = cur_team_data[0].text_content()
    except:
        continue
    cur_team_wins = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
    cur_team_loss = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
    cur_team_tie = tree.xpath(f'{base_xpath}div[1]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

    wins = int(cur_team_wins[0].text_content())
    losses = int(cur_team_loss[0].text_content())
    ties = int(cur_team_tie[0].text_content())
    nfl_results_df.iloc[ctr, :] = team_name, wins, losses, ties
    ctr += 1
    
# NFC Teams
for i in range(1, 21):
    cur_team_data = tree.xpath(f'{base_xpath}div[2]/div/div[2]/table/tbody/tr[{i}]/td/div/span[3]/a')
    try:
        team_name = cur_team_data[0].text_content()
    except:
        continue
    cur_team_wins = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[1]/span')
    cur_team_loss = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[2]/span')
    cur_team_tie = tree.xpath(f'{base_xpath}div[2]/div/div[2]/div/div[2]/table/tbody/tr[{i}]/td[3]/span')

    wins = int(cur_team_wins[0].text_content())
    losses = int(cur_team_loss[0].text_content())
    ties = int(cur_team_tie[0].text_content())
    nfl_results_df.iloc[ctr, :] = team_name, wins, losses, ties
    ctr += 1

standings = name_team.merge(nfl_results_df, how = 'left', on = 'Team')

standings.groupby('Name').sum()  # Total standings
standings.loc[standings['Name'] == 'Jordan', :]  # Individual results
pd.pivot_table(standings, index = ['Name', 'Team'])  # Total standings, team level