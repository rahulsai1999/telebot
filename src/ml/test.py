import requests
import json
import pandas as pd
import numpy as np
from joblib import load
import pickle
from sklearn.preprocessing import PolynomialFeatures
import sys
import os


def return_crops(state, dis, season):
    state_dis_path = os.path.join(os.getcwd(), "JSON\\state_dis_loc.json")
    seasonwise_path = os.path.join(os.getcwd(), "JSON\\SeasonwiseCrops.json")
    savedModel_path = os.path.join(os.getcwd(), "JSON\\SavedModelInfo.json")
    produceInfo_path = os.path.join(os.getcwd(), "JSON\\ProduceInfo.json")

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
    returnstr = "Crops Recommended to grow in", dis+', '+state, "in", season, "are:"
    l = min(10, len(ScoredList))
    for i in range(0, l):
        returnstr = returnstr + "\n" + str(i+1) + ScoredList[i][1]
    return returnstr;
