from flask import Flask, request
import re
import os
import telegram
import requests
import json

TOKEN = os.environ['token']
url = os.environ['url']
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    if len(update.message.photo)!=0:
        file_id = update.message.photo[-1].file_id
        x=bot.getFile(file_id=file_id)
        bot.sendMessage(chat_id=chat_id, text="Aristolochia bractiata - 78.5%", reply_to_message_id=msg_id)


    text = update.message.text.encode('utf-8').decode()
    
    print("got text message :", text)
    
    if text == "/start":
        bot_welcome = """Welcome to Krishi bot, the bot can help in many ways. Start by typing /temp to know the current temperature."""
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    
    elif text=="/temp":
        url="https://api.openweathermap.org/data/2.5/weather?q=Vellore&appid=e64631cab1fe775900d1a6a2b809eda6"
        r=requests.get(url)
        r=r.json()
        weather=format(int(r["main"]["temp"])-273.16,'.1f') + chr(176) +"C"
        bot.sendMessage(chat_id=chat_id, text=weather, reply_to_message_id=msg_id)


    else:
        bot.sendMessage(chat_id=chat_id,text="Please try different command",reply_to_message_id=msg_id)

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=url, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return 'Server OK'


if __name__ == '__main__':
    app.run(threaded=True)