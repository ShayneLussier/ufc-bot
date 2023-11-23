from selenium import webdriver
from selenium.webdriver.common.by import By
import math
import time


# ------------------------- SELENIUM SETUP -------------------------- #
# proxy needed to load website in english via usa
proxy = {
    'http': '32.223.6.94:80',
    'https': '37.19.220.133:8443',
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
    "Flyweight": "3A10",
    "Bantamweight": "3A8",
    "Featherweight": "3A9",
    "Lightweight": "3A12",
    "Welterweight": "3A15",
    "Middleweight": "3A14",
    "Light Heavyweight": "3A13",
    "Heavyweight": "3A11",
    "Women Strawweight": "3A16",
    "Women Flyweight": "3A38",
    "Women Bantamweight": "3A37",
    "Women Featherweight": "3A39"
}

driver = webdriver.Chrome(options=chrome_options)
driver.get(f'https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&filters%5B1%5D=weight_class%{WEIGHT_CLASSES["Women Bantamweight"]}')


athlete_total = driver.find_element(By.CLASS_NAME, 'althelete-total').text
athlete_total = int(athlete_total.split()[0])
extra_athletes = athlete_total - 11
load_more_athletes = math.ceil(extra_athletes / 11)


for n in range(load_more_athletes):
    load_more_button = driver.find_element(By.CSS_SELECTOR, ".pager__item .button")
    print("clicking button")
    load_more_button.click()
    print("button clicked!")
    time.sleep(2)

athlete_names = driver.find_elements(By.CSS_SELECTOR, '.c-listing-athlete__text .c-listing-athlete__name')

names = []
for name in athlete_names:
    names.append(name.text.lower().replace(" ", "-"))
print(names)

for name in names:
    time.sleep(3) # is this timeout needed???
    driver.get(f'https://www.ufc.com/athlete/{name}')
    try:
        ranking = driver.find_element(By.CLASS_NAME, 'hero-profile__tag').text.split()[0]
        print(ranking)
    except:
        pass


    # https://www.sherdog.com/stats/fightfinder?SearchTxt=raquel+pennington&weight=&association=
    # .replace("-", "+")
    # click on fighter to open page

    # past_3_results = []
    # for n in range(3):
    #     past_result = driver.find_elements(By.CSS_SELECTOR, 'strong').text
    #     past_3_results.append(past_result)

    # print(past_3_results)
    # win = 0
    # loss = 0
    # draw = 0
    # for result in past_3_results:
    #     if "won" in result:
    #         win += 1
    #     elif "stopped" in result:
    #         win += 1
    #     elif "knocked out" in result:
    #         win += 1
    #     elif "submitted" in result:
    #         win += 1
    #     elif "lost" in result:
    #         loss += 1
    #     elif "was submitted" in result:
    #         loss += 1
    #     elif "was knocked" in result:
    #         loss += 1
    #     else:
    #         draw += 1
    # record = {
    #     "wins": win,
    #     "loss": loss,
    #     "draw": draw
    # }
    # print(record)


    # get record of last 3 fights (w-l-d)
    # get name of last opponent
    # get outcome of last fight (w-l-d)
    # save data to csv

# upload csv to database


driver.quit()