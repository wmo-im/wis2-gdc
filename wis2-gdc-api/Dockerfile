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

FROM geopython/pygeoapi:0.20.0

LABEL maintainer="Tom Kralidis <tomkralidis@gmail.com>"

ENV PYGEOAPI_CONFIG=/pygeoapi/local.config.yml
ENV PYGEOAPI_OPENAPI=/pygeoapi/local.openapi.yml

RUN apt-get update && \
    apt-get install -y curl

COPY ./app.py /pygeoapi/pygeoapi/app.py
COPY ./pygeoapi_provider_elasticsearch_2025-03-30.py /pygeoapi/pygeoapi/provider/elasticsearch_.py
COPY ./requirements.txt /app/docker/wis2-gdc-api/requirements.txt
COPY ./docker/entrypoint.sh /app/docker/wis2-gdc-api/entrypoint.sh
COPY ./docker/wis2-gdc-api.yml /pygeoapi/local.config.yml
COPY ./templates/collections/items/item.html /pygeoapi/pygeoapi/templates/collections/items/item.html

RUN pip3 install -r /app/docker/wis2-gdc-api/requirements.txt && \
    pywcmp bundle sync && \
    chmod +x /app/docker/wis2-gdc-api/entrypoint.sh

ENTRYPOINT [ "/app/docker/wis2-gdc-api/entrypoint.sh" ]
