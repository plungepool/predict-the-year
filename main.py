import numpy as np
import pickle
import ast
import random
import pandas as pd
import plotly
import plotly.express as px
import json
import datetime as dt
from dash import html, dcc

from flask import Flask, request, render_template
from flask_caching import Cache

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

TIMEOUT = 60

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


@cache.memoize(timeout=TIMEOUT)
def query_data():
    # This could be an expensive data querying step
    np.random.seed(0)  # no-display
    df = pd.DataFrame(
        pd.read_csv("jupyter/test_data.csv")
    )
    now = dt.datetime.now()
    df['time'] = [now - dt.timedelta(seconds=5*i) for i in range(34301)]
    return df.to_json(date_format='iso', orient='split')


def dataframe():
    return pd.read_json(query_data(), orient='split')


@app.route('/graphs', methods=['GET', 'POST'])
def home():
    data = dataframe()
    # import chart as JSON Object
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
    fig = px.line(x=years, y=avg_tempos[0:100], title='Average tempo by year',
                  labels={
                      "x": "Year",
                      "y": "Average Tempo (BPM)"
                  }
                  )
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
    fig = px.line(x=years, y=avg_loudness[0:100], width=800, height=400, title='Average loudness by year',
                  labels={
                      "x": "Year",
                      "y": "Average Loudness (LUFS)"
                  }
                  )
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
    fig = px.line(x=years, y=avg_acousticness[0:100], title='Average acousticness by year',
                  labels={
                      "x": "Year",
                      "y": "Average Acousticness"
                  }
                  )
    # Convert to JSON object
    fig_json = fig.to_json()
    graphJSON = json.dumps(fig_json, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == "__main__":
    app.run(debug=True)
