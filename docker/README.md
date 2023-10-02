# Docker

## Overview

This Docker setup uses Docker and Docker Compose to manage the following services:

- **pygeoapi**: OGC API - Records metadata catalogue
- **Elasticsearch**: GDC search engine backend
- **wis2-gdc-management**: management service to ingest, validate and publish discovery metadata published from a WIS2 Global Broker instance
  - the default Global Broker connection is to Météo-France.  This can be modified in `pywis-pubsub-config.local.yml` to point to an alternate Global Broker

See [`wis2-gdc-config.local.env`](wis2-gdc-config.local.env) for default environment variable settings.

To adjust service ports, edit [`docker-compose.override.yml`](docker-compose.override.yml) accordingly.

## Running

The [`Makefile`](../Makefile) in the root directory provides options to manage the Docker Compose setup.
