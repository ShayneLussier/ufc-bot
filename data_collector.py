# ------------------------- IMPORTS -------------------------- #
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
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
    collect_country,
    collect_espn_id
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
    athlete_espn_id = []
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
    athlete_country = []
    athlete_rankings = []
    athlete_champion = []
    athlete_win_streak = []
    athlete_last_fight_outcome = []
    athlete_last_opponents = {}
    athlete_last_5_record = {}


    # collect active fighter names for current division
    athlete_names, athlete_count = collect_names(
        Driver=driver,
        WeightClassName=weight_class_name,
        WeightClassCode=weight_class_code,
        NamesDict=athlete_names
    )

    # collect data from fighter page at ufc.com
    for name in athlete_names[weight_class_name]:
        driver.get(f"https://www.ufc.com/athlete/{name}")
        sleep(1)

        # collect rank
        athlete_rankings = collect_rank(
            Driver=driver, RankingsList=athlete_rankings
        )

        # collect championship status
        athlete_champion = collect_is_champion(
            RankingList=athlete_rankings, ChampionStatusList=athlete_champion
        )
        
        # retrive remaining data from espn.com
    for name in athlete_names[weight_class_name]:
        fighter_found = False
        driver.get(f"https://www.espn.com/search/_/type/players/q/{name}")
        sleep(1)

        athlete_link = driver.find_elements(By.CSS_SELECTOR, ".AnchorLink.LogoTile.flex.items-center.pl3.pr3")
        # collect all fighter profile urls that do MMA under current name
        athlete_urls = []
        for link in athlete_link:
            athlete_urls.append(link.get_attribute("href"))

        for link in athlete_urls:
            if link.split("/")[3] == "mma":
                driver.get(link)
                sleep(1)

                try: # verify if athlete has had a UFC or Contender Series bout, if not skip to next fighter with same name
                    event_names = driver.find_elements(By.CSS_SELECTOR, ".AnchorLink.FightHistoryCard__Event.tl")
                    for event in event_names:
                        if event.text[:3] == "UFC" or event.text[:4] == "Dana":
                            fighter_found = True
                except:
                    driver.get(f"https://www.espn.com/search/_/type/players/q/{name}")
                    sleep(1)


        # if fighter isn't found, enter default value and skip the data collection loop
        if not fighter_found:
            athlete_rankings.append(None)
            athlete_champion.append(False)
            athlete_last_opponents[name] = []
            athlete_last_5_record[name] = {"wins": 0, "loss": 0, "other": 0}
            athlete_win_streak.append(0)
            athlete_last_fight_outcome.append("not found")
            athlete_country.append(None)
            athlete_espn_id.append(None)
            continue

        fight_record_link = driver.find_element(By.CLASS_NAME, "Card__Header__SubLink__Text")

        fight_record_link.click()
        sleep(1)

        try:
            # collect last 5 opponents
            athlete_last_opponents = collect_last_opponents(
                Driver=driver,
                FighterName=name,
                LastOpponentsDict=athlete_last_opponents,
            )

            # collect last 5 fight record
            athlete_last_5_record, fight_results = collect_last_5_record(
                Driver=driver,
                FighterName=name,
                LastFightsDict=athlete_last_5_record,
            )

            # collect win streak
            athlete_win_streak = collect_win_streak(
                FightResults=fight_results, WinStreakList=athlete_win_streak
            )

            # collect last fight outcome
            athlete_last_fight_outcome = collect_last_fight_outcome(
                FightResults=fight_results,
                FightOutcomeList=athlete_last_fight_outcome,
            )

            # collect country
            athlete_country = collect_country(Driver=driver, CountryList=athlete_country)

            # collect espn_id
            athlete_espn_id = collect_espn_id(Driver=driver, IdList=athlete_espn_id)

        except: # if espn page doesn't load, commit default values
            athlete_rankings.append(None)
            athlete_champion.append(False)
            athlete_last_opponents[name] = []
            athlete_last_5_record[name] = {"wins": 0, "loss": 0, "other": 0}
            athlete_win_streak.append(0)
            athlete_last_fight_outcome.append("not found")
            athlete_country.append(None)
            athlete_espn_id.append(None)


    # save data to json file
    index = 0
    for name in athlete_names[weight_class_name]:
        fighter_dict = Fighter(
            id=athlete_espn_id[index],
            name=athlete_names[weight_class_name][index],
            country=athlete_country[index],
            weight_class=weight_class_name,
            rank=athlete_rankings[index],
            champion=athlete_champion[index],
            win_streak=athlete_win_streak[index],
            last_fight_outcome=athlete_last_fight_outcome[index],
            last_5_fight_record=athlete_last_5_record[name],
            last_5_opponents=athlete_last_opponents[name],
        ).to_dict()
        save_data(fighter_dict)
        index += 1

driver.quit()
