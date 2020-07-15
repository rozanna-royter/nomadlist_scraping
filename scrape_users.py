from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import utils
import config
import db_utils


def get_users_info(driver, usernames):
    """
    Main function for processing pages of users from usernames list.
    Uses selenium webdriver as well as beautiful soup.
    :param driver: The instantiated web driver
    :param usernames: List of user names
    :return: Dictionary of users' info
    """
    result = {}
    for username in usernames:
        utils.go_to_url(driver, f'{config.BASE_URL}/@{username}')
        time.sleep(config.USERS_WAITER)
        soup_html = BeautifulSoup(driver.page_source, 'html.parser')

        like_button = soup_html.find(config.ATTRIBUTES_DICT["DIV_TAG"], class_=config.ATTRIBUTES_DICT["LIKE_USER"])
        if not like_button:
            driver.refresh()
            time.sleep(config.GENERAL_WAITER)
            like_button = soup_html.find(config.ATTRIBUTES_DICT["DIV_TAG"], class_=config.ATTRIBUTES_DICT["LIKE_USER"])
            if not like_button:
                print(config.MSG_DICT["USER_NOT_FOUND"].format(username))
                continue

        result[username] = {}
        result[username][config.NAMES_DICT["USER_ID"]] = like_button[config.ATTRIBUTES_DICT["USER_ID"]]

        for element in config.ELEMENTS_TO_PARSE:
            result[username][element] = get_text_from_info_bar(soup_html, element)
        distance_traveled = config.NAMES_DICT['DISTANCE']
        if result[username][distance_traveled]:
            result[username][distance_traveled] = result[username][distance_traveled].replace(',', '')

        result[username][config.NAMES_DICT["TRIP_LIST"]] = get_trips_selenium(driver)

        twitter_string = config.NAMES_DICT["TWITTER"]
        instagram_string = config.NAMES_DICT["INSTAGRAM"]
        result[username][twitter_string] = get_socials(driver, twitter_string)
        result[username][instagram_string] = get_socials(driver, instagram_string)

        bio = soup_html.find(config.ATTRIBUTES_DICT["DIV_TAG"], class_=config.ATTRIBUTES_DICT["USER_BIO"]).text
        result[username][config.NAMES_DICT["BIO"]] = bio[:config.BIO_LENGTH]
    return result


def print_details(info, username):
    """
    Prints all collected data per user
    :param info: Dictionary of user info
    :param username: User name
    :return: None
    """
    print(f"Username: {username}\nNumber of followers: {info['follower-count']}\n"
          f"Following: {info['following-count']}\nNumber of trips: {info['trips-count']}\n"
          f"Distance traveled: {info['distance-traveled']}\nCountries visited: {info['countries-count']}\n"
          f"Cities visited: {info['cities-count']}\nTrip list: {info['trip_list']}\n"
          f"Twitter account: {info['twitter']}\nInstagram account: {info['instagram']}\n")


def get_trips_selenium(driver):
    """
    Returns trips info from current page using selenium (faster than bs4)
    :param driver: The instantiated web driver
    :return: Dictionary of trip info
    """
    trips = driver.find_elements_by_xpath(config.TRIPS_XPATH)
    trip_ids = [t.get_attribute(config.ATTRIBUTES_DICT["ID"]) for t in trips]
    trip_editor_string = config.NAMES_DICT["TRIP_EDITOR"]
    if trip_editor_string in trip_ids:
        trip_ids.pop(trip_ids.index(trip_editor_string))
    if '' in trip_ids:
        trip_ids.pop(trip_ids.index(''))
    try:
        expand_trips_btn = driver.find_element_by_xpath(config.BUTTON_EXPAND_ALL_TRIPS)
    except NoSuchElementException:
        expand_trips_btn = None
    if expand_trips_btn:
        expand_trips_btn.click()
    trips_dict = {}
    for tid in trip_ids:
        trips_dict[tid] = {}
        for element in config.TRIP_ELEMENTS:
            if element == config.NAMES_DICT["NAME"]:
                trips_dict[tid][element] = driver.find_element_by_xpath(
                    config.CITY_NAME_ELEMENT_XPATH.format(tid, element)).text
            else:
                trips_dict[tid][element] = driver.find_element_by_xpath(
                    config.TRIP_ELEMENT_XPATH.format(tid, element)).text
    return trips_dict


def get_socials(driver, sn_name):
    """
    Function for extracting social network information (i.e. Twitter and Instagram)
    :param driver: The instantiated web driver
    :param sn_name: Social network name
    :return: Social network username (if exists, else - None)
    """
    try:
        social_button = driver.find_element_by_xpath(
            config.GET_SOCIALS_XPATH.format(sn_name)).get_attribute(config.ATTRIBUTES_DICT["HREF"])
        if social_button:
            return social_button.split('/')[-1]
        else:
            return None
    except NoSuchElementException:
        return None


def get_text_from_info_bar(soup, el_name):
    """
    Function for extracting info from an element of info bar
    :param soup: Html of the page (BeautifulSoup)
    :param el_name: Element (class) name
    :return: Appropriate info by element name (if exists, else - None)
    """
    try:
        return soup.select_one(config.SELECT_CLASS_CONTAINS.format(el_name)).find(
            config.ATTRIBUTES_DICT["DIV_TAG"], attrs={config.ATTRIBUTES_DICT["CLASS"]: config.NAMES_DICT["NUMBER"]}
        ).text
    except AttributeError:
        return None


def log_in(driver, m_link):
    """
    Log in using a link
    :param m_link: The link for log in as subscriber
    :param driver: The instantiated web driver
    :return: None
    """
    utils.go_to_url(driver, m_link)


def get_new_users(user_list, users_dict):
    """
    Returns a list of users that are present in user_list, but not present among the keys of users_dict
    :param user_list: Input list of users
    :param users_dict: Dictionary of users to check against
    :return: List of new users
    """
    res_list = []
    for u in user_list:
        if u not in users_dict.keys():
            res_list.append(u)
    return res_list


def get_new_users_db(user_list, existing_users):
    """
    Returns a list of users that are present in user_list, but not present in the list from DB
    :param user_list: Input list of users
    :param existing_users: List of users to check against
    :return: List of new users
    """
    res_list = []
    existing_users_list = [u['username'] for u in existing_users]
    for u in user_list:
        if u not in existing_users_list:
            res_list.append(u)
    return res_list


def user_info_extraction_cycle(driver, users_list, is_from_scratch):
    """
    Process of extracting user data of user_list and saving them to a file
    :param driver: The instantiated web driver
    :param users_list: List of user names
    :param is_from_scratch: boolean, specify if taking info from scratch
    :return: None
    """
    users_info_filename = config.USERS_INFO_FILENAME
    users_dict = {}
    if not is_from_scratch:
        try:
            users_dict = utils.read_dict_from_json(users_info_filename)
        except:
            users_dict = {}
        users_list = get_new_users(users_list, users_dict)
    if users_list:
        new_users_info = get_users_info(driver, users_list)
        users_dict.update(new_users_info)
        utils.write_dict_to_json(users_info_filename, users_dict)
        print(config.MSG_DICT["SAVING_USERS_COUNT"].format(len(new_users_info)))


def user_info_extraction_cycle_db(driver, users_list, is_from_scratch):
    """
    Process of extracting user data of user_list and saving them to a DB
    :param driver: The instantiated web driver
    :param users_list: List of user names
    :param is_from_scratch: boolean, specify if taking info from scratch
    :return: None
    """
    connection = db_utils.connect_to_db(config.DB_HOST, config.DB_USER, config.DB_PWD, config.DB_NAME)
    if not is_from_scratch:
        existing_users = db_utils.select_users(connection, users_list)
        users_list = get_new_users_db(users_list, existing_users)
    if users_list:
        users_dict = get_users_info(driver, users_list)
        if users_dict:
            db_utils.save_user_info(connection, users_dict)
            print(config.MSG_DICT["SAVING_DB_USERS_COUNT"].format(len(users_dict)))
    connection.close()


def get_users_loop(driver, users_list, is_from_scratch, chunk_size):
    """
    Looping through sublists of users with extraction_cycle
    :param driver: The instantiated web driver
    :param users_list: List of user names
    :param is_from_scratch: boolean, specify if taking info from scratch
    :param chunk_size: the size of group of users that function scrap their info in each cycle
    :return: None
    """
    user_chunks = [users_list[x:x + chunk_size] for x in range(0, len(users_list), chunk_size)]
    i = 1
    for chunk in user_chunks:
        print(config.MSG_DICT["PROCESSING_USER_CHUNK"].format(i, len(user_chunks)))
        user_info_extraction_cycle_db(driver, chunk, is_from_scratch)
        i += 1


def run(magic_link, from_scratch, chunk_size):  # TODO: bad gateway
    driver = webdriver.Chrome(utils.get_chromedriver_path())
    driver.maximize_window()
    if magic_link != '':
        log_in(driver, magic_link)
    users_list = utils.read_list_from_file(config.USERS_LIST_FILENAME)
    if config.SAVE_MID_RESULTS:
        get_users_loop(driver, users_list, from_scratch, chunk_size)
    else:
        user_info_extraction_cycle(driver, users_list)
    time.sleep(config.GENERAL_WAITER)
    driver.quit()
