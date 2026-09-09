    wis2-discovery-metadata:
        type: collection
        title: WIS2 discovery metadata
        description: WIS2 discovery metadata
        keywords:
            - wmo information system
            - wis2
            - global discovery catalogue
            - gdc
            - wmo core metadata profile
            - wcmp2
            - discovery metadata
        crs:
            - CRS84
        links:
            - type: application/zip
              rel: archives
              title: Metadata archive (generated daily)
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/wis2-discovery-metadata-archive.zip
              hreflang: en-CA
              length: -1
            - type: text/plain
              rel: related
              title: OpenMetrics
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/wmo-resource-catalogue-metrics.txt
              hreflang: en-CA
            - type: text/plain
              rel: related
              title: Live channel list
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/wmo-resource-catalogue-all-channels-latest.txt
              hreflang: en-CA
            - type: text/html
              rel: related
              title: Analytics and monitoring dashboard
              href: ${WMO_RESOURCE_CATALOGUE_API_URL:-http://localhost}/grafana
              hreflang: en-CA
            - type: text/html
              rel: canonical
              title: WMO Information System (WIS) | World Meteorological Organization
              href: https://community.wmo.int/en/activity-areas/wis
              hreflang: en-CA
        extents:
            spatial:
                bbox: [-180, -90, 180, 90]
                crs: http://www.opengis.net/def/crs/OGC/1.3/CRS84
        providers:
            - type: record
              name: ${WMO_RESOURCE_CATALOGUE_BACKEND_TYPE:-Elasticsearch}
              data: ${WMO_RESOURCE_CATALOGUE_BACKEND_CONNECTION:-http://wmo-resource-catalogue-backend:9200/wis2-discovery-metadata}
              id_field: id
              time_field: updated
              title_field: title
              include_extra_query_parameters: true

    pywcmp-wis2-wcmp2-ets:
        type: process
        processor:
            name: pywcmp.pygeoapi_plugin.WCMP2ETSProcessor

    pywcmp-wis2-wcmp2-kpi:
        type: process
        processor:
            name: pywcmp.pygeoapi_plugin.WCMP2KPIProcessor
