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

from datetime import datetime, UTC
import logging
import uuid

from wis2_gdc.env import CENTRE_ID

LOGGER = logging.getLogger(__name__)

DATASCHEMAS = {
    'ets': 'https://raw.githubusercontent.com/wmo-im/wis2-monitoring-events/refs/heads/main/schemas/wcmp2-ets-bundled.json',  # noqa
    'kpi': 'https://raw.githubusercontent.com/wmo-im/wis2-monitoring-events/refs/heads/main/schemas/wcmp2-kpi-bundled.json'  # noqa
}


def generate_wme(subject: str, report_type: str, data: dict) -> dict:
    """
    Generate WIS2 Monitoring Event Message of WCMP2 report

    :param subject: `str` of centre-id being reported
    :param report_type: `str` of WCMP2 report type (default is ets)

    :returns: `dict` of WMEM
    """

    return {
        'specversion': '1.0',
        'type': 'int.wmo.wis2.wme.report.wcmp2.{report_type}',
        'source': CENTRE_ID,
        'subject': subject,
        'id': str(uuid.uuid4()),
        'time': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'datacontenttype': 'application/json',
        'dataschema': DATASCHEMAS[report_type],
        'data': data
    }
