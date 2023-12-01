import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from math import ceil
from time import sleep
from unidecode import unidecode
from uuid import uuid4
from schema import Fighter


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
                    ranking = rank.text.split()[0][1:]
                    RankingsList.append(int(ranking))
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
    try:
        record = Driver.find_element(By.CLASS_NAME, "hero-profile__division-body")
        wins = record.text.split("-")[0]
        losses = record.text.split("-")[1]
        fighter_record = {"win": int(wins), "loss": int(losses)}
        RecordDict[FighterName] = fighter_record
    except:
        RecordDict[FighterName] = {"win": 0, "loss": 0}
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
    WinStreakList.append(int(win_streak))
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


def data_collector():
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
        athlete_record = {}

        # collect active fighter names for current division
        athlete_names, athlete_count = collect_names(
            Driver=driver,
            WeightClassName=weight_class_name,
            WeightClassCode=weight_class_code,
            NamesDict=athlete_names,
        )

        # collect data from fighter page at ufc.com
        for name in athlete_names[weight_class_name]:
            driver.get(f"https://www.ufc.com/athlete/{name}")
            sleep(1)

            # collect rank
            athlete_rankings = collect_rank(Driver=driver, RankingsList=athlete_rankings)

            # collect championship status
            athlete_champion = collect_is_champion(
                RankingList=athlete_rankings, ChampionStatusList=athlete_champion
            )

            # collect record
            athlete_record = collect_record(Driver=driver, FighterName=name, RecordDict=athlete_record)

        # retrive remaining data from espn.com
        for name in athlete_names[weight_class_name]:
            fighter_found = False
            driver.get(f"https://www.espn.com/search/_/type/players/q/{name}")
            sleep(1)

            athlete_link = driver.find_elements(
                By.CSS_SELECTOR, ".AnchorLink.LogoTile.flex.items-center.pl3.pr3"
            )
            # collect all fighter profile urls that do MMA under current name (doppleganger)
            athlete_urls = []
            for link in athlete_link:
                athlete_urls.append(link.get_attribute("href"))

            for link in athlete_urls:
                if link.split("/")[3] == "mma":
                    driver.get(link)
                    sleep(1)

                    try:  # verify if doppleganger has a UFC or Contender Series bout, if not skip to next fighter
                        event_names = driver.find_elements(
                            By.CSS_SELECTOR, ".AnchorLink.FightHistoryCard__Event.tl"
                        )
                        for event in event_names:
                            if event.text[:3] == "UFC" or event.text[:4] == "Dana":
                                fighter_found = True
                                break  # break for event in event_names loop

                        if fighter_found:
                            break  # if doppleganger has UFC experience, break for link in athlete_urls loop

                    except:  # if no UFC experience, verify next doppleganger in list
                        driver.get(f"https://www.espn.com/search/_/type/players/q/{name}")
                        sleep(1)

            # if no fighter page exists, commit default value and skip the data collection loop
            if not fighter_found:
                athlete_rankings.append(None)
                athlete_champion.append(False)
                athlete_last_opponents[name] = []
                athlete_record[name] = {"win": 0, "loss": 0}
                athlete_win_streak.append(0)
                athlete_last_fight_outcome.append("not found")
                athlete_country.append("Unknown")
                athlete_espn_id.append(str(uuid4())) # append random uuid to missing fighter, if mutliple fighters have null "_id", mongodb will return error
                continue

            fight_record_link = driver.find_element(
                By.CLASS_NAME, "Card__Header__SubLink__Text"
            )
            fight_record_link.click()
            sleep(1)

            # collect remaining stats
            try:
                # collect last 5 opponents
                athlete_last_opponents = collect_last_opponents(
                    Driver=driver,
                    FighterName=name,
                    LastOpponentsDict=athlete_last_opponents,
                )

                # collect win streak
                athlete_win_streak, fight_results = collect_win_streak(Driver=driver, WinStreakList=athlete_win_streak)

                # collect last fight outcome
                athlete_last_fight_outcome = collect_last_fight_outcome(
                    FightResults=fight_results,
                    FightOutcomeList=athlete_last_fight_outcome,
                )

                # collect country
                athlete_country = collect_country(Driver=driver, CountryList=athlete_country)

                # collect espn_id
                athlete_espn_id = collect_espn_id(Driver=driver, IdList=athlete_espn_id)

            except:  # espn page blank, commit default values
                athlete_rankings.append(None)
                athlete_champion.append(False)
                athlete_last_opponents[name] = []
                athlete_record[name] = {"win": 0, "loss": 0}
                athlete_win_streak.append(0)
                athlete_last_fight_outcome.append("not found")
                athlete_country.append("Unknown")
                athlete_espn_id.append(str(uuid4()))

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
                fight_record=athlete_record[name],
                last_5_opponents=athlete_last_opponents[name],
            ).to_dict()
            save_data(fighter_dict)
            index += 1

    driver.quit()
