.. _api:

API
===

The WIS2 GDC provides a search API according to the GDC `technical considerations`_ in the WIS2 Guide, supporting
the `OGC API - Records`_ standard.

Overview
--------

The wis2-gdc OGC API - Records API is powered by `pygeoapi`_, an OGC API Reference Implementation, and contains
the following resources:

.. list-table:: GDC API main endpoints
   :widths: 30, 70
   :header-rows: 1

   * - Resource type
     - Endpoint
   * - OpenAPI/Swagger API description
     - ``/openapi``
   * - WCMP2 records
     - ``/collections/wis2-discovery-metadata``
   * - WCMP2 validation
     - ``/processes/pywcmp-wis2-wcmp2-ets/execution``
   * - WCMP2 quality assessment
     - ``/processes/pywcmp-wis2-wcmp2-kpi/execution``

OpenAPI/Swagger
---------------

The easiest way to test the GDC API is using the Swagger endpoint, which allows for testing various capabilities
and queries into the GDC.

.. image:: /_static/gdc-api-swagger.png
   :width: 80%
   :alt: GDC API Swagger endpoint

Discovery
---------

The GDC API allows for a wide range of query predicates to search for data in WIS2 as per the OGC API - Records - Part 1: Core specification.

The GDC can be searched via the ``/collections/wis2-discovery-metadata/items`` endpoint.  This endpoint provides a number query parameters as described in the examples below.

**NOTE**: examples below are not URL encoded for clarity / readability, but should be when interacting with the GDC API.

Spatial queries
^^^^^^^^^^^^^^^

- search for metadata records of data in Canada: ``bbox=-142,42,-52,84``

Note that the format of `bbox` is comma-separated values in the following order:

- minimum longitude
- minimum latitude
- maximum longitude
- maximum latitude

Temporal queries
^^^^^^^^^^^^^^^^

- search for metadata records updated since 29 July 2024: ``datetime=2024-07-29/..``
- search for metadata records updated before 29 July 2024: ``datetime=../2024-07-29``
- search for metadata records updated on 29 July 2024: ``datetime=2024-07-29``

Equality queries
^^^^^^^^^^^^^^^^

- search for metadata records whose title contains the terms hourly observations: ``title=hourly observations``
- search for metadata records whose title contains the terms hourly or observations: ``title=hourly | observations``
- search for metadata records for a specific contact organization ``contacts.addresses.organization=Direction Generale de la Météorologie``

Freetext search
^^^^^^^^^^^^^^^

- search metadata records for temperature: `q=temperature``
- search metadata records for GRIB2 data: ``q=GRIB2``
- search metadata records for any GRIB data: ``q=\*GRIB*``
- search metadata records for any GRIB data in Germany: ``q=*GRIB* AND germany``
- search for either GRIB data or data in Europe with subscriptions to the Météo-France Global Broker: ``q=(\*GRIB* OR \*Europe*) AND \*globalbroker*``
- search for data from Belize with MQTT subscription capabilities: ``q="cache/a/wis2/bz-nms"``

Sorting
^^^^^^^

- sort search results by title, ascending: ``sortby=title``
- sort search results by title, descending: ``sortby=-title``

Paging
^^^^^^

- present search results 1-10: ``limit=10``
- present search results 11-20: ``limit=10&offset=10``
- limit to 3 search results: ``limit=3``

Finding data subscription services
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The GDC API contains both real-time and non real-time data.  A typical WCMP2 distribution link for data subscriptions can be found below:

.. code-block:: json

   {
     "rel": "items",
     "href": "mqtts://everyone:everyone@globalbroker.meteo.fr:8883",
     "channel": "origin/a/wis2/ca-eccc-msc/data/core/hydrology",
     "type": "application/geo+json",
     "title": "Data notifications"
   }


.. note::

   The ``channel`` property represents WIS2 topic which can be used to subscribe to the ``href`` property (i.e. the MQTT address) of the Global Broker (GB).

Programmatically, a GDC client can query the catalogue and filter the results for real-time subscriptions in the following manner:

.. code-block:: python

  import requests

  response = requests.get('https://wis2-gdc.weather.gc.ca/collections/wis2-discovery-metadata/items').json()

  def is_wis2_subscription_link(link) -> bool:
      if (link['href'].startswith('mqtt') and 
              link.get('channel', '').startswith(('origin/a/wis2', 'cache/a/wis2'))):
          return True

  for feature in response['features']:
      for link in feature['links']:
          if is_wis2_subscription_link(link):
              print('WIS2 subscription link')

Using the ``href`` and ``channel`` properties of a matching link object, a client can connect and subscribe to data notifications for a given dataset.

Validation and quality assessment
---------------------------------

The GDC API provides processes to validate WCMP2 records (required by WIS2) and perform quality assessment as a value added service.  Both processes
utilize the `pywcmp`_ package to achieve this capability.

The Swagger interface will provide a sample WCMP2 record as part of the JSON request payload example.  To validate a specific WCMP2, copy/paste the
WCMP2 record, replacing the contents of the ``record`` property in the example request payload.  If the WCMP2 record is a link, provide the link instead,
as the value of the ``record`` property.

Interfaces for both ETS validation and KPI quality assessment take the same inputs and provide similar output reports.

.. image:: /_static/gdc-api-swagger-process-ets.png
   :width: 80%
   :alt: GDC API Swagger Process for WCMP2 validation


.. _`technical considerations`: https://wmo-im.github.io/wis2-guide/guide/wis2-guide-APPROVED.html#_2_7_5_global_discovery_catalogue
.. _`OGC API - Records`: https://docs.ogc.org/is/20-004r1/20-004r1.html
.. _`pygeoapi`: https://pygeoapi.io
.. _`WCMP2 Abstract Test Suite`: https://wmo-im.github.io/wcmp2/standard/wcmp2-STABLE.html#_conformance_class_abstract_test_suite_normative
.. _`WCMP2 Key Performance Indicators`: https://wmo-im.github.io/wcmp2/kpi/wcmp2-kpi-DRAFT.html
.. _`pywcmp`: https://github.com/World-Meteorological-Organization/pywcmp
