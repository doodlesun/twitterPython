import login
import tweets
import json

if __name__ == '__main__':
    bearer = login.authorization()
    f = open('twitterNames.json')
    data = json.load(f)
    tweets.writeTodayTweets(bearer, data)

