import re

import logger
import requests
import json
from datetime import datetime 

coingeckoUrl = 'https://api.coingecko.com/api/v3'
allCoins = requests.get(coingeckoUrl + '/coins/list')
logger.printError(allCoins)

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

# Might be useful later on
def checkForToken(entry, filtered):
    foundTicker = []
    for ticker in allCoins.json():
        if ticker['name'] in entry['text']:
            print(entry['text'])
            filtered.append(entry)
            print('foundTicker', ticker)
    return foundTicker

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
    ids = []
    tokens = {}
    for coin in allCoins.json():
        if coin['symbol'] in lowerTokenArr:
            ids.append(coin['id'])
            tokens[f'${coin["symbol"].upper()}'] = coin['id']
    returnValue = {}
    if len(ids) > 0:
        params = {'ids': ','.join(ids) , 'vs_currencies': 'usd' }
        price = requests.get(coingeckoUrl + '/simple/price', params=params)
        logger.printError(price)
        response = price.json()
        for symbol, tokenId in tokens.items():
            returnValue[symbol] = {}
            returnValue[symbol]['usd'] = response[tokenId]['usd']
            returnValue[symbol]['time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    for coin in lowerTokenArr:
        upperCoin = f'${coin.upper()}' 
        if upperCoin not in list(dict.fromkeys(returnValue)):
            returnValue[upperCoin] = {'usd': 'no_price'}
    return returnValue;

