#!/bin/bash
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

# pygeoapi entry script

echo "START /entrypoint.sh"

set +e

# gunicorn env settings with defaults
SCRIPT_NAME="/"
CONTAINER_NAME="wis2-gdc-api"
CONTAINER_HOST=${CONTAINER_HOST:=0.0.0.0}
CONTAINER_PORT=${CONTAINER_PORT:=80}
WSGI_WORKERS=${WSGI_WORKERS:=4}
WSGI_WORKER_TIMEOUT=${WSGI_WORKER_TIMEOUT:=6000}
WSGI_WORKER_CLASS=${WSGI_WORKER_CLASS:=gevent}

# What to invoke: default is to run gunicorn server
entry_cmd=${1:-run}

# Shorthand
function error() {
    echo "ERROR: $@"
    exit -1
}

# Workdir
cd /pygeoapi

# Lock all Python files (for gunicorn hot reload)
find . -type f -name "*.py" | xargs chmod -R 0444

echo "Trying to generate OpenAPI document"
pygeoapi openapi generate ${PYGEOAPI_CONFIG} --output-file ${PYGEOAPI_OPENAPI}

[[ $? -ne 0 ]] && error "ERROR: OpenAPI document could not be generated"

echo "openapi.yml generated continue to pygeoapi"

case ${entry_cmd} in
    # Run pygeoapi server
    run)
        # SCRIPT_NAME should not have value '/'
        [[ "${SCRIPT_NAME}" = '/' ]] && export SCRIPT_NAME="" && echo "make SCRIPT_NAME empty from /"

        echo "Start gunicorn name=${CONTAINER_NAME} on ${CONTAINER_HOST}:${CONTAINER_PORT} with ${WSGI_WORKERS} workers and SCRIPT_NAME=${SCRIPT_NAME}"
        exec gunicorn --workers ${WSGI_WORKERS} \
                --worker-class=${WSGI_WORKER_CLASS} \
                --timeout ${WSGI_WORKER_TIMEOUT} \
                --name=${CONTAINER_NAME} \
                --bind ${CONTAINER_HOST}:${CONTAINER_PORT} \
                --reload \
                --reload-extra-file ${PYGEOAPI_CONFIG} \
                pygeoapi.app:app
      ;;
    *)
      error "unknown command arg: must be run (default)"
      ;;
esac

echo "END /entrypoint.sh"

