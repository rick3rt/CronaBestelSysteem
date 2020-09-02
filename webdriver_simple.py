from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import pickle
import time

driver = webdriver.Chrome()
driver.get("https://www.ah.nl/")

print('login bij de appie in de browser, druk enter als klaar')
foo = input()


urls = ['https://www.ah.nl/producten/product/wi67896/ah-handsinaasappelen-medium',
        'https://www.ah.nl/producten/product/wi188228/chocomel-dark',
        'https://www.ah.nl/producten/product/wi446406/ah-les-pains-de-boulogne-meergr-volk-heel',
        'https://www.ah.nl/producten/product/wi420789/statesman-tonijn-stukken-in-water',
        'https://www.ah.nl/producten/product/wi67762/ah-afwas-extra-hygiene']
# elem = driver.find_elements_by_css_selector("[aria-label=plus]").click()


# COOKIE BUTTON
# '//*[@id="accept-cookies"]'

for i, url in enumerate(urls):
    driver.get(url)
    actions = ActionChains(driver)

    elem_voeg_toe = driver.find_element_by_xpath(
        '//*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/button/span')
    actions.click(elem_voeg_toe).perform()

    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    elem_voeg_meer_toe = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]')))
    elem_voeg_meer_toe.click()
    elem_voeg_meer_toe.click()

    time.sleep(2.5)

    # elem_voeg_meer_toe = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_any_elements_located(
    #         (By.XPATH, '/html/body/div[3]/main/article/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]/svg'))
    # )
    # elem_voeg_meer_toe.send_keys(u'\ue007')  # send enter

    # EC.element_to_be_clickable((By.XPATH, '//*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]/svg'))

    # elem_voeg_meer_toe = driver.find_element_by_xpath(
    #     '//*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]/svg')
    # actions.click(elem_voeg_meer_toe).perform()


print('betaal en druk enter om browser te sluiten')
foo = input()

driver.close()


# VOEG TOE:
# //*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/button/span/svg
# PLUS
# //*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]/svg
# //*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]
# //*[@id="start-of-content"]/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]/svg/use
# /html/body/div[3]/main/article/div[1]/div/div/div/article/div/div/div[2]/div[2]/div[2]/div/button[2]/svg

# # COOCKIE MANAGEMENT
# def save_cookie(mydriver, path):
#     with open(path, 'wb') as filehandler:
#         pickle.dump(mydriver.get_cookies(), filehandler)


# def load_cookie(mydriver, path):
#     with open(path, 'rb') as cookiesfile:
#         cookies = pickle.load(cookiesfile)
#         for cookie in cookies:
#             mydriver.add_cookie(cookie)


# driver = webdriver.Chrome()
# load_cookie(driver, 'cookie_ah')
# driver.get("https://www.ah.nl/")
# # assert "Jumbo" in driver.title

# # urls

# # urls = ['https://www.ah.nl/producten/product/wi67896/ah-handsinaasappelen-medium',
# #         'https://www.ah.nl/producten/product/wi188228/chocomel-dark',
# #         'https://www.ah.nl/producten/product/wi446406/ah-les-pains-de-boulogne-meergr-volk-heel',
# #         'https://www.ah.nl/producten/product/wi420789/statesman-tonijn-stukken-in-water',
# #         'https://www.ah.nl/producten/product/wi67762/ah-afwas-extra-hygiene']

# # for url in urls:
# #     driver.get(url)
# #     time.sleep(2)

# # elem = driver.find_element_by_name("searchTerms")
# # elem.clear()
# # elem.send_keys("pycon")
# # elem.send_keys(Keys.RETURN)
# # assert "No results found." not in driver.page_source

# foo = input()
# # save_cookie(driver, 'cookie_ah')

# driver.close()
