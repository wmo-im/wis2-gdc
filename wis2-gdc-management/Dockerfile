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
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

FROM ubuntu:jammy

LABEL maintainer="tomkralidis@gmail.com"

ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    DEBIAN_PACKAGES="bash cron curl git python3-pip python3-setuptools vim"

# copy the app
COPY ./ /app

# add to crontab
COPY ./docker/wis2-gdc-management.cron /var/spool/cron/crontabs/wis2-gdc

RUN apt-get update -y && \
    # install dependencies
    apt-get install -y ${DEBIAN_PACKAGES} && \
    pip3 install --no-cache-dir -r /app/requirements-backend.txt && \
    # install wis2-gdc
    cd /app && \
    pip3 install -e . && \
    chmod +x /app/docker/entrypoint.sh && \
    # cleanup
    apt autoremove -y && \
    apt-get -q clean && \
    rm -rf /var/lib/apt/lists/* && \
    chmod 0644 /var/spool/cron/crontabs/wis2-gdc && \
    crontab /var/spool/cron/crontabs/wis2-gdc && \
    # add wis2-gdc user
    useradd -ms /bin/bash wis2-gdc

USER wis2-gdc

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]
