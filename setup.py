#!/usr/bin/env python

from distutils.core import setup
import sys
sys.path.insert(0, 'src')
import SSHLibrary


def main():
    setup(name         = 'SSHLibrary',
          version      =  SSHLibrary.__version__,
          description  = 'Test Library for Robot Framework enabling SSH',
          author       = 'Robot Framework Developers',
          author_email = 'robotframework-sshlibrary@groups.google.com',
          url          = 'http://code.google.com/p/robotframework-sshlibrary/',
          package_dir  = { '' : 'src'},
          packages     = ['SSHLibrary']
          )
        

if __name__ == "__main__":
    main()
