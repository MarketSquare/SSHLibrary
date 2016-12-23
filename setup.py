#!/usr/bin/env python

from __future__ import with_statement
from sys import platform

requires = {}

try:
    from setuptools import setup

    if not platform.startswith('java'):
        requires = {
            'install_requires': ['robotframework', 'paramiko >= 1.8.0'],
        }
except ImportError:
    from distutils.core import setup


from os.path import abspath, dirname, join

CURDIR = dirname(abspath(__file__))
execfile(join(CURDIR, 'src', 'SSHLibrary', 'version.py'))
with open(join(CURDIR, 'README.rst')) as readme:
    README = readme.read()
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
"""[1:-1]

setup(
    name='robotframework-sshlibrary',
    version=VERSION, # resolved with execfile
    description='Robot Framework test library for SSH and SFTP',
    long_description=README,
    author='Robot Framework Developers',
    author_email='robotframework@gmail.com',
    url='https://github.com/robotframework/SSHLibrary',
    license='Apache License 2.0',
    keywords='robotframework testing testautomation ssh sftp',
    platforms='any',
    classifiers=CLASSIFIERS.splitlines(),
    package_dir={'': 'src'},
    packages=['SSHLibrary'],
    **requires
)
