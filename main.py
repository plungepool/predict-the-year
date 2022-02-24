import random
from pyexpat import model

from flask import Flask, request, render_template
import os
import pandas as pd
import numpy as np
import pickle
import sklearn
import ast

app = Flask(__name__)


# Ties a page on your website to a function
# @ signifies a decorator - way to wrap a function and modify its behavior
@app.route('/')
def index():
    song_list = 'jupyter/test_data.csv'
    rand_songs = getRandomSongs(song_list)
    return render_template("index.html", rand_songs=rand_songs)

def ValuePredictor(to_predict_list):
    to_predict = np.array(to_predict_list).reshape(1, 14)
    loaded_model = pickle.load(open("jupyter/model.pkl", "rb"))
    result = loaded_model.predict(to_predict)
    return result[0]

def getRandomSongs(song_list):
    rand_songs = []
    for i in range(5):
        file = open(song_list, 'r', encoding="utf-8")
        random.seed()
        song_id = random.randrange(3, 137206, 4)
        index = 3
        for row in file:
            if index == song_id:
                rand_songs.append(list(row.split(",")))#rand_songs.append(list(row.split(","))[17][1])
            index += 2
    return rand_songs

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':

        if request.form.to_dict().get('song_select'):
            to_predict_list = request.form.to_dict()
            to_predict_list = ast.literal_eval(to_predict_list.get('song_select'))
            result = ValuePredictor(to_predict_list)
        else:
            to_predict_list = request.form.to_dict()
            to_predict_list = list(to_predict_list.values())
            # to_predict_list = list(map(int, to_predict_list))
            result = ValuePredictor(to_predict_list)

        if int(result) <= 1929:
            prediction = 'Roaring 20s! - ' + str(int(result))
        else:
            prediction = 'A different era! - ' + str(int(result))
        return render_template("result.html", prediction=prediction, to_predict_list=to_predict_list)


if __name__ == "__main__":
    app.run(debug=True)
