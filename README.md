[![flake8](https://github.com/wmo-im/wis2-gdc/workflows/flake8/badge.svg)](https://github.com/wmo-im/wis2-gdc/actions)

# wis2-gdc

wis2-gdc is a Reference Implementation of a WIS2 Global Discovery Catalogue.

<em>Note: architecture diagrams referenced from the <a href="https://github.com/wmo-im/wis2-guide">WIS2 Guide</a></em>

<a href="https://github.com/wmo-im/wis2-guide/blob/main/guide/images/architecture/c4.component-gdc.png"><img alt="WIS2 GDC C4 component diagram" src="https://github.com/wmo-im/wis2-guide/raw/main/guide/images/architecture/c4.component-gdc.png" width="800"/></a>

## Workflow

- connects to a WIS2 Global Broker, subscribed to the following:
  - `origin/a/wis2/+/+/metadata/#`
- on discovery metadata notifications, run the WCMP2 ATS via [pywcmp](https://github.com/wmo-im/pywcmp)
  - ETS
  - KPIs
- publish ETS and KPI reports to local broker under `gdc-reports`
- publish to a WIS2 GDC (OGC API - Records) using one of the supported transaction backends:
  - [OGC API - Features - Part 4: Create, Replace, Update and Delete](https://docs.ogc.org/DRAFTS/20-002.html)
  - Elasticsearch direct (default)

## Installation

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pywis-pubsub installation.

### Installing wis2-gdc

```bash
# setup virtualenv
python3 -m venv --system-site-packages wis2-gdc
cd wis2-gdc
source bin/activate

# clone codebase and install
git clone https://github.com/wmo-im/wis2-gdc.git
cd wis2-gdc
python3 setup.py install
```

## Running

```bash
# setup environment and configuration
cp wis2-gdc.env local.env
vim local.env # update accordingly

source local.env

# setup pywis-pubsub - sync WIS2 notification schema
pywis-pubsub schema sync

# setup backend
wis2-gdc setup

# teardown backend
wis2-gdc teardown

# connect to Global Broker
# discovery metadata notifications will automatically trigger wis2-gdc to validate and publish
# WCMP2 to the GDC identified in wis2-gdc.env (WIS2_GDC_GB)
pywis-pubsub subscribe --config pywis-pubsub.yml

# loading metadata manually (single file)
wis2-gdc register /path/to/wcmp2-file.json

# loading metadata manually (directory of .json files)
wis2-gdc register /path/to/dir/or/wcmp2-files

# loading metadata from a known harvest endpoint

# load from wis2box known deployments (https://demo.wis2box.wis.wmo.int)
wis2-gdc sync wis2box
```

### Docker

Instructions to run wis2-gdc via Docker can be found the [`docker`](docker) directory.

## Development

### Running Tests

```bash
# install dev requirements
pip3 install -r requirements-dev.txt

# run tests like this:
python3 tests/run_tests.py

# or this:
python3 setup.py test
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/wmo-im/wis2-gdc/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
