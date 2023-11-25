# ------------------------- IMPORTS -------------------------- #
from selenium import webdriver
from selenium.webdriver.common.by import By
import math
import time
from schema import Fighter
from ufc_functions import (
    save_data,
    collect_names,
    collect_rank,
    collect_champion_status,
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
    "women strawweight": "3A16",
    "women flyweight": "3A38",
    "women bantamweight": "3A37",
    "women featherweight": "3A39",
}


# ------------------------- SELENIUM SETUP -------------------------- #
# proxy needed to load website in english via usa
proxy = {
    "http": "32.223.6.94:80",
    "https": "37.19.220.131:8443",
}

# keep browser open
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Merge Chrome options and proxy options
chrome_options.add_argument(f'--proxy-server={proxy["http"]}')
chrome_options.add_argument(f'--proxy-server={proxy["https"]}')

driver = webdriver.Chrome(options=chrome_options)


# ------------------------- TESTING -------------------------- #
# fighter data
athlete_weight_class = []
athlete_win_streak = []
athlete_last_fight_outcome = []
athlete_last_5_record = {"wins": 0, "loss": 0, "other": 0}
athlete_last_opponents = []

# collect names
for weight_class_name, weight_class_code in WEIGHT_CLASSES.items():
    athlete_names, athlete_count = collect_names(
        Driver=driver,
        WeightClassName=weight_class_name,
        WeightClassCode=weight_class_code,
    )

# visit fighter page for stats
for weight_class_name, names in athlete_names.items():
    # initialize lists for functions arguments
    athlete_rankings = []
    athlete_champion = []

    for name in names:
        driver.get(f"https://www.ufc.com/athlete/{name}")

        # collect rank
        athlete_rankings = collect_rank(Driver=driver, RankingsList=athlete_rankings)

    # collect championship status
    collect_champion_status(
        RankingList=athlete_rankings, ChampionStatusList=athlete_champion
    )

    # retrive remaining data from espn
    driver.get(f"https://www.espn.com/search/_/q/{name}")
    # time.sleep() ?
    link = driver.find_element(
        By.CSS_SELECTOR, ".AnchorLink.LogoTile.flex.items-center.pl3.pr3"
    )
    link.click()

    # try block, does not mean there is up to 5 opponents
    # collect last 5 opponents
    fight_results = driver.find_elements(By.CSS_SELECTOR, ".tl.Table__TD .AnchorLink")
    for result in fight_results[:10:2]:
        opponent = result.get_attribute("href").split("/")[-1]
        athlete_last_opponents.append(opponent)

    # collect last 5 fight record
    last_5_record = []
    web_last_5_result = driver.find_elements(By.CSS_SELECTOR, ".Table__TD .ResultCell")
    for record in web_last_5_result[:5]:
        last_5_record.append(record.text.lower())

    for result in last_5_record:
        if result == "w":
            athlete_last_5_record["wins"] += 1
        elif result == "l":
            athlete_last_5_record["loss"] += 1
        elif result == "d":
            athlete_last_5_record["other"] += 1

    # collect win streak
    win_streak = 0
    for result in last_5_record:
        if result == "w":
            win_streak += 1
        else:
            break
    athlete_win_streak.append(win_streak)

    # collect last fight outcome
    last_fight_outcome = last_5_record[0]

    # create a fighter class for each fighter
    # fighter.to_dict method
    # convert dict to json
    # load json into a file
    # upload file to database

    # driver.quit()

    print(athlete_names)
    print(athlete_weight_class)
    print(athlete_rankings)
    print(athlete_champion)
    print(athlete_win_streak)
    print(athlete_last_fight_outcome)
    print(athlete_last_5_record)
    print(athlete_last_opponents)
