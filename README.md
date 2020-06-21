# nomadlist_scraping

###The purpose of this scraper is to get information about users of www.nomadlist.com:

- follower count
- trip count
- distance travelled
- number of countries and cities visited
- twitter and instagram accounts
- trip history


To run the full process run main_scraper.py

The process is using files such as cities.txt, users.txt, users_info.txt for information storage.
To start from scratch you need to either remove the files from the directory, or set the START_FROM_TOP 
constant to True (in scrape_cities.py and scrape_users.py)

To get such info as Twitter and Instagram accounts you need a login link that expires within 24 hours.

You can change the login link in scrape_users.py - constant LOGIN_URL

