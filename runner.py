import requests
import json
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

USERNAME = str(input("Type in your asianodds username: "))
PASSWORD = str(input("Type in your password (MD5 hash of password): "))
TELEGRAM_BOT_TOKEN = str(input("Type in your telegram bot token: "))
TELEGRAM_USER_IDs = []
while(True):
    id = str(input('Type in telegram userID to send notifications to (type "done" if done): '))
    if id == "done":
        break;
    else:
        TELEGRAM_USER_IDs.append(id)
URL = ''
TOKEN = ''
matchIds = []

# If any substring in substrings is a substring in string, return true
# else false
def contains(string, substrings):
    bcontains = False
    for i in range(len(substrings)):
        if(substrings[i] in string):
            bcontains = True
    return bcontains

def createText(odds, handicap):
    odds_split = odds.split(";")
    text = "-----Handicap---- \n"
    text += " Home: " + handicap + "\n"
    text += "-------Odds------ \n"

    for i in odds_split[:-1]:
        a = i.split("=")
        text += a[0] + " "
        b = a[1].split(",")
        text += b[0] + " " + b[1] + "\n"
    return text
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
    global URL

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
        ('oddsFormat', '00'),
        #('since', 1580259445000)

    )
    #url = 'https://webapitest.asianodds88.com/AsianOddsService/getMatches'

    global matchIds
    leagues = ["reykjavik","iceland","ICELAND","REYKJAVIK","FOTBOLTI","fotbolti","FAXAFLOAMOT","FOTBOLTI.NET","FAXAFLOI"] # strings to match
    response = requests.get(URL + "/getFeeds",headers = headers, params = params)
    print("Fetched games")
    #print(response.json())
    if response.json()["Code"] != -1 and response.json()["Result"] is None:
        matches = []
        print(response.json())
    elif response.json()["Code"] == -1:
        print(response.json())
        print("Restarting bot")
        setup()
        runbot()
    else:
        #print(response.json()["Result"]["Sports"][0]["MatchGames"])
        matches = response.json()["Result"]["Sports"][0]["MatchGames"]
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

                text = game["HomeTeam"]["Name"] + " vs " + game["AwayTeam"]["Name"] + " just in! \n"
                odds = game["FullTimeHdp"]["BookieOdds"]
                handicap = game["FullTimeHdp"]["Handicap"]
                text += createText(odds, handicap)

                #Send notifications
                for userid in TELEGRAM_USER_IDs:
                    cmd = 'curl --data chat_id="' + userid +'"  --data "text=' + text + '" "https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage" '
                    os.system(cmd)
                    print("Sent notification")

    if len(matchIds) > 30:
        matchIds.pop(0) # Keep matchids max 30 items

setup()
runbot()
sched.start()
