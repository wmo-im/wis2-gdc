###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

from pathlib import Path
import re
from setuptools import Command, find_packages, setup
import sys


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, 'tests/run_tests.py'])
        raise SystemExit(errno)


def read(filename, encoding='utf-8'):
    """read file contents"""

    fullpath = Path(__file__).resolve().parent / filename

    with fullpath.open() as fh:
        contents = fh.read().strip()
    return contents


def get_package_version():
    """get version from top-level package init"""
    version_file = read('wis2_gdc/__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


LONG_DESCRIPTION = read('README.md')

DESCRIPTION = 'wis2-gdc is a Reference Implementation of a WIS2 Global Discovery Catalogue'  # noqa

MANIFEST = Path('MANIFEST')

if MANIFEST.exists():
    MANIFEST.unlink()


setup(
    name='wis2-gdc',
    version=get_package_version(),
    description=DESCRIPTION.strip(),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license='Apache Software License',
    platforms='all',
    keywords=' '.join([
        'WIS2',
        'Global Discovery Catalogue',
        'GDC',
        'WCMP2',
        'discovery metadata'
    ]),
    author='Tom Kralidis',
    author_email='tomkralidis@gmail.com',
    maintainer='Tom Kralidis',
    maintainer_email='tomkraldis@gmail.com',
    url='https://github.com/wmo-im/wis2-gdc',
    install_requires=read('requirements.txt').splitlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'wis2-gdc=wis2_gdc:cli'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    cmdclass={'test': PyTest}
)
