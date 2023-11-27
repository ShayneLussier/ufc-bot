import json
from selenium.webdriver.common.by import By
import math
import copy
import time
import unidecode


def save_data(fighterDict):
    # Load existing data from the file, if any
    existing_data = []
    try:
        with open("fighter_data.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        pass

    # Append new data to the existing list of dictionaries
    existing_data.extend(fighterDict)

    # Write the updated data back to the file
    with open("fighter_data.json", "w") as file:
        json.dump(existing_data, file, indent=4)


def collect_names(Driver, WeightClassName, WeightClassCode):
    athlete_names = {
        "flyweight": [],
        "bantamweight": [],
        "featherweight": [],
        "lightweight": [],
        "welterweight": [],
        "middleweight": [],
        "light heavyweight": [],
        "heavyweight": [],
        "women's strawweight": [],
        "women's flyweight": [],
        "women's bantamweight": [],
        "women's featherweight": [],
    }

    Driver.get(
        f"https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&filters%5B1%5D=weight_class%{WeightClassCode}"
    )
    time.sleep(2)

    #  checks how many extra pages of athletes
    athlete_count = int(
        Driver.find_element(By.CLASS_NAME, "althelete-total").text.split()[0]
    )
    extra_athletes = athlete_count - 11
    load_more_athletes = math.ceil(extra_athletes / 11)

    web_names = Driver.find_elements(
        By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
    )
    for name in web_names:
        athlete_names[WeightClassName].append(
            unidecode(
                name.text.lower().replace(" ", "-").replace("'", "").replace(".", "")
            )
        )

    # visits remaining pages if nedded
    if load_more_athletes > 0:
        for n in range(load_more_athletes):
            Driver.get(
                f"https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&filters%5B1%5D=weight_class%{WeightClassCode}&page={n+1}"
            )
            time.sleep(2)

            # find remaining names
            remaining_names = Driver.find_elements(
                By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
            )
            for name in remaining_names:
                athlete_names[WeightClassName].append(
                    unidecode(
                        name.text.lower()
                        .replace(" ", "-")
                        .replace("'", "")
                        .replace(".", "")
                    )
                )
    return athlete_names, athlete_count


def collect_rank(Driver, RankingsList):
    title_holder_found = False  # Flag to check if "Title Holder" is found

    try:
        rankings = Driver.find_elements(By.CLASS_NAME, "hero-profile__tag")

        for rank in rankings:
            if "Title Holder" in rank.text:
                RankingsList.append(0)
                title_holder_found = True
                break

        if not title_holder_found:  # If "Title Holder" wasn't found, check for #
            for rank in rankings:
                if "#" in rank.text:
                    ranking = int(rank.text.split()[0][1:])
                    RankingsList.append(ranking)
                    break
            else:  # If neither "Title Holder" nor "#" was found
                RankingsList.append(None)

    except IndexError:
        RankingsList.append(None)

    return RankingsList


def collect_is_champion(RankingList, ChampionStatusList):
    for ranking in RankingList:
        if ranking == 0:
            champion_status = True
        else:
            champion_status = False
        ChampionStatusList.append(champion_status)
    return ChampionStatusList


def collect_last_opponents(Driver, FighterName, LastOpponentsDict):
    opponent_list = []
    web_opponent = Driver.find_elements(By.CSS_SELECTOR, ".tl.Table__TD .AnchorLink")
    for opponent in web_opponent[:10]:
        opponent = opponent.get_attribute("href").split("/")[-1]
        if opponent == "ufc":
            pass
        else:
            opponent_list.append(opponent)
    LastOpponentsDict[FighterName] = opponent_list[:5]
    return LastOpponentsDict


def collect_last_5_record(Driver, FighterName, LastFightsDict):
    fight_results = []
    web_last_5_result = Driver.find_elements(By.CSS_SELECTOR, ".Table__TD .ResultCell")
    for record in web_last_5_result:
        fight_results.append(record.text.lower())

    last_5_record_dict = {"wins": 0, "loss": 0, "other": 0}
    for result in fight_results[:5]:
        if result == "w":
            last_5_record_dict["wins"] += 1
        elif result == "l":
            last_5_record_dict["loss"] += 1
        elif result == "d":
            last_5_record_dict["other"] += 1
    LastFightsDict[FighterName] = copy.deepcopy(last_5_record_dict)
    return LastFightsDict, fight_results


def collect_win_streak(FightResults, WinStreakList):
    win_streak = 0
    for result in FightResults:
        if result == "w":
            win_streak += 1
        else:
            break
    WinStreakList.append(win_streak)
    return WinStreakList


def collect_last_fight_outcome(FightResults, FightOutcomeList):
    if FightResults == []:
        FightOutcomeList.append("not found")
    else:
        last_fight_outcome = FightResults[0]
        if last_fight_outcome == "w":
            FightOutcomeList.append("win")
        elif last_fight_outcome == "l":
            FightOutcomeList.append("loss")
        else:
            FightOutcomeList.append("other")
    return FightOutcomeList
