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

import logging
import json

from owslib.ogcapi.records import Records

from wis2_gdc import env
from wis2_gdc.backend.base import BaseBackend

LOGGER = logging.getLogger(__name__)


class OGCAPIRecordsBackend(BaseBackend):

    def __init__(self, defs):
        super().__init__(defs)

        self.conn = Records(env.API_URL)
        self.collection = 'discovery-metadata'

    def save_record(self):

        ttype = 'create'

        try:
            _ = self.conn.get_collection_item(self.metadata['id'])
            ttype = 'update'
        except Exception:
            pass

        payload = json.dumps(self.metadata)

        if ttype == 'create':
            LOGGER.debug('Adding new record to catalogue')
            _ = self.conn.get_collection_create(self.collection, payload)
        elif ttype == 'update':
            LOGGER.debug('Updating existing record in catalogue')
            _ = self.conn.get_collection_update(self.collection, payload)

    def record_exists(self, identifier: str) -> bool:
        LOGGER.debug(f'Querying GDC for id {identifier}')
        try:
            _ = self.conn.collection_item(self.collection, identifier)
            return True
        except RuntimeError:
            return False

    def __repr__(self):
        return '<OGCAPIRecordsBackend>'
