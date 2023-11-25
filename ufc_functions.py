import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import math


def save_data(fighterDict):
    # Load existing data from the file, if any
    existing_data = []
    try:
        with open("fighter_data.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        pass

    # Append new data to the existing list of dictionaries
    existing_data.extend(fighterDict)

    # Write the updated data back to the file
    with open("fighter_data.json", "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)


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
            remaining_names = Driver.find_elements(
                By.CSS_SELECTOR, ".c-listing-athlete__text .c-listing-athlete__name"
            )
            for name in remaining_names:
                athlete_names[WeightClassName].append(
                    name.text.lower().replace(" ", "-").replace("'", "")
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
