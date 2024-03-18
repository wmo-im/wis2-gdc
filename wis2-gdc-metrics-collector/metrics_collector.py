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

import json
import logging
import os
import sys
from urllib.parse import urlparse

import paho.mqtt.client as mqtt_client
from prometheus_client import (
    Counter, Gauge, Info, start_http_server, REGISTRY, GC_COLLECTOR,
    PLATFORM_COLLECTOR, PROCESS_COLLECTOR
)

REGISTRY.unregister(GC_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(PROCESS_COLLECTOR)

API_URL = os.environ['WIS2_GDC_API_URL']
BROKER_URL = os.environ['WIS2_GDC_BROKER_URL']
CENTRE_ID = os.environ['WIS2_GDC_CENTRE_ID']
GB = urlparse(os.environ['WIS2_GDC_GB'])
GB_TOPIC = os.environ['WIS2_GDC_GB_TOPIC']
HTTP_PORT = 8006
LOGGING_LEVEL = os.environ['WIS2_GDC_LOGGING_LEVEL']

logging.basicConfig(stream=sys.stdout)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOGGING_LEVEL)

# sets metrics as per https://github.com/wmo-im/wis2-metric-hierarchy/blob/main/metric-hierarchy/gdc.csv  # noqa

METRIC_INFO = Info(
    'wis2_gdc_metrics',
    'WIS2 GDC metrics'
)

METRIC_PASSED_TOTAL = Counter(
    'wmo_wis2_gdc_passed_total',
    'Number of metadata records passed validation',
    ['centre_id', 'report_by']
)

METRIC_FAILED_TOTAL = Counter(
    'wmo_wis2_gdc_failed_total',
    'Number of metadata records failed validation',
    ['centre_id', 'report_by']
)

METRIC_CORE_TOTAL = Counter(
    'wmo_wis2_gdc_core_total',
    'Number of core metadata records',
    ['centre_id', 'report_by']
)

METRIC_RECOMMENDED_TOTAL = Counter(
    'wmo_wis2_gdc_recommendedcore_total',
    'Number of recommended metadata records',
    ['centre_id', 'report_by']
)

METRIC_KPI_PERCENTAGE_TOTAL = Counter(
    'wmo_wis2_gdc_kpi_percentage_total',
    'KPI percentage for a single metadata record (metadata_id equals WCMP2 id)',  # noqa
    ['metadata_id', 'centre_id', 'report_by']
)

METRIC_KPI_PERCENTAGE_AVERAGE = Gauge(
    'wmo_wis2_gdc_kpi_percentage_average',
    'Average KPI percentage',
    ['centre_id', 'report_by']
)

METRIC_KPI_PERCENTAGE_OVER80_TOTAL = Counter(
    'wmo_wis2_gdc_kpi_percentage_over80_total',
    'Number of metadata records with KPI percentage over 80',
    ['centre_id', 'report_by']
)

METRIC_SEARCH_TOTAL = Counter(
    'wmo_wis2_gdc_search_total',
    'Number of search requests (during last monitoring period)',
    ['centre_id', 'report_by']
)

METRIC_SEARCH_TERMS = Gauge(
    'wmo_wis2_gdc_search_terms',
    'Most popular search terms (e.g. top=1 to top=5)',
    ['top', 'centre_id', 'report_by']
)

METRIC_INFO.info({
    'centre-id': CENTRE_ID,
    'url': API_URL,
    'subscribed-to': f'{GB.scheme}://{GB.hostname}:{GB.port} (topic: {GB_TOPIC})'  # noqa
})


def collect_metrics() -> None:
    """
    Subscribe to MQTT wis2-gdc/metrics and collect metrics

    :returns: `None`
    """

    def _sub_connect(client, userdata, flags, rc):
        LOGGER.info('Subscribing to topic wis2-gdc/metrics/#')
        client.subscribe('wis2-gdc/metrics/#', qos=0)

    def _sub_message(client, userdata, msg):
        LOGGER.debug('Processing message')
        topic = msg.topic
        labels = json.loads(msg.payload)
        LOGGER.debug(f'Topic: {topic}')
        LOGGER.debug(f'Labels: {labels}')

        if topic == 'wis2-gdc/metrics/passed_total':
            METRIC_PASSED_TOTAL.labels(*labels).inc()
        if topic == 'wis2-gdc/metrics/failed_total':
            METRIC_FAILED_TOTAL.labels(*labels).inc()
        elif topic == 'wis2-gdc/metrics/core_total':
            METRIC_CORE_TOTAL.labels(*labels).inc()
        elif topic == 'wis2-gdc/metrics/recommended_total':
            METRIC_RECOMMENDED_TOTAL.labels(*labels).inc()

    url = urlparse(BROKER_URL)

    client_id = 'wis2-gdc metrics collector'

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
    collect_metrics()
