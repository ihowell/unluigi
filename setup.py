# Copyright (c) 2012 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import os
import sys

from setuptools import setup

readme_note = """\
.. note::

   For the latest source, discussion, etc, please visit the
   `GitHub repository <https://github.com/spotify/gaps>`_\n\n
"""

# with open('README.rst') as fobj:
long_description = readme_note  #+ fobj.read()

install_requires = ['python-dateutil>=2.7.5,<3']

if os.environ.get('READTHEDOCS', None) == 'True':
    # So that we can build documentation for gaps.db_task_history and gaps.contrib.sqla
    install_requires.append('sqlalchemy')
    # readthedocs don't like python-daemon, see #1342
    install_requires = [
        x for x in install_requires if not x.startswith('python-daemon')
    ]
    install_requires.append('sphinx>=1.4.4')  # Value mirrored in doc/conf.py

# load meta package infos
meta = {}
with open("gaps/__meta__.py", "r") as f:
    exec (f.read(), meta)

setup(
    name='gaps',
    version=meta['__version__'],
    description=meta['__doc__'],
    long_description=long_description,
    author=meta['__author__'],
    url=meta['__contact__'],
    license=meta['__license__'],
    packages=['gaps', 'gaps.configuration', 'gaps.tools'],
    entry_points={'console_scripts': ['gaps = gaps.cmdline:gaps_run']},
    install_requires=install_requires,
    extras_require={
        'toml': ['toml<2.0.0'],
    },
)
