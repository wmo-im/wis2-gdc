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

import click

from pywis_pubsub import cli_options

from wis2_gdc.harvester import HARVESTERS


@click.command
@click.argument('harvest_type', nargs=1,
                type=click.Choice(list(HARVESTERS.keys())))
@cli_options.OPTION_VERBOSITY
def sync(harvest_type, verbosity):
    """Synchronization utilities"""

    harvesters = list(HARVESTERS.keys())

    if harvest_type not in harvesters:
        msg = f'Invalid harvester (supported harvesters: {harvesters})'
        raise click.ClickException(msg)

    click.echo(f'Harvesting {harvest_type}')
    harvester = HARVESTERS[harvest_type]()

    harvester.sync()
