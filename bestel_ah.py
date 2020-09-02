from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from sheet_scraper import ScraleScraper
import pandas as pd
import time


def bestellen_maar(datafreempje, driver):
    # maak frame
    df_gemist = pd.DataFrame(data=None, columns=datafreempje.columns)

    for index, row in datafreempje.iterrows():
        url = row['Link']
        aantal = int(row['Hoeveel'])
        producenaam = SS.get_name_url(url)

        print('ik ga bestellen:\t %d x %s' % (aantal, producenaam))

        driver.get(url)
        actions = ActionChains(driver)
        try:
            elem_voeg_toe = driver.find_element_by_xpath(
                '//*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/button/span')
            actions.click(elem_voeg_toe).perform()

            if aantal > 1:
                ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
                elem_voeg_meer_toe = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]')))
                elem_voeg_meer_toe.click()
                while aantal - 2 > 0:
                    elem_voeg_meer_toe.click()
                    aantal -= 1

            # print('even wachten tot het in mn mandje ligt...', end='', flush=True)
            time.sleep(4)
            # print('ja ligt erin hoor!')

        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            print('product gemist, even op adem komen... %s' % producenaam)
            time.sleep(5)
            df_gemist = df_gemist.append(row, ignore_index=True)

    return df_gemist


# start driver
driver = webdriver.Chrome()
driver.get("https://www.ah.nl/")
actions = ActionChains(driver)

# maak skrale skraper
SPREADSHEET_ID_input = '1gEUMO67MNcgKsz40Wfx5GinMjJoLWGm9tSyLJ2MCnuc'
RANGE_NAME = 'A4:AD100'
SS = ScraleScraper(SPREADSHEET_ID_input, RANGE_NAME)
SS.doe_het_allemaal()
# levert op
# SS.df_simple

# data frame voor gemiste producten
# df_gemist = pd.DataFrame().reindex_like(SS.df_simple)
# df_gemist = pd.DataFrame(data=None, columns=SS.df_simple.columns)
# for index, row in SS.df_simple.iterrows():
#     df_gemist = df_gemist.append(row, ignore_index=True)

# click cookie knop
elem_cook = driver.find_element_by_xpath('//*[@id="accept-cookies"]')
actions.click(elem_cook).perform()

print('login bij de appie in de browser, druk enter als klaar')
foo = input()


gemiste_produce = bestellen_maar(SS.df_simple, driver)
print("============================")
print("ik heb wat gemist:")
print(gemiste_produce)
print("============================")
print("opniew proberen:")
alweer_gemist = bestellen_maar(gemiste_produce, driver)
print("============================")
print("ik heb weer wat gemist:")
print(alweer_gemist)
print("============================")
print("Moet je even handmatig toevoegen:")
lijstje = alweer_gemist['Link'].tolist()
for l in lijstje:
    print(l)

print("============================")
print('Totaal aantal producten moet zijn: %d' % SS.df_simple['Hoeveel'].sum())


print("============================")


print('betaal en druk enter om browser te sluiten')
foo = input()

driver.close()
