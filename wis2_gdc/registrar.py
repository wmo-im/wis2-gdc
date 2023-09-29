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

import click

from pywis_pubsub import cli_options
from pywis_pubsub.subscribe import get_data

from wis2_gdc.backend import BACKENDS
from wis2_gdc.env import BACKEND_TYPE, BACKEND_CONNECTION

LOGGER = logging.getLogger(__name__)


class Registrar:
    def __init__(self):
        self.metadata = None

    def register(self, metadata: dict):
        self.metadata = metadata
        LOGGER.debug(f'Metadata: {self.metadata}')
        LOGGER.debug(f'Publishing metadata to {BACKEND_TYPE} ({BACKEND_CONNECTION})')  # noqa
        self._publish()

    def _run_ets(self):
        pass

    def _run_kpi(self):
        pass

    def _publish(self):
        backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})

        backend.save(self.metadata)


@click.command()
@click.pass_context
@click.option('--yes', '-y', 'bypass', is_flag=True, default=False,
              help='Bypass permission prompts')
@cli_options.OPTION_VERBOSITY
def setup(ctx, bypass, verbosity='NOTSET'):
    """Create GDC backend"""

    if not bypass:
        if not click.confirm('Create GDC backends?  This will overwrite existing collections', abort=True):  # noqa
            return

    backend = BACKENDS[BACKEND_TYPE]({'connection': BACKEND_CONNECTION})
    LOGGER.debug(f'Backend: {backend}')
    backend.setup()


@click.command()
@click.pass_context
@click.argument('path')
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
