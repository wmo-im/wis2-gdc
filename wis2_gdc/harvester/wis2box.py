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
#   https://www.apache.org/licenses/LICENSE-2.0
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
import urllib.request

import unicodecsv as csv
from wis2_gdc.harvester.base import BaseHarvester
from wis2_gdc.registrar import Registrar

LOGGER = logging.getLogger(__name__)

WIS2BOX_URLS = 'https://raw.githubusercontent.com/wmo-im/wis2box-demo-proxy/main/deployments.csv'  # noqa


class Wis2boxHarvester(BaseHarvester):
    def __init__(self):
        super().__init__()

    def sync(self) -> None:
        LOGGER.debug(f'Fetching: {WIS2BOX_URLS}')

        r = Registrar()

        with urllib.request.urlopen(WIS2BOX_URLS) as fh:
            metadata = csv.reader(fh)
            next(metadata)

            for row in metadata:
                url = row[-1]

                try:
                    records_url = f'{url}/oapi/collections/discovery-metadata/items'  # noqa
                    with urllib.request.urlopen(records_url) as fh2:
                        records = json.load(fh2)
                except Exception as err:
                    LOGGER.warning(f'Cannot get URL {records_url}: {err}')
                    continue

                LOGGER.debug('Iterating over all WCMP2 records')
                for record in records['features']:
                    # TODO: remove once WCMP2 is adopted
                    LOGGER.debug('Monkeypatching wmo:dataPolicy')
                    if not isinstance(record['properties']['wmo:dataPolicy'], str):  # noqa
                        dp = record['properties'].pop('wmo:dataPolicy', None)
                        record['properties']['wmo:dataPolicy'] = dp['name']

                    # TODO: remove once WCMP2 is adopted
                    LOGGER.debug('Monkeypatching themes/concepts')
                    themes = record['properties']['themes']
                    if isinstance(themes[0]['concepts'][0], str):
                        themes2 = []
                        for theme in themes:
                            theme2 = {
                                'concepts': []
                            }
                            for concept in theme['concepts']:
                                theme2['concepts'].append({
                                    'id': concept
                                })
                            if 'scheme' in theme:
                                theme2['scheme'] = theme['scheme']

                            themes2.append(theme2)

                        record['properties']['themes'] = themes2

                LOGGER.debug(f"Saving {record['id']} to catalogue")
                r.register(record)
