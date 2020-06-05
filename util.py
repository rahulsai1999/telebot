import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
from joblib import load
import pickle
from sklearn.preprocessing import PolynomialFeatures
import sys
import os

data = pd.read_csv("apy.csv")


def return_crops(state, dis, season):
    state_dis_path = os.path.join(os.getcwd(), "JSON/state_dis_loc.json")
    seasonwise_path = os.path.join(os.getcwd(), "JSON/SeasonwiseCrops.json")
    savedModel_path = os.path.join(os.getcwd(), "JSON/SavedModelInfo.json")
    produceInfo_path = os.path.join(os.getcwd(), "JSON/ProduceInfo.json")

    with open(state_dis_path) as json_file:
        StateDisList = json.load(json_file)
    with open(seasonwise_path) as json_file:
        SeasonWiseCrops = json.load(json_file)
    with open(savedModel_path) as json_file:
        SavedModelInfo = json.load(json_file)
    with open(produceInfo_path) as json_file:
        ProduceInfo = json.load(json_file)

    SeasonList = ["Rabi", "Autumn", "Kharif", "Summer", "Whole Year", "Winter"]

    # Code to fetch Weather Data on basis of location
    req_f = "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=23199ca3783649b7868111655202505&q="
    Lat_Long = str(StateDisList[state][dis][0]) + \
        ',' + str(StateDisList[state][dis][1])
    req_e = "&format=json&mca=yes"
    resp = requests.get(req_f + Lat_Long + req_e)
    res = dict(resp.json())

    fil_resp = res['data']['ClimateAverages'][0]['month']
    temp = []
    rain = []
    for i in range(0, 12):
        temp.append((float(fil_resp[i]['avgMinTemp']) +
                     float(fil_resp[i]['absMaxTemp']))/2)
        rain.append(float(fil_resp[i]['avgDailyRainfall']) * 30)

    temp_input = 0
    rain_input = 0
    if(season == "Rabi"):
        temp_input = (temp[0] + temp[1] + temp[2] +
                      temp[9] + temp[10] + temp[11])/6
        rain_input = (rain[0] + rain[1] + rain[2] +
                      rain[9] + rain[10] + rain[11])/6
    elif(season == "Autumn"):
        temp_input = (temp[8] + temp[9] + temp[10] + temp[11])/4
        rain_input = (rain[8] + rain[9] + rain[10] + rain[11])/4
    elif(season == "Kharif"):
        temp_input = (temp[6] + temp[7] + temp[8] + temp[9])/4
        rain_input = (rain[6] + rain[7] + rain[8] + rain[9])/4
    elif(season == "Summer"):
        temp_input = (temp[4] + temp[5] + temp[6] + temp[7] + temp[8])/5
        rain_input = (rain[4] + rain[5] + rain[6] + rain[7] + rain[8])/5
    elif(season == "Whole Year"):
        temp_input = sum(temp)/12
        rain_input = sum(rain)/12
    elif(season == "Winter"):
        temp_input = (temp[0] + temp[1] + temp[2] + temp[11])/4
        rain_input = (rain[0] + rain[1] + rain[2] + rain[11])/4

    # Making the input feature vector and Scaling it using Standard Scalar
    scaler_path = os.path.join(os.getcwd(), "stdScaler")
    dbfile = open(scaler_path, 'rb')
    std_scaler = pickle.load(dbfile)
    dbfile.close()
    inp = np.array([StateDisList[state][dis][0], StateDisList[state]
                    [dis][1], rain_input, temp_input])
    inp = inp.reshape(1, -1)
    input_feature = std_scaler.transform(inp)

    # Evaluation using trained and saved models
    crop_list = SeasonWiseCrops[season]
    ScoredList = []
    for crop in crop_list:

        if crop in SavedModelInfo:
            result = 0
            count = 0
            score = 0
            for i in range(1, len(SavedModelInfo[crop])):
                model_path = SavedModelInfo[crop][i][0].split('/')[-1]
                model_path = os.path.join(
                    os.getcwd(), "Saved_Model", model_path)
                model_file = open(model_path, 'rb')
                model = pickle.load(model_file)
                model_file.close()
                if('POLY' in model_path):
                    polynomial_features = PolynomialFeatures(degree=2)
                    input_feat = polynomial_features.fit_transform(
                        input_feature)
                    res = model.predict(input_feat)
                    if(res > 0):
                        result += res
                        count += 1
                else:
                    res = model.predict(input_feature)
                    if(res > 0):
                        result += res
                        count += 1
            if(count != 0):
                score = float(result)/float(count)
                score = score/ProduceInfo[crop]['Avg']
            if(score > 10):
                score = score * \
                    ProduceInfo[crop]['Avg'] / ProduceInfo[crop]['Max']
            ScoredList.append([score, crop])

    ScoredList.sort(reverse=True)

    for i in range(0, len(ScoredList)):
        if(ScoredList[i][0] <= 20):
            break
    ScoredList = ScoredList[i:]
    returnstr = "Crops Recommended to grow in your area:"
    l = min(10, len(ScoredList))
    for i in range(0, l):
        returnstr = returnstr + "\n" + str(i+1) + ". " + str(ScoredList[i][1])
    return returnstr


def start_message(bot, chat_id, msg_id):
    bwelcome = """Welcome to Krishi bot, the bot can help in many ways.
    \nAvailable Commands:
    \n/weather - to know the current weather conditions
    \n/pumpOn - to turn on the pump 
    \n/pumpOff - to turn off the pump
    \nWhat is the price of {} - to know the price of a commodity
    \nWhat are the popular crops in {} - to visualise the amount of crops in specified area
    \nWhat are the viable crops in {} - to get the most viable crops in this area """
    bot.sendMessage(chat_id=chat_id, text=bwelcome, reply_to_message_id=msg_id)


def viableCrops(bot, chat_id, msg_id):
    bot.sendMessage(chat_id=chat_id, text=return_crops(
        "Tamil Nadu", "Kanchipuram", "Summer"))


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
    url = "https://api.openweathermap.org/data/2.5/weather?q=Chennai&appid=e64631cab1fe775900d1a6a2b809eda6"
    r = requests.get(url)
    r = r.json()
    weather = format(int(r["main"]["temp"])-273.16, '.1f') + chr(176) + "C"
    parameters = ["Location: ", "Current Temperature: ",
                  "Humidity: ", "Description: ", "Pressure: "]
    actuals = [str(r["name"]), weather, str(
        r["main"]["humidity"]), str(r["weather"][0]["description"]).title(), str(r["main"]["pressure"])]
    units = ["", "", "%", "", "psi"]

    fin = ""
    for i in range(len(parameters)):
        fin = fin+parameters[i]+actuals[i]+units[i]+"\n"

    bot.sendMessage(chat_id=chat_id, text=fin, reply_to_message_id=msg_id)


def get_chart(bot, chat_id, msg_id, district, limit):
    state = data[(data['District_Name'] == "Kanchipuram")
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


def default_message(bot, chat_id, msg_id):
    text_h = "Please try accepted commands"
    bot.sendMessage(chat_id=chat_id, text=text_h, reply_to_message_id=msg_id)
