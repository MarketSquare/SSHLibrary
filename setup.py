#!/usr/bin/env python

import re
import sys
from os.path import abspath, dirname, join
from setuptools import setup

CURDIR = dirname(abspath(__file__))
REQUIREMENTS = ['robotframework >= 3.0']
if not sys.platform.startswith('java'):
    REQUIREMENTS.append('paramiko >= 1.15.0')
with open(join(CURDIR, 'src', 'SSHLibrary', 'version.py')) as f:
    VERSION = re.search("\nVERSION = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'README.rst')) as f:
    DESCRIPTION = f.read()
CLASSIFIERS = '''
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()

setup(
    name='robotframework-sshlibrary',
    version=VERSION,
    description='Robot Framework test library for SSH and SFTP',
    long_description=DESCRIPTION,
    author='Robot Framework Developers',
    author_email='robotframework@gmail.com',
    url='https://github.com/robotframework/SSHLibrary',
    license='Apache License 2.0',
    keywords='robotframework testing testautomation ssh sftp',
    platforms='any',
    classifiers=CLASSIFIERS,
    install_requires = REQUIREMENTS,
    package_dir={'': 'src'},
    packages=['SSHLibrary']
)
