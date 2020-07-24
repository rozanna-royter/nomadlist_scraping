import requests
from requests_oauthlib import OAuth1


APP_KEY = 'HRMehIJDMugllNyvbV8hF0sTp'
APP_SECRET = 'sN8PAcNC5o2e35ekAz8vAT6SQuq0YZfvHTvXHv1v5mAfiUr6Of'
ACCESS_TOKEN = '1100683857576247296-Wh2aPXkcRciBmtJfiuX06LTffITaJU'
ACCESS_TOKEN_SECRET = 'A7Ah1mBhfQIYReqkGR3telp4Qtv8o5sHhLFJNCCc7ok5L'


def display_user(r):
    r = r.json()  # parse the json
    print(r)


url = 'https://api.twitter.com/1.1/users/show.json'
params = {'screen_name': '@DatzOrna'}
auth = OAuth1(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
try:
    res = requests.get(url, auth=auth, params=params)
    display_user(res)
except requests.exceptions.RequestException as error:
    print(error)



















#
# import tweepy
#
#
#
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
#
# api = tweepy.API(auth)
#
# followers = api.followers('@DatzOrna', wait_on_rate_limit=True, count=200)
# print(len(followers))








# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     # print(tweet.text)
