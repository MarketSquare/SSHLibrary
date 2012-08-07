#!/usr/bin/env python

from distutils.core import setup
from os.path import abspath, dirname, join
execfile(join(dirname(abspath(__file__)), 'src', 'SSHLibrary', 'version.py'))

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
    description='Test Library for Robot Framework enabling SSH',
    author='Robot Framework Developers',
    author_email='robotframework-devel@groups.google.com',
    url='http://code.google.com/p/robotframework-sshlibrary/',
    license='Apache License 2.0',
    keywords='robotframework testing testautomation ssh',
    platforms='any',
    classifiers=CLASSIFIERS.splitlines(),
    package_dir={'': 'src'},
    packages=['SSHLibrary']
)
