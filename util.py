import requests
import json


def start_message(bot, chat_id, msg_id):
    bwelcome = """Welcome to Krishi bot, the bot can help in many ways.
    \nAvailable Commands: 
    \n/weather - to know the current weather conditions
    \nWhat is the price of {} - to know the price of a commodity
    \nWhat are the popular crops in my area - to visualise the amount of crops in area"""
    bot.sendMessage(chat_id=chat_id, text=bwelcome, reply_to_message_id=msg_id)


def sendMarketInfo(bot, chat_id, msg_id, text):
    spl = text.split(" ")[5:]
    crop = ' '.join(spl).title().strip()
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd0000011b09046c709041a44b5e0d909f7db4a8&format=json&offset=1&limit=637"
    r = requests.get(url)
    r = r.json()

    records = r["records"]
    for i in records:
        if crop in i.values():
            text_here = "State: "+i["state"]+"\nMarket: " + \
                i["district"] + "\nPrice: "+i["modal_price"]
            bot.sendMessage(chat_id=chat_id, text=text_here,
                            reply_to_message_id=msg_id)


def temperature_api(bot, chat_id, msg_id):
    url = "https://api.openweathermap.org/data/2.5/weather?q=Vellore&appid=e64631cab1fe775900d1a6a2b809eda6"
    r = requests.get(url)
    r = r.json()
    weather = format(int(r["main"]["temp"])-273.16, '.1f') + chr(176) + "C"
    parameters = ["Location: ", "Current Temperature: ",
                  "Humidity: ", "Description: ", "Elevation: ", "Pressure: "]
    actuals = [str(r["name"]), weather, str(
        r["main"]["humidity"]), str(r["weather"]["description"]), str(r["main"]["grnd_level"]), str(r["main"]["pressure"])]
    units = ["", "", "%", "", "m", "psi"]

    fin = ""
    for i in range(len(parameters)):
        fin = fin+parameters[i]+actuals[i]+units[i]+"\n"

    bot.sendMessage(chat_id=chat_id, text=fin, reply_to_message_id=msg_id)


def default_message(bot, chat_id, msg_id):
    text_h = "Please try accepted commands"
    bot.sendMessage(chat_id=chat_id, text=text_h, reply_to_message_id=msg_id)
