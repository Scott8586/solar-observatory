#!/usr/bin/env python3

import os
import time
import json
import requests
import threading
from requests.auth import HTTPDigestAuth
from prometheus_client import start_http_server, Gauge

host = os.getenv('WEEWX_HOST')
#host = "192.168.35.157"

current_gauges = {
    'inTemp': Gauge('temperature_inside', 'Inside Temperature'),
    'outTemp': Gauge('temperature_outside', 'Outside Temperature'),
    'inHumidity': Gauge('humidity_inside', 'Inside Humidity'),
    'outHumidity': Gauge('humidity_outside', 'Outside Humidity'),
    'solarRadiation': Gauge('solar_radiation', 'Solar Radiaion'),
    'pm2_5': Gauge('particulate_matter', 'Particulate Matter 2.5'),
    'windchill': Gauge('wind_chill', 'Wind Chill'),
    'heatindex': Gauge('heat_index', 'Heat Index'),
    'dewpoint': Gauge('dew_point', 'Dew Point'),
    'barometer': Gauge('barometer', 'Barometer'),
    'windSpeed': Gauge('wind_speed', 'Wind Speed'),
    'windGust': Gauge('wind_gust', 'Wind Gust'),
    'windDir': Gauge('wind_direction', 'Wind Direction'),
    'rainRate': Gauge('rain_rate', 'Rain Rate'),
    'cloudbase': Gauge('cloud_base', 'Cloud Base'),
}

def scrape_weather_json():
    url = 'http://%s/weewx/daily.json' % host
    data = requests.get(url).json()
    current = data['current']
    # print(current)
    for key in ['inTemp', 'outTemp', 'inHumidity', 'outHumidity', 'solarRadiation', 'pm2_5', 'windchill', 'heatindex', 'dewpoint', 'barometer', 'windSpeed', 'windGust', 'windDir', 'rainRate', 'cloudbase']:
        value = current.get(key)
        if value is not None:
            current_gauges[key].set(value)

def main():
    start_http_server(8001)
    counter = 0
    while True:
        counter += 1
        if counter % 1 == 0: 
            try:
                scrape_weather_json()
            except Exception as e:
                print('Exception fetching weewx weather data: %s' % e)
            counter = 0
        time.sleep(60)

if __name__ == '__main__':
    main()
