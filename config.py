# Flags
START_FROM_TOP = False
SAVE_MID_RESULTS = True
USER_CHUNK_SIZE = 10

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

# Filenames
CITIES_FILENAME = 'cities.txt'
USERS_INFO_FILENAME = 'users_info.txt'
USERS_LIST_FILENAME = 'users.txt'  # TODO: choose one
USERS_FILENAME = 'users.txt'

# Waiters
GENERAL_WAITER = 5
USERS_WAITER = 10
