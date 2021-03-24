import requests
import logger
import json
import jsonUtil
from datetime import datetime, timedelta
import filtering

baseUrl = "https://api.twitter.com/2"
def getUserId(token, username):
    headers = {'Authorization': 'Bearer ' + token}
    params = {'usernames': username}
    response = requests.get(baseUrl + '/users/by', headers=headers, params=params)
    logger.printError(response)
    return response.json()['data'][0]['id']

def timelineOneDay(token, userId):
    headers = {'Authorization': 'Bearer ' + token }
    start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
            'start_time': start_time,
            'end_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            'tweet.fields': 'author_id,referenced_tweets'
    }
    response = requests.get(baseUrl + '/users/' + userId + '/tweets', headers=headers, params=params)
    logger.printError(response)
    return response.json()

def writeTodayTweets(bearer, usernames):
    collected = { 'filteredTweets': []}
    for user in usernames['twitterNames']:
        response = timelineOneDay(bearer, getUserId(bearer, user))
        if 'data' in response:
            appendRetweets(response['data'], bearer)
        if 'data' in response:
            filteredTweets = filtering.filterForTokens(response['data'])
            tweetsPerUser = { user: [] }
            for entry in filteredTweets:
                entry['link'] = f'https://twitter.com/{user}/status/{entry["id"]}'
                tweetsPerUser[user].append(entry)
            collected['filteredTweets'].append(tweetsPerUser)
    f = open(f"{datetime.now().strftime('%Y-%m-%d')}.json", "w")
    f.write(jsonUtil.toJson(collected))

def appendRetweets(data, bearer):
    for entry in data:
        if 'referenced_tweets' in entry:
            for reference in entry['referenced_tweets']:
                if reference['type'] == 'retweeted':
                    entry['text'] = fetchSingleTweet(bearer, reference['id'])


def fetchSingleTweet(token, tweetId):
    headers = {'Authorization': 'Bearer ' + token }
    response = requests.get(baseUrl + '/tweets/' + tweetId, headers=headers)
    return jsonUtil.toJson(jsonUtil.sanitizeText(response.json()['data']['text']))

