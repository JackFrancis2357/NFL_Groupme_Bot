test = ['BAL', 'TEN', 'NYJ', 'MIA', 'NE', 'ATL', 'SF', 'ARI']
print('ARI' in test)

import pandas as pd

weekly_matchups_df = pd.DataFrame(index=['jack', 'jordan', 'patrick', 'nathan'],
                                  columns=['jack', 'jordan', 'patrick', 'nathan'])
print(weekly_matchups_df.columns.tolist())

test = [x.capitalize() for x in weekly_matchups_df.columns.tolist()]
test.insert(0, 'Table')
print(test)