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
from pathlib import Path
from typing import Union
import uuid

import click
import requests

from pywmdr.wmdr2.ets import WMDR2TestSuite
from pywis_pubsub import cli_options
from pywis_pubsub.mqtt import MQTTPubSubClient

from wmo_resource_catalogue.backend import BACKENDS
from wmo_resource_catalogue.env import (BACKEND_TYPE, BACKEND_CONNECTION,
                                        BROKER_URL,
                                        WIGOS_GOFC_METADATA_ARCHIVE_SOURCE,
                                        PUBLISH_REPORTS, REJECT_ON_FAILING_ETS,
                                        WIGOS_GOFC_CENTRE_ID)

from wmo_resource_catalogue.wme import generate_wme

LOGGER = logging.getLogger(__name__)

BACKEND_DEFS = {
    'connection': BACKEND_CONNECTION,
    'collection': 'wigos-observing-facility-metadata'
}


class Registrar:
    def __init__(self):
        """
        Initializer

        :returns: `wmo_resource_catalogue.wigos_gofc.registrar.Registrar`
        """

        self.broker = None
        self.record_url = None
        self.source = None
        self.metadata = None
        self.backend = BACKENDS[BACKEND_TYPE](BACKEND_DEFS)

        if PUBLISH_REPORTS:
            self.broker = MQTTPubSubClient(BROKER_URL)

    def get_record(self, wnm: dict, topic: str) -> Union[dict, None]:
        """
        Helper function to fetch WMDR2 document from a WNM

        :param wnm: `dict` of WNM
        :param topic: `str` of topic

        :returns: `dict` of WMDR2 or `None`
        """

        message = {}
        message_failure_reason = None

        centre_id = topic.split('/')[3]
        if centre_id.endswith('global-observing-facility-catalogue'):
            msg = 'WMDR2 record republished from another GOFC; not processing'
            LOGGER.info(msg)
            return None

        try:
            LOGGER.debug('Fetching canonical URL')
            self.record_url = list(
                filter(lambda d: d['rel'] in ['canonical', 'update'],
                       wnm['links']))[0]['href']
        except (IndexError, KeyError):
            LOGGER.error('No canonical link found')
            raise

        LOGGER.debug(f'Fetching {self.record_url}')

        try:
            r = requests.get(self.record_url)
            r.raise_for_status()
            self.source = r.content
            return r.json()
        except requests.exceptions.HTTPError as err:
            message_failure_reason = err
            LOGGER.warning(err)
        except json.decoder.JSONDecodeError as err:
            message_failure_reason = err
            LOGGER.warning(err)

        LOGGER.debug(f'WMDR2 access failed: {message_failure_reason}')

        message['description'] = str(message_failure_reason)

        LOGGER.info('Publishing URL error report to broker')
        wme = generate_wme(WIGOS_GOFC_CENTRE_ID, centre_id, 'item.download',
                           'ERROR', 'WMDR2 access failure',
                           message, [self._get_link()])
        publish_report_topic = f'monitor/a/wigos/{centre_id}'
        self.broker.pub(publish_report_topic, json.dumps(wme))

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
            self.source = json.dumps(metadata, indent=4).encode('utf-8')
        elif isinstance(metadata, (bytes, str)):
            LOGGER.debug('Metadata is bytes or string; parsing')
            try:
                self.metadata = json.loads(metadata)
                self.source = metadata.encode('utf-8')
            except json.decoder.JSONDecodeError as err:
                LOGGER.warning(err)
                return

        # FIXME: bypassing centre-id detection until centre-id
        # workflow is established
        self.centre_id = topic.split('/')[3]
        # self.centre_id = self.metadata['id'].split('-')[3]
        publish_report_topic = f'monitor/a/wigos/{self.centre_id}'

        if topic is None:
            LOGGER.warning('No incoming topic defined')
        else:
            LOGGER.info('Comparing centre-id of topic and metadata record')
            incoming_topic_centre_id = topic.split('/')[3]

            LOGGER.debug(f'Topic centre-id: {incoming_topic_centre_id}')
            LOGGER.debug(f'Metadata centre-id {self.centre_id}')

            if incoming_topic_centre_id != self.centre_id:
                LOGGER.warning('Topic mismatch')
                message = {
                    'description': f'Topic mismatch ({incoming_topic_centre_id} != {self.centre_id})'  # noqa
                }

                wme = generate_wme(WIGOS_GOFC_CENTRE_ID, self.centre_id,
                                   'wmdr2.ets', 'ERROR', 'Topic mismatch',
                                   message, [self._get_link()])

                self.broker.pub(publish_report_topic, json.dumps(wme))

                return

        LOGGER.debug(f'Metadata: {json.dumps(self.metadata, indent=4)}')

        LOGGER.info('Running ETS')
        failed_ets = False

        try:
            ts = WMDR2TestSuite(metadata)
            ets_results = ts.run_tests()
        except ValueError as err:
            LOGGER.info('Validation errors; metadata not published')
            ets_results = {
                'id': str(uuid.uuid4()),
                'report_type': 'ets',
                'summary': {
                    'FAILED': 1
                },
                'tests': [{
                    'id': 'http://wigos.wmo.int/spec/wmdr/2/conf/core/conformance',  # noqa
                    'code': 'FAILED',
                    'message': str(err)
                }]
            }

        if ets_results['summary']['FAILED'] > 0:
            LOGGER.warning('ETS errors; metadata not published')
            failed_ets = True

        ets_results['report_by'] = WIGOS_GOFC_CENTRE_ID
        ets_results['centre_id'] = self.centre_id

        if PUBLISH_REPORTS:
            severity = 'INFO'

            codes = [r['code'] for r in ets_results['tests']]

            if codes.count('WARNING') > 0:
                severity = 'WARNING'
            if codes.count('FAILED') > 0:
                severity = 'ERROR'

            LOGGER.info('Publishing ETS report to broker')
            wme = generate_wme(WIGOS_GOFC_CENTRE_ID, self.centre_id,
                               'wmdr2.ets', severity, 'WMDR2 ETS report',
                               ets_results, [self._get_link()])
            self.broker.pub(publish_report_topic, json.dumps(wme))

        if failed_ets:
            if REJECT_ON_FAILING_ETS:
                LOGGER.info('Stopping further processing')
                return

        source_filename = f"{self.metadata['id']}.json"
        source_filename = WIGOS_GOFC_METADATA_ARCHIVE_SOURCE / source_filename
        LOGGER.debug(f'Saving source record to {source_filename}')
        with source_filename.open('wb') as fh:
            fh.write(self.source)

        LOGGER.info('Adding centre-id property')
        self.metadata['properties']['centre-id'] = self.centre_id

        LOGGER.info('Publishing metadata to backend')
        self._publish()

    def delete_record(self, topic: str, wnm: dict) -> None:
        """
        Delete a metadata document

        :param topic: `str` of incoming topic (default is `None`)
        :param wnm: `dict` of WNM

        :returns: `None`
        """

        centre_id = topic.split('/')[3]
        publish_report_topic = f'monitor/a/wigos/{centre_id}'
        severity = 'INFO'

        message = {}

        metadata_id = wnm['properties'].get('metadata_id')

        if metadata_id is None:
            message['description'] = 'No metadata id specified'
            severity = 'ERROR'
        else:
            message['metadata_id'] = metadata_id
            try:
                self.backend.delete_record(metadata_id)
                message['description'] = f'metadata {metadata_id} deleted'
            except Exception:
                message['description'] = f'metadata {metadata_id} not found'
                severity = 'ERROR'

            source_filename = f"{metadata_id}.json"
            source_filename = WIGOS_GOFC_METADATA_ARCHIVE_SOURCE / source_filename  # noqa
            LOGGER.debug(f'Deleting source record {source_filename}')
            source_filename.unlink(missing_ok=True)

        LOGGER.info('Publishing metadata deletion report to broker')
        wme = generate_wme(WIGOS_GOFC_CENTRE_ID, centre_id, 'item.download',
                           severity, 'WIGOS GOFC WMDR2 deletion report',
                           message)
        self.broker.pub(publish_report_topic, json.dumps(wme))

        return

    def _publish(self):
        """
        Publish metadata from `wigos_gofc.registrar:Registrar.metadata`
        to backend

        :returns: `None`
        """

        LOGGER.info(f'Saving to {BACKEND_TYPE} ({BACKEND_DEFS})')
        self.backend.save_record(self.metadata)

    def _get_link(self):
        """
        Generates a link object

        :returns: `dict` of link object
        """

        link = {
            'rel': 'related',
            'type': 'application/geo+json',
            'title': 'WMDR2 observing facility metadata record',
            'href': self.record_url
        }

        if self.metadata is not None:
            link['length'] = len(self.metadata)

        return link

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
    """Create WIGOS GOFC backend"""

    backend = BACKENDS[BACKEND_TYPE](BACKEND_DEFS)
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
    """Delete WIGOS GOFC backend"""

    if not bypass:
        if not click.confirm('Delete WIGOS GOFC backend?  This will remove existing collections', abort=True):  # noqa
            return

    backend = BACKENDS[BACKEND_TYPE](BACKEND_DEFS)
    LOGGER.debug(f'Backend: {backend}')
    backend.teardown()

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument(
    'path', type=click.Path(exists=False, dir_okay=True, file_okay=True))
@cli_options.OPTION_VERBOSITY
def register(ctx, path, verbosity='NOTSET'):
    """Register observing facility metadata"""

    wmdr2s_to_process = []

    if path.startswith('http'):
        wmdr2s_to_process = [path]
    else:
        p = Path(path)

        if not p.exists():
            raise click.ClickException('File not found')

        if p.is_file():
            wmdr2s_to_process = [p]
        else:
            wmdr2s_to_process = p.rglob('*.json')

    for w2p in wmdr2s_to_process:
        click.echo(f'Processing {w2p}')

        r = Registrar()

        if isinstance(w2p, str) and w2p.startswith('http'):
            response = requests.get(w2p)
            metadata = response.content
            r.record_url = w2p
            r.metadata_length = response.headers.get('Content-Length')
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
    """Unregister observing facility metadata"""

    click.echo(f'Unregistering {identifier}')
    backend = BACKENDS[BACKEND_TYPE](BACKEND_DEFS)
    try:
        LOGGER.debug(f'Backend: {backend}')
        backend.delete_record(identifier)
    except Exception:
        click.echo('record not found')

    click.echo('Done')
