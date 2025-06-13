.. _running:

Running
=======

As defined by the WIS2 Technical Regulations, wis2-gdc is an event driven service which listens to WIS2 Global Broker services in order to manage discovery metadata publication.

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

   # restore from a metadata archive zipfile
   wis2-gdc restore foo.zip

Services
--------

The following publically facing services are running when wis2-gdc is started:

- API (port 80)
- Broker (port 1883)

TLS/SSL
-------

To enable SSL, it is advised to setup SSL on a proxy server and "proxy pass" to wis2-gdc services accordingly.

Below are examples of adding HTTP (port 443) and MQTT (port 8883) proxies to Nginx:

HTTP
^^^^

.. code-block:: nginx

   server {
           listen 443 ssl default_server;
           listen [::]:443 ssl default_server;
   
           ssl_certificate /path/to/fullchain.pem;
           ssl_certificate_key /path/to/privkey.pem;
   
           root /var/www/html;
   
           server_name gdc.hostname;  // adjust accordingly
   
           location / {
                   proxy_pass http://localhost:5001/;
           }
   
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Host $server_name;
   
           add_header 'Access-Control-Allow-Origin' '*';
           add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
           add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
   }

MQTT
^^^^

.. code-block:: nginx

   stream {
           upstream broker {
                   server 127.0.0.1:1883 fail_timeout=1s max_fails=1;
           }
           server {
                   ssl_certificate /etc/letsencrypt/live/gdc.wis2dev.io/fullchain.pem;
                   ssl_certificate_key /etc/letsencrypt/live/gdc.wis2dev.io/privkey.pem;
                   ssl_protocols TLSv1.2;
                   listen 8883 ssl;
                   proxy_pass broker;
                   proxy_connect_timeout 1s;
           }
   }

.. note::

   It is strongly recommended to run services using TLS/SSL to offer HTTPS and MQTTS
