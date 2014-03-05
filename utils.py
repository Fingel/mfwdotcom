import json
from urllib2 import urlopen
from urllib import quote_plus


def get_location_data(app, request):
    ip = None
    data = None
    if app.config['DEBUG'] is True:
        ip = app.config['FAKEIP']
    else:
        ip = request.remote_addr
    if ip is not None:
        try:
            response = json.load(urlopen("http://freegeoip.net/json/" + ip, None, 4))
            data = {"mode": "latlng", "lat": str(response['latitude']), "lng": str(response["longitude"])}
        except:
            try:
                #God this API is so innacurate.
                response = json.load(urlopen("http://api.ipinfodb.com/v3/ip-city/?key="
                    + app.config['IPINFODB'] + "&ip=" + ip + "&format=json", None, 7))
                data = {"mode": "latlng", "lat": response['latitude'], "lng": response["longitude"]}
            except:
                raise OutOfApisError("Out of geolocation apis")
    return data


def get_current_weather(location):
    if location['mode'] == 'latlng':
        url = "http://api.openweathermap.org/data/2.5/weather?lat=" + location['lat'] + "&lon=" + location['lng']
    else:
        city = quote_plus(location['city'])
        region = quote_plus(',' + location['region_code']) if location.get('region_code') else ''
        url = "http://api.openweathermap.org/data/2.5/find?q=%s%s&mode=json" % (city, region)
    try:
        data = json.load(urlopen(url))
        if location['mode'] == 'search' or location['mode'] == 'ipaddr':
            data = data['list'][0]
        temperature = kelvin_to_f(data['main']['temp'])
        code = data['weather'][0]['id']
        w_city = data['name']
    except:
        raise ValueError
    return (temperature, get_weather_type(code), w_city)


def get_forecast(location):
    forecast = []
    if location['mode'] == 'latlng':
        url = "http://api.openweathermap.org/data/2.5/forecast/daily?lat=" + location['lat'] + "&lon=" + location['lng']
    else:
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
            "min": kelvin_to_f(d["temp"]["min"]),
            "max": kelvin_to_f(d["temp"]["max"]),
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


class OutOfApisError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
