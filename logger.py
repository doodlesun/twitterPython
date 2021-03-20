import requests

def printError(request):
    try:
        request.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
