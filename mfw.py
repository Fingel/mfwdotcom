from flask import Flask
from flask import render_template, request
from utils import get_location_data, get_current_weather, get_forecast, OutOfApisError
from random import choice
from flavor_text import flavor_text

app = Flask(__name__)
app.config.from_object('settings')


@app.route('/')
def index():
    lat_long = request.args.get('latlng', '').replace('#', '')
    searchword = request.args.get('loc', '').replace('#', '')
    if lat_long:
        split_lat_long = lat_long.split(',')
        location = {'mode': 'latlng', 'lat': split_lat_long[0], 'lng': split_lat_long[1]}
    elif searchword:
        split_word = searchword.split(',')
        location = {'mode': 'search', 'city': split_word[0]}
        if len(split_word) > 1:
            location['region_code'] = split_word[1]
    else:
        try:
            location = get_location_data(app, request)
        except OutOfApisError:
            return render_template('index.html', error="You're a hard person to find!")
    try:
        temp, weather, city = get_current_weather(location)
        forecast = get_forecast(location)
    except ValueError:
            return render_template('index.html', error="Can't find that fucking place!")
    return render_template('index.html', weather=weather, temp=temp, forecast=forecast, city=city)


@app.template_filter('flavor_text')
def flavor_text_filter(s):
    return choice(flavor_text[s])

if __name__ == '__main__':
    app.run()
