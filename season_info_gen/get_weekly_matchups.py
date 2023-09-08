import pandas as pd

# You should only run this file once
# Go to: https://www.espn.com/nfl/schedulegrid and copy/paste the table into an Excel sheet
# Make the following changes
# Update the column headers from 1, 2, 3 ... 18 to Wk 1, Wk 2, Wk 3, ... Wk 18
# Update "WSH" to "WAS"
# Update "JAX" to "JAC"

df = pd.read_csv("../NFL_Schedule_Data/2023_NFL_Schedule_Grid.csv")

# Need to create a csv with "team 1 at team 2" for each week of season
for j in range(1, 19):
    df[f"Wk_{j}_Matchups"] = 0
    ctr = 0
    for i in range(df.shape[0]):
        if "at" in df[f"Wk {j}"][i]:
            df[f"Wk_{j}_Matchups"][ctr] = df["Team"][i] + " " + df[f"Wk {j}"][i]
            ctr += 1

test_df = df.iloc[:16, -18:]
test_df.to_csv("../NFL_Schedule_Data/2023_weekly_matchups.csv")
