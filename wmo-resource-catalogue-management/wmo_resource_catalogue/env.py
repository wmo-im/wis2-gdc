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
from pathlib import Path
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


API_URL = os.environ.get('WMO_RESOURCE_CATALOGUE_API_URL')
API_URL_DOCKER = os.environ.get('WMO_RESOURCE_CATALOGUE_API_URL_DOCKER')
BACKEND_TYPE = os.environ.get('WMO_RESOURCE_CATALOGUE_BACKEND_TYPE')
BACKEND_CONNECTION = os.environ.get(
    'WMO_RESOURCE_CATALOGUE_BACKEND_CONNECTION')
BROKER_URL = os.environ.get('WMO_RESOURCE_CATALOGUE_BROKER_URL')
WIS2_GDC_CENTRE_ID = os.environ.get('WMO_RESOURCE_CATALOGUE_WIS2_GDC_CENTRE_ID')  # noqa
WIGOS_GOFC_CENTRE_ID = os.environ.get('WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_CENTRE_ID')  # noqa
CACHE_URL = os.environ.get('WMO_RESOURCE_CATALOGUE_CACHE_URL')
CACHE_RETENTION_SECONDS = int(os.environ.get('WMO_RESOURCE_CATALOGUE_CACHE_RETENTION_SECONDS', 3600))  # noqa
GB = os.environ.get('WMO_RESOURCE_CATALOGUE_GB')
GB_CENTRE_ID = None
WIS2_GDC_GB_TOPIC = os.environ.get('WMO_RESOURCE_CATALOGUE_WIS2_GDC_GB_TOPIC')
WIS2_GDC_METADATA_ARCHIVE_SOURCE = Path(
    os.environ.get('WMO_RESOURCE_CATALOGUE_WIS2_GDC_METADATA_ARCHIVE_SOURCE'))
WIS2_GDC_METADATA_ARCHIVE_ZIPFILE = os.environ.get(
    'WMO_RESOURCE_CATALOGUE_WIS2_GDC_METADATA_ARCHIVE_ZIPFILE')
WIGOS_GOFC_METADATA_ARCHIVE_SOURCE = Path(
    os.environ.get('WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_METADATA_ARCHIVE_SOURCE'))  # noqa
WIGOS_GOFC_METADATA_ARCHIVE_ZIPFILE = os.environ.get(
    'WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_METADATA_ARCHIVE_ZIPFILE')
PUBLISH_REPORTS = str2bool(
    os.environ.get('WMO_RESOURCE_CATALOGUE_PUBLISH_REPORTS', 'false'))
REJECT_ON_FAILING_ETS = str2bool(os.environ.get('WMO_RESOURCE_CATALOGUE_REJECT_ON_FAILING_ETS', 'true'))  # noqa
RUN_KPI = str2bool(os.environ.get('WMO_RESOURCE_CATALOGUE_RUN_KPI', 'false'))
EXPERIMENTAL = str2bool(
    os.environ.get('WMO_RESOURCE_CATALOGUE_EXPERIMENTAL', 'false'))

WIS2_GDC_ENABLED = str2bool(os.environ.get('WMO_RESOURCE_CATALOGUE_WIS2_GDC_ENABLED', 'true'))  # noqa
WIGOS_GOFC_ENABLED = str2bool(os.environ.get('WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_ENABLED', 'true'))  # noqa

GB_LINKS = []

REQUIRED_ENV_VARS = [API_URL, API_URL_DOCKER, BACKEND_TYPE, BACKEND_CONNECTION,
                     BROKER_URL, CACHE_URL, GB, WIS2_GDC_GB_TOPIC]

if WIS2_GDC_ENABLED:
    REQUIRED_ENV_VARS.append(WIS2_GDC_CENTRE_ID)
if WIGOS_GOFC_ENABLED:
    REQUIRED_ENV_VARS.append(WIGOS_GOFC_CENTRE_ID)

if None in REQUIRED_ENV_VARS:
    raise EnvironmentError('Environment variables not set!')

for key, value in os.environ.items():
    if key.startswith('WMO_RESOURCE_CATALOGUE_GB_LINK'):
        centre_id, url, title = value.rsplit(',', 2)
        if GB == url:
            GB_CENTRE_ID = centre_id
        GB_LINKS.append(value.split(',', 2))
