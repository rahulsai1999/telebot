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

    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)
    if text == "/start":
        bot_welcome = """Welcome to coolAvatar bot, the bot is using the service from http://avatars.adorable.io/ to 
        generate cool looking avatars based on the name you enter so please enter a name and the bot will reply with 
        an avatar for your name. """
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    
    elif text=="/temp":
        x=telegram.Location()
        url="http://api.openweathermap.org/data/2.5/weather?lat="+x.latitude+"&lon="+x.longitude+"&appid=e64631cab1fe775900d1a6a2b809eda6";
        r=requests.get(url)
        r=r.json()
        r=json.loads(r)
        weather=r["main"]["temp"]
        bot.sendMessage(chat_id=chat_id, text=weather, reply_to_message_id=msg_id)


    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # note that you can send photos by url and telegram will fetch it for you
            bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
        except Exception:
            bot.sendMessage(chat_id=chat_id,
                            text="There was a problem in the name you used, please enter different name",
                            reply_to_message_id=msg_id)

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