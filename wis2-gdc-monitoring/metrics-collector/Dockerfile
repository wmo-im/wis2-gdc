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

FROM python:3-alpine

COPY ./metrics_collector.py /app/metrics_collector.py
COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt && \
    mkdir -p /data && \
    wget -P /data https://wmo-im.github.io/wis2-topic-hierarchy/wth-bundle.zip && \
    cd /data && \
    unzip /data/wth-bundle.zip

ENV WIS2_GDC_CENTRE_ID_CSV="/data/centre-id.csv"
ENV PYTHONUNBUFFERED="true"

RUN chgrp -R 0 /app && \
    chmod -R g=u /app

USER 1001

ENTRYPOINT [ "python3","-u","/app/metrics_collector.py" ]
