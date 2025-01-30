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
from typing import Union
import uuid

import click
import requests

from pywcmp.wcmp2.ets import WMOCoreMetadataProfileTestSuite2
from pywcmp.wcmp2.kpi import WMOCoreMetadataProfileKeyPerformanceIndicators
from pywis_pubsub import cli_options
from pywis_pubsub.mqtt import MQTTPubSubClient
from pywis_pubsub.publish import create_message

from wis2_gdc.backend import BACKENDS
from wis2_gdc.env import (API_URL, API_URL_DOCKER, BACKEND_TYPE,
                          BACKEND_CONNECTION, BROKER_URL,
                          CENTRE_ID, GB_LINKS, PUBLISH_REPORTS,
                          REJECT_ON_FAILING_ETS, RUN_KPI)
from wis2_gdc.wme import generate_wme

LOGGER = logging.getLogger(__name__)


class Registrar:
    def __init__(self):
        """
        Initializer

        :returns: `wis2_gdc.registrar.Registrar`
        """

        self.broker = None
        self.wcmp2_url = None
        self.metadata = None
        self.backend = BACKENDS[BACKEND_TYPE](
                    {'connection': BACKEND_CONNECTION})

        if PUBLISH_REPORTS:
            self.broker = MQTTPubSubClient(BROKER_URL)

    def get_wcmp2(self, wnm: dict, topic: str) -> Union[dict, None]:
        """
        Helper function to fetch WCMP2 document from a WNM

        :param wnm: `dict` of WNM
        :param topic: `str` of topic

        :returns: `dict` of WCMP2 or `None`
        """

        message = {}
        message_failure_reason = None

        centre_id = topic.split('/')[3]
        if centre_id.endswith('global-discovery-catalogue'):
            msg = 'WCMP2 record republished from another GDC; not processing'
            LOGGER.info(msg)
            return None

        try:
            LOGGER.debug('Fetching canonical URL')
            self.wcmp2_url = list(filter(lambda d: d['rel'] == 'canonical',
                                  wnm['links']))[0]['href']
        except (IndexError, KeyError):
            LOGGER.error('No canonical link found')
            raise

        LOGGER.debug(f'Fetching {self.wcmp2_url}')

        try:
            r = requests.get(self.wcmp2_url)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            message_failure_reason = err
            LOGGER.warning(err)
            self._process_record_metric(
                'unknown', 'downloaded_errors_total',
                [BROKER_URL, CENTRE_ID])
        except json.decoder.JSONDecodeError as err:
            message_failure_reason = err
            LOGGER.warning(err)
            self._process_record_metric(
                'unknown', 'failed_total',
                [BROKER_URL, CENTRE_ID])

        LOGGER.debug(f'WCMP2 access failed: {message_failure_reason}')
        message['id'] = str(uuid.uuid4())
        message['message'] = str(message_failure_reason)
        message['href'] = self.wcmp2_url
        message['report_by'] = CENTRE_ID
        message['centre_id'] = centre_id

        publish_report_topic = f'monitor/a/wis2/{CENTRE_ID}/{centre_id}'
        self.broker.pub(publish_report_topic, json.dumps(message))

        return None

    def register(self, metadata: Union[dict, str], topic: str = None) -> None:
        """
        Register a metadata document

        :param metadata: `dict` or `str` of metadata document
        :param topic: `str` of incoming topic (default is `None`)

        :returns: `None`
        """

        if isinstance(metadata, dict):
            LOGGER.debug('Metadata is already a dict')
            self.metadata = metadata
        elif isinstance(metadata, (bytes, str)):
            LOGGER.debug('Metadata is bytes or string; parsing')
            try:
                self.metadata = json.loads(metadata)
            except json.decoder.JSONDecodeError as err:
                LOGGER.warning(err)
                self._process_record_metric(
                    'unknown', 'failed_total', [BROKER_URL, CENTRE_ID])
                return

        self.centre_id = self.metadata['id'].split(':')[3]
        publish_report_topic = f'monitor/a/wis2/{CENTRE_ID}/{self.centre_id}'
        centre_id_labels = [self.centre_id, CENTRE_ID]

        if topic is None:
            LOGGER.warning('No incoming topic defined')
        else:
            LOGGER.info('Comparing centre-id of topic and metadata record')
            incoming_topic_centre_id = topic.split('/')[3]

            LOGGER.debug(f'Topic centre-id: {incoming_topic_centre_id}')
            LOGGER.debug(f'Metadata centre-id {self.centre_id}')

            if incoming_topic_centre_id != self.centre_id:
                LOGGER.warning('Topic mismatch')
                self._process_record_metric(
                    self.metadata['id'], 'failed_total', [BROKER_URL, CENTRE_ID])  # noqa

                msg = f'Topic mismatch ({incoming_topic_centre_id} != {self.centre_id})'  # noqa
                message = {
                    'id': str(uuid.uuid4()),
                    'message': msg,
                    'href': self.wcmp2_url,
                    'report_by': CENTRE_ID,
                    'centre_id': self.centre_id
                }
                self.broker.pub(publish_report_topic, json.dumps(message))

                return

        LOGGER.debug(f'Metadata: {json.dumps(self.metadata, indent=4)}')

        LOGGER.info('Running ETS')
        ets_results = self._run_ets()
        failed_ets = False

        try:
            if ets_results['summary']['FAILED'] > 0:
                LOGGER.warning('ETS errors; metadata not published')
                failed_ets = True
        except KeyError:
            LOGGER.debug('Validation errors; metadata not published')
            ets_results['id'] = str(uuid.uuid4())
            ets_results['href'] = self.wcmp2_url
            failed_ets = True

        ets_results['report_by'] = CENTRE_ID
        ets_results['centre_id'] = self.centre_id

        if PUBLISH_REPORTS:
            LOGGER.info('Publishing ETS report to broker')
            wme = generate_wme(self.centre_id, 'ets', ets_results)
            self.broker.pub(publish_report_topic, json.dumps(wme))

        if failed_ets:
            self._process_record_metric(
                self.metadata['id'], 'failed_total', centre_id_labels)

            if REJECT_ON_FAILING_ETS:
                LOGGER.info('Stopping further processing')
                return

        self._process_record_metric(
            self.metadata['id'], 'passed_total', centre_id_labels)

        data_policy = self.metadata['properties'].get('wmo:dataPolicy')

        if data_policy is not None:
            LOGGER.debug('Adding data policy metric')
            self._process_record_metric(
                self.metadata['id'], f'{data_policy}_total', centre_id_labels)

        LOGGER.info('Updating links')
        self.metadata['links'] = self.update_record_links(data_policy)

        LOGGER.info('Adding centre-id property')
        self.metadata['properties']['centre-id'] = self.centre_id

        LOGGER.info('Publishing metadata to backend')
        self._publish()

        if RUN_KPI:
            LOGGER.info('Running KPI')
            kpi_results = self._run_kpi()
            kpi_results['report_by'] = CENTRE_ID
            kpi_results['centre_id'] = self.centre_id

            if PUBLISH_REPORTS and 'summary' in kpi_results:
                LOGGER.info('Publishing KPI report to broker')
                wme = generate_wme(self.centre_id, 'kpi', kpi_results)
                self.broker.pub(publish_report_topic, json.dumps(wme))

                kpi_labels = [self.metadata['id']] + centre_id_labels

                self._process_record_metric(
                    self.metadata['id'], 'kpi_percentage_total',
                    kpi_labels, kpi_results['summary']['percentage'])

        api_url = f"{API_URL_DOCKER}/collections/wis2-discovery-metadata/items/{self.metadata['id']}"  # noqa

        publish_report_topic = f'origin/a/wis2/{CENTRE_ID}/metadata'

        message = create_message(
            topic=publish_report_topic,
            content_type='application/geo+json',
            url=api_url,
            identifier=str(uuid.uuid4()),
            datetime_=None,
            metadata_id=self.metadata['id'],
            operation='update'
        )

        message = json.dumps(message).replace(API_URL_DOCKER, API_URL)

        LOGGER.info('Publishing updated record to GDC broker')
        self.broker.pub(publish_report_topic, message)

    def delete_record(self, topic: str, wnm: dict) -> None:
        """
        Delete a metadata document

        :param topic: `str` of incoming topic (default is `None`)
        :param wnm: `dict` of WNM

        :returns: `None`
        """

        centre_id = topic.split('/')[3]
        publish_report_topic = f'monitor/a/wis2/{CENTRE_ID}/{centre_id}'

        message = {
            'id': str(uuid.uuid4()),
            'href': None,
            'report_by': CENTRE_ID,
            'centre_id': centre_id
        }

        metadata_id = wnm['properties'].get('metadata_id')

        if metadata_id is None:
            message['message'] = 'No metadata id specified'
        else:
            message['metadata_id'] = metadata_id
            try:
                self.backend.delete_record(metadata_id)
                message['message'] = f'metadata {metadata_id} deleted'
            except Exception:
                message['message'] = f'metadata {metadata_id} not found'

        self.broker.pub(publish_report_topic, json.dumps(message))

        return

    def _process_record_metric(self, identifier: str, metric_name: str,
                               labels: list,
                               value: Union[str, int, float] = None) -> None:
        """
        Helper function to process record metric

        :param identifier: identifier of metadata record
        :param metric_name: `str` of name of metric
        :param labels: `list` of labels to apply
        :param value: optional value(s) to set

        :returns: `None`
        """

        publish_metric = True

        message_payload = {
            'labels': labels
        }

        if value is not None:
            message_payload['value'] = value

        if self.backend.record_exists(identifier) and len(labels) == 2:
            LOGGER.debug('Record exists; not publishing metric')
            publish_metric = False

        if publish_metric:
            LOGGER.debug('Record does not exist; publishing metric')
            self.broker.pub(f'wis2-gdc/metrics/{metric_name}',
                            json.dumps(message_payload))

    def _run_ets(self) -> dict:
        """
        Helper function to run ETS

        :returns: `dict` of ETS results
        """

        try:
            ts = WMOCoreMetadataProfileTestSuite2(self.metadata)
            return ts.run_tests(fail_on_schema_validation=True)
        except ValueError as err:
            return {'message': f'Failed ETS: {err}'}

    def _run_kpi(self) -> dict:
        """
        Helper function to run KPI

        :returns: `dict` of KPI results
        """

        try:
            kpis = WMOCoreMetadataProfileKeyPerformanceIndicators(self.metadata)  # noqa
            return kpis.evaluate()
        except Exception as err:
            return {'message': f'Failed KPI: {err}'}

    def _publish(self):
        """
        Publish metadata from `wis2_gdc.registrar:Registrar.metadata`
        to backend

        :returns: `None`
        """

        LOGGER.info(f'Saving to {BACKEND_TYPE} ({BACKEND_CONNECTION})')
        self.backend.save_record(self.metadata)

    def update_record_links(self, data_policy: str) -> list:
        """
        Update Global Service links

        :returns: `list` of links, updated accordingly
        """

        def is_wis2_mqtt_link(link) -> bool:
            if link['href'].startswith('mqtt'):
                if link.get('channel', '').startswith('origin/a/wis2'):
                    LOGGER.debug('Found MQTT link')
                    return True

            return False

        new_links = []

        for link in self.metadata['links']:
            new_link = deepcopy(link)

            if is_wis2_mqtt_link(link):
                LOGGER.debug('Adjusting MQTT link')
                channel = link.get('channel', link.get('wmo:topic'))

                _ = new_link.pop('wmo:topic', None)

                if data_policy == 'core':
                    LOGGER.debug('Adjusting channel origin to cache')
                    new_link['channel'] = channel.replace('origin', 'cache')

                new_link['rel'] = 'items'
                new_link['type'] = 'application/geo+json'

                for gb_link in GB_LINKS:
                    gb_link_to_add = deepcopy(new_link)
                    title = f'Notifications from {gb_link[2]} ({gb_link[0]})'
                    gb_link_to_add['title'] = title
                    gb_link_to_add['href'] = gb_link[1]

                    LOGGER.debug(f'Adding new link: {gb_link_to_add}')
                    new_links.append(gb_link_to_add)
            else:
                new_links.append(new_link)

        return new_links

    def __repr__(self):
        return '<Registrar>'


@click.command()
@click.pass_context
@click.option('--force', '-f', 'force', is_flag=True, default=False,
              help='Force reinitialization of backend')
@click.option('--yes', '-y', 'bypass', is_flag=True, default=False,
              help='Bypass permission prompts')
@cli_options.OPTION_VERBOSITY
def setup(ctx, force, bypass, verbosity='NOTSET'):
    """Create GDC backend"""

    backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})
    LOGGER.debug(f'Backend: {backend}')

    if backend.exists():
        if not force:
            click.echo('Backend already exists')
            return
        else:
            if bypass:
                click.echo('Reinitializing backend')
                backend.teardown()
                backend.setup()
            else:
                msg = ('Recreate backend?  This will delete all metadata '
                       'and delete/setup/reinitialize the backend.')

                if not click.confirm(msg, abort=True):
                    click.echo('Not reinitializing backend')
                    return
                else:
                    click.echo('Reinitializing backend')
                    backend.teardown()
                    backend.setup()
    else:
        click.echo('Setting up backend')
        backend.setup()

    click.echo('Done')


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

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument(
    'path', type=click.Path(exists=False, dir_okay=True, file_okay=True))
@cli_options.OPTION_VERBOSITY
def register(ctx, path, verbosity='NOTSET'):
    """Register discovery metadata"""

    wcmp2s_to_process = []

    if path.startswith('http'):
        wcmp2s_to_process = [path]
    else:
        p = Path(path)

        if not p.exists():
            raise click.ClickException('File not found')

        if p.is_file():
            wcmp2s_to_process = [p]
        else:
            wcmp2s_to_process = p.rglob('*.json')

    for w2p in wcmp2s_to_process:
        click.echo(f'Processing {w2p}')

        r = Registrar()

        if isinstance(w2p, str) and w2p.startswith('http'):
            metadata = requests.get(w2p).content
        else:
            with w2p.open() as fh:
                metadata = fh.read()

        r.register(metadata)

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument('identifier')
@cli_options.OPTION_VERBOSITY
def unregister(ctx, identifier, verbosity='NOTSET'):
    """Unregister discovery metadata"""

    click.echo(f'Unregistering {identifier}')
    backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})
    try:
        LOGGER.debug(f'Backend: {backend}')
        backend.delete_record(identifier)
    except Exception:
        click.echo('record not found')

    click.echo('Done')
