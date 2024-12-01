.. _configuration:

Configuration
=============

Main configuration environment variables
----------------------------------------

``wis2-gdc`` configuration is driven by the following environment variables, which are managed in ``wis2-gdc.env``:

.. csv-table:: Main environment variables
   :widths: 30 30 30
   :header: Name,Description,Default

   ``WIS2_GDC_LOGGING_LEVEL``,logging level as per the standard `Python logging levels`_,``ERROR``
   ``WIS2_GDC_API_URL``,public URL of the GDC API,``http://localhost``
   ``WIS2_GDC_API_URL_DOCKER``,internal Docker URL of the API,``http://wis2-gdc-api``
   ``WIS2_GDC_BACKEND_TYPE``,API backend type,``Elasticsearch``
   ``WIS2_GDC_BACKEND_CONNECTION``,API backend connection,``http://wis2-gdc-backend:9200/wis2-discovery-metadata``
   ``WIS2_GDC_BROKER_URL``,URL of the GDC broker,``mqtt://wis2-gdc:wis2-gdc@wis2-gdc-broker:1883``
   ``WIS2_GDC_CENTRE_ID``,centre identifier of the GDC,``ca-eccc-msc-global-discovery-catalogue``
   ``WIS2_GDC_COLLECTOR_URL``,URL of metrics collector,``http://wis2-gdc-metrics-collector:8006``
   ``WIS2_GDC_GB``,WIS2 Global Broker that the GDC connects to,``mqtts://everyone:everyone@globalbroker.meteo.fr:8883``
   ``WIS2_GDC_GB_TOPIC``,WIS2 topic that the GDC subscribes to,``cache/a/wis2/+/metadata/#``
   ``WIS2_GDC_METADATA_ARCHIVE_ZIPFILE``,filepath to the metadata archive zipfile,``/data/wis2-gdc-archive.zip``
   ``WIS2_GDC_PUBLISH_REPORTS``,whether the GDC should publish ETS and KPI reports,``true``
   ``WIS2_GDC_REJECT_ON_FAILING_ETS``,whether the GDC should stop ingest based on on failing record,``true``
   ``WIS2_GDC_RUN_KPI``,whether the GDC should run KPI as part of ingest,``false``

API configuration environment variables
---------------------------------------

If you wish to update the API configuration, you can set the below values accordingly (to override the pygeoapi defaults):

.. csv-table:: pygeoapi configuration environment variables
   :widths: 30 30
   :header: Name,Description

   ``WIS2_GDC_METADATA_IDENTIFICATION_TITLE``,API title
   ``WIS2_GDC_METADATA_IDENTIFICATION_DESCRIPTION``,API description 
   ``WIS2_GDC_METADATA_IDENTIFICATION_KEYWORDS``,API keywords
   ``WIS2_GDC_METADATA_IDENTIFICATION_TERMS_OF_SERVICE``,API terms of service
   ``WIS2_GDC_METADATA_IDENTIFICATION_URL``,URL related to API
   ``WIS2_GDC_METADATA_LICENSE_NAME``,API license name
   ``WIS2_GDC_METADATA_LICENSE_URL``,API license URL
   ``WIS2_GDC_METADATA_PROVIDER_NAME``,API provider name
   ``WIS2_GDC_METADATA_PROVIDER_URL``,API provider URL
   ``WIS2_GDC_METADATA_CONTACT_NAME``,API contact name
   ``WIS2_GDC_METADATA_CONTACT_POSITION``,API contact position
   ``WIS2_GDC_METADATA_CONTACT_ADDRESS``,API contact address
   ``WIS2_GDC_METADATA_CONTACT_CITY``,API contact city
   ``WIS2_GDC_METADATA_CONTACT_STATEORPROVINCE``,API contact state or province
   ``WIS2_GDC_METADATA_CONTACT_POSTALCODE``,API contact postal code
   ``WIS2_GDC_METADATA_CONTACT_COUNTRY``,API contact country
   ``WIS2_GDC_METADATA_CONTACT_PHONE``,API contact phone number (in format ``+xx-xxx-xxx-xxxx``)
   ``WIS2_GDC_METADATA_CONTACT_FAX``,API contact fax number (in format ``+xx-xxx-xxx-xxxx``)
   ``WIS2_GDC_METADATA_CONTACT_EMAIL``,API contact email
   ``WIS2_GDC_METADATA_CONTACT_URL``,API contact URL
   ``WIS2_GDC_METADATA_CONTACT_HOURS``,API contact hours of service
   ``WIS2_GDC_METADATA_CONTACT_INSTRUCTIONS``,API contact instructions
   ``WIS2_GDC_METADATA_CONTACT_ROLE``,API contact role

Global Broker environment variables
-----------------------------------

WIS2 Global Broker environment variables are defined as comma-separated values (centre=id,url,centre-name).  ``wis2-gdc`` allows for 1..n Global Broker environment variables as required.

.. note::

   - the naming convention is ``WIS_GDC_GB_LINK_<LABEL>``, where ``<LABEL>`` can be named as desired to identify the GB
   - at least one Global Broker environment variable is required
   - the centre name may contain commas

An example can be found below:

.. code-block:: csv

   WIS2_GDC_GB_LINK_METEOFRANCE,"fr-meteo-france-global-broker,mqtts://everyone:everyone@globalbroker.meteo.fr:8883,Météo-France, Global Broker Service"

Key settings
------------

A default installation with minimal configuration changes per below satisfies most use casess:

- ``WIS2_GDC_API_URL``
- ``WIS2_GDC_CENTRE_ID``
- ``WIS2_GDC_GB``
- ``WIS2_GDC_GB_LINK...``

.. note::

   The ``wis2-gdc`` Docker Compose file also contains additional environment variables (see ``docker-compose.yml`` to adjust accordingly).  In most cases, these values do not need adjustment.

Application specific configurations
-----------------------------------

Application specific configurations can be found in the following files (for direct editing if needed):

.. csv-table:: Application specific configuration files
   :widths: 30 30
   :header: Filepath,Description

   ``wis2-gdc-api/docker/wis2-gdc-config.yml``,pygeoapi configuration (`documentation`_)
   ``wis2-gdc-broker/docker/mosquitto.conf``,mosquitto main configuration
   ``wis2-gdc-broker/docker/acl.conf``,mosquitto access control list
   ``wis2-gdc-management/docker/pywis-pubsub.yml``,pywis-pubsub configuration
   ``wis2-gdc-monitoring/grafana/datasource.yml``,Grafana configuration
   ``wis2-gdc-monitoring/grafana/datasource.yml``,Grafana configuration
   ``wis2-gdc-monitoring/prometheus/datasource.yml``,Prometheus configuration
   
.. note::

   Application specific configurations do not need adjustment in most cases.

.. _`Python logging levels`: https://docs.python.org/library/logging.html#logging-levels
.. _`documentation`: https://docs.pygeoapi.io/en/latest/configuration.html
