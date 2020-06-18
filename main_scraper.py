"""Full process of scraping city names and user info wrapped in one place"""
import scrape_cities
import get_users
import scrape_users


def main():
    print("Scraping cities...")
    scrape_cities.main()
    print("Getting all usernames...")
    get_users.main()
    print("Scraping user info...")
    scrape_users.main()


if __name__ == '__main__':
    main()


