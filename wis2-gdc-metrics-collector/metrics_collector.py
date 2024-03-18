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
from urllib.parse import urlparse

import paho.mqtt.client as mqtt_client
import prometheus_client
from prometheus_client import Counter, Gauge, Info, start_http_server


prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

LOGGER = logging.getLogger(__name__)

API_URL = os.environ['WIS2_GDC_API_URL']
BROKER_URL = os.environ['WIS2_GDC_BROKER_URL']
CENTRE_ID = os.environ['WIS2_GDC_CENTRE_ID']
GB = os.environ['WIS2_GDC_GB']
GB_TOPIC = os.environ['WIS2_GDC_GB_TOPIC']
HTTP_PORT = 8001


# sets metrics as per https://github.com/wmo-im/wis2-metric-hierarchy/blob/main/metric-hierarchy/gdc.csv  # noqa

metric_info = Info(
    'wis2_gdc_metrics',
    'WIS2 GDC metrics'
)

metric_passed_total = Counter(
    'wmo_wis2_gdc_passed_total',
    'Number of metadata records passed validation',
    ['centre_id', 'report_by']
)

metric_failed_total = Counter(
    'wmo_wis2_gdc_failed_total',
    'Number of metadata records failed validation',
    ['centre_id', 'report_by']
)

metric_core_total = Counter(
    'wmo_wis2_gdc_core_total',
    'Number of core metadata records',
    ['centre_id', 'report_by']
)

metric_recommended_total = Counter(
    'wmo_wis2_gdc_recommendedcore_total',
    'Number of recommended metadata records',
    ['centre_id', 'report_by']
)

metric_kpi_percentage_total = Counter(
    'wmo_wis2_gdc_kpi_percentage_total',
    'KPI percentage for a single metadata record (metadata_id equals WCMP2 id)',  # noqa
    ['metadata_id', 'centre_id', 'report_by']
)

metric_kpi_percentage_average = Gauge(
    'wmo_wis2_gdc_kpi_percentage_average',
    'Average KPI percentage',
    ['centre_id', 'report_by']
)

metric_kpi_percentage_over80_total = Counter(
    'wmo_wis2_gdc_kpi_percentage_over80_total',
    'Number of metadata records with KPI percentage over 80',
    ['centre_id', 'report_by']
)

metric_search_total = Counter(
    'wmo_wis2_gdc_search_total',
    'Number of search requests (during last monitoring period)',
    ['centre_id', 'report_by']
)

metric_search_terms = Gauge(
    'wmo_wis2_gdc_search_terms',
    'Most popular search terms (e.g. top=1 to top=5)',
    ['top', 'centre_id', 'report_by']
)

metric_info.info({
    'centre-id': CENTRE_ID,
    'url': API_URL,
    'subscribed-to': f'{GB}/{GB_TOPIC}'
})


def collect_metrics():
    """
    Subscribe to MQTT wis2-gdc/metrics and collect metrics

    :returns: `None`
    """

    def _sub_connect(client, userdata, flags, rc):
        client.subscribe('wis2-gdc/metrics')

    def _sub_collect(client, userdata, msg):
        topic = json.loads(msg.topic)
        labels = json.loads(msg.payload)

        if topic == 'wis2-gdc/metrics/passed_total':
            metric_passed_total.labels(*labels).inc()
        if topic == 'wis2-gdc/metrics/failed_total':
            metric_failed_total.labels(*labels).inc()
        elif topic == 'wis2-gdc/metrics/core_total':
            metric_core_total.labels(*labels).inc()
        elif topic == 'wis2-gdc/metrics/recommended_total':
            metric_recommended_total.labels(*labels).inc()

    url = urlparse(BROKER_URL)

    client_id = 'wis2-gdc metrics collector'

    try:
        LOGGER.info('Setting up MQTT client')
        client = mqtt_client.Client(client_id)
        client.on_connect = _sub_connect
        client.on_message = _sub_collect
        client.username_pw_set(url.username, url.password)
        client.connect(url.hostname, url.port)
        client.loop_forever()
    except Exception as err:
        LOGGER.error(err)


if __name__ == '__main__':
    print(f'Starting metrics collector server on port {HTTP_PORT}')
    start_http_server(HTTP_PORT)
    collect_metrics()
