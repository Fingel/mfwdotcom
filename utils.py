import json
from urllib2 import urlopen
from urllib import quote_plus


def get_location_data(app, request):
    ip = None
    data = {}
    if app.config['DEBUG'] is True:
        ip = app.config['FAKEIP']
    else:
        ip = request.remote_addr
    if ip is not None:
        try:
            data = json.load(urlopen("http://freegeoip.net/json/" + ip))
        except:
            raise ValueError
    return data


def get_current_weather(location):
    city = quote_plus(location['city'])
    region = quote_plus(',' + location['region_code']) if location.get('region_code') else ''
    url = "http://api.openweathermap.org/data/2.5/find?q=%s%s&mode=json" % (city, region)
    try:
        data = json.load(urlopen(url))
        data = data['list'][0]
    except:
        raise ValueError
    temperature = (data['main']['temp'] - 273.15) * 1.8000 + 32.00
    code = data['weather'][0]['id']
    return (temperature, get_weather_type(code))


def get_forecast(location):
    forecast = []
    city = quote_plus(location['city'])
    region = quote_plus(',' + location['region_code']) if location.get('region_code') else ''
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=%s%s&mode=json" % (city, region)
    try:
        data = json.load(urlopen(url))
        data = data['list'][:3]
    except:
        raise ValueError
    for d in data:
        forecast.append({
            "temp": kelvin_to_f(d["temp"]["day"]),
            "weather": get_weather_type(d["weather"][0]["id"])
        })
    return forecast


def kelvin_to_f(kelvin):
    return (kelvin - 273.15) * 1.8000 + 32.00


def get_weather_type(code):
    if code < 300:
        return "thunder"
    if code < 501:
        return "light-rain"
    if code < 600:
        return "rain"
    if code < 700:
        return "snow"
    if code < 800:
        return "cloudy"
    if code < 900:
        if code == 800:
            return "sunny"
        else:
            return "cloudy"
    return "unknown"
