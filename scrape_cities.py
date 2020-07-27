import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import utils
import config
from logger import Logger


logger = Logger("scrape_cities").logger


def get_cities_list(driver, scroll_down_loop_count):
    """
    Gets list of cities from homepage of nomadlist.com, sorted by total count of users that visited the city
    Scrolls down the page scroll_down_loop_count times
    :param driver: The instantiated web driver
    :param scroll_down_loop_count: number of scroll downs to perform
    :return: List of cities extracted from the home page
    """
    utils.go_to_url(driver, config.BASE_URL)
    time.sleep(config.GENERAL_WAITER)
    driver.find_element_by_xpath(config.BUTTON_SORT_CITIES_BY_USERS_BEEN).click()
    time.sleep(config.GENERAL_WAITER)
    # The homepage initially loads with around 20 cities, to get more cities we need to scroll down
    # For initial testing purposes the scroll_down_loop_count can be set to a small number
    # Each scroll adds apprx 24 cities (can vary based on screen resolution)
    scroll_down(driver, scroll_down_loop_count)
    city_list = []
    city_elements = driver.find_elements_by_css_selector(config.CITY_ELEMENTS_CSS)
    for c in city_elements:
        city_list.append(c.get_attribute(config.CITY_NAME_ATTR))
    if '{slug}' in city_list:
        city_list.pop(city_list.index('{slug}'))
    return city_list


def scroll_down(driver, num):
    """
    Function for scrolling down on home page.
    Breaks if bottom of page is reached before we run out of loops to go through.
    Gives 3 more attempts in case there was in issue scrolling before
    (e.g. slow internet connection and new cities didn't load)
    :param driver: The instantiated web driver
    :param num: Number of scrolls to perform
    :return: None
    """
    city_count = 0
    attempt = 1
    scroll_num = 0
    while scroll_num < num:
        driver.execute_script(config.SCROLL_DOWN_SCRIPT)
        time.sleep(1)
        city_count_new = len(driver.find_elements_by_css_selector(config.CITY_ELEMENTS_CSS))
        if city_count == city_count_new:
            if attempt >= config.NUMBER_OF_ATTEMPTS:
                break
            else:
                attempt += 1
                time.sleep(config.WAIT_BEFORE_NEXT_ATTEMPT)
        city_count = city_count_new
        scroll_num += 1


def cities_extraction(driver, from_scrach, scroll_down):
    """
    Process of extracting user data of user_list
    :param driver: The instantiated web driver
    :param from_scrach: flag to determine whether to override the existing city list or append to it
    :param scroll_down: number of scroll downs to perform
    :return: List of cities
    """
    cities_list = get_cities_list(driver, scroll_down)
    if not from_scrach:
        try:
            cities_list_from_file = utils.read_list_from_file(config.CITIES_FILENAME)
        except FileNotFoundError:
            cities_list_from_file = []
        result_list = cities_list_from_file
        result_list.extend(utils.get_new_items(cities_list_from_file, cities_list))
    else:
        result_list = cities_list
    return result_list


def run(from_scratch, scroll_down_count):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(utils.get_chromedriver_path(), chrome_options=chrome_options)
    driver.maximize_window()

    cities_list = cities_extraction(driver, from_scratch, scroll_down_count)
    logger.info(config.MSG_DICT["CITIES_FOUND_COUNT"].format(len(cities_list)))
    utils.write_list_to_file(config.CITIES_FILENAME, cities_list)

    time.sleep(config.GENERAL_WAITER)
    driver.quit()



