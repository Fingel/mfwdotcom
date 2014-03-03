from flask import Flask
from flask import render_template, request
from utils import get_location_data, get_current_weather, get_forecast
from random import choice
from flavor_text import flavor_text

app = Flask(__name__)
app.config.from_object('settings')


@app.route('/')
def index():
    searchword = request.args.get('loc', '')
    if searchword:
        split_word = searchword.split(',')
        if len(split_word) > 1:
            location = {'city': split_word[0], 'region_code': split_word[1]}
        else:
            location = {'city': split_word[0]}
    else:
        location = get_location_data(app, request)
    try:
        temp, weather = get_current_weather(location)
        forecast = get_forecast(location)
    except ValueError:
        return render_template('index.html', error="Can't find that fucking place!")
    return render_template('index.html', location=location, weather=weather, temp=temp, forecast=forecast)


@app.template_filter('flavor_text')
def flavor_text_filter(s):
    return choice(flavor_text[s])

if __name__ == '__main__':
    app.run()
