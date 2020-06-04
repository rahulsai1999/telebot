from flask import Flask, request
from util import sendMarketInfo, temperature_api, default_message, start_message, get_chart

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
    location = update.message.location

    # image processing done in this block

    if len(update.message.photo) != 0:
        file_id = update.message.photo[-1].file_id
        x = bot.getFile(file_id=file_id)
        bot.sendMessage(
            chat_id=chat_id, text="Aristolochia bractiata - 78.5%", reply_to_message_id=msg_id)

    # text based processing done in this block
    else:
        text = update.message.text.encode('utf-8').decode()

        print("got text message :", text)

        if text == "/start":
            start_message(bot, chat_id, msg_id)

        elif text == "/weather":
            temperature_api(bot, chat_id, msg_id)

        elif text.lower().startswith("what is the price of"):
            sendMarketInfo(bot, chat_id, msg_id, text)

        elif text.lower().startswith("what are the popular crops"):
            dist = text.strip().split(" ")[6]
            dist = dist.upper()
            get_chart(bot, chat_id, msg_id, dist, 10)
        else:
            default_message(bot, chat_id, msg_id)

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
