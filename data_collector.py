# ------------------------- IMPORTS -------------------------- #
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from schema import Fighter
from ufc_functions import (
    collect_last_5_record,
    collect_win_streak,
    save_data,
    collect_names,
    collect_rank,
    collect_is_champion,
    collect_last_opponents,
    collect_last_fight_outcome,
)

# ------------------------- CONSTANTS -------------------------- #
WEIGHT_CLASSES = {
    "flyweight": "3A10",
    "bantamweight": "3A8",
    "featherweight": "3A9",
    "lightweight": "3A12",
    "welterweight": "3A15",
    "middleweight": "3A14",
    "light heavyweight": "3A13",
    "heavyweight": "3A11",
    "women's strawweight": "3A16",
    "women's flyweight": "3A38",
    "women's bantamweight": "3A37",
    "women's featherweight": "3A39",
}

# ------------------------- SELENIUM SETUP -------------------------- #
# keep browser open
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

# ------------------------- DATA COLLECTION -------------------------- #
for weight_class_name, weight_class_code in WEIGHT_CLASSES.items():
    # initialize data structures for functions
    athlete_rankings = []
    athlete_champion = []
    athlete_last_opponents = {}
    athlete_last_5_record = {}
    athlete_win_streak = []
    athlete_last_fight_outcome = []

    # collect names
    athlete_names, athlete_count = collect_names(
        Driver=driver,
        WeightClassName=weight_class_name,
        WeightClassCode=weight_class_code,
    )

    # visit fighter page
    for weight_class_name, names in athlete_names.items():
        # collect data from ufc.com
        for name in names:
            driver.get(f"https://www.ufc.com/athlete/{name}")

            # collect rank
            athlete_rankings = collect_rank(
                Driver=driver, RankingsList=athlete_rankings
            )
            print(athlete_rankings)

        # collect championship status
        athlete_champion = collect_is_champion(
            RankingList=athlete_rankings, ChampionStatusList=athlete_champion
        )
        print(athlete_champion)
        # retrive remaining data from espn.com
        for name in names:
            driver.get(f"https://www.espn.com/search/_/q/{name}")
            time.sleep(2)
            athlete_link = driver.find_elements(
                By.CSS_SELECTOR, ".LogoTile__Meta.LogoTile__Meta--category"
            )
            for sport in athlete_link:
                if sport.text == "MMA":
                    sport.click()
                    fighter_found = True
                    break

            # if fighter data isn't found, enter these default value and skip the rest of the data colelction loop
            if not fighter_found:
                athlete_rankings.append(None)
                athlete_champion.append(False)
                athlete_last_opponents[name] = []
                athlete_last_5_record[name] = {"wins": 0, "loss": 0, "other": 0}
                athlete_win_streak.append(0)
                athlete_last_fight_outcome.append("not found")
                continue

            time.sleep(2)
            fight_record_link = driver.find_element(
                By.CLASS_NAME, "Card__Header__SubLink__Text"
            )
            fight_record_link.click()

            # collect last 5 opponents
            athlete_last_opponents = collect_last_opponents(
                Driver=driver,
                FighterName=name,
                LastOpponentsDict=athlete_last_opponents,
            )
            print(athlete_last_opponents)
            # collect last 5 fight record
            athlete_last_5_record, fight_results = collect_last_5_record(
                Driver=driver, FighterName=name, LastFightsDict=athlete_last_5_record
            )
            print(athlete_last_5_record)
            # collect win streak
            athlete_win_streak = collect_win_streak(
                FightResults=fight_results, WinStreakList=athlete_win_streak
            )
            print(athlete_win_streak)
            # collect last fight outcome
            athlete_last_fight_outcome = collect_last_fight_outcome(
                FightResults=fight_results, FightOutcomeList=athlete_last_fight_outcome
            )
            print(athlete_last_fight_outcome)
        # save data to json file only if all athletes have been captured
        if len(athlete_names[weight_class_name]) == athlete_count:
            for i in range(athlete_count):
                fighter_dict = Fighter(
                    name=athlete_names[weight_class_name][i],
                    weight_class=weight_class_name,
                    rank=athlete_rankings[i],
                    champion=athlete_champion[i],
                    win_streak=athlete_win_streak[i],
                    last_fight_outcome=athlete_last_fight_outcome[i],
                    last_5_fight_record=athlete_last_5_record[names[i]],
                    last_5_opponents=athlete_last_opponents[names[i]],
                ).to_dict()
                save_data(fighter_dict)

# driver.quit()
