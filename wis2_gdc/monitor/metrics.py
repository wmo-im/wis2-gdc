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

import logging
from time import time
from typing import Union

import prometheus_client
from prometheus_client import CollectorRegistry, Gauge, Info, write_to_textfile

from wis2_gdc.env import API_URL, CENTRE_ID, GB, GB_TOPIC, OPENMETRICS_FILE

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

LOGGER = logging.getLogger(__name__)

# sets metrics as per https://github.com/wmo-im/wis2-metric-hierarchy/blob/main/metric-hierarchy/gdc.csv  # noqa


class Metrics:
    def __init__(self):
        self.registry = CollectorRegistry()

        self.info = Info(
            'wis2_gdc_metrics',
            'WIS2 GDC metrics',
            registry=self.registry
        )

        self.passed_total = Gauge(
            'wmo_wis2_gdc_passed_total',
            'Number of metadata records passed validation',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.failed_total = Gauge(
            'wmo_wis2_gdc_failed_total',
            'Number of metadata records failed validation',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.core_total = Gauge(
            'wmo_wis2_gdc_core_total',
            'Number of core metadata records',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.recommended_total = Gauge(
            'wmo_wis2_gdc_recommendedcore_total',
            'Number of recommended metadata records',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.kpi_percentage_total = Gauge(
            'wmo_wis2_gdc_kpi_percentage_total',
            'KPI percentage for a single metadata record (metadata_id equals WCMP2 id)',  # noqa
            ['metadata_id', 'centre_id', 'report_by'],
            registry=self.registry
        )

        self.kpi_percentage_average = Gauge(
            'wmo_wis2_gdc_kpi_percentage_average',
            'Average KPI percentage',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.kpi_percentage_over80_total = Gauge(
            'wmo_wis2_gdc_kpi_percentage_over80_total',
            'Number of metadata records with KPI percentage over 80',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.search_total = Gauge(
            'wmo_wis2_gdc_search_total',
            'Number of search requests (during last monitoring period)',
            ['centre_id', 'report_by'],
            registry=self.registry
        )

        self.search_terms = Gauge(
            'wmo_wis2_gdc_search_terms',
            'Most popular search terms (e.g. top=1 to top=5)',
            ['top', 'centre_id', 'report_by'],
            registry=self.registry
        )

        self.info.info({
            'centre-id': CENTRE_ID,
            'url': API_URL,
            'subscribed-to': f'{GB}/{GB_TOPIC}'
        })

    def inc(self, metric: str, labels: list) -> None:
        """
        Convenience function to increment a value for a given label set

        :param metric: `str` of metric name
        :param labels: `list` of label set

        :returns: `None`
        """

        getattr(self, metric).labels(*labels).inc()
        getattr(self, metric).labels(*labels)._timestamp = time()

    def set(self, metric: str, labels: list,
            value: Union[int, float, str]) -> None:
        """
        Convenience function to set a value for a given label set

        :param metric: `str` of metric name
        :param labels: `list` of label set
        :param value: literal of value

        :returns: `None`
        """

        getattr(self, metric).labels(*labels).set(value)
        getattr(self, metric).labels(*labels)._timestamp = time()

    def write(self) -> None:
        """
        Writes OpenMetrics to file

        :returns: `None`
        """

        write_to_textfile(OPENMETRICS_FILE, self.registry)

    def __exit__(self, exc_type, exc_value, traceback):
        LOGGER.debug('Exiting')

    def __repr__(self):
        return '<Metrics>'
