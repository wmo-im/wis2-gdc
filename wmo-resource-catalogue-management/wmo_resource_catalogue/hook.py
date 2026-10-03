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

from pywis_pubsub.hook import Hook
import redis

from wmo_resource_catalogue.env import (
    CACHE_URL, CACHE_RETENTION_SECONDS)
from wmo_resource_catalogue.wigos_gofc.registrar import Registrar as R1
from wmo_resource_catalogue.wis2_gdc.registrar import Registrar as R2

LOGGER = logging.getLogger(__name__)


class MetadataHook(Hook):
    def execute(self, topic: str, msg_dict: dict) -> None:
        record_dict = None
        self.cache = redis.Redis().from_url(CACHE_URL, protocol=2)

        LOGGER.debug('Checking for duplicate message')
        if self.cache.get(msg_dict['id']) is not None:
            msg = f"Duplicate message {msg_dict['id']}; discarding"
            LOGGER.info(msg)
            return
        else:
            msg = f"New message {msg_dict['id']}; adding"
            LOGGER.info(msg)
            self.cache.set(
                msg_dict['id'],
                msg_dict['properties']['data_id'],
                nx=True,
                ex=CACHE_RETENTION_SECONDS
            )

        LOGGER.debug('Metadata hook execution begin')
        if '/wis2/' in topic:
            r = R2()
        elif '/wigos/' in topic:
            r = R1()

        is_deletion = list(filter(lambda d: d['rel'] == 'deletion',
                                  msg_dict['links']))
        if is_deletion:
            r.delete_record(topic, msg_dict)
            return

        record_dict = r.get_record(msg_dict, topic)

        if record_dict is not None:
            r.register(record_dict, topic)

        LOGGER.debug('Metadata hook execution end')

    def __repr__(self):
        return '<MetadataHook>'
