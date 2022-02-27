import numpy as np
import pickle
import ast
import random
import pandas as pd
import plotly
import plotly.express as px
import json
import datetime as dt

from flask import Flask, request, render_template
from flask_caching import Cache

config = {
    "DEBUG": False,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

TIMEOUT = 60


@app.route('/')
def index():
    test_song_list = 'jupyter/test_data.csv'
    rand_songs = getRandomSongs(test_song_list)
    data = dataframe()
    # import charts as JSON Object
    tempo_year_chart = tempo_by_year(data)
    loudness_year_chart = loudness_by_year(data)
    acousticness_year_chart = acousticness_by_year(data)
    return render_template("index.html", rand_songs=rand_songs,
                           tempo_year_chart=tempo_year_chart,
                           loudness_year_chart=loudness_year_chart,
                           acousticness_year_chart=acousticness_year_chart)


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
        songartist = to_predict_list[16] + " - " + to_predict_list[17]

        return render_template("result.html", to_predict_list=to_predict_list, prediction=prediction,
                               actual=actual, accuracy=accuracy, songartist=songartist)


@cache.memoize(timeout=TIMEOUT)
def query_data():
    np.random.seed(0)
    df = pd.DataFrame(
        pd.read_csv("jupyter/data_SpotifyTop100PerYear.csv")
    )
    now = dt.datetime.now()
    df['time'] = [now - dt.timedelta(seconds=5*i) for i in range(169909)]
    return df.to_json(date_format='iso', orient='split')


def dataframe():
    return pd.read_json(query_data(), orient='split')


@app.route('/graphs', methods=['GET', 'POST'])
def home():
    data = dataframe()
    # import charts as JSON Object
    tempo_year_chart = tempo_by_year(data)
    loudness_year_chart = loudness_by_year(data)
    acousticness_year_chart = acousticness_by_year(data)
    # Pass to front end
    return render_template("graphs.html", tempo_year_chart=tempo_year_chart,
                           loudness_year_chart=loudness_year_chart,
                           acousticness_year_chart=acousticness_year_chart)


def tempo_by_year(data):
    avg_tempos = []
    years = range(1921, 2021)
    for i in years:
        file = data
        year = file.loc[file['year'] == i]
        tempos = year['tempo']
        tempos = pd.DataFrame(tempos)
        avg_tempos.append(float(pd.DataFrame.mean(tempos)))
    fig = px.line(x=years, y=avg_tempos[0:100], width=600, height=400,
                  labels={
                      "x": "Year",
                      "y": "Average Tempo (BPM)"
                  }
                  )
    fig.update_layout(title_text='Average tempo by year', title_x=0.5)
    # Convert to JSON object
    fig_json = fig.to_json()
    graphJSON = json.dumps(fig_json, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def loudness_by_year(data):
    avg_loudness = []
    years = range(1921, 2021)
    for i in years:
        file = data
        year = file.loc[file['year'] == i]
        loudnesses = year['loudness']
        loudnesses = pd.DataFrame(loudnesses)
        avg_loudness.append(float(pd.DataFrame.mean(loudnesses)))
    fig = px.line(x=years, y=avg_loudness[0:100], width=600, height=400,
                  labels={
                      "x": "Year",
                      "y": "Average Loudness (LUFS)"
                  }
                  )
    fig.update_layout(title_text='Average loudness by year', title_x=0.5)
    # Convert to JSON object
    fig_json = fig.to_json()
    graphJSON = json.dumps(fig_json, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def acousticness_by_year(data):
    avg_acousticness = []
    years = range(1921, 2021)
    for i in years:
        file = data
        year = file.loc[file['year'] == i]
        acousticnesses = year['acousticness']
        acousticnesses = pd.DataFrame(acousticnesses)
        avg_acousticness.append(float(pd.DataFrame.mean(acousticnesses)))
    fig = px.line(x=years, y=avg_acousticness[0:100], width=600, height=400,
                  labels={
                      "x": "Year",
                      "y": "Average Acousticness"
                  }
                  )
    fig.update_layout(title_text='Average acousticness by year', title_x=0.5)
    # Convert to JSON object
    fig_json = fig.to_json()
    graphJSON = json.dumps(fig_json, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == "__main__":
    app.run(debug=True)
