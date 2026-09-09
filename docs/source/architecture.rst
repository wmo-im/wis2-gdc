.. _architecture:

Architecture
============

``wmo-resource-catalogue`` is implemented in the spirit of the `Twelve-Factor App methodology`_.

``wmo-resource-catalogue`` is a `Docker`_ and `Python`_-based platform in support of WIS2 and WIGOS metadata management, publication, and discovery.

High level system context
-------------------------

The following diagram provides a high level overview of the main functions
of ``wmo-resource-catalogue``:

.. figure:: ../architecture/c4.container.png
   :scale: 70%
   :alt: wmo-resource-catalogue architecture
   :align: center

How ``wmo-resource-catalogue`` works
------------------------------------

As a containerized solution, ``wmo-resource-catalogue`` provides functionality via the following services:

* **wmo-resource-catalogue-management**: ingests, validates and publishes discovery metadata published from a WIS2 Global Broker instance
* **wmo-resource-catalogue-api**: API powered by `pygeoapi`_
* **wmo-resource-catalogue-monitoring**: monitoring

  * **metrics-collector**: metrics collector
  * **prometheus**: metrics scraper
  * **grafana**: analytics and visualization
* **wmo-resource-catalogue-broker**: MQTT broker
* **wmo-resource-catalogue-backend**: API search engine backend (default Elasticsearch)
* **wmo-resource-catalogue-cache**: message cache (default Redis)

``wmo-resource-catalogue`` is primarily an event-driven system, also providing interactive functionality for managing WIS2 and WIGOS metadata as required.

Workflows
^^^^^^^^^

``wmo-resource-catalogue`` starts up by connecting to one or more WIS2 Global Brokers (GB), subscribing to notifications for WIS2 metadata (WMO Core Metadata Profile [WCMP2]) and WIGOS metadata (WIGOS Metadata Record [WMDR2]).  On receipt of WIS2 Notification Messages (WNM) for metadata, ``wmo-resource-catalogue`` will perform message deduplication, validate, ingest and publish WCMP2 and WMDR2 records to its catalogue API.  In addition, WCMP2 and WMDR2 update and deletion is supported with the appropriate WNM.

.. note::

   * Valid WCMP2 record sources are always saved in their original form in the ``wmo-resource-catalogue-management`` container, in ``data/source/wis2-gdc``.
   * Valid WMDR2 record sources are always saved in their original form in the ``wmo-resource-catalogue-management`` container, in ``data/source/wigos-gofc``.

The ``wmo-resource-catalogue`` monitoring capability collects and provides metrics on WCMP2 and WMDR2 that is scraped by the WIS2 Global Monitor (GM).

``wmo-resource-catalogue`` also provides its own MQTT broker that provides WCMP2/WMDR2 compliance and key performance indicator (KPI) reports.  The WIS2 GB subscribes to the ``wmo-resource-catalogue`` broker in order to publish these reports back to users (available on WIS2 topic ``monitor/a/wis2/<CENTRE_ID_OF_DATA_PUBLISHER>`` and WIGOS topic ``monitor/a/wigos/<CENTRE_ID_OF_DATA_PUBLISHER>) for data providers in support of quality assessment, scoring and corrective action.  The ``wmo-resource-catalogue`` broker also acts as an internal message bus for inter-application event handling.

The ``wmo-resource-catalogue`` API provides an OGC API - Records endpoint that is OGC compliant.  The API provides search engine capability for WIS2 metadata, also providing OGC API - Processes functionality for WCMP2, WMDR2 validation and KPI quality assessment.

The ``wmo-resource-catalogue-management`` container provides functionality to restore a WCMP2 or WMDR2 metadata archive zipfile from another GDC or GOFC.  Note that ETS and KPI validations are not performed during restore workflows.

.. _`Twelve-Factor App methodology`: https://12factor.net
.. _`Docker`: https://www.docker.com
.. _`Python`: https://www.python.org
.. _`pygeoapi`: https://pygeoapi.io
