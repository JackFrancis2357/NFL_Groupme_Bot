import pandas as pd
from app_helper_functions import get_team_abb, get_team_owner, get_start_final_date
from groupme_bot_functions import get_standings
import datetime
import requests

from configs import Config


def get_homepage_data(current_week):
    default_name_ordering = ["Jack", "Jordan", "Nathan", "Patrick"]
    matchups_df = pd.read_csv(Config["BASE_CONFIG"]["weekly_matchups_filepath"])
    current_matchups = matchups_df[f"Wk_{current_week}_Matchups"]
    current_matchups = current_matchups[current_matchups != "0"]
    away_home_teams = current_matchups.str.split(pat="at", expand=True)
    away_home_teams.columns = ["Away", "Home"]
    away_home_teams["Away"] = away_home_teams["Away"].map(lambda x: x.rstrip())
    away_home_teams["Home"] = away_home_teams["Home"].map(lambda x: x.lstrip())

    ja_t, jo_t, na_t, pa_t = get_team_abb()
    weekly_matchups_df = pd.DataFrame(0, index=default_name_ordering, columns=default_name_ordering)
    current_week_record_df = pd.DataFrame(0, index=default_name_ordering, columns=["Wins", "Losses", "Ties"])

    start_date, final_date = get_start_final_date(current_week)

    score_dict = get_current_scores(start_date, final_date)

    matchups_columns = ["Away", "Home", "Status"]
    matchups = []
    matchups_two = []
    for i in range(away_home_teams.shape[0]):
        away_team = away_home_teams["Away"][i]
        away_score = score_dict[away_team][0]
        home_team = away_home_teams["Home"][i]
        home_score = score_dict[home_team][0]
        home_status = score_dict[home_team][1]
        away_owner, away_color = get_team_owner(str(away_team), ja_t, jo_t, na_t, pa_t)
        home_owner, home_color = get_team_owner(str(home_team), ja_t, jo_t, na_t, pa_t)

        doc = {
            "Away": away_team,
            "Away_Score": away_score,
            "Away_Owner": away_color,
            "Home": home_team,
            "Home_Score": home_score,
            "Home_Owner": home_color,
            "Status": home_status,
        }
        if i < 8:
            matchups.append(doc)
        else:
            matchups_two.append(doc)

        weekly_matchups_df.loc[away_owner, home_owner] += 1
        weekly_matchups_df.loc[home_owner, away_owner] += 1

        if int(home_score) == int(away_score):
            current_week_record_df.loc[home_owner, "Ties"] += 1
            current_week_record_df.loc[away_owner, "Ties"] += 1

        elif int(home_score) > int(away_score):
            current_week_record_df.loc[home_owner, "Wins"] += 1
            current_week_record_df.loc[away_owner, "Losses"] += 1

        elif int(away_score) > int(home_score):
            current_week_record_df.loc[home_owner, "Losses"] += 1
            current_week_record_df.loc[away_owner, "Wins"] += 1

    owner_matchups = []
    for i in range(weekly_matchups_df.shape[0]):
        weekly_matchups_df.iloc[i, i] /= 2
        owner_name = weekly_matchups_df.columns[i].capitalize()
        doc = {
            "owner": owner_name,
            "owner_color": Config["USERS"][owner_name]["hexcolor"],
            "Jack": weekly_matchups_df.iloc[i, 0],
            "Jordan": weekly_matchups_df.iloc[i, 1],
            "Nathan": weekly_matchups_df.iloc[i, 2],
            "Patrick": weekly_matchups_df.iloc[i, 3],
        }
        owner_matchups.append(doc)

    owner_matchups_columns = [x for x in weekly_matchups_df.columns.tolist()]
    owner_matchups_columns.insert(0, "Table")

    return matchups, matchups_columns, matchups_two, owner_matchups, owner_matchups_columns, current_week_record_df


def get_homepage_standings(current_week_record_df, current_week):
    standings = get_standings(current_week)
    standings = standings.drop(["Team"], axis=1)
    standings = standings.groupby(by="Name").sum().reset_index()
    standings_columns = standings.columns.tolist()
    standings_columns.append("Week")
    standings_docs = []
    for i in range(standings.shape[0]):
        current_record = (
            str(current_week_record_df.iloc[i, 0])
            + "-"
            + str(current_week_record_df.iloc[i, 1])
            + "-"
            + str(current_week_record_df.iloc[i, 2])
        )
        owner_name = standings.iloc[i, 0]
        doc = {
            "owner": owner_name,
            "owner_color": Config["USERS"][owner_name]["hexcolor"],
            "wins": standings.iloc[i, 1],
            "losses": standings.iloc[i, 2],
            "ties": standings.iloc[i, 3],
            "current_record": current_record,
        }
        standings_docs.append(doc)
    return standings_docs, standings_columns


def get_current_scores(start_date, final_date):
    score_dict = {}
    espn_score_data = requests.get(
        f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={start_date}-{final_date}"
    ).json()
    for event in espn_score_data["events"]:
        for competition in event["competitions"]:
            try:
                d_and_d = competition["situation"]["downDistanceText"]
            except KeyError:
                d_and_d = ""
            status_detail = competition["status"]["type"]["shortDetail"]
            if d_and_d == "":
                status = status_detail
            else:
                status = status_detail
            for competitor in competition["competitors"]:
                if competitor["team"]["abbreviation"] == "JAX":
                    score_dict["JAC"] = competitor["score"], status
                elif competitor["team"]["abbreviation"] == "WSH":
                    score_dict["WAS"] = competitor["score"], status
                else:
                    score_dict[competitor["team"]["abbreviation"]] = competitor["score"], status

    return score_dict
