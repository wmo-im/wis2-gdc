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

from wmo_resource_catalogue.wigos_gofc.registrar import (
   register, setup, teardown, unregister)
from wmo_resource_catalogue.wigos_gofc.archive import archive, restore


@click.group()
def wigos_gofc():
    """WIGOS Global Observing Facility Catalogue management utilities"""

    pass


wigos_gofc.add_command(setup)
wigos_gofc.add_command(teardown)
wigos_gofc.add_command(unregister)
wigos_gofc.add_command(register)
wigos_gofc.add_command(archive)
wigos_gofc.add_command(restore)
