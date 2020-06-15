import requests
from bs4 import BeautifulSoup


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
    return(people)


def get_all_users(list_of_cities):
    """
    scraps the desired cities' pages for users names
    params: list of cities
    return: list of users (uniq)
    """
    users_names = []
    for city in list_of_cities:
        domain = get_domain(city)
        users_names.extend(scrap_city(domain))
        users_names = list(set(users_names))
    return(users_names)


def main():
    cities = ['canggu', 'lisbon', 'berlin', 'buenos-aires', 'chiang-mai', 'puerto-vallarta', 'bangkok', 'mexico-city', 'belgrade', 'bengaluru', 'prague', 'taipei', 'cape-town', 'budapest', 'auckland', 'warsaw', 'singapore']
    list_of_cities = ['canggu', 'lisbon']
    print(get_all_users(list_of_cities))
    return 0


if __name__ == '__main__':
    main()
