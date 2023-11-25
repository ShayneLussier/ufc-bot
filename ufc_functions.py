import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import math


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

    #  checks how many extra pages of athletes
    athlete_count = int(
        Driver.find_element(By.CLASS_NAME, "althelete-total").text.split()[0]
    )
    extra_athletes = athlete_count - 11
    load_more_athletes = math.ceil(extra_athletes / 11)

    #  checks how many extra pages of athletes
    athlete_count_rest = int(
        Driver.find_element(By.CLASS_NAME, "althelete-total").text.split()[0]
    )
    extra_athletes = athlete_count_rest - 11
    load_more_athletes = math.ceil(extra_athletes / 11)

    web_names = Driver.find_elements(
        By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
    )
    for name in web_names:
        athlete_names[WeightClassName].append(name.text.lower().replace(" ", "-"))

    # visits remaining pages if nedded
    if load_more_athletes > 0:
        for n in range(load_more_athletes):
            Driver.get(
                f"https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&filters%5B1%5D=weight_class%{WeightClassCode}&page={n+1}"
            )

            # find remaining names
            reamining_names = Driver.find_elements(
                By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
            )
            for name in reamining_names:
                athlete_names[WeightClassName].append(
                    name.text.lower().replace(" ", "-")
                )
    return athlete_names, athlete_count


def collect_rank(Driver, RankingsList):
    try:
        ranking = Driver.find_element(By.CLASS_NAME, "hero-profile__tag").text.split()[
            0
        ]  # rank number
        if "#" not in ranking:
            ranking = Driver.find_elements(
                By.CLASS_NAME, "hero-profile__tag"
            )  # title holder
        if "Title Holder" in ranking[3].text:
            ranking = 0
    except:
        ranking = None
    finally:
        RankingsList.append(ranking)
    return RankingsList


def collect_champion_status(RankingList, ChampionStatusList):
    for ranking in RankingList:
        if ranking == 0:
            champion_status = True
            ChampionStatusList.append(champion_status)
        else:
            champion_status = False
            ChampionStatusList.append(champion_status)
    return ChampionStatusList
