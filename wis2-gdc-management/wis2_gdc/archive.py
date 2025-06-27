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
import uuid
from pathlib import Path
import zipfile

import click
import requests
from typing import Union

from pywis_pubsub import cli_options
from pywis_pubsub.mqtt import MQTTPubSubClient
from pywis_pubsub.publish import create_message

from wis2_gdc.env import API_URL, API_URL_DOCKER, BROKER_URL, CENTRE_ID
from wis2_gdc.registrar import Registrar
from wis2_gdc.wme import generate_wme

LOGGER = logging.getLogger(__name__)


def archive_metadata(archive_zipfile: str) -> None:
    """
    Archive all discovery metadata from a GDC to an archive zipfile

    :param archive_zipfile: `str` of filename of zipfile

    :returns: `None`
    """

    def _get_next_link(links) -> Union[str, None]:
        """
        Inner helper function to derive rel=next link from GDC response

        :param links: `list` of links array

        :returns: `str` of next link or `None`
        """

        for link in links:
            if link['rel'] == 'next':
                return link['href']

        return None

    end = False
    gdc_items_url = f'{API_URL_DOCKER}/collections/wis2-discovery-metadata/items'  # noqa
    response = None

    with zipfile.ZipFile(archive_zipfile, 'w') as zf:
        while not end:
            if response is None:
                gdc_items_url2 = gdc_items_url
            else:
                gdc_items_url2 = _get_next_link(response['links'])

            LOGGER.info('Replacing with Docker internal hostname')
            gdc_items_url2 = gdc_items_url2.replace(API_URL, API_URL_DOCKER)
            LOGGER.info(f'Querying GDC with {gdc_items_url2}')
            response = requests.get(gdc_items_url2).json()

            for feature in response['features']:
                LOGGER.debug(f"Saving {feature['id']} to archive")
                filename = f"{CENTRE_ID}/{feature['id']}.json"
                zf.writestr(filename, json.dumps(feature))

            if _get_next_link(response['links']) is None:
                end = True

    metadata_archive_zipfile_topic = f'origin/a/wis2/{CENTRE_ID}/metadata'

    n = Path(archive_zipfile).name
    url = f'{API_URL_DOCKER}/{n}'

    LOGGER.info(f"URL: {url}")

    message = create_message(
        topic=metadata_archive_zipfile_topic,
        content_type='application/zip',
        url=url,
        identifier=str(uuid.uuid4())
    )

    message = json.dumps(message).replace(API_URL_DOCKER, API_URL)

    m = MQTTPubSubClient(BROKER_URL)
    m.pub(metadata_archive_zipfile_topic, message)
    m.close()


def restore_metadata(archive_zipfile: str) -> None:
    """
    Restore all discovery metadata from an archive zipfile

    :param archive_zipfile: `str` of filename of zipfile

    :returns: `None`
    """

    r = Registrar()

    with zipfile.ZipFile(archive_zipfile) as zf:
        for filename in zf.namelist():
            if not zf.getinfo(filename).is_dir():
                LOGGER.debug(f'Reading {filename}')
                metadata = json.loads(zf.read(filename))
                r.metadata = metadata
                LOGGER.debug(f'Publishing {filename}')
                r._publish()

    message = {
        'message': 'Archive metadata restore complete'
    }

    archive_restore_topic = f'monitor/a/wis2/{CENTRE_ID}'
    wme = generate_wme(CENTRE_ID, 'ets', message)

    LOGGER.info('Publishing restore report to broker')
    m = MQTTPubSubClient(BROKER_URL)
    m.pub(archive_restore_topic, json.dumps(wme))
    m.close()


@click.command()
@click.pass_context
@click.argument('archive-zipfile')
@cli_options.OPTION_VERBOSITY
def archive(ctx, archive_zipfile, verbosity='NOTSET'):
    """Archive discovery metadata records"""

    click.echo(f'Archiving metadata from GDC {API_URL} to {archive_zipfile}')
    archive_metadata(archive_zipfile)


@click.command()
@click.pass_context
@click.argument('archive-zipfile')
@cli_options.OPTION_VERBOSITY
def restore(ctx, archive_zipfile, verbosity='NOTSET'):
    """Restore discovery metadata records from an archive zipfile"""

    click.echo(f'Restoring metadata {archive_zipfile} to GDC {API_URL}')
    restore_metadata(archive_zipfile)
