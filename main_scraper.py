"""Full process of scraping city names and user info wrapped in one place"""
import scrape_cities
import get_users
import scrape_users


def main():
    scrape_cities.main()
    get_users.main()
    scrape_users.main()


if __name__ == '__main__':
    main()


