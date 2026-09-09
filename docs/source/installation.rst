.. _installation:

Installation
============

Requirements
------------

wis2box is built as a `Docker Compose`_ application, allowing for easy installation and container management.  Ensure that `Docker`_ and Docker Compose are installed on the system in order to install and run ``wmo-resource-catalogue``.

The `make`_ utility can be used as a convenience to executing Docker Compose commands via the provided ``Makefile``.

Install
-------

.. code-block:: bash

   # clone codebase and build/run
   git clone https://github.com/wmo-im/wmo-resource-catalogue.git
   cd wmo-resource-catalogue-management
   make up

After installing ``wmo-resource-catalogue``, the next steps involve updating the default configuration before running the system.

Install with TLS/SSL
--------------------

To enable TLS/SSL support, perform the following steps:

1. update ``docker-compose.ssl.yml``

2. add the file ``docker-compose.ssl.yml`` to the ``Makefile`` Docker Compose arguments, updating as follows:

.. code-block:: make

   DOCKER_COMPOSE_ARGS=--project-name wmo-resource-catalogue --file docker-compose.yml --file docker-compose.override.yml --file docker-compose.ssl.yml

This will result in running ``make up`` with TLS/SSL support.



.. _`Docker`: https://www.docker.com
.. _`Docker Compose`: https://docs.docker.com/compose
.. _`make`: https://www.gnu.org/software/make/manual/make.html
