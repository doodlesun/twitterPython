import requests
import logger
import json
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
    params = {'start_time': start_time, 'end_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
    response = requests.get(baseUrl + '/users/' + userId + '/tweets', headers=headers, params=params)
    logger.printError(response)
    return response.json()

def writeTodayTweets(bearer):
    f = open('twitterNamesTest.json')
    data = json.load(f)
    collected = { 'filteredTweets': []}
    for user in data['twitterNames']:
        response = timelineOneDay(bearer, getUserId(bearer, user))
        if 'data' in response:
            filteredTweets = filtering.filterForTokens(response['data'])
            tweetsPerUser = { user: [] }
            for entry in filteredTweets:
                entry['link'] = f'https://twitter.com/{user}/status/{entry["id"]}'
                tweetsPerUser[user].append(entry)
            collected['filteredTweets'].append(tweetsPerUser)
    f = open(f"{datetime.now().strftime('%Y-%m-%d')}.json", "w")
    f.write(json.dumps(collected, indent=4, sort_keys=False))

