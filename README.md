# nomadlist_scraping

###The purpose of this scraper is to get information about users of www.nomadlist.com:

- follower count
- trip count
- distance travelled
- number of countries and cities visited
- twitter and instagram accounts
- trip history


To run the full process run main_scraper.py

The process is using files such as cities.txt, users.txt for information storage.
Saves info into a DB. To create the database use create_db_script.sql <br>
To start from scratch (getting a list of cities and users) you need to either remove the files from the directory, 
or set the --new CLI argument to True. <br>
Setting the --new CLI argument to True will make the scraper run even on those users, who already exist in the DB,
and then updates their information (and inserts new trips if there are any)

To get such info as Twitter and Instagram accounts you need a login link that expires within 24 hours.

The app uses Twitter API to get Twitter user information. <br>
Set up the API keys in file config_secret.py (attached with the project submission, NOT included in github for security reasons)

You can set the login link as a CLI parameter --login_url

