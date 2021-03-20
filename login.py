import requests
import yaml
import urllib.parse
import base64
import logger

authUrl = "https://api.twitter.com"

def authorization():
    with open("env.yaml", 'r') as stream:
        envs = yaml.safe_load(stream)
    basicAuth = login(envs['apiKey'], envs['apiKeySecret'])
    return fetchBearer(basicAuth)

def login(apiKey, apiKeySecret):
    keyEncoded = urllib.parse.quote_plus(apiKey)
    secretEncoded = urllib.parse.quote_plus(apiKeySecret)
    query = base64.b64encode(bytes(keyEncoded + ":" + secretEncoded, 'utf8'))
    return query.decode('utf8')

def fetchBearer(basicAuth):
    headers = {'Authorization': 'Basic ' + basicAuth, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    response = requests.post(authUrl + '/oauth2/token', headers=headers, data='grant_type=client_credentials')
    logger.printError(response)
    return response.json()['access_token']


