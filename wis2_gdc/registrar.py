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

from copy import deepcopy
import json
import logging
from pathlib import Path

import click
import requests

from pywcmp.wcmp2.ets import WMOCoreMetadataProfileTestSuite2
from pywcmp.wcmp2.kpi import WMOCoreMetadataProfileKeyPerformanceIndicators
from pywis_pubsub import cli_options
from pywis_pubsub.mqtt import MQTTPubSubClient

from wis2_gdc.backend import BACKENDS
from wis2_gdc.env import (BACKEND_TYPE, BACKEND_CONNECTION, BROKER_URL,
                          CENTRE_ID, GB_LINKS, PUBLISH_REPORTS,
                          REJECT_ON_FAILING_ETS, RUN_KPI)
from wis2_gdc.monitor.metrics import Metrics

LOGGER = logging.getLogger(__name__)


class Registrar:
    def __init__(self):
        """
        Initializer

        :returns: `wis2_gdc.registrar.Registrar`
        """

        self.broker = None
        self.metadata = None
        self.metrics = Metrics()

        if PUBLISH_REPORTS:
            self.broker = MQTTPubSubClient(BROKER_URL)

    def get_wcmp2(self, wnm: dict) -> dict:
        """
        Helper function to fetch WCMP2 document from a WNM

        :param wnm: `dict` of WNM

        :returns: `dict` of WCMP2
        """

        try:
            LOGGER.debug('Fetching canonical URL')
            wcmp2_url = list(filter(lambda d: d['rel'] == 'canonical',
                             wnm['links']))[0]['href']
        except (IndexError, KeyError):
            LOGGER.error('No canonical link found')
            raise

        LOGGER.debug(f'Fetching {wcmp2_url}')
        return requests.get(wcmp2_url).json()

    def register(self, metadata: dict) -> None:
        """
        Register a metadata document

        :param metadata: `dict` of metadata document

        :returns: `None`
        """

        self.metadata = metadata

        self.centre_id = self.metadata['id'].split(':')[3]
        topic = f'monitor/a/wis2/{CENTRE_ID}/{self.centre_id}'
        centre_id_labels = [self.centre_id, CENTRE_ID]

        LOGGER.debug(f'Metadata: {json.dumps(self.metadata, indent=4)}')

        LOGGER.info('Running ETS')
        ets_results = self._run_ets()
        ets_results['report-by'] = CENTRE_ID
        ets_results['centre-id'] = self.centre_id

        if PUBLISH_REPORTS:
            LOGGER.info('Publishing ETS report to broker')
            self.broker.pub(topic, json.dumps(ets_results))

        if REJECT_ON_FAILING_ETS:
            try:
                if ets_results['ets-report']['summary']['FAILED'] > 0:
                    LOGGER.warning('ETS errors; metadata not published')
                    return
            except KeyError:  # validation error
                self.metrics.failed_total.labels(*centre_id_labels).inc()
                LOGGER.debug('Validation errors; metadata not published')
                self.metrics.write()
                return

        self.metrics.passed_total.labels(*centre_id_labels).inc()

        # TODO: remove following wis2box b7 updates
        data_policy = self.metadata['properties']['wmo:dataPolicy']
        if data_policy == 'core':
            self.metrics.core_total.labels(*centre_id_labels).inc()
        elif data_policy == 'recommended':
            self.metrics.recommended_total.labels(*centre_id_labels).inc()

        LOGGER.info('Updating links')
        self.update_record_links()

        LOGGER.info(f'Publishing metadata to {BACKEND_TYPE} ({BACKEND_CONNECTION})')  # noqa
        self._publish()

        if RUN_KPI:
            LOGGER.info('Running KPI')
            kpi_results = self._run_kpi()
            kpi_results['report-by'] = CENTRE_ID
            kpi_results['centre-id'] = self.centre_id

            if PUBLISH_REPORTS:
                LOGGER.info('Publishing KPI report to broker')
                self.broker.pub(topic, json.dumps(kpi_results))

        self.metrics.write()

    def _run_ets(self) -> dict:
        """
        Helper function to run ETS

        :returns: `dict` of ETS results
        """

        try:
            ts = WMOCoreMetadataProfileTestSuite2(self.metadata)
            return ts.run_tests(fail_on_schema_validation=True)
        except ValueError as err:
            return {'description': f'Failed ETS: {err}'}

    def _run_kpi(self) -> dict:
        """
        Helper function to run KPI

        :returns: `dict` of KPI results
        """

        try:
            kpis = WMOCoreMetadataProfileKeyPerformanceIndicators(self.metadata)  # noqa
            return kpis.evaluate()
        except Exception as err:
            return {'description': f'Failed KPI: {err}'}

    def _publish(self):
        """
        Publish metadata from `wis2_gdc.registrar:Registrar.metadata`
        to backend

        :returns: `None`
        """

        backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})
        LOGGER.info('Saving metadata to backend')
        backend.save(self.metadata)

    def update_record_links(self) -> None:
        """
        Update Global Service links

        :returns: `None` (self.metadata updated inline)
        """

        def is_wis2_mqtt_link(link) -> bool:
            if link['href'].startswith('mqtt'):
                if (link.get('wmo:topic', '').startswith('origin/a/wis2') or
                        link.get('channel', '').startswith('origin/a/wis2')):
                    LOGGER.debug('Found MQTT link')
                    return True

            return False

        for count, value in enumerate(self.metadata['links']):
            if is_wis2_mqtt_link(value):
                LOGGER.debug('Adjusting MQTT link')
                channel = value.get('wmo:topic', value.get('channel'))

                new_link = value
                _ = new_link.pop('wmo:topic', None)

                new_link['rel'] = 'items'
                new_link['channel'] = channel.replace('origin', 'cache')
                new_link['type'] = 'application/geo+json'

                del self.metadata['links'][count]

                for gb_link in GB_LINKS:
                    gb_link_to_add = deepcopy(new_link)
                    title = f'Notifications from {gb_link[0]} Global Broker'
                    gb_link_to_add['title'] = title
                    gb_link_to_add['href'] = gb_link[1]

                    LOGGER.debug(f'Adding new link: {gb_link_to_add}')
                    self.metadata['links'].append(gb_link_to_add)

    def __repr__(self):
        return '<Registrar>'


@click.command()
@click.pass_context
@click.option('--yes', '-y', 'bypass', is_flag=True, default=False,
              help='Bypass permission prompts')
@cli_options.OPTION_VERBOSITY
def setup(ctx, bypass, verbosity='NOTSET'):
    """Create GDC backend"""

    if not bypass:
        if not click.confirm('Create GDC backend?  This will overwrite existing collections', abort=True):  # noqa
            return

    backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})
    LOGGER.debug(f'Backend: {backend}')
    backend.setup()


@click.command()
@click.pass_context
@click.option('--yes', '-y', 'bypass', is_flag=True, default=False,
              help='Bypass permission prompts')
@cli_options.OPTION_VERBOSITY
def teardown(ctx, bypass, verbosity='NOTSET'):
    """Delete GDC backend"""

    if not bypass:
        if not click.confirm('Delete GDC backend?  This will remove existing collections', abort=True):  # noqa
            return

    backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})
    LOGGER.debug(f'Backend: {backend}')
    backend.teardown()


@click.command()
@click.pass_context
@click.argument(
    'path', type=click.Path(exists=True, dir_okay=True, file_okay=True))
@cli_options.OPTION_VERBOSITY
def register(ctx, path, verbosity='NOTSET'):
    """Register discovery metadata"""

    p = Path(path)

    if p.is_file():
        wcmp2s_to_process = [p]
    else:
        wcmp2s_to_process = p.rglob('*.json')

    for w2p in wcmp2s_to_process:
        click.echo(f'Processing {w2p}')
        with w2p.open() as fh:
            m = json.load(fh)
            r = Registrar()
            r.register(m)
