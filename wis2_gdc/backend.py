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

from abc import ABC, abstractmethod
import logging

from wis2_gdc import env

LOGGER = logging.getLogger(__name__)


class Backend(ABC):
    def __init__(self, defs):
        self.defs = defs

    @abstractmethod
    def save(self, record: dict) -> None:
        """
        Upsert a resource to a backend

        :param payload: `dict` of resource

        :returns: `None`
        """

        raise NotImplementedError()


class ElasticsearchBackend(Backend):

    def save(self, record: dict) -> None:

        from urllib.parse import urlparse

        from elasticsearch import Elasticsearch

        self.url_parsed = urlparse(self.defs.get('connection'))
        self.index_name = self.url_parsed.path.lstrip('/')

        url2 = f'{self.url_parsed.scheme}://{self.url_parsed.netloc}'

        if self.url_parsed.path.count('/') > 1:
            LOGGER.debug('ES URL has a basepath')
            basepath = self.url_parsed.path.split('/')[1]
            self.index_name = self.url_parsed.path.split('/')[-1]
            url2 = f'{url2}/{basepath}/'

        print(f'ES URL: {url2}')
        print(f'ES index: {self.index_name}')

        settings = {
            'hosts': [url2],
            'retry_on_timeout': True,
            'max_retries': 10,
            'timeout': 30
        }

        if self.url_parsed.username and self.url_parsed.password:
            settings['http_auth'] = (
                self.url_parsed.username, self.url_parsed.password)

        es = Elasticsearch(**settings)

        LOGGER.debug(record)
        es.index(index=self.index_name, id=record['id'], body=record)


class OGCAPI(Backend):

    def save(self):

        import json

        from owslib.ogcapi import Records

        oarec = Records(env.API_URL)
        collection = 'discovery-metadata'
        ttype = 'create'

        try:
            _ = oarec.get_collection_item(self.metadata['id'])
            ttype = 'update'
        except Exception:
            pass

        payload = json.dumps(self.metadata)

        if ttype == 'create':
            LOGGER.debug('Adding new record to catalogue')
            _ = oarec.get_collection_create(collection, payload)
        elif ttype == 'update':
            LOGGER.debug('Updating existing record in catalogue')
            _ = oarec.get_collection_update(collection, payload)


BACKENDS = {
    'Elasticsearch': ElasticsearchBackend
}
