import json
from selenium.webdriver.common.by import By
from math import ceil
from copy import deepcopy
from time import sleep
from unidecode import unidecode


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


def collect_names(Driver, WeightClassName, WeightClassCode, NamesDict):
    Driver.get(
        f"https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&filters%5B1%5D=weight_class%{WeightClassCode}"
    )
    sleep(5)

    #  checks how many extra pages of athletes
    athlete_count = int(
        Driver.find_element(By.CLASS_NAME, "althelete-total").text.split()[0]
    )
    extra_athletes = athlete_count - 11
    load_more_athletes = ceil(extra_athletes / 11)

    web_names = Driver.find_elements(
        By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
    )
    for name in web_names:
        NamesDict[WeightClassName].append(
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
            sleep(2)

            # find remaining names
            remaining_names = Driver.find_elements(
                By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
            )
            for name in remaining_names:
                NamesDict[WeightClassName].append(
                    unidecode(
                        name.text.lower()
                        .replace(" ", "-")
                        .replace("'", "")
                        .replace(".", "")
                    )
                )
    return NamesDict, athlete_count


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
    if RankingList[-1] == 0:
        ChampionStatusList.append(True)
    else:
        ChampionStatusList.append(False)
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


def collect_record(Driver, FighterName, RecordDict):
    record = Driver.find_element(By.CLASS_NAME, "hero-profile__division-body")
    wins = record.text.split("-")[0]
    losses = record.text.split("-")[1]
    fighter_record = {"win": wins, "loss": losses}
    print(fighter_record)
    RecordDict[FighterName] = fighter_record
    return RecordDict


def collect_win_streak(Driver, WinStreakList):
    fight_results = []
    web_last_5_result = Driver.find_elements(By.CSS_SELECTOR, ".Table__TD .ResultCell")
    for record in web_last_5_result:
        fight_results.append(record.text.lower())

    win_streak = 0
    for result in fight_results:
        if result == "w":
            win_streak += 1
        else:
            break
    WinStreakList.append(win_streak)
    return WinStreakList, fight_results


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


def collect_country(Driver, CountryList):
    country = Driver.find_element(By.CSS_SELECTOR, ".Image.Logo.Logo__sm")
    CountryList.append(country.get_attribute("title"))
    return CountryList


def collect_espn_id(Driver, IdList):
    espn_url = Driver.current_url.split("/")
    IdList.append(espn_url[-2])
    return IdList
