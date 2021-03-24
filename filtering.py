import re

import logger
import requests
from datetime import datetime 

coingeckoUrl = 'https://api.coingecko.com/api/v3'
allCoins = requests.get(coingeckoUrl + '/coins/list')

def filterForTokens(data):
    regex = re.compile(r'(?!.*[BTC]|[ETH])([\$|\#][A-Z0-1]{2,})')
    filtered = []
    for entry in data:
        if match := regex.findall(entry['text']):
            extractTicker(entry, match, filtered)
        elif 'retweet' in entry:
            if match := regex.findall(entry['retweet']):
                extractTicker(entry, match, filtered)
    return filtered

def extractTicker(entry, match, filtered):
        replacedMatches = []
        for ticker in match:
            replacedMatches.append(ticker.replace('#', '').replace('$', ''))
        noDuplicateList = list(dict.fromkeys(replacedMatches))
        entry['token_prices'] = getTokenPrice(noDuplicateList)
        filtered.append(entry)

def getTokenPrice(tokenArr):
    lowerTokenArr = []
    for entryToken in tokenArr:
        lowerTokenArr.append(entryToken.lower())
    logger.printError(allCoins)
    ids = []
    tokens = {}
    for coin in allCoins.json():
        if coin['symbol'] in lowerTokenArr:
            ids.append(coin['id'])
            tokens[coin['id']] = coin['symbol']
    returnValue = {}
    if len(ids) > 0:
        params = {'ids': ','.join(ids) , 'vs_currencies': 'usd' }
        price = requests.get(coingeckoUrl + '/simple/price', params=params)
        logger.printError(price)
        response = price.json()
        for tokenId in list(dict.fromkeys(tokens)):
            response[tokenId]['symbol'] = tokens[tokenId].upper()
            response[tokenId]['time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        returnValue = response
    return returnValue;

