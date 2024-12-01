.. _running:

Running
=======

As defined by the WIS2 Technical Regulations, wis2-gdc is an event driven service which listens to WIS2 Global Broker services in ordder to manage discovery metadata publication.

Interactive discovery metadata workflows
----------------------------------------

To register metadata manually, login to the ``wis2-gdc-management`` container and run the following commands:

.. code-block::

   # loading metadata manually (single file)
   wis2-gdc register /path/to/wcmp2-file.json

   # loading metadata manually (directory of .json files)
   wis2-gdc register /path/to/dir/of/wcmp2-files

   # loading metadata manually (from URL)
   wis2-gdc register https://example.org/wcmp2-file.json

   # deleting metadata by identifier
   wis2-gdc unregister "urn:wmo:md:ca-eccc-msc:id123"

   # load all WCMP2 metadata from known wis2box deployments (https://demo.wis2box.wis.wmo.int)
   wis2-gdc sync wis2box

   # create a metadata archive zipfile
   wis2-gdc archive foo.zip

Services
--------

The following publically facing services are running when wis2-gdc is started:

- API (port 80)
- Broker (port 1883)

TLS/SSL
-------

To enable SSL, it is advised to setup SSL on a proxy server and "proxy pass" to wis2-gdc services accordingly.

Below are examples of adding HTTP and MQTT proxies to Nginx:

TODO: add nginx snippets

.. note::

   It is strongly recommended to run services using TLS/SSL to offer HTTPS and MQTTS
