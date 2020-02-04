import os
import requests
import time


def telegram_bot_sendtext(bot_message):

    bot_token = '1047851159:AAFrVRnoCisvG2wsaL3k6UD5P1IZaaBSikY'
    bot_chatID = '851738746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)


    return response.json()
bot_token = '1047851159:AAFrVRnoCisvG2wsaL3k6UD5P1IZaaBSikY'
messageids = []
updates = 'https://api.telegram.org/bot' + bot_token + '/getUpdates'
while(True):

    response = requests.get(updates)
    print(response.json())
    #if response.json()[]
    #print(telegram_bot_sendtext("Haltu kjafti"))
    time.sleep(10)
