import re
import logger
import requests
import json
from datetime import datetime, timedelta 


f = open('noiseTickers.json')
noise = json.load(f)
coingeckoUrl = 'https://api.coingecko.com/api/v3'


def filterForTokens(data):
    allCoins = requests.get(coingeckoUrl + '/coins/list')
    logger.printError(allCoins)
    regex = re.compile(r'([\$\#]{1}[A-Za-z0-1]{2,})')
    filtered = []
    for entry in data:
        entry['text'] = __sanitizeText(entry['text'])
        if match := regex.findall(entry['text']):
            match.extend(__checkMentionsForTokens(entry, allCoins))
            __extractTicker(entry, match, filtered, allCoins)
        elif 'retweet' in entry:
            if match := regex.findall(entry['retweet']):
                __extractTicker(entry, match, filtered, allCoins)
    return filtered

def __sanitizeText(data):
    data = data.replace('\n', ' ')
    data = re.sub(r'(https:\/\/t\.co\/)([A-Za-z0-9]*)', ' ', data)
    return data

def __checkMentionsForTokens(data, allCoins):
    result = list()
    regex = re.compile(r'@(\S*)')
    if match := regex.findall(data['text']):
        lowerCase = list()
        for finding in match:
            lowerCase.append(finding.lower())
            for coin in allCoins.json():
                if coin['name'].lower() in lowerCase:
                    result.append(coin['symbol'])
    return result


# Might be useful later on
def __checkForToken(entry, filtered, allCoins):
    foundTicker = []
    for ticker in allCoins.json():
        if ticker['name'] in entry['text']:
            filtered.append(entry)
    return foundTicker

def __extractTicker(entry, match, filtered, allCoins):
    replacedMatches = []
    for ticker in match:
        rawTicker = ticker.replace('#', '').replace('$', '')
        if rawTicker.upper() not in noise:
            replacedMatches.append(rawTicker)
    if len(replacedMatches) > 0:
        noDuplicateList = list(dict.fromkeys(replacedMatches))
        entry['token_prices'] = __getTokenPrice(noDuplicateList, allCoins)
        filtered.append(entry)

def __getTokenPrice(tokenArr, allCoins):
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
            currentPrice = response[tokenId]['usd']
            returnValue[symbol] = {}
            returnValue[symbol]['seven_delta'] = __extractSevenDayDelta(tokenId, currentPrice)
            returnValue[symbol]['usd'] = currentPrice
            returnValue[symbol]['time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    for coin in lowerTokenArr:
        upperCoin = f'${coin.upper()}' 
        if upperCoin not in list(dict.fromkeys(returnValue)):
            returnValue[upperCoin] = {'usd': 'no_price'}
    return returnValue;

def __extractSevenDayDelta(tokenId, currentPrice):
    sevenDays = (datetime.now() - timedelta(weeks=1)).strftime('%d-%m-%Y')
    historyParams = { 'date': sevenDays }
    sevenDayPriceResponse = requests.get(coingeckoUrl + '/coins/' + tokenId + '/history', params=historyParams).json()
    if 'market_data' in sevenDayPriceResponse:
        sevenDayPrice = sevenDayPriceResponse['market_data']['current_price']['usd']
        priceDelta = '{:.2%}'.format((currentPrice - sevenDayPrice) / sevenDayPrice)
        return priceDelta

