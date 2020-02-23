import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


data = pd.read_csv("apy.csv")


def get_chart(bot, chat_id, msg_id, district, limit):
    state = data[(data['District_Name'] == district)
                 & (data["Crop_Year"] == 2013)]
    state = state.fillna(0)

    state.sort_values(by=['Production'], inplace=True, ascending=False)

    crop_name = state['Crop'].values.tolist()[:limit]
    prod = state['Production'].values.tolist()[:limit]

    fig1, ax1 = plt.subplots()
    ax1.pie(prod, labels=crop_name, autopct='%1.1f%%')
    ax1.axis('equal')
    plt.savefig('./images/temp.png')
    bot.send_photo(chat_id=chat_id, photo=open('images/temp.png', 'rb'),
                   reply_to_message_id=msg_id)
