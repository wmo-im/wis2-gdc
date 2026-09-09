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

from wmo_resource_catalogue.util import get_package_version
from wmo_resource_catalogue.wis2_gdc.registrar import (
   register, setup, teardown, unregister)
from wmo_resource_catalogue.wis2_gdc.metrics import metrics
from wmo_resource_catalogue.wis2_gdc.archive import archive, restore
from wmo_resource_catalogue.wis2_gdc.sync import sync


@click.group()
@click.version_option(version=get_package_version())
def wis2_gdc():
    """WIS2 Global Discovery Catalogue management utilities"""

    pass


wis2_gdc.add_command(setup)
wis2_gdc.add_command(teardown)
wis2_gdc.add_command(unregister)
wis2_gdc.add_command(register)
wis2_gdc.add_command(sync)
wis2_gdc.add_command(archive)
wis2_gdc.add_command(restore)
wis2_gdc.add_command(metrics)
