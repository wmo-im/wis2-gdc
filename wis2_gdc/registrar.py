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

import click
from owslib.ogcapi.records import Records

from pywis_pubsub import cli_options
from pywis_pubsub.subscribe import get_data

from wis2_gdc.env import API_URL

LOGGER = logging.getLogger(__name__)


class Registrar:
    def __init__(self):
        self.metadata = None

    def register(self, metadata: dict):
        if 'conformsTo' in metadata:
            LOGGER.debug('Discovery metadata detected')
            self.metadata = metadata
        elif 'version' in metadata:
            LOGGER.debug('Notification metadata detected')
            self.metadata = get_data(metadata)

    def _run_ats(self):
        pass

    def _run_kpi(self):
        pass

    def _publish(self):
        oarec = Records(API_URL)
        collection = 'discovery-metadata'
        ttype = 'create'

        try:
            _ = oarec.get_collection_item(self.metadata['id'])
            ttype = 'update'
        except Exception:
            pass

        payload = json.dumps(self.metadata)

        if ttype == 'create':
            LOGGER.debug('Adding new record to catalogue')
            _ = oarec.get_collection_create(collection, payload)
        elif ttype == 'update':
            LOGGER.debug('Updating existing record in catalogue')
            _ = oarec.get_collection_update(collection, payload)


@click.command()
@click.pass_context
@click.argument('metadata', type=click.File())
@cli_options.OPTION_VERBOSITY
def register(ctx, metadata, verbosity='NOTSET'):
    """Register discovery metadata"""

    m = json.load(metadata)

    r = Registrar()

    r.register(m)
