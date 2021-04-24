# solar-observatory
Monitoring system for Enphase envoy-based photovoltaic systems

## Update

This fork of this includes some changes to support the IQ Envoy, which requires a simple password to grab more information.
Also included is an updated dashboard that corresponds to the new/changed fields in this scraper, with an adjusted layout.

## Setup instructions

* install docker and docker-compose
* set ENVOY_HOST (ip address for your envoy) and ENVOY_PASS
* in prometheus/prometheus.yml set the `targets` for the `node-exporter` job (if you want to monitor your host machine)
* `docker-compose build scraper`
* `docker-compose up -d`


I have 3 rows of panels, so I have some location labeling for these 3 arrays. If you wish to label your panels
just replace the `serials` map in scrape.py and rebuild the container.

![dashboard](https://github.com/Scott8586/solar-observatory/blob/master/screenshot.png)
![dashboard2](https://github.com/Scott8586/solar-observatory/blob/master/screenshot2.png)
