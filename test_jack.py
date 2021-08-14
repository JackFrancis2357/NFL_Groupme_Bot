# test = ['BAL', 'TEN', 'NYJ', 'MIA', 'NE', 'ATL', 'SF', 'ARI']
# print('ARI' in test)
#
# import pandas as pd
#
# weekly_matchups_df = pd.DataFrame(index=['jack', 'jordan', 'patrick', 'nathan'],
#                                   columns=['jack', 'jordan', 'patrick', 'nathan'])
# print(weekly_matchups_df.columns.tolist())
#
# test = [x.capitalize() for x in weekly_matchups_df.columns.tolist()]
# test.insert(0, 'Table')
# print(test)

# import configs
#
# def get_teams():
#     jack_teams = configs.base_configs['Jack']
#     jordan_teams = configs.base_configs['Jordan']
#     nathan_teams = configs.base_configs['Nathan']
#     patrick_teams = configs.base_configs['Patrick']
#
#     return jack_teams, jordan_teams, nathan_teams, patrick_teams
#
# test = get_teams()
# print(test)

from groupme_bot_functions import get_standings, get_standings_message

#import pandas as pd
# test = pd.read_csv('test_standings.csv', index_col=0)
#
# test = test.drop(['Team'], axis=1)
# test = test.groupby(by='Name').sum().reset_index()
# print(test.columns.tolist())
# standings_docs = []
# for i in range(test.shape[0]):
#     doc = {
#         'Name': test.iloc[i, 0],
#         'Wins': test.iloc[i, 1],
#         'Losses': test.iloc[i, 2],
#         'Ties': test.iloc[i, 3]
#
#     }
#     print(doc)
# for i in range(test.shape[0]):
#     print(test.iloc[i, 1])

import datetime
import numpy as np

from datetime import date

today = datetime.datetime.today()
print("Today's date:", today)

datetime_object = datetime.datetime.strptime('09/07/2021', '%m/%d/%Y')
test = datetime.datetime.strptime('09/28/2021', '%m/%d/%Y')
delta = test - datetime_object
print(int(np.floor(delta.days / 7) + 1))
