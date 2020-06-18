import os, time
from selenium import webdriver
import utils

SCROLL_DOWN_LOOP_COUNT = 5
NUMBER_OF_ATTEMPTS = 3
GENERAL_WAITER = 5
WAIT_BEFORE_NEXT_ATTEMPT = 5
CITIES_FILENAME = 'cities.txt'
START_FROM_TOP = False


def get_cities_list(d):  # TODO: Remove {slug}
    """
    Gets list of cities from homepage of nomadlist.com, sorted by total count of users that visited the city
    Scrolls down the page SCROLL_DOWN_LOOP_COUNT times
    """
    go_to_url(d, 'https://nomadlist.com')
    time.sleep(GENERAL_WAITER)
    d.find_element_by_xpath("//option[@data-sort='users_been_count']").click()
    time.sleep(GENERAL_WAITER)
    # The homepage initially loads with around 20 cities, to get more cities we need to scroll down
    # For initial testing purposes the SCROLL_DOWN_LOOP_COUNT can be set to a small number
    # Each scroll adds apprx 24 cities (can vary based on screen resolution)
    scroll_down(d, SCROLL_DOWN_LOOP_COUNT)
    city_list = []
    city_elements = d.find_elements_by_css_selector("li[data-type='city']")
    for c in city_elements:
        city_list.append(c.get_attribute("data-slug"))
    if '{slug}' in city_list:
        city_list.pop(city_list.index('{slug}'))
    return city_list


def scroll_down(d, num):
    """
    Function for scrolling down on home page.
    Breaks if bottom of page is reached before we run out of loops to go through.
    Gives 3 more attempts in case there was in issue scrolling before
    (e.g. slow internet connection and new cities didn't load)
    """
    city_count = 0
    attempt = 1
    for i in range(num):
        d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        city_count_new = len(d.find_elements_by_css_selector("li[data-type='city']"))
        # print(f'City counts: old = {city_count}, new = {city_count_new}')
        if city_count == city_count_new:
            if attempt >= NUMBER_OF_ATTEMPTS:
                break
            else:
                attempt += 1
                time.sleep(WAIT_BEFORE_NEXT_ATTEMPT)
        city_count = city_count_new


def cities_extraction(driver):
    """Process of extracting user data of user_list"""
    cities_list = get_cities_list(driver)
    if not START_FROM_TOP:
        cities_list_from_file = utils.read_list_from_file(CITIES_FILENAME)
        result_list = cities_list_from_file
        result_list.extend(utils.get_new_items(cities_list_from_file, cities_list))
    else:
        result_list = cities_list
    return result_list


def go_to_url(d, url):
    """Navigates the browser to the url"""
    d.get(url)


def main():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.maximize_window()

    cities_list = cities_extraction(driver)
    print(f"Cities found: {len(cities_list)}")
    utils.write_list_to_file(CITIES_FILENAME, cities_list)

    time.sleep(GENERAL_WAITER)
    driver.quit()


if __name__ == '__main__':
    main()



