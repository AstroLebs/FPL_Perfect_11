import hydra
import requests
import pickle
import pandas as pd
from omegaconf import DictConfig
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
import re


@hydra.main(config_path="../config", config_name="main", version_base=None)
def collect_data(config: DictConfig):
    """Function to collect the data"""
    collect_fpl_data(config)
    collect_fbref_team(config)
    collect_fbref_player(config)
    # collect_fbref_scout(config)
    collect_historic_fpl(config)


def collect_fpl_data(config: DictConfig):
    print("Collecting data from FPL site...")
    with requests.Session() as s:
        r = s.get(url=config.collect.fpl_url)
        json = r.json()

    player_df = pd.DataFrame(json["elements"])
    team_df = pd.DataFrame(json["teams"])
    pos_df = pd.DataFrame(json["element_types"])

    player_df.to_csv(f"../data/raw/fpl_player_{config.collect.year}.csv")
    team_df.to_csv(f"../data/raw/fpl_team_{config.collect.year}.csv")
    pos_df.to_csv(f"../data/raw/fpl_pos_{config.collect.year}.csv")

    print("Collected data from FPL site")


def collect_fbref_player(config: DictConfig):
    """Function to pull data from FBRef.com"""
    print("Collecting FBRef.com player data")
    print("Collected FBRef.com player data")


def collect_fbref_scout(config: DictConfig, retry):
    """Function to collect scouting data from FBRef"""
    print("Collecting FBRef.com scout data")

    if retry is None:
        retry = 0
    else:
        print(f"waiting for {retry} seconds")
        sleep(retry)
    # URL for the EPL page on FBref.com
    url = "https://fbref.com/en/comps/9/wages/Premier-League-Wages"
    response = requests.get(url, headers={"User-agent": "fpl_test"})
    if response.status_code == 200:
        print("Finding Players...")
        soup = BeautifulSoup(re.sub("<!--|-->", "", str(response.content)), "lxml")
        table = soup.find("table", {"id": "player_wages"})

        player_urls = [
            a["href"] for a in table.select('tbody tr td[data-stat="player"] a')
        ]

        scouting_report = {"MF": [], "FW": [], "FB": [], "GK": [], "AM": [], "CB": []}
        request_count = 0
        for player_url in player_urls:
            full_url = "https://fbref.com" + player_url
            if request_count >= 25:
                request_count = 0
                print("Sleeping to avoid 429 status code")
                sleep(30)

            player_response = requests.get(full_url)
            if int(player_response.status_code) == 429:
                print(f"Sleeping for: {player_response.headers['Retry-After']}")
                sleep(int(player_response.headers["Retry-After"]))
                player_response = requests.get(full_url)

            request_count += 1
            if player_response.status_code == 200:
                player_soup = BeautifulSoup(player_response.content, "html.parser")

                # Add check against FPL Data
                for pos in ["MF", "FW", "FB", "GK", "AM", "CB"]:
                    scouting_table = player_soup.find(
                        "table", {"id": f"scout_summary_{pos}"}
                    )
                    if scouting_table is not None:
                        scouting_report[pos].append(
                            (
                                player_url,
                                [data.text for data in scouting_table.select("td")],
                            )
                        )
                    else:
                        scouting_report[pos].append(None)

                print(f"Success: {full_url}")
            else:
                print(
                    f"Failed to retrieve data for player: {full_url} | {player_response.status_code}"
                )

            date = datetime.now()
            file_path = f"FBREF_SCOUT_{date.strftime('%Y%m%d')}.pickle"

            # Save the object to a pickle file
            with open(file_path, "wb") as f:
                pickle.dump(scouting_report, f)

        print("Scraping completed. Scouting reports saved")
    else:
        print("Failed to retrieve data from FBref.com")
        print(response.status_code)
        print(response.headers["Retry-After"])
        print(type(response.headers["Retry-After"]))
        collect_fbref_scout(int(response.headers["Retry-After"]))
    print("Collected FBRef.com scout data")


def collect_historic_fpl(config: DictConfig):
    """
    Reads historic FPL from vaastav records hosted on github
    """
    print("Collecting historic FPL data...")
    url = (
        config.collect.fpl_hist
        + str(config.collect.year - 1)
        + "-"
        + str(config.collect.year - 2000)
        + "/cleaned_players.csv"
    )
    return_df = pd.read_csv(url)
    return_df.to_csv("../data/raw/historic_fpl.csv")
    print("Collected historic FPL data")


def collect_fbref_team(config: DictConfig):
    print("Collecting FBRef.com team data...")
    raw_data = pd.read_html(
        f"https://fbref.com/en/comps/9/{config.collect.year-1}-{config.collect.year}/{config.collect.year}-{config.collect.year}-Premier-League-Stats/"
    )
    overall = raw_data[0]
    home_away = raw_data[1]

    squad = raw_data[2::2]
    opponent = raw_data[3::2]

    overall.to_csv(f"../data/raw/overall_{config.collect.year}.csv")
    home_away.to_csv(f"../data/raw/home_away_{config.collect.year}.csv")

    with open(f"../data/raw/squad_{config.collect.year}.pickle", "wb") as f:
        pickle.dump(squad, f)

    with open(f"../data/raw/opponent_{config.collect.year}.pickle", "wb") as f:
        pickle.dump(opponent, f)

    print("Collected FBRef.com team data")


if __name__ == "__main__":
    collect_data()
