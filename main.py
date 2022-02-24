from flask import Flask, request, render_template
import numpy as np
import pickle
import ast
import random
from pyexpat import model
import os
import pandas as pd
import sklearn

app = Flask(__name__)


# Ties a page on your website to a function
# @ signifies a decorator - way to wrap a function and modify its behavior
@app.route('/')
def index():
    song_list = 'jupyter/test_data.csv'
    rand_songs = getRandomSongs(song_list)
    return render_template("index.html", rand_songs=rand_songs)

def getRandomSongs(song_list):
    rand_songs = []
    for i in range(5):
        file = open(song_list, 'r', encoding="utf-8")
        random.seed()
        song_id = random.randrange(3, 137206, 4)
        index = 3
        for row in file:
            if index == song_id:
                rand_songs.append(list(row.split(",")))
            index += 2
    return rand_songs

def ValuePredictor(to_predict_list):
    to_predict = np.array(to_predict_list[1:15]).reshape(1, 14)
    loaded_model = pickle.load(open("jupyter/model.pkl", "rb"))
    result = loaded_model.predict(to_predict)
    return result[0]


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = ast.literal_eval(to_predict_list.get('song_select'))
        result = ValuePredictor(to_predict_list)

        Tv = int(to_predict_list[15]) - 1921
        Ov = int(result) - 1921
        percent_accurate = 100 - abs(((Tv - Ov) / Tv) * 100)

        prediction = 'Prediction - ' + str(int(result))
        actual = 'Actual - ' + str(int(to_predict_list[15]))
        accuracy = 'Percent accuracy - ' + str(percent_accurate)[:5] + "%"
        songartist = to_predict_list[18] + " - " + to_predict_list[16]

        return render_template("result.html", to_predict_list=to_predict_list, prediction=prediction,
                               actual=actual, accuracy=accuracy, songartist=songartist)


if __name__ == "__main__":
    app.run(debug=True)
