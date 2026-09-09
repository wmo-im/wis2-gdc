    wigos-observing-facility-metadata:
        type: collection
        title: WIGOS observing facility metadata
        description: WIGOS observing facility metadata
        keywords:
            - wmo integrated global observing system
            - wigos
            - global observing facility catalogue
            - gofc
            - wigos metadata record
            - wmdr2
            - observing facility metadata
        crs:
            - CRS84
        links:
            - type: application/zip
              rel: archives
              title: Metadata archive (generated daily)
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/wigos-observing-facility-metadata-archive.zip
              hreflang: en-US
              length: -1
            - type: text/plain
              rel: related
              title: OpenMetrics
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/wmo-resource-catalogue-metrics.txt
              hreflang: en-US
            - type: text/html
              rel: related
              title: Analytics and monitoring dashboard
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/grafana
              hreflang: en-US
            - type: text/html
              rel: canonical
              title: WMO Integration Global Observing System (WIGOS) | World Meteorological Organization
              href: https://community.wmo.int/en/activity-areas/wigos
              hreflang: en-US
        extents:
            spatial:
                bbox: [-180, -90, 180, 90]
                crs: http://www.opengis.net/def/crs/OGC/1.3/CRS84
        providers:
            - type: record
              name: ${WMO_RESOURCE_CATALOGUE_BACKEND_TYPE:-Elasticsearch}
              data: ${WMO_RESOURCE_CATALOGUE_BACKEND_CONNECTION:-http://wmo-resource-catalogue-backend:9200/wigos-observing-facility-metadata}
              id_field: id
              time_field: updated
              title_field: title
              include_extra_query_parameters: true

    pywmdr-wigos-wmdr2-ets:
        type: process
        processor:
            name: pywmdr.pygeoapi_plugin.WMDR2ETSProcessor
