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

from wis2_gdc.registrar import register, setup, teardown, unregister
from wis2_gdc.archive import archive, restore
from wis2_gdc.sync import sync

__version__ = '0.7.0'


@click.group()
@click.version_option(version=__version__)
def cli():
    """WIS2 Global Discovery Catalogue management utilities"""

    pass


cli.add_command(setup)
cli.add_command(teardown)
cli.add_command(unregister)
cli.add_command(register)
cli.add_command(sync)
cli.add_command(archive)
cli.add_command(restore)
