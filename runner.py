import requests
import json
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

USERNAME = input("Type in your asianodds username: ")
PASSWORD = input("Type in your password (MD5 hash of password): ")
TELEGRAM_BOT_TOKEN = input("Type in your telegram bot token: ")
telegram_userID = input("Type in your telegram userId that recieves the notifications")

URL = ''
TOKEN = ''

USERNAME = input("Type in your asianodds username: ")
PASSWORD = input("Type in your password (MD5 hash of password): ")
TELEGRAM_BOT_TOKEN = input("Type in your telegram bot token: ")
#telegram_userID = input("Type in your telegram userId that recieves the notifications")




# If any substring in substrings is a substring in string, return true
# else false
def contains(string, substrings):
    bcontains = False
    for i in range(len(substrings)):
        if(substrings[i] in string):
            bcontains = True
    return bcontains

# Authenticating login to be able to get games
def setup():
    headers = {
        'Accept': 'application/json',
    }

    params = (
        ('username', USERNAME ),
        ('password', PASSWORD ),
    )

    response = requests.get('https://webapi.asianodds88.com/AsianOddsService/Login', headers=headers, params=params)
    print("Login request sent")
    print(response.json())

    global TOKEN

    key = response.json()["Result"]["Key"]
    TOKEN = response.json()["Result"]["Token"]
    URL = response.json()["Result"]["Url"]# + "/Register"

    headers = {
        'Accept': 'application/json',
        'AOKey': key,
        'AOToken': TOKEN
    }

    params = (
        ('username', USERNAME ),
    )

    response = requests.get(URL + "/Register", headers = headers, params = params)

    print("Authenticating")
    print(response.json())


@sched.scheduled_job('interval',  seconds = 40 ) # runs every 40 seconds
def runbot():
    headers = {
        'Accept': 'application/json',
        'AOToken': TOKEN
    }

    params = (
        ('sportsType', 1),
        ('marketTypeId', 1), #0 : Live Market 1 : Today Market 2 : Early Market
        ('bookies', 'ALL'),
        ('leagues', 'ALL'),
        #('since', 1580259445000)

    )
    #url = 'https://webapitest.asianodds88.com/AsianOddsService/getMatches'

    matchIds = []
    leagues = ["reykjavik","iceland","ICELAND","REYKJAVIK","FOTBOLTI","fotbolti","FAXAFLOAMOT","FOTBOLTI.NET","FAXAFLOI"] # strings to match
    response = requests.get(URL + "/getMatches",headers = headers, params = params)
    print("Fetched games")
    print(response.json())
    if response.json()["Code"] != -1 and response.json()["Result"] is None:
        matches = []
        print(response.json())
    elif response.json()["Code"] == -1:
        print(response.json())
        print("Restarting bot")
        setup()
        runbot()
    else:
        matches = response.json()["Result"]["EventSportsTypes"][0]["Events"]
    print("Number of matches:", len(matches))
    print("Fetched:" ,time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()) )
    for game in matches:
        if contains(game["LeagueName"],leagues):
            print("Got match! name:", game["LeagueName"],"Leagues to match:",leagues)
            gameId = game["MatchId"]
            print("id:" , gameId)
            print("matched id's", matchIds)
            if gameId not in matchIds:
                print("game not in database!")
                print("LeagueName", game["LeagueName"])
                matchIds.append(game["MatchId"])

                text = game["Home"] + " vs " + game["Away"] + " is just in!"
                
                cmd = 'curl --data chat_id="456563394" --data "text=' + text + '" "https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage" '
                os.system(cmd)
                print("Sent notification")

                cmd = 'curl --data chat_id="845105397" --data "text=' + text + '" "https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage" '
                os.system(cmd)
                print("Sent notification")

    if len(matchIds) > 30:
        matchIds.pop(0) # Keep matchids max 30 items

setup()
runbot()
sched.start()
