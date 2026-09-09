.. _introduction:

Introduction
============

``wmo-resource-catalogue`` is a Reference Implementation of the following WMO metadata standards and services:

* `WIS2`_ Global Discovery Catalogue (GDC) as defined in the `Guide to WIS, Volume II: WIS 2.0`_.
* `WIGOS`_ Global Observing Facility Catalogue (GOFC) as defined in TODO.

``wmo-resource-catalogue`` is `open source <https://opensource.org>`_ and released under an Apache 2 :ref:`license`.

Features
--------

* fully compliant WIS2 Global Discovery Catalogue (GDC) (as per the `WIS2 Guide component definition`_ and `WIS2 Guide technical considerations`_)
* fully compliant WIGOS Global Observing Facility Catalogue (GOFC) (as per TODO)
* metadata / catalogue / search engine
* WCMP2 validation as a service
* WMDR2 validation as a service
* out of the box modern OGC API compliant server:

  * `OGC API - Records`_
  * `OGC API - Processes`_
* easy to use OpenAPI / Swagger documentation for developers
* supports JSON, GeoJSON, and HTML output
* supports metadata filtering by spatial, temporal freetext or attribute queries
* easy to deploy: Docker / Docker Compose based setup and configuration

.. _`WIS2`: https://community.wmo.int/en/activity-areas/wis
.. _`WIGOS`: https://community.wmo.int/en/activity-areas/wigos
.. _`Guide to WIS, Volume II: WIS 2.0`: https://wmo-im.github.io/wis2-guide/guide/wis2-guide-APPROVED.html
.. _`WIS2 Guide component definition`: https://wmo-im.github.io/wis2-guide/guide/wis2-guide-APPROVED.html#_2_4_4_global_discovery_catalogue
.. _`WIS2 Guide technical considerations`: https://wmo-im.github.io/wis2-guide/guide/wis2-guide-APPROVED.html#_2_7_5_global_discovery_catalogue
.. _`OGC API - Records`: https://ogcapi.ogc.org/records
.. _`OGC API - Processes`: https://ogcapi.ogc.org/processes
