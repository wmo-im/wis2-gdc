.. _installation:

Installation
============

Requirements
------------

wis2-gdc is built as a `Docker Compose`_ application, allowing for easy install and container management.  Ensure that `Docker`_ and Docker Compose
are installed on the system in order to install and run ``wis2-gdc``.

The `make`_ utility can be used as a convenience to executing Docker Compose commands via the provided ``Makefile``.

Install
-------

.. code-block:: bash

   # clone codebase and build/run
   git clone https://github.com/wmo-im/wis2-gdc.git
   cd wis2-gdc-management
   make up


After installing ``wis2-gdc``, the next steps involve updating the default configuration before running the system.

.. _`Docker`: https://www.docker.com
.. _`Docker Compose`: https://docs.docker.com/compose
.. _`make`: https://www.gnu.org/software/make/manual/make.html
