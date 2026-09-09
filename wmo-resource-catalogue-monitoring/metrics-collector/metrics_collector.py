###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import csv
import json
import logging
import os
import sys
from urllib.parse import urlparse

import paho.mqtt.client as mqtt_client
from prometheus_client import (
    Gauge, start_http_server, REGISTRY, GC_COLLECTOR,
    PLATFORM_COLLECTOR, PROCESS_COLLECTOR
)

REGISTRY.unregister(GC_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(PROCESS_COLLECTOR)

API_URL = os.environ['WMO_RESOURCE_CATALOGUE_API_URL']
BROKER_URL = os.environ['WMO_RESOURCE_CATALOGUE_BROKER_URL']
CENTRE_ID = os.environ['WMO_RESOURCE_CATALOGUE_CENTRE_ID']
CENTRE_ID_CSV = os.environ['WMO_RESOURCE_CATALOGUE_CENTRE_ID_CSV']
GB = os.environ['WMO_RESOURCE_CATALOGUE_GB']
GB_TOPIC = os.environ['WMO_RESOURCE_CATALOGUE_GB_TOPIC']
HTTP_PORT = 8006
LOGGING_LEVEL = os.environ['WMO_RESOURCE_CATALOGUE_LOGGING_LEVEL']

logging.basicConfig(stream=sys.stdout)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOGGING_LEVEL)

# sets metrics as per https://github.com/wmo-im/wis2-metric-hierarchy/blob/main/metric-hierarchy/gdc.csv  # noqa

METRIC_WIS2_GDC_CORE_TOTAL = Gauge(
    'wmo_wis2_gdc_core_total',
    'Number of core metadata records',
    ['centre_id', 'report_by']
)

METRIC_WIS2_GDC_RECOMMENDED_TOTAL = Gauge(
    'wmo_wis2_gdc_recommended_total',
    'Number of recommended metadata records',
    ['centre_id', 'report_by']
)

METRIC_WIS2_GDC_EARTH_SYSTEM_DISCIPLINE_TOTAL = Gauge(
    'wmo_wis2_gdc_earth_system_discipline_total',
    'Number of metadata records for an Earth system discipline',
    ['earth_system_discipline', 'centre_id', 'report_by']
)

METRIC_WIS2_GDC_KPI_PERCENTAGE_TOTAL = Gauge(
    'wmo_wis2_gdc_kpi_percentage_total',
    'KPI percentage for a single metadata record (metadata_id = WCMP2 id)',
    ['metadata_id', 'centre_id', 'report_by']
)

METRIC_WIS2_GDC_KPI_PERCENTAGE_AVERAGE = Gauge(
    'wmo_wis2_gdc_kpi_percentage_average',
    'Average KPI percentage',
    ['centre_id', 'report_by']
)

METRIC_WIS2_GDC_KPI_PERCENTAGE_OVER80_TOTAL = Gauge(
    'wmo_wis2_gdc_kpi_percentage_over80_total',
    'Number of metadata records with KPI percentage over 80',
    ['centre_id', 'report_by']
)


def init_metrics() -> None:
    """
    Initializes metrics on startup

    :returns: `None`
    """

    with open(CENTRE_ID_CSV) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            labels = [row['Name'], CENTRE_ID]

            METRIC_WIS2_GDC_CORE_TOTAL.labels(*labels).set(0)
            METRIC_WIS2_GDC_RECOMMENDED_TOTAL.labels(*labels).set(0)


def collect_metrics() -> None:
    """
    Subscribe to MQTT wmo-resource-catalogue/metrics and collect metrics

    :returns: `None`
    """

    def _sub_connect(client, userdata, flags, rc):
        topic = 'wmo-resource-catalogue/#'
        LOGGER.info(f'Subscribing to topic {topic}')
        client.subscribe(topic, qos=0)

    def _sub_message(client, userdata, msg):
        LOGGER.debug('Processing message')
        topic = msg.topic
        payload = json.loads(msg.payload)
        labels = payload['labels']
        value = payload.get('value')
        LOGGER.debug(f'Topic: {topic}')
        LOGGER.debug(f"Labels: {labels}")
        LOGGER.debug(f"Value: {value}")

        if topic == 'wmo-resource-catalogue/wis2-gdc/metrics/clear':
            LOGGER.info('Clearing all metrics')
            METRIC_WIS2_GDC_CORE_TOTAL.clear()
            METRIC_WIS2_GDC_RECOMMENDED_TOTAL.clear()
            METRIC_WIS2_GDC_EARTH_SYSTEM_DISCIPLINE_TOTAL.clear()
            METRIC_WIS2_GDC_KPI_PERCENTAGE_TOTAL.clear()
            METRIC_WIS2_GDC_KPI_PERCENTAGE_OVER80_TOTAL.clear()
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/init':
            LOGGER.info('Initializing metrics')
            init_metrics()
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/core_total':
            METRIC_WIS2_GDC_CORE_TOTAL.labels(*labels).set(value)
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/recommended_total':  # noqa
            METRIC_WIS2_GDC_RECOMMENDED_TOTAL.labels(*labels).set(value)
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/earth_system_discipline_total':  # noqa
            METRIC_WIS2_GDC_EARTH_SYSTEM_DISCIPLINE_TOTAL.labels(*labels).set(value)  # noqa
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/kpi_percentage_total':  # noqa
            METRIC_WIS2_GDC_KPI_PERCENTAGE_TOTAL.labels(*labels).set(value)
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/kpi_percentage_average':  # noqa
            METRIC_WIS2_GDC_KPI_PERCENTAGE_AVERAGE.labels(*labels).set(value)
        elif topic == 'wmo-resource-catalogue/wis2-gdc/metrics/kpi_over80_total':  # noqa
            METRIC_WIS2_GDC_KPI_PERCENTAGE_OVER80_TOTAL.labels(*labels).set(value)  # noqa

    url = urlparse(BROKER_URL)

    client_id = 'wmo-resource-catalogue metrics collector'

    try:
        LOGGER.info('Setting up MQTT client')
        client = mqtt_client.Client(client_id)
        client.on_connect = _sub_connect
        client.on_message = _sub_message
        client.username_pw_set(url.username, url.password)
        LOGGER.info(f'Connecting to {url.hostname}')
        client.connect(url.hostname, url.port)
        client.loop_forever()
    except Exception as err:
        LOGGER.error(err)


if __name__ == '__main__':
    LOGGER.info(f'Starting metrics collector server on port {HTTP_PORT}')
    start_http_server(HTTP_PORT)
    init_metrics()
    collect_metrics()
