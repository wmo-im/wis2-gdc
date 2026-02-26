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
from pathlib import Path
import tempfile
from typing import Union
from urllib.parse import urlparse
import zipfile

import click
import paho.mqtt.client as mqtt
from pywcmp.bundle import WIS2_TOPIC_HIERARCHY_DIR
from pywis_pubsub import cli_options
from pywiscat.wis2.metrics import (
    analyze_data_policy, analyze_earth_system_discipline, analyze_kpi
)

from wis2_gdc.env import (BROKER_URL, CENTRE_ID, METADATA_ARCHIVE_ZIPFILE,
                          PUBLISH_REPORTS)

LOGGER = logging.getLogger(__name__)


class MetricsAnalyzer:
    def __init__(self, archive_dir: Path):
        """
        Initializer

        :param archive_dir: archive directory
        :returns: `wis2_gdc.metrics.MetricsAnalyzer`
        """

        self.archive_dir = archive_dir
        self.broker = None

        if PUBLISH_REPORTS:
            _broker = urlparse(BROKER_URL)
            self.broker = mqtt.Client()
            self.broker.username_pw_set(_broker.username, _broker.password)
            self.broker.connect(_broker.hostname, _broker.port, 60)
            self.broker.loop_start()

    def analyze(self) -> None:
        """
        Analyze catalogue metadata records archive

        :returns: `None`
        """

        self._analyze_data_policy()
        self._analyze_earth_system_discipline()
        self._analyze_kpi()

    def _analyze_data_policy(self) -> None:
        """
        Analyze and publish WIS2 Metrics:

        - wmo_wis2_gdc_core_total
        - wmo_wis2_gdc_recommended_total

        :returns: `None`
        """

        for dp in ['core', 'recommended']:
            LOGGER.debug(f'Analyzing wmo_wis2_gdc_{dp}_total')
            report = analyze_data_policy(dp, self.archive_dir)

            for centre_id, count in report.items():
                self._publish_gdc_metric(f'wis2-gdc/metrics/{dp}_total',
                                         [centre_id], count)

    def _analyze_earth_system_discipline(self) -> None:
        """
        Analyze and publish WIS2 Metrics:

        - wmo_wis2_gdc_earth_system_discipline_total

        :returns: `None`
        """

        LOGGER.debug('Analyzing wmo_wis2_gdc_earth_system_discipline_total')
        report = analyze_earth_system_discipline(self.archive_dir)

        for centre_id in report.keys():
            for esd in report[centre_id].keys():
                self._publish_gdc_metric(
                    'wis2-gdc/metrics/earth_system_discipline_total',
                    [esd, centre_id], report[centre_id][esd])

    def _analyze_kpi(self) -> None:
        """
        Analyze and publish WIS2 Metrics:

        - wmo_wis2_gdc_kpi_percentage_total
        - wmo_wis2_gdc_kpi_percentage_average
        - wmo_wis2_gdc_kpi_percentage_over80_total

        :returns: `None`
        """

        centre_id_csv = WIS2_TOPIC_HIERARCHY_DIR / 'centre-id.csv'

        with centre_id_csv.open() as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                centre_id = row['Name']
                LOGGER.debug(f'Analyzing KPI metrics for {centre_id}')
                report = analyze_kpi(centre_id, self.archive_dir)

                for key, value in report[centre_id]['scoring'].items():
                    LOGGER.debug(f'Publishing KPI score for WCMP2 id {key}')
                    self._publish_gdc_metric(
                        'wis2-gdc/metrics/kpi_percentage_total',
                        [key, centre_id], value)

                LOGGER.debug(f'Publishing KPI percentage for {centre_id}')
                self._publish_gdc_metric(
                    'wis2-gdc/metrics/kpi_percentage_average',
                    [centre_id], report[centre_id]['kpi_percentage_average'])

                LOGGER.debug(f'Publishing KPI percentage over 80 for {centre_id}')  # noqa
                self._publish_gdc_metric(
                    'wis2-gdc/metrics/kpi_percentage_over80_total',
                    [centre_id],
                    report[centre_id]['kpi_percentage_over80_total'])

    def _publish_gdc_metric(self, topic: str, labels: list,
                            value: Union[int, float]) -> None:
        """
        Publish GDC metric

        :param topic: `str` of internal topic
        :param labels: `list` of metric labels
        :param value: `int` or `float` of value
        """

        if not PUBLISH_REPORTS:
            LOGGER.info('Report publishing not set; not publishing metric')
            return

        message = {
            'labels': labels + [CENTRE_ID],
            'value': value
        }

        self.broker.publish(topic, json.dumps(message))

    def __repr__(self):
        return '<MetricsAnalyzer>'


@click.group()
def metrics():
    """WIS2 Global Discovery Catalogue metrics utilities"""

    pass


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def analyze(ctx, verbosity='NOTSET'):
    """Analyze WCMP2 metadata arcvhie"""

    click.echo(f'Analyzing {METADATA_ARCHIVE_ZIPFILE}')
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(METADATA_ARCHIVE_ZIPFILE) as zfh:
            zfh.extractall(tmpdirname)

            archive_dir = list(Path(tmpdirname).iterdir())[0]
            ma = MetricsAnalyzer(archive_dir)
            ma.analyze()
            ma.broker.disconnect()
            ma.broker.loop_stop()

    click.echo('Done')


metrics.add_command(analyze)
