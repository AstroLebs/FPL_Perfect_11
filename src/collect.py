import hydra
import requests
import pandas as pd
from omegaconf import DictConfig



@hydra.main(config_path="../config", config_name="main", version_base=None)
def collect_data(config: DictConfig):
    """Function to collect the data"""
    collect_fpl_data()
    collect_fbref_player()
    get_historic_fpl()
    get_fbref_team()


@hydra.main(config_path="../config", config_name="main", version_base=None)
def collect_fpl_data(config: DictConfig) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    print(f"Collecting data from FPL site")
    with requests.Session() as s:
        r = s.get(url=config.collect.fpl_url)
        json = r.json()

    player_df = pd.DataFrame(json["elements"])
    team_df = pd.DataFrame(json["teams"])
    pos_df = pd.DataFrame(json["element_types"])

    player_df.to_csv("../data/raw/fpl_player.csv")
    team_df.to_csv("../data/raw/fpl_team.csv")
    pos_df.to_csv("../data/raw/fpl_pos.csv")

    print(f"Collected data from FPL site")
    return(player_df, team_df, pos_df)

@hydra.main(config_path="../config", config_name="main", version_base=None)
def collect_fbref_player(config: DictConfig):
    """Function to pull data from FBRef.com"""

@hydra.main(config_path="../config", config_name="main", version_base=None)
def collect_fbref_scout(config: DictConfig):
    """Function to collect scouting data from FBRef"""

@hydra.main(config_path="../config", config_name="main", version_base=None)
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

@hydra.main(config_path="../config", config_name="main", version_base=None)
def get_fbref_team(config: DictConfig) -> (pd.DataFrame, pd.DataFrame):
    """
    Returns team and vs team data
    """
    raw_data = pd.read_html(config.collect.fbref_url)

    raw_data[1].columns = raw_data[1].columns.map(lambda x: f"{x[0]}_{x[1]}")
    squad = pd.merge(
        raw_data[0],
        raw_data[1],
        left_index=True,
        right_index=True,
    )
    opponents = None

    for i, table in enumerate(raw_data[2:]):
        try:
            table.columns = table.columns.map(lambda x: f"{x[0]}_{x[1]}")
        except Exception as e:
            print(e)
            pass

        if i % 2 == 0:
            squad = pd.merge(
                squad, table, left_on="Squad",
                right_on="Unnamed: 0_level_0_Squad"
            )
        else:
            if opponents is None:
                opponents = table
                continue
            else:
                opponents = pd.merge(
                    opponents,
                    table,
                    left_on="Unnamed: 0_level_0_Squad",
                    right_on="Unnamed: 0_level_0_Squad",
                )

    squad = squad.T.drop_duplicates().T
    opponents = opponents.T.drop_duplicates().T

    return (squad, opponents)



if __name__ == "__main__":
    collect_data()
