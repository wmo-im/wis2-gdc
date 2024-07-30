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

LOGGER = logging.getLogger(__name__)


class BaseBackend(ABC):
    def __init__(self, defs):
        self.defs = defs

    @abstractmethod
    def setup(self) -> None:
        """
        Setup a backend

        :returns: `None`
        """

        raise NotImplementedError()

    @abstractmethod
    def teardown(self) -> None:
        """
        Tear down a backend

        :returns: `None`
        """

        raise NotImplementedError()

    @abstractmethod
    def save(self, record: dict) -> None:
        """
        Upsert a resource to a backend

        :param payload: `dict` of resource

        :returns: `None`
        """

        raise NotImplementedError()

    @abstractmethod
    def exists(self) -> bool:
        """
        Querying whether backend exists

        :returns: `bool` of whether backend exists
        """

        raise NotImplementedError()

    @abstractmethod
    def record_exists(self, identifier: str) -> bool:
        """
        Querying whether a record exists in a backend

        :param identifier: `str` of record identifier

        :returns: `bool` of whether record exists in backend
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseBackend>'
