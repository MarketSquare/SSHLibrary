#!/usr/bin/env python

try:
    from setuptools import setup
    kw = {
        'install_requires': 'paramiko >= 1.8.0',
    }
except ImportError:
    from distutils.core import setup
    kw = {}

from os.path import abspath, dirname, join

execfile(join(dirname(abspath(__file__)), 'src', 'SSHLibrary', 'version.py'))

# Maximum width in Windows installer seems to be 70 characters -------|
DESCRIPTION = """
This is a Robot Framework test library for testing SSH and SFTP.

Required packages:
    paramiko
"""[1:-1]

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
    long_description=DESCRIPTION,
    author='Robot Framework Developers',
    author_email='robotframework-devel@groups.google.com',
    url='http://code.google.com/p/robotframework-sshlibrary/',
    license='Apache License 2.0',
    keywords='robotframework testing testautomation ssh',
    platforms='Posix, MacOS X, Windows',
    classifiers=CLASSIFIERS.splitlines(),
    package_dir={'': 'src'},
    packages=['SSHLibrary'],
    **kw
)
