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

from wis2_gdc.registrar import Registrar

LOGGER = logging.getLogger(__name__)


class DiscoveryMetadataHook(Hook):
    def execute(self, topic: str, msg_dict: dict) -> None:
        LOGGER.debug('Discovery metadata hook execution begin')
        r = Registrar()
        wcmp2_dict = r.get_wcmp2(msg_dict)
        r.register(wcmp2_dict, topic)
        LOGGER.debug('Discovery metadata hook execution end')

    def __repr__(self):
        return '<DiscoveryMetadataHook>'
