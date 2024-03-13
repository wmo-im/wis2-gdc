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

import os
from typing import Any


def str2bool(value: Any) -> bool:
    """
    helper function to return Python boolean
    type (source: https://stackoverflow.com/a/715468)

    :param value: value to be evaluated

    :returns: `bool` of whether the value is boolean-ish
    """

    value2 = False

    if isinstance(value, bool):
        value2 = value
    else:
        value2 = value.lower() in ('yes', 'true', 't', '1', 'on')

    return value2


API_URL = os.environ.get('WIS2_GDC_API_URL')
API_URL_DOCKER = os.environ.get('WIS2_GDC_API_URL_DOCKER')
BACKEND_TYPE = os.environ.get('WIS2_GDC_BACKEND_TYPE')
BACKEND_CONNECTION = os.environ.get('WIS2_GDC_BACKEND_CONNECTION')
BROKER_URL = os.environ.get('WIS2_GDC_BROKER_URL')
CENTRE_ID = os.environ.get('WIS2_GDC_CENTRE_ID')
GB = os.environ.get('WIS2_GDC_GB')
GB_TOPIC = os.environ.get('WIS2_GDC_GB_TOPIC')
OPENMETRICS_FILE = os.environ.get('WIS2_GDC_OPENMETRICS_FILE')
PUBLISH_REPORTS = str2bool(os.environ.get('WIS2_GDC_PUBLISH_REPORTS', 'false'))
REJECT_ON_FAILING_ETS = str2bool(os.environ.get('WIS2_GDC_REJECT_ON_FAILING_ETS', 'true'))  # noqa
RUN_KPI = str2bool(os.environ.get('WIS2_GDC_RUN_KPI', 'false'))

GB_LINKS = []

if None in [API_URL, API_URL_DOCKER, BACKEND_TYPE,
            BACKEND_CONNECTION, BROKER_URL, CENTRE_ID,
            GB, GB_TOPIC, OPENMETRICS_FILE]:
    raise EnvironmentError('Environment variables not set!')

for key, value in os.environ.items():
    if key.startswith('WIS2_GDC_GB_LINK'):
        GB_LINKS.append(value.split(','))
