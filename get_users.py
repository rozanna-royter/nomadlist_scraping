import requests
from bs4 import BeautifulSoup
import utils
import config
from logger import Logger


logger = Logger("get_users").logger


def get_domain(city_name):
    """
    param: string with city name
    return: domain of the people area inside city's page
    example:
        input: berlin
        output: https://nomadlist.com/people/berlin
    """
    city_domain = config.CITY_PEOPLE_URL + city_name
    return city_domain


def scrap_city(domain):
    """
    param: string containing a domain of people area inside city's page
    return: list of users that can be scrapped from that domain
            (visited the city, are there now, will be there)
            https://nomadlist.com/people/berlin
    """
    people = []
    try:
        r = requests.get(domain)
        soup = BeautifulSoup(r.content, 'html.parser')
        people_there = soup.find(config.ATTRIBUTES_DICT["DIV_TAG"], class_=config.ATTRIBUTES_DICT["PEOPLE"])
        for a in people_there.find_all(config.ATTRIBUTES_DICT["A_TAG"], href=True):
            people.append(a[config.ATTRIBUTES_DICT["HREF"]][config.USER_LINK_CHAR_START:])
    except requests.TooManyRedirects as error:
        logger.error(error)
        logger.error(f'For url: {domain}')
    return people




def get_all_users(list_of_cities):
    """
    scraps the desired cities' pages for users names
    params: list of cities
    return: list of users (uniq)
    """
    try:
        users_names = utils.read_list_from_file(config.USERS_FILENAME)
    except FileNotFoundError:
        users_names = []
    for city in list_of_cities:
        domain = get_domain(city)
        new_user_names = []
        try:
            new_user_names = scrap_city(domain)
            users_names.extend(new_user_names)
        except FileNotFoundError:
            logger.warning(config.MSG_DICT["CITY_PAGE_NOT_FOUND"].format(city))
        users_names = list(set(users_names))
        if len(new_user_names) > 0:
            logger.info(config.MSG_DICT["ADDING_USERS"].format(city))
    return users_names


def run():
    cities = utils.read_list_from_file(config.CITIES_FILENAME)
    users_list = get_all_users(cities)
    utils.write_list_to_file(config.USERS_FILENAME, users_list)
