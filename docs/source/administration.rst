.. _administration:

Administration
==============

Docker Compose
--------------

As a Docker Compose based application, ``wmo-resource-catalogue`` uses the ``docker compose`` command to manage services.  The Docker Compose setups are defined in the following configurations:

- ``docker-compose.yml``
- ``docker-compose.override.yml``

To adjust service ports, edit ``docker-compose.override.yml`` accordingly.

As a convenience, the ``Makefile`` in the root directory provides shortcuts to manage the Docker Compose setup (encapsulating the various ``docker compose`` commands).

.. code-block:: bash

   # build all images
   make build

   # build all images (no cache)
   make force-build

   # start all containers
   make up

   # reinitialize backends
   make reinit-backends

   # view all container logs in realtime
   make logs

   # login to the wmo-resource-catalogue-management container
   make login

   # restart all containers
   make restart

   # shutdown all containers
   make down

   # remove all volumes
   make rm

   # perform pruning of Docker system artifacts
   make clean

   # monitor running containers
   make ps
