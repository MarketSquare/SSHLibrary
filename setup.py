#!/usr/bin/env python

try:
    from setuptools import setup
    requires = {
        'install_requires': ['robotframework', 'paramiko >= 1.8.0'],
    }
except ImportError:
    from distutils.core import setup
    requires = {}

from os.path import abspath, dirname, join

execfile(join(dirname(abspath(__file__)), 'src', 'SSHLibrary', 'version.py'))

# Maximum width in Windows installer seems to be 70 characters -------|
DESCRIPTION = """
This is a Robot Framework test library for testing SSH and SFTP.

The library has the following main usages:
- Executing commands on remote, either with blocking or non-blocking
  behaviour.
- Writing and reading in an interactive session.
- Transferring files and directories over SFTP.
- Ensuring that files or directories exist on remote.

Required packages:
    robotframework
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
    platforms='any',
    classifiers=CLASSIFIERS.splitlines(),
    package_dir={'': 'src'},
    packages=['SSHLibrary'],
    **requires
)
