# Flags
START_FROM_TOP = False
SAVE_MID_RESULTS = True
USER_CHUNK_SIZE = 10
USER_LINK_CHAR_START = 2

# Elements
ELEMENTS_TO_PARSE = ['follower-count', 'following-count', 'trips-count', 'distance-traveled', 'countries-count', 'cities-count']
TRIP_ELEMENTS = ['trip_start', 'trip_length', 'trip_end', 'name', 'country']

# Constants for scrolling
SCROLL_DOWN_LOOP_COUNT = 60
NUMBER_OF_ATTEMPTS = 3
WAIT_BEFORE_NEXT_ATTEMPT = 5

# URLs
LOGIN_URL = 'http://nomadlist.com/userApi.php?action=login_by_email&hash=8a50429958a8730e6ff97e65e1c4840798e86053'
BASE_URL = 'https://nomadlist.com'
CITY_PEOPLE_URL = 'https://nomadlist.com/people/'

# Filenames
CITIES_FILENAME = 'cities.txt'
USERS_INFO_FILENAME = 'users_info.txt'
USERS_LIST_FILENAME = 'users.txt'  # TODO: choose one
USERS_FILENAME = 'users.txt'

# Waiters
GENERAL_WAITER = 5
USERS_WAITER = 10

# Driver paths
PATH_TO_CHROMEDRIVER_MACOS = 'Drivers/macos/chromedriver'
PATH_TO_CHROMEDRIVER_LINUX = 'Drivers/linux/chromedriver'
PATH_TO_CHROMEDRIVER_WINDOWS = 'Drivers/windows/chromedriver.exe'
OS_DRIVER_PATHS = {
    'darwin': PATH_TO_CHROMEDRIVER_MACOS,
    'win32': PATH_TO_CHROMEDRIVER_WINDOWS,
    'linux': PATH_TO_CHROMEDRIVER_LINUX,
    'linux2': PATH_TO_CHROMEDRIVER_LINUX
}
# Scripts
SCROLL_DOWN_SCRIPT = "window.scrollTo(0, document.body.scrollHeight);"

# Strings for selenium and bs4 finders
BUTTON_SORT_CITIES_BY_USERS_BEEN = "//option[@data-sort='users_been_count']"
CITY_ELEMENTS_CSS = "li[data-type='city']"
CITY_NAME_ATTR = "data-slug"
TRIPS_XPATH = "//table[@id='trips']//tr[contains(@class,'trip')]"
BUTTON_EXPAND_ALL_TRIPS = "//div[contains(@class,'action-expand-all')][@data-what='trips']"
CITY_NAME_ELEMENT_XPATH = "//tr[@id='{}']//td[contains(@class,'{}')]//h2"
TRIP_ELEMENT_XPATH = "//tr[@id='{}']//td[contains(@class,'{}')]"
GET_SOCIALS_XPATH = "//a[contains(@class,'action-contact-user-{}')]"
SELECT_CLASS_CONTAINS = "div[class*={}]"
ATTRIBUTES_DICT = {
    "CITY_NAME": "data-slug",
    "HREF": "href",
    "ID": "id",
    "CLASS": "class",
    "DIV_TAG": "div",
    "A_TAG": "a",
    "PEOPLE": "people-here-now"
}
NAMES_DICT = {
    "TRIP_LIST": "trip_list",
    "TWITTER": 'twitter',
    "INSTAGRAM": "instagram",
    "TRIP_EDITOR": "trip_editor",
    "NAME": "name",
    "NUMBER": "number"
}

# Messages
MSG_DICT = {
    "CITIES_FOUND_COUNT": "Cities found: {}",
    "SAVING_USERS_COUNT": "Saving to file: {} new users",
    "PROCESSING_USER_CHUNK": "Processing user chunk #{} out of {}",
    "OS_ERROR": "Unknown OS '{}'",
    "FILE_NOT_FOUND": "File {} doesn't exist",
    "CITY_PAGE_NOT_FOUND": "{} city page not found",
    "ADDING_USERS": "adding users from {}"
}