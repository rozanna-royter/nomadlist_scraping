import requests
from bs4 import BeautifulSoup
import utils

CITIES_FILENAME = 'cities.txt'
USERS_FILENAME = 'users.txt'


def get_domain(city_name):
    """
    param: string with city name
    return: domain of the people area inside city's page
    exemple:
        input: berlin
        output: https://nomadlist.com/people/berlin
    """
    city_domain = "https://nomadlist.com/people/" + city_name
    return city_domain


def scrap_city(domain):
    """
    param: string containing a domain of people area inside city's page
    return: list of users that can be scrapped from that domain
            (visited the city, are there now, will be there)
            https://nomadlist.com/people/berlin
    """
    r = requests.get(domain)
    soup = BeautifulSoup(r.content, 'html.parser')
    people_there = soup.find('div', class_='people-here-now')
    people = []
    for a in people_there.find_all('a', href=True):
        people.append(a['href'][2:])
    return (people)


def get_all_users(list_of_cities):
    """
    scraps the desired cities' pages for users names
    params: list of cities
    return: list of users (uniq)
    """
    try:
        users_names = utils.read_list_from_file(USERS_FILENAME)
    except:
        users_names = []
    for city in list_of_cities:
        domain = get_domain(city)
        try:
            users_names.extend(scrap_city(domain))
        except:
            print(f"{city} city page not found")
        users_names = list(set(users_names))
        print(f"adding users from {city}")
    return users_names


def main():
    cities = utils.read_list_from_file(CITIES_FILENAME)
    users_list = get_all_users(cities)
    utils.write_list_to_file(USERS_FILENAME, users_list)
    return 0


if __name__ == '__main__':
    main()
