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

import logging
from urllib.parse import urlparse

from elasticsearch import Elasticsearch

from wis2_gdc.backend.base import BaseBackend

LOGGER = logging.getLogger(__name__)


class ElasticsearchBackend(BaseBackend):

    from urllib.parse import urlparse
    from elasticsearch import Elasticsearch

    def __init__(self, defs):
        super().__init__(defs)

        # default index settings
        self.ES_SETTINGS = {
            'settings': {
                'number_of_shards': 1,
                'number_of_replicas': 0
            },
            'mappings': {
                'properties': {
                    'id': {
                        'type': 'text',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'geometry': {
                        'type': 'geo_shape'
                    },
                    'time': {
                        'properties': {
                            'interval': {
                                'type': 'date',
                                'null_value': '1850',
                                'format': 'year||year_month||year_month_day||date_time||t_time||t_time_no_millis',  # noqa
                                'ignore_malformed': True
                            }
                        }
                    },
                    'properties': {
                        'properties': {
                            'type': {
                                'type': 'text',
                                'fields': {
                                    'raw': {
                                        'type': 'keyword'
                                    }
                                }
                            },
                            'title': {
                                'type': 'text',
                                'fields': {
                                    'raw': {
                                        'type': 'keyword'
                                    }
                                }
                            },
                            'description': {
                                'type': 'text',
                                'fields': {
                                    'raw': {
                                        'type': 'keyword'
                                    }
                                }
                            },
                            'wmo:dataPolicy': {
                                'type': 'text',
                                'fields': {
                                    'raw': {
                                        'type': 'keyword'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        self.url_parsed = urlparse(self.defs.get('connection'))
        self.index_name = self.url_parsed.path.lstrip('/')

        url2 = f'{self.url_parsed.scheme}://{self.url_parsed.netloc}'

        if self.url_parsed.port is None:
            LOGGER.debug('No port found; trying autodetect')
            port = None
            if self.url_parsed.scheme == 'http':
                port = 80
            elif self.url_parsed.scheme == 'https':
                port = 443
            if port is not None:
                url2 = f'{self.url_parsed.scheme}://{self.url_parsed.netloc}:{port}'  # noqa

        if self.url_parsed.path.count('/') > 1:
            LOGGER.debug('ES URL has a basepath')
            basepath = self.url_parsed.path.split('/')[1]
            self.index_name = self.url_parsed.path.split('/')[-1]
            url2 = f'{url2}/{basepath}/'

        LOGGER.debug(f'ES URL: {url2}')
        LOGGER.debug(f'ES index: {self.index_name}')

        settings = {
            'hosts': [url2],
            'retry_on_timeout': True,
            'max_retries': 10,
            'timeout': 30
        }

        if self.url_parsed.username and self.url_parsed.password:
            settings['http_auth'] = (
                self.url_parsed.username, self.url_parsed.password)

        LOGGER.debug(f'Settings: {settings}')
        self.es = Elasticsearch(**settings)

    def setup(self) -> None:
        if self.es.indices.exists(index=self.index_name):
            LOGGER.debug(f'Deleting index {self.index_name}')
            self.es.indices.delete(index=self.index_name)

        LOGGER.debug(f'Creating index {self.index_name}')
        self.es.indices.create(index=self.index_name, body=self.ES_SETTINGS)

    def save(self, record: dict) -> None:
        LOGGER.debug(f"Indexing record {record['id']}")
        self.es.index(index=self.index_name, id=record['id'], body=record)
