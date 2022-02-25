import numpy as np
import pickle
import ast
import random

import pandas as pd
import plotly
import plotly.graph_objects as go
import json

from flask import Flask, request, render_template

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


@app.route('/sample_page', methods=['GET', 'POST'])
def home():
    data = pd.read_csv("jupyter/test_data.csv")
    # import chart as JSON Object
    chart_from_python = my_plot(data, "liveness")
    # pass the JSON Chart object
    # into the front end
    return render_template("sample_page.html", chart_for_html=chart_from_python)


def my_plot(data, plot_var):
    data_plot = go.Scatter(x=list(range(data.shape[0])), y=data[plot_var], line=dict(color="#CE285E", width=2))
    layout = go.Layout(title=dict(text="This is a Line Chart of Variable" + " " + str(plot_var), x=0.5),
                       xaxis_title="Record Number", yaxis_title="Values"
                       )
    fig = go.Figure(data=data_plot, layout=layout)
    # This is conversion step...
    fig_json = fig.to_json()
    graphJSON = json.dumps(fig_json, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == "__main__":
    app.run(debug=True)
