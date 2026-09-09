.. _configuration:

Configuration
=============

Main configuration environment variables
----------------------------------------

``wmo-resource-catalogue`` configuration is driven by the following environment variables, which are managed in ``wmo-resource-catalogue.env``:

.. csv-table:: Main environment variables
   :widths: 30 30 30
   :header: Name,Description,Default

   ``WMO_RESOURCE_CATALOGUE_LOGGING_LEVEL``,logging level as per the standard `Python logging levels`_,``ERROR``
   ``WMO_RESOURCE_CATALOGUE_API_URL``,public URL of the API,``http://localhost:8000``
   ``WMO_RESOURCE_CATALOGUE_API_URL_DOCKER``,internal Docker URL of the API,``http://wmo-resource-catalogue-api``
   ``WMO_RESOURCE_CATALOGUE_BACKEND_TYPE``,API backend type,``Elasticsearch``
   ``WMO_RESOURCE_CATALOGUE_BACKEND_CONNECTION``,API backend connection,``http://wmo-resource-catalogue-backend:9200``
   ``WMO_RESOURCE_CATALOGUE_BROKER_URL``,URL of the catalogue broker,``mqtt://wmo-resource-catalogue:wmo-resource-catalogue@wmo-resource-catalogue-broker:1883``
   ``WMO_RESOURCE_CATALOGUE_WIS2_GDC_CENTRE_ID``,centre identifier of the WIS2 GDC,``ca-eccc-msc-global-discovery-catalogue``
   ``WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_CENTRE_ID``,centre identifier of the WIGOS GOFC,``ca-eccc-msc-global-observing-facility-catalogue``
   ``WMO_RESOURCE_CATALOGUE_COLLECTOR_URL``,URL of metrics collector,``http://wmo-resource-catalogue-metrics-collector:8006``
   ``WMO_RESOURCE_CATALOGUE_GB``,WIS2 Global Broker that the catalogue connects to,``mqtts://everyone:everyone@globalbroker.meteo.fr:8883``
   ``WMO_RESOURCE_CATALOGUE_WIS2_GDC_GB_TOPIC``,WIS2 topic that the GDC subscribes to,``cache/a/wis2/+/metadata``
   ``WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_GB_TOPIC``,WIGOS topic that the GOFC subscribes to,``cache/a/wigos/+/metadata``
   ``WMO_RESOURCE_CATALOGUE_PUBLISH_REPORTS``,whether the catalogue should publish ETS and KPI reports,``true``
   ``WMO_RESOURCE_CATALOGUE_REJECT_ON_FAILING_ETS``,whether the catalogue should stop ingest based on on failing record,``true``
   ``WMO_RESOURCE_CATALOGUE_RUN_KPI``,whether the catalogue should run KPI as part of ingest,``false``
   ``WMO_RESOURCE_CATALOGUE_EXPERIMENTAL``,whether the catalogue should in experimental mode,``false``
   ``WMO_RESOURCE_CATALOGUE_CACHE_URL``,URL of the catalogue cache,``redis://wmo-resource-catalogue-cache:6379``
   ``WMO_RESOURCE_CATALOGUE_CACHE_RETENTION_SECONDS``,cache retention policy for notification messages in seconds,``3600``
   ``WMO_RESOURCE_CATALOGUE_WIS2_GDC_ENABLED``,whether to enable WIS2 GDC functionality,``true``
   ``WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_ENABLED``,whether to enable WIGOS GOFC functionality,``true``

API configuration environment variables
---------------------------------------

If you wish to update the API configuration, you can set the below values accordingly (to override the pygeoapi defaults):

.. csv-table:: pygeoapi configuration environment variables
   :widths: 30 30
   :header: Name,Description

   ``WMO_RESOURCE_CATALOGUE_SERVER_ICON``,Icon for HTML templates
   ``WMO_RESOURCE_CATALOGUE_SERVER_LOGO``,Logo/banner for HTML templates
   ``WMO_RESOURCE_CATALOGUE_METADATA_IDENTIFICATION_TITLE``,Title
   ``WMO_RESOURCE_CATALOGUE_METADATA_IDENTIFICATION_DESCRIPTION``,Description 
   ``WMO_RESOURCE_CATALOGUE_METADATA_IDENTIFICATION_TERMS_OF_SERVICE``,Terms of service
   ``WMO_RESOURCE_CATALOGUE_METADATA_IDENTIFICATION_URL``,URL related to API
   ``WMO_RESOURCE_CATALOGUE_METADATA_LICENSE_NAME``,License name
   ``WMO_RESOURCE_CATALOGUE_METADATA_LICENSE_URL``,License URL
   ``WMO_RESOURCE_CATALOGUE_METADATA_PROVIDER_NAME``,Provider name
   ``WMO_RESOURCE_CATALOGUE_METADATA_PROVIDER_URL``,Provider URL
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_NAME``,Contact name
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_POSITION``,Contact position
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_ADDRESS``,Contact address
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_CITY``,Contact city
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_STATEORPROVINCE``,Contact state or province
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_POSTALCODE``,Contact postal code
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_COUNTRY``,Contact country
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_PHONE``,Contact phone number (in format ``+xx-xxx-xxx-xxxx``)
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_FAX``,Contact fax number (in format ``+xx-xxx-xxx-xxxx``)
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_EMAIL``,Contact email
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_URL``,Contact URL
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_HOURS``,Contact hours of service
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_INSTRUCTIONS``,Contact instructions
   ``WMO_RESOURCE_CATALOGUE_METADATA_CONTACT_ROLE``,Contact role

Global Broker environment variables
-----------------------------------

WIS2 Global Broker environment variables are defined as comma-separated values (centre=id,url,centre-name).  ``wmo-resource-catalogue`` allows for 1..n Global Broker environment variables as required.

.. note::

   - the naming convention is ``WIS_GDC_GB_LINK_<LABEL>``, where ``<LABEL>`` can be named as desired to identify the GB
   - at least one Global Broker environment variable is required
   - the centre name may contain commas

An example can be found below:

.. code-block:: text

   WMO_RESOURCE_CATALOGUE_GB_LINK_METEOFRANCE,"fr-meteo-france-global-broker,mqtts://everyone:everyone@globalbroker.meteo.fr:8883,Météo-France, Global Broker Service"

Key settings
------------

A default installation with minimal configuration changes per below satisfies most use casess:

- ``WMO_RESOURCE_CATALOGUE_API_URL``
- ``WMO_RESOURCE_CATALOGUE_CENTRE_ID``
- ``WMO_RESOURCE_CATALOGUE_GB``
- ``WMO_RESOURCE_CATALOGUE_GB_LINK...``

.. note::

   The ``wmo-resource-catalogue`` Docker Compose file also contains additional environment variables (see ``docker-compose.yml`` to adjust accordingly).  In most cases, these values do not need adjustment.

.. note::

   The ``WMO_RESOURCE_CATALOGUE_WIS2_GDC_METADATA_ARCHIVE_SOURCE`` environment variable is always set by wmo-resource-catalogue to ``/data/source/wis2-gdc`` for the ``wmo-resource-catalogue-management`` container.
   The ``WMO_RESOURCE_CATALOGUE_WIS2_GDC_METADATA_ARCHIVE_ZIPFILE`` environment variable is always set by wmo-resource-catalogue to ``/data/wis2-discovery-metadata-archive.zip`` for the ``wmo-resource-catalogue-management`` and ``wmo-resource-catalogue-api`` containers.
   The ``WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_METADATA_ARCHIVE_SOURCE`` environment variable is always set by wmo-resource-catalogue to ``/data/source/wigos-gofc`` for the ``wmo-resource-catalogue-management`` container.
   The ``WMO_RESOURCE_CATALOGUE_WIGOS_GOFC_METADATA_ARCHIVE_ZIPFILE`` environment variable is always set by wmo-resource-catalogue to ``/data/wigos-observing-facility-metadata-archive.zip`` for the ``wmo-resource-catalogue-management`` and ``wmo-resource-catalogue-api`` containers.

Application specific configurations
-----------------------------------

Application specific configurations can be found in the following files (for direct editing if needed):

.. csv-table:: Application specific configuration files
   :widths: 30 30
   :header: Filepath,Description

   ``wmo-resource-catalogue-api/docker/wmo-resource-catalogue-config.yml``,pygeoapi configuration (`documentation`_)
   ``wmo-resource-catalogue-broker/docker/mosquitto.conf``,mosquitto main configuration
   ``wmo-resource-catalogue-broker/docker/acl.conf``,mosquitto access control list
   ``wmo-resource-catalogue-management/docker/pywis-pubsub.yml``,pywis-pubsub configuration
   ``wmo-resource-catalogue-monitoring/grafana/datasource.yml``,Grafana configuration
   ``wmo-resource-catalogue-monitoring/grafana/datasource.yml``,Grafana configuration
   ``wmo-resource-catalogue-monitoring/prometheus/datasource.yml``,Prometheus configuration
   
.. note::

   Application specific configurations do not need adjustment in most cases.

.. _`Python logging levels`: https://docs.python.org/library/logging.html#logging-levels
.. _`documentation`: https://docs.pygeoapi.io/en/latest/configuration.html

Connections to additional Global Brokers
----------------------------------------

By default, wmo-resource-catalogue interacts with a single Global Broker via the ``wmo-resource-catalogue-management`` service.

To connect to additional Global Brokers, any number of additional ``wmo-resource-catalogue-management`` services may be added.  For example, adding in ``docker-compose.yml``:

.. code-block:: yaml

   wmo-resource-catalogue-management2:  # update name accordingly
     container_name: wmo-resource-catalogue-management2  # update name accordingly
     build:
       context: ./wmo-resource-catalogue-management/
     env_file:
       - wmo-resource-catalogue.env
     environment:
       - WMO_RESOURCE_CATALOGUE_API_URL_DOCKER=http://wmo-resource-catalogue-api:8080
       - WMO_RESOURCE_CATALOGUE_GB=mqtts://everyone:everyone@globalbroker.inmet.br:8883  # override default WMO_RESOURCE_CATALOGUE_GB
     depends_on:
       wmo-resource-catalogue-backend:
         condition: service_healthy
       wmo-resource-catalogue-cache:
         condition: service_healthy
     healthcheck:
       test: ["CMD", "curl", "-f", "http://wmo-resource-catalogue-backend:9200/wis2-discovery-metadata"]
       interval: 1m
       retries: 3
     volumes:
       - wmo-resource-catalogue-management-data2:/data  # update volume accordingly
     restart: always
     command: ["/venv/bin/pywis-pubsub", "subscribe", "--config", "/app/docker/pywis-pubsub.yml", "--verbosity", "DEBUG"]
     networks:
       - wmo-resource-catalogue-net
     <<: *logging

...then adding the associated volume:

.. code-block:: yaml

   volumes:
     wmo-resource-catalogue-backend-data:
     wmo-resource-catalogue-management-data:
     wmo-resource-catalogue-management2-data:  # added volume
