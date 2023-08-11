import hydra
import requests
import pickle
import pandas as pd
from omegaconf import DictConfig


@hydra.main(config_path="../config", config_name="main", version_base=None)
def collect_data(config: DictConfig):
    """Function to collect the data"""
    collect_fpl_data(config)
    collect_fbref_team(config)
    collect_fbref_player(config)
    collect_fbref_scout(config)
    get_historic_fpl(config)


def collect_fpl_data(config: DictConfig):
    print(f"Collecting data from FPL site")
    with requests.Session() as s:
        r = s.get(url=config.collect.fpl_url)
        json = r.json()

    player_df = pd.DataFrame(json["elements"])
    team_df = pd.DataFrame(json["teams"])
    pos_df = pd.DataFrame(json["element_types"])

    player_df.to_csv(f"../data/raw/fpl_player_{config.year}.csv")
    team_df.to_csv(f"../data/raw/fpl_team_{config.year}.csv")
    pos_df.to_csv(f"../data/raw/fpl_pos_{config.year}.csv")

    print(f"Collected data from FPL site")


def collect_fbref_player(config: DictConfig):
    """Function to pull data from FBRef.com"""


def collect_fbref_scout(config: DictConfig):
    """Function to collect scouting data from FBRef"""


def get_historic_fpl(config: DictConfig):
    """
    Reads historic FPL from vaastav records hosted on github
    """
    url = (
        config.collect.fpl_hist
        + str(config.collect.year - 1)
        + "-"
        + str(config.collect.year - 2000)
        + "/cleaned_players.csv"
    )
    return_df = pd.read_csv(url)
    return_df.to_csv("../data/raw/historic_fpl.csv")


def collect_fbref_team(config: DictConfig):
    raw_data = pd.read_html(
        f"https://fbref.com/en/comps/9/{config.year-1}-{config.year}/{config.year}-{config.year}-Premier-League-Stats/"
    )
    overall = raw_data[0]
    home_away = raw_data[1]

    squad = raw_data[2::2]
    opponent = raw_data[3::2]

    overall.to_csv(f"../data/raw/overall_{config.year}.csv")
    home_away.to_csv(f"../data/raw/home_away_{config.year}.csv")d

    with open(f"../data/raw/squad_{config.year}.pickle", "wb") as f:
        pickle.dump(squad, f)

    with open(f"../data/raw/opponent_{config.year}.pickle", "wb") as f:
        pickle.dump(opponent, f)


if __name__ == "__main__":
    collect_data()
