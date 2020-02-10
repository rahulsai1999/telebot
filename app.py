from flask import Flask, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import re
import os
import telegram
import requests

TOKEN = os.environ['token']
url = os.environ['url']
bot = telegram.Bot(token=TOKEN)
model = load_model("model.h5")

app = Flask(__name__)


def load_image(filename):
    img = load_img(filename, grayscale=True, target_size=((28, 28)))
    img = img_to_array(img)
    img = img.reshape(1, 28, 28, 1)
    img = img.astype('float32')
    img = img / 255.0
    return img


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    file_arr = update.message.photo
    file_m = file_arr[-1]
    file_id = file_m.file_id
    print(file_id)
    bot.get_file(file_id=file_id).download(custom_path="images/" + file_id)

    # # process the photo here
    # filename = "images/" + file_id
    # img = load_image(filename)
    # digit = model.predict_classes(img)

    # delete photo from directory
    os.remove('images/' + file_id)

    # send user output from here
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    bot.sendMessage(chat_id=chat_id, text="Aristolochia bractiata - 78.5%",
                    reply_to_message_id=msg_id)
    
    # bot.send_photo(chat_id=chat_id, photo=file_id, reply_to_message_id=msg_id)

    text=update.message.text.encode('utf-8').decode()
    if text=='/weather':
        x=telegram.Location()
        url="http://api.openweathermap.org/data/2.5/weather?lat="+x.latitude+"&lon="+x.longitude+"&appid=e64631cab1fe775900d1a6a2b809eda6";
        r=requests.get(url)
        r=r.json()
        print(r["main"])
        

    # text = update.message.text.encode('utf-8').decode()
    # print("got text message :", text)
    # if text == "/start":
    #     bot_welcome = """Welcome to coolAvatar bot, the bot is using the service from http://avatars.adorable.io/ to
    #     generate cool looking avatars based on the name you enter so please enter a name and the bot will reply with
    #     an avatar for your name. """
    #     bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    #
    # else:
    #     try:
    #         # clear the message we got from any non alphabets
    #         text = re.sub(r"\W", "_", text)
    #         url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
    #         # note that you can send images by url and telegram will fetch it for you
    #         bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
    #     except Exception:
    #         bot.sendMessage(chat_id=chat_id,
    #                         text="There was a problem in the name you used, please enter different name",
    #                         reply_to_message_id=msg_id)

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=url, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/files', methods=['GET'])
def get_files():
    x = ""
    for root, dirs, files in os.walk("images"):
        for filename in files:
            x = x + filename + "<br>"
    return x


@app.route('/')
def index():
    return 'Server OK'


if __name__ == '__main__':
    app.run(threaded=True)
