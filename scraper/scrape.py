#!/usr/bin/env python -f

import os
import time
import json
import requests
import threading
from requests.auth import HTTPDigestAuth
from prometheus_client import start_http_server, Gauge


host = os.getenv('ENVOY_HOST')
username = os.getenv('ENVOY_USER')
password = os.getenv('ENVOY_PASS')

#user = 'envoy'
auth = HTTPDigestAuth(username, password)
marker = b'data: '

inverter_period = int(os.getenv('INVERTER_PERIOD'))
production_period = int(os.getenv('PRODUCTION_PERIOD'))

serials = {

    122007058453: 'South',
    122007070980: 'South',
    122009090297: 'East',
    122009090314: 'East',
    122009090358: 'South',
    122009090470: 'East',
    122009090473: 'East',
    122009091799: 'East',
    122009092522: 'South',
    122009092985: 'East',
    122009100520: 'East',
    122009101008: 'East',
    122009101485: 'East',
    122009101595: 'East',
    122009101914: 'South',
    122009101919: 'East',
    122009102188: 'East',
    122009102189: 'East',
    122009102313: 'South',
    122009108321: 'East',
    202010015498: 'South',
    202010023216: 'West',
    202010023428: 'West',
    202010024508: 'South',
    202010025360: 'West',
    202010026555: 'South',
    202010026589: 'South',
    202010026755: 'South',
    202010027375: 'South',
    202010027455: 'West',
    202010027734: 'West',
    202010027743: 'West',
    202010027744: 'West',
    202010027771: 'West',
    202010027988: 'South',
    202010028299: 'West',
    202010028310: 'South',
    202010028406: 'West',

}


#stream_gauges = {
#    'p': Gauge('meter_active_power_watts', 'Active Power', ['type', 'phase']),
#    'q': Gauge('meter_reactive_power_watts', 'Reactive Power', ['type', 'phase']),
#    's': Gauge('meter_apparent_power_watts', 'Apparent Power', ['type', 'phase']),
#    'v': Gauge('meter_voltage_volts', 'Voltage', ['type', 'phase']),
#    'i': Gauge('meter_current_amps', 'Current', ['type', 'phase']),
#    'f': Gauge('meter_frequency_hertz', 'Frequency', ['type', 'phase']),
#    'pf': Gauge('meter_power_factor_ratio', 'Power Factor', ['type', 'phase']),
#}

production_gauges = {
    'activeCount': Gauge('production_active_count', 'Active Count', ['type']),
    'wNow': Gauge('power_now_watts', 'Active Count', ['type']),
    'whToday': Gauge('production_today_watthours', 'Total production today', ['type']),
    'whLastSevenDays': Gauge('production_7days_watthours', 'Total production last seven days', ['type']),
    'whLifetime': Gauge('production_lifetime_watthours', 'Total production lifetime', ['type']),
    'rmsCurrent': Gauge('production_rms_current', 'Production RMS Current', ['type']),
    'rmsVoltage': Gauge('production_rms_voltage', 'Production RMS Voltage', ['type']),
    'pwrFactor': Gauge('production_power_factor', 'Production Power Factor', ['type']),
}

consumption_gauges = {
    'wNow': Gauge('consumption_now_watts', 'Active Count', ['type']),
    'whToday': Gauge('consumption_today_watthours', 'Total consumption today', ['type']),
    'whLastSevenDays': Gauge('consumption_7days_watthours', 'Total consumption last seven days', ['type']),
    'whLifetime': Gauge('consumption_lifetime_watthours', 'Total consumption lifetime', ['type']),
    'rmsCurrent': Gauge('consumption_rms_current', 'Consumption RMS Current', ['type']),
    'rmsVoltage': Gauge('consumption_rms_voltage', 'Consumption RMS Voltage', ['type']),
    'pwrFactor': Gauge('consumption_power_factor', 'Consumption Power Factor', ['type']),
}

inverter_gauges = {
    'last': Gauge('inverter_last_report_watts', 'Last reported watts', ['serial', 'location']),
    'max': Gauge('inverter_max_report_watts', 'Max reported watts', ['serial', 'location']),
}


def scrape_stream():
    while True:
        try:
            url = 'http://%s/stream/meter' % host
            stream = requests.get(url, auth=auth, stream=True, timeout=5)
            for line in stream.iter_lines():
                if line.startswith(marker):
                    data = json.loads(line.replace(marker, b''))
                    print(data)
                    for meter_type in ['production', 'net-consumption', 'total-consumption']:
                        for phase in ['ph-a', 'ph-b']:
                            for key, value in data.get(meter_type, {}).get(phase, {}).items():
                                if key in stream_gauges:
                                    stream_gauges[key].labels(type=meter_type, phase=phase).set(value)
        except requests.exceptions.RequestException as e:
            print('Exception fetching stream data: %s' % e)
            time.sleep(5)


def scrape_production_json():
    url = 'http://%s/production.json' % host
    data = requests.get(url).json()
    production = data['production']
#    print(production)
    for each in production:
        mtype = each['type']
        for key in ['activeCount', 'wNow', 'whLifetime', 'whToday', 'whLastSevenDays', 'rmsCurrent', 'rmsVoltage', 'pwrFactor']:
            value = each.get(key)
            if value is not None:
                production_gauges[key].labels(type=mtype).set(value)
    consumption = data['consumption']
#    print(consumption)
    for each in consumption:
        mtype = each['measurementType']
        for key in ['wNow', 'whLifetime', 'whToday', 'whLastSevenDays', 'rmsCurrent', 'rmsVoltage', 'pwrFactor']:
            value = each.get(key)
            if value is not None:
                consumption_gauges[key].labels(type=mtype).set(value)



def scrape_inverters():
    url = 'http://%s/api/v1/production/inverters' % host
    data = requests.get(url, auth=auth).json()
#    print(data)
    for inverter in data:
        serial = int(inverter['serialNumber'])
        location = serials.get(serial, 'unknown')
        inverter_gauges['last'].labels(serial=serial, location=location).set(inverter['lastReportWatts'])
        inverter_gauges['max'].labels(serial=serial, location=location).set(inverter['maxReportWatts'])


def main():
    start_http_server(8000)
#    stream_thread = threading.Thread(target=scrape_stream)
#    stream_thread.setDaemon(True)
#    stream_thread.start()
    counter = 0
    while True:
        counter += 1
        if counter % production_period == 0: 
            try:
                scrape_production_json()
            except Exception as e:
                print('Exception fetching production data: %s' % e)
        time.sleep(30)
        if counter % inverter_period == 0:
            try:
                scrape_inverters()
            except Exception as e:
                print('Exception fetching inverters data: %s' % e)
            counter = 0
        time.sleep(30)


if __name__ == '__main__':
    main()
