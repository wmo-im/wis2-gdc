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

# wis2-gdc entry script

echo "START /entrypoint.sh"

if [ "${WIS2_GDC_ENABLE_CRON}" = "true" ]; then
  echo "Enabling cron"
  crontab /app/docker/wis2-gdc-management.cron
  echo "Crontab for current user:"
  crontab -l
fi

echo "Caching WNM schema"
pywis-pubsub schema sync

echo "Caching WCMP schemas"
pywcmp bundle sync

echo "Setting up discovery metadata backend"
wis2-gdc setup -y

echo "END /entrypoint.sh"
exec "$@"