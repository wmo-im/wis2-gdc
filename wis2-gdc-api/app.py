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

from flask import Flask, Response, send_file
from pygeoapi.flask_app import BLUEPRINT as pygeoapi_blueprint
import requests

app = Flask(__name__, static_url_path='/static')
app.url_map.strict_slashes = False

app.register_blueprint(pygeoapi_blueprint, url_prefix='/')

try:
    from flask_cors import CORS
    CORS(app)
except ImportError:  # CORS needs to be handled by upstream server
    pass


@app.route('/wis2-discovery-metadata-archive.zip')
def archive():

    zip_file = os.environ.get('WIS2_GDC_METADATA_ARCHIVE_ZIPFILE')

    try:
        return send_file(zip_file, mimetype='application/zip')
    except FileNotFoundError:
        return 'Not Found', 404


@app.route('/wis2-gdc-metrics.txt')
def metrics():

    collector_url = os.environ.get('WIS2_GDC_COLLECTOR_URL')

    try:
        response = requests.get(collector_url).text
        return Response(response, mimetype='text/plain')
    except Exception:
        return 'Internal Server Error', 500


@app.route('/wis2-gdc-all-channels-latest.txt')
def wis2_gdc_all_channels_latest():

    LIVE_CHANNELS = []

    URL = os.environ.get('WIS2_GDC_BACKEND_CONNECTION')
    URL = f'{URL}/_search'

    PARAMS = {
        'size': 9999
    }

    CHANNELS = (
        'cache/a/wis2',
        'origin/a/wis2'
    )

    response = requests.get(URL, params=PARAMS)
    response = response.json()

    for feature in response['hits']['hits']:
        for link in feature['_source']['links']:
            channel = link.get('channel', '')
            if channel.startswith(CHANNELS):
                channel = '/'.join(channel.split('/')[4:])
                LIVE_CHANNELS.append(
                    ','.join([feature['_source']['id'], channel]))

    LIVE_CHANNELS = list(sorted(set(LIVE_CHANNELS)))

    return Response('\n'.join(LIVE_CHANNELS), mimetype='text/plain')
