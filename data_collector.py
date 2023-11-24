from selenium import webdriver
from selenium.webdriver.common.by import By
import math
import time
from schema import Fighter
from ufc_functions import save_data


# ------------------------- SELENIUM SETUP -------------------------- #
# proxy needed to load website in english via usa
proxy = {
    'http': '32.223.6.94:80',
    'https': '37.19.220.132:8443',
}

# keep browser open
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Merge Chrome options and proxy options
chrome_options.add_argument(f'--proxy-server={proxy["http"]}')
chrome_options.add_argument(f'--proxy-server={proxy["https"]}')


# ------------------------- TESTING -------------------------- #
# add all weight classes
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
    "women featherweight": "3A39"
}

driver = webdriver.Chrome(options=chrome_options)
driver.get(f'https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&filters%5B1%5D=weight_class%{WEIGHT_CLASSES["women bantamweight"]}')


athlete_total = driver.find_element(By.CLASS_NAME, 'althelete-total').text
athlete_total = int(athlete_total.split()[0])
extra_athletes = athlete_total - 11
load_more_athletes = math.ceil(extra_athletes / 11)

# load more pages
# for n in range(load_more_athletes):
#     load_more_button = driver.find_element(By.CSS_SELECTOR, ".pager__item .button")
#     print("clicking button")
#     load_more_button.click()
#     print("button clicked!")
#     time.sleep(20)

# fighter data
athlete_names = driver.find_elements(By.CSS_SELECTOR, '.c-listing-athlete__text .c-listing-athlete__name')
athlete_weight_class = "women bantamweight"
athlete_rankings = []
athlete_champion = []


athlete_last_opponents = []



# visit fighter page
url_names = []
for name in athlete_names:
    url_names.append(name.text.lower().replace(" ", "-"))
for name in url_names:
    time.sleep(3) # is this timeout needed???
    driver.get(f'https://www.ufc.com/athlete/{name}')

    # collect rank
    try:
        ranking = driver.find_element(By.CLASS_NAME, 'hero-profile__tag').text.split()[0] # rank number
        if "#" not in ranking:
            ranking = driver.find_elements(By.CLASS_NAME, 'hero-profile__tag') # title holder
        if "Title Holder" in ranking[3].text:
            ranking = 0
    except:
        ranking =  None
    finally:
        athlete_rankings.append(ranking)

    # collect championship status
    for ranking in athlete_rankings:
        if ranking == 0:
            champion_status = True
            athlete_champion.append(champion_status)
        else:
            champion_status = False
            athlete_champion.append(champion_status)
    
    # retrive remaining data from espn
    driver.get(f'https://www.espn.com/search/_/q/{name}')
    # time.sleep() ?
    link = driver.find_element(By.CSS_SELECTOR, '.AnchorLink.LogoTile.flex.items-center.pl3.pr3')
    link.click()

    # try block, does not mean there is up to 5 opponents
    # collect last 5 opponents
    fight_results = driver.find_elements(By.CSS_SELECTOR, '.tl.Table__TD .AnchorLink')
    for result in fight_results[:10:2]:
        opponent = result.get_attribute("href").split('/')[-1]
        athlete_last_opponents.append(opponent)


    



# create a fighter class for each fighter
# fighter.to_dict method
# convert dict to json
# load json into a file
# upload file to database


# driver.quit()