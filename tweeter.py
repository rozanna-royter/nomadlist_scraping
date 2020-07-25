import requests
from requests_oauthlib import OAuth1
import config
import config_secret


def display_user(twitter_name):
    """
    Uses twitter API to get user info
    :param twitter_name: str - twitter username
    :return: dictionary with user info
    """
    url = config.TWITTER_API_URL
    params = {'screen_name': f'{twitter_name}'}
    auth = OAuth1(config_secret.APP_KEY, config_secret.APP_SECRET, config_secret.ACCESS_TOKEN,
                  config_secret.ACCESS_TOKEN_SECRET)
    try:
        res = requests.get(url, auth=auth, params=params)
        r = res.json()  # parse the json
        return r
    except requests.exceptions.RequestException as error:
        print(error)
        return None
